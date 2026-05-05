# Pipeline CI/CD con GitHub Actions — Documentación

## Aplicación

Pequeña calculadora en Python (`app/calculator.py`) expuesta como CLI
(`app/main.py`, comando `calc`). El foco del ejercicio no es la lógica, sino
demostrar un **pipeline CI/CD** que valide y despliegue el código de forma
automática y reproducible.

## Trigger

El workflow `.github/workflows/ci-cd.yml` se dispara en:

- **`push` a `main`** → pipeline completo, incluyendo despliegue.
- **`pull_request` contra `main`** → validación previa al merge (lint + test + build).
- **`workflow_dispatch`** → ejecución manual desde la pestaña *Actions*.

## Flujo de ejecución

```
            ┌──────┐    ┌──────┐    ┌───────┐    ┌────────┐
push  ───▶  │ LINT │──▶ │ TEST │──▶ │ BUILD │──▶ │ DEPLOY │
            └──────┘    └──────┘    └───────┘    └────────┘
                                                  (solo en
                                                   push a main)
```

Los jobs se encadenan con `needs:`. Si una etapa falla, las siguientes no se
ejecutan, garantizando que nunca se despliega código que no haya pasado lint y
tests.

## Etapas

### 1. Lint
Análisis estático y verificación de formato con **ruff**. Se ejecuta primero
porque es la etapa más barata y detecta errores triviales antes de invertir
tiempo en los tests.

### 2. Test
**pytest** con cobertura, sobre una **matriz** de Python 3.10, 3.11 y 3.12
(tres jobs en paralelo). Se publica `coverage.xml` y `junit.xml` como
artefactos del run para auditoría posterior.

### 3. Build
Empaqueta la aplicación con `python -m build`, generando `sdist` y `wheel`
en `dist/`. El artefacto resultante se sube con `actions/upload-artifact`
para que la siguiente etapa lo consuma sin reconstruirlo —el mismo binario
testeado es el que se despliega.

### 4. Deploy
Solo corre cuando el evento es `push` y la rama es `main`. Descarga el
artefacto `dist`, crea una **GitHub Release** con tag basado en el número
de run y adjunta los binarios. Está aislado en el `environment: production`,
con permisos `contents: write` concedidos exclusivamente a este job.

## Principios DevOps aplicados

| Principio                    | Cómo se materializa                                          |
|------------------------------|--------------------------------------------------------------|
| Automatización completa      | Sin pasos manuales; todo dispara desde `push` o `PR`.        |
| Separación de etapas         | 4 jobs independientes (lint / test / build / deploy).        |
| Pasos reutilizables          | *Composite action* `setup-python-env` compartida por todos.  |
| Claridad en logs             | Pasos con nombres descriptivos en español; un paso = una idea. |
| Ejecución reproducible       | Versiones pinneadas, caché de pip, matriz de Python, mismo artefacto en build/deploy. |
| Seguridad                    | `permissions: read` global; escala a `write` solo en deploy. |
| Eficiencia                   | `concurrency` cancela runs viejos de la misma rama.          |

## Cómo verificarlo

1. Hacer push a `main` y observar la pestaña *Actions*.
2. Confirmar que los 4 jobs pasan en orden (`lint → test → build → deploy`).
3. Comprobar artefactos: `coverage-*` y `dist` en el run, y la Release nueva
   en la pestaña *Releases* del repositorio.
