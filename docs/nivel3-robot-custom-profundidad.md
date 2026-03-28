# NIVEL 3 en Profundidad: Robot Custom para WRO Junior 2026

## Documento de ingeniería detallada — "IITA WRO Bot v1"

> Este documento expande el Nivel 3 del análisis de hardware con el detalle necesario para construirlo. Cubre arquitectura eléctrica, PCB, firmware, mecánica, y fabricación.

---

## 1. Arquitectura del sistema completa

```
                         ┌──────────────────────────────────┐
                         │    "IITA WRO Bot v1" — PCB       │
                         │                                  │
  LiPo 2S 7.4V ─────▶  │  [TPS5430 5V/2A] [AMS1117 3.3V] │
  500mAh 30g            │        │               │         │
                         │        ▼               ▼         │
                         │  ┌──────────────────────────┐    │
                         │  │     ESP32-S3-WROOM-1     │    │
                         │  │                          │    │
                         │  │  Core 0: Motor Control   │    │
                         │  │    - PID loop 1kHz       │    │
                         │  │    - Encoder ISR          │    │
                         │  │    - Dynamixel TTL        │    │
                         │  │                          │    │
                         │  │  Core 1: Mission Logic   │    │
                         │  │    - Navigation FSM       │    │
                         │  │    - Sensor fusion         │    │
                         │  │    - Camera (OV2640)      │    │
                         │  │    - WiFi debug (práctica)│    │
                         │  └──────────────────────────┘    │
                         │       │    │    │    │    │       │
                         │       ▼    ▼    ▼    ▼    ▼       │
                         │  [DRV8833] [DRV8833] [DXL TTL]  │
                         │   M1  M2    M3  M4   S1 S2 S3   │
                         │                                  │
                         │  [BNO055]  [VL53L1X×2] [TCS34725]│
                         │  I2C bus @ 400kHz                │
                         │                                  │
                         │  [OV2640]  [Buzzer] [LED×4]     │
                         │  [BTN Start] [BTN Select]        │
                         └──────────────────────────────────┘
                              │         │         │
                              ▼         ▼         ▼
                         Tracción   Mecanismos  Sensores
                         Pololu×2   DXL330×3    BNO/ToF/Color
```

### Asignación de GPIOs del ESP32-S3

| GPIO | Función | Notas |
|------|---------|-------|
| 1 | DRV8833_A IN1 (Motor izq) | PWM LEDC ch0 |
| 2 | DRV8833_A IN2 (Motor izq) | PWM LEDC ch1 |
| 3 | DRV8833_A IN3 (Motor der) | PWM LEDC ch2 |
| 4 | DRV8833_A IN4 (Motor der) | PWM LEDC ch3 |
| 5 | DRV8833_B IN1 (Motor mec 3) | PWM LEDC ch4 (si se usa 3er N20) |
| 6 | DRV8833_B IN2 (Motor mec 3) | PWM LEDC ch5 |
| 7 | Encoder izq A | Interrupt, PCNT unit 0 |
| 8 | Encoder izq B | Interrupt, PCNT unit 0 |
| 9 | Encoder der A | Interrupt, PCNT unit 1 |
| 10 | Encoder der B | Interrupt, PCNT unit 1 |
| 11 | Dynamixel TTL TX/RX | Half-duplex UART1 |
| 12 | Dynamixel DIR (dirección bus) | GPIO output |
| 13 | I2C SDA | Shared bus: BNO055, VL53L1X×2, TCS34725 |
| 14 | I2C SCL | 400kHz, pull-up 4.7kΩ |
| 15 | OV2640 SDA (SCCB) | I2C camera config |
| 16 | OV2640 SCL (SCCB) | |
| 17-24 | OV2640 D0-D7 | Paralelo 8-bit |
| 38 | OV2640 PCLK | |
| 39 | OV2640 VSYNC | |
| 40 | OV2640 HREF | |
| 41 | OV2640 XCLK | 20MHz output |
| 42 | Buzzer (PWM) | Para feedback sonoro |
| 43 | LED Status | NeoPixel WS2812B |
| 44 | BTN Start | Pull-up, active low |
| 45 | BTN Select | Pull-up, active low |
| 46 | nFAULT DRV8833_A | Input, fault detection |
| 47 | nFAULT DRV8833_B | Input |
| 48 | Battery voltage divider | ADC, 10kΩ/4.7kΩ divider |

