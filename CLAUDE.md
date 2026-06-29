# wro-2026-robomission-junior — instrucciones de proyecto

> Las directivas globales de Gustavo se heredan de la carpeta padre. Acá va solo lo específico del repo.

## ⚠️ Leé primero `AI-INSTRUCTIONS.md`

Este repo ya tiene **`AI-INSTRUCTIONS.md`** + **`CONTRIBUTING.md`** + **`CODEOWNERS`** con las reglas canónicas (incluidos los **headers obligatorios de autoría/IA** en los `.py`). Ese archivo manda; este CLAUDE.md solo orienta.

## Qué es

Documentación + diseño del robot **WRO RoboMission Junior 2026 "Heritage Heroes"** del equipo IITA Salta. Plataforma **LEGO Spike Prime + Pybricks** (Python que corre en el hub, vía code.pybricks.com).

## Estructura

- **`software/`** — programas Pybricks (`.py`): config base, calibración (brazo/color), tools de test de motores.
- **`hardware/`** — piezas **OpenSCAD** (`.scad`) para impresión 3D.
- **`docs/`** — arquitectura, hardware, research WRO 2026.
- **`journal/`**, **`testing/`** — bitácora y protocolos de prueba.

## Cómo trabajar

1. `AI-INSTRUCTIONS.md` → `CONTRIBUTING.md` → `README.md`.
2. Verificación read-only: `python -m py_compile software/.../<archivo>.py` (chequea sintaxis; `pybricks` no es pip-instalable pero py_compile no resuelve imports). `openscad -o /dev/null hardware/**/*.scad` para validar SCAD.
3. **La prueba real es en el robot físico** (cargar Pybricks al hub + calibrar en el mat oficial WRO). Eso lo cierra el equipo humano, no se automatiza.

## Regla IITA

- Sin datos sensibles en el repo. `.gitignore` ya bloquea `.env`/`*.pem`/`*.key`.
