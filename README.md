# gh-actions-lab

[![CI](https://github.com/sergio-santiago/gh-actions-lab/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/sergio-santiago/gh-actions-lab/actions/workflows/ci-cd.yml)

A **CI/CD lab with GitHub Actions**, built around a deliberately simple Python
application (a calculator exposed as a CLI).

The app is not the point, the **pipeline** is: lint → test → build → deploy, run
automatically on every `push` to `main`.

---

## Repository layout

```
.
├── app/                       # Application source
│   ├── __init__.py
│   ├── calculator.py          # Arithmetic operations
│   └── main.py                # CLI (`calc add 2 3`)
├── tests/                     # Unit and CLI tests with pytest
│   ├── test_calculator.py
│   └── test_main.py
├── .github/
│   ├── actions/
│   │   └── setup-python-env/  # Reusable composite action
│   └── workflows/
│       └── ci-cd.yml          # CI/CD pipeline
├── pyproject.toml             # Packaging plus pytest/ruff/coverage config
├── requirements.txt           # Runtime dependencies (empty, stdlib only)
├── requirements-dev.txt       # Development dependencies
├── Makefile                   # Local tasks: install / lint / test / build
├── DOCUMENTATION.md           # One page write-up of the flow
└── README.md
```

---

## Local usage

Requires Python 3.10+ and `make`.

```bash
make install   # install dependencies and the app in editable mode
make lint      # run ruff (lint and format)
make test      # run pytest with coverage
make build     # produce sdist and wheel in dist/
make run ARGS="add 2 3"   # → 5.0
```

---

## CI/CD pipeline

The workflow lives in [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).

### Trigger

- `push` to `main` runs the full pipeline, **deploy** included.
- `pull_request` against `main` runs **lint, test and build**, without deploying.
- `workflow_dispatch` allows a manual run from the GitHub UI.

### Stages (jobs)

| # | Job      | Depends on | What it does                                                     |
|---|----------|------------|------------------------------------------------------------------|
| 1 | `lint`   | none       | `ruff check` plus `ruff format --check`                          |
| 2 | `test`   | `lint`     | `pytest` with coverage across a Python 3.10/3.11/3.12 matrix     |
| 3 | `build`  | `test`     | `python -m build`, producing sdist and wheel, uploaded as artifact |
| 4 | `deploy` | `build`    | Only on `push` to `main`: downloads the artifact and publishes a Release |

Jobs run in parallel inside the matrix and are chained with `needs:`. Environment
setup is extracted into a **composite action**
(`.github/actions/setup-python-env`) so no job repeats those steps.

### DevOps principles applied

- **Full automation**: no manual steps, everything starts from a `push`.
- **Separated stages**: lint, test, build and deploy are independent jobs with
  their own logs and artifacts.
- **Reusable steps**: a composite action for the setup, avoiding duplication.
- **Reproducibility**: pinned dependency versions, a Python matrix, and pip cache
  keyed by lock file.
- **Traceability**: artifacts (`coverage.xml`, `dist/*`) uploaded on every run, and
  the deploy creates a Release referencing the commit and the run id.
- **Security**: `permissions: contents: read` by default, escalated only in
  `deploy`. `concurrency` cancels stale runs per branch.

See [`DOCUMENTATION.md`](DOCUMENTATION.md) for the one page write-up.
