from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Agrosentinelles & Sentinel OS - Vérolis SARL",
    description="API de démonstration officielle pour le concours FrancoTech 2026",
    version="1.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    """Sert l'interface HTML principale si elle existe, sinon renvoie un statut JSON."""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {
        "status": "Agrosentinelles-demo OK",
        "auteur": "Dany Tshiseleka Thoka",
        "organisation": "Centre Éducation Pour Tous / Vérolis SARL"
    }

@app.get("/health")
def health():
    """Vérification de l'état du système et des paramètres TTD."""
    return {
        "status": "ok",
        "projet": "Sentinel OS v10 & Ligo-Box v1.2",
        "theorie": "Triade Dynamique (TTD)",
        "epsilon_cible": 1e-5
    }

@app.get("/api/qr/{parcelle_id}")
def generate_qr(parcelle_id: str):
    """Génération des données pour les QR codes des parcelles."""
    return {
        "parcelle": parcelle_id,
        "qr_data": f"AGROSENTINELLES:{parcelle_id}:VEROLISxCVMH",
        "message": "QR Code prêt pour module 5 sentinelles"
    }

@app.get("/api/ligo-box/v1")
def ligo_box_telemetry():
    """Télémétrie et mesures du prototype Ligo-Box V1.2 (Lien direct avec les spécifications techniques)."""
    return {
        "module": "Ligo-Box V1.2",
        "statut_operationnel": True,
        "parametres_physiques": {
            "Tr_T": 0,
            "RC_RI": 0,
            "epsilon_simule": 1e-5,
            "delta_phi": "1e-3 rad @ 1kHz / 1 Gpc"
        },
        "validation": "Conforme aux specs TTD - Prêt pour déploiement"
    }
