# code-evaluator

Evaluador de calidad de código para proyectos Python/PySpark. Ejecuta 4 analizadores en paralelo, calcula un score global ponderado y genera dos reportes en Markdown: uno técnico (detalle por archivo) y otro ejecutivo (semáforo, riesgos, recomendaciones).

## Instalación

```bash
pip install -e .
```

Requiere Python >= 3.12. Los analizadores externos (ruff, mypy, bandit, radon) deben estar instalados para evaluar calidad, tipado y seguridad. El analizador de arquitectura funciona sin dependencias externas.

## Uso

```bash
# Evaluar proyecto local
evaluator --path ./mi-proyecto

# Evaluar repositorio GitHub
evaluator --github https://github.com/usuario/repo

# Con configuración personalizada y directorio de salida
evaluator --path ./proyecto --config .code-evaluator.yml --output ./reportes

# Ver ayuda
evaluator --help
```

## Analizadores

| Dimensión | Herramienta | Qué mide |
|-----------|-------------|----------|
| Calidad | ruff + radon | Estilo, complejidad ciclomática, mantenibilidad |
| Tipado | mypy | Cobertura de tipos, errores de tipo |
| Seguridad | bandit | Vulnerabilidades, secrets hardcodeados |
| Arquitectura | AST propio | Tamaño de funciones, parámetros, herencia |

Los 4 analizadores se ejecutan en paralelo vía `ThreadPoolExecutor`.

## Score global

```
score = w1 × calidad + w2 × tipado + w3 × seguridad + w4 × arquitectura
```

Cada dimensión puntúa de 0 a 100. Pesos default configurables vía YAML:

| Dimensión | Peso | Umbral |
|-----------|------|--------|
| Calidad | 35% | 70 |
| Tipado | 10% | 60 |
| Seguridad | 35% | 80 |
| Arquitectura | 20% | 60 |

### Configuración personalizada

```yaml
# .code-evaluator.yml
weights:
  quality: 0.35
  typing: 0.10
  security: 0.35
  architecture: 0.20

thresholds:
  quality: 70
  typing: 60
  security: 80
  architecture: 60
```

## Reportes

### Técnico (`technical.md`)
Para ingenieros. Incluye score por dimensión, tabla de hallazgos agrupados por archivo con línea, severidad y mensaje.

### Ejecutivo (`executive.md`)
Para stakeholders. Incluye score global con semáforo (🟢/🟡/🔴), riesgos identificados y recomendaciones accionables.

## Tests

```bash
pytest tests/ -v
```

28 tests: unitarios (modelos, scoring, reportes, structure analyzer) y de integración (scanner local).

## Proyecto

```
src/evaluator/
├── cli.py              → Entry point argparse
├── models.py           → Dataclasses: Finding, DimScore, Config, Report
├── scoring.py          → Cálculo de score ponderado + umbrales
├── scanner/
│   ├── base.py         → Scanner ABC
│   ├── local.py        → Escanea directorio local
│   └── github.py       → Clona repo GitHub y escanea
├── analyzers/
│   ├── base.py         → Analyzer ABC
│   ├── quality.py      → ruff + radon
│   ├── typing.py       → mypy
│   ├── security.py     → bandit
│   └── structure.py    → AST (funciones largas, parámetros, herencia)
└── reporters/
    ├── base.py         → Reporter ABC
    ├── technical.py    → Reporte detallado por archivo
    └── executive.py    → Reporte ejecutivo con semáforo
```
