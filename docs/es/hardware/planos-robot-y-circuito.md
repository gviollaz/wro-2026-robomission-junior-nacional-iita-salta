# Planos del Robot y Circuito Eléctrico — IITA WRO Bot v1

## Vista general

Este documento describe los planos mecánicos y el esquemático eléctrico completo del robot Nivel 3+ para WRO Junior 2026.

Los diagramas interactivos están disponibles en la conversación de Claude donde fueron generados. Acá se documenta la información técnica de referencia.

---

## 1. Plano mecánico — Dimensiones

### Vista superior (80×90mm)

```
         ┌───────── GARRA DXL #1 + TCS34725 ──────────┐
         │              [OV2640 cam]                     │
┌────────┤──────────────────────────────────────────────├────────┐
│ ToF    │         PCB superior 80×80mm                 │        │
│ 5CX    │         ESP32-S3 + sensores                  │        │
│ front  │─────────────────────────────────────────────│        │
│        │         PCB inferior 80×80mm                 │        │
│ BRAZO  │         Teensy 4.1 + DRV8833                │        │
│ DXL #2 │─ ─ ─ [BNO055 centro] ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │        │
│        │                                              │        │
│        │  ⊙ Rueda L    [LiPo 2S]      Rueda R ⊙     │        │
│        │  Pololu 30:1   800mAh         Pololu 30:1   │        │
│        │  32mm                          32mm          │        │
│        │                                              │        │
│        │  ■ ■ ■ ■ ■ ■ ■  ← 7× VEML6040 color array │        │
│        │                                              │        │
│        │           ◎ Ball caster        [PALA DXL #3]│ ToF    │
│        │                                              │ 5CX   │
└────────┴──────────────────────────────────────────────┴─back──┘
```

### Vista lateral (corte)

```
                  ┌── Garra DXL #1 + TCS34725
                  │
     ┌── Brazo ───┘
     │  DXL #2
     │
┌────┤─────────────────────────────────────────┐
│    │  PCB superior (ESP32-S3, cam, sensores) │  ← 12mm standoffs
│    │─────────────────────────────────────────│
│    │  PCB inferior (Teensy, DRV8833, power)  │
│    │      [BNO055]    [LiPo entre ruedas]    │
└────┤──⊙─────────────────────────────────⊙──┤
     │ Rueda L  ■■■■■■■ (color array)  Rueda R│
     └──────────────◎ caster───────────────────┘
                    ═══════════ Piso

Altura plegado: 58mm
Altura con brazo arriba: ~140mm
Peso total: ~291g
```

---

## 2. Esquemático eléctrico — Resumen

### Distribución de energía

```
LiPo 2S 7.4V 800mAh 45C
     │
     ├──► [TPS5430 Buck] ──► 5V / 2A
     │         │
     │         ├──► DRV8833 Vm (motores tracción)
     │         ├──► Dynamixel XL330 ×3 Vcc
     │         ├──► TCS34725 LED
     │         │
     │         └──► [AMS1117 LDO] ──► 3.3V / 1A
     │                    │
     │                    ├──► Teensy 4.1
     │                    ├──► ESP32-S3
     │                    ├──► BNO055
     │                    ├──► VL53L5CX ×2
     │                    ├──► TCA9548A + VEML6040 ×7
     │                    └──► OV2640
     │
     └──► [10kΩ/4.7kΩ divider] ──► ADC GPIO 48 (Vbatt monitor)
```

### Conexiones Teensy 4.1 (Motor Brain)

| GPIO | Señal | Destino |
|------|-------|---------|
| 2 | PWM (LEDC ch0) | DRV8833 AIN1 (Motor L fwd) |
| 3 | PWM (LEDC ch1) | DRV8833 AIN2 (Motor L rev) |
| 4 | PWM (LEDC ch2) | DRV8833 BIN1 (Motor R fwd) |
| 5 | PWM (LEDC ch3) | DRV8833 BIN2 (Motor R rev) |
| 7 | QuadTimer | Encoder L canal A |
| 8 | QuadTimer | Encoder L canal B |
| 9 | QuadTimer | Encoder R canal A |
| 10 | QuadTimer | Encoder R canal B |
| 0 (Serial1 TX) | UART 1Mbps | Dynamixel TTL bus (half-duplex) |
| 1 (Serial1 RX) | UART 1Mbps | Dynamixel TTL bus |
| 24 | GPIO output | Dynamixel DIR control |
| 34 (Serial5 TX) | UART 1Mbps | ESP32-S3 RX (inter-MCU) |
| 35 (Serial5 RX) | UART 1Mbps | ESP32-S3 TX (inter-MCU) |
| 46 | Digital input | DRV8833 nFAULT |

