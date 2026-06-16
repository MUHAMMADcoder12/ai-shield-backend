from fastapi import FastAPI
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

class SaytMaoruz(BaseModel):
    matn: str

@app.post("/tahlil")
async def tahlil_qil(sayt: SaytMaoruz):
    try:
        # Tashqi API'larga bog'lanmasdan, serverning o'zida oddiy tekshiruv qilamiz
        matn_lower = sayt.matn.lower()
        
        # Agar matnda kiberxavfsizlikka oid shubhali so'zlar bo'lsa srazi bloklaymiz
        if "karta" in matn_lower or "kod" in matn_lower or "yutuq" in matn_lower or "sms" in matn_lower:
            return {"status": "fishing"}
        else:
            return {"status": "xavfsiz"}
            
    except Exception as e:
        return {"status": "XATO", "error": str(e)}
