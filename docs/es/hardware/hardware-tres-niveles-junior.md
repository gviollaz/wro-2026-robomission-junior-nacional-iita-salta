# Tres Niveles de Hardware para WRO Junior 2026 — Del LEGO al Robot Custom

## Contexto: las reglas lo permiten todo

Desde 2025, WRO RoboMission permite **cualquier hardware**. Ya no es obligatorio usar LEGO. Se pueden usar motores, sensores, controladores, piezas 3D impresas, PCBs custom — todo. Las únicas restricciones son: 25×25×25cm, 1500g, máximo 5 motores (Junior), sin comunicación wireless entre componentes, y 1 controlador.

Este documento analiza 3 niveles de hardware, desde LEGO puro hasta un robot 100% custom, con recomendaciones específicas de componentes, costos, y trade-offs.

---

## NIVEL 1: LEGO SPIKE Prime puro

### Hardware

| Componente | Modelo | Precio aprox. |
|------------|--------|---------------|
| Controlador | SPIKE Prime Hub | Incluido en kit |
| Motores tracción (×2) | LEGO Medium Angular Motor | Incluidos |
| Motores mecanismo (×2-3) | LEGO Medium Angular Motor | Incluidos/extra ~$25 |
| Sensor color (×2) | LEGO Color Sensor | Incluidos |
| IMU/Gyro | Integrado en Hub | Incluido |
| Ruedas | LEGO 56mm o 62.4mm | Incluidas |
| Estructura | LEGO Technic beams, pins, axles | Incluidos |
| **Costo total** | | **~$350-400** (kit SPIKE Prime) |

### Ventajas

- Ecosistema integrado, todo funciona out-of-the-box
- Pybricks excelente para programar
- Soporte de la comunidad WRO enorme
- Los alumnos ya lo conocen
- Mantenimiento simple (piezas reemplazables)
- Giroscopio integrado en el hub (no hay cableado extra)

### Limitaciones

- **Motores**: backlash en los engranajes internos (~2-3°), velocidad máxima limitada (~1000°/s), resolución encoder 360 CPR
- **Giroscopio**: drift ~1-2°/min, no tiene magnetómetro, calibración lenta
- **Sensor de color**: campo de visión amplio (difícil leer objetos pequeños sin contaminación), solo HSV (no RGB raw accesible)
- **Estructura**: LEGO Technic tiene juego mecánico inherente en las conexiones pin-agujero (~0.1-0.2mm por unión, se acumula)
- **Ruedas**: goma blanda que comprime bajo carga, desgaste desigual
- **Alimentación**: batería LiPo integrada no reemplazable fácilmente

### Puntaje máximo realista: 200-220/230

Con LEGO puro, el apilado de torres amarillas (50 pts) es difícil pero posible si la construcción es excelente. El juego mecánico limita la precisión de posicionamiento a ±3-5mm, lo que está en el borde de lo necesario para apilar.

---

## NIVEL 2: SPIKE Prime + Mejoras Custom

### Filosofía: mantener el ecosistema SPIKE pero agregar componentes que resuelvan sus limitaciones específicas.

### Mejora 1: IMU externa BNO055 (reemplaza gyro del hub)

| Componente | Detalle | Precio |
|------------|---------|--------|
| BNO055 breakout (Adafruit/DFRobot) | 9-axis, fusión onboard, heading drift-free | ~$30 |
| Conexión | I2C via LMS-ESP32 → SPIKE | Via LMS-ESP32 |

**¿Por qué?** El BNO055 tiene fusión de datos onboard (gyro + acelerómetro + magnetómetro) que entrega heading con drift prácticamente cero. El gyro del SPIKE driftea 1-2° por minuto; el BNO055 con magnetómetro compensa automáticamente. Para 2 minutos de misión, esto puede ser la diferencia entre ±4° de error y ±0.5°.

**Nota WRO:** Requiere LMS-ESP32 como puente. Cuenta como "sensor" (sin límite en Junior).

### Mejora 2: Sensor ToF VL53L1X (distancia láser precisa)

| Componente | Detalle | Precio |
|------------|---------|--------|
| VL53L1X (STMicro) breakout | Time-of-Flight laser, 4m rango, ±3mm precisión | ~$15 |

