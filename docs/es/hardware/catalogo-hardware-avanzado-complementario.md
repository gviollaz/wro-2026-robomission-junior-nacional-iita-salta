# Hardware avanzado WRO 2026 — Hallazgos complementarios

> **Qué es este documento.** Catálogo acotado de hallazgos de investigación que **NO están cubiertos** en los otros docs de `docs/es/hardware/`. No repite motores, encoders, batería, drivers, PCB custom, pinzas 3D, cámaras ni planos — todo eso ya vive en los docs dedicados. Acá solo va el delta.
>
> **Docs relacionados en este directorio:**
> - [`hardware-tres-niveles-junior.md`](./hardware-tres-niveles-junior.md) — estrategia 3 niveles
> - [`nivel3-robot-custom-profundidad.md`](./nivel3-robot-custom-profundidad.md) — robot custom
> - [`nivel3-plus-robot-definitivo.md`](./nivel3-plus-robot-definitivo.md) — evolución nivel 3
> - [`diseno-230-campeon-junior.md`](./diseno-230-campeon-junior.md) — diseño para 230 pts
> - [`seleccion-bateria-driver-encoders.md`](./seleccion-bateria-driver-encoders.md) — selección eléctrica
> - [`mecanismos-pinzas-diseno-3d.md`](./mecanismos-pinzas-diseno-3d.md) — pinzas y garras
> - [`planos-robot-y-circuito.md`](./planos-robot-y-circuito.md) — planos
> - [`vision-camaras/`](./vision-camaras/) — cámaras y visión
>
> **Fecha:** 2026-04-11 · **Versión:** 2.0 (reescritura acotada)

---

## Marco legal WRO 2026 (resumen operativo)

