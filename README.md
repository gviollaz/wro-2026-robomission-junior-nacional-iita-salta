# WRO RoboMission Junior 2026 — "Heritage Heroes" — Nacional Argentina

> **Equipo IITA Salta** | Repo creado desde [IITA Competition Template (ICRS)](https://github.com/IITA-Proyectos/iita-competition-template).

## Documentación completa

📋 **[Índice principal (ES)](docs/es/index.md)** — punto de entrada a toda la documentación

### Competencia

| Documento | Descripción |
|---|---|
| [Análisis de misiones](docs/es/competition/analisis-misiones-junior-2026.md) | Desafío completo, puntajes, randomización, estrategia por misión |
| [Dimensiones objetos WRO](docs/es/competition/dimensiones-objetos-wro-junior-2026.md) | Medidas de torres, artefactos, visitantes, partículas |
| [Reglas competencia](docs/es/competition/README.md) | Resumen reglas WRO 2026 RoboMission Junior |

### Diseño del robot

| Documento | Descripción |
|---|---|
| [Diseño robot IITA v1](docs/es/diseno_robot_iita_v1.md) | Decisión de arquitectura definitiva — 2WD, elevador, compuerta |
| [Diseño 230 pts campeón](docs/es/hardware/diseno-230-campeon-junior.md) | Diseño optimizado para puntaje máximo |
| [Robot definitivo nivel 3+](docs/es/hardware/nivel3-plus-robot-definitivo.md) | Evolución del robot con piezas custom |
| [Robot custom profundidad](docs/es/hardware/nivel3-robot-custom-profundidad.md) | Diseño custom avanzado con análisis detallado |
| [Hardware tres niveles](docs/es/hardware/hardware-tres-niveles-junior.md) | Progresión LEGO puro → híbrido → custom |
| [Diseño físico robot](docs/es/hardware/diseno-fisico-robot.md) | Especificaciones físicas y mecánicas |
| [Mecanismos y pinzas 3D](docs/es/hardware/mecanismos-pinzas-diseno-3d.md) | Diseño de garras, pinzas y mecanismos impresos 3D |
| [Planos robot y circuito](docs/es/hardware/planos-robot-y-circuito.md) | Planos de referencia rápida |
| [Batería, drivers, encoders](docs/es/hardware/seleccion-bateria-driver-encoders.md) | Selección de componentes eléctricos |
| [Visión por cámara](docs/es/hardware/vision-camaras/README.md) | Comparativa HuskyLens/OpenMV/ESP32-CAM/Pixy2 + conexión SPIKE |
| [Especificación mecánica](hardware/roboto_iita_v1.md) | BOM y módulos físicos del robot v1 |

### Software

| Documento | Descripción |
|---|---|
| [Arquitectura de control](software/programs/arquitectura_control_iita_v1.md) | Organización del código Pybricks |
| [Calibración PID e IA](docs/es/software/calibracion-pid-e-ia.md) | Tuning PID con asistencia de IA |
| [Estrategias posicionamiento](docs/es/software/estrategias-posicionamiento.md) | Navegación y posicionamiento en el mat |
| [Serie: Seguimiento de línea](docs/es/software/line-following/README.md) | 7 capítulos — fundamentos → competición |
| [Serie: Movimiento](docs/es/software/movement/README.md) | 4 capítulos — arranque suave, odometría, giroscopio, PID |
| [Serie: Detección de color](docs/es/software/color-detection/README.md) | Guía completa + inmunidad a iluminación |
| [Perfiles calibración](software/calibration/perfiles_calibracion_iita_v1.md) | Perfiles de calibración documentados |

### Código fuente

| Path | Descripción |
|---|---|
| `software/programs/base_config.py` | Configuración base del robot |
| `software/calibration/calibrar_brazo.py` | Script calibración del brazo |
| `software/calibration/calibrar_color.py` | Script calibración de color |
| `software/tools/test_motores.py` | Test de motores |
| `hardware/scad/` | Piezas 3D OpenSCAD (chasis, garra, bracket) |

### Testing y journal

| Documento | Descripción |
|---|---|
| [Plan de validación](testing/plan_validacion_iita_v1.md) | Métricas, pruebas y criterios de aceptación |
| [Journal 2026-03-28](journal/2026-03-28-diseno-robot-iita-v1.md) | Registro de decisión: diseño robot v1 |

### Otros

| Documento | Descripción |
|---|---|
| [Plan aprendizaje IA alumnos](docs/es/learning/plan-aprendizaje-ia-alumnos.md) | Material pedagógico para el equipo |
| [Crítica abogado del diablo](docs/es/reviews/abogado-del-diablo-critica.md) | Análisis crítico del diseño |
| [Alternativa README soñada](docs/es/reviews/ALTERNATIVA-SONADA-README.md) | Alternativa de presentación del proyecto |
| [AI Skills](docs/ai-skills/) | 4 skills para asistentes IA (line-following, color, movement) |
| [Arquitectura general](docs/es/architecture/README.md) | Visión de alto nivel del diseño |
| [Onboarding](docs/es/onboarding/README.md) | Guía para nuevos miembros |
| [Operaciones](docs/es/operations/README.md) | Logística y checklist competencia |

## Status

| Campo | Valor |
|---|---|
| **Season** | 2026 |
| **Theme** | Robots Meet Culture |
| **Competition** | WRO (World Robot Olympiad) |
| **Category** | RoboMission Junior (11-15 años) |
| **Challenge** | Heritage Heroes (fortaleza histórica) |
| **Scope** | Nacional Argentina |
| **Team** | IITA Salta |
| **Platform** | LEGO Spike Prime + Pybricks (Python) |
| **Puntaje máximo** | 230 puntos |

## Resumen del desafío

El robot trabaja en una fortaleza histórica:
1. **Guiar visitantes** a áreas por color (40 pts)
2. **Reconstruir torres** — rojas al target + apilar tapas amarillas (80 pts)
3. **Artefactos al museo** — detectar color y llevar a exhibition spot (60 pts)
4. **Limpiar adoquines** — sacar 10 partículas del área (20 pts)
5. **Bonus** — no dañar barreras ni loro (30 pts)

**Randomización:** 4 de 5 artefactos + 10 partículas cambian cada ronda → sensor de color obligatorio.

## Setup

1. Instalar firmware Pybricks en Spike Prime: [pybricks.com/install](https://pybricks.com/install/)
2. Abrir [code.pybricks.com](https://code.pybricks.com) para programar en Python
3. Configurar DriveBase con medidas reales del robot
4. Calibrar sensor de color en el mat oficial WRO
5. Calibrar ángulos del brazo elevador

## Contributing

Ver `CONTRIBUTING.md` y la [política ICRS](https://github.com/IITA-Proyectos/iita-competition-playbook).
