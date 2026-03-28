# NIVEL 3+ Evolución: El Robot Definitivo para WRO Junior 2026

## Todas las preguntas de Gustavo, analizadas en profundidad

> Este documento responde cada pregunta sobre mejoras al Nivel 3 con análisis técnico fundamentado: sensores ToF avanzados, cámara, motores rápidos con encoder, LiDAR, array de sensores de color en piso, PCB como chasis, y ESP32 vs Teensy 4.1.

---

## 1. ESP32-S3 vs Teensy 4.1: ¿cuál es mejor para este robot?

### Tabla comparativa decisiva

| Parámetro | ESP32-S3 | Teensy 4.1 | ¿Cuál gana? |
|-----------|---------|-----------|--------------|
| **CPU** | Xtensa LX7 240MHz dual-core | ARM Cortex-M7 600MHz | **Teensy** (2.5× más rápido) |
| **RAM** | 512KB SRAM + 8MB PSRAM | 1024KB SRAM tightly-coupled | **Teensy** (RAM ultra rápida) |
| **Flash** | 8-16MB SPI | 8MB | Empate |
| **FPU** | Single-precision (32-bit) | **Double-precision (64-bit)** | **Teensy** (clave para PID) |
| **PWM outputs** | 8 LEDC channels | **35 FlexPWM** | **Teensy** (más motores) |
| **Encoder hardware** | 4 PCNT units | **4 QuadTimer + FlexPWM encoder mode** | **Teensy** (más flexible) |
| **ADC** | 2× 12-bit SAR | **2× 12-bit + 1× 10-bit**, 18 canales | **Teensy** |
| **I2C** | 2 buses | **3 buses** | **Teensy** (separar sensores lentos de rápidos) |
| **UART** | 3 | **8** | **Teensy** (Dynamixel en UART dedicado) |
| **WiFi/BLE** | **✅ Sí (802.11n + BLE 5.0)** | ❌ No | **ESP32** (debug inalámbrico) |
| **Cámara integrada** | **✅ DVP paralelo OV2640** | ❌ No nativo | **ESP32** |
| **Precio** | ~$8 | ~$30 | **ESP32** |
| **Tamaño** | 18×25mm (módulo) | 61×18mm (board) | **ESP32** (3× más chico) |
| **Comunidad Arduino** | Enorme (ESP-IDF + Arduino) | Grande (Teensyduino) | Empate |
| **MicroPython** | ✅ Nativo | ⚠️ CircuitPython (limitado) | **ESP32** |
| **Latencia ISR** | ~2µs | **~0.1µs** (determinístico) | **Teensy** (20× menor) |

### El veredicto para WRO

**Para este robot específico, la respuesta es: DEPENDE de qué priorizás.**

**Elegir Teensy 4.1 si:**
- La prioridad es **control de motores ultra preciso** (PID a 10kHz+)
- Se necesitan **muchos periféricos UART** (Dynamixel en UART dedicado, sin multiplexar)
- Se quiere FPU de 64 bits para navegación con mínimo error de redondeo
- No se necesita WiFi para debugging (se usa USB serial)
- Se trabaja en C++ con Arduino IDE

**Elegir ESP32-S3 si:**
- Se quiere **WiFi para debugging** en práctica (stream de sensores al celular)
- Se integra **cámara OV2640** directamente en el controlador
- Se prefiere **MicroPython** para prototipado rápido
- El costo importa ($8 vs $30)
- El tamaño importa (módulo 3× más chico)

### Mi recomendación: ARQUITECTURA DUAL

La jugada maestra que usan los equipos de élite de RoboCup y WRO avanzado es **dos procesadores con roles separados**:

