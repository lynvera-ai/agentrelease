# Primeros pasos con Lynvera AgentRelease

Experimental, en desarrollo. AgentRelease compara evidencias de pruebas con
criterios explícitos de publicación y genera reportes reproducibles. Está
dirigido a personas que ya tienen resultados de pruebas de un agente.
No ejecuta agentes, no autentica las evidencias y no certifica seguridad general.

## Instalar

Requiere Python 3.12 o posterior con `pip` y `venv`, y Git para clonar. La
validación local incluye macOS Apple Silicon con Python 3.12.9, 3.13.6 y
3.14.4, y Linux ARM64 en contenedor Debian con Python 3.12.16. Windows y otras
combinaciones siguen pendientes. Consulta la [matriz](../validation-matrix.md).

```sh
git clone --branch v0.1.0 --single-branch https://github.com/lynvera-ai/agentrelease.git
cd agentrelease
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m pip check
agentrelease --version
```

El resultado esperado es `AgentRelease 0.1.0`. Guarda el resultado de
`git rev-parse HEAD` para identificar el código exacto. El
[release experimental v0.1.0](https://github.com/lynvera-ai/agentrelease/releases/tag/v0.1.0)
incluye el wheel, el código fuente y las sumas de comprobación.
La [guía de instalación](../installation.md) explica ese recorrido y el uso
de un wheel sin conexión. No uses `pip install agentrelease` sin una ruta
para instalar esta versión; no está publicada en PyPI.

La instalación puede descargar herramientas pequeñas y PyYAML. La evaluación
funciona localmente, sin claves, cuentas, modelos, conexión ni servicios pagados.

## Primera prueba

Desde la carpeta del proyecto, con el entorno activo:

```sh
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json
```

Las primeras líneas serán:

```text
AgentRelease: PASS
Policy: synthetic-release
Evaluator version: 0.1.0
```

El reporte incluye tres comprobaciones aprobadas. El código de salida es `0`.
Todos los ejemplos contienen datos sintéticos.

Para guardar JSON:

```sh
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json --format json --output report.json
python -c "import json; r = json.load(open('report.json')); print(r['status'], len(r['checks']))"
```

El resultado esperado es `PASS 3`. El archivo debe ser nuevo y su carpeta
debe existir y permitir escritura. No se sobrescriben entradas ni reportes
anteriores. Usa otro nombre al repetir el comando.

## Interpretar y configurar

| Estado | Significado | Código |
| --- | --- | --- |
| PASS | Se cumplen todos los criterios obligatorios | 0 |
| FAIL | Una evidencia válida incumple un criterio | 1 |
| INCONCLUSIVE | Falta una prueba o medida, o se omitió una prueba | 2 |
| ERROR | Entrada inválida, error de evaluación, archivo o uso de la CLI | 3 |

La prioridad es `ERROR > FAIL > INCONCLUSIVE > PASS`. Solo PASS representa
éxito de evaluación. Los comandos de ayuda y versión también devuelven 0.

La configuración consiste en una política YAML y evidencias JSON, indicadas
con `--policy` y `--evidence`. No hay configuración global ni credenciales.
Consulta el [formato completo](../formats.md) y `agentrelease evaluate --help`.
Los reportes de entrada van a la salida estándar; los errores de uso o escritura,
a la salida de errores.

Para actualizar, crea un entorno nuevo, instala el candidato revisado y prueba
los ejemplos. Conserva el entorno, wheel y reportes anteriores para recuperar
la instalación si hace falta. Para desinstalar:

```sh
python -m pip uninstall agentrelease
```

La desinstalación no borra evidencias ni reportes. Ante INPUT_IO, revisa rutas
y permisos; ante OUTPUT_IO, elige otro nombre en una carpeta escribible.
No publiques credenciales, rutas personales, evidencias privadas ni registros.

La aceptación externa sigue pendiente. Las comparaciones no tienen tolerancia,
conversión de unidades ni interpretación estadística. No hay integraciones,
servicios cloud ni promesa de preparación para producción.

[Documentación principal](../../README.md) y
[guía de revisión externa](../external-review.md).
