from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Brauzer bloklab qo'ymasligi uchun CORS sozlamasi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ MUHIM: Bu yerga AI Studio'dan olingan haqiqiy AIzaSy bilan boshlanadigan kalitni qo'ying!
API_KEY = "AQ.Ab8RN6INL0r-7d-7ehRlEboFGcBhbjQg-4X5K3YBX6tJNHJSbQ"
genai.configure(api_key=API_KEY)

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
        # Gemini modelini tizim yo'riqnomasi bilan birga sozlaymiz
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=tizim_yoʻriqnomasi
        )
        
        # Sayt matnini sun'iy intellektga yuboramiz
        response = model.generate_content(sayt.matn)
        
        # Kelgan javobni tozalab olamiz
        natija = response.text.strip()
        
        # Agar javob ichida XAVFLI degan so'z bo'lsa, plaginga 'fishing' deb qaytaramiz
        if "XAVFLI" in natija:
            return {"status": "fishing"}
        else:
            return {"status": "xavfsiz"}
            
    except Exception as e:
        # Konsolda xatoni aniq ko'rish uchun:
        print(f"Xatolik yuz berdi: {str(e)}")
        return {"status": "XATO", "error": str(e)}
