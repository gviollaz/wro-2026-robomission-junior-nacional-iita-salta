# 🏆 La Alternativa Soñada — IITA WRO Bot v1

## "Construido por niños. Potenciado por IA. Explicado por ellos."

### Qué es esto

Este repositorio contiene el diseño completo de un robot de competencia para WRO RoboMission Junior 2026 "Heritage Heroes", desarrollado por el Instituto de Innovación y Tecnología Aplicada (IITA) de Salta, Argentina, con IA (Claude, Anthropic) como copiloto de diseño y aprendizaje.

**La apuesta:** Demostrar que alumnos de 11-15 años, con IA como herramienta de aprendizaje, pueden diseñar, construir y explicar un robot que compite al nivel de equipos con ingenieros profesionales.

### El robot en números

| Especificación | Valor |
|----------------|-------|
| Peso total | **~291g** (un SPIKE Prime vacío pesa 340g) |
| Dimensiones | 80×90×58mm plegado, 80×90×140mm con brazo |
| Procesadores | Teensy 4.1 (motores) + ESP32-S3 (sensores+cámara) |
| Motores tracción | 2× Pololu 30:1 HPCB con encoder 358 CPR |
| Mecanismos | 3× Dynamixel XL330-M288-T (garra+brazo+pala) |
| IMU | BNO055 9-axis, drift-free |
| Visión 3D | 2× VL53L5CX (128 puntos de profundidad) |
| Color | 7× VEML6040 array en piso + 1× TCS34725 en garra |
| Cámara | OV2640 2MP integrada en ESP32-S3 |
| Batería | LiPo 2S 800mAh 45C (~48 rondas sin cargar) |
| PCB | 2× PCBs custom 80×80mm, 4 capas, JLCPCB |
| Chasis | PLA+ 3D impreso (prototipo) → Aluminio 2mm (final) |
| Costo total | ~$330 USD |
| Puntaje esperado | 225-230/230 |

---

## 📚 Índice de documentación (orden de lectura recomendado)

### 🎯 Estrategia del juego

| # | Documento | Contenido | KB |
|---|-----------|-----------|-----|
| 1 | [diseno-230-campeon-junior.md](docs/diseno-230-campeon-junior.md) | Análisis del juego Heritage Heroes, 3 diseños de robot campeón (α Arquitecto, β Barrendero, γ Visionario), presupuesto de tiempo 120s | 19.8 |

### 🔧 Hardware — Del LEGO al custom

| # | Documento | Contenido | KB |
|---|-----------|-----------|-----|
| 2 | [hardware-tres-niveles-junior.md](docs/hardware-tres-niveles-junior.md) | 3 niveles: SPIKE puro ($350) → SPIKE+mejoras ($515) → Custom ($245). Comparativa de componentes, costos, pesos, puntajes | 17.8 |
| 3 | [nivel3-robot-custom-profundidad.md](docs/nivel3-robot-custom-profundidad.md) | Nivel 3 en detalle: GPIO mapping, PID a 1kHz con PCNT, Dynamixel con detección de contacto, sensor fusion, PCB spec para JLCPCB, FreeRTOS dual-core | 27.8 |
| 4 | [nivel3-plus-robot-definitivo.md](docs/nivel3-plus-robot-definitivo.md) | Nivel 3+ evolución: ESP32 vs Teensy (tabla 17 params), arquitectura dual, VL53L5CX 8×8, array 7 sensores color, PCB como chasis modular, BOM $330, 291g | 23.0 |
| 5 | [seleccion-bateria-driver-encoders.md](docs/seleccion-bateria-driver-encoders.md) | LiPo 2S 800mAh 45C, DRV8833 vs TB6612FNG, encoders Hall 12CPR integrados Pololu, lista de compra con modelos exactos | 12.2 |

### 📐 Diseño mecánico y 3D