### Conexiones ESP32-S3 (Sensor Brain)

| GPIO | Señal | Destino |
|------|-------|---------|
| 13 | I2C SDA | Bus I2C principal (400kHz) |
| 14 | I2C SCL | Bus I2C principal |
| 17-24 | DVP D0-D7 | OV2640 datos paralelo |
| 38 | DVP PCLK | OV2640 pixel clock |
| 39 | DVP VSYNC | OV2640 vertical sync |
| 40 | DVP HREF | OV2640 horizontal ref |
| 41 | XCLK out (20MHz) | OV2640 master clock |
| 15 | I2C SDA (cam) | OV2640 SCCB config |
| 16 | I2C SCL (cam) | OV2640 SCCB config |
| 42 | PWM | Buzzer pasivo |
| 43 | Digital | WS2812B NeoPixel |
| 44 | Input pull-up | Botón START |
| 45 | Input pull-up | Botón SELECT |
| 48 | ADC | Vbatt monitor (divisor 10k/4.7k) |
| 11 | UART RX | Teensy TX (inter-MCU) |
| 12 | UART TX | Teensy RX (inter-MCU) |

### Bus I2C — Dispositivos y direcciones

| Dispositivo | Dirección | Bus |
|-------------|----------|-----|
| BNO055 | 0x28 | Principal |
| VL53L5CX #1 (frontal) | 0x30 (re-addressed) | Principal |
| VL53L5CX #2 (trasero) | 0x31 (re-addressed) | Principal |
| TCA9548A (multiplexor) | 0x70 | Principal |
| VEML6040 #1-#7 | 0x10 (todos) | Canales 0-6 del TCA9548A |
| TCS34725 (en brazo) | 0x29 | Canal 7 del TCA9548A |

### Secuencia de inicio I2C

1. Mantener XSHUT de VL53L5CX #2 en LOW (GPIO del ESP32)
2. Inicializar VL53L5CX #1 en 0x29, re-address a 0x30
3. Liberar XSHUT de VL53L5CX #2
4. Inicializar VL53L5CX #2 en 0x29, re-address a 0x31
5. Inicializar BNO055 en 0x28
6. Inicializar TCA9548A en 0x70
7. Por cada canal 0-6: seleccionar canal → inicializar VEML6040
8. Canal 7: inicializar TCS34725

### Dynamixel TTL bus

```
Teensy UART1 (half-duplex)
     │
     └──► [74HC126 tri-state buffer o directo con DIR pin]
              │
              └──► DXL #1 (ID=1, Garra) ──► DXL #2 (ID=2, Brazo) ──► DXL #3 (ID=3, Pala)
                   Daisy-chain: un solo cable de datos para los 3 servos
                   VCC = 5V, GND compartido
```

---

## 3. Notas de diseño de PCB

### PCB inferior (Motor Brain) — 80×80mm, 4 capas

- Capa 1 (top): Teensy 4.1 module + DRV8833 + conectores motores/encoders
- Capa 2 (inner): GND plane (crítico para retorno de corriente de motores)
- Capa 3 (inner): 5V power plane
- Capa 4 (bottom): Conector batería XT30 + TPS5430 + AMS1117 + capacitores

### PCB superior (Sensor Brain) — 80×80mm, 4 capas

- Capa 1 (top): ESP32-S3-WROOM + OV2640 connector + botones + LEDs
- Capa 2 (inner): GND plane
- Capa 3 (inner): 3.3V plane
- Capa 4 (bottom): 7× VEML6040 (mirando al piso) + TCA9548A + BNO055 + conectores I2C

### Montaje entre PCBs

4× standoffs M2 aluminio de 12mm en las esquinas. Las PCBs se conectan por:
- Cable flat 4-pin: UART inter-MCU (TX, RX, 3.3V, GND)
- Cable flat 2-pin: 5V + GND (power distribution)
- Conector I2C 4-pin si BNO055 está en PCB inferior
