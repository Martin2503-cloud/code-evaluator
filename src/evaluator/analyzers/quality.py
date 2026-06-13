import re
import subprocess

from evaluator.models import Finding
from evaluator.analyzers.base import Analyzer

_RUFF_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):\s*(?P<code>\S+)\s+(?P<msg>.+)$"
)


class QualityAnalyzer(Analyzer):
    """Analizador de calidad de código usando ruff y radon.

    Ejecuta:
      - ruff check: detecta violaciones de estilo y buenas prácticas.
      - radon cc: mide complejidad ciclomática de funciones.

    Si una herramienta no está instalada, reporta un error como hallazgo
    y continúa con la otra.

    Example:
        >>> a = QualityAnalyzer()
        >>> # a.analyze(["src/app.py"])  # requiere ruff y radon instalados
    """
    def analyze(self, files: list[str]) -> list[Finding]:
        """Ejecuta ruff y radon sobre los archivos.

        Args:
            files: Lista de rutas a archivos .py.

        Returns:
            Hallazgos combinados de ruff (estilo) y radon (complejidad).
        """
        findings: list[Finding] = []
        findings.extend(self._run_ruff(files))
        findings.extend(self._run_radon(files))
        return findings

    def _run_ruff(self, files: list[str]) -> list[Finding]:
        """Ejecuta ruff check y parsea su salida.

        Args:
            files: Archivos a analizar.

        Returns:
            Hallazgos de estilo con severidad 'warning'.
        """
        try:
            result = subprocess.run(
                ["ruff", "check", *files],
                capture_output=True, text=True, timeout=60,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return [Finding(
                file="", line=0, severity="error",
                message=f"ruff check failed: {e}", dimension="quality",
            )]
        return self._parse_ruff_output(result.stdout)

    def _parse_ruff_output(self, output: str) -> list[Finding]:
        """Convierte la salida textual de ruff en objetos Finding.

        Formato esperado por línea:
            archivo:línea:columna:código mensaje

        Args:
            output: Salida stdout de ruff check.

        Returns:
            Lista de hallazgos parseados.
        """
        findings: list[Finding] = []
        for line in output.splitlines():
            m = _RUFF_RE.match(line)
            if m:
                findings.append(Finding(
                    file=m.group("file"),
                    line=int(m.group("line")),
                    severity="warning",
                    message=f"{m.group('code')}: {m.group('msg')}",
                    dimension="quality",
                ))
        return findings

    def _run_radon(self, files: list[str]) -> list[Finding]:
        """Ejecuta radon cc para medir complejidad ciclomática.

        Args:
            files: Archivos a analizar.

        Returns:
            Hallazgos por funciones con complejidad > 10.
        """
        try:
            result = subprocess.run(
                ["radon", "cc", *files, "--average"],
                capture_output=True, text=True, timeout=30,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return [Finding(
                file="", line=0, severity="info",
                message=f"radon cc failed: {e}", dimension="quality",
            )]
        return self._parse_radon_output(result.stdout)

    def _parse_radon_output(self, output: str) -> list[Finding]:
        """Convierte la salida de radon en hallazgos de complejidad.

        Reporta como warning las funciones con complejidad > 10.

        Args:
            output: Salida stdout de radon cc.

        Returns:
            Hallazgos por alta complejidad ciclomática.
        """
        findings: list[Finding] = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[0].count(":") == 1:
                try:
                    complexity = int(parts[3].strip("()"))
                    if complexity > 10:
                        findings.append(Finding(
                            file=parts[0],
                            line=0,
                            severity="warning",
                            message=f"High cyclomatic complexity: {complexity}",
                            dimension="quality",
                        ))
                except (ValueError, IndexError):
                    pass
        return findings
