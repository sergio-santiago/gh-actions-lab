# CI/CD pipeline with GitHub Actions

## Application

A small Python calculator (`app/calculator.py`) exposed as a CLI (`app/main.py`,
command `calc`). The point of the exercise is not the logic, it is demonstrating a
**CI/CD pipeline** that validates and ships the code automatically and reproducibly.

## Trigger

The workflow `.github/workflows/ci-cd.yml` fires on:

- **`push` to `main`**: full pipeline, deploy included.
- **`pull_request` against `main`**: pre merge validation (lint, test, build).
- **`workflow_dispatch`**: manual run from the *Actions* tab.

## Execution flow

```
            ┌──────┐    ┌──────┐    ┌───────┐    ┌────────┐
push  ───▶  │ LINT │──▶ │ TEST │──▶ │ BUILD │──▶ │ DEPLOY │
            └──────┘    └──────┘    └───────┘    └────────┘
                                                  (only on
                                                   push to main)
```

Jobs are chained with `needs:`. If a stage fails the following ones do not run, which
guarantees that code failing lint or tests is never deployed.

## Stages

### 1. Lint
Static analysis and format check with **ruff**. It runs first because it is the
cheapest stage and catches trivial errors before spending time on tests.

### 2. Test
**pytest** with coverage, across a **matrix** of Python 3.10, 3.11 and 3.12 (three
parallel jobs). `coverage.xml` and `junit.xml` are published as run artifacts for
later auditing.

### 3. Build
Packages the application with `python -m build`, producing `sdist` and `wheel` in
`dist/`. The resulting artifact is uploaded with `actions/upload-artifact` so the next
stage consumes it without rebuilding, which means the binary that was tested is the
binary that ships.

### 4. Deploy
Runs only when the event is a `push` and the branch is `main`. It downloads the `dist`
artifact, creates a **GitHub Release** tagged from the run number, and attaches the
binaries. It is isolated in `environment: production`, with `contents: write` granted
exclusively to this job.

## DevOps principles applied

| Principle              | How it materialises                                             |
|------------------------|-----------------------------------------------------------------|
| Full automation        | No manual steps, everything starts from a `push` or a PR.       |
| Stage separation       | 4 independent jobs (lint / test / build / deploy).              |
| Reusable steps         | The `setup-python-env` composite action, shared by all of them. |
| Readable logs          | Descriptive step names, one step for one idea.                  |
| Reproducible runs      | Pinned versions, pip cache, Python matrix, same artifact in build and deploy. |
| Security               | `permissions: read` globally, escalating to `write` only in deploy. |
| Efficiency             | `concurrency` cancels stale runs on the same branch.            |

## How to verify it

1. Push to `main` and watch the *Actions* tab.
2. Confirm the 4 jobs pass in order (`lint → test → build → deploy`).
3. Check the artifacts: `coverage-*` and `dist` on the run, and the new Release in the
   repository's *Releases* tab.