### Bus I2C: direcciones

| Dispositivo | Dirección I2C | Notas |
|-------------|--------------|-------|
| BNO055 | 0x28 (default) | Pin ADR a GND |
| VL53L1X #1 (frontal) | 0x29 (default) | Después de re-address: 0x30 |
| VL53L1X #2 (lateral) | 0x30 | XSHUT pin para secuencia de inicio |
| TCS34725 | 0x29 | Conflicto con VL53L1X → re-address VL53L1X primero |

**Secuencia de inicio I2C:**
1. Mantener XSHUT de VL53L1X #2 en LOW
2. Inicializar VL53L1X #1 en 0x29, re-address a 0x30
3. Liberar XSHUT de VL53L1X #2
4. Inicializar VL53L1X #2 en 0x29, re-address a 0x31
5. Ahora TCS34725 puede usar 0x29 sin conflicto
6. Inicializar BNO055 en 0x28

---

## 2. Control de motores de tracción

### Pololu 100:1 HPCB 6V — Especificaciones

| Parámetro | Valor |
|-----------|-------|
| Voltaje nominal | 6V |
| RPM sin carga | 150 RPM |
| Corriente sin carga | 100mA |
| Torque máx | 2.0 kg·cm |
| Corriente stall | 1600mA |
| Encoder | 12 CPR en eje motor × 100:1 = **1200 CPR en eje de salida** |
| Tipo encoder | Hall effect, cuadratura |
| Peso | 10g |

### Comparación con motor LEGO

| Parámetro | LEGO Medium | Pololu 100:1 HPCB | Mejora |
|-----------|-------------|-------------------|--------|
| Resolución encoder | 360 CPR | 1200 CPR | **3.3×** |
| Backlash | 2-3° | <1° (engranajes metal) | **>2×** |
| Peso motor | 55g | 10g | **5.5×** más liviano |
| Torque | 0.18 Nm | 0.20 Nm | Similar |
| Control de corriente | No | Sí (via DRV8833 sense) | **Nuevo** |

### PID de velocidad con PCNT del ESP32-S3

El ESP32-S3 tiene un periférico **PCNT** (Pulse Counter) dedicado para contar pulsos de encoder en hardware, sin interrumpir la CPU. Esto es enormemente superior a interrupciones por software.

```cpp
// Configuración PCNT para encoder cuadratura
#include "driver/pcnt.h"

pcnt_config_t pcnt_config = {
    .pulse_gpio_num = ENC_A_PIN,
    .ctrl_gpio_num = ENC_B_PIN,
    .channel = PCNT_CHANNEL_0,
    .unit = PCNT_UNIT_0,
    .pos_mode = PCNT_COUNT_INC,   // Cuenta A rising + B high = forward
    .neg_mode = PCNT_COUNT_DEC,   // Cuenta A rising + B low = reverse
    .lctrl_mode = PCNT_MODE_REVERSE,
    .hctrl_mode = PCNT_MODE_KEEP,
    .counter_h_lim = 32767,
    .counter_l_lim = -32768,
};
```

### PID loop a 1kHz en Core 0