```
┌─────────────────────┐         ┌──────────────────────┐
│   Teensy 4.1        │  UART   │   ESP32-S3           │
│   "Motor Brain"     │◄───────►│   "Sensor Brain"     │
│                     │ 1Mbps   │                      │
│ - PID motores 5kHz  │         │ - Cámara OV2640      │
│ - Dynamixel TTL     │         │ - WiFi debug         │
│ - Encoder PCNT      │         │ - BNO055 fusion      │
│ - Lógica de misión  │         │ - ToF array          │
│ - Odometría         │         │ - Color sensors      │
│                     │         │ - Envía: heading,    │
│ Recibe: heading,    │         │   colores, distancias│
│ colores, objetos    │         │   objetos detectados │
└─────────────────────┘         └──────────────────────┘
```

**Costo extra:** Solo $8 (el ESP32-S3). **Ventaja:** Cada procesador hace lo que mejor sabe. El Teensy controla motores con latencia de 0.1µs. El ESP32 procesa cámara y sensores con WiFi para debug.

**¿Es esto legal en WRO?** Sí. La regla dice "1 controlador" pero se refiere a que el robot es autónomo (1 robot, no controlado remotamente). Múltiples procesadores internos están permitidos, igual que un SPIKE Prime + LMS-ESP32 son dos procesadores. La comunicación entre ellos es por cable (UART), no wireless.

---

## 2. Sensores ToF avanzados: el mapa 3D del entorno

### La evolución: de 1 punto a 64 puntos

| Sensor | Zonas | FoV | Rango | Frecuencia | Precio | I2C |
|--------|-------|-----|-------|-----------|--------|-----|
| VL53L0X | 1 | 25° | 2m | 50Hz | $5 | 0x29 |
| VL53L1X | 1 | 27° (programable) | 4m | 50Hz | $12 | 0x29 |
| VL53L4CX | 1 (multi-target) | 18° | 6m | 60Hz | $15 | 0x29 |
| **VL53L5CX** | **8×8 = 64** | **63°** | **4m** | **60Hz** | **$20** | 0x29 |
| **VL53L8CX** | **8×8 = 64** | **65°** | **4m** | **60Hz** | **$22** | 0x29 |

### VL53L5CX: un mini-LiDAR en un chip

El VL53L5CX es una revolución. Un solo sensor de $20 te da **64 mediciones de distancia simultáneas** en una grilla de 8×8, actualizadas a 60Hz. Es como tener 64 sensores VL53L1X en uno solo.

**¿Qué podés hacer con esto que no podés con un VL53L1X?**

- **Detectar objetos y su posición lateral** sin mover el robot. La grilla 8×8 te dice "hay algo a 15cm en la zona (3,4)" — sabés que está a la izquierda-arriba del centro.
- **Clasificar objetos por forma.** Una torre ocupa 2×1 zonas (alta y angosta). Un visitante ocupa 2×2 zonas. Un artefacto ocupa 1×1 zona. Sin cámara.
- **Medir distancia a la pared mientras avanzás.** Las zonas laterales de la grilla ven las paredes del campo, las centrales ven objetos adelante.

### ¿8 sensores ToF en los bordes?

La idea de Gustavo de poner 8 VL53L1X apuntando a los 8 puntos cardinales alrededor del robot es inteligente pero hay una opción más elegante:

**Opción A: 8× VL53L1X individuales ($96)**

```
        [ToF N]
    [ToF NW]  [ToF NE]
  [ToF W]  ROBOT  [ToF E]
    [ToF SW]  [ToF SE]
        [ToF S]
```

Requiere 8 sensores, re-address de I2C (complejo), 8 cables, mucho espacio.

**Opción B: 2× VL53L5CX ($40) — MUCHO MEJOR**

```
    [VL53L5CX frontal, 63° FoV]
              ↓ ve todo lo que está adelante en 8×8 zonas
            ROBOT
              ↑ ve todo lo que está atrás en 8×8 zonas
    [VL53L5CX trasero, 63° FoV]
```

Con 2 sensores VL53L5CX (uno adelante, uno atrás), el robot tiene **visión 3D de 360°** con 128 puntos de medición. Cada sensor cubre 63° de campo de visión. Con el robot girando, puede mapear todo el entorno.

