# Batería, Driver y Encoders — Selección definitiva para Nivel 3+

## Respuestas directas a las 3 preguntas

---

## 1. BATERÍA: ¿Cuál usar?

### Recomendación: LiPo 2S 7.4V 800mAh 25-45C

**Modelo específico:** Gens Ace 800mAh 2S 45C (JST) o TATTU 800mAh 2S 45C (JST)

| Parámetro | Valor |
|-----------|-------|
| Química | LiPo (Litio Polímero) |
| Configuración | 2S (2 celdas en serie) |
| Voltaje nominal | 7.4V |
| Voltaje máximo (carga completa) | 8.4V |
| Voltaje mínimo seguro | 6.4V (3.2V/celda) |
| Capacidad | 800mAh |
| Tasa de descarga | 25-45C continuo |
| Corriente máx continua | 45C × 0.8A = **36A** (sobra enormemente) |
| Peso | **30-50g** |
| Dimensiones típicas | 47×25×13mm |
| Precio | ~$8-15 |
| Conector descarga | JST-SYP (recomendar cambiar a XT30 para más corriente) |
| Conector balance | JST-XH 3-pin |

### ¿Por qué 2S 800mAh y no otra cosa?

**¿Por qué 2S (7.4V) y no 3S (11.1V)?**

Los motores Pololu N20 son de 6V. Con batería 2S (7.4-8.4V) + regulador buck a 6V, tenés suficiente headroom (1.4-2.4V de margen). Con 3S (11.1V) necesitás un regulador que disipe más calor y es overkill. Los Dynamixel XL330 operan de 3.7-6V, así que también van regulados desde los 7.4V. Todo el sistema corre cómodo con 2S.

**¿Por qué 800mAh y no 500mAh?**

Hice el cálculo de consumo:

| Componente | Corriente típica | Duración |
|------------|-----------------|----------|
| Teensy 4.1 | 100mA | 2 min |
| ESP32-S3 (WiFi off) | 80mA | 2 min |
| Pololu 30:1 ×2 (marcha) | 200mA | 2 min |
| Dynamixel XL330 ×3 (activos) | 200mA | 1 min |
| Sensores (BNO055 + ToF + color) | 80mA | 2 min |
| **Total promedio** | **~500mA** | **2 min** |

Consumo por ronda: 500mA × (2/60)h = **16.7mAh por ronda**.

Con 800mAh, tenés para **~48 rondas** sin recargar. ¿Por qué tanto margen? Porque:
- Picos de corriente al arrancar motores (stall breve) llegan a 2-3A
- La capacidad real de una LiPo bajo carga es ~80% de la nominal
- Querés llegar al final del día de competencia (3 rondas oficiales + práctica) SIN cargar
- El peso extra de 800 vs 500mAh es solo ~10g (insignificante en un robot de 300g)

**¿Por qué NO LiFePO4 o Li-Ion 18650?**

- LiFePO4: más segura pero 2× más pesada y más grande para la misma energía
- Li-Ion 18650: forma cilíndrica difícil de integrar, peso alto (~45g/celda), menor C-rate (no soporta picos de stall)
- LiPo: la mejor densidad de energía, forma plana ideal para PCB-chassis, altas tasas de descarga

### Cargador recomendado

**ISDT Q6 Nano** (~$35) o **ToolkitRC M4AC** (~$20). Ambos son cargadores balance LiPo compactos con pantalla. Cargan 2S a 1C (0.8A) en ~1 hora.

### Seguridad

- Siempre usar batería LiPo con **conector de balance** (3 cables: V+, Vmid, V-)
- Cargar SOLO con cargador balance LiPo (nunca con cargador genérico)
- Almacenar a **3.8V/celda** (storage voltage)
- Usar **LiPo bag** para cargar y transportar
- En el robot: monitorear voltaje por ADC del ESP32/Teensy, cortar motores si baja de 6.4V

---

