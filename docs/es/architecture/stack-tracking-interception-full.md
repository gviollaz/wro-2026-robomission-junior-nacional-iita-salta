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

---

## 6. Catálogo de skills

### 6.1 `omni3-kinematics` (base, sin dependencias)

- **Inputs:** `(vx_r, vy_r, omega)` en m/s y rad/s.
- **Outputs:** `(w1, w2, w3)` en rad/s de cada rueda.
- **Matemática:** matriz 3×3 cerrada para ruedas a 0°, 120°, 240°, radio del robot `L`.
- **Inversa (odometría):** dadas `(w1,w2,w3)` medidas por encoders, devolver `(vx_r, vy_r, omega)`.
- **Tests:** unitarios con casos conocidos (avanzar puro, strafe puro, rotación pura).

### 6.2 `ball-tracking-kalman` (depende de: protocolo UART)

- **Modelo:** estado `[x, y, vx, vy]` en robot frame, transición velocidad-constante.
- **Inputs:** medición `(x_meas, y_meas)` + flag `ball_seen` + `dt`.
- **Outputs:** estado filtrado + covarianza + flag de confianza.
- **Manejo de oclusiones:** si `ball_seen == false`, solo `predict()` (coast), covarianza crece.
- **Outlier rejection:** Mahalanobis > umbral → descartar medición.
- **Matrices 4×4 precalculadas** para no hacer álgebra general.

### 6.3 `ball-prediction` (depende de: kalman)

- **Input:** estado Kalman actual + horizonte `t_future`.
- **Output:** `(x_pred, y_pred)` en robot frame + elipse 2σ de incertidumbre.
- **Modelo de fricción:** `v(t) = v0 · exp(-k · t)`, `k` calibrado empírico.
- **Integración analítica:** posición futura tiene forma cerrada, no hay que integrar numéricamente.

### 6.4 `interception-planner` (depende de: prediction, localization)

- **Problema:** encontrar `t*` tal que el robot (moviendo a `v_max`) y la pelota se
  encuentren en el mismo punto.
- **Método:** búsqueda binaria en `t ∈ [0, t_max]` evaluando
  `distancia(robot, ball_pred(t)) < v_max · t`.
- **Output:** punto de intercepción `(x*, y*)` y tiempo estimado `t*`.
- **Fallback:** si no hay solución (pelota muy rápida), apuntar a la trayectoria
  futura más cercana alcanzable.

### 6.5 `dwa-lite` (depende de: interception-planner)

- **Dynamic Window:** ventana de comandos alcanzables desde velocidad actual en un `dt`.
- **Muestreo:** grilla de 5×5×3 = 75 candidatos `(vx, vy, ω)` — reducir a 30 si CPU aprieta.
- **Cost function:** `α · dist_a_target + β · clearance_obstaculos + γ · suavidad`.
- **Output:** mejor comando `(vx, vy, ω)` que pasa a cinemática inversa.
- **Simplificación vs DWA clásico:** no simulamos trayectorias completas, solo evaluamos
  el estado resultante en `dt` — suficiente para pelota + intercepción.

### 6.6 `robot-localization` (depende de: BNO055 + encoders + kinematics inversa)

- **Estado:** `(x_w, y_w, theta_w)` en world frame.
- **Heading:** lectura directa del BNO055 (fusionado por el chip), con offset inicial.
- **Posición:** integración de `(vx_r, vy_r)` (de odometría) rotados al world frame por θ.
- **Drift:** acepta drift lento en (x,y) — el juego es en coordenadas relativas al robot
  la mayor parte del tiempo, la posición absoluta es secundaria.

### 6.7 Orden de implementación recomendado

```
1. omni3-kinematics     ─┐
2. robot-localization   ─┴─▶ permiten mover el robot manualmente y trackear pose
3. ball-tracking-kalman ─┐
4. ball-prediction      ─┴─▶ permiten visualizar pelota en telemetría sin control
5. interception-planner ─┐
6. dwa-lite             ─┴─▶ cierran el loop de control completo
```

