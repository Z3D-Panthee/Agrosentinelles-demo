from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Sentinel OS & TTD Oracle - Offline Mode")

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
    return {"status": "Sentinel OS Core OK"}

@app.get("/sw.js")
def service_worker():
    """Sert le Service Worker pour la PWA offline."""
    if os.path.exists("sw.js"):
        return FileResponse("sw.js", media_type="application/javascript")
    return {"error": "sw.js not found"}

@app.get("/manifest.json")
def manifest():
    """Sert le manifeste de l'application."""
    if os.path.exists("manifest.json"):
        return FileResponse("manifest.json", media_type="application/json")
    return {"error": "manifest.json not found"}

@app.get("/health")
def health():
    return {"status": "ok", "mode": "offline-first", "epsilon": 1e-5}

@app.get("/api/ligo-box/v1")
def ligo_box_telemetry():
    return {
        "module": "Ligo-Box V1.2",
        "statut": "Operationnel hors-ligne",
        "parametres": {"Tr_T": 0, "RC_RI": 0, "epsilon": 1e-5}
    }
