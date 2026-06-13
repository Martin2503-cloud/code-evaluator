from evaluator.models import Config, DimScore, Finding


def compute_dim_scores(
    findings: list[Finding], config: Config,
) -> list[DimScore]:
    """Calcula puntajes por dimensión de calidad.

    Para cada dimensión (quality, typing, security, architecture):
      1. Filtra los hallazgos de esa dimensión.
      2. Calcula el score restando penalidades según severidad.
      3. Compara contra el umbral configurado (passed = score >= threshold).

    Penalidades por hallazgo:
      - error: -10 puntos
      - warning: -5 puntos
      - info: -1 punto

    Args:
        findings: Lista completa de hallazgos de todos los analizadores.
        config: Configuración con umbrales por dimensión.

    Returns:
        Lista de DimScore, uno por dimensión.

    Example:
        >>> cfg = Config()
        >>> findings = [
        ...     Finding("app.py", 1, "error", "error", "quality"),
        ...     Finding("app.py", 2, "warning", "warning", "quality"),
        ... ]
        >>> scores = compute_dim_scores(findings, cfg)
        >>> quality = [s for s in scores if s.dimension == "quality"][0]
        >>> quality.score
        85.0
    """
    dimensions = ["quality", "typing", "security", "architecture"]
    scores: list[DimScore] = []
    for dim in dimensions:
        dim_findings = [f for f in findings if f.dimension == dim]
        score = _compute_dim_score(dim_findings, dim)
        threshold = config.thresholds.get(dim, 60.0)
        scores.append(DimScore(
            dimension=dim,
            score=score,
            findings=dim_findings,
            passed=score >= threshold,
        ))
    return scores


def _compute_dim_score(findings: list[Finding], dim: str) -> float:
    """Calcula puntaje individual para una dimensión.

    Parte de 100 y resta penalidades según severidad de hallazgos.
    El mínimo es 0.

    Args:
        findings: Hallazgos de una sola dimensión.
        dim: Nombre de la dimensión (solo para logging).

    Returns:
        Puntaje de 0 a 100.
    """
    if not findings:
        return 100.0
    total_penalty = sum(
        10 for f in findings if f.severity == "error"
    ) + sum(
        5 for f in findings if f.severity == "warning"
    ) + sum(
        1 for f in findings if f.severity == "info"
    )
    return max(0.0, 100.0 - total_penalty)


def compute_global(dim_scores: list[DimScore], config: Config) -> float:
    """Calcula el score global ponderado.

    Fórmula: Σ(score_dimensión × peso_dimensión)

    Los pesos por defecto son:
      - quality: 0.35
      - typing: 0.10
      - security: 0.35
      - architecture: 0.20

    Args:
        dim_scores: Scores calculados por dimensión.
        config: Configuración con pesos por dimensión.

    Returns:
        Score global redondeado a 1 decimal (0-100).

    Example:
        >>> cfg = Config()
        >>> scores = [
        ...     DimScore("quality", 80.0, [], True),
        ...     DimScore("typing", 90.0, [], True),
        ...     DimScore("security", 70.0, [], True),
        ...     DimScore("architecture", 85.0, [], True),
        ... ]
        >>> compute_global(scores, cfg)
        78.5
    """
    total = 0.0
    for ds in dim_scores:
        weight = config.weights.get(ds.dimension, 0.0)
        total += ds.score * weight
    return round(total, 1)