Además, al montar uno mirando al piso en ángulo, puede detectar las líneas y zonas del tapete por diferencia de distancia (las líneas están impresas, no en relieve, pero los objetos del campo sí tienen altura detectable).

### ¿Sirve un LiDAR?

**LiDAR rotativo (tipo RPLidar A1):** Mapeo 360° a 12m con 8000 puntos/s. Es espectacular para SLAM y navegación autónoma.

**Pero para WRO:** Es overkill. El campo es de 2.4×1.8m con objetos conocidos en posiciones semi-conocidas. El robot no necesita SLAM; necesita ir a coordenadas precisas. Un LiDAR rotativo agrega peso (~170g), costo (~$100), y complejidad. El VL53L5CX da suficiente información espacial.

**LiDAR punto (TF-Luna):** $20, 8m rango, ±6mm precisión, 2° FoV, 250Hz. Puede servir como sensor de distancia de alta velocidad para alineación precisa con paredes. Pero el VL53L1X a $12 hace casi lo mismo.

**Veredicto:** No usar LiDAR rotativo. Usar 2× VL53L5CX como "mini-LiDAR" integrado.

---

## 3. ¿Sirve una cámara? ¿Cuál?

### Para qué sirve la cámara en Heritage Heroes

| Tarea | Sin cámara | Con cámara |
|-------|-----------|-----------|
| Detectar color artefactos | Ir a cada uno, sensor a 15mm | **Ver los 4 desde lejos, identificar al pasar** |
| Verificar apilado de torre | No sabés si quedó bien | **Verificar visualmente después de depositar** |
| Encontrar partículas de suciedad | Barrer ciego | **Ver dónde están las partículas negras** |
| Ajustar posición frente a objetos | Solo odometría/ToF | **Visual servoing: centrar objeto en imagen** |

### La cámara que más aporta

**OpenMV H7 Plus ($85):** La mejor para visión de competencia.
- Cortex-M7 dedicado (no comparte CPU con el robot)
- IDE propia con vista en vivo por USB
- `find_blobs()` a 30+ FPS en 320×240
- TensorFlow Lite para clasificación
- Se conecta al Teensy por UART (envía: "objeto rojo en x=150, y=80, area=2000")

**ESP32-S3 + OV2640 ($15):** Si usás la arquitectura dual, el ESP32-S3 ya tiene cámara integrada.
- Procesamiento en el mismo chip que los sensores
- Stream WiFi para debug
- Más lento que OpenMV para visión (pero suficiente para WRO)

**Recomendación:** En arquitectura dual, el ESP32-S3 YA tiene cámara. No gastar extra en OpenMV a menos que necesitemos TensorFlow Lite para clasificación avanzada.

---

## 4. Motores rápidos con encoder para tracción

### Los mejores motores para robot de competencia WRO

| Motor | Tipo | RPM | Torque | Encoder | Peso | Precio/u |
|-------|------|-----|--------|---------|------|----------|
| Pololu 50:1 HPCB 6V | N20 metal | 310 | 1.5 kg·cm | 600 CPR | 10g | $15 |
| **Pololu 30:1 HPCB 6V** | N20 metal | **500 RPM** | 1.0 kg·cm | **360 CPR** | 10g | $15 |
| Pololu 10:1 HPCB 6V | N20 metal | **1500 RPM** | 0.3 kg·cm | 120 CPR | 10g | $15 |
| **TT motor con encoder hall** | Plastic gear | 200 | 0.8 kg·cm | 330 CPR | 25g | $5 |
| Maxon DCX 10L + GPX 10 26:1 | Swiss | 460 | 0.8 kg·cm | 512 CPR | 8g | $200+ |
| **Faulhaber 2224-006SR + 22/5 14:1** | German | 500 | 1.0 Nm | **3000+ CPR (IE2-1024)** | 15g | $250+ |

### ¿Qué significa "rápido"?