```cpp
// Core 0: motor control task (1kHz)
void motorControlTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    while (true) {
        // Leer encoders (PCNT, sin costo CPU)
        int16_t enc_left, enc_right;
        pcnt_get_counter_value(PCNT_UNIT_0, &enc_left);
        pcnt_get_counter_value(PCNT_UNIT_1, &enc_right);
        
        // Calcular velocidad actual (counts/ms)
        float vel_left = (enc_left - prev_left) * 1000.0f;  // counts/sec
        float vel_right = (enc_right - prev_right) * 1000.0f;
        
        // PID para cada motor
        float output_left = pid_compute(&pid_left, target_vel_left, vel_left);
        float output_right = pid_compute(&pid_right, target_vel_right, vel_right);
        
        // Aplicar PWM al DRV8833
        drv8833_set_speed(MOTOR_LEFT, output_left);
        drv8833_set_speed(MOTOR_RIGHT, output_right);
        
        prev_left = enc_left;
        prev_right = enc_right;
        
        // 1ms period exacto
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(1));
    }
}
```

### Parámetros PID recomendados (punto de partida)

| Parámetro | Valor inicial | Rango de ajuste |
|-----------|--------------|-----------------|
| Kp | 0.8 | 0.3 - 2.0 |
| Ki | 0.05 | 0.01 - 0.2 |
| Kd | 0.02 | 0.005 - 0.1 |
| Output límite | ±255 (8-bit PWM) | — |
| Anti-windup | ±500 (integral clamp) | — |
| Deadband | 10 counts/s | — |
| Frecuencia PWM | 20kHz | Inaudible |

### Odometría y navegación

Con 1200 CPR y ruedas de 32mm de diámetro:

```
Distancia por count = π × 32mm / 1200 = 0.0838 mm/count
```

Eso es **0.084mm de resolución** — 12× mejor que LEGO (1.0mm/count). Podés medir desplazamientos de menos de 0.1mm.

### DriveBase virtual (equivalente a Pybricks)

```cpp
class DriveBase {
    float wheel_diameter;  // mm
    float axle_track;      // mm (distancia entre ruedas)
    float mm_per_count;    // precalculado
    
    void straight(float distance_mm, float speed_mmps) {
        float target_counts = distance_mm / mm_per_count;
        // Ramp up, cruise, ramp down profile
        // Con PID de posición sobre los encoders
    }
    
    void turn(float angle_deg, float rate_dps) {
        float arc_mm = (angle_deg / 360.0) * PI * axle_track;
        // Motor izq y der giran en sentidos opuestos
    }
    
    void curve(float radius_mm, float angle_deg, float speed_mmps) {
        // Velocidad diferencial calculada
        float v_outer = speed_mmps * (radius_mm + axle_track/2) / radius_mm;
        float v_inner = speed_mmps * (radius_mm - axle_track/2) / radius_mm;
    }
};
```

---

## 3. Dynamixel XL330 — Integración profunda

### ¿Por qué Dynamixel y no servos comunes?

| Característica | Servo RC (MG90S) | **Dynamixel XL330** |
|---------------|------------------|---------------------|
| Control | PWM (posición sola) | **Posición + velocidad + corriente** |
| Feedback | Ninguno | **Posición actual, velocidad, carga, temperatura, voltaje** |
| Resolución | ~1° (típico) | **0.088° (4096 pasos/vuelta)** |
| Comunicación | PWM analógica | **TTL half-duplex digital, 1Mbps** |
| Encadenamiento | 1 cable PWM por servo | **Daisy-chain: 1 cable para todos** |
| Detección de contacto | Imposible | **Sí: monitorear corriente en tiempo real** |
| Precio | ~$5 | ~$24 |

### Protocolo Dynamixel 2.0

Los Dynamixel usan un protocolo binario sobre UART half-duplex TTL. El ESP32-S3 se conecta con un solo GPIO (via circuito de direction control con tri-state buffer).

```
ESP32 GPIO11 (UART TX) ──┬── 74HC126 buffer ──▶ DXL Data Bus
                          │
ESP32 GPIO12 (DIR) ──────┤── Controla dirección TX/RX
                          │
ESP32 GPIO11 (UART RX) ──┘── Recibe via resistor pull-up
```

