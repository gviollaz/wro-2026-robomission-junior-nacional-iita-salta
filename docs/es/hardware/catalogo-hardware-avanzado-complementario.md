# ⚠️ Nota de ubicación

El contenido completo de este informe está en el artifact generado en la conversación de Claude del 2026-04-11 (ID: `compass_artifact_wf-0d388957-501c-44d2-b7a3-cdcb89152d5d`).

**Este archivo es un placeholder** porque el contenido completo (~30 KB, 8 secciones con tablas comparativas, 50+ componentes, investigación OFDL Taiwan, benchmarks SPIKE-RT) excede el presupuesto de tokens disponible en la sesión de push.

## Acción requerida por Gustavo

1. Copiar el contenido del artifact de Claude (visible en la UI de la conversación del 2026-04-11)
2. Pegarlo en este archivo reemplazando este placeholder
3. Hacer ACP desde el IITA Git Panel

## Qué contiene el informe completo

Catálogo complementario a `hardware-tres-niveles-junior.md` con hardware avanzado para SPIKE Prime + Pybricks NO cubierto en ese doc:

1. **Sensores de línea** — Pololu QTR-8RC, Mindsensors LineLeader/SPSumoEyes, MyOwnBricks DIY
2. **Posicionamiento absoluto** — SparkFun PAA5160E1 (odometría óptica), AS5600/AS5048B, PMW3901, advertencia BNO085+ESP32
3. **ToF** — VL53L0X/L1X/L5CX (array 8×8 mini-LIDAR), Mindsensors SPToF LPF2 nativo
4. **Cámaras** (solo Junior) — ESP32-S3-CAM, M5Stack UnitV2, OAK-D Lite, investigación OFDL Robotics Lab Taiwan (equipo referencia real, github.com/ofdl-robotics-tw)
5. **Firmwares** — SPIKE-RT/TOPPERS ASP3 con benchmarks (2% error vs 5% de Pybricks en detección de color)
6. **Ruedas** — Nexus 48mm Omni LEGO-compatible, Pololu silicona, FingerTech poliuretano, mecanum 64mm
7. **Motores** — tabla comparativa torque/RPM/encoder LEGO vs Pololu HP vs Dynamixel XL-320/XC330
8. **Multiplexores** — Pybricks BLE Multi-Hub (2 hubs coordinados), LMS-ESP32+TCA9548A, splitters pasivos

Presupuesto upgrade recomendado: ~$128 USD (Junior) / ~$113 (Elementary).

Incluye tabla de proveedores con envío a Salta AR (AliExpress, Tiendamia, antonsmindstorms.com, MercadoLibre).

## Referencia cruzada

Ver también: [`hardware-tres-niveles-junior.md`](./hardware-tres-niveles-junior.md) — guía estratégica de 3 niveles (SPIKE puro / SPIKE+mejoras / custom).