Para un robot WRO con ruedas de 32mm de diámetro:

| Motor RPM | Velocidad del robot | ¿Para WRO? |
|-----------|--------------------|-----------| 
| 150 RPM | 250 mm/s | Lento (misiones con tiempo justo) |
| 300 RPM | **500 mm/s** | **Ideal (rápido + controlable)** |
| 500 RPM | 840 mm/s | Rápido (difícil frenar preciso) |
| 1500 RPM | 2500 mm/s | Excesivo (imposible de controlar en 2.4m) |

**El campo tiene 2.4m de largo.** A 500mm/s (Pololu 30:1), lo cruzás en 4.8 segundos. No necesitás ir más rápido; necesitás **frenar preciso**.

### Recomendación: Pololu 30:1 HPCB (el sweet spot)

- 500 RPM → ~840mm/s teóricos, usarías ~500mm/s en práctica
- 360 CPR → suficiente para 0.28mm/count con rueda de 32mm
- Engranajes de acero nitrurado (mínimo backlash)
- Carbon brushes HPCB (vida útil 10× mayor que precious metal)
- Costo: $15/u → $30 por par
- Peso: 10g/u → 20g el par (vs 110g el par de LEGO)

### Ruedas óptimas

Para maximizar tracción y precisión odométrica:

| Rueda | Diámetro | Material | Ventaja |
|-------|----------|----------|---------|
| Pololu 32×7mm | 32mm | Plástico + O-ring silicona | La más precisa, diámetro constante |
| Pololu 42×19mm | 42mm | Plástico + O-ring silicona | Más rápida (mayor diámetro) |
| Custom 3D PLA + TPU 70A band | Configurable | PLA hub + TPU banda | Diámetro exacto a medida |

**Recomendación:** Pololu 32×7mm con O-ring de silicona 70A. Diámetro ultra constante, sin deformación bajo carga, excelente tracción en el tapete WRO.

---

## 5. Array de sensores de color en el piso: la PCB como sensor distribuido

### La idea: una PCB que ES el piso del robot

En vez de tener 1-2 sensores de color, diseñar la PCB para que tenga **múltiples sensores de color integrados en su cara inferior**, mirando al piso. El robot "ve" el tapete desde abajo con resolución espacial.

```
Vista inferior de la PCB (el robot visto desde abajo):

  ┌──────────────────────────────────┐
  │                                  │
  │  [C1]  [C2]  [C3]  [C4]  [C5]  │  ← 5 sensores color frontales
  │                                  │     detectan líneas y zonas
  │          [C6]  [C7]             │  ← 2 sensores centrales
  │                                  │     confirman posición
  │  ⊙ Rueda izq     Rueda der ⊙   │
  │                                  │
  │          [C8]  [C9]             │  ← 2 sensores traseros
  │                                  │     detectan al cruzar líneas
  │              ◎                   │  ← Rueda loca
  └──────────────────────────────────┘
```

### ¿Qué sensor usar para el array?

| Sensor | Canales | Tamaño | I2C | Precio | Multiplexable |
|--------|---------|--------|-----|--------|--------------|
| **VEML6040** | RGBW | 2×2mm | 0x10 (fijo) | $2 | Sí con TCA9548A |
| TCS34725 | RGBC | 3.9×2.4mm | 0x29 (fijo) | $8 | Sí con TCA9548A |
| **APDS-9960** | RGBC+prox | 3.9×2.4mm | 0x39 (fijo) | $3 | Sí con TCA9548A |
| ISL29125 | RGB | 2×2.2mm | 0x44 | $3 | Dirección fija |

**Problema:** Todos estos sensores tienen dirección I2C fija. Para poner 9 en el mismo bus necesitamos un **multiplexor I2C**.

### TCA9548A: multiplexor I2C de 8 canales ($2)

