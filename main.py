from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import io
import random
import qrcode

app = FastAPI(
    title="VEROLIS Sentinel V2.0 — CVMH Demo",
    version="1.0.0",
    description="Démonstrateur interactif : données simulées, non connectées à des capteurs réels."
)

app.mount("/static", StaticFiles(directory="static"), name="static")

state = {"scenario": "optimal"}

def now():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def build_state(scenario):
    if scenario == "secheresse":
        return {
            "scenario": "secheresse",
            "agri": {
                "status": "ALERTE",
                "humidity": 22,
                "prediction": "-40% rendement (scénario)",
                "decision": "Irrigation immédiate — scénario de démonstration",
                "action": "IRRIGUER",
                "severity": "critical"
            },
            "entropia": {
                "diagnosis": "Stress hydrique",
                "probability": 91,
                "recommendation": "Vérifier irrigation et état foliaire",
                "severity": "warning"
            },
            "communion": {
                "lot": "GOMBE-452",
                "price": "0 $/kg",
                "traceability": "LOT BLOQUÉ — simulation",
                "esg": "Contrôle qualité requis",
                "status": "NON VENDABLE",
                "severity": "critical"
            }
        }

    if scenario == "maladie":
        return {
            "scenario": "maladie",
            "agri": {
                "status": "OPTIMAL",
                "humidity": 68,
                "prediction": "+25% rendement (scénario)",
                "decision": "Maintenir — surveillance active",
                "action": "SURVEILLER",
                "severity": "ok"
            },
            "entropia": {
                "diagnosis": "Mosaïque virale — scénario",
                "probability": 87,
                "recommendation": "Isoler la zone et confirmer par diagnostic agronomique",
                "severity": "critical"
            },
            "communion": {
                "lot": "GOMBE-452",
                "price": "0 $/kg",
                "traceability": "LOT EN CONTRÔLE — simulation",
                "esg": "Vérification qualité requise",
                "status": "BLOQUÉ",
                "severity": "critical"
            }
        }

    # optimal
    return {
        "scenario": "optimal",
        "agri": {
            "status": "OPTIMAL",
            "humidity": 68,
            "prediction": "+25% rendement (scénario)",
            "decision": "Maintenir — irrigation J+1 (simulation)",
            "action": "OK",
            "severity": "ok"
        },
        "entropia": {
            "diagnosis": "Saine — scénario",
            "probability": 95,
            "recommendation": "Surveillance normale",
            "severity": "ok"
        },
        "communion": {
            "lot": "GOMBE-452",
            "price": "1.20 $/kg",
            "traceability": "Traçabilité simulée",
            "esg": "Contrôle qualité à confirmer",
            "status": "PRÊT À ÉVALUER",
            "severity": "ok"
        }
    }

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/api/sentinelles")
def sentinelles():
    data = build_state(state["scenario"])
    data["timestamp"] = now()
    data["mode"] = "SIMULATION"
    data["source"] = "Données générées pour démonstration"
    return data

@app.post("/api/simulate/{scenario}")
def simulate(scenario: str):
    if scenario not in {"optimal", "secheresse", "maladie"}:
        return {"error": "Scénario inconnu"}
    state["scenario"] = scenario
    data = build_state(scenario)
    data["timestamp"] = now()
    data["mode"] = "SIMULATION"
    return data

@app.get("/api/qr")
def qr(lot: str = "GOMBE-452"):
    payload = f"VEROLIS|LOT={lot}|MODE=DEMO|STATUS=SIMULATION"
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