---

## 7. Calibración empírica

Cinco mediciones indispensables antes de que el stack funcione bien:

| # | Parámetro                          | Método                                              |
|---|------------------------------------|-----------------------------------------------------|
| 1 | Radio efectivo de rueda            | Avanzar 1 m medido, contar ticks de encoder         |
| 2 | Radio del robot `L` (centro→rueda) | Regla, verificar con test de rotación pura          |
| 3 | Fricción pelota `k`                | Rodar pelota 5× distancias conocidas, ajustar exp   |
| 4 | Conversión píxel→metros OpenMV     | Pelota a distancias conocidas, fitear modelo        |
| 5 | Offset cámara-centro robot         | Pelota en centro robot, leer coords OpenMV          |
| 6 | Latencia total percepción→acción   | Flash LED sincronizado con evento de pelota         |
| 7 | `v_max` real del robot             | Comandar máximo, medir con cronómetro + distancia   |

Todos estos valores van a `config.h` como constantes, **nunca hardcodeados en skills**.

---

## 8. Plan de testing incremental

Cada skill se valida **sin depender** de las siguientes:

1. **`omni3-kinematics`:** tests unitarios en ESP32 sin motores (prints por serial).
2. **`robot-localization`:** empujar robot a mano por trayectoria conocida, verificar drift.
3. **`ball-tracking-kalman`:** grabar log de OpenMV en SD, reproducir offline en Python
   con las mismas matrices, comparar resultados.
4. **`ball-prediction`:** soltar pelota con velocidad conocida, verificar que predicción
   a 500 ms coincide con posición real medida.
5. **`interception-planner`:** simulación Python antes de ESP32, casos límite
   (pelota quieta, pelota hacia el robot, pelota perpendicular).
6. **`dwa-lite`:** test en cancha con pelota estática, verificar que el robot llega
   al target sin oscilaciones.
7. **Integración:** pelota rodando lenta → rápida, medir tasa de intercepciones exitosas
   sobre 20 intentos.

**Criterio de éxito mínimo:** 70% de intercepciones con pelota a 0.5 m/s a 1 m de distancia.

---

## 9. Referencias a ligas mayores

### 9.1 Adaptado de RoboCup SSL / Small Size League

- **Kalman 2D velocidad-constante** para tracking de pelota — estándar en SSL, trivial
  de portar a ESP32.
- **DWA** como controlador local — se usa en múltiples equipos SSL para navegación
  reactiva, versión recortada cabe en MCU.
- **Separación percepción/control en threads distintos** — arquitectura clásica ROS
  adaptada a FreeRTOS dual-core.

### 9.2 Descartado por costo computacional

- **MPC (Model Predictive Control):** requiere solver QR online, no entra en ESP32
  con los tiempos que necesitamos.
- **RRT* / A* sobre grilla:** innecesario para un campo pequeño con obstáculos dinámicos
  pocos; DWA alcanza.
- **Redes neuronales de tracking:** la OpenMV ya hace detección por color, no hace falta
  CNN en el ESP32.
- **Visión global cenital:** infraestructura que no tenemos ni vamos a tener en WRO
  RoboSport — todo debe ser a bordo.

### 9.3 Diferencias conceptuales clave vs ligas mayores

| Aspecto            | SSL/MSL                    | Nuestro stack               |
|--------------------|----------------------------|-----------------------------|
| Cámara             | Cenital externa            | A bordo (OpenMV)            |
| Frame primario     | Mundo (cancha completa)    | Robot (local)               |
| Compute            | PC externa + WiFi          | ESP32 a bordo               |
| Coordinación       | Multi-robot                | Single-robot                |
| Latencia objetivo  | ~30 ms                     | ~20 ms                      |

---

## Próximos pasos

1. Revisar y aprobar este documento.
2. Crear skeleton de cada skill en `software/skills/<nombre>/` con header obligatorio.
3. Implementar en el orden de 6.7.
4. Ir llenando `config.h` con valores de calibración conforme se midan.

*Fin del documento.*
