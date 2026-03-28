# 02 - Seguimiento de Línea con 1 Sensor

## La idea principal

Con un solo sensor de color, el robot sigue el **borde** de la línea (izquierdo o derecho). El sensor "baila" en zigzag entre el negro y el blanco, intentando mantenerse justo en el borde.

```
Vista desde arriba (siguiendo borde izquierdo):
                                    
  Blanco  │████ Negro ████│  Blanco
          │               │
    ←─ ·  │  · ─→         │
       ↑  │↗              │
       · ─┤               │
          │← ·             │
          │  ↑             │
          │  · ─→          │
          │     ↑          │
          │     · ──       │

  El sensor zigzaguea sobre el borde
```

## Nivel 1: Control ON/OFF (solo para entender, NO usar en competencia)

La forma más simple pero menos precisa. El robot solo puede ir a la izquierda o a la derecha, sin punto medio.

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction
from pybricks.tools import wait

hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)
sensor = ColorSensor(Port.C)

NEGRO = 10
BLANCO = 90
UMBRAL = (NEGRO + BLANCO) / 2
VELOCIDAD = 200  # grados por segundo

while True:
    if sensor.reflection() < UMBRAL:
        # Estamos sobre negro → girar a la izquierda (borde izquierdo)
        left_motor.run(VELOCIDAD * 0.2)
        right_motor.run(VELOCIDAD)
    else:
        # Estamos sobre blanco → girar a la derecha
        left_motor.run(VELOCIDAD)
        right_motor.run(VELOCIDAD * 0.2)
    wait(10)
```

**Problema:** El robot se sacude mucho porque solo tiene dos estados. Es como manejar un auto girando el volante todo a la izquierda o todo a la derecha.

## Nivel 2: Control Proporcional (P) — Recomendado para empezar

La corrección es **proporcional** al error. Si el robot se desvía poquito, corrige poquito. Si se desvía mucho, corrige mucho.

### Fórmula

```
error = reflexión_actual - umbral
corrección = Kp × error
```

- `Kp` es la **ganancia proporcional**. Controla qué tan fuerte reacciona el robot.
- Si `Kp` es muy chico → el robot reacciona lento y se pierde en las curvas
- Si `Kp` es muy grande → el robot se sacude demasiado

### Seguir borde IZQUIERDO con control P

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=112)
sensor = ColorSensor(Port.C)

# --- Calibración ---
NEGRO = 10
BLANCO = 90
UMBRAL = (NEGRO + BLANCO) / 2

# --- Parámetros ---
VELOCIDAD = 150   # mm/s (empezá lento, subí cuando funcione)
Kp = 1.5          # Ganancia proporcional (ajustar experimentando)

# --- Bucle principal ---
while True:
    error = sensor.reflection() - UMBRAL
    correccion = Kp * error
    
    # BORDE IZQUIERDO: error positivo (blanco) → girar derecha (hacia negro)
    robot.drive(VELOCIDAD, correccion)
    wait(10)
```

### Seguir borde DERECHO con control P

La **única diferencia** es invertir el signo del error:

```python
while True:
    error = UMBRAL - sensor.reflection()  # ← signo invertido
    correccion = Kp * error
    robot.drive(VELOCIDAD, correccion)
    wait(10)
```

**¿Por qué se invierte?** Porque ahora cuando el sensor ve blanco (a la izquierda de la línea), queremos girar a la izquierda (negativo), y cuando ve negro queremos girar a la derecha (positivo).

### Tabla para entender el signo

| Borde | Sensor ve blanco (refl. alta) | Sensor ve negro (refl. baja) |
|-------|-------------------------------|------------------------------|
| Izquierdo | error positivo → girar derecha | error negativo → girar izquierda |
| Derecho | error negativo → girar izquierda | error positivo → girar derecha |

## Nivel 3: Control PID — Para máxima precisión

El control PID agrega dos componentes más al control P:

- **P (Proporcional):** Corrige según el error actual. "¿Qué tan lejos estoy?"
- **I (Integral):** Corrige según el error acumulado. "¿Hace rato que estoy desviado?"
- **D (Derivativo):** Corrige según la velocidad del cambio. "¿Estoy empeorando o mejorando?"

### Fórmula completa

```
error = reflexión_actual - umbral

P = Kp × error
I = Ki × suma_de_errores
D = Kd × (error - error_anterior)

corrección = P + I + D
```

### Seguidor PID borde IZQUIERDO completo

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=112)
sensor = ColorSensor(Port.C)

