from evaluator.reporters.technical import TechnicalReporter
from evaluator.reporters.executive import ExecutiveReporter
from evaluator.models import Report, Config, DimScore


class TestTechnicalReporter:
    def test_generates_markdown(self):
        r = _make_report(global_score=85.0)
        output = TechnicalReporter().generate(r)
        assert "# Technical Report" in output
        assert "85.0/100" in output
        assert "quality" in output.lower()

    def test_includes_findings_table(self):
        r = _make_report(global_score=85.0)
        output = TechnicalReporter().generate(r)
        assert "Findings by File" in output


class TestExecutiveReporter:
    def test_generates_markdown(self):
        r = _make_report(global_score=85.0)
        output = ExecutiveReporter().generate(r)
        assert "Executive Report" in output
        assert "85.0/100" in output

    def test_semaforo_green_high_score(self):
        r = _make_report(global_score=90.0)
        output = ExecutiveReporter().generate(r)
        assert "Green" in output

    def test_semaforo_red_low_score(self):
        r = _make_report(global_score=45.0)
        output = ExecutiveReporter().generate(r)
        assert "Red" in output
        assert "Risks" in output

    def test_semaforo_amber(self):
        r = _make_report(global_score=70.0)
        output = ExecutiveReporter().generate(r)
        assert "Amber" in output


def _make_report(global_score: float) -> Report:
    config = Config()
    dim_scores = [
        DimScore(dimension="quality", score=global_score, findings=[], passed=global_score >= 70),
    ]
    return Report(dim_scores=dim_scores, global_score=global_score, config=config)
