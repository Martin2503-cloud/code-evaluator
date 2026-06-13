import re
import subprocess

from evaluator.models import Finding
from evaluator.analyzers.base import Analyzer

_MYPY_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):\s*(?P<severity>error|warning|note):\s*(?P<msg>.+)$"
)


class TypingAnalyzer(Analyzer):
    """Analizador de tipado estático usando mypy.

    Ejecuta mypy sobre los archivos y captura errores de tipo,
    advertencias y notas. Requiere mypy instalado en el sistema.

    Example:
        >>> a = TypingAnalyzer()
        >>> # a.analyze(["src/app.py"])  # requiere mypy instalado
    """
    def analyze(self, files: list[str]) -> list[Finding]:
        """Ejecuta mypy y parsea su salida.

        Args:
            files: Lista de rutas a archivos .py.

        Returns:
            Hallazgos de tipado con severidad error, warning o note.
        """
        try:
            result = subprocess.run(
                ["mypy", "--show-column-numbers", *files],
                capture_output=True, text=True, timeout=60,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return [Finding(
                file="", line=0, severity="error",
                message=f"mypy failed: {e}", dimension="typing",
            )]
        return self._parse_output(result.stdout)

    def _parse_output(self, output: str) -> list[Finding]:
        """Convierte la salida de mypy en objetos Finding.

        Formato esperado por línea:
            archivo:línea: severidad: mensaje

        Args:
            output: Salida stdout de mypy.

        Returns:
            Lista de hallazgos de tipado.
        """
        findings: list[Finding] = []
        for line in output.splitlines():
            m = _MYPY_RE.match(line)
            if m:
                findings.append(Finding(
                    file=m.group("file"),
                    line=int(m.group("line")),
                    severity=m.group("severity"),
                    message=m.group("msg"),
                    dimension="typing",
                ))
        return findings
