import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Frontend se connect karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchReq(BaseModel): 
    phone_number: str

@app.get("/")
def home(): 
    return {"message": "🚀 Blitz Search Engine API is Lightning Fast!"}

# --- MAIN SEARCH API (Super Fast) ---
@app.post("/search")
async def search_number(req: SearchReq):
    # Aapki di hui direct API (yahan number automatically lag jayega)
    api_url = f"https://ayaanmods.site/number.php?key=annonymous&number={req.phone_number}"
    
    try:
        # API ko hit karna aur data lana
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    # API jo bhi degi (Text ya JSON), hum seedha frontend ko bhej denge
                    data = await response.text() 
                    return {"status": "success", "result": data}
                else:
                    raise HTTPException(status_code=500, detail="Main API Server is down")
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Network error while fetching data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
  
