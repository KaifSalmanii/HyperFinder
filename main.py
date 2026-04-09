import os
import aiohttp
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Render ki tijori se keys nikali jayengi
CASHFREE_APP_ID = os.environ.get("CASHFREE_APP_ID")
CASHFREE_SECRET_KEY = os.environ.get("CASHFREE_SECRET_KEY")
# Live mode ki API link
CASHFREE_API_URL = "https://api.cashfree.com/pg/orders" 

class SearchReq(BaseModel): phone_number: str
class OrderReq(BaseModel): amount: float; uid: str; email: str; name: str

@app.get("/")
def home(): return {"message": "🚀 HyperFinder API is Live with Cashfree!"}

# --- 1. SEARCH API ---
@app.post("/search")
async def search_number(req: SearchReq):
    api_url = f"https://ayaanmods.site/number.php?key=annonymous&number={req.phone_number}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.text()
                    return {"status": "success", "result": data}
                else:
                    raise HTTPException(status_code=500, detail="Main API Server is down")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Network error")

# --- 2. CASHFREE: CREATE ORDER (Payment Link Banana) ---
@app.post("/create-order")
async def create_order(req: OrderReq):
    if not CASHFREE_APP_ID or not CASHFREE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Cashfree keys missing in Render")

    order_id = f"ORDER_{uuid.uuid4().hex[:10].upper()}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-version": "2023-08-01",
        "x-client-id": CASHFREE_APP_ID,
        "x-client-secret": CASHFREE_SECRET_KEY
    }
    
    payload = {
        "order_amount": req.amount,
        "order_currency": "INR",
        "order_id": order_id,
        "customer_details": {
            "customer_id": req.uid,
            "customer_email": req.email,
            "customer_phone": "9999999999", # Demo number
            "customer_name": req.name
        },
        "order_meta": {
            "return_url": f"https://hyperfinderr.blogspot.com?order_id={order_id}"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(CASHFREE_API_URL, json=payload, headers=headers) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return {"payment_session_id": data.get("payment_session_id"), "order_id": order_id}
                else:
                    raise HTTPException(status_code=400, detail=str(data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 3. CASHFREE: VERIFY PAYMENT (Check karna ki paise aaye ya nahi) ---
@app.get("/verify-payment/{order_id}")
async def verify_payment(order_id: str):
    headers = {
        "accept": "application/json",
        "x-api-version": "2023-08-01",
        "x-client-id": CASHFREE_APP_ID,
        "x-client-secret": CASHFREE_SECRET_KEY
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{CASHFREE_API_URL}/{order_id}", headers=headers) as resp:
                data = await resp.json()
                if resp.status == 200:
                    status = data.get("order_status")
                    return {"order_id": order_id, "status": status} # 'PAID' or 'ACTIVE'
                else:
                    raise HTTPException(status_code=400, detail="Invalid Order")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
