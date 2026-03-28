# 03 - Giroscopio: Guía Completa para WRO con SPIKE Prime

## ¿Qué es el giroscopio?

El SPIKE Prime Hub tiene un **IMU** (giroscopio + acelerómetro). El giroscopio mide qué tan rápido gira el hub y calcula cuántos grados giró en total (el "heading"). Es como una brújula digital que no depende de las ruedas.

## Activar giroscopio

```python
hub = PrimeHub()
robot = DriveBase(motor_izq, motor_der, wheel_diameter=56, axle_track=112)
robot.use_gyro(True)  # Todos los movimientos usan gyro automáticamente
```

## Inicialización: el momento más crítico

### Regla #1: NO MOVER el hub durante el encendido

```python
hub = PrimeHub()
hub.imu.settings(angular_velocity_threshold=5, acceleration_threshold=50)
print("Calibrando... ¡NO TOCAR!")
hub.light.on(Color.RED)
while not hub.imu.ready():
    wait(100)
hub.light.on(Color.GREEN)
print("Gyro OK")
```

### Regla #2: Hub QUIETO y PLANO sobre una superficie

### En competencia con vibraciones:
Subir umbrales para que el hub pueda calibrar en ambiente ruidoso:
```python
hub.imu.settings(angular_velocity_threshold=5, acceleration_threshold=50)
```

## heading_correction: compensar el error de fábrica

Cada hub reporta un valor diferente para 360°. Medir así:

```python
hub.imu.reset_heading(0)
# Girar robot EXACTAMENTE 360° a mano con marca de referencia
heading_medido = hub.imu.heading()
print("heading_correction =", heading_medido)
# Aplicar:
hub.imu.settings(heading_correction=heading_medido)
```

Hacer 3 veces y promediar. Anotar el valor — es específico de cada hub.

## Recalibración durante la misión

```python
def recalibrar_gyro():
    robot.stop()
    wait(1500)  # Quieto 1.5s para que recalibre automáticamente
```

Cuándo: antes de ronda (siempre), después de colisión, antes de giros críticos, cada 30-60s.
NO recalibrar mientras se mueve.

## Orientación del hub

```python
hub = PrimeHub()  # Default: horizontal, plano
hub = PrimeHub(top_side=Axis.Z, front_side=Axis.X)  # Si está parado
```

Recomendación: montar horizontal y centrado siempre que se pueda.

## 5 Limitaciones del giroscopio SPIKE Prime

### 1. Drift (~0.5-2°/min)
Heading se desvía incluso quieto. Mitigación: recalibrar, usar líneas del tapete.

### 2. Error acumulativo en giros repetidos
10 giros de 90° acumulan ~10-20° de error. Mitigación: heading_correction, alternar dirección.

### 3. No funciona bien en rampas
Heading se contamina si el robot se inclina. Mitigación: Pybricks 3.6+ tiene heading('3D').

### 4. Sensible a temperatura
Hub caliente driftea más. Mitigación: no dejar encendido innecesariamente.

### 5. Sensible a vibraciones
Motores potentes confunden al gyro. Mitigación: amortiguación, alejar hub de motores.

## Programa completo de inicialización

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Stop, Color, Button
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

hub = PrimeHub()
hub.imu.settings(angular_velocity_threshold=5, acceleration_threshold=50,
                  heading_correction=358)  # MEDIR
hub.light.on(Color.RED)
while not hub.imu.ready():
    wait(100)
hub.light.on(Color.GREEN)

motor_izq = Motor(Port.A, Direction.COUNTERCLOCKWISE)
motor_der = Motor(Port.B)
robot = DriveBase(motor_izq, motor_der, wheel_diameter=56, axle_track=112)
robot.use_gyro(True)
robot.settings(straight_speed=200, straight_acceleration=150,
               turn_rate=120, turn_acceleration=80)

print("Listo. Centro para iniciar.")
while Button.CENTER not in hub.buttons.pressed():
    wait(50)
wait(500)
hub.imu.reset_heading(0)
cronometro = StopWatch()
```

## Resumen

| Práctica | Importancia |
|----------|-------------|
| No mover al encender | CRÍTICA |
| Esperar `hub.imu.ready()` | CRÍTICA |
| Medir heading_correction | ALTA |
| Ajustar thresholds competencia | ALTA |
| Recalibrar en momentos quietos | MEDIA |
| Montar hub horizontal | MEDIA |
| No superar 80% velocidad máxima | ALTA |
| Resetear heading al inicio | ALTA |
