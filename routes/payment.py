import os
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import razorpay
from database import db_dependency
from models import payments, setSchedule, refundModel
from routes.token import bearer_scheme, decode_token
from base_model import paymentModel, verifyPayment, refundMod
import uuid
from datetime import datetime, timedelta
from typing import Optional
import pytz
from routes.scheduler import scheduler
from routes.helpers import merchantCancellation
from apscheduler.triggers.date import DateTrigger

router = APIRouter(tags=["payments"])



R_KEY = os.getenv('RAZORPAY_KEY')
R_SECRET = os.getenv('RAZORPAY_SECRET')

client = razorpay.Client(auth=(R_KEY, R_SECRET))
client.set_app_details({"title" : "Orado", "version" : "1.0.0"})


@router.post("/get-payment",summary="first")
async def paymentRazor(sm:paymentModel,db:db_dependency,token: Optional[str] = Depends(bearer_scheme)):
    decoded_token = decode_token(token.credentials)
    if isinstance(decoded_token, JSONResponse):
        return decoded_token
    userId = decoded_token.get("userId")
    unique_id = uuid.uuid4().hex
    reciept = "orado" + "/" + unique_id
    try:
        data = { "amount": sm.amount, "currency": "INR", "receipt": reciept }
        payment = client.order.create(data=data)
        if payment is None:
            return  JSONResponse(status_code=400, content={"detail":[],"message":"unable to create a payment request"})

        orderId =payment.get('id')
        getPayment = payments(oradoOrderId=sm.oradoOrderId,userId=userId,orderId= orderId,recieptId=reciept,amount=sm.amount)
        db.add(getPayment)
        db.commit()
        return JSONResponse(status_code=200,content={"detail":payment})
    except Exception as e:
        print(e)
        db.rollback()
        return  JSONResponse(status_code=500, content={"detail":[]})
    
@router.post("/store-payment",summary="second")
async def storePayment(vm:verifyPayment,db:db_dependency,token: Optional[str] = Depends(bearer_scheme)): #
    decoded_token = decode_token(token.credentials)
    if isinstance(decoded_token, JSONResponse):
        return decoded_token
    
    try:
        verify = client.utility.verify_payment_signature({
    'razorpay_order_id': vm.razorpay_order_id,
    'razorpay_payment_id': vm.razorpay_payment_id,
    'razorpay_signature': vm.razorpay_signature
    })
        
        if not verify:
            return JSONResponse(status_code=406,content={"detail":"not verified"})
        else:
            getdata =client.payment.fetch(vm.razorpay_payment_id)
            if not getdata:
                return JSONResponse(status_code=404, content={"detail":"not found"})
            else:
                #oId = getdata.get('order_id')
                status = getdata.get('status')
              
                if status == "captured":
                    store = db.query(payments).filter(payments.orderId == vm.razorpay_order_id).first()
                    if store is None:
                        return JSONResponse(status_code=404, content={"detail":"not found"})
                    store.razorpayPaymentId = vm.razorpay_payment_id
                    store.status = 1
                    current = datetime.now()
                    store.transactionTime = current
                    orderAcceptanceTime = 40
                    expectedOrderAcceptance = current + timedelta(seconds=orderAcceptanceTime)
                    addToMerchantSchedule = setSchedule(orderId=store.oradoOrderId,timeStamp=expectedOrderAcceptance)
                    db.add(addToMerchantSchedule)
                    db.flush()
                    jobId = addToMerchantSchedule.jobId
                    sgt_timestamp = expectedOrderAcceptance.astimezone(pytz.timezone('Asia/Singapore')) #when a job is added to db it has to trigger the scheduler
                    trigger = DateTrigger(run_date=sgt_timestamp)
                    scheduler.add_job(
                        merchantCancellation,
                        trigger,
                        args=[jobId, db],
                        id=str(jobId),
                        replace_existing=True
                    )
                    db.commit()
                    
                    return JSONResponse(status_code=200, content={"detail":"payment success"})
                else:
                    return JSONResponse(status_code=400, content={"detail":"payment failed"})
    except Exception as e:
        
        return JSONResponse(status_code=500, content={"detail":str(e)})
    

@router.post("/refund",summary="second")
async def refund(rm:refundMod,db:db_dependency,token: Optional[str] = Depends(bearer_scheme)):
    decoded_token = decode_token(token.credentials)
    if isinstance(decoded_token, JSONResponse):
        return decoded_token
    userType = decoded_token.get('userType')
    userId = decoded_token.get('userId')
    if userType != "admin":
        return JSONResponse(status_code=403, content={"detail": "you lack admin privilages"})
    try:
        getamount = db.query(payments).filter(payments.razorpayPaymentId == rm.paymentId).first()
        if getamount is None:
            return JSONResponse(status_code=404, content={"detail":"payment data not found"})
        amount = getamount.amount
        unique_id = uuid.uuid4().hex
        reciept = "oradoRefund" + "/" + unique_id
        getres = client.payment.refund(rm.paymentId,{
        "amount": amount,
        "speed": "optimum",
        "receipt": reciept
        })

        if getres is None:
            return JSONResponse(status_code=406, content={"detail":"unable to process refund"})
        
        addToRefund = refundModel(userId=userId,cancelledByUserType=3,refundId= getres.get('id'),amount=getres.get('amount'),currency=getres.get('currency'),receiptId=getres.get('receipt'),razorpayPaymentId=getres.get('payment_id'),oradoOrderId= getamount.oradoOrderId)
        db.add(addToRefund)
        db.commit()
        return JSONResponse(status_code=200, content={"detail":getres})
        
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"detail":"refund failed"})
       

    
def refund(paymentId, amount):

    unique_id = uuid.uuid4().hex
    reciept = "oradoRefund" + "/" + unique_id
    getres = client.payment.refund(paymentId,{
    "amount": amount,
    "speed": "optimum",
    "receipt": reciept
    })

    return getres