### Circuito half-duplex simplificado

```
          3.3V
           │
          10kΩ
           │
GPIO11 ────┼──── DXL DATA (pin 2 del conector)
           │
          [DIR control via GPIO12]
```

En la práctica, la forma más simple es usar el modo half-duplex nativo del UART del ESP32-S3 (soportado en ESP-IDF):

```cpp
uart_config_t uart_config = {
    .baud_rate = 1000000,  // 1Mbps
    .data_bits = UART_DATA_8_BITS,
    .parity = UART_PARITY_DISABLE,
    .stop_bits = UART_STOP_BITS_1,
    .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
};
uart_driver_install(UART_NUM_1, 256, 256, 0, NULL, 0);
uart_param_config(UART_NUM_1, &uart_config);
uart_set_pin(UART_NUM_1, DXL_PIN, DXL_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
uart_set_mode(UART_NUM_1, UART_MODE_RS485_HALF_DUPLEX);
```

### Modos de operación para WRO

**Garra (ID 1): Current-based Position Control (modo 5)**

La garra se cierra hasta una posición objetivo, pero con un **límite de corriente**. Si la corriente sube (el objeto resiste), el servo se detiene. Esto da un agarre adaptativo: agarra objetos de diferentes tamaños sin aplastarlos.

```cpp
// Configurar modo 5: Current-based Position Control
dxl_write_byte(ID_GARRA, 11, 5);  // Operating Mode = 5

// Posición objetivo: cerrado
dxl_write_dword(ID_GARRA, 116, 2048);  // Goal Position (mitad de rango)

// Límite de corriente: 200mA (ajustar según objeto)
dxl_write_word(ID_GARRA, 102, 200);  // Goal Current

// Leer corriente actual para detectar contacto
int16_t current = dxl_read_word(ID_GARRA, 126);  // Present Current
if (abs(current) > 150) {
    // El objeto está en la garra
    objeto_agarrado = true;
}
```

**Brazo (ID 2): Position Control (modo 3)**

El brazo sube y baja a posiciones precisas. La reducción interna del XL330 (288:1) da torque suficiente para levantar cualquier objeto WRO.

```cpp
// 3 posiciones del brazo
#define BRAZO_ABAJO     1024   // 90° (0.088° × 1024)
#define BRAZO_TRANSPORTE 2048  // 180°
#define BRAZO_ALTO       3072  // 270°

// Velocidad de depósito (LENTO para vertical)
dxl_write_dword(ID_BRAZO, 112, 50);  // Profile Velocity = 50 (~17 RPM)
dxl_write_dword(ID_BRAZO, 116, BRAZO_ABAJO);  // Goal Position
```

**Pala/barredor (ID 3): Velocity Control (modo 1)**

La pala barre a velocidad constante cuando está activada.

### Detección de contacto para apilado de torres

El secreto del puntaje perfecto en las torres amarillas:

```cpp
void apilar_torre() {
    // 1. Posicionar robot frente a la base (odometría + VL53L1X)
    navegar_a_base_torre();
    
    // 2. Brazo sube el techo a posición alta
    brazo_mover(BRAZO_ALTO);
    
    // 3. Brazo baja LENTO
    dxl_write_dword(ID_BRAZO, 112, 20);  // Muy lento
    dxl_write_dword(ID_BRAZO, 116, BRAZO_ABAJO);
    
    // 4. Monitorear corriente mientras baja
    while (brazo_en_movimiento()) {
        int16_t current = dxl_read_word(ID_BRAZO, 126);
        if (abs(current) > UMBRAL_CONTACTO) {
            // ¡El techo tocó la base!
            brazo_parar();
            break;
        }
    }
    
    // 5. Abrir garra LENTO
    dxl_write_dword(ID_GARRA, 112, 30);  // Profile Velocity lento
    dxl_write_dword(ID_GARRA, 116, GARRA_ABIERTA);
    
    // 6. Retroceder sin tocar
    drivebase.straight(-20, 50);  // 20mm atrás, lento
}
```

