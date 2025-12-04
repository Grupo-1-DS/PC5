import re
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class SecretPattern:
    """Clase que representa un patrón de secreto a detectar"""

    def __init__(self, name: str, pattern: str, description: str):
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.description = description


class SecretGuardian:
    """Escáner de secretos hardcodeados en repositorios"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.findings = []
        self.excluded_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "evidence", "fixtures"}
        self.excluded_extensions = {".pyc", ".pyo", ".exe", ".dll", ".so", ".dylib"}

    def _initialize_patterns(self) -> List[SecretPattern]:
        """Inicializa los patrones de detección de secretos"""
        return [
            SecretPattern(
                "API_KEY", r'API[_-]?KEY\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', "Detecta claves API hardcodeadas"
            ),
            SecretPattern("PASSWORD", r'PASSWORD\s*[=:]\s*["\']([^"\']{4,})["\']', "Detecta contraseñas hardcodeadas"),
            SecretPattern(
                "SECRET",
                r'SECRET[_-]?KEY?\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
                "Detecta claves secretas hardcodeadas",
            ),
            SecretPattern(
                "TOKEN", r'TOKEN\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', "Detecta tokens de autenticación"
            ),
            SecretPattern(
                "AWS_ACCESS_KEY",
                r'AWS[_-]?ACCESS[_-]?KEY[_-]?ID\s*[=:]\s*["\']?(AKIA[A-Z0-9]{16})["\']?',
                "Detecta AWS Access Key ID",
            ),
            SecretPattern(
                "PRIVATE_KEY", r'PRIVATE[_-]?KEY\s*[=:]\s*["\']([^"\']{20,})["\']', "Detecta claves privadas"
            ),
            SecretPattern(
                "DATABASE_URL",
                r'DATABASE[_-]?URL\s*[=:]\s*["\']([^"\']+@[^"\']+)["\']',
                "Detecta URLs de bases de datos con credenciales",
            ),
            SecretPattern("BEARER_TOKEN", r"Bearer\s+([a-zA-Z0-9_\-\.]{20,})", "Detecta tokens Bearer en headers"),
        ]

    def should_scan_file(self, file_path: Path) -> bool:
        """Determina si un archivo debe ser escaneado"""
        # Excluir directorios
        if any(excluded in file_path.parts for excluded in self.excluded_dirs):
            return False

        # Excluir por extensión
        if file_path.suffix in self.excluded_extensions:
            return False

        # Solo escanear archivos de texto
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                f.read(1024)
            return True
        except:
            return False

    def scan_file(self, file_path: Path) -> None:
        """Escanea un archivo en busca de secretos"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.readlines()

            for line_num, line in enumerate(content, start=1):
                for pattern in self.patterns:
                    matches = pattern.pattern.finditer(line)
                    for match in matches:
                        finding = {
                            "file": str(file_path),
                            "line": line_num,
                            "pattern": pattern.name,
                            "description": pattern.description,
                            "matched_text": match.group(0),
                            "severity": "HIGH",
                        }
                        self.findings.append(finding)

        except Exception as e:
            print(f"Error escaneando {file_path}: {e}")

    def scan_directory(self, directory: Path) -> None:
        """Escanea recursivamente un directorio"""
        for item in directory.rglob("*"):
            if item.is_file() and self.should_scan_file(item):
                self.scan_file(item)

    def generate_report(self, output_path: Path) -> Dict[str, Any]:
        """Genera el reporte JSON de resultados"""
        report = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_findings": len(self.findings),
            "findings": self.findings,
            "summary": {
                "high_severity": len([f for f in self.findings if f["severity"] == "HIGH"]),
                "patterns_detected": list(set(f["pattern"] for f in self.findings)),
            },
            "status": "FAIL" if self.findings else "PASS",
        }

        # Asegurar que el directorio de salida existe
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Escribir el reporte
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report


def main():
    """Función principal"""
    # Obtener el directorio raíz del proyecto
    project_root = Path(__file__).parent.parent

    print("=" * 60)
    print("SECRET GUARDIAN - Escaner de Secretos Hardcodeados")
    print("=" * 60)
    print(f"\nEscaneando directorio: {project_root}")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Crear instancia del escáner
    scanner = SecretGuardian()

    # Escanear el directorio
    scanner.scan_directory(project_root)

    # Generar reporte
    output_path = project_root / "evidence" / "secrets-scan.json"
    report = scanner.generate_report(output_path)

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DEL ESCANEO")
    print("=" * 60)
    print(f"Total de hallazgos: {report['total_findings']}")
    print(f"Severidad alta: {report['summary']['high_severity']}")
    print(
        f"Patrones detectados: {', '.join(report['summary']['patterns_detected']) if report['summary']['patterns_detected'] else 'Ninguno'}"
    )
    print(
        f"Estado: {'FAIL - Se encontraron secretos' if report['status'] == 'FAIL' else 'PASS - No se encontraron secretos'}"
    )
    print(f"Reporte guardado en: {output_path}")
    print("=" * 60)

    # Mostrar detalles de hallazgos si existen
    if report["findings"]:
        print("\nDETALLES DE HALLAZGOS:")
        for i, finding in enumerate(report["findings"], 1):
            print(f"\n  [{i}] {finding['pattern']}")
            print(f"      Archivo: {finding['file']}")
            print(f"      Linea: {finding['line']}")
            print(f"      Texto: {finding['matched_text'][:50]}...")

    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    exit(main())
