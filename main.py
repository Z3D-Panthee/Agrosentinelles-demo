from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import sqlite3
import os
import json

# ============================================================
# AGROSENTINELLES ADMIN V5.0 — FINALE & INTEGRALE
# Backend FastAPI — Offline First / SQLite / Synchronisation Batch
# VÉROLIS SARL × Sentinel OS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "agrosentinelles.db")

app = FastAPI(
    title="AGROSENTINELLES ADMIN V5.0",
    description="Administration agricole, traçabilité et intelligence Sentinel OS",
    version="5.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# DATABASE & INITIALISATION
# ------------------------------------------------------------

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS exploitations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE,
        localisation TEXT DEFAULT '',
        superficie REAL DEFAULT 0,
        culture TEXT DEFAULT '',
        statut TEXT DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS producteurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        telephone TEXT DEFAULT '',
        exploitation_id INTEGER,
        statut TEXT DEFAULT 'ACTIF',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS parcelles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        culture TEXT DEFAULT '',
        superficie REAL DEFAULT 0,
        exploitation_id INTEGER,
        statut TEXT DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS lots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        produit TEXT NOT NULL,
        quantite REAL DEFAULT 0,
        unite TEXT DEFAULT 'kg',
        origine TEXT DEFAULT '',
        statut TEXT DEFAULT 'EN_STOCK',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produit TEXT NOT NULL UNIQUE,
        quantite REAL DEFAULT 0,
        unite TEXT DEFAULT 'kg',
        emplacement TEXT DEFAULT '',
        seuil REAL DEFAULT 0,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS alertes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        niveau TEXT DEFAULT 'INFO',
        titre TEXT NOT NULL,
        message TEXT DEFAULT '',
        statut TEXT DEFAULT 'OUVERTE',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        module TEXT DEFAULT 'SYSTEM',
        details TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# MODELS PYDANTIC (Validation stricte)
# ------------------------------------------------------------

class ExploitationIn(BaseModel):
    nom: str = Field(min_length=1)
    localisation: str = ""
    superficie: float = 0
    culture: str = ""
    statut: str = "ACTIVE"


class ProducteurIn(BaseModel):
    nom: str = Field(min_length=1)
    telephone: str = ""
    exploitation_id: Optional[int] = None
    statut: str = "ACTIF"


class ParcelleIn(BaseModel):
    code: str = Field(min_length=1)
    culture: str = ""
    superficie: float = 0
    exploitation_id: Optional[int] = None
    statut: str = "ACTIVE"


class LotIn(BaseModel):
    code: str = Field(min_length=1)
    produit: str = Field(min_length=1)
    quantite: float = 0
    unite: str = "kg"
    origine: str = ""
    statut: str = "EN_STOCK"


class StockIn(BaseModel):
    produit: str = Field(min_length=1)
    quantite: float = 0
    unite: str = "kg"
    emplacement: str = ""
    seuil: float = 0


class AlerteIn(BaseModel):
    niveau: str = "INFO"
    titre: str = Field(min_length=1)
    message: str = ""
    statut: str = "OUVERTE"


class SyncPayload(BaseModel):
    operations: List[Dict[str, Any]] = []


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def now():
    return datetime.now(timezone.utc).isoformat()


def log_action(action, module="SYSTEM", details=""):
    try:
        conn = db()
        conn.execute(
            "INSERT INTO journal(action,module,details,created_at) VALUES(?,?,?,?)",
            (action, module, details, now())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def rows(table, limit=200):
    conn = db()
    result = [dict(r) for r in conn.execute(
        f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()]
    conn.close()
    return result


def insert_and_return(table, data):
    keys = list(data.keys())
    placeholders = ",".join(["?"] * len(keys))
    sql = f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders})"

    conn = db()
    cur = conn.execute(sql, [data[k] for k in keys])
    conn.commit()
    item = dict(conn.execute(
        f"SELECT * FROM {table} WHERE id=?", (cur.lastrowid,)
    ).fetchone())
    conn.close()
    return item


# ------------------------------------------------------------
# FRONTEND / PWA ROUTES
# ------------------------------------------------------------

@app.get("/")
def home():
    path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"status": "AGROSENTINELLES ADMIN V5.0", "error": "index.html absent"}, status_code=404)