**¿Por qué?** El sensor de distancia ultrasónico de LEGO tiene ±10mm de precisión y es grande. El VL53L1X es 10× más preciso (±3mm), más compacto, y tiene Field-of-View programable (esto permite apuntar a un objeto específico sin "ver" objetos laterales). Ideal para posicionarse exactamente frente a una torre antes de apilar.

### Mejora 3: Cámara via LMS-ESP32

| Componente | Detalle | Precio |
|------------|---------|--------|
| LMS-ESP32 v2 | Puente ESP32 con conector LEGO LPF2 | ~$40 |
| HuskyLens o OV2640 camera | Visión por cámara, detección de color/objetos | ~$15-55 |

**¿Por qué?** Detectar colores de artefactos a distancia (15-30cm) sin detenerse. Ahorra 10-15s en la misión de artefactos.

### Mejora 4: Piezas 3D impresas para mecanismos críticos

| Componente | Material | Precio |
|------------|----------|--------|
| Garra custom (dedos optimizados para objetos WRO) | PLA/PETG | ~$2 |
| Soporte sensor a medida | PLA | ~$1 |
| Ruedas con mejor grip (TPU borde) | TPU + PLA | ~$3 |
| Adaptadores LEGO→eje custom | PLA | ~$1 |

**¿Por qué?** La garra LEGO genérica no está optimizada para los objetos específicos de WRO 2026. Una garra diseñada específicamente para agarrar notas/torres/artefactos tiene tolerancias exactas y superficie de agarre óptima. Imprimirla en 3D cuesta centavos y la diferencia en fiabilidad es enorme.

### Mejora 5: Ruedas con mejor odometría

| Componente | Detalle | Precio |
|------------|---------|--------|
| Ruedas de silicona/poliuretano | O-rings de alta precisión sobre llanta LEGO | ~$5 |

**¿Por qué?** Las ruedas LEGO de goma se comprimen bajo peso y se desgastan desigualmente. Un O-ring de silicona de dureza 70A montado sobre una llanta LEGO tiene diámetro constante, no se deforma, y tiene excelente tracción.

### BOM (Bill of Materials) Nivel 2

| Componente | Precio |
|------------|--------|
| Kit SPIKE Prime base | $350 |
| LMS-ESP32 v2 | $40 |
| BNO055 breakout | $30 |
| VL53L1X breakout | $15 |
| HuskyLens | $55 |
| Filamento 3D (PLA+TPU) | $10 |
| Cables, conectores, misceláneos | $15 |
| **Total** | **~$515** |

### Puntaje máximo realista: 215-230/230

Las mejoras en IMU y sensor de distancia hacen que el posicionamiento sea mucho más preciso. Las piezas 3D custom permiten una garra optimizada para los objetos del juego. La cámara ahorra tiempo en detección de artefactos. El apilado de torres se vuelve consistente gracias a la precisión del BNO055 + VL53L1X.

---

## NIVEL 3: Hardware libre — El mejor robot posible

### Filosofía: diseñar cada componente para máximo rendimiento, sin compromisos de compatibilidad. PCB custom, motores industriales, sensores de gama alta, chasis impreso en 3D.

### Controlador

| Opción | Procesador | Precio | Ventaja |
|--------|-----------|--------|---------|
| **ESP32-S3 (recomendado)** | Xtensa LX7 240MHz dual-core | ~$8 | WiFi+BLE para debug, AI acceleration, enorme comunidad |
| Teensy 4.1 | ARM Cortex-M7 600MHz | ~$30 | El más rápido, USB host, mucha RAM |
| STM32H7 (Nucleo) | ARM Cortex-M7 480MHz | ~$25 | Industria estándar, HAL maduro |
| Raspberry Pi Pico 2 | RP2350 Cortex-M33 150MHz | ~$5 | Ultra barato, MicroPython nativo |

**Recomendación:** ESP32-S3 como controlador principal. WiFi para debugging en práctica (desactivar en ronda), dual-core para procesamiento paralelo (un core para control de motores, otro para lógica de misión), y AI acceleration para procesar imágenes de cámara localmente.

### Motores de tracción

