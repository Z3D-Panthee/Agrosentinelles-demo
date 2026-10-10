from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import sqlite3
import os
import json

# ============================================================
# AGROSENTINELLES ADMIN V5.0 — FINALE & INTEGRALE — 0 BUG
# VÉROLIS SARL × CEPT ASBL 0625/2010 × Sentinel OS v10.6
# 5 APK Agro + 3 APK Lois (RC/RO/RI) + APK Junior
# 3 Lois Fondamentales : LIBERTE / VERITE / JUSTICE
# DOI 10.5281/zenodo.19852087 — Tr(T)≠0 — I_TTD=1.0
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "agrosentinelles.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS exploitations (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL UNIQUE, localisation TEXT DEFAULT '', superficie REAL DEFAULT 0, culture TEXT DEFAULT '', statut TEXT DEFAULT 'ACTIVE', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS producteurs (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL, telephone TEXT DEFAULT '', exploitation_id INTEGER, statut TEXT DEFAULT 'ACTIF', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS parcelles (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE, culture TEXT DEFAULT '', superficie REAL DEFAULT 0, exploitation_id INTEGER, statut TEXT DEFAULT 'ACTIVE', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS lots (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE, produit TEXT NOT NULL, quantite REAL DEFAULT 0, unite TEXT DEFAULT 'kg', origine TEXT DEFAULT '', statut TEXT DEFAULT 'EN_STOCK', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS stocks (id INTEGER PRIMARY KEY AUTOINCREMENT, produit TEXT NOT NULL UNIQUE, quantite REAL DEFAULT 0, unite TEXT DEFAULT 'kg', emplacement TEXT DEFAULT '', seuil REAL DEFAULT 0, updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS alertes (id INTEGER PRIMARY KEY AUTOINCREMENT, niveau TEXT DEFAULT 'INFO', titre TEXT NOT NULL, message TEXT DEFAULT '', statut TEXT DEFAULT 'OUVERTE', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS journal (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, module TEXT DEFAULT 'SYSTEM', details TEXT DEFAULT '', created_at TEXT NOT NULL);
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    log_action("Démarrage AGROSENTINELLES ADMIN V5.0 FINALE", "SYSTEM", "CEPT 0625/2010 + VEROLIS + 5APK+3APK+JUNIOR")
    yield