@app.get("/sw.js")
def service_worker():
    path = os.path.join(BASE_DIR, "sw.js")
    if os.path.exists(path):
        return FileResponse(path, media_type="application/javascript")
    return JSONResponse({"error": "sw.js not found"}, status_code=404)


@app.get("/manifest.json")
def manifest():
    path = os.path.join(BASE_DIR, "manifest.json")
    if os.path.exists(path):
        return FileResponse(path, media_type="application/json")
    return JSONResponse({"error": "manifest.json not found"}, status_code=404)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": "AGROSENTINELLES ADMIN",
        "version": "5.0.0",
        "mode": "offline-first",
        "database": "sqlite",
        "sentinel": "active",
        "epsilon": 1e-5,
        "timestamp": now()
    }


# ------------------------------------------------------------
# DASHBOARD API
# ------------------------------------------------------------

@app.get("/api/dashboard")
def dashboard():
    conn = db()
    def count(table):
        try:
            return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except Exception:
            return 0

    stats = {
        "exploitations": count("exploitations"),
        "producteurs": count("producteurs"),
        "parcelles": count("parcelles"),
        "lots": count("lots"),
        "stocks": count("stocks"),
        "alertes_ouvertes": conn.execute(
            "SELECT COUNT(*) FROM alertes WHERE statut='OUVERTE'"
        ).fetchone()[0] if count("alertes") > 0 else 0,
        "lots_en_stock": conn.execute(
            "SELECT COALESCE(SUM(quantite),0) FROM lots WHERE statut='EN_STOCK'"
        ).fetchone()[0] if count("lots") > 0 else 0,
    }
    conn.close()

    return {
        "application": "AGROSENTINELLES ADMIN V5.0",
        "organisation": "VÉROLIS SARL",
        "moteur": "Sentinel OS",
        "status": "OPERATIONNEL",
        "stats": stats,
        "offline_first": True,
        "timestamp": now()
    }


# ------------------------------------------------------------
# EXPLOITATIONS API
# ------------------------------------------------------------

@app.get("/api/exploitations")
def get_exploitations():
    return rows("exploitations")