| Opción | Tipo | Encoder | Torque | RPM | Precio (×2) | Ventaja |
|--------|------|---------|--------|-----|-------------|---------|
| **Pololu 50:1 HPCB 6V con encoder** | N20 metal gearbox | 12 CPR × 50 = 600 CPR | 1.5 kg·cm | 310 RPM | ~$30 | Mejor relación costo/rendimiento, engranajes de acero |
| Pololu 100:1 HP 6V con encoder | N20 metal gearbox | 12 CPR × 100 = 1200 CPR | 2.0 kg·cm | 150 RPM | ~$32 | Más torque, más resolución encoder |
| Maxon DCX 10L + GPX 10 | Swiss precision | 512 CPR | Configurable | Config. | ~$200+ | Precisión industrial, 0 backlash |
| Faulhaber 1024K006SR | German precision | 512 CPR | 0.64 mNm | 15000 RPM | ~$150+ | El Rolls-Royce de los micro motores |

**Recomendación:** Pololu 100:1 HPCB con encoder integrado. La resolución de 1200 CPR por revolución de rueda (vs 360 del LEGO) da 3× más precisión en odometría. Los engranajes de acero tienen menos backlash que LEGO. Costo accesible.

**Para presupuesto ilimitado:** Maxon DCX 10L con caja reductora GPX 10. Backlash <0.5°, vida útil de miles de horas, precisión de encoder incomparable. Pero cuestan 10× más.

### Motores de mecanismos

| Opción | Tipo | Precio | Ventaja |
|--------|------|--------|---------|
| **Dynamixel XL330-M288-T** | Servo smart, TTL, 0.52 Nm | ~$24 | Control de posición onboard, feedback de corriente, chainable |
| Dynamixel XL330-M077-T | Servo smart, TTL, rápido | ~$24 | Más rápido (383 RPM), menos torque |
| MG90S metal gear servo | Analog servo | ~$5 | Barato, simple |
| Geekservo 9g 360° | Servo contínuo | ~$4 | Compatible con LEGO |

**Recomendación:** Dynamixel XL330-M288-T. Son los servos más avanzados del mercado en este tamaño (20×34×26mm, solo 18g). Tienen control de posición, velocidad Y corriente onboard, feedback en tiempo real, y se conectan en cadena (un solo cable para múltiples servos). La detección de corriente permite saber si la garra agarró algo o está vacía. Para el apilado de torres, poder controlar la corriente del servo significa que podés bajar el techo con fuerza controlada — si la corriente sube (resistencia), sabés que tocaste la base.

### IMU/Giroscopio

| Opción | Ejes | Fusión onboard | Drift | Precio |
|--------|------|----------------|-------|--------|
| **BNO055** | 9-axis (gyro+accel+mag) | Sí (Cortex-M0) | ~0.5°/min (con mag) | ~$30 |
| ICM-42688-P | 6-axis (gyro+accel) | No | ~2°/min (sin mag) | ~$15 |
| BNO085 | 9-axis | Sí (mejorado) | ~0.3°/min | ~$20 |
| LSM6DSOX + LIS2MDL | 6+3 axis | ML core | ~1°/min | ~$15+$8 |

**Recomendación:** BNO055 para simplicidad (fusión onboard, I2C directo, leer heading sin programar filtro Kalman). BNO085 si está disponible (mismo concepto, mejor firmware). Para el nivel más alto, ICM-42688-P con filtro Madgwick custom en el ESP32 — más trabajo pero menor latencia y control total.

### Sensores de distancia

| Opción | Tecnología | Rango | Precisión | FOV | Precio |
|--------|-----------|-------|-----------|-----|--------|
| **VL53L1X** | ToF laser | 4m | ±3mm | 27° (programable) | ~$12 |
| VL53L4CX | ToF laser multizona | 6m | ±3mm | 18° (4×4 zonas) | ~$15 |
| TF-Luna | LiDAR | 8m | ±6mm | 2° | ~$20 |
| Sharp GP2Y0A21YK0F | IR analógico | 80cm | ±10mm | ~5° | ~$8 |

**Recomendación:** VL53L1X para posicionamiento general. VL53L4CX si necesitás detectar objetos en múltiples zonas simultáneamente (tiene 4×4 zonas de detección programables, podés "ver" si hay un objeto a la izquierda, centro y derecha al mismo tiempo).

### Sensor de color de alta gama