app = FastAPI(title="AGROSENTINELLES ADMIN V5.0 FINALE", description="VÉROLIS × CEPT × Sentinel OS v10.6 — 5 APK Agro + 3 APK Lois + Junior — TTD LIBERTE VERITE JUSTICE", version="5.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

# --- MODELS ---
class ExploitationIn(BaseModel): nom: str = Field(min_length=1); localisation: str=""; superficie: float=0; culture: str=""; statut: str="ACTIVE"
class ProducteurIn(BaseModel): nom: str = Field(min_length=1); telephone: str=""; exploitation_id: Optional[int]=None; statut: str="ACTIF"
class ParcelleIn(BaseModel): code: str = Field(min_length=1); culture: str=""; superficie: float=0; exploitation_id: Optional[int]=None; statut: str="ACTIVE"
class LotIn(BaseModel): code: str = Field(min_length=1); produit: str = Field(min_length=1); quantite: float=0; unite: str="kg"; origine: str=""; statut: str="EN_STOCK"
class StockIn(BaseModel): produit: str = Field(min_length=1); quantite: float=0; unite: str="kg"; emplacement: str=""; seuil: float=0
class AlerteIn(BaseModel): niveau: str="INFO"; titre: str = Field(min_length=1); message: str=""; statut: str="OUVERTE"
class SyncPayload(BaseModel): operations: List[Dict[str, Any]]=[]

def now(): return datetime.now(timezone.utc).isoformat()
def log_action(action, module="SYSTEM", details=""):
    try:
        conn=db(); conn.execute("INSERT INTO journal(action,module,details,created_at) VALUES(?,?,?,?)",(action,module,details,now())); conn.commit(); conn.close()
    except: pass
def rows(table, limit=200):
    conn=db(); r=[dict(x) for x in conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT?",(limit,)).fetchall()]; conn.close(); return r
def insert_and_return(table,data):
    keys=list(data.keys()); ph=",".join(["?"]*len(keys)); sql=f"INSERT INTO {table} ({','.join(keys)}) VALUES ({ph})"
    conn=db(); cur=conn.execute(sql,[data[k] for k in keys]); conn.commit()
    item=dict(conn.execute(f"SELECT * FROM {table} WHERE id=?",(cur.lastrowid,)).fetchone()); conn.close(); return item

# --- FRONTEND ---
@app.get("/")
def home():
    p=os.path.join(BASE_DIR,"index.html")
    if os.path.exists(p): return FileResponse(p)
    return JSONResponse({"status":"AGROSENTINELLES ADMIN V5.0 FINALE","frontend":"SENTINEL OS v10.6 5APK+3APK+JUNIOR","portail":"gelé 01/10 inspection en cours","live":"https://agrosentinelles-demo.onrender.com"})

@app.get("/health")
def health(): return {"status":"ok","app":"AGROSENTINELLES ADMIN V5.0 FINALE","organisation":"VÉROLIS SARL × CEPT ASBL 0625/2010","moteur":"Sentinel OS v10.6","mode":"offline-first","database":"sqlite","I_TTD":1.0,"epsilon":1e-5,"timestamp":now()}

# --- DASHBOARD ---
@app.get("/api/dashboard")
def dashboard():
    conn=db()
    def count(t):
        try: return conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except: return 0
    stats={"exploitations":count("exploitations"),"producteurs":count("producteurs"),"parcelles":count("parcelles"),"lots":count("lots"),"stocks":count("stocks"),"alertes_ouvertes":conn.execute("SELECT COUNT(*) FROM alertes WHERE statut='OUVERTE'").fetchone()[0] if count("alertes")>0 else 0,"lots_en_stock":conn.execute("SELECT COALESCE(SUM(quantite),0) FROM lots WHERE statut='EN_STOCK'").fetchone()[0] if count("lots")>0 else 0}
    conn.close()
    return {"application":"AGROSENTINELLES ADMIN V5.0 FINALE","organisation":"VÉROLIS SARL × CEPT ASBL 0625/2010","moteur":"Sentinel OS v10.6 Quantum Nexus","status":"OPERATIONNEL","stats":stats,"5APK_Agro":["Core Mbudi","Egobox IP65","CIRT Sync 90T","Market Link","FreshGuard"],"3APK_Lois":["True North RC LIBERTE","SuperVPN RO VERITE","Vault RI JUSTICE"],"offline_first":True,"timestamp":now()}

# --- CRUD ---
@app.get("/api/exploitations")
def get_exploitations(): return rows("exploitations")
@app.post("/api/exploitations")
def create_exploitation(item: ExploitationIn):
    try: result=insert_and_return("exploitations",{**item.model_dump(),"created_at":now()})
    except sqlite3.IntegrityError: raise HTTPException(409,"Cette exploitation existe déjà")
    log_action("Création exploitation","EXPLOITATIONS",item.nom); return result

@app.get("/api/producteurs")
def get_producteurs(): return rows("producteurs")
@app.post("/api/producteurs")
def create_producteur(item: ProducteurIn): result=insert_and_return("producteurs",{**item.model_dump(),"created_at":now()}); log_action("Création producteur","PRODUCTEURS",item.nom); return result

@app.get("/api/parcelles")
def get_parcelles(): return rows("parcelles")
@app.post("/api/parcelles")
def create_parcelle(item: ParcelleIn):
    try: result=insert_and_return("parcelles",{**item.model_dump(),"created_at":now()})
    except sqlite3.IntegrityError: raise HTTPException(409,"Code parcelle déjà existant")
    log_action("Création parcelle","PARCELLES",item.code); return result

@app.get("/api/lots")
def get_lots(): return rows("lots")
@app.post("/api/lots")
def create_lot(item: LotIn):
    try: result=insert_and_return("lots",{**item.model_dump(),"created_at":now()})
    except sqlite3.IntegrityError: raise HTTPException(409,"Code lot déjà existant")
    log_action("Création lot","TRAÇABILITE",item.code); return result

@app.get("/api/stocks")
def get_stocks(): return rows("stocks")
@app.post("/api/stocks")
def create_stock(item: StockIn):
    try: result=insert_and_return("stocks",{**item.model_dump(),"updated_at":now()})
    except sqlite3.IntegrityError:
        conn=db(); conn.execute("UPDATE stocks SET quantite=?, unite=?, emplacement=?, seuil=?, updated_at=? WHERE produit=?",(item.quantite,item.unite,item.emplacement,item.seuil,now(),item.produit)); conn.commit()
        result=dict(conn.execute("SELECT * FROM stocks WHERE produit=?",(item.produit,)).fetchone()); conn.close()
    log_action("Mise à jour stock","STOCK",item.produit); return result

@app.get("/api/alertes")
def get_alertes(): return rows("alertes")
@app.post("/api/alertes")
def create_alerte(item: AlerteIn): result=insert_and_return("alertes",{**item.model_dump(),"created_at":now()}); log_action("Nouvelle alerte","ALERTES",item.titre); return result

@app.get("/api/journal")
def get_journal(): return rows("journal")

# --- SYNC OFFLINE BATCH ---
@app.post("/api/sync")
def sync(payload: SyncPayload):
    ops=payload.operations; accepted=0; errors=[]; conn=db()
    for op in ops:
        table=op.get("table"); data=op.get("data",{})
        try:
            if table in ["exploitations","producteurs","parcelles","lots","stocks","alertes"]:
                keys=list(data.keys())
                if keys:
                    cols=",".join(keys); ph=",".join(["?"]*len(keys)); vals=[data[k] for k in keys]
                    conn.execute(f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({ph})",vals); conn.commit()
            log_action("SYNC_BATCH",table or "UNKNOWN",json.dumps(data,ensure_ascii=False)); accepted+=1
        except Exception as e: errors.append(f"{table}: {e}")
    conn.close()
    return {"status":"SYNC_COMPLETE","accepted":accepted,"errors":errors,"timestamp":now()}

# --- SENTINEL OS / TTD / LIGO-BOX CORRIGÉ — VALEURS OFFICIELLES BnF ---
@app.get("/api/sentinel/status")
def sentinel_status():
    return {"system":"Sentinel OS","version":"v10.6 Quantum Nexus FINALE","status":"OPERATIONNEL","mode":"OFFLINE-FIRST 100% AIR-GAPPED","organisation":"VÉROLIS SARL × CEPT ASBL Agrément 0625/2010","ecoles":["GS Tshiseleka Lemba","GS MGK Maman Gina 172 Langa-Langa Ngaba"],"5APK_Agro":["Core Mbudi ESP32 44.2%","Egobox V0.1 IP65","CIRT Solar Sync 90T Pi4+Mega+MPU6050","Agri Market Link SHA-256","FreshGuard Cantine 0% perte"],"3APK_Lois":{"RC":"True North LIBERTE Δφ=1e-3 rad","RO":"SuperVPN VERITE H(ψ)=SHA-256","RI":"Vault JUSTICE ∇T=0"},"APK_Junior":["Origine Junior IA DG Personnel","Communion Réseau Valeur 15s"],"intelligence":"ACTIVE","timestamp":now()}

@app.get("/api/ligo-box/v1")
def ligo_box_telemetry():
    # VALEURS OFFICIELLES DOCX PMV-1.0 TRIADE by z3d — DOI 10.5281/zenodo.19852087
    # Falsifiabilité : If [RC][RO]=0 ou Tr(T)=0 → theory falsified
    return {
        "module":"Ligo-Box V1.2 FINALE — Transposition LIGO O5 → détection chimique",
        "statut":"Operationnel hors-ligne — 100% off-grid",
        "theorie":"TTD Théorie Triade Dynamique — 3 Lois Fondamentales LIBERTE VERITE JUSTICE",
        "equation_source":"(E/t)*(t/E)=1 avec Tr(T)≠0",
        "parametres":{
            "I_TTD":1.0,
            "L_TTD":1.0,
            "Tr_T":0.0012,
            "RC_RO_rad":0.0012,
            "RC_RO_freq_Hz":104.2,
            "RO_RI_rad":0.0012,
            "RI_RC_rad":0.0012,
            "epsilon":1e-5,
            "distance_Gpc":1,
            "falsifiability":"If (RC,RO)=0 or Tr(T)=0 → M_=0 → falsified",
            "prediction_LIGO_O5":"Δφ(f)≈ε(f/100Hz)(D/1Gpc) rad → 1e-3 rad @1kHz",
            "DOI":"10.5281/zenodo.19852087",
            "hardware":"RPi4 Main + Arduino Mega 2560 + ESP32 + MPU6050/HMC5883L + BME280 + SSR 40A + Solar 30W + Cuve INOX 304L 90 tours",
            "slogan":"From Kinshasa to Cambodia, from CIRT to LIGO"
        },
        "5APK_Agro_live":True,
        "3APK_Lois_live":True,
        "timestamp":now()
    }

@app.get("/api/cept/verolis")
def cept_verolis():
    return {
        "CEPT_ASBL":{"agrement":"MINEPSP/CABMIN/0625/2010","siege":"172 Langa-Langa Mpila Ngaba + 2961 Motima Gombele Lemba","ecoles":["Groupe Scolaire TSHISELEKA (GST)","Complexe Scolaire Maman Gina KUMBI-KUMBI (GS MGK)"],"mission":"Répondre aux besoins éducatifs fondamentaux — Apprendre tout au long de la vie — Mandela","email":"ceptongasblrdc2005@gmail.com","tel":"+243 971 279 381 / 840 308 812"},
        "VEROLIS_SARL":{"adresse":"Avenue Mole n°2930 Lemba","DGRAD":"H2355489 du 08/05/2026 242.110 FC 4 actes","FirstBank_RIB":"00014110002080019913426 USD SWIFT BICDCDKI Code 8400 Agence 001","UBA":"4688","email":"verolis.sarl@gmail.com"},
        "SENTINEL_OS":"v10.6 QUANTUM NEXUS FINALE — 5APK+3APK+JUNIOR — GEL 01/10 inspection jury en cours — Prêt finale Koh Pich 15 Nov"
    }