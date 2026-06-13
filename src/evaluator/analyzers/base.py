from abc import ABC, abstractmethod

from evaluator.models import Finding


class Analyzer(ABC):
    """Analizador de calidad de código.

    Interfaz base para todos los analizadores. Cada implementación
    ejecuta una herramienta específica (ruff, mypy, bandit, AST)
    y convierte sus resultados a una lista de Finding.

    Example:
        >>> class MiAnalyzer(Analyzer):
        ...     def analyze(self, files):
        ...         return [Finding("app.py", 1, "info", "ok", "quality")]
        >>> a = MiAnalyzer()
        >>> len(a.analyze(["app.py"]))
        1
    """

    @abstractmethod
    def analyze(self, files: list[str]) -> list[Finding]:
        """Ejecuta el análisis sobre los archivos dados.

        Args:
            files: Lista de rutas a archivos .py a analizar.

        Returns:
            Lista de hallazgos encontrados. Vacía si no hay problemas.
        """
        ...
