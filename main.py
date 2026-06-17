import os
import requests
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

# Hugging Face va Llama-3 sozlamalari
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
# O'zingizning Hugging Face Tokeningizni kiriting (agar o'zgargan bo'lsa)
HF_TOKEN = "hf_Sizning Tokeningiz Shu Yerda Bo'lsin" 
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.post("/tahlil")
async def tahlil_qil(sayt: SaytMaoruz):
    matn_lower = sayt.matn.lower()
    
    # ========================================================
    # 🛡️ 1-bosqich: BARCHA TURDAGI FISHING SO'ZLARI RO'YXATI (Zaxira)
    # ========================================================
    fishing_belgilari = [
        # Plastik karta o'g'rilari
        "plastik karta", "karta paroli", "sms kodni kiriting", "cvv", "kodni kiriting",
        # Telegram va ijtimoiy tarmoq o'g'rilari
        "telegramga kirish", "ovoz bering", "tg bot", "tasdiqlash kodi", "shaxsiy kabinet",
        # Soxta yutuq va investitsiyalar
        "yutuqni oling", "bepul megabayt", "pul mukofoti", "aksiyada qatnashish", "fondi taqdirlash",
        # Chet el xavfli so'zlari
        "card number", "card holder", "expiry date", "verify your account", "login to continue"
    ]
    
    # Agar matnda ushbu shubhali so'zlardan biri VA so'rov/forma elementlari qatnashsa:
    for belgi in fishing_belgilari:
        if belgi in matn_lower:
            # Oddiy yangilik saytlarini noto'g'ri bloklab qo'ymaslik uchun qo'shimcha filtr
            if "kiriting" in matn_lower or "oling" in matn_lower or "parol" in matn_lower or "login" in matn_lower:
                return {"status": "fishing"}

    # ========================================================
    # 🧠 2-bosqich: SUN'IY INTELLEKT (LLAMA-3) TAHLILI
    # ========================================================
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n" \
             f"Siz kiberxavfsizlik bo'yicha ekspertsiz. Berilgan matn fishing (firgarlik, ma'lumot o'g'irlash, soxta aksiya, soxta login) sayti ekanligini aniqlang. " \
             f"Faqat bitta so'z javob bering: agar fishing bo'lsa 'fishing', xavfsiz bo'lsa 'xavfsiz' deb yozing.<|eot_id|>" \
             f"<|start_header_id|>user<|end_header_id|>\n" \
             f"Matn:\n{sayt.matn[:1000]}\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"

    try:
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt, "parameters": {"max_new_tokens": 10}}, timeout=5)
        if response.status_code == 200:
            ai_javob = response.json()[0]['generated_text'].split("<|start_header_id|>assistant<|end_header_id|>\n")[-1].strip().lower()
            if "fishing" in ai_javob:
                return {"status": "fishing"}
    except Exception as e:
        print("AI tizimida xatolik, zaxira filtri ishladi:", e)

    # Agar hech qaysi filtrda shubha topilmasa
    return {"status": "xavfsiz"}