| Opción | Canales | Comunicación | Precio |
|--------|---------|-------------|--------|
| **TCS34725** | RGBC (con clear channel) | I2C | ~$8 |
| APDS-9960 | RGBC + proximidad + gesture | I2C | ~$8 |
| AS7262 | 6 canales visibles calibrados | I2C | ~$15 |
| AS7341 | 11 canales (8 visibles + NIR + clear + flicker) | I2C | ~$20 |

**Recomendación:** TCS34725 con LED integrado para iluminación constante. Da R, G, B, Clear raw — con estos podés hacer la normalización por cromaticidad r/(R+G+B) que es inmune a iluminación. El canal Clear te da la intensidad total para detectar negro/blanco. El AS7341 es superior pero más complejo de programar.

### Cámara

| Opción | Resolución | Procesamiento | Conexión | Precio |
|--------|-----------|---------------|----------|--------|
| ESP32-S3 + OV2640 (integrado) | 2MP | En el mismo controlador | Directo | ~$15 |
| OpenMV H7 Plus (dedicada) | 5MP | Cortex-M7 dedicado | UART | ~$85 |
| OV5640 + ESP32-CAM (separada) | 5MP | ESP32 dedicado | UART/I2C | ~$15 |

**Recomendación:** Si el controlador principal es ESP32-S3, integrar la cámara OV2640 directamente. Un solo chip hace todo. Si se quiere máximo rendimiento de visión, agregar OpenMV H7 como coprocesador dedicado.

### Chasis y estructura

| Opción | Material | Ventaja | Precio |
|--------|----------|---------|--------|
| **3D impreso PLA** | PLA (chasis) + TPU (flexibles) | Diseño exacto para la misión, peso optimizado | ~$10-20 |
| Aluminio cortado CNC | Al 6061 | Máxima rigidez, 0 flexión | ~$50-100 |
| PCB como chasis | FR4 | Integra electrónica + estructura, ultra liviano | ~$15-30 |
| Carbono/fibra de vidrio | CF/FG plate | Rigidez extrema, ultra liviano | ~$30-50 |

**Recomendación:** Chasis principal en 3D PLA con insertos metálicos para ejes. Partes flexibles (dedos de garra, amortiguadores) en TPU. Para equipos con acceso a CNC: placa base de aluminio de 2mm con torretas para montar motores y electrónica.

**La jugada maestra:** Usar la PCB del controlador como parte estructural del chasis. Una PCB de 100×100mm en FR4 de 1.6mm es sorprendentemente rígida y liviana (20g). Los motores se montan directamente con brackets soldados a la PCB. Esto elimina una capa de complejidad y peso.

### PCB custom (el nivel máximo)

Diseñar una PCB que integre:
- ESP32-S3-WROOM (controlador + WiFi + cámara)
- Drivers de motor DRV8833 o TB6612FNG (2 motores DC por chip)
- Conector para Dynamixel TTL (half-duplex UART)
- BNO055 o ICM-42688 onboard
- Conectores I2C para VL53L1X, TCS34725
- Reguladores de voltaje (5V para servos, 3.3V para lógica)
- Conector batería LiPo 7.4V
- LEDs de estado y buzzer
- Botón de inicio

```
PCB Custom "IITA WRO Bot v1" (~80×80mm)
┌──────────────────────────────────────┐
│  [ESP32-S3]    [DRV8833×2]          │
│  [OV2640 cam]  [M1][M2][M3][M4]    │
│                                      │
│  [BNO055]      [DXL TTL port]       │
│  [Buzzer]      [VL53L1X I2C]       │
│  [LED×4]       [TCS34725 I2C]      │
│                                      │
│  [LiPo 7.4V]  [5V reg] [3.3V reg] │
│  [Power switch] [START button]      │
└──────────────────────────────────────┘
```

Costo de fabricación PCB (JLCPCB): ~$15 por 5 unidades con SMD assembly.

### Batería

| Opción | Voltaje | Capacidad | Peso | Precio |
|--------|---------|-----------|------|--------|
| LiPo 2S 7.4V 500mAh | 7.4V | 500mAh | 30g | ~$8 |
| LiPo 2S 7.4V 1000mAh | 7.4V | 1000mAh | 55g | ~$12 |
| LiPo 1S 3.7V 1200mAh (×2) | 7.4V (series) | 1200mAh | 50g | ~$10 |

