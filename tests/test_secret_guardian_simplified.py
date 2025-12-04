"""
Tests para secret_guardian.py
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from secret_guardian import SecretGuardian


@pytest.fixture
def scanner():
    return SecretGuardian()


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


# Tests basicos
class TestPatterns:

    def test_patterns_loaded(self, scanner):
        assert len(scanner.patterns) > 0
        assert len(scanner.patterns) == 8


# Tests con archivos
class TestDetection:

    def test_api_keys(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "api_keys.py")
        assert len(scanner.findings) > 0

    def test_passwords(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "passwords.py")
        assert len(scanner.findings) > 0

    def test_tokens(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "tokens.py")
        assert len(scanner.findings) > 0

    def test_aws_keys(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "aws_keys.py")
        assert len(scanner.findings) > 0

    def test_secret_keys(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "secret_keys.py")
        assert len(scanner.findings) > 0

    def test_private_keys(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "private_keys.py")
        assert len(scanner.findings) > 0

    def test_database_urls(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "database_urls.py")
        assert len(scanner.findings) > 0

    def test_bearer_tokens(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "bearer_tokens.py")
        assert len(scanner.findings) > 0

    def test_clean_file(self, scanner, fixtures_dir):
        scanner.scan_file(fixtures_dir / "clean_file.py")
        assert len(scanner.findings) == 0


# Test de exclusiones
class TestExclusions:

    def test_git_excluded(self, scanner):
        assert not scanner.should_scan_file(Path(".git/config"))

    def test_node_modules_excluded(self, scanner):
        assert not scanner.should_scan_file(Path("node_modules/package.json"))


# Test de reportes
class TestReports:

    def test_generate_report(self, scanner, tmp_path):
        scanner.findings.append({
            "file": "test.py",
            "line": 1,
            "pattern": "API_KEY",
            "description": "Test",
            "matched_text": "API_KEY=test",
            "severity": "HIGH"
        })

        output = tmp_path / "report.json"
        report = scanner.generate_report(output)

        assert report["status"] == "FAIL"
        assert report["total_findings"] == 1
        assert output.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
