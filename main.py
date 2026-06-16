from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Brauzer bloklab qo'ymasligi uchun CORS sozlamasi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = 'AQ.Ab8RN6I0Y1AxqwoyiCH5Xm9y5bKaYY_j9LQS1AAa7GWZYB1qnQ'
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

class SaytMaoruz(BaseModel):
    matn: str

tizim_yoʻriqnomasi = (
    "Siz kiberxavfsizlik mutaxassissiz. Agar matnda plastik karta o'g'irlash, "
    "soxta yutuq yoki SMS kod so'rash bo'lsa 'XAVFLI', aks holda 'XAVFSIZ' deb javob bering. "
    "Ortiqcha so'z yozmang, faqat shu ikki so'zdan birini qaytaring."
)

@app.post("/tahlil")
async def tahlil_qil(sayt: SaytMaoruz):
    try:
        # Google serveriga to'g'ridan-to'g'ri so'rov yuboramiz
        payload = {
            "contents": [{"parts": [{"text": sayt.matn}]}],
            "systemInstruction": {"parts": [{"text": tizim_yoʻriqnomasi}]},
            "generationConfig": {"temperature": 0.1}
        }
        res = requests.post(GEMINI_URL, json=payload)
        data = res.json()
        natija = data['candidates'][0]['content']['parts'][0]['text'].strip()
        return {"status": natija}
    except Exception as e:
        return {"status": "XATO", "error": str(e)}