| # | Documento | Contenido | KB |
|---|-----------|-----------|-----|
| 6 | [mecanismos-pinzas-diseno-3d.md](docs/mecanismos-pinzas-diseno-3d.md) | 4 tipos de garra, pinzas comerciales, OpenSCAD workflow, fabricación en metal, montaje modular rápido | 16.5 |
| 7 | [planos-robot-y-circuito.md](docs/planos-robot-y-circuito.md) | Planos mecánicos (vista superior + lateral), esquemático eléctrico completo, tablas GPIO, bus I2C, Dynamixel daisy-chain | 7.8 |
| 8 | [dimensiones-objetos-wro-junior-2026.md](docs/dimensiones-objetos-wro-junior-2026.md) | Dimensiones estimadas de todos los objetos del juego (visitantes, torres, artefactos, dirt), campos pendientes para medir con calibre | 6.6 |

### 📷 Sensores y visión

| # | Documento | Contenido | KB |
|---|-----------|-----------|-----|
| 9 | [vision/README.md](docs/vision/README.md) | Comparativa 4 cámaras (HuskyLens, OpenMV, ESP32-CAM, Pixy2), conexión con SPIKE via LMS-ESP32/PUPRemote | 12.5 |
| 10 | [vision/02-regla-wireless-wro.md](docs/vision/02-regla-wireless-wro.md) | ⚠️ Bluetooth/WiFi PROHIBIDO entre componentes en WRO. Solo cable. WiFi solo para práctica | 5.5 |
| 11 | [color-detection/README.md](docs/color-detection/README.md) | Detección de color avanzada, clasificador distancia euclidiana, media circular Hue, multitask | 14.8 |
| 12 | [color-detection/02-inmunidad-iluminacion.md](docs/color-detection/02-inmunidad-iluminacion.md) | 5 estrategias de inmunización a luz variable, cromaticidad normalizada, HSV con descarte V | 15.4 |

### 🤖 Skills de navegación

| # | Documento | Contenido | KB |
|---|-----------|-----------|-----|
| 13 | [movement/README.md](docs/movement/README.md) | Índice de mejores prácticas de movimiento |
| 14 | [movement/01-arranque-freno-suave.md](docs/movement/01-arranque-freno-suave.md) | Perfiles de velocidad, stop modes, velocidad máxima segura |
| 15 | [movement/02-odometria-precisa.md](docs/movement/02-odometria-precisa.md) | 3 métodos calibración, fuentes de error, fusión gyro+odometría |
| 16 | [movement/03-giroscopio.md](docs/movement/03-giroscopio.md) | hub.imu.ready(), heading_correction, recalibración |
| 17 | [movement/04-calibracion-pid.md](docs/movement/04-calibracion-pid.md) | Ziegler-Nichols simplificado, PID adaptativo, anti-windup |
| 18 | [line-following/](docs/line-following/) | 8 archivos: fundamentos → 1 sensor → 2 sensores → 3 sensores → intersecciones → alinear → estrategias competición |

### 🎓 Plan educativo

| # | Documento | Contenido | KB |
|---|-----------|-----------|-----|
| 19 | [plan-aprendizaje-ia-alumnos.md](docs/plan-aprendizaje-ia-alumnos.md) | **EL DOCUMENTO CENTRAL.** Plan 14 semanas con IA como copiloto. Filosofía educativa, actividades diarias, roles de equipo, respuestas para jueces, diario de viaje | 23.7 |

### ⚖️ Análisis crítico

| # | Documento | Contenido | KB |
|---|-----------|-----------|-----|
| 20 | [abogado-del-diablo-critica.md](docs/abogado-del-diablo-critica.md) | **Plan B.** Autocrítica brutal: 12 riesgos rankeados, diseño Nivel 3 lite a $180 como alternativa segura | 16.8 |

### 🔩 Archivos de diseño (OpenSCAD)

