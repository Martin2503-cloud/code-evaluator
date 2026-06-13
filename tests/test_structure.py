from evaluator.analyzers.structure import StructureAnalyzer


class TestStructureAnalyzer:
    def test_no_findings_for_clean_code(self):
        findings = StructureAnalyzer().analyze_source("x = 1\ny = 2\n")
        assert len(findings) == 0

    def test_long_function_triggers_warning(self):
        code = "def long():\n" + "    pass\n" * 60
        findings = StructureAnalyzer().analyze_source(code)
        assert any("Function too long" in f.message for f in findings)

    def test_too_many_parameters(self):
        code = "def f(a, b, c, d, e, f, g, h): pass"
        findings = StructureAnalyzer().analyze_source(code)
        assert any("Too many parameters" in f.message for f in findings)

    def test_deep_inheritance(self):
        code = """
class A: pass
class B(A): pass
class C(B): pass
class D(C): pass
class E(D): pass
"""
        findings = StructureAnalyzer().analyze_source(code)
        assert any("Deep inheritance" in f.message for f in findings)

    def test_short_function_ok(self):
        findings = StructureAnalyzer().analyze_source("def short():\n    pass\n")
        assert len(findings) == 0

    def test_syntax_error_returns_empty(self):
        findings = StructureAnalyzer().analyze_source("this is not valid python @@@")
        assert findings == []