## 2. DRIVER DE MOTORES: ¿Cuál usar?

### Recomendación: DRV8833 para tracción + Dynamixel directo para mecanismos

### Para motores de tracción (Pololu N20): DRV8833

| Parámetro | DRV8833 | TB6612FNG | L298N |
|-----------|---------|-----------|-------|
| Tecnología | MOSFET | MOSFET | BJT |
| Voltaje motor | 2.7-10.8V | 4.5-13.5V | 5-35V |
| Voltaje lógica | **1.8-7V** | 2.7-5.5V | 5V |
| Corriente continua/canal | **1.5A** | 1.2A | 2A |
| Corriente pico/canal | 2A | 3.2A | 3A |
| Voltage drop (Rds_on) | **~0.3V** (360mΩ) | ~0.5V | **~2V** (fatal) |
| Current limiting | **Sí (configurable con R)** | No | No |
| Sleep mode | **Sí (<1µA)** | Sí (STBY pin) | No |
| Fault output | **Sí (nFAULT pin)** | No | No |
| Pines por motor | 2 (ambos PWM) | 3 (2 dir + 1 PWM) | 3 (2 dir + 1 EN) |
| Tamaño package | HTSSOP-16 (tiny) | SOP-24 | TO-220 (enorme) |
| Precio breakout | ~$3 | ~$4 | ~$3 |
| **Para este robot** | **✅ GANADOR** | ⚠️ Bueno pero... | ❌ Obsoleto |

### ¿Por qué DRV8833 y no TB6612FNG?

1. **Voltaje lógico 1.8V:** Compatible directo con 3.3V del ESP32-S3 y Teensy sin level shifter. El TB6612 necesita mínimo 2.7V y algunos módulos fallan con 3.3V.

2. **Current limiting integrado:** Con una resistencia en el pin ISENSE, el DRV8833 limita la corriente automáticamente. Si el Pololu se traba (stall), el driver limita a 1A en vez de dejar pasar 1.6A que quemaría el motor. Esto protege el motor Y la batería.

3. **nFAULT output:** Si hay sobrecorriente, sobretemperatura, o undervoltage, el DRV8833 baja el pin nFAULT. El Teensy puede leer esto y reaccionar (parar, alarma). El TB6612 no tiene esto.

4. **2 pines por motor:** Necesitás 2 canales PWM por motor, total 4 para 2 motores. El Teensy 4.1 tiene 35 PWM → sobra. El ESP32-S3 tiene 8 LEDC → también sobra.

### Configuración del current limit

```
RISENSE = VREF / ILIMIT

Para limitar a 1.0A (protección Pololu N20):
RISENSE = 0.2V / 1.0A = 0.2Ω

Resistor: 0.2Ω 1/4W (SMD 0805 o through-hole)
```

Poner la resistencia entre el pin ISENSE del DRV8833 y GND. Listo, el motor nunca va a recibir más de 1A.

### Cantidad de DRV8833

Cada DRV8833 maneja 2 motores. Para 2 motores de tracción necesitás 1 DRV8833.

Si usás un 3er motor DC (en vez de Dynamixel) para algún mecanismo, agregás un 2do DRV8833. Total: 1 o 2 chips DRV8833 (~$3-6).

### Para mecanismos: Dynamixel directo (NO driver externo)

Los Dynamixel XL330 tienen driver integrado. Se conectan directamente al bus TTL del Teensy/ESP32. No necesitan H-bridge externo. Esto es una de sus grandes ventajas: menos componentes, menos cables, menos puntos de falla.

```
Teensy UART (half-duplex) → Cable 3-pin JST → DXL330 #1 → DXL330 #2 → DXL330 #3
                                                (daisy-chain, un solo cable)
```

---

## 3. ENCODERS: ¿Cuáles usar?

### Recomendación: Pololu con encoder magnético integrado (12 CPR en eje motor)

### ¿Qué tipos de encoder existen?