La **detección de corriente** del Dynamixel es lo que hace posible saber exactamente cuándo el techo toca la base, sin sensor extra. Ningún servo RC puede hacer esto.

---

## 4. Sensor fusion pipeline

### Navegación: odometría + gyro + ToF

```
┌──────────────┐     ┌───────────┐     ┌──────────────┐
│  Encoders    │────▶│  Odometría │────▶│              │
│  1200 CPR×2  │     │  Δx, Δy, Δθ│    │  Estimador   │
└──────────────┘     └───────────┘    │  de posición  │
                                       │  (x, y, θ)    │
┌──────────────┐     ┌───────────┐    │              │
│  BNO055      │────▶│  Heading   │───▶│  Fusión:     │
│  9-axis IMU  │     │  absoluto  │    │  θ = 0.1×odo │
└──────────────┘     └───────────┘    │  + 0.9×gyro  │
                                       │              │
┌──────────────┐     ┌───────────┐    │              │
│  VL53L1X     │────▶│  Distancia │───▶│  Corrección  │
│  frontal     │     │  a pared   │    │  cuando hay  │
└──────────────┘     └───────────┘    │  referencia  │
                                       └──────────────┘
```

### Regla de fusión para heading

El heading del BNO055 es más confiable que la odometría para ángulos, pero la odometría es mejor para desplazamientos lineales:

```cpp
// Fusión complementaria
float heading_fused = 0.1 * heading_odometria + 0.9 * heading_bno055;
float x_fused = x_odometria;  // La odometría gana en x,y
float y_fused = y_odometria;

// Corrección con ToF cuando hay pared de referencia
if (tof_front.distance_mm() < 300 && near_wall) {
    float error_x = tof_front.distance_mm() - expected_distance;
    x_fused += 0.5 * error_x;  // Corrección parcial
}
```

---

## 5. Diseño del chasis 3D

### Filosofía: diseñar PARA los motores y sensores, no adaptar

```
Vista superior del chasis (80×90mm):

         ┌─ Garra (DXL330 #1) ──────────┐
         │                                │
    ┌────┤  [VL53L1X frontal]            │
    │    │  [TCS34725 en brazo]          │
    │    │                                │
    │    │  ┌───────PCB────────┐          │
    │    │  │ ESP32-S3         │          │
    │    │  │ DRV8833×2        │          │
    │    │  │ BNO055 (centro)  │          │
    │    │  └──────────────────┘          │
    │    │                                │
    │    │  [Motor izq]────⊙────[Motor der]
    │    │      Pololu 100:1 HPCB        │
    │    │                                │
    │    │  ────◎──── rueda loca          │
    │    │                                │
    │    └── [Pala/barredor DXL330 #3] ──┘
    │
    └── [Brazo DXL330 #2 (lateral)]
        [VL53L1X lateral]
```

### Especificaciones de impresión 3D

| Parte | Material | Relleno | Resolución | Pared |
|-------|----------|---------|------------|-------|
| Chasis base | PLA+ | 40% gyroid | 0.2mm | 3 capas (1.2mm) |
| Soporte motores | PETG | 60% | 0.15mm | 4 capas |
| Garra dedos | TPU 95A | 30% | 0.2mm | 2 capas |
| Ruedas (llanta) | PLA+ | 100% | 0.1mm | — |
| Ruedas (banda) | TPU 70A | 100% | 0.2mm | — |
| Soporte sensores | PLA | 30% | 0.2mm | 2 capas |

### Insertos metálicos

Para montar motores y PCB sin que los tornillos arranquen el plástico:

- **M2 heat-set inserts** (4mm largo) para PCB y motores Pololu
- **M2.5 heat-set inserts** para Dynamixel (usan tornillos M2.5)
- Se insertan con cautín a 230°C en los agujeros del PLA

