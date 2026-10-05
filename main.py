from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Agrosentinelles & Ligo-Box Demo - Vérolis SARL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "Agrosentinelles-demo OK", "auteur": "Dany Tshiseleka Thoka - Vérolis SARL"}

@app.get("/health")
def health():
    return {"status": "ok", "projet": "Sentinel OS & Ligo-Box v1.2", "epsilon": "1e-5"}

@app.get("/api/qr/{parcelle_id}")
def generate_qr(parcelle_id: str):
    return {
        "parcelle": parcelle_id,
        "qr_data": f"AGROSENTINELLES:{parcelle_id}:VEROLISxCVMH",
        "message": "QR Code prêt pour module 5 sentinelles"
    }

@app.get("/api/ligo-box/v1")
def ligo_box_telemetry():
    """Endpoint de télémétrie TTD et Ligo-Box pour le jury FrancoTech."""
    return {
        "module": "Ligo-Box V1.2",
        "tr_t": 0,
        "rc_ri": 0,
        "epsilon_simule": 1e-5,
        "delta_phi": "1e-3 rad @ 1kHz",
        "statut": "Operationnel - TTD Confirmee"
    }
