from fastapi import APIRouter,Depends
from database import db_dependency
from routes.token import decode_token, bearer_scheme
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from base_model import TaxModel,TaxEditModel
from models import *

router=APIRouter()


@router.post("/add-tax", tags=['Tax'])
async def addTax(lm:TaxModel,db:db_dependency, token:Optional[str] = Depends(bearer_scheme)):
    decoded_token = decode_token(token.credentials)
    if isinstance(decoded_token, JSONResponse):
        return decoded_token
    userType = decoded_token.get('userType')
    if userType != "admin":
        return JSONResponse(status_code=403, content={"detail": "you lack admin privilages"})
    
    try:
       
        addloyal = taxTable(taxName = lm.taxName, tax= float(lm.tax), taxType = int(lm.taxType), ApplicableOn = lm.ApplicableOn, differentiate= int(lm.differentiate))
        db.add(addloyal)
        db.commit()
        return JSONResponse(status_code=200, content={"detail": "Tax criterion added"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=400, content={"detail": "unable to add Tax"})
    

@router.post("/edit-tax/{taxId}", tags=['Tax'])
async def editTax(taxId:int,lm:TaxEditModel,db:db_dependency, token:Optional[str] = Depends(bearer_scheme)):
    decoded_token = decode_token(token.credentials)
    if isinstance(decoded_token, JSONResponse):
        return decoded_token
    userType = decoded_token.get('userType')
    if userType != "admin":
        return JSONResponse(status_code=403, content={"detail": "you lack admin privilages"})
    
    try:
        fetch = db.query(taxTable).filter(taxTable.taxId == taxId).first()

        if lm.taxName != "":
            fetch.taxName = lm.taxName
        if lm.tax != "":
            fetch.tax = float(lm.tax)
        if lm.taxType != "":
            fetch.taxType = int(lm.taxType)
        if lm.ApplicableOn != "":
            fetch.ApplicableOn = lm.ApplicableOn
        if lm.status != "":
            fetch.status = int(lm.status)
        if lm.differentiate != "":
            fetch.differentiate = int(lm.differentiate)
       
        db.commit()
        return JSONResponse(status_code=200, content={"detail": "Tax criterion updated"})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=400, content={"detail": "unable to update Tax"})
    
@router.get("/viewall-tax", tags=['Tax'])
async def viewTax(db:db_dependency, token:Optional[str] = Depends(bearer_scheme)):
    decoded_token = decode_token(token.credentials)
    if isinstance(decoded_token, JSONResponse):
        return decoded_token
    userType = decoded_token.get('userType')
    if userType != "admin" and userType != "merchant":
        return JSONResponse(status_code=403, content={"detail": "you lack admin privilages"})
    
    try:
        fetch = db.query(taxTable).filter(taxTable.deleteStatus == 0).order_by(taxTable.status.asc()).all()

        return JSONResponse(status_code=200, content={"detail": jsonable_encoder(fetch)})
    except Exception as e:
        print(e)
        db.rollback()
        return JSONResponse(status_code=400, content={"detail": "unable to add Tax"})
    
@router.delete("/delete-tax/{taxId}", tags=["Tax"])
async def deleteTax(taxId:int,db:db_dependency, token:Optional[str] = Depends(bearer_scheme)):
    decoded_token = decode_token(token.credentials)
    if isinstance(decoded_token, JSONResponse):
        return decoded_token
    userType = decoded_token.get('userType')
    if userType != "admin":
        return JSONResponse(status_code=403, content={"detail": "you lack admin privilages"})
    
    fetchTax = db.query(taxTable).filter(taxTable.taxId == taxId).first()
    if fetchTax is None:
        return JSONResponse(status_code=404, content={"detail": "Tax not found"})
    fetchTax.deleteStatus = 1
    db.commit()
    return JSONResponse(status_code=200, content={"detail": "Tax successfully deleted"})