# 04 - Calibración de PID para Color y Giroscopio

## ¿Qué es PID?

**P**roporcional-**I**ntegral-**D**erivativo. Ajusta la corrección del robot según:
- **P**: "¿Qué tan lejos estoy?" → corrección proporcional al error
- **I**: "¿Hace rato que estoy desviado?" → corrige errores persistentes
- **D**: "¿Estoy mejorando o empeorando?" → frena oscilaciones

## Método Ziegler-Nichols simplificado

### Paso 1: Encontrar Kp crítico (Ki=0, Kd=0)
Empezar Kp=0.5, subir hasta que oscile violentamente. Ese es Kp_critico.

### Paso 2: Kp_trabajo = Kp_critico × 0.6

### Paso 3: Kd_inicial = Kp_trabajo × 4

### Paso 4: Ki solo si hay error constante. Ki_inicial = Kp_trabajo × 0.01

### Tabla de ajuste rápido

| Si el robot... | Ajustar | Dirección |
|----------------|---------|-----------|
| Reacciona lento | Kp | ↑ Subir |
| Oscila mucho | Kp | ↓ Bajar |
| Sacude | Kd | ↑ Subir |
| Lento en curvas | Kd | ↓ Bajar |
| Error constante | Ki | ↑ Subir (poco!) |
| Se vuelve loco | Ki | ↓ Bajar o = 0 |

## Valores por escenario

| Escenario | Kp | Ki | Kd | Vel mm/s |
|-----------|----|----|----|----|
| Línea 1 sensor lento | 1.5 | 0 | 5 | 120 |
| Línea con curvas, 1 sensor | 2.0 | 0.01 | 7 | 150 |
| Línea 2 sensores | 0.8 | 0 | 4 | 200 |
| Línea 2 sensores curvas | 1.2 | 0.005 | 6 | 150 |
| Seguimiento rápido | 2.5 | 0 | 10 | 300 |

## PID depende de la velocidad

```python
Kp_lento, Kd_lento = 1.5, 5.0     # Para 100-150 mm/s
Kp_rapido, Kd_rapido = 2.5, 10.0  # Para 250-350 mm/s

def seguir_linea(velocidad=150):
    kp, kd = (Kp_lento, Kd_lento) if velocidad <= 150 else (Kp_rapido, Kd_rapido)
```

## DriveBase settings()

```python
speed, accel, turn_rate, turn_accel = robot.settings()
# Sobrepasa objetivo → bajar aceleración
# Sobregira → bajar turn_acceleration
# Giros lentos → subir turn_rate (máx ~180°/s)
```

## Programa de calibración interactivo

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Button
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()
while not hub.imu.ready():
    wait(100)
motor_izq = Motor(Port.A, Direction.COUNTERCLOCKWISE)
motor_der = Motor(Port.B)
robot = DriveBase(motor_izq, motor_der, wheel_diameter=56, axle_track=112)
robot.use_gyro(True)
sensor = ColorSensor(Port.E)

UMBRAL = 50
Kp, Ki, Kd = 1.5, 0.0, 5.0
error_ant, integral = 0, 0

print("Izq = bajar Kp, Der = subir Kp. Centro = iniciar")
while Button.CENTER not in hub.buttons.pressed():
    wait(50)
wait(500)

while True:
    error = sensor.reflection() - UMBRAL
    integral = max(-100, min(100, integral + error))
    correccion = Kp*error + Ki*integral + Kd*(error - error_ant)
    error_ant = error
    robot.drive(150, correccion)
    if Button.LEFT in hub.buttons.pressed():
        Kp = max(0.1, Kp - 0.1)
        hub.speaker.beep(400, 50)
        print("Kp =", Kp)
        wait(300)
    if Button.RIGHT in hub.buttons.pressed():
        Kp += 0.1
        hub.speaker.beep(600, 50)
        print("Kp =", Kp)
        wait(300)
    wait(10)
```

## Anti-windup

```python
INTEGRAL_MAX = 100
integral = max(-INTEGRAL_MAX, min(INTEGRAL_MAX, integral + error))

def resetear_pid():
    global error_ant, integral
    error_ant, integral = 0, 0
```

**Estos son puntos de partida.** Cada robot es diferente. Siempre calibrá con TU robot en el tapete real.