```
I2C Bus principal (ESP32-S3)
        │
  ┌─────┤ TCA9548A (0x70)
  │     │
  │  ch0 ├── VEML6040 #1 (0x10) ← Sensor color frontal izq
  │  ch1 ├── VEML6040 #2 (0x10) ← Sensor color frontal centro-izq
  │  ch2 ├── VEML6040 #3 (0x10) ← Sensor color frontal centro
  │  ch3 ├── VEML6040 #4 (0x10) ← Sensor color frontal centro-der
  │  ch4 ├── VEML6040 #5 (0x10) ← Sensor color frontal der
  │  ch5 ├── VEML6040 #6 (0x10) ← Sensor color central izq
  │  ch6 ├── VEML6040 #7 (0x10) ← Sensor color central der
  │  ch7 ├── VL53L5CX (0x29) ← ToF frontal
  │
  │  I2C Bus directo (sin mux):
  ├── BNO055 (0x28)
  ├── VL53L5CX #2 (0x30, re-addressed)
  └── TCS34725 (0x29) ← Sensor color para objetos (en brazo)
```

### ¿Qué puede hacer el robot con 9 sensores de color en el piso?

**1. Seguir líneas sin PID.** Con 5 sensores frontales en línea, detectás exactamente la posición de la línea relativa al robot. En vez de un PID que oscila, usás interpolación directa: "la línea está entre el sensor 3 y 4, ligeramente a la derecha" → corrección proporcional exacta.

**2. Detectar intersecciones y zonas instantáneamente.** Cuando los 5 sensores frontales ven todos el mismo color (blanco, verde, rojo), sabés que entraste a una zona. Cuando 2-3 ven negro y los otros blanco, es una línea cruzando.

**3. Alineación perpendicular a líneas.** Si el sensor 1 y 5 (extremos) ven la línea al mismo tiempo, el robot está perpendicular. Si el sensor 1 la ve antes que el 5, el robot está girado a la izquierda.

**4. Odometría por color.** Al cruzar zonas de diferentes colores, el robot confirma su posición. "Acabo de pasar de blanco a marrón → estoy en el cobblestone." Esto corrige el drift acumulado de la odometría de ruedas.

### Velocidad de lectura: ¿alcanzan 9 sensores?

VEML6040 a 40ms integration time = 25Hz por sensor. Con TCA9548A y lectura secuencial:

- Seleccionar canal: ~100µs
- Leer sensor: ~1ms (I2C a 400kHz)
- Total 9 sensores: 9 × 1.1ms ≈ **10ms → 100Hz**

A 500mm/s, en 10ms el robot avanza 5mm. Eso significa que el array de sensores tiene resolución espacial de 5mm en la dirección de movimiento. Más que suficiente para líneas de 10-20mm de ancho.

---

## 6. La PCB como chasis: diseño mecánico modular

### Concepto: PCB-Chassis con sistema de montaje

```
Vista explosionada:

  Nivel 3: Mecanismos (intercambiables por misión)
  ┌─────────────────────────────┐
  │  Garra + Brazo + Pala       │  ← Piezas 3D, se atornillan
  │  (Dynamixel ×3)             │     a la PCB superior
  └──────────┬──────────────────┘
             │ tornillos M2.5
  Nivel 2: PCB Superior ("Sensor Brain")
  ┌──────────┴──────────────────┐
  │  ESP32-S3 + OV2640          │  ← PCB 80×80mm, FR4 1.6mm
  │  TCA9548A + VEML6040 ×7    │     Sensores color en cara inferior
  │  VL53L5CX ×2               │     ToF en bordes
  │  BNO055                     │     WiFi antenna on top
  └──────────┬──────────────────┘
             │ standoffs M2 (12mm)
  Nivel 1: PCB Inferior ("Motor Brain")
  ┌──────────┴──────────────────┐
  │  Teensy 4.1                 │  ← PCB 80×80mm, FR4 1.6mm
  │  DRV8833 ×2                │     Motor drivers + connectors
  │  Dynamixel TTL hub          │     Power management
  │  TPS5430 + AMS1117          │     Battery connector
  │  Motor connectors ×5        │     Encoder connectors ×2
  └──────────┬──────────────────┘
             │ motor brackets (3D print)
  Nivel 0: Tracción
  ┌──────────┴──────────────────┐
  │  Pololu 30:1 HPCB ×2       │  ← Montados en brackets 3D
  │  Ruedas 32mm + O-ring       │     atornillados a PCB inferior
  │  Rueda loca trasera          │
  │  LiPo 2S 500mAh             │  ← Batería entre las ruedas
  └─────────────────────────────┘
```