@app.post("/api/exploitations")
def create_exploitation(item: ExploitationIn):
    try:
        result = insert_and_return(
            "exploitations",
            {**item.model_dump(), "created_at": now()}
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Cette exploitation existe déjà")
    log_action("Création exploitation", "EXPLOITATIONS", item.nom)
    return result


# ------------------------------------------------------------
# PRODUCTEURS API
# ------------------------------------------------------------

@app.get("/api/producteurs")
def get_producteurs():
    return rows("producteurs")


@app.post("/api/producteurs")
def create_producteur(item: ProducteurIn):
    result = insert_and_return(
        "producteurs",
        {**item.model_dump(), "created_at": now()}
    )
    log_action("Création producteur", "PRODUCTEURS", item.nom)
    return result


# ------------------------------------------------------------
# PARCELLES API
# ------------------------------------------------------------

@app.get("/api/parcelles")
def get_parcelles():
    return rows("parcelles")


@app.post("/api/parcelles")
def create_parcelle(item: ParcelleIn):
    try:
        result = insert_and_return(
            "parcelles",
            {**item.model_dump(), "created_at": now()}
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Ce code de parcelle existe déjà")
    log_action("Création parcelle", "PARCELLES", item.code)
    return result


# ------------------------------------------------------------
# LOTS / TRAÇABILITÉ API
# ------------------------------------------------------------

@app.get("/api/lots")
def get_lots():
    return rows("lots")


@app.post("/api/lots")
def create_lot(item: LotIn):
    try:
        result = insert_and_return(
            "lots",
            {**item.model_dump(), "created_at": now()}
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Code de lot déjà existant")
    log_action("Création lot", "TRAÇABILITE", item.code)
    return result


# ------------------------------------------------------------
# STOCKS API
# ------------------------------------------------------------

@app.get("/api/stocks")
def get_stocks():
    return rows("stocks")


@app.post("/api/stocks")
def create_stock(item: StockIn):
    try:
        result = insert_and_return(
            "stocks",
            {**item.model_dump(), "updated_at": now()}
        )
    except sqlite3.IntegrityError:
        conn = db()
        conn.execute(
            "UPDATE stocks SET quantite=?, unite=?, emplacement=?, seuil=?, updated_at=? WHERE produit=?",
            (item.quantite, item.unite, item.emplacement, item.seuil, now(), item.produit)
        )
        conn.commit()
        result = dict(conn.execute("SELECT * FROM stocks WHERE produit=?", (item.produit,)).fetchone())
        conn.close()

    log_action("Mise à jour stock", "STOCK", item.produit)
    return result


# ------------------------------------------------------------
# ALERTES API
# ------------------------------------------------------------

@app.get("/api/alertes")
def get_alertes():
    return rows("alertes")


@app.post("/api/alertes")
def create_alerte(item: AlerteIn):
    result = insert_and_return(
        "alertes",
        {**item.model_dump(), "created_at": now()}
    )
    log_action("Nouvelle alerte", "ALERTES", item.titre)
    return result


# ------------------------------------------------------------
# JOURNAL ADMINISTRATIF API
# ------------------------------------------------------------

@app.get("/api/journal")
def get_journal():
    return rows("journal")


# ------------------------------------------------------------
# SYNCHRONISATION OFFLINE AVANCÉE (BIRDRECTIONNELLE BATCH)
# ------------------------------------------------------------

@app.post("/api/sync")
def sync(payload: SyncPayload):
    operations = payload.operations
    accepted = 0
    errors = []

    conn = db()
    for op in operations:
        table = op.get("table")
        data = op.get("data", {})
        action_type = op.get("action", "INSERT")

        try:
            if table in ["exploitations", "producteurs", "parcelles", "lots", "stocks", "alertes"]:
                keys = list(data.keys())
                if keys:
                    placeholders = ",".join(["?"] * len(keys))
                    columns = ",".join(keys)
                    values = [data[k] for k in keys]
                    
                    # Tentative d'insertion sécurisée (ignore ou remplace en cas de doublon pour la synchro)
                    sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
                    conn.execute(sql, values)
                    conn.commit()
            
            log_action("SYNC_BATCH_OP", table or "UNKNOWN", json.dumps(data, ensure_ascii=False))
            accepted += 1
        except Exception as exc:
            errors.append(f"Erreur sur {table}: {str(exc)}")

    conn.close()

    return {
        "status": "SYNC_COMPLETE",
        "accepted": accepted,
        "errors": errors,
        "timestamp": now()
    }


# ------------------------------------------------------------
# SENTINEL OS / LIGO BOX API
# ------------------------------------------------------------

@app.get("/api/sentinel/status")
def sentinel_status():
    return {
        "system": "Sentinel OS",
        "version": "V5.0",
        "status": "OPERATIONNEL",
        "mode": "OFFLINE-FIRST",
        "intelligence": "ACTIVE",
        "traceability": "ACTIVE",
        "agriculture": "ACTIVE",
        "timestamp": now()
    }


@app.get("/api/ligo-box/v1")
def ligo_box_telemetry():
    return {
        "module": "Ligo-Box V1.2",
        "statut": "Operationnel hors-ligne",
        "parametres": {
            "Tr_T": 0,
            "RC_RI": 0,
            "epsilon": 1e-5
        },
        "timestamp": now()
    }


# ------------------------------------------------------------
# STARTUP EVENT
# ------------------------------------------------------------

@app.on_event("startup")
def startup():
    init_db()
    log_action("Démarrage AGROSENTINELLES ADMIN V5.0", "SYSTEM")
