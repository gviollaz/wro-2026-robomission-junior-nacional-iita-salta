# ============================================================================
# Configuracion base del robot - WRO Junior 2026 "Heritage Heroes"
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 4.6
# Fecha:       2026-03-21 20:00
# Rev:         v1
# Hardware:    Spike Prime, 2 motores grandes, 2 motores medianos,
#              sensor color, sensor distancia
#
# DESCRIPCION:
#   Configuracion base del robot: hub, motores, sensores, DriveBase
#   y funciones auxiliares. Importar desde programas de mision.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Stop, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

# --- HUB ---
hub = PrimeHub()

# --- MOTORES ---
motor_izq = Motor(Port.A, Direction.COUNTERCLOCKWISE)
motor_der = Motor(Port.B)
motor_brazo = Motor(Port.C)
motor_garra = Motor(Port.D)

# --- SENSORES ---
sensor_color = ColorSensor(Port.E)
# Descomentar si se usa sensor de distancia:
# sensor_dist = UltrasonicSensor(Port.F)

# --- DRIVEBASE ---
# MEDIR CON REGLA Y AJUSTAR ESTOS VALORES
WHEEL_DIAMETER = 56    # mm
AXLE_TRACK = 112       # mm

robot = DriveBase(motor_izq, motor_der,
    wheel_diameter=WHEEL_DIAMETER,
    axle_track=AXLE_TRACK)

# --- VELOCIDADES ---
def velocidad_normal():
    robot.settings(
        straight_speed=250,
        straight_acceleration=150,
        turn_rate=120,
        turn_acceleration=80
    )

def velocidad_lenta():
    robot.settings(
        straight_speed=120,
        straight_acceleration=60,
        turn_rate=60,
        turn_acceleration=40
    )

def velocidad_rapida():
    robot.settings(
        straight_speed=400,
        straight_acceleration=200,
        turn_rate=180,
        turn_acceleration=100
    )

# --- BRAZO ---
BRAZO_ARRIBA = -180    # grados (ajustar)
BRAZO_ABAJO = 180      # grados (ajustar)

def brazo_subir():
    motor_brazo.run_angle(300, BRAZO_ARRIBA, then=Stop.HOLD)

def brazo_bajar():
    motor_brazo.run_angle(300, BRAZO_ABAJO, then=Stop.HOLD)

# --- GARRA ---
GARRA_ABRIR = 90       # grados (ajustar)
GARRA_CERRAR = -90     # grados (ajustar)

def garra_abrir():
    motor_garra.run_angle(400, GARRA_ABRIR, then=Stop.HOLD)

def garra_cerrar():
    motor_garra.run_angle(400, GARRA_CERRAR, then=Stop.HOLD)

# --- DETECCION DE COLOR AVANZADA ---
def detectar_color():
    """Detectar color usando HSV para mayor precision."""
    wait(200)  # estabilizar lectura
    hsv = sensor_color.hsv()
    h, s, v = hsv.h, hsv.s, hsv.v

    if v < 15:
        return Color.BLACK
    elif s < 20 and v > 60:
        return Color.WHITE
    elif h < 30 or h > 340:
        return Color.RED
    elif 30 <= h < 70:
        return Color.YELLOW
    elif 70 <= h < 160:
        return Color.GREEN
    elif 160 <= h < 260:
        return Color.BLUE

    # Fallback al detector estandar
    return sensor_color.color()

# --- CRONOMETRO ---
cronometro = StopWatch()

def tiempo_restante(limite_ms=120000):
    """Retorna milisegundos restantes de la ronda (2 min)."""
    return limite_ms - cronometro.time()

def hay_tiempo(minimo_ms=5000):
    """True si queda al menos minimo_ms de tiempo."""
    return tiempo_restante() > minimo_ms

# Inicializar
velocidad_normal()