### Sistema de montaje/desmontaje rápido

**Nivel 0 → Nivel 1:** Los motores se montan en brackets 3D impresos con insertos M2. Los brackets se atornillan a la PCB inferior con 4 tornillos M2. Cambiar un motor: 4 tornillos + desconectar JST.

**Nivel 1 → Nivel 2:** Standoffs M2 de 12mm de aluminio. 4 standoffs. Desmontaje: 4 tuercas.

**Nivel 2 → Nivel 3:** Los mecanismos (garra, brazo, pala) se montan con tornillos M2.5 en agujeros pasantes de la PCB superior. **Los Dynamixel XL330 tienen agujeros de montaje estándar M2.5.** Cambiar de mecanismo: sacar 6-8 tornillos.

### Altura total

| Nivel | Altura |
|-------|--------|
| Ruedas (base del robot al piso) | 16mm (radio rueda 32mm/2) |
| PCB inferior + componentes | 15mm |
| Standoffs | 12mm |
| PCB superior + componentes | 15mm |
| Mecanismos (garra + brazo) | ~80mm desplegado |
| **Total plegado** | **~58mm** (sin mecanismo arriba) |
| **Total con mecanismo** | **~140mm** (con brazo arriba) |

Cabe en 25×25×25cm sin problemas.

---

## 7. BOM del robot definitivo (Nivel 3+)

| Componente | Cant. | Precio/u | Total |
|------------|-------|----------|-------|
| **Controladores** | | | |
| Teensy 4.1 | 1 | $30 | $30 |
| ESP32-S3-DevKitC-1 + OV2640 | 1 | $15 | $15 |
| **Motores** | | | |
| Pololu 30:1 HPCB 6V con encoder | 2 | $15 | $30 |
| Dynamixel XL330-M288-T | 3 | $24 | $72 |
| **Sensores** | | | |
| BNO055 breakout (Adafruit) | 1 | $30 | $30 |
| VL53L5CX breakout (Pololu/SparkFun) | 2 | $20 | $40 |
| VEML6040 breakout (array piso) | 7 | $2 | $14 |
| TCA9548A I2C multiplexor | 1 | $2 | $2 |
| TCS34725 (sensor objetos en brazo) | 1 | $8 | $8 |
| **Electrónica** | | | |
| DRV8833 dual H-bridge | 2 | $3 | $6 |
| TPS5430 5V/2A buck regulator | 1 | $2 | $2 |
| AMS1117-3.3V | 1 | $0.10 | $0.10 |
| **PCBs** | | | |
| PCB inferior "Motor Brain" (JLCPCB) | 1 | $15 | $15 |
| PCB superior "Sensor Brain" (JLCPCB) | 1 | $15 | $15 |
| **Estructura** | | | |
| Chasis 3D PLA + TPU | 1 | $15 | $15 |
| Standoffs M2 aluminio 12mm | 4 | $0.50 | $2 |
| Insertos metálicos M2/M2.5 | 20 | $0.10 | $2 |
| Tornillos M2/M2.5 surtido | — | — | $5 |
| **Energía** | | | |
| LiPo 2S 7.4V 500mAh | 1 | $8 | $8 |
| **Ruedas** | | | |
| Pololu 32×7mm + O-ring silicona | 2 | $3 | $6 |
| Rueda loca 14mm (ball caster) | 1 | $3 | $3 |
| **Cables/conectores** | | | |
| JST-SH cables, headers, misc | — | — | $10 |
| **TOTAL** | | | **~$330** |

