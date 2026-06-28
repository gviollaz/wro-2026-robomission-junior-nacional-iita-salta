---
// Autor:       Gustavo Viollaz
// Herramienta: Claude Opus 4.6
// Fecha:       2026-04-10
// Rev:         v1 (secciones 1-5)
---

# Stack de Tracking e Interceptación — WRO RoboSport 2026

Arquitectura del pipeline de percepción, predicción y control para el robot
omnidireccional de 3 ruedas con ESP32 + OpenMV + BNO055.

---

## 1. Visión general

### 1.1 Hardware asumido

- **MCU principal:** ESP32 dual-core 240 MHz, ~320 KB RAM libre.
- **Visión:** OpenMV H7/RT1062 detectando blob de pelota, salida por UART.
- **IMU:** BNO055 por I2C (heading absoluto fusionado, no necesitamos filtro propio).
- **Locomoción:** 3 ruedas omni a 120°, motores DC con encoders en cuadratura.
- **Alimentación:** LiPo, regulada a 5V/3.3V según etapa.

### 1.2 Diagrama de bloques

```
 ┌──────────┐  UART   ┌──────────────────────── ESP32 ─────────────────────────┐
 │ OpenMV   │────────▶│  Core 0 (percepción)      │  Core 1 (control)         │
 │ blob det │ 100 Hz  │  ┌─────────────────────┐  │  ┌─────────────────────┐  │
 └──────────┘         │  │ uart_parser         │  │  │ interception_planner│  │
                      │  │ ball_kalman (2D CV) │──┼─▶│ dwa_lite            │  │
 ┌──────────┐  I2C    │  │ ball_predictor      │  │  │ omni3_inverse_kin   │  │
 │ BNO055   │────────▶│  │ robot_localization  │──┼─▶│ motor_pwm (LEDC)    │  │
 └──────────┘ 100 Hz  │  └─────────────────────┘  │  └─────────────────────┘  │
                      │            ▲              │            │              │
 ┌──────────┐         │            │              │            ▼              │
 │ Encoders │────────▶│         odometry          │      3× DRV8833 / TB6612  │
 └──────────┘ ISR     └───────────────────────────┴──────────────┬────────────┘
                                                                  │
                                                                  ▼
                                                          3× motor DC omni
```

### 1.3 Frecuencias objetivo

| Loop                      | Core | Frecuencia | Periodo | Criticidad |
|---------------------------|------|------------|---------|------------|
| Parser UART OpenMV        | 0    | 100 Hz     | 10 ms   | Alta       |
| Kalman + predictor pelota | 0    | 100 Hz     | 10 ms   | Alta       |
| Lectura BNO055 + encoders | 0    | 100 Hz     | 10 ms   | Alta       |
| Interception + DWA        | 1    | 50 Hz      | 20 ms   | Alta       |
| Cinemática inversa + PWM  | 1    | 100 Hz     | 10 ms   | Crítica    |
| Telemetría / logging      | 0    | 10 Hz      | 100 ms  | Baja       |

Comunicación entre cores vía **FreeRTOS queues** (no variables globales).

---

## 2. Presupuesto de CPU / RAM

Estimaciones conservadoras medidas en clases similares ESP32 @240 MHz.

### 2.1 CPU por ciclo (Core 0 @ 10 ms)

| Módulo              | μs/ciclo | % del ciclo |
|---------------------|----------|-------------|
| Parser UART         | ~150     | 1.5%        |
| Kalman 2D CV (4×4)  | ~400     | 4.0%        |
| Predictor balístico | ~100     | 1.0%        |
| BNO055 I2C read     | ~800     | 8.0%        |
| Encoders + odom     | ~200     | 2.0%        |
| **Total Core 0**    | ~1650    | **16.5%**   |

Margen abundante para logging y jitter.

### 2.2 CPU por ciclo (Core 1 @ 20 ms)

| Módulo                    | μs/ciclo | % del ciclo |
|---------------------------|----------|-------------|
| Interception planner      | ~500     | 2.5%        |
| DWA-lite (30 candidatos)  | ~3500    | 17.5%       |
| Cinemática inversa omni   | ~80      | 0.4%        |
| PWM update (LEDC)         | ~50      | 0.3%        |
| **Total Core 1**          | ~4130    | **20.7%**   |

### 2.3 RAM

| Componente              | Bytes aprox |
|-------------------------|-------------|
| Kalman state + cov      | 200         |
| Historial pelota (ring) | 800         |
| DWA candidatos          | 1200        |
| Buffers UART            | 512         |
| Stacks FreeRTOS (2)     | 8192        |
| **Total**               | **~11 KB**  |

Holgadísimo frente a los ~320 KB disponibles.

---

## 3. Frames de referencia