Reglas RoboMission 2026 (v. 15-ene-2026) confirman libre elección de hardware. Límites duros: **250×250×250 mm** antes del arranque, **1500 g** peso máximo, **4 motores** (Elementary) / **5 motores** (Junior), **sin wireless entre componentes** del robot durante la corrida, **cámaras prohibidas en Elementary** (permitidas en Junior y Senior), LIDAR/escáneres 3D solo en Senior. Múltiples controladores están permitidos. Fuente: [WRO 2026 RoboMission General Rules](https://wro-association.org/wp-content/uploads/WRO-2026-RoboMission-General-Rules.pdf).

> **Acción IITA:** confirmar con organizador nacional WRO Argentina que dos hubs SPIKE coordinados vía Pybricks BLE sean aceptados (sección 6).

---

## 1. SparkFun PAA5160E1 — odometría óptica de piso

**Hallazgo principal de esta investigación.** Ningún doc del repo menciona tracking óptico de piso como alternativa al encoder+gyro.

- Sensor óptico de flujo + IMU 6-ejes con **fusión a bordo**, en un solo módulo Qwiic de 25×25 mm, ~$25 USD.
- Diseñado específicamente para robots de competencia FTC/XRP — provee posición X/Y sub-milimétrica del desplazamiento en el piso, **sin depender de encoders de rueda**.
- Elimina el error acumulado por patinaje de ruedas, diámetro inconsistente y backlash de caja reductora — precisamente los problemas que el doc `hardware-tres-niveles-junior.md` identifica como limitación del Nivel 1.
- Conexión I2C vía cable Qwiic al LMS-ESP32 (cero soldadura). Láser clase 1 seguro.
- Precio: $24.95 en [sparkfun.com](https://www.sparkfun.com/sparkfun-optical-tracking-odometry-sensor-paa5160e1-qwiic.html). Envío a AR vía Tiendamia.
- **Legal Junior ✅ / Elementary ✅** (es un sensor, no una cámara). Dificultad Pybricks: 3/5 (requiere LMS-ESP32 como bridge I2C).

**Por qué importa:** el robot Nivel 2 del repo gana ~$25 una mejora de navegación que supera al encoder+gyro del SPIKE sin requerir un salto a Nivel 3.

---

## 2. VL53L5CX — array ToF 8×8 (mini-LIDAR legal en Junior)

El doc `hardware-tres-niveles-junior.md` ya cubre VL53L1X. El VL53L5CX es el escalón siguiente y no aparece en ningún doc del repo.

- **Array de 8×8 = 64 zonas de detección** simultáneas, rango 4 m, hasta 60 Hz en modo 4×4 o 15 Hz en 8×8.
- Funciona como un "mini-LIDAR" sin partes móviles — te permite detectar obstáculos en múltiples direcciones **sin mover el sensor**.
- **Legal en Junior y Elementary**: WRO 2026 prohíbe LIDAR escaneante solo en categorías Senior; el VL53L5CX es un sensor ToF estático multizona, no un escáner mecánico.
- Precio: $8–15 en AliExpress, $19.95 en [Pololu #3417](https://www.pololu.com/product/3417), $24.95 Qwiic en SparkFun.
- Driver ST requiere ~90 KB de RAM — el ESP32 del LMS-ESP32 lo soporta sin problema. Ya hay drivers Arduino/MicroPython probados.
- Dificultad Pybricks: 3/5 (vía LMS-ESP32 I2C + PUPRemote al hub).

**Caso de uso WRO:** detección de la geometría del area de apilado de torres sin detenerse a escanear con un VL53L1X puntual. Reemplaza barridos mecánicos con un motor dedicado.

---

## 3. SPIKE-RT / TOPPERS ASP3 — firmware alternativo con benchmarks publicados

Ningún doc del repo evalúa alternativas a Pybricks. Este hallazgo es relevante porque los docs asumen Pybricks como único firmware viable.

- **SPIKE-RT** es el sucesor del EV3RT japonés, desarrollado por el laboratorio ERTL de la Universidad de Nagoya. Corre **TOPPERS/ASP3 RTOS** directamente en el STM32F413 del hub SPIKE Prime. Ganó el Premio de Plata en el TOPPERS Application Development Contest 2022.
- Repositorio: [github.com/spike-rt/spike-rt](https://github.com/spike-rt/spike-rt) · Gratis · Programación en C.

**Benchmarks publicados** (砂田沙耶, dev.to, marzo 2025):

| Métrica | SPIKE-RT (C) | Pybricks (Python) | SPIKE App 3 (Bloques) |
|---|---|---|---|
| Error detección color en movimiento | **2%** | 5% | 22% |
| Distancia de frenado | Menor | Media | Mayor |
| Estabilidad line-follower alta velocidad | Estable | Buena | Inestable |

- La diferencia 2% vs 5% en detección de color puede decidir una misión WRO.
- **Trade-off:** requiere Docker, toolchain ARM GCC, flash vía USB DFU, y programar en C. Solo recomendable con un mentor con experiencia en C embebido.
- **Otras alternativas evaluadas y descartadas:** leJOS (imposible, necesita JVM/Linux), ev3dev (imposible, Cortex-M4 sin MMU), Zephyr RTOS (soporta el STM32F413 pero nadie creó el BSP del hub SPIKE), FreeRTOS bare-metal (sin proyectos activos para SPIKE).

---

## 4. Investigación OFDL Robotics Lab Taiwan — el "equipo referencia"

Relevante para el análisis en `docs/research/analisis-lauxiao-taiwan.md`. La búsqueda de un producto comercial llamado "MBC Hue12" en Shopee Taiwan, Taobao, PCHome, Ruten y Google en chino **no arrojó ningún resultado**.

**Hallazgo probable:** el equipo taiwanés referencia es **OFDL Robotics Lab** (崇倫國中, Taichung), 4° puesto WRO Internacional 2020, más de una década en WRO.

- Sitio: [ofdl.tw](https://ofdl.tw/en/) · GitHub: [github.com/ofdl-robotics-tw](https://github.com/ofdl-robotics-tw)
- Repos clave que IITA puede usar directamente:
  - **`lump-device-builder-library`** — librería Arduino para crear sensores LPF2 custom que el hub SPIKE reconoce como sensores LEGO nativos. **Elimina la necesidad del bridge LMS-ESP32 + PUPRemote** si estás dispuesto a programar Arduino.
  - **`SPIKE-utils`** — utilidades Pybricks para SPIKE Prime.
  - **`SPIKE-PD_Line_Follow`** — PD line-following con valores raw normalizados de 2 sensores LEGO Color (demuestra que no hacen falta arrays de 8 sensores para line-following competitivo).
- El "Hue12" probablemente es un **array custom de 12 sensores TCS34725** conectados a un Arduino/ESP32 con protocolo LUMP, apareciendo como sensor LPF2 nativo. No se compra: se construye con la `lump-device-builder-library` de OFDL.

**Acción IITA:** clonar `lump-device-builder-library` y `SPIKE-PD_Line_Follow` y adaptarlos. Es propiedad intelectual regalada por un equipo WRO top-4 mundial.

---

## 5. Nexus 48 mm Omni Wheels — hub LEGO nativo

Las ruedas omnidireccionales no están cubiertas en ningún doc del repo (`hardware-tres-niveles-junior.md` trata ruedas de silicona y O-rings, no omni/mecanum).

- **Nexus 48 mm Omni Wheels** con hub para eje cruz Technic — **encajan directo en el eje de un motor LEGO sin adaptador impreso**.
- 3 omni wheels en configuración holonómica (120° entre sí) dan movimiento en cualquier dirección sin rotar el chasis. Útil para maniobrar entre objetos apilados sin perturbarlos.
- Precio: ~$6.50–7.50 c/u, set de 3 (código 14113) ~$16–20. Envío a AR vía RobotShop/Tiendamia.
- **Legal Junior ✅ / Elementary ✅** (WRO 2026: *"Any kind of wheels (including omni wheels) or tracks can be used."*). Dificultad Pybricks: 1/5 (plug and play).
- Link: [nexusrobot.com producto 14113](https://www.nexusrobot.com/product/a-set-of-48mm-omni-wheel-for-lego-nxt-and-servo-motor-14113.html)

**Alternativa mecanum:** sets de 4 ruedas mecanum 64 mm con adaptador LEGO incluido en Amazon/AliExpress por $15–25. Más complejas de programar (cinemática mecanum) pero permiten el mismo movimiento holonómico con 4 ruedas estándar.

---

## 6. Pybricks BLE Multi-Hub — 2 hubs coordinados sin wireless intra-robot

Solución para cuando se agotan los 6 puertos del hub SPIKE. Ningún doc del repo lo menciona.

- Pybricks v3.6 incluye `hub.ble.broadcast(channel, data)` y `hub.ble.observe(channel)` nativos.
- **Dos hubs SPIKE Prime** en el mismo robot: hub A lee sensores y transmite en canal 1, hub B recibe y controla motores. Total: **12 puertos disponibles** en lugar de 6.
- Latencia ~100 ms por ciclo, payload ~26 bytes, sin necesidad de emparejar — funciona como radio broadcast.
- Costo: segundo hub ~$100 usado en Bricklink, ~$350 nuevo.

**⚠️ Advertencia regulatoria crítica:** las reglas WRO 2026 dicen *"no wireless communication between components of the robot during the run"*. Pybricks BLE broadcast/observe **técnicamente es comunicación wireless entre componentes**, aunque Pybricks lo implemente sin emparejamiento. **Antes de diseñar el robot alrededor de esta arquitectura, Gustavo debe consultar por escrito al organizador nacional WRO Argentina** si dos hubs coordinados por Pybricks BLE son aceptados en la edición nacional 2026. Si la respuesta es no, usar LMS-ESP32 + TCA9548A como expansor I2C cableado (ver sección siguiente).

Ejemplo de código:

```python
# Hub A (sensores)
from pybricks.hubs import PrimeHub
hub = PrimeHub(broadcast_channel=1)
while True:
    hub.ble.broadcast(sensor.color())

# Hub B (motores)
hub = PrimeHub(observe_channels=[1])
while True:
    data = hub.ble.observe(1)
    if data is not None:
        motor.run_angle(500, data)
```

---

## 7. TCA9548A + LMS-ESP32 — alternativa cableada al multi-hub

Complemento directo del LMS-ESP32 ya mencionado en `hardware-tres-niveles-junior.md`. El TCA9548A no aparece explícitamente en ese doc.

- **TCA9548A** es un multiplexor I2C 1→8 canales, ~$3–5 en AliExpress.
- Resuelve el problema de **múltiples sensores con la misma dirección I2C** (ej: 4× VL53L1X todos en 0x29). Cada canal del TCA9548A es un bus I2C aislado.
- Arquitectura: 1 puerto SPIKE → LMS-ESP32 → TCA9548A → hasta 8 sensores I2C + servos PWM + NeoPixels simultáneamente.
- **100% cableado**, sin riesgo regulatorio WRO.

**Caso de uso:** robot IITA con 4× VL53L1X (direcciones frontal/trasera/izquierda/derecha) + BNO055 (heading) + PAA5160E1 (odometría) + TCS34725 (color) — todo colgando de **1 solo puerto SPIKE**, dejando los otros 5 para motores y sensores LEGO nativos.

---

## 8. BNO085 + ESP32 — advertencia crítica de compatibilidad

Si el repo (en `nivel3-robot-custom-profundidad.md` o `seleccion-bateria-driver-encoders.md`) considera el BNO085 como upgrade del BNO055, esta advertencia es relevante antes de comprarlo.

- El BNO085 es técnicamente superior al BNO055: mejor firmware de fusión, calibración automática persistente, drift <5°/10 min.
- **Pero tiene un problema documentado con I2C + ESP32**. Adafruit confirmó en sus foros que la implementación I2C del BNO085 viola el protocolo estándar en ciertas circunstancias, causando hangs o lecturas corruptas cuando el master es un ESP32. Fuente: [foro Adafruit](https://forums.adafruit.com/viewtopic.php?t=182704).
- **Recomendación operativa:** si el bridge es LMS-ESP32 (ESP32), **usar BNO055 por I2C** o BNO085 **en modo UART-RVC** (salida serial simple de heading + aceleración, sin I2C). No usar BNO085 en I2C con ESP32.

---

## Presupuesto delta recomendado para IITA

Agregados a un robot Nivel 2 del doc `hardware-tres-niveles-junior.md`:

| Componente | Proveedor | USD | Justificación |
|---|---|---|---|
| SparkFun PAA5160E1 | SparkFun (Tiendamia) | 25 | Odometría de piso — sección 1 |
| VL53L5CX (AliExpress) | AliExpress | 12 | Mini-LIDAR 8×8 — sección 2 |
| TCA9548A | AliExpress | 4 | Multiplexor I2C — sección 7 |
| Nexus Omni 48 mm ×3 | RobotShop/Tiendamia | 20 | Holonómico — sección 5 |
| **Total delta** | | **~$61** | |

Este delta se **suma** al BOM Nivel 2 existente ($515). No reemplaza componentes — los extiende.

---

## Fuentes

- [WRO 2026 RoboMission General Rules](https://wro-association.org/wp-content/uploads/WRO-2026-RoboMission-General-Rules.pdf) · [WRO 2026 Robots Meet Culture (v.16-12-2025)](https://wro.lv/wp-content/uploads/2026/01/WRO-2026-RoboMission-General-Rules-UPDATED-2025-12-16.pdf)
- [SparkFun PAA5160E1 product page](https://www.sparkfun.com/sparkfun-optical-tracking-odometry-sensor-paa5160e1-qwiic.html)
- [Pololu VL53L5CX #3417](https://www.pololu.com/product/3417) · [STMicro VL53L5CX](https://www.st.com/en/imaging-and-photonics-solutions/vl53l5cx.html) · [Pimoroni VL53L5CX](https://shop.pimoroni.com/en-us/products/vl53l5cx-time-of-flight-tof-sensor-breakout)
- [spike-rt en GitHub](https://github.com/spike-rt/spike-rt) · [gpdaniels/spike-prime (reverse engineering)](https://github.com/gpdaniels/spike-prime)
- [OFDL Robotics Lab Taiwan en GitHub](https://github.com/ofdl-robotics-tw) · [ofdl.tw](https://ofdl.tw/en/) · [SPIKE-PD_Line_Follow repo](https://github.com/ofdl-robotics-tw/SPIKE-PD_Line_Follow)
- [Nexus 48 mm Omni Wheels LEGO-compatible (14113)](https://www.nexusrobot.com/product/a-set-of-48mm-omni-wheel-for-lego-nxt-and-servo-motor-14113.html)
- [Anton's Mindstorms: LEGO with Laser Distance Sensor](https://www.antonsmindstorms.com/2024/05/02/lego-with-a-laser-distance-sensor/) · [PUPRemote library](https://www.antonsmindstorms.com/2023/09/07/make-your-custom-robot-electronics-speak-like-a-custom-lego-sensor-with-pupremote-library/) · [Pybricks support for LMS-ESP32](https://www.antonsmindstorms.com/2023/02/12/proof-of-concept-pybricks-support-for-lms-esp32/)
- [Adafruit forum: BNO085 vs BNO055 I2C issues](https://forums.adafruit.com/viewtopic.php?t=182704)
- [Pybricks i2c on SPIKE Prime — discussion #1047](https://github.com/orgs/pybricks/discussions/1047)
- [Adafruit TCA9548A I2C Multiplexer](https://www.adafruit.com/product/2717)

---

**Nota sobre este documento.** Versión 1.0 (2026-04-11) era un placeholder sin contenido. Versión 2.0 reescrita tras auditar los 10 docs existentes en `docs/es/hardware/` para eliminar ~80% del contenido que ya estaba cubierto en `hardware-tres-niveles-junior.md`, `nivel3-robot-custom-profundidad.md`, `nivel3-plus-robot-definitivo.md`, `seleccion-bateria-driver-encoders.md`, `mecanismos-pinzas-diseno-3d.md` y `vision-camaras/`. Solo queda el delta de hallazgos nuevos.
