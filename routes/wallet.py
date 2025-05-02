from fastapi import APIRouter, HTTPException
from base_model import PaymentRequest
import httpx

router =APIRouter()

RasroPay_BASE_URL = "https://api.rasropay.com"  # Replace with the actual RasroPay base URL

# Function to create a payment
async def create_payment(email: str, password: str, amount: float, currency: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RasroPay_BASE_URL}/create-payment",  # Replace with actual RasroPay endpoint
            json={
                "email": email,
                "password": password,
                "amount": amount,
                "currency": currency
            }
        )
        response_data = response.json()
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response_data.get("message", "Error creating payment"))
        return response_data

# Endpoint to initiate payment
@router.post("/create-payment/")
async def initiate_payment(payment_request: PaymentRequest):
    payment_response = await create_payment(
        payment_request.email,
        payment_request.password,
        payment_request.amount,
        payment_request.currency
    )
    return payment_response

@router.get("/")
def read_root():
    return {"message": "Welcome to the Wallet API"}