| Tipo | Resolución típica | Precisión | Tamaño | Precio | Robustez |
|------|-------------------|-----------|--------|--------|----------|
| **Hall effect magnético** | 12 CPR en eje motor | ±0.5° | Muy chico (dentro del motor) | Incluido en motor | ⭐⭐⭐⭐⭐ Sin contacto |
| Óptico reflectivo | 12-20 CPR | ±1° | Chico | ~$5 | ⭐⭐⭐ Sucio = falla |
| Óptico transmisivo | 100-2048 CPR | ±0.05° | Grande (disco perforado) | ~$20-50 | ⭐⭐⭐⭐ |
| Capacitivo (CUI AMT10) | 2048+ CPR | ±0.1° | Mediano | ~$30 | ⭐⭐⭐⭐⭐ |
| Resolvers (industrial) | Analógico contínuo | ±0.01° | Grande | ~$100+ | ⭐⭐⭐⭐⭐ |

### Encoder del Pololu N20: la mejor opción integrada

Los Pololu HPCB con encoder ya vienen con el encoder Hall magnético de 12 CPR **integrado y calibrado de fábrica**. No hay nada que armar ni calibrar.

**Resolución final en el eje de salida:**

| Motor | Reducción | CPR motor | **CPR eje de salida** | Resolución angular |
|-------|-----------|-----------|----------------------|-------------------|
| Pololu 10:1 HPCB | 10.28:1 | 12 | 123 | 2.9° |
| Pololu 30:1 HPCB | 29.86:1 | 12 | **358** | **1.0°** |
| Pololu 50:1 HPCB | 51.45:1 | 12 | **617** | **0.58°** |
| Pololu 100:1 HPCB | 100.37:1 | 12 | **1204** | **0.30°** |
| LEGO Motor (referencia) | — | — | 360 | 1.0° |

### ¿30:1 o 100:1? La decisión del encoder

| Motor | CPR salida | Vel. robot (rueda 32mm) | Resolución lineal | ¿Para WRO? |
|-------|-----------|------------------------|-------------------|-----------|
| 30:1 | 358 CPR | **500mm/s** (rápido) | 0.28mm/count | **Sweet spot: rápido + preciso** |
| 50:1 | 617 CPR | 300mm/s (moderado) | 0.16mm/count | Más preciso, algo lento |
| 100:1 | 1204 CPR | 150mm/s (lento) | 0.083mm/count | Ultra preciso, demasiado lento |

**Recomendación: Pololu 30:1 HPCB 6V con encoder integrado**

El 30:1 da 358 CPR (comparable a LEGO 360 CPR) pero a 500mm/s de velocidad (2× LEGO). El robot cruza el campo de 2.4m en 5 segundos. Si necesitás más precisión en un momento específico (ej: apilado de torre), reducís la velocidad a 100mm/s por software y la resolución efectiva sube proporcionalmente.

### ¿No alcanza 358 CPR? Mejora sin cambiar motor

Si querés más resolución sin cambiar el motor, hay dos opciones:

**Opción A: Encoder externo en eje de salida**

Agregar un encoder óptico CUI AMT103-V (2048 PPR configurable) en el eje de salida del motor. Es un encoder de alta resolución ($18/u) que se monta externamente.

Problema: agrega tamaño y peso. No vale la pena para WRO.

**Opción B: Interpolación por software**

Con el PID corriendo a 5kHz y encoder de 358 CPR, a 500mm/s el robot cuenta ~2.7 pulsos por milisegundo. El Teensy 4.1 puede interpolar entre pulsos usando el timer de alta resolución para estimar posición sub-pulse. Esto da resolución "virtual" de ~3000+ CPR sin hardware extra.

### Conexión eléctrica del encoder Pololu