**Recomendación:** LiPo 2S 500mAh. Una misión de 2 minutos consume ~200mAh máximo con 5 motores. 500mAh da 2.5× de margen. Peso: solo 30g (vs ~150g de la batería SPIKE).

### BOM completo Nivel 3

| Componente | Cantidad | Precio |
|------------|----------|--------|
| ESP32-S3-DevKitC + OV2640 | 1 | $15 |
| Pololu 100:1 HPCB 6V con encoder | 2 | $32 |
| Dynamixel XL330-M288-T | 3 | $72 |
| BNO055 breakout | 1 | $30 |
| VL53L1X breakout | 2 | $24 |
| TCS34725 breakout | 1 | $8 |
| DRV8833 dual H-bridge (×2) | 2 | $6 |
| PCB custom (JLCPCB) | 1 | $15 |
| LiPo 2S 500mAh | 1 | $8 |
| Chasis 3D (PLA + TPU) | 1 | $15 |
| Ruedas silicona + O-rings | 2 | $5 |
| Cables, conectores, tornillos M2/M3 | - | $15 |
| **Total** | | **~$245** |

### Peso estimado: 350-500g (vs 1000-1200g del SPIKE)

El robot custom pesa MENOS DE LA MITAD que el SPIKE con el mismo o mejor rendimiento. Menos peso = menos inercia = frenado más preciso = mejor odometría.

### Puntaje máximo realista: 225-230/230

Con encoders de 1200 CPR, BNO055 drift-free, Dynamixel con control de corriente para apilado, y chasis rígido 3D impreso, el robot puede alcanzar 230 puntos de forma consistente. El apilado de torres es casi seguro gracias al feedback de corriente del Dynamixel (sentís cuándo el techo toca la base).

---

## Comparativa final

| Aspecto | Nivel 1: SPIKE puro | Nivel 2: SPIKE + mejoras | Nivel 3: Custom |
|---------|--------------------|-----------------------------|-----------------|
| **Costo** | $350-400 | ~$515 | **~$245** |
| **Peso** | 1000-1200g | 1000-1300g | **350-500g** |
| **Precisión odometría** | ±3-5mm/m | ±2-3mm/m | **±0.5-1mm/m** |
| **Precisión gyro** | ±2-4°/2min | **±0.5°/2min** | **±0.5°/2min** |
| **Backlash motores** | 2-3° | 2-3° (LEGO motors) | **<0.5°** |
| **Resolución encoder** | 360 CPR | 360 CPR (LEGO) | **1200 CPR** |
| **Sensor de color** | HSV (Pybricks) | HSV + cámara | **RGBC raw + cámara** |
| **Mecanismos** | LEGO Technic (juego mecánico) | LEGO + 3D custom | **3D custom + Dynamixel** |
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Tiempo de desarrollo** | 4-6 semanas | 6-8 semanas | **10-14 semanas** |
| **Mantenibilidad** | ⭐⭐⭐⭐⭐ (piezas LEGO) | ⭐⭐⭐ | ⭐⭐ (requiere soldar, imprimir) |
| **Puntaje esperado** | 200-220 | 215-230 | **225-230** |
| **Riesgo** | Bajo | Medio | Alto (más cosas que pueden fallar) |

---

## Recomendación para IITA 2026

### Corto plazo (nacional): Nivel 2

Usar SPIKE Prime + LMS-ESP32 + BNO055 + piezas 3D para la garra. Esto da el mejor balance de rendimiento vs riesgo vs tiempo de desarrollo. Los alumnos ya conocen SPIKE, y las mejoras son incrementales.

### Mediano plazo (internacional): Nivel 2 avanzado o Nivel 3 parcial

Si IITA clasifica al mundial, evaluar migrar a Nivel 3 para las ventajas de peso y precisión. O mantener SPIKE pero con todas las mejoras del Nivel 2 maximizadas.

### Largo plazo (2027+): Nivel 3

Desarrollar una plataforma custom IITA basada en ESP32-S3 + Dynamixel + PCB propia. Una vez desarrollada, la plataforma se reutiliza temporada tras temporada cambiando solo los mecanismos específicos del juego.

### La decisión que NO depende del hardware

> El robot más caro no gana. El robot más **probado** gana. Un SPIKE Prime con 200 horas de prueba le gana a un robot custom con 20 horas de prueba. El hardware es el 30% del éxito. El 70% es ensayo, calibración, y consistencia.
