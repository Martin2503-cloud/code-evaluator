import json
import subprocess

from evaluator.models import Finding
from evaluator.analyzers.base import Analyzer


class SecurityAnalyzer(Analyzer):
    """Analizador de seguridad usando bandit.

    Ejecuta bandit en formato JSON y parsea los resultados.
    Requiere bandit instalado en el sistema.

    Los niveles de severidad se mapean así:
      - high → severity='error'
      - medium → severity='warning'
      - low → severity='info'

    Example:
        >>> a = SecurityAnalyzer()
        >>> # a.analyze(["src/app.py"])  # requiere bandit instalado
    """
    def analyze(self, files: list[str]) -> list[Finding]:
        """Ejecuta bandit y parsea su salida JSON.

        Args:
            files: Lista de rutas a archivos .py.

        Returns:
            Hallazgos de seguridad con severidad mapeada.
        """
        try:
            result = subprocess.run(
                ["bandit", "-r", *files, "-f", "json"],
                capture_output=True, text=True, timeout=60,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return [Finding(
                file="", line=0, severity="error",
                message=f"bandit failed: {e}", dimension="security",
            )]
        return self._parse_output(result.stdout)

    def _parse_output(self, output: str) -> list[Finding]:
        """Convierte el JSON de bandit en objetos Finding.

        Bandit exporta en formato:
            {"results": [{"filename": "...", "line_number": N,
                          "issue_severity": "MEDIUM", "issue_text": "..."}]}

        Args:
            output: Salida stdout de bandit en formato JSON.

        Returns:
            Lista de hallazgos de seguridad.
        """
        findings: list[Finding] = []
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return findings
        for result in data.get("results", []):
            severity = result.get("issue_severity", "low").lower()
            if severity == "medium":
                sev = "warning"
            elif severity == "high":
                sev = "error"
            else:
                sev = "info"
            findings.append(Finding(
                file=result.get("filename", ""),
                line=result.get("line_number", 0),
                severity=sev,
                message=result.get("issue_text", ""),
                dimension="security",
            ))
        return findings