### Peso estimado total

| Componente | Peso |
|------------|------|
| Teensy 4.1 | 5g |
| ESP32-S3 módulo | 3g |
| Pololu motors ×2 | 20g |
| Dynamixel ×3 | 54g (18g × 3) |
| PCBs ×2 (80×80mm FR4) | 40g |
| BNO055 breakout | 3g |
| VL53L5CX ×2 | 4g |
| VEML6040 ×7 | 7g |
| Chasis 3D + brackets | 50g |
| Ruedas + caster | 15g |
| LiPo 2S 500mAh | 30g |
| Cables, conectores | 20g |
| Dynamixel mecanismos (3D) | 40g |
| **TOTAL** | **~291g** |

**291 gramos.** Es un robot de competencia de menos de 300g. Para comparar: un SPIKE Prime solo (sin motores ni sensores) pesa 340g. Este robot completo pesa menos que el hub SPIKE solo.

---

## 8. ¿Qué ganamos vs el Nivel 3 original?

| Aspecto | Nivel 3 original | Nivel 3+ (este doc) | Mejora |
|---------|-----------------|--------------------|---------| 
| Controlador | ESP32-S3 solo | **Teensy 4.1 + ESP32-S3** | PID 5kHz + WiFi + cámara |
| ToF | 2× VL53L1X (2 puntos) | **2× VL53L5CX (128 puntos)** | Mapa 3D del entorno |
| Color piso | 1 sensor | **7 sensores en array** | Sigue líneas sin PID, detecta zonas |
| Motor tracción | 100:1 (150 RPM) | **30:1 (500 RPM)** | 3× más rápido |
| Cámara | ESP32-S3 integrada | **ESP32-S3 integrada + WiFi debug** | Igual + mejor debug |
| Estructura | 1 PCB + chasis 3D | **2 PCBs modulares + chasis 3D** | Montaje/desmontaje rápido |
| Peso | 350-500g | **~291g** | 20-40% más liviano |
| Costo | ~$245 | **~$330** | +$85 por mucha más capacidad |

---

## 9. La pregunta final: ¿vale la pena todo esto?

### Para nacional argentino: **NO**

Un SPIKE Prime bien armado (Nivel 1-2) con 200 horas de práctica gana el nacional. La competencia local todavía no tiene equipos con robots custom de este nivel. Invertir en más tiempo de práctica rinde más que invertir en mejor hardware.

### Para clasificar al mundial: **QUIZÁS**

Si IITA clasifica al mundial con SPIKE, evaluar migrar a Nivel 3 parcial (agregar BNO055 + VL53L5CX + piezas 3D). No hace falta ir a Nivel 3+ completo.

### Para ganar el mundial: **SÍ**

Los equipos que ganan el mundial de WRO Junior en 2025-2026 ya están usando hardware custom. Robots de 300g con motores de precisión, sensores de gama alta, y chasis 3D optimizados. El SPIKE Prime es una plataforma de aprendizaje; estos robots son máquinas de competencia.

### El plan IITA a 2 años

1. **2026 Nacional:** Nivel 2 (SPIKE + BNO055 + LMS-ESP32). Foco en práctica y estrategia.
2. **2026 Mundial (si clasifica):** Nivel 2 mejorado + piezas 3D + VL53L5CX.
3. **2027 pretemporada:** Desarrollar plataforma Nivel 3+ completa. Diseñar PCBs, probar motores, calibrar. Esto lleva 3-4 meses.
4. **2027 temporada:** Usar plataforma Nivel 3+ con mecanismos nuevos para el juego de ese año. Solo cambiar las piezas 3D del mecanismo, toda la electrónica se reutiliza.

> **La inversión de 2027 se amortiza en 3+ temporadas. Las PCBs, motores y sensores son reutilizables. Solo se rediseña el mecanismo cada año.**
