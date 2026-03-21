# ============================================================================
# Test basico de motores y sensores - WRO Junior 2026
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 4.6
# Fecha:       2026-03-21 20:00
# Rev:         v1
# Hardware:    Spike Prime, 2 motores grandes, 2 medianos, sensor color
#
# DESCRIPCION:
#   Test completo: traccion, brazo, garra, sensor color, sensor distancia.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()
print("=== TEST COMPLETO JUNIOR ===")

# --- Traccion ---
motor_izq = Motor(Port.A, Direction.COUNTERCLOCKWISE)
motor_der = Motor(Port.B)
robot = DriveBase(motor_izq, motor_der, wheel_diameter=56, axle_track=112)

print("1. Avanzar 200mm...")
robot.straight(200)
wait(500)
print("2. Retroceder 200mm...")
robot.straight(-200)
wait(500)
print("3. Girar 90 derecha...")
robot.turn(90)
wait(500)
print("4. Girar 90 izquierda...")
robot.turn(-90)
wait(500)

# --- Brazo ---
print("5. Motor brazo (Puerto C)...")
try:
    brazo = Motor(Port.C)
    brazo.run_angle(300, -180, then=Stop.HOLD)
    wait(500)
    brazo.run_angle(300, 180, then=Stop.HOLD)
    print("   Brazo OK")
except:
    print("   Brazo no detectado en Puerto C")

# --- Garra ---
print("6. Motor garra (Puerto D)...")
try:
    garra = Motor(Port.D)
    garra.run_angle(400, 90, then=Stop.HOLD)
    wait(500)
    garra.run_angle(400, -90, then=Stop.HOLD)
    print("   Garra OK")
except:
    print("   Garra no detectada en Puerto D")

# --- Sensor color ---
print("7. Sensor color (Puerto E)...")
try:
    sc = ColorSensor(Port.E)
    color = sc.color()
    hsv = sc.hsv()
    print("   Color: " + str(color))
    print("   HSV: H=" + str(hsv.h) + " S=" + str(hsv.s) + " V=" + str(hsv.v))
except:
    print("   Sensor no detectado en Puerto E")

# --- Sensor distancia (opcional) ---
print("8. Sensor distancia (Puerto F)...")
try:
    from pybricks.pupdevices import UltrasonicSensor
    sd = UltrasonicSensor(Port.F)
    dist = sd.distance()
    print("   Distancia: " + str(dist) + " mm")
except:
    print("   No conectado (opcional)")

print("")
print("=== TEST COMPLETO ===")
hub.speaker.beep(frequency=1000, duration=500)
