from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Agrosentinelles Demo - Z3D")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    # index.html est à la racine
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "Agrosentinelles-demo OK", "auteur": "Z3D-Panthere"}

@app.get("/health")
def health():
    return {"status": "ok", "projet": "Agrosentinelles - AIIFAC"}

@app.get("/api/qr/{parcelle_id}")
def generate_qr(parcelle_id: str):
    return {
        "parcelle": parcelle_id,
        "qr_data": f"AGROSENTINELLES:{parcelle_id}:VEROLISxCVMH",
        "message": "QR Code prêt pour module 5 sentinelles"
    }