---

## 6. PCB custom — Especificación para JLCPCB

### Parámetros de fabricación

| Parámetro | Valor |
|-----------|-------|
| Tamaño | 80×80mm (cabe en 100×100 de JLCPCB económico) |
| Capas | 4 (señal/GND/power/señal) |
| Espesor | 1.6mm FR4 |
| Acabado | ENIG (para soldadura fine-pitch) |
| Máscara | Negro mate |
| Serigrafía | Blanca |
| Assembly | SMD un lado (JLCPCB SMT) |
| Cantidad | 5 unidades |
| **Costo estimado** | **~$25-35 con assembly** |

### Componentes críticos del BOM de la PCB

| Componente | Package | LCSC # (ejemplo) | Precio/u |
|------------|---------|-------------------|----------|
| ESP32-S3-WROOM-1 (N8R8) | Module | C2913202 | $3.50 |
| DRV8833PWPR | HTSSOP-16 | C50506 | $1.20 |
| BNO055 | LGA-28 | C190649 | $8.00 |
| TPS5430DDAR | SOIC-8 | C28009 | $1.50 |
| AMS1117-3.3 | SOT-223 | C6186 | $0.10 |
| Conector JST-SH 3-pin (DXL) | SMD | C265090 | $0.05 |
| Conector JST-SH 6-pin (encoder) | SMD | C265093 | $0.05 |
| USB-C (programación) | SMD | C168688 | $0.15 |
| WS2812B-2020 | 2×2mm | C2976072 | $0.08 |
| Buzzer pasivo | SMD 5mm | — | $0.20 |

### Nota sobre el BNO055 en la PCB

El BNO055 debe estar montado en el **centro geométrico** del robot, lejos de motores (interferencia magnética). Si no es posible, usar un breakout externo conectado por cable I2C de 5cm.

**Alternativa más simple:** No soldar el BNO055 en la PCB. Dejar un conector STEMMA-QT/Qwiic y usar un breakout Adafruit/DFRobot. Esto permite reemplazarlo si se daña y facilita el posicionamiento.

---

## 7. Gestión de energía

### Presupuesto de consumo

| Componente | Corriente típica | Corriente pico |
|------------|-----------------|----------------|
| ESP32-S3 (WiFi off) | 80mA | 240mA (WiFi TX) |
| Pololu 100:1 ×2 | 200mA (marcha) | 3200mA (stall×2) |
| DXL330 ×3 | 150mA (marcha) | 1200mA (stall×3) |
| BNO055 | 12mA | 15mA |
| VL53L1X ×2 | 40mA | 40mA |
| TCS34725 + LED | 20mA | 250mA (LED max) |
| OV2640 | 40mA | 50mA |
| **Total típico** | **~540mA** | **~5000mA (stall)** |

### Batería: LiPo 2S 7.4V 500mAh

- Corriente de descarga contínua: 20C × 500mA = 10A → soporta picos de stall
- Energía: 7.4V × 0.5Ah = 3.7Wh
- Consumo típico: 7.4V × 0.54A = 4.0W
- Autonomía: 3.7Wh / 4.0W = **55 minutos** → sobra para varias rondas de 2 min
- Peso: ~30g (vs ~150g batería SPIKE)

### Regulación

```
LiPo 7.4V ──▶ [TPS5430 Buck 5V/2A] ──▶ Dynamixel, DRV8833 VMOTOR
                    │
                    └──▶ [AMS1117 LDO 3.3V/1A] ──▶ ESP32-S3, sensores
```

**¿Por qué TPS5430 y no un LDO?** Con 7.4V→5V, un LDO disiparía (7.4-5)×2A = 4.8W en calor. El buck converter (TPS5430) tiene 93% de eficiencia → solo 0.35W de calor.

### Protecciones

