# SKILL: Seguimiento de Línea en Pybricks Python para WRO RoboMission

## Descripción
Skill para generar código Pybricks Python de seguimiento de línea para LEGO SPIKE Prime en WRO RoboMission (Elementary y Junior). Cubre 1, 2 y 3 sensores, control PID, intersecciones, búsqueda y alineación.

## Plataforma
- **Hub:** LEGO SPIKE Prime (PrimeHub)
- **Firmware:** Pybricks v3.x
- **Sensores:** ColorSensor, `.reflection()` retorna 0-100
- **Motores:** Motor + DriveBase/GyroDriveBase

## API de referencia

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Stop, Button, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

sensor = ColorSensor(Port.C)
sensor.reflection()  # 0-100
sensor.color()       # Color.RED, etc.

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=112)
robot.drive(speed_mm_s, turn_rate_deg_s)
robot.straight(distance_mm)
robot.turn(angle_deg)
robot.stop()
robot.distance()
robot.angle()
robot.reset()
```

## Parámetros típicos

| Parámetro | Valor típico | Rango |
|-----------|-------------|-------|
| NEGRO | 8-15 | 5-25 |
| BLANCO | 85-95 | 60-100 |
| UMBRAL | 45-55 | 30-60 |
| UMBRAL_INTERSECCION | 20-30 | 15-40 |
| Kp | 1.5 | 0.5-4.0 |
| Ki | 0.01 | 0.0-0.05 |
| Kd | 5.0 | 1.0-15.0 |
| VELOCIDAD | 150-200 | 80-300 mm/s |
| INTEGRAL_MAX | 100 | 50-200 |

## Funciones fundamentales

### seguir_linea_pid (1 sensor)
```
error = sensor.reflection() - umbral (borde izq) o umbral - sensor.reflection() (borde der)
integral += error, clamp [-MAX, MAX]
P = kp*error, I = ki*integral, D = kd*(error - error_anterior)
robot.drive(velocidad, P + I + D)
```

### seguir_linea_diferencial (2 sensores)
```
error = sensor_izq.reflection() - sensor_der.reflection()
Luego PID igual
```

### seguir_hasta_interseccion (3 sensores)
Central sigue con PID, laterales detectan con reflection() < UMBRAL_INTER. Anti-rebote con variable `en_interseccion`. Conteo hasta N.

### girar_buscando_linea
Fase 1: girar hasta reflection > 60 (salir de negro). Fase 2: girar hasta reflection < 30 (encontrar nuevo negro).

### alinear_perpendicular
Motores individuales, cada uno frena cuando su sensor ve negro.

## Ejemplo completo: 3 sensores

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Button, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=112)
sensor_izq = ColorSensor(Port.C)
sensor_centro = ColorSensor(Port.D)
sensor_der = ColorSensor(Port.E)

NEGRO, BLANCO = 10, 90
UMBRAL = (NEGRO + BLANCO) / 2
UMBRAL_INTER = 25
Kp, Ki, Kd = 1.5, 0.01, 5.0
INTEGRAL_MAX = 100
_err_ant, _integral = 0, 0

def reset_pid():
    global _err_ant, _integral
    _err_ant, _integral = 0, 0

def seguir(borde="izquierdo", velocidad=180):
    global _err_ant, _integral
    err = sensor_centro.reflection() - UMBRAL if borde == "izquierdo" else UMBRAL - sensor_centro.reflection()
    _integral = max(-INTEGRAL_MAX, min(INTEGRAL_MAX, _integral + err))
    cor = Kp*err + Ki*_integral + Kd*(err - _err_ant)
    _err_ant = err
    robot.drive(velocidad, cor)

def ir_a_interseccion(lado="izquierda", n=1, borde="izquierdo", vel=180):
    reset_pid()
    conteo, en_inter = 0, False
    while True:
        seguir(borde, vel)
        if lado == "izquierda":
            det = sensor_izq.reflection() < UMBRAL_INTER
        elif lado == "derecha":
            det = sensor_der.reflection() < UMBRAL_INTER
        else:
            det = sensor_izq.reflection() < UMBRAL_INTER and sensor_der.reflection() < UMBRAL_INTER
        if det and not en_inter:
            conteo += 1
            en_inter = True
            if conteo >= n:
                robot.stop()
                return
        elif not det:
            en_inter = False
        wait(10)

def main():
    while Button.CENTER not in hub.buttons.pressed():
        wait(50)
    wait(500)
    ir_a_interseccion("derecha", 2)
    robot.straight(40)
    robot.turn(90)
    robot.straight(25)
    reset_pid()
    while True:
        seguir("izquierdo", 120)
        if (sensor_izq.reflection() > 70 and sensor_centro.reflection() > 70 and sensor_der.reflection() > 70):
            robot.stop()
            break
        wait(10)

main()
```

## Reglas para generar código

1. SIEMPRE incluir calibración NEGRO/BLANCO configurables
2. SIEMPRE usar debounce en detección de intersecciones
3. SIEMPRE resetear PID al cambiar de tramo
4. SIEMPRE limitar integral (anti-windup)
5. Usar wait(10) al final de cada ciclo while
6. Comentar wheel_diameter y axle_track como ajustables
7. Incluir prints para debugging
8. Estructura: imports → init → constantes → funciones → main()
