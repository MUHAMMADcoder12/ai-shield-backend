from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 MANA SHU YERGA BOYAGI OLGAN HAQIQIY GEMINI KALITINGIZNI QO'YING!
GEMINI_API_KEY = "AQ.Ab8RN6J5jKIQGCVdLwtuGtDtA5__SB-y4K2X2TAK5Dq3mc1ukg"

# Gemini API'ning rasmiy manzili
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

class SaytMaoruz(BaseModel):
    matn: str

tizim_yoʻriqnomasi = (
    "Siz kiberxavfsizlik sohasida anti-phishing mutaxassisiz. "
    "Sizga kelgan matnni tahlil qiling. Agar matnda shaxsiy ma'lumotlarni, "
    "plastik karta raqamlarini o'g'irlash, shubhali tekin yutuqlar yoki SMS kod so'rash kabi "
    "fishing (aldov) alomatlari bo'lsa faqat 'XAVFLI' so'zini qaytaring. "
    "Agar oddiy, xavfsiz sayt bo'lsa 'XAVFSIZ' so'zini qaytaring. "
    "Hech qanday ortiqcha tushuntirish yoki gap yozmang, faqat shu ikki so'zdan birini qaytaring."
)

@app.post("/tahlil")
async def tahlil_qil(sayt: SaytMaoruz):
    try:
        # Gemini API uchun so'rov paketi (Payload)
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{tizim_yoʻriqnomasi}\n\nTahlil qilinadigan matn:\n{sayt.matn}"
                }]
            }]
        }
        
        res = requests.post(URL, json=payload, headers={"Content-Type": "application/json"})
        data = res.json()
        
        # Geminidan kelgan javob matnini tozalab olamiz
        gemini_javobi = data['candidates'][0]['content']['parts'][0]['text'].strip().upper()
        
        # Agar javob ichida XAVFLI so'zi bo'lsa, plaginga signal beramiz
        if "XAVFLI" in gemini_javobi:
            return {"status": "fishing"}
        else:
            return {"status": "xavfsiz"}
            
    except Exception as e:
        return {"status": "XATO", "error": str(e)}
