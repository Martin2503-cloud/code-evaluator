from dataclasses import dataclass, field


@dataclass
class Finding:
    """Hallazgo individual de un analizador.

    Representa un problema detectado por una herramienta de análisis
    en una línea específica de un archivo.

    Args:
        file: Ruta absoluta o relativa al archivo donde se encontró el hallazgo.
        line: Número de línea dentro del archivo (1-based).
        severity: Gravedad del hallazgo: 'error', 'warning' o 'info'.
        message: Descripción legible del problema encontrado.
        dimension: Dimensión de calidad: 'quality', 'typing', 'security' o 'architecture'.

    Example:
        >>> Finding(
        ...     file="src/app.py", line=42, severity="error",
        ...     message="Undefined variable 'x'", dimension="typing",
        ... )
        Finding(file='src/app.py', line=42, severity='error', ...)
    """
    file: str
    line: int
    severity: str
    message: str
    dimension: str


@dataclass
class DimScore:
    """Puntaje calculado para una dimensión de calidad.

    Args:
        dimension: Nombre de la dimensión ('quality', 'typing', 'security', 'architecture').
        score: Puntaje de 0 a 100, donde 100 es perfecto.
        findings: Lista de hallazgos que afectaron esta dimensión.
        passed: True si el score supera o iguala el umbral configurado.

    Example:
        >>> ds = DimScore(dimension="quality", score=85.0, findings=[], passed=True)
        >>> ds.passed
        True
    """
    dimension: str
    score: float
    findings: list[Finding]
    passed: bool


@dataclass
class Config:
    """Configuración del evaluador con pesos y umbrales por dimensión.

    Los pesos definen la importancia relativa de cada dimensión en el score global.
    Los umbrales determinan si una dimensión se considera aprobada.

    Args:
        weights: Diccionario dimensión → peso (debe sumar 1.0).
            Valores default: quality=0.35, typing=0.10, security=0.35, architecture=0.20.
        thresholds: Diccionario dimensión → umbral mínimo para aprobar.
            Valores default: quality=70, typing=60, security=80, architecture=60.

    Example:
        >>> cfg = Config(weights={"quality": 1.0, "typing": 0.0, "security": 0.0, "architecture": 0.0})
        >>> cfg.weights["quality"]
        1.0
    """
    weights: dict[str, float] = field(default_factory=lambda: {
        "quality": 0.35,
        "typing": 0.10,
        "security": 0.35,
        "architecture": 0.20,
    })
    thresholds: dict[str, float] = field(default_factory=lambda: {
        "quality": 70.0,
        "typing": 60.0,
        "security": 80.0,
        "architecture": 60.0,
    })


@dataclass
class Report:
    """Reporte completo generado tras evaluar un proyecto.

    Agrega todos los resultados del pipeline: scores por dimensión,
    score global, y la configuración utilizada.

    Args:
        dim_scores: Lista de puntajes calculados por dimensión.
        global_score: Score global ponderado (0-100).
        config: Configuración utilizada para el cálculo.

    Example:
        >>> cfg = Config()
        >>> ds = DimScore("quality", 90.0, [], True)
        >>> r = Report([ds], 90.0, cfg)
        >>> r.global_score
        90.0
    """
    dim_scores: list[DimScore]
    global_score: float
    config: Config