| Archivo | Qué es |
|---------|--------|
| [hardware/scad/config_objetos.scad](hardware/scad/config_objetos.scad) | Variables parametrizadas de dimensiones de objetos WRO |
| [hardware/scad/garra_v_xl330.scad](hardware/scad/garra_v_xl330.scad) | Garra tipo V para Dynamixel XL330, dedos PLA+TPU, soporte TCS34725 |
| [hardware/scad/bracket_pololu_n20.scad](hardware/scad/bracket_pololu_n20.scad) | Bracket en U para motor Pololu N20 con ventana encoder |
| [hardware/scad/placa_base_chasis.scad](hardware/scad/placa_base_chasis.scad) | Placa base 80×90mm, exportable DXF para corte láser aluminio |

### 📄 AI Skills (para generación de código con IA)

| Archivo | Para qué |
|---------|----------|
| [ai-skills/SKILL-line-following-pybricks.md](docs/ai-skills/SKILL-line-following-pybricks.md) | Generar código Pybricks de seguimiento de línea |
| [ai-skills/SKILL-line-following-blocks.md](docs/ai-skills/SKILL-line-following-blocks.md) | Generar código bloques de seguimiento de línea |
| [ai-skills/SKILL-movement-best-practices.md](docs/ai-skills/SKILL-movement-best-practices.md) | Generar código de movimiento con mejores prácticas |
| [ai-skills/SKILL-color-detection-python.md](docs/ai-skills/SKILL-color-detection-python.md) | Generar código Python de detección de color avanzada |

---

## 📊 Estadísticas del repositorio

| Métrica | Valor |
|---------|-------|
| Documentos técnicos | **20+** |
| Archivos OpenSCAD | **4** |
| AI Skills | **4** |
| Kilobytes de documentación | **~260 KB** |
| Horas de análisis con IA | ~6 horas (esta sesión) |

---

## 🗺️ Roadmap

### Inmediato (esta semana)
- [ ] Gustavo hace Pull de este repo
- [ ] Comprar/imprimir tapete WRO 2026 Junior
- [ ] Armar objetos del juego con brick set
- [ ] Medir objetos con calibre digital → actualizar `config_objetos.scad`

### Corto plazo (semanas 1-4)
- [ ] Decidir: ¿Plan A (Nivel 3+) o Plan B (Nivel 2 + SPIKE)?
- [ ] Si Plan A: pedir componentes (Pololu, Dynamixel, ESP32-S3)
- [ ] Si Plan B: empezar con SPIKE + BNO055 via LMS-ESP32
- [ ] Instalar OpenSCAD, renderizar y imprimir garra v1

### Mediano plazo (semanas 5-10)
- [ ] Robot base funcionando (tracción + navegación)
- [ ] Mecanismos probados con objetos reales
- [ ] PCB diseñada y enviada a JLCPCB
- [ ] Firmware de misiones en desarrollo

### Competencia (semanas 11-14)
- [ ] 50+ ejecuciones completas en tapete real
- [ ] Technical Summary escrito
- [ ] Presentación ante jueces ensayada
- [ ] Kit de herramientas y repuestos preparado

---

## 🏫 Sobre IITA

El **Instituto de Innovación y Tecnología Aplicada** (IITA / Fundación Innovar) es un instituto de educación tecnológica en Salta, Argentina, con sedes en Salta Centro y San Lorenzo Chico. Ofrece cursos de robótica, videojuegos, Python, IA, impresión 3D, y más. Los equipos de IITA compiten en WRO y RoboCupJunior, con el equipo de Soccer ganando el campeonato nacional argentino 2025.

**Coach:** Gustavo Viollaz ([@profegustavo](https://github.com/gviollaz))

---

*Este repositorio fue creado con asistencia de Claude (Anthropic) como herramienta de diseño y documentación. Todas las decisiones de ingeniería, la construcción física, la calibración, y las horas de práctica son responsabilidad exclusiva del equipo de IITA.*