```
Motor Pololu con encoder (6 pines JST-SH):
  Pin 1: Motor + (al DRV8833 OUT)
  Pin 2: Motor - (al DRV8833 OUT)
  Pin 3: Encoder GND
  Pin 4: Encoder VCC (3.3V o 5V)
  Pin 5: Encoder A (al GPIO Teensy, con pull-up)
  Pin 6: Encoder B (al GPIO Teensy, con pull-up)
```

En el Teensy 4.1, los encoders se leen con la librería `Encoder.h` que usa interrupciones de hardware para no perder pulsos. En el ESP32-S3, se usa el periférico PCNT.

---

## 4. Resumen: la compra completa

### Lista de compra con links de referencia

| # | Componente | Modelo exacto | Cant. | Precio/u | Total |
|---|-----------|---------------|-------|----------|-------|
| 1 | Motor tracción con encoder | Pololu #4823 (30:1 HPCB 6V, encoder integrado, back connector) | 2 | $17 | $34 |
| 2 | Driver motores tracción | Pololu #2130 (DRV8833 Dual Motor Driver Carrier) | 1 | $5 | $5 |
| 3 | Servo mecanismos | Robotis Dynamixel XL330-M288-T | 3 | $24 | $72 |
| 4 | Batería | Gens Ace / TATTU 800mAh 2S 45C LiPo (JST) | 1 | $12 | $12 |
| 5 | Cargador balance LiPo | ToolkitRC M4AC (o similar 2-4S) | 1 | $20 | $20 |
| 6 | Conector batería | XT30 macho+hembra (reemplazar JST) | 2 pares | $2 | $2 |
| 7 | Resistor current limit | 0.2Ω 1/4W (para DRV8833 ISENSE) | 2 | $0.05 | $0.10 |
| **Subtotal motores+batería+driver** | | | | | **~$145** |

Estos $145 cubren tracción + mecanismos + energía + cargador, que son el corazón del robot.

---

## 5. Compatibilidad del conjunto

### Flujo de energía

```
LiPo 2S 7.4V 800mAh
     │
     ├──▶ [TPS5430 Buck 5V/2A] ──▶ Dynamixel XL330 ×3 (3.7-6V OK)
     │                              DRV8833 Vmotor (hasta 10.8V)
     │                              → Pololu N20 6V (recibe ~5V vía PWM)
     │
     └──▶ [AMS1117 3.3V/1A] ──▶ Teensy 4.1
                                   ESP32-S3
                                   Sensores (BNO055, VL53L5CX, etc.)
```

### ¿Por qué regular a 5V para los motores y no conectar directo 7.4V?

Los Pololu son motores de 6V. A 7.4V funcionan, pero la corriente de stall sube (~1.6A × 7.4/6 = ~2A) y la vida útil se reduce. Con el regulador a 5V (o regulando por PWM desde 7.4V nunca al 100%), mantenés los motores dentro de spec.

En la práctica, el DRV8833 conectado a 7.4V con PWM al 70% entrega ~5.2V al motor, que es perfecto. No necesitás regulador separado para los motores si controlás el duty cycle máximo por software:

```cpp
#define MAX_PWM 180  // de 255 → 70% de 7.4V = 5.2V al motor
```

Esto simplifica el circuito (un regulador menos) y funciona perfectamente.

---

## 6. Tip final: orden de prototipado

1. **Semana 1:** Comprar Pololu con encoder + DRV8833 breakout + Teensy 4.1 + LiPo. Armar en breadboard. Hacer girar motores con PID.
2. **Semana 2:** Agregar Dynamixel XL330 ×1. Probar control de posición y corriente.
3. **Semana 3:** Agregar BNO055. Fusionar heading con odometría.
4. **Semana 4:** Armar chasis 3D provisional. Robot se mueve y gira preciso.
5. **Semana 5+:** Agregar mecanismos, sensores ToF, color, cámara...

Empezar con lo mínimo y agregar de a poco. Cada componente tiene que funcionar PERFECTO antes de agregar el siguiente.
