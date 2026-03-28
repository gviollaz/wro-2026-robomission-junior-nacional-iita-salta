# SKILL: Mejores Prácticas de Movimiento para WRO RoboMission (Pybricks)

## Descripción
Skill para generar código Pybricks Python con mejores prácticas de movimiento de competencia: arranque/freno suave, odometría precisa, uso correcto del giroscopio, calibración PID, perfiles de velocidad. SPIKE Prime en WRO RoboMission.

## Reglas obligatorias al generar código

### 1. Inicialización del giroscopio
```python
hub = PrimeHub()
hub.imu.settings(angular_velocity_threshold=5, acceleration_threshold=50,
                  heading_correction=358)  # MEDIR
while not hub.imu.ready():
    wait(100)
robot.use_gyro(True)
```

### 2. Velocidad máxima segura
NUNCA > 400 mm/s (80% de ~488 mm/s teórico con ruedas 56mm). Recomendado: 150-250 navegación, 80-120 precisión.

### 3. Aceleración suave
```python
robot.settings(straight_speed=200, straight_acceleration=150,
               turn_rate=120, turn_acceleration=80)
```

### 4. Perfiles de velocidad
```python
def perfil_preciso():
    robot.settings(120, 80, 80, 60)
def perfil_normal():
    robot.settings(200, 150, 120, 80)
def perfil_rapido():
    robot.settings(350, 200, 150, 100)
```

### 5. Calibración obligatoria (comentar en código)
```python
robot = DriveBase(motor_izq, motor_der,
    wheel_diameter=56,   # CALIBRAR
    axle_track=112)      # CALIBRAR
```

### 6. Stop modes
HOLD para posiciones críticas, COAST para transiciones.

## API relevante

### DriveBase.settings()
straight_speed (mm/s, máx ~400), straight_acceleration (mm/s², ≤200), turn_rate (°/s, máx ~180), turn_acceleration (°/s²)

### IMU
hub.imu.settings(angular_velocity_threshold, acceleration_threshold, heading_correction)
hub.imu.ready(), hub.imu.stationary(), hub.imu.heading(), hub.imu.reset_heading(0)

### PID por escenario
| Escenario | Kp | Ki | Kd | Vel |
|-----------|----|----|----|----|
| 1 sensor lento | 1.5 | 0 | 5 | 120 |
| 1 sensor curvas | 2.0 | 0.01 | 7 | 150 |
| 2 sensores | 0.8 | 0 | 4 | 200 |
| Rápido | 2.5 | 0 | 10 | 300 |

## Orden de calibración
1. wheel_diameter → avanzar 1000mm, medir, ajustar
2. axle_track → girar 3600° (10 vueltas), ajustar
3. heading_correction → girar 360° a mano
4. Activar use_gyro(True)
5. Calibrar PID con robot calibrado

## Plantilla de competencia

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Stop, Color, Button
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

hub = PrimeHub()
hub.imu.settings(angular_velocity_threshold=5, acceleration_threshold=50,
                  heading_correction=358)
hub.light.on(Color.RED)
while not hub.imu.ready():
    wait(100)
hub.light.on(Color.GREEN)

motor_izq = Motor(Port.A, Direction.COUNTERCLOCKWISE)
motor_der = Motor(Port.B)
robot = DriveBase(motor_izq, motor_der, wheel_diameter=56, axle_track=112)
robot.use_gyro(True)
robot.settings(200, 150, 120, 80)

sensor = ColorSensor(Port.E)
NEGRO, BLANCO = 10, 90
UMBRAL = (NEGRO + BLANCO) / 2
Kp, Ki, Kd = 1.5, 0.01, 5.0
_err_ant, _integral = 0, 0

def reset_pid():
    global _err_ant, _integral
    _err_ant, _integral = 0, 0

def recalibrar_gyro():
    robot.stop()
    wait(1500)

while Button.CENTER not in hub.buttons.pressed():
    wait(50)
wait(500)
hub.imu.reset_heading(0)
# === MISIÓN ===
```

## Errores a evitar
- NO velocidades > 400 mm/s
- NO olvidar wait(10) en loops de drive()
- NO olvidar hub.imu.ready()
- NO asumir turn(90) exacto sin heading_correction
- NO Ki > 0.05
- NO olvidar reset_pid() al cambiar tramo
