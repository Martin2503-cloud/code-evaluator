"""Entry point de línea de comandos para code-evaluator.

Uso:
    evaluator --path ./mi-proyecto
    evaluator --path ./proyecto --config .code-evaluator.yml --output ./reportes
    evaluator --github https://github.com/usuario/repo
"""
import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml

from evaluator.models import Config, Finding, Report
from evaluator.scanner.local import LocalScanner
from evaluator.scanner.github import GithubScanner
from evaluator.analyzers.quality import QualityAnalyzer
from evaluator.analyzers.typing import TypingAnalyzer
from evaluator.analyzers.security import SecurityAnalyzer
from evaluator.analyzers.structure import StructureAnalyzer
from evaluator.scoring import compute_dim_scores, compute_global
from evaluator.reporters.technical import TechnicalReporter
from evaluator.reporters.executive import ExecutiveReporter


def load_config(config_path: str | None) -> Config:
    """Carga configuración desde archivo YAML opcional.

    Si no se especifica ruta o el archivo no existe, devuelve
    la configuración por defecto (pesos y umbrales predefinidos).

    Args:
        config_path: Ruta al archivo .code-evaluator.yml o None.

    Returns:
        Config con pesos y umbrales (defaults o del archivo YAML).

    Example:
        >>> cfg = load_config(None)
        >>> cfg.weights["quality"]
        0.35
    """
    if config_path and os.path.isfile(config_path):
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        weights = data.get("weights", {})
        thresholds = data.get("thresholds", {})
        return Config(
            weights={
                "quality": weights.get("quality", 0.35),
                "typing": weights.get("typing", 0.10),
                "security": weights.get("security", 0.35),
                "architecture": weights.get("architecture", 0.20),
            },
            thresholds={
                "quality": thresholds.get("quality", 70.0),
                "typing": thresholds.get("typing", 60.0),
                "security": thresholds.get("security", 80.0),
                "architecture": thresholds.get("architecture", 60.0),
            },
        )
    return Config()


def run_analyzers(files: list[str]) -> list[Finding]:
    """Ejecuta los 4 analizadores en paralelo sobre los archivos dados.

    Usa ThreadPoolExecutor con 4 workers para ejecutar simultáneamente:
      - QualityAnalyzer (ruff + radon)
      - TypingAnalyzer (mypy)
      - SecurityAnalyzer (bandit)
      - StructureAnalyzer (AST)

    Si un analizador falla, se captura la excepción y se agrega
    como hallazgo de error en lugar de interrumpir el pipeline.

    Args:
        files: Lista de rutas a archivos .py.

    Returns:
        Lista combinada de hallazgos de todos los analizadores.

    Example:
        >>> # run_analyzers(["src/app.py"])  # requiere herramientas instaladas
    """
    analyzers = [
        QualityAnalyzer(),
        TypingAnalyzer(),
        SecurityAnalyzer(),
        StructureAnalyzer(),
    ]
    findings: list[Finding] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(a.analyze, files): a for a in analyzers}
        for future in as_completed(futures):
            try:
                findings.extend(future.result())
            except Exception as e:
                findings.append(Finding(
                    file="", line=0, severity="error",
                    message=f"Analyzer failed: {e}", dimension="unknown",
                ))
    return findings


def main() -> None:
    """Punto de entrada principal del CLI.

    Pipeline completo:
      1. Parsear argumentos (--path | --github, --config, --output).
      2. Cargar configuración (default o YAML).
      3. Escanear archivos .py (local o GitHub).
      4. Ejecutar analizadores en paralelo.
      5. Calcular scores por dimensión y global.
      6. Generar reportes técnico y ejecutivo en Markdown.
      7. Mostrar resumen en terminal.

    Uso desde terminal:
        $ evaluator --path ./mi-proyecto
        $ evaluator --github https://github.com/usuario/repo --output ./reportes
    """
    parser = argparse.ArgumentParser(
        description="Evaluador de calidad de código Python/PySpark"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", help="Ruta local al proyecto")
    group.add_argument("--github", help="URL del repositorio GitHub")
    parser.add_argument("--config", help="Ruta a archivo YAML de configuración")
    parser.add_argument("--output", default="./reports", help="Directorio de salida")

    args = parser.parse_args()

    config = load_config(args.config)

    if args.path:
        files = LocalScanner(args.path).scan()
    else:
        files = GithubScanner(args.github).scan()

    if not files:
        print("No .py files found.")
        return

    print(f"Scanning {len(files)} files...")

    findings = run_analyzers(files)
    dim_scores = compute_dim_scores(findings, config)
    global_score = compute_global(dim_scores, config)
    report_model = Report(dim_scores=dim_scores, global_score=global_score, config=config)

    os.makedirs(args.output, exist_ok=True)

    tech = TechnicalReporter().generate(report_model)
    tech_path = os.path.join(args.output, "technical.md")
    with open(tech_path, "w", encoding="utf-8") as f:
        f.write(tech)

    exec_rep = ExecutiveReporter().generate(report_model)
    exec_path = os.path.join(args.output, "executive.md")
    with open(exec_path, "w", encoding="utf-8") as f:
        f.write(exec_rep)

    print(f"Reports generated:")
    print(f"  Technical: {tech_path}")
    print(f"  Executive: {exec_path}")
    print(f"Global score: {global_score}/100")


if __name__ == "__main__":
    main()
