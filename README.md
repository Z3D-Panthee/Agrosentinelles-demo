# 5-sentinelles-demo — VEROLIS × CVMH

Démonstrateur FastAPI + HTML des 3 Sentinelles :
- AGRI-ORIGINE
- ENTROPIA AGRO
- COMMUNION AGRO

Les données sont explicitement simulées.

## Lancer localement

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Puis ouvrir `http://127.0.0.1:8000`.

## Déploiement Render

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## API

- `GET /api/sentinelles`
- `POST /api/simulate/optimal`
- `POST /api/simulate/secheresse`
- `POST /api/simulate/maladie`
- `GET /api/qr?lot=GOMBE-452`

Le QR contient un identifiant de démonstration, pas une preuve de certification.
