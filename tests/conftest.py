from evaluator.models import Finding


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