Tres sistemas de coordenadas, explícitos en todo el código:

### 3.1 Robot frame (R)

- Origen: centro geométrico del robot.
- Eje **+X**: hacia adelante (frente del robot).
- Eje **+Y**: hacia la izquierda.
- Eje **+Z**: hacia arriba.
- Rotación **+θ**: antihoraria vista desde arriba.

Las 3 ruedas omni se numeran **W1, W2, W3** a 0°, 120°, 240° respecto de +X.

### 3.2 World frame (W)

- Origen: punto de inicio del robot al encender (o reset manual).
- Ejes alineados con el robot en t=0.
- Heading absoluto provisto por BNO055 (restando offset inicial).

### 3.3 Camera frame (C)

- Origen: lente de la OpenMV.
- Offset fijo respecto del robot frame: `(dx_cam, dy_cam, dz_cam)` — medir empíricamente.
- La OpenMV entrega coordenadas de pelota en píxeles; la conversión a metros
  en robot frame requiere calibración (ver sección 7, próximo turno).

### 3.4 Transformaciones

```
P_R = T_RC · P_C           (cámara → robot, matriz fija precalibrada)
P_W = T_WR(θ, x, y) · P_R  (robot → mundo, depende de pose actual)
```

**Regla de oro:** ningún módulo mezcla frames. Variables siempre sufijadas
`_r`, `_w`, `_c` (ej: `ball_x_r`, `robot_theta_w`).

---

## 4. Protocolo UART OpenMV ↔ ESP32

### 4.1 Parámetros físicos

- **Baudrate:** 115200 (alcanza holgado para 100 Hz).
- **Formato:** 8N1, sin control de flujo.
- **Pines ESP32:** UART2 (GPIO16 RX, GPIO17 TX) — UART0 queda para debug USB.

### 4.2 Formato de paquete (binario, 16 bytes)

```
Offset  Campo         Tipo     Descripción
------  ------------  -------  ------------------------------------
  0     HEADER        uint16   0xAA55 (magic)
  2     seq           uint8    secuencia 0-255 (detectar pérdidas)
  3     flags         uint8    bit0=ball_seen, bit1=multiple_blobs
  4     ball_x        int16    píxeles, centro imagen = 0
  6     ball_y        int16    píxeles, centro imagen = 0
  8     ball_radius   uint16   píxeles (para estimar distancia)
 10     confidence    uint8    0-255 (brillo/tamaño del blob)
 11     reserved      uint8    padding
 12     timestamp_ms  uint32   reloj OpenMV (ms desde boot)
 16     CRC16         uint16   CRC-16/CCITT sobre bytes 0-15
```

Total **18 bytes** con CRC. A 100 Hz = 1800 B/s, 2% del ancho de banda.

### 4.3 Manejo de errores

- CRC inválido → descartar paquete, incrementar contador de errores.
- Gap de `seq` → log, marcar discontinuidad al Kalman (aumenta covarianza).
- Sin paquete válido por > 100 ms → `ball_seen = false`, Kalman en modo *coast*
  (predice sin corregir durante máx 500 ms antes de dar pelota por perdida).

---

## 5. Pipeline de datos end-to-end

### 5.1 Flujo nominal (pelota visible)

```
1. OpenMV detecta blob pelota            [t0]
2. Empaqueta y envía por UART            [t0 + 2 ms]
3. ESP32 parser UART lee paquete         [t0 + 3 ms]
4. Convierte pixel → metros en frame R   [t0 + 3 ms]
5. Kalman predict (con dt desde última)  [t0 + 4 ms]
6. Kalman update con medición            [t0 + 4 ms]
7. Predictor extrapola pelota a t+Δ      [t0 + 5 ms]
8. Interception planner calcula target   [t0 + 15 ms, core 1]
9. DWA evalúa candidatos                 [t0 + 18 ms]
10. Cinemática inversa → (w1,w2,w3)      [t0 + 19 ms]
11. PWM a motores                        [t0 + 20 ms]
```

**Latencia total percepción → acción: ~20 ms** (objetivo). Medirla en testing.

### 5.2 Modos degradados

| Situación               | Comportamiento                                      |
|-------------------------|-----------------------------------------------------|
| Pelota perdida < 500ms  | Kalman coast, DWA sigue target predicho             |
| Pelota perdida > 500ms  | Modo búsqueda: rotar en el lugar escaneando         |
| UART sin datos > 200ms  | Detener motores, flag de error, seguir leyendo      |
| BNO055 falla I2C        | Fallback a heading por encoders (menos preciso)     |
| Batería baja (<20%)     | Reducir velocidad máxima 50%, log agresivo          |

---

*Continúa en turno 2: secciones 6-9 (catálogo de skills, calibración, testing, referencias a ligas mayores).*
