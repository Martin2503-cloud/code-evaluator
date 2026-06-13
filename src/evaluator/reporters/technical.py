from collections import defaultdict

from evaluator.models import Report
from evaluator.reporters.base import Reporter


class TechnicalReporter(Reporter):
    """Genera reporte técnico detallado para ingenieros.

    El reporte incluye:
      - Score global y por dimensión con tabla comparativa.
      - Hallazgos agrupados por archivo, con línea, severidad y mensaje.
      - Conteo total de hallazgos.

    Example:
        >>> from evaluator.models import Config, DimScore, Report
        >>> cfg = Config()
        >>> ds = DimScore("quality", 85.0, [], True)
        >>> r = Report([ds], 85.0, cfg)
        >>> output = TechnicalReporter().generate(r)
        >>> "# Technical Report" in output
        True
    """
    def generate(self, report: Report) -> str:
        """Genera reporte técnico en Markdown.

        Args:
            report: Modelo con datos del proyecto evaluado.

        Returns:
            String Markdown con tabla de scores y hallazgos por archivo.
        """
        lines = ["# Technical Report\n"]
        lines.append(f"**Global Score**: {report.global_score}/100\n")
        lines.append("## Scores by Dimension\n")
        lines.append("| Dimension | Score | Passed | Findings |")
        lines.append("|-----------|-------|--------|----------|")
        for ds in report.dim_scores:
            status = "✅" if ds.passed else "❌"
            lines.append(
                f"| {ds.dimension} | {ds.score}/100 | {status} | {len(ds.findings)} |"
            )

        grouped = defaultdict(list)
        for ds in report.dim_scores:
            for f in ds.findings:
                grouped[f.file].append(f)

        lines.append("\n## Findings by File\n")
        for filepath in sorted(grouped):
            lines.append(f"\n### {filepath}\n")
            lines.append("| Line | Severity | Dimension | Message |")
            lines.append("|------|----------|-----------|---------|")
            for f in grouped[filepath]:
                lines.append(
                    f"| {f.line} | {f.severity} | {f.dimension} | {f.message} |"
                )

        lines.append("\n---\n")
        total = sum(len(ds.findings) for ds in report.dim_scores)
        lines.append(f"**Total findings**: {total}")
        return "\n".join(lines) + "\n"
