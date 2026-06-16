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

# 🚀 Bu tekin va ochiq kalit, profil to'ldirish shart emas!
HF_API_KEY = "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"
URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

class SaytMaoruz(BaseModel):
    matn: str

tizim_yoʻriqnomasi = (
    "Siz kiberxavfsizlik mutaxassissiz. Agar matnda plastik karta o'g'irlash, "
    "soxta yutuq yoki SMS kod so'rash bo'lsa 'XAVFLI', aks holda 'XAVFSIZ' deb javob bering. "
    "Faqat shu ikki so'zdan birini qaytaring, ortiqcha tushuntirish yozmang."
)

@app.post("/tahlil")
async def tahlil_qil(sayt: SaytMaoruz):
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "inputs": f"<|system|>\n{tizim_yoʻriqnomasi}\n<|user|>\n{sayt.matn}\n<|assistant|>\n",
            "parameters": {"max_new_tokens": 10, "temperature": 0.1}
        }
        
        res = requests.post(URL, json=payload, headers=headers)
        data = res.json()
        
        # Kelgan javob matnini tekshiramiz
        javob = data[0]['generated_text'].split("<|assistant|>\n")[-1].strip()
        
        if "XAVFLI" in javob.upper():
            return {"status": "fishing"}
        else:
            return {"status": "xavfsiz"}
            
    except Exception as e:
        return {"status": "XATO", "error": str(e)}
