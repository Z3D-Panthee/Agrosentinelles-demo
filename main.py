from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, time, io, hashlib
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = FastAPI(title="SENTINEL OS v10.6 - CEPT 2 Ecoles + Mobile Money RDC")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB = "cept_2_ecoles.db"

LANGUAGES = {
    "fr": {"title": "Rapport Caisse CEPT", "eleves": "Élèves", "total": "Total Caisse", "ecole": "École"},
    "ln": {"title": "Raporan ya Mbongo ya CEPT", "eleves": "Basani", "total": "Molungango ya Mbongo", "ecole": "Sikola"},
    "kg": {"title": "Lapi ya Mbongo ya CEPT", "eleves": "Bandumba", "total": "Nzimbu Nionso", "ecole": "Nzo ya Nkanda"},
    "sw": {"title": "Ripoti ya Fedha ya CEPT", "eleves": "Wanafunzi", "total": "Jumla ya Fedha", "ecole": "Shule"}
}

MOBILE_MONEY = ["M-Pesa", "Orange Money", "Airtel Money", "Africell Money", "Cash"]

def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS ecoles (id INTEGER PRIMARY KEY, nom TEXT, adresse TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS eleves (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, classe TEXT, ecole_id INTEGER, frais_total INTEGER DEFAULT 50000)")
    # Nouvelle table paiements avec method + transaction_id SHA-256
    con.execute("CREATE TABLE IF NOT EXISTS paiements (id INTEGER PRIMARY KEY AUTOINCREMENT, eleve_id INTEGER, montant INTEGER, date INTEGER, ecole_id INTEGER, method TEXT DEFAULT 'Cash', txn_id TEXT)")
    if not con.execute("SELECT * FROM ecoles").fetchall():
        con.execute("INSERT INTO ecoles VALUES (1, 'GS Tshiseleka', '2961 Motima Gombele Lemba')")
        con.execute("INSERT INTO ecoles VALUES (2, 'GS Maman Gina KUMBI-KUMBI', '172 Langa-Langa Ngaba')")
    con.commit(); con.close()

init_db()

@app.get("/")
def root(): return FileResponse("index.html")

@app.get("/health")
def health(): return {"status": "LIVE", "I_TTD": 1.0, "ecoles": 2, "mobile_money": MOBILE_MONEY, "version": "10.6 Finale Mobile Money"}

@app.get("/api/ecoles")
def get_ecoles():
    con = sqlite3.connect(DB); rows = con.execute("SELECT * FROM ecoles").fetchall(); con.close()
    return [{"id": r[0], "nom": r[1], "adresse": r[2]} for r in rows]

@app.get("/api/eleves/{ecole_id}")
def get_eleves(ecole_id: int):
    con = sqlite3.connect(DB)
    eleves = con.execute("SELECT * FROM eleves WHERE ecole_id=?", (ecole_id,)).fetchall()
    caisse = con.execute("SELECT SUM(montant) FROM paiements WHERE ecole_id=?", (ecole_id,)).fetchone()[0] or 0
    # Caisse par operateur
    by_method = con.execute("SELECT method, SUM(montant) FROM paiements WHERE ecole_id=? GROUP BY method", (ecole_id,)).fetchall()
    con.close()
    return {
        "eleves": [{"id": e[0], "nom": e[1], "classe": e[2], "ecole_id": e[3]} for e in eleves],
        "caisse": caisse,
        "total": len(eleves),
        "by_method": {m[0]: m[1] for m in by_method}
    }

@app.post("/api/eleves/add")
def add_eleve(nom: str, classe: str = "Primaire", ecole_id: int = 1):
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO eleves (nom, classe, ecole_id) VALUES (?,?,?)", (nom, classe, ecole_id))
    con.commit(); con.close()
    return {"ok": True}

@app.post("/api/paiement/add")
def add_paiement(eleve_id: int, montant: int, ecole_id: int, method: str = "Cash"):
    if method not in MOBILE_MONEY: raise HTTPException(400, f"Method doit etre parmi {MOBILE_MONEY}")
    txn_raw = f"{eleve_id}-{montant}-{time.time()}-{method}"
    txn_id = hashlib.sha256(txn_raw.encode()).hexdigest()[:12].upper() # RO VERITE SHA-256
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO paiements (eleve_id, montant, date, ecole_id, method, txn_id) VALUES (?,?,?,?,?,?)",
                (eleve_id, montant, int(time.time()), ecole_id, method, txn_id))
    con.commit(); con.close()
    return {"ok": True, "txn_id": txn_id, "method": method, "message": f"Paiement {montant} CDF via {method} - TXN {txn_id}"}

# --- EXPORT EXCEL avec Mobile Money ---
@app.get("/api/export/excel/{ecole_id}")
def export_excel(ecole_id: int):
    con = sqlite3.connect(DB)
    df_e = pd.read_sql_query("SELECT id, nom, classe FROM eleves WHERE ecole_id=?", con, params=(ecole_id,))
    df_p = pd.read_sql_query("SELECT id, eleve_id, montant, method, txn_id, date FROM paiements WHERE ecole_id=?", con, params=(ecole_id,))
    con.close()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_e.to_excel(writer, sheet_name='Eleves', index=False)
        df_p.to_excel(writer, sheet_name='Paiements_MobileMoney', index=False)
    output.seek(0)
    headers = {'Content-Disposition': f'attachment; filename=CEPT_ecole_{ecole_id}_MobileMoney.xlsx'}
    return Response(output.read(), headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# --- EXPORT PDF avec detail par operateur ---
@app.get("/api/export/pdf/{ecole_id}")
def export_pdf(ecole_id: int, lang: str = "fr"):
    con = sqlite3.connect(DB)
    ecole = con.execute("SELECT nom FROM ecoles WHERE id=?", (ecole_id,)).fetchone()
    eleves = con.execute("SELECT COUNT(*) FROM eleves WHERE ecole_id=?", (ecole_id,)).fetchone()[0]
    caisse = con.execute("SELECT SUM(montant) FROM paiements WHERE ecole_id=?", (ecole_id,)).fetchone()[0] or 0
    by_method = con.execute("SELECT method, SUM(montant) FROM paiements WHERE ecole_id=? GROUP BY method", (ecole_id,)).fetchall()
    con.close()
    t = LANGUAGES.get(lang, LANGUAGES["fr"])
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"SENTINEL OS v10.6 - {t['title']} - {ecole[0]}")
    p.drawString(100, 730, f"{t['total']}: {caisse} CDF - {t['eleves']}: {eleves}")
    y=700
    p.drawString(100, y, "Detail Mobile Money RDC:")
    y-=20
    for m, total in by_method:
        p.drawString(120, y, f"- {m}: {total} CDF"); y-=20
    p.drawString(100, y-20, "Operateurs: M-Pesa * Orange Money * Airtel Money * Africell Money")
    p.drawString(100, y-40, "VEROLIS SARL x CEPT ASBL 0625/2010 - RC LIBERTE")
    p.showPage(); p.save(); buffer.seek(0)
    headers = {'Content-Disposition': f'attachment; filename=CEPT_{ecole_id}_{lang}_MobileMoney.pdf'}
    return Response(buffer.read(), headers=headers, media_type='application/pdf')