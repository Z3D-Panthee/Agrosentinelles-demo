from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, time, io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = FastAPI(title="SENTINEL OS v10.6 - CEPT 2 Ecoles (PDF, Excel & Multilingue)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB = "cept_2_ecoles.db"

# Dictionnaire des 4 langues nationales de la RDC pour l'interface et les rapports
LANGUAGES = {
    "fr": {"title": "Rapport Caisse CEPT", "eleves": "Élèves", "total": "Total Caisse", "ecole": "École"},
    "ln": {"title": "Raporan ya Mbongo ya CEPT", "eleves": "Basani / Bana", "total": "Molungango ya Mbongo", "ecole": "Sikola"},
    "kg": {"title": "Lapi ya Mbongo ya CEPT", "eleves": "Bandumba", "total": "Nzimbu Nionso", "ecole": "Nzo ya Nkanda"},
    "sw": {"title": "Ripoti ya Fedha ya CEPT", "eleves": "Wanafunzi", "total": "Jumla ya Fedha", "ecole": "Shule"}
}

def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS ecoles (id INTEGER PRIMARY KEY, nom TEXT, adresse TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS eleves (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, classe TEXT, ecole_id INTEGER, frais_total INTEGER DEFAULT 50000)")
    con.execute("CREATE TABLE IF NOT EXISTS paiements (id INTEGER PRIMARY KEY AUTOINCREMENT, eleve_id INTEGER, montant INTEGER, date INTEGER, ecole_id INTEGER)")
    
    if not con.execute("SELECT * FROM ecoles").fetchall():
        con.execute("INSERT INTO ecoles VALUES (1, 'GS Tshiseleka', '2961 Motima Gombele Lemba')")
        con.execute("INSERT INTO ecoles VALUES (2, 'GS Maman Gina KUMBI-KUMBI', '172 Langa-Langa Ngaba')")
    con.commit(); con.close()

init_db()

@app.get("/")
def root(): return FileResponse("index.html")

@app.get("/health")
def health(): return {"status": "LIVE", "I_TTD": 1.0, "L_TTD": 1.0, "ecoles": 2, "version": "10.6 Finale Multilingue & Docs"}

@app.get("/api/ecoles")
def get_ecoles():
    con = sqlite3.connect(DB); rows = con.execute("SELECT * FROM ecoles").fetchall(); con.close()
    return [{"id": r[0], "nom": r[1], "adresse": r[2]} for r in rows]

@app.get("/api/eleves/{ecole_id}")
def get_eleves(ecole_id: int):
    con = sqlite3.connect(DB)
    eleves = con.execute("SELECT * FROM eleves WHERE ecole_id=?", (ecole_id,)).fetchall()
    caisse = con.execute("SELECT SUM(montant) FROM paiements WHERE ecole_id=?", (ecole_id,)).fetchone()[0] or 0
    con.close()
    return {"eleves": [{"id": e[0], "nom": e[1], "classe": e[2], "ecole_id": e[3]} for e in eleves], "caisse": caisse, "total": len(eleves)}

@app.post("/api/eleves/add")
def add_eleve(nom: str, classe: str = "Primaire", ecole_id: int = 1):
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO eleves (nom, classe, ecole_id) VALUES (?,?,?)", (nom, classe, ecole_id))
    con.commit(); con.close()
    return {"ok": True}

@app.post("/api/paiement/add")
def add_paiement(eleve_id: int, montant: int, ecole_id: int):
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO paiements (eleve_id, montant, date, ecole_id) VALUES (?,?,?,?)", (eleve_id, montant, int(time.time()), ecole_id))
    con.commit(); con.close()
    return {"ok": True}

# --- EXPORT EXCEL ---
@app.get("/api/export/excel/{ecole_id}")
def export_excel(ecole_id: int):
    con = sqlite3.connect(DB)
    df_eleves = pd.read_sql_query("SELECT id, nom, classe FROM eleves WHERE ecole_id = ?", con, params=(ecole_id,))
    df_paiements = pd.read_sql_query("SELECT id, eleve_id, montant, date FROM paiements WHERE ecole_id = ?", con, params=(ecole_id,))
    con.close()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_eleves.to_excel(writer, sheet_name='Eleves', index=False)
        df_paiements.to_excel(writer, sheet_name='Paiements', index=False)
    output.seek(0)

    headers = {'Content-Disposition': f'attachment; filename=rapport_ecole_{ecole_id}.xlsx'}
    return Response(output.read(), headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# --- EXPORT PDF ---
@app.get("/api/export/pdf/{ecole_id}")
def export_pdf(ecole_id: int, lang: str = "fr"):
    con = sqlite3.connect(DB)
    ecole = con.execute("SELECT nom, adresse FROM ecoles WHERE id = ?", (ecole_id,)).fetchone()
    eleves = con.execute("SELECT COUNT(*) FROM eleves WHERE ecole_id = ?", (ecole_id,)).fetchone()[0]
    caisse = con.execute("SELECT SUM(montant) FROM paiements WHERE ecole_id = ?", (ecole_id,)).fetchone()[0] or 0
    con.close()

    t = LANGUAGES.get(lang, LANGUAGES["fr"])
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"SENTINEL OS v10.6 — {t['title']}")
    p.drawString(100, 725, f"{t['ecole']}: {ecole[0]} ({ecole[1]})")
    p.drawString(100, 700, f"--------------------------------------------------")
    p.drawString(100, 675, f"Total {t['eleves']}: {eleves}")
    p.drawString(100, 650, f"{t['total']}: {caisse} $")
    p.drawString(100, 600, "Vérolis SARL x CEPT ASBL (Agrément 0625/2010)")
    p.showPage()
    p.save()
    
    buffer.seek(0)
    headers = {'Content-Disposition': f'attachment; filename=rapport_ecole_{ecole_id}.pdf'}
    return Response(buffer.read(), headers=headers, media_type='application/pdf')
