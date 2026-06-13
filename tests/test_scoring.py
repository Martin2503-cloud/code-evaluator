from evaluator.scoring import compute_dim_scores, compute_global
from evaluator.models import Config, Finding


def make_finding(
    dimension: str = "quality",
    severity: str = "warning",
    file: str = "test.py",
    line: int = 1,
    message: str = "issue",
) -> Finding:
    return Finding(
        file=file, line=line, severity=severity,
        message=message, dimension=dimension,
    )


class TestComputeDimScores:
    def test_no_findings_returns_100(self):
        scores = compute_dim_scores([], Config())
        quality = [s for s in scores if s.dimension == "quality"][0]
        assert quality.score == 100.0
        assert quality.passed is True

    def test_errors_penalize(self):
        findings = [make_finding(severity="error")]
        scores = compute_dim_scores(findings, Config())
        quality = [s for s in scores if s.dimension == "quality"][0]
        assert quality.score == 90.0

    def test_warnings_penalize_less(self):
        findings = [make_finding(severity="warning")]
        scores = compute_dim_scores(findings, Config())
        quality = [s for s in scores if s.dimension == "quality"][0]
        assert quality.score == 95.0

    def test_infos_penalize_minimally(self):
        findings = [make_finding(severity="info")]
        scores = compute_dim_scores(findings, Config())
        quality = [s for s in scores if s.dimension == "quality"][0]
        assert quality.score == 99.0

    def test_below_threshold_fails(self):
        findings = [make_finding(severity="error", dimension="security") for _ in range(5)]
        scores = compute_dim_scores(findings, Config())
        security = [s for s in scores if s.dimension == "security"][0]
        assert security.passed is False
        assert security.score < 80.0


class TestComputeGlobal:
    def test_default_weights(self):
        scores = [
            make_score("quality", 100.0),
            make_score("typing", 100.0),
            make_score("security", 100.0),
            make_score("architecture", 100.0),
        ]
        g = compute_global(scores, Config())
        assert g == 100.0

    def test_weighted_average(self):
        scores = [
            make_score("quality", 80.0),
            make_score("typing", 90.0),
            make_score("security", 70.0),
            make_score("architecture", 85.0),
        ]
        g = compute_global(scores, Config())
        assert g == 78.5


def make_score(dimension: str, score: float):
    from evaluator.models import DimScore
    return DimScore(dimension=dimension, score=score, findings=[], passed=True)
