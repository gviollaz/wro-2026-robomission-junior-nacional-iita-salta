# WRO RoboMission Junior 2026 "Heritage Heroes" — Documentación (ES)

## Índice completo

### 🏆 Competencia
- [Reglas y puntajes](competition/README.md) — Resumen reglas WRO 2026 RoboMission Junior
- [Análisis de misiones](competition/analisis-misiones-junior-2026.md) — Desafío completo, puntajes, randomización, estrategia por misión
- [Dimensiones objetos WRO](competition/dimensiones-objetos-wro-junior-2026.md) — Medidas de torres, artefactos, visitantes, partículas

### 🤖 Arquitectura
- [Visión general](architecture/README.md) — Diseño general del robot
- [Diseño robot IITA v1](diseno_robot_iita_v1.md) — Decisión de arquitectura definitiva: 2WD, elevador, compuerta

### 🔧 Hardware
- [Introducción hardware](hardware/README.md)
- [Diseño físico robot](hardware/diseno-fisico-robot.md) — Especificaciones físicas y mecánicas completas
- [Diseño 230 pts campeón](hardware/diseno-230-campeon-junior.md) — Diseño optimizado para puntaje máximo
- [Robot definitivo nivel 3+](hardware/nivel3-plus-robot-definitivo.md) — Evolución con piezas custom
- [Robot custom profundidad](hardware/nivel3-robot-custom-profundidad.md) — Diseño custom avanzado
- [Hardware tres niveles](hardware/hardware-tres-niveles-junior.md) — Progresión: LEGO puro → híbrido → custom
- [Mecanismos y pinzas 3D](hardware/mecanismos-pinzas-diseno-3d.md) — Garras, pinzas y mecanismos impresos 3D
- [Planos robot y circuito](hardware/planos-robot-y-circuito.md) — Planos de referencia rápida
- [Batería, drivers, encoders](hardware/seleccion-bateria-driver-encoders.md) — Selección de componentes eléctricos
- [Especificación mecánica v1](../../hardware/roboto_iita_v1.md) — BOM y módulos físicos

#### Visión por cámara
- [Guía completa cámaras](hardware/vision-camaras/README.md) — Comparativa HuskyLens/OpenMV/ESP32-CAM/Pixy2 + conexión SPIKE
- [Regla wireless WRO](hardware/vision-camaras/02-regla-wireless-wro.md) — Análisis de la regla de comunicación inalámbrica

### 💻 Software
- [Introducción software](software/README.md)
- [Calibración PID e IA](software/calibracion-pid-e-ia.md) — Tuning PID con asistencia de IA
- [Estrategias posicionamiento](software/estrategias-posicionamiento.md) — Navegación y posicionamiento en el mat
- [Arquitectura de control v1](../../software/programs/arquitectura_control_iita_v1.md) — Organización del código Pybricks
- [Perfiles calibración v1](../../software/calibration/perfiles_calibracion_iita_v1.md) — Perfiles de calibración documentados

#### Serie: Seguimiento de línea (7 capítulos)
- [Índice de la serie](software/line-following/README.md)
- [01 — Fundamentos](software/line-following/01-fundamentos.md)
- [02 — Un sensor](software/line-following/02-un-sensor.md)
- [03 — Dos sensores](software/line-following/03-dos-sensores.md)
- [04 — Tres sensores](software/line-following/04-tres-sensores.md)
- [05 — Intersecciones](software/line-following/05-intersecciones.md)
- [06 — Encontrar y alinear](software/line-following/06-encontrar-y-alinear.md)
- [07 — Estrategias competición](software/line-following/07-estrategias-competicion.md)

#### Serie: Movimiento (4 capítulos)
- [Índice de la serie](software/movement/README.md)
- [01 — Arranque y freno suave](software/movement/01-arranque-freno-suave.md)
- [02 — Odometría precisa](software/movement/02-odometria-precisa.md)
- [03 — Giroscopio](software/movement/03-giroscopio.md)
- [04 — Calibración PID](software/movement/04-calibracion-pid.md)

#### Serie: Detección de color (2 capítulos)
- [Guía completa](software/color-detection/README.md)
- [02 — Inmunidad a iluminación](software/color-detection/02-inmunidad-iluminacion.md)

### 📝 Testing
- [Plan de validación v1](../../testing/plan_validacion_iita_v1.md) — Métricas, pruebas y criterios de aceptación

### 📓 Journal
- [2026-03-28 — Diseño robot v1](../../journal/2026-03-28-diseno-robot-iita-v1.md) — Registro de decisión y trazabilidad técnica

### 📚 Aprendizaje
- [Plan aprendizaje IA alumnos](learning/plan-aprendizaje-ia-alumnos.md) — Material pedagógico para el equipo

### 🔍 Revisiones y análisis
- [Crítica abogado del diablo](reviews/abogado-del-diablo-critica.md) — Análisis crítico del diseño actual
- [Alternativa README soñada](reviews/ALTERNATIVA-SONADA-README.md) — Alternativa de presentación del proyecto

### 🤖 AI Skills
Los siguientes archivos son consumidos por asistentes de IA para generar código y sugerencias:
- [SKILL — Color detection Python](../ai-skills/SKILL-color-detection-python.md)
- [SKILL — Line following blocks](../ai-skills/SKILL-line-following-blocks.md)
- [SKILL — Line following Pybricks](../ai-skills/SKILL-line-following-pybricks.md)
- [SKILL — Movement best practices](../ai-skills/SKILL-movement-best-practices.md)

### 👋 Equipo
- [Onboarding](onboarding/README.md) — Guía para nuevos miembros
- [Operaciones](operations/README.md) — Logística y checklist competencia

---

### Código fuente

| Path | Descripción |
|---|---|
| `software/programs/base_config.py` | Configuración base del robot |
| `software/calibration/calibrar_brazo.py` | Script calibración del brazo |
| `software/calibration/calibrar_color.py` | Script calibración de color |
| `software/tools/test_motores.py` | Test de motores |
| `hardware/scad/*.scad` | Piezas 3D OpenSCAD (chasis, garra XL330, bracket Pololu N20) |
