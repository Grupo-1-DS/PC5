from fastapi import FastAPI, HTTPException
from pathlib import Path
import json
import uvicorn

app = FastAPI(title="Secret guardian API")

EVIDENCE_PATH = Path(__file__).resolve().parent.parent / "evidence"
SECRETS_SCAN_JSON = EVIDENCE_PATH / "secrets-scan.json"

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/scan-result")
def scan_result():
    if not SECRETS_SCAN_JSON.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró {SECRETS_SCAN_JSON}")

    data = json.loads(SECRETS_SCAN_JSON.read_text(encoding="utf-8"))
    return data

@app.get("/config-check")
def config_check():
    rules = {
        "patterns": ["API_KEY", "PASSWORD", "PRIVATE_KEY"],
    }
    return {"rules": rules}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)