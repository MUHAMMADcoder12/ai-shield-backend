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

# Kalitsiz va tekin ishlaydigan ochiq AI API manzili
URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

class SaytMaoruz(BaseModel):
    matn: str

tizim_yoʻriqnomasi = (
    "Siz anti-phishing tizimisiz. Matnni tekshiring. Agar unda plastik karta o'g'irlash, "
    "soxta yutuq, login-parol yoki SMS kod so'rash bo'lsa faqat 'XAVFLI' deb javob bering. "
    "Aks holda 'XAVFSIZ' deb javob bering. Faqat shu birgina so'zning o'zini qaytaring."
)

@app.post("/tahlil")
async def tahlil_qil(sayt: SaytMaoruz):
    try:
        # Hech qanday Bearer Token yoki API Key-siz to'g'ridan-to'g'ri so'rov yuboramiz
        payload = {
            "inputs": f"<|system|>\n{tizim_yoʻriqnomasi}\n<|user|>\n{sayt.matn}\n<|assistant|>\n",
            "parameters": {"max_new_tokens": 5, "temperature": 0.1}
        }
        
        res = requests.post(URL, json=payload)
        data = res.json()
        
        # Ochiq API ba'zan ro'yxat qaytaradi, tekshiramiz
        if isinstance(data, list) and len(data) > 0:
            javob = data[0].get('generated_text', '').split("<|assistant|>\n")[-1].strip().upper()
        else:
            javob = str(data).upper()
        
        if "XAVFLI" in javob:
            return {"status": "fishing"}
        else:
            # Agar sun'iy intellekt yuklamasi band bo'lsa, zaxira filtri ishlaydi
            matn_lower = sayt.matn.lower()
            if any(soz in matn_lower for soz in ["karta", "kod", "sms", "yutuq"]):
                return {"status": "fishing"}
            return {"status": "xavfsiz"}
            
    except Exception as e:
        # Tarmoqda xato bo'lsa ham foydalanuvchini himoya qilish uchun zaxira filtri
        matn_lower = sayt.matn.lower()
        if any(soz in matn_lower for soz in ["karta", "kod", "sms", "yutuq"]):
            return {"status": "fishing"}
        return {"status": "xavfsiz"}