- **Undervoltage cutoff:** Si V_batt < 6.4V (3.2V/celda), ESP32 detiene motores y enciende LED rojo
- **Overcurrent:** DRV8833 tiene current limiting integrado (1.5A/canal configurable con resistor RISENSE)
- **Reverse polarity:** Diodo Schottky en entrada de batería

---

## 8. Firmware: arquitectura de software

### Estructura de archivos (Arduino/PlatformIO)

```
firmware/
├── platformio.ini
├── src/
│   ├── main.cpp              ← Setup + task creation
│   ├── motor_control.h/cpp   ← PID, encoder, DRV8833
│   ├── drivebase.h/cpp       ← Navegación: straight, turn, curve
│   ├── dynamixel.h/cpp       ← Protocolo DXL 2.0, servo control
│   ├── sensors.h/cpp         ← BNO055, VL53L1X, TCS34725
│   ├── camera.h/cpp          ← OV2640, blob detection
│   ├── navigation.h/cpp      ← Sensor fusion, posición x,y,θ
│   ├── missions.h/cpp        ← Lógica de misiones WRO
│   ├── config.h              ← Todos los parámetros calibrables
│   └── wifi_debug.h/cpp      ← Web server debug (solo práctica)
└── lib/
    ├── DynamixelSDK/
    └── Adafruit_BNO055/
```

### Task model FreeRTOS (dual-core)

```cpp
void setup() {
    // Core 0: Motor control (tiempo real, prioridad máxima)
    xTaskCreatePinnedToCore(
        motorControlTask, "MotorCtrl", 4096, NULL, 
        configMAX_PRIORITIES - 1, NULL, 0  // Core 0
    );
    
    // Core 1: Misión (lógica, sensores, cámara)
    xTaskCreatePinnedToCore(
        missionTask, "Mission", 8192, NULL,
        5, NULL, 1  // Core 1
    );
    
    // Core 1: Sensor fusion (50Hz)
    xTaskCreatePinnedToCore(
        sensorFusionTask, "SensFusion", 4096, NULL,
        4, NULL, 1  // Core 1
    );
}
```

### Máquina de estados de misión

