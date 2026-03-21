# ============================================================================
# Calibracion de sensor de color - WRO Junior 2026
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 4.6
# Fecha:       2026-03-21 20:00
# Rev:         v1
# Hardware:    Spike Prime, sensor de color
#
# DESCRIPCION:
#   Script para calibrar el sensor de color sobre el mat WRO.
#   Muestra color detectado y valores HSV para cada artefacto.
#   Los 5 colores posibles: azul, rojo, verde, negro, amarillo.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.pupdevices import ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait

hub = PrimeHub()
sensor = ColorSensor(Port.E)  # Ajustar puerto

print("=== CALIBRACION SENSOR DE COLOR ===")
print("Posicionar sensor sobre cada artefacto.")
print("Presionar boton central cuando este listo.")
print("")

colores = ["AZUL", "ROJO", "VERDE", "NEGRO", "AMARILLO"]

resultados = {}
for nombre in colores:
    print("--- Artefacto " + nombre + " ---")
    while not hub.buttons.pressed():
        wait(50)
    while hub.buttons.pressed():
        wait(50)

    color = sensor.color()
    hsv = sensor.hsv()
    reflection = sensor.reflection()

    resultados[nombre] = {'h': hsv.h, 's': hsv.s, 'v': hsv.v}
    print("  Color: " + str(color))
    print("  H=" + str(hsv.h) + " S=" + str(hsv.s) + " V=" + str(hsv.v))
    print("  Reflexion: " + str(reflection) + "%")
    print("")

print("=== RESUMEN ===")
for nombre, vals in resultados.items():
    print(nombre + ": H=" + str(vals['h']) + " S=" + str(vals['s']) + " V=" + str(vals['v']))

print("")
print("Usar estos valores para ajustar detectar_color() en base_config.py")
