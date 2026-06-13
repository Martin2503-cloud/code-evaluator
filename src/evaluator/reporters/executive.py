from evaluator.models import Report
from evaluator.reporters.base import Reporter


class ExecutiveReporter(Reporter):
    """Genera reporte ejecutivo para stakeholders no técnicos.

    El reporte incluye:
      - Score global con semáforo visual (🟢/🟡/🔴).
      - Scores por dimensión con umbral y estado.
      - Riesgos identificados (dimensiones por debajo del umbral).
      - Recomendaciones accionables priorizadas.

    Semáforo:
      - 🟢 Green: score >= 80
      - 🟡 Amber: score >= 60 y < 80
      - 🔴 Red: score < 60

    Example:
        >>> from evaluator.models import Config, DimScore, Report
        >>> cfg = Config()
        >>> ds = DimScore("quality", 45.0, [], False)
        >>> r = Report([ds], 45.0, cfg)
        >>> output = ExecutiveReporter().generate(r)
        >>> "Red" in output
        True
    """
    def generate(self, report: Report) -> str:
        """Genera reporte ejecutivo en Markdown.

        Args:
            report: Modelo con datos del proyecto evaluado.

        Returns:
            String Markdown con score global, semáforo, riesgos y recomendaciones.
        """
        lines = ["# Executive Report\n"]
        lines.append(f"## Global Score: **{report.global_score}/100**\n")

        semaforo = self._semaforo(report.global_score)
        lines.append(f"**Status**: {semaforo}\n")

        lines.append("## Scores by Dimension\n")
        lines.append("| Dimension | Score | Threshold | Status |")
        lines.append("|-----------|-------|-----------|--------|")
        for ds in report.dim_scores:
            status = self._semaforo(ds.score)
            threshold = report.config.thresholds.get(ds.dimension, 60)
            lines.append(
                f"| {ds.dimension.capitalize()} | {ds.score}/100 | {threshold} | {status} |"
            )

        low_scores = [ds for ds in report.dim_scores if not ds.passed]
        if low_scores:
            lines.append("\n## Risks\n")
            for ds in low_scores:
                lines.append(
                    f"- **{ds.dimension.capitalize()}** (score: {ds.score}): "
                    f"below threshold of {report.config.thresholds.get(ds.dimension, 60)}. "
                    f"{len(ds.findings)} issues found."
                )

        lines.append("\n## Recommendations\n")
        for ds in report.dim_scores:
            if not ds.passed:
                lines.append(
                    f"- Review **{ds.dimension}**: "
                    f"address top {min(3, len(ds.findings))} severity issues first."
                )
        if all(ds.passed for ds in report.dim_scores):
            lines.append("- All dimensions pass thresholds. Keep current practices.")

        return "\n".join(lines) + "\n"

    @staticmethod
    def _semaforo(score: float) -> str:
        """Devuelve el estado del semáforo según el score.

        Args:
            score: Puntaje de 0 a 100.

        Returns:
            "🟢 Green", "🟡 Amber" o "🔴 Red" según el nivel.
        """
        if score >= 80:
            return "🟢 Green"
        if score >= 60:
            return "🟡 Amber"
        return "🔴 Red"
