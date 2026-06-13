# code-evaluator

Evaluador de calidad de código para proyectos Python/PySpark con reportes para dos audiencias: ingenieros (detalle técnico) y ejecutivos (contexto de negocio).

## Dimensiones de evaluación

| Dimensión | Herramienta | Qué mide |
|-----------|-------------|----------|
| **Calidad de código** | `ruff` + `radon` | Estilo, complejidad ciclomática, mantenibilidad, duplicación |
| **Tipado** | `mypy` | Cobertura de tipos, errores de tipo, consistencia |
| **Seguridad** | `bandit` | Vulnerabilidades, hardcodeo de secrets, inyección SQL |
| **Arquitectura** | Análisis AST propio | Tamaño de funciones, acoplamiento, profundidad de herencia, dependencias circulares |

## Reportes

| Reporte | Audiencia | Formato | Contenido |
|---------|-----------|---------|-----------|
| Técnico | Data engineers / Devs Jr. | Markdown (.md) | Detalle línea por línea, tabla de errores, deuda técnica |
| Ejecutivo | Gerentes / Stakeholders | Markdown (.md) | Score global (0-100), tendencias, riesgos de negocio, recomendaciones |

## Score global

```
score = w1 × calidad + w2 × tipado + w3 × seguridad + w4 × arquitectura
```

Cada dimensión puntúa de 0 a 100. Pesos configurables (default: calidad 35%, tipado 10%, seguridad 35%, arquitectura 20%).

## Fuentes de código

- **Rutas locales**: escanea archivos `.py` en directorios locales.
- **Repositorios GitHub**: clona el repo a un directorio temporal y lo escanea.

## Arquitectura

```
src/evaluator/
├── cli.py                    ← Entry point vía argparse
│
├── scanner/
│   ├── __init__.py
│   ├── base.py               ← Interfaz común para scanners
│   ├── local.py              ← Escanea rutas del sistema de archivos
│   └── github.py             ← Clona repos desde GitHub
│
├── analyzers/
│   ├── __init__.py
│   ├── quality.py            ← ruff + radon
│   ├── typing.py             ← mypy
│   ├── security.py           ← bandit
│   └── structure.py          ← AST analysis (tamaño fn, acoplamiento, etc.)
│
├── scoring.py                ← Cálculo de scores por dimensión + global
│
├── reporters/
│   ├── __init__.py
│   ├── base.py               ← Interfaz común para reportes
│   ├── technical.py          ← Reporte detallado para ingenieros
│   └── executive.py          ← Resumen para ejecutivos
│
└── models.py                 ← Tipos y estructuras compartidas
```

## Flujo de ejecución

```
1. Recibir ruta local o URL de GitHub
2. (Si es GitHub) clonar a directorio temporal
3. Ejecutar los 4 analizadores en paralelo
4. Recolectar resultados → unificar en estructura común
5. Calcular scores por dimensión
6. Generar ambos reportes (.md)
7. Mostrar resumen en terminal
```

## Configuración

Mediante archivo YAML opcional (`.code-evaluator.yml` dentro del proyecto evaluado) o argumentos CLI:

```yaml
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

## Riesgos

- **Dependencias externas**: ruff, mypy, bandit, radon deben instalarse. El evaluador verificará su presencia o los instalará bajo demanda.
- **Proyectos sin tipos**: mypy en proyectos sin type hints no reportará errores pero sí baja cobertura → hay que manejarlo como caso válido.
- **Repos grandes**: clonar y escanear puede tomar tiempo. Se mostrará progreso mediante barras/indicadores.
- **PySpark**: linting y tipado necesitan configuración especial (pyspark-stubs, reglas específicas de ruff).

## Próximos pasos

1. Ajustar pesos y thresholds según preferencia.
2. Crear el spec con requerimientos detallados y escenarios.
3. Diseño técnico con decisiones de implementación.
4. Desglose de tareas.
5. Implementación.
