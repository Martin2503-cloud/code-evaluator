from abc import ABC, abstractmethod

from evaluator.models import Report


class Reporter(ABC):
    """Generador de reportes en formato Markdown.

    Interfaz base para todos los generadores de reporte.
    Cada Reporter produce un string Markdown diferente a partir
    del mismo modelo Report.

    Example:
        >>> class MiReporter(Reporter):
        ...     def generate(self, report):
        ...         return f"# Score: {report.global_score}"
        >>> r = type("R", (), {"global_score": 85.0})()
        >>> MiReporter().generate(r)
        '# Score: 85.0'
    """

    @abstractmethod
    def generate(self, report: Report) -> str:
        """Genera el contenido del reporte como Markdown.

        Args:
            report: Modelo con scores, hallazgos y configuración.

        Returns:
            String con el contenido del reporte en formato Markdown.
        """
        ...
