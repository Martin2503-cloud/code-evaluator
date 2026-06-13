from evaluator.models import Finding, DimScore, Report, Config


class TestFinding:
    def test_create(self):
        f = Finding(file="a.py", line=10, severity="error", message="bad", dimension="quality")
        assert f.file == "a.py"
        assert f.line == 10
        assert f.severity == "error"


class TestDimScore:
    def test_create(self):
        ds = DimScore(dimension="quality", score=85.0, findings=[], passed=True)
        assert ds.score == 85.0
        assert ds.passed is True


class TestConfig:
    def test_default_weights(self):
        c = Config()
        assert c.weights["quality"] == 0.35
        assert c.weights["typing"] == 0.10
        assert c.weights["security"] == 0.35
        assert c.weights["architecture"] == 0.20

    def test_default_thresholds(self):
        c = Config()
        assert c.thresholds["quality"] == 70.0

    def test_custom_weights(self):
        c = Config(weights={"quality": 1.0})
        assert c.weights["quality"] == 1.0


class TestReport:
    def test_create(self):
        config = Config()
        ds = DimScore(dimension="quality", score=90.0, findings=[], passed=True)
        r = Report(dim_scores=[ds], global_score=90.0, config=config)
        assert r.global_score == 90.0
        assert len(r.dim_scores) == 1
