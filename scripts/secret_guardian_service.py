from fastapi import FastAPI
from secret_guardian import main
import uvicorn
import os

app = FastAPI(title="Secret Guardian Service")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/scan")
def scan():
    result = main()
    return result


if __name__ == "__main__":
    port = int(os.getenv("SCANNER_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