```cpp
enum MissionState {
    INIT,
    WAIT_START,
    MISSION_VISITORS,
    MISSION_RED_TOWERS,
    MISSION_YELLOW_TOWERS,
    MISSION_SWEEP_DIRT,
    MISSION_SCAN_ARTEFACTS,
    MISSION_DELIVER_ARTEFACTS,
    SAFE_RETURN,
    DONE
};

void missionTask(void *pvParameters) {
    MissionState state = INIT;
    StopWatch chrono;
    
    while (true) {
        switch (state) {
            case INIT:
                initSensors();
                calibrateGyro();
                state = WAIT_START;
                break;
                
            case WAIT_START:
                if (buttonPressed(BTN_START)) {
                    chrono.reset();
                    state = MISSION_VISITORS;
                }
                break;
                
            case MISSION_VISITORS:
                if (chrono.elapsed_ms() > 100000) { state = SAFE_RETURN; break; }
                executeVisitorMission();
                state = MISSION_RED_TOWERS;
                break;
            
            // ... cada misión con timeout
            
            case SAFE_RETURN:
                navigateToSafeZone();
                state = DONE;
                break;
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

### WiFi debug dashboard (solo práctica)

```cpp
// En práctica: web server en el robot
// http://192.168.4.1 (AP mode)
// Muestra: posición x,y,θ, velocidades, sensores, cámara
// Permite: cambiar parámetros PID, umbrales de color, waypoints
// Desactivar en competencia con: #ifdef DEBUG_MODE
```

---

## 9. Cronograma de desarrollo

| Semana | Hito | Entregable |
|--------|------|-----------|
| 1-2 | Diseño PCB en KiCad | Gerbers listos para JLCPCB |
| 2-3 | Envío PCB + espera fabricación | Mientras: diseño chasis 3D |
| 3-4 | PCB llega, soldar, probar alimentación | PCB funcional, ESP32 programa |
| 4-5 | Motor control: PID, encoders, DRV8833 | Robot se mueve recto y gira preciso |
| 5-6 | Integración Dynamixel: garra + brazo | Garra agarra y suelta, brazo 3 posiciones |
| 6-7 | Sensores: BNO055 + VL53L1X + TCS34725 | Navegación con fusion, lectura color |
| 7-8 | Chasis definitivo + mecanismos WRO | Robot completo mecánicamente |
| 8-9 | Calibración odometría + mapeo tapete | Robot navega a coordenadas del tapete |
| 9-10 | Programar misiones individuales | Cada misión funciona aislada |
| 10-11 | Integrar misiones + pruebas de estrés | Programa completo, 50+ ejecuciones |
| 11-12 | Optimización de tiempos + robustez | Robot listo para competencia |
| 12-14 | Competencia simulada + ajustes finales | Formato 3 rondas, randomizaciones |

**Total: 12-14 semanas.** Es el doble que LEGO (6-8 semanas) pero el resultado es un robot significativamente superior.

---

## 10. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|-----------|
| PCB con error de diseño | Media | Alto (2-3 semanas delay) | Revisión doble en KiCad, usar DRC, mandar 2do lote rápido |
| Motor Pololu quemado (stall) | Baja | Medio | DRV8833 tiene current limit integrado; limitar PWM a 80% |
| Dynamixel no responde | Baja | Alto | Tener spare; verificar voltaje (5V estable) |
| BNO055 interferencia magnética de motores | Media | Medio | Montar BNO055 lejos de motores (≥3cm), calibrar mag in-situ |
| Firmware bug en competencia | Media | Muy alto | Pruebas exhaustivas, fallback: cada misión independiente |
| Chasis 3D se rompe | Baja | Alto | PETG para partes estructurales, llevar chasis de repuesto impreso |
| Batería insuficiente | Muy baja | Alto | 500mAh da 55min, sobra por lejos |
| Conflicto I2C (direcciones) | Media | Bajo | Secuencia de init con XSHUT para VL53L1X |
| WiFi no se apaga para ronda | Baja | Descalificación | `WiFi.mode(WIFI_OFF)` en competencia; verificar antes de cada ronda |

### Plan B: si la PCB falla

Si la PCB custom no llega a tiempo o tiene errores, usar **ESP32-S3-DevKitC** (~$15) + **breadboard/perfboard** con los mismos componentes. Más grande, menos prolijo, pero funcional. El firmware es el mismo.

### Plan C: fallback a Nivel 2

Si el robot custom no es confiable para la competencia, el equipo vuelve a SPIKE Prime + LMS-ESP32 (Nivel 2). Por eso es clave tener el Nivel 2 funcionando en paralelo como backup.

---

## 11. Dónde comprar (accesible desde Argentina)

| Componente | Proveedor | Envío a AR |
|------------|-----------|-----------|
| ESP32-S3-DevKitC | AliExpress / MercadoLibre | 15-30 días / inmediato |
| Pololu N20 motors | Pololu.com (envío internacional) | 15-20 días |
| Dynamixel XL330 | Robotis.com / RobotShop | 15-25 días |
| BNO055 breakout | Adafruit / AliExpress | 15-30 días |
| VL53L1X breakout | AliExpress / Pololu | 15-30 días |
| TCS34725 breakout | AliExpress / Adafruit | 15-30 días |
| DRV8833 breakout | Pololu / AliExpress | 15-30 días |
| PCB fabricación | JLCPCB.com | 10-15 días (DHL) |
| LiPo 2S 500mAh | Tiendas drone/hobby locales | Inmediato |
| Filamento PLA/TPU | MercadoLibre AR | Inmediato |

**Tip:** Pedir todo junto en el primer pedido para aprovechar envío. El lead time total desde pedido hasta tener todo es ~3-4 semanas.