# --- Calibración ---
NEGRO = 10
BLANCO = 90
UMBRAL = (NEGRO + BLANCO) / 2

# --- Parámetros PID ---
VELOCIDAD = 150   # mm/s
Kp = 1.5          # Proporcional
Ki = 0.01         # Integral (empezar muy bajo!)
Kd = 5.0          # Derivativo

# --- Variables de estado ---
error_anterior = 0
integral = 0
INTEGRAL_MAX = 100  # Límite para evitar que se acumule demasiado

# --- Bucle principal ---
while True:
    error = sensor.reflection() - UMBRAL
    
    # Proporcional
    P = Kp * error
    
    # Integral (con límite anti-windup)
    integral = integral + error
    if integral > INTEGRAL_MAX:
        integral = INTEGRAL_MAX
    elif integral < -INTEGRAL_MAX:
        integral = -INTEGRAL_MAX
    I = Ki * integral
    
    # Derivativo
    D = Kd * (error - error_anterior)
    error_anterior = error
    
    # Corrección total
    correccion = P + I + D
    
    robot.drive(VELOCIDAD, correccion)
    wait(10)
```

### Para borde DERECHO, solo cambiá el cálculo del error:
```python
    error = UMBRAL - sensor.reflection()  # Invertido
```

## ¿Cómo ajustar los parámetros Kp, Ki, Kd?

### Método paso a paso (receta para principiantes):

1. **Empezá solo con P (Ki=0, Kd=0)**
   - Poné `Kp = 0.5` y probá
   - Si el robot reacciona lento y se pierde → subí Kp
   - Si el robot se sacude mucho → bajá Kp
   - Buscá un Kp donde el robot siga la línea pero oscile un poco

2. **Agregá D (dejá Ki=0 todavía)**
   - Poné `Kd = 3.0` y probá
   - El D "frena" las oscilaciones. Hace que el robot sea más suave
   - Si sigue oscilando → subí Kd
   - Si reacciona muy lento en curvas → bajá Kd

3. **Agregá I solo si es necesario**
   - La I sirve si el robot tiende a quedarse un poquito desviado constantemente
   - Empezá con `Ki = 0.005` (muy bajo!)
   - Si el robot empieza a oscilar cada vez más → bajá Ki o subí INTEGRAL_MAX

### Valores típicos para SPIKE Prime en tapete WRO

| Parámetro | Valor inicial | Rango típico |
|-----------|--------------|--------------|
| Kp | 1.5 | 0.5 - 4.0 |
| Ki | 0.01 | 0.0 - 0.05 |
| Kd | 5.0 | 1.0 - 15.0 |
| VELOCIDAD | 150 mm/s | 80 - 300 mm/s |

**Tip competitivo:** Usá velocidad baja (100-150) cuando necesitás precisión, y más alta (200-300) en tramos rectos donde la línea no tiene curvas cerradas.

## Función reutilizable para seguir línea

```python
def seguir_linea_1sensor(sensor, robot, borde="izquierdo",
                          velocidad=150, kp=1.5, ki=0.01, kd=5.0,
                          negro=10, blanco=90):
    """
    Sigue la línea por un ciclo del bucle.
    Llamar dentro de un while loop.
    
    borde: "izquierdo" o "derecho"
    Retorna el error actual (útil para combinación con otros sensores)
    """
    umbral = (negro + blanco) / 2
    
    # Variables persistentes (usar atributos de la función)
    if not hasattr(seguir_linea_1sensor, "error_ant"):
        seguir_linea_1sensor.error_ant = 0
        seguir_linea_1sensor.integral = 0
    
    if borde == "izquierdo":
        error = sensor.reflection() - umbral
    else:
        error = umbral - sensor.reflection()
    
    seguir_linea_1sensor.integral += error
    seguir_linea_1sensor.integral = max(-100, min(100, seguir_linea_1sensor.integral))
    
    P = kp * error
    I = ki * seguir_linea_1sensor.integral
    D = kd * (error - seguir_linea_1sensor.error_ant)
    seguir_linea_1sensor.error_ant = error
    
    correccion = P + I + D
    robot.drive(velocidad, correccion)
    
    return error
```

## Limitaciones del seguimiento con 1 sensor

- **No detecta intersecciones** directamente (solo ve un punto)
- **No sabe si llegó al final** de la línea
- **Puede confundirse** en curvas muy cerradas o cruces
- **Velocidad limitada** en curvas porque necesita oscilar

**Para resolver estas limitaciones → ver los documentos de 2 y 3 sensores.**
