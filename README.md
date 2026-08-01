# gh-actions-lab

[![CI](https://github.com/sergio-santiago/gh-actions-lab/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/sergio-santiago/gh-actions-lab/actions/workflows/ci-cd.yml)

Laboratorio de **CI/CD con GitHub Actions** sobre una aplicación Python sencilla
(una calculadora invocable por CLI).

El objetivo no es la app, sino el **pipeline**: lint → test → build → deploy,
ejecutado automáticamente en cada `push` a `main`.

---

## Estructura del repositorio

```
.
├── app/                       # Código fuente de la aplicación
│   ├── __init__.py
│   ├── calculator.py          # Operaciones aritméticas
│   └── main.py                # CLI (`calc add 2 3`)
├── tests/                     # Tests unitarios + CLI con pytest
│   ├── test_calculator.py
│   └── test_main.py
├── .github/
│   ├── actions/
│   │   └── setup-python-env/  # Composite action reutilizable
│   └── workflows/
│       └── ci-cd.yml          # Pipeline CI/CD
├── pyproject.toml             # Empaquetado + config de pytest/ruff/coverage
├── requirements.txt           # Dependencias runtime (vacío: stdlib)
├── requirements-dev.txt       # Dependencias de desarrollo
├── Makefile                   # Tareas locales: install / lint / test / build
├── DOCUMENTACION.md           # Documento de 1 página sobre el flujo
└── README.md
```

---

## Uso local

Requisitos: Python 3.10+ y `make`.

```bash
make install   # instala dependencias y la app en modo editable
make lint      # ejecuta ruff (lint + formato)
make test      # corre pytest con cobertura
make build     # genera sdist y wheel en dist/
make run ARGS="add 2 3"   # → 5.0
```

---

## Pipeline CI/CD

El workflow está en [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).

### Trigger

- `push` a `main` → corre el pipeline completo (incluye **deploy**).
- `pull_request` contra `main` → corre **lint + test + build** (sin deploy).
- `workflow_dispatch` → ejecución manual desde la UI de GitHub.

### Etapas (jobs)

| # | Job      | Depende de | Qué hace                                                          |
|---|----------|------------|-------------------------------------------------------------------|
| 1 | `lint`   | —          | `ruff check` + `ruff format --check`                              |
| 2 | `test`   | `lint`     | `pytest` con cobertura sobre matriz Python 3.10/3.11/3.12         |
| 3 | `build`  | `test`     | `python -m build` → genera sdist y wheel, los sube como artefacto |
| 4 | `deploy` | `build`    | Solo en `push` a `main`: descarga el artefacto y publica Release  |

Los jobs corren en paralelo dentro de la matriz y se encadenan vía `needs:`.
La instalación del entorno está extraída a una **composite action**
(`.github/actions/setup-python-env`) para no repetir pasos en cada job.

### Principios DevOps aplicados

- **Automatización completa**: nada de pasos manuales, todo dispara desde `push`.
- **Etapas separadas**: lint, test, build y deploy son jobs independientes con
  sus propios logs y artefactos.
- **Pasos reutilizables**: composite action para el setup, evitando duplicación.
- **Reproducibilidad**: versiones de dependencias pinneadas, matriz de Python,
  caché de pip por lock-file.
- **Trazabilidad**: artefactos (`coverage.xml`, `dist/*`) subidos a cada run y
  el deploy crea un Release referenciando commit y run id.
- **Seguridad**: `permissions: contents: read` por defecto, escalado solo en
  `deploy`. `concurrency` cancela runs antiguos por rama.

Ver [`DOCUMENTACION.md`](DOCUMENTACION.md) para la explicación de 1 página.
