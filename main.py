from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os, io, hashlib, time
import pandas as pd
from reportlab.pdfgen import canvas

app = FastAPI(title="SENTINEL OS v10.6 QUANTUM NEXUS - LIVE")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB = {
  1: {"nom": "GS Tshiseleka - 2961 Motima - Lemba", "eleves": [], "paiements": [], "caisse": 0},
  2: {"nom": "GS Maman Gina KUMBI - 172 Langa - Ngaba", "eleves": [], "paiements": [], "caisse": 0},
}
ID_COUNTER = 1

@app.get("/health")
def health():
    return {
        "status": "LIVE",
        "I_TTD": 1.0,
        "L_TTD": 1.0,
        "epsilon": 1e-5,
        "Tr_T": 0.0012,
        "RC_RO": 0.0012,
        "DOI": "10.5281/zenodo.19852087",
        "ecoles": 2,
        "mobile_money": ["M-Pesa","Orange Money","Airtel Money","Africell Money","Cash"],
        "os": "SENTINEL OS v10.6 QUANTUM NEXUS FINALE - From Kinshasa to Cambodia"
    }

@app.get("/api/eleves/{ecole_id}")
def get_eleves(ecole_id: int):
    eco = DB.get(ecole_id, DB[1])
    by_method = {}
    for p in eco["paiements"]:
        by_method[p["method"]] = by_method.get(p["method"], 0) + p["montant"]
    return {
        "total": len(eco["eleves"]),
        "caisse": eco["caisse"],
        "by_method": by_method,
        "eleves": eco["eleves"]
    }

@app.post("/api/eleves/add")
def add_eleve(nom: str = Query(...), ecole_id: int = Query(1)):
    global ID_COUNTER
    eco = DB.get(ecole_id, DB[1])
    eleve = {"id": ID_COUNTER, "nom": nom, "classe": "Futur", "ecole_id": ecole_id}
    eco["eleves"].append(eleve)
    ID_COUNTER += 1
    return eleve

@app.post("/api/paiement/add")
def add_paiement(eleve_id: int = Query(...), montant: int = Query(5000), ecole_id: int = Query(1), method: str = Query("M-Pesa")):
    eco = DB.get(ecole_id, DB[1])
    txn_raw = f"{eleve_id}{montant}{method}{time.time()}".encode()
    txn_id = "TXN-" + hashlib.sha256(txn_raw).hexdigest()[:16].upper()
    eco["caisse"] += int(montant)
    eco["paiements"].append({"eleve_id": eleve_id, "montant": int(montant), "method": method, "txn_id": txn_id})
    return {"status": "PAID", "method": method, "txn_id": txn_id, "message": f"Paiement {method} validé - École {ecole_id} - CEPT 0625/2010"}

@app.get("/api/export/excel/{ecole_id}")
def export_excel(ecole_id: int):
    eco = DB.get(ecole_id, DB[1])
    df = pd.DataFrame(eco["eleves"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Eleves")
        pd.DataFrame(eco["paiements"]).to_excel(writer, index=False, sheet_name="Paiements")
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=CEPT_Ecole_{ecole_id}_v10_6.xlsx"})

@app.get("/api/export/pdf/{ecole_id}")
def export_pdf(ecole_id: int, lang: str = "fr"):
    eco = DB.get(ecole_id, DB[1])
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, 800, f"SENTINEL OS v10.6 - {eco['nom']} - CEPT 0625/2010")
    c.setFont("Helvetica", 10)
    c.drawString(30, 780, f"Caisse: {eco['caisse']} CDF | Eleves: {len(eco['eleves'])} | DOI 10.5281/zenodo.19852087")
    y = 760
    for e in eco["eleves"][:40]:
        c.drawString(30, y, f"{e['id']} - {e['nom']} - {e['classe']}")
        y -= 14
    c.save()
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=CEPT_Ecole_{ecole_id}_v10_6.pdf"})

@app.get("/")
def serve_index():
    return FileResponse("index.html") if os.path.exists("index.html") else {"msg": "index.html manquant"}

@app.get("/manifest.json")
def serve_manifest():
    return FileResponse("manifest.json") if os.path.exists("manifest.json") else {"msg": "manifest manquant"}

@app.get("/service-worker.js")
def serve_sw():
    return FileResponse("service-worker.js") if os.path.exists("service-worker.js") else {"msg": "sw manquant"}

@app.get("/script.js")
def serve_script():
    return FileResponse("script.js") if os.path.exists("script.js") else {"msg": "script manquant"}

@app.get("/icon.png")
def serve_icon():
    return FileResponse("icon.png") if os.path.exists("icon.png") else {"msg": "icon manquant"}

@app.get("/{path:path}")
def serve_static_fallback(path: str):
    if os.path.exists(path) and os.path.isfile(path):
        return FileResponse(path)
    return FileResponse("index.html") if os.path.exists("index.html") else {"msg": "Not found"}
