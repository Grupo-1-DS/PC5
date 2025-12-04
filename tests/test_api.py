import sys
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.main import app

ROOT = Path(__file__).resolve().parent.parent

client = TestClient(app)


@pytest.fixture
def create_and_clean_evidence():
    evidence_dir = ROOT / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    scan_file = evidence_dir / "secrets-scan.json"
    scan_file.write_text(
        '{"founded_count":1, \
        "founded_secrets":[{"type":"API Key","file":"test.py","line":15}]}',
        encoding="utf-8",
    )

    yield

    if scan_file.exists():
        scan_file.unlink()
        evidence_dir.rmdir()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_scan_result_success(create_and_clean_evidence):
    result = client.get("/scan-result")
    data = result.json()

    assert result.status_code == 200
    assert data["founded_count"] == 1
    assert data["founded_secrets"][0]["type"] == "API Key"


def test_scan_result_404():
    evidence_dir = ROOT / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    result = client.get("/scan-result")
    evidence_dir.rmdir()

    assert result.status_code == 404
