# ============================================================================
# Calibracion del brazo elevador - WRO Junior 2026
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 4.6
# Fecha:       2026-03-21 20:00
# Rev:         v1
# Hardware:    Spike Prime, motor mediano en Puerto C
#
# DESCRIPCION:
#   Script interactivo para encontrar los angulos correctos
#   del brazo elevador. Sube y baja en pasos de 30 grados.
#   Anotar los valores para usar en base_config.py.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait

hub = PrimeHub()
brazo = Motor(Port.C)

print("=== CALIBRACION BRAZO ELEVADOR ===")
print("Boton central = subir 30 grados")
print("Esperar 3 seg sin tocar = bajar 30 grados")
print("Mantener boton 2 seg = salir")
print("")

angulo_total = 0

while True:
    print("Angulo actual: " + str(angulo_total))

    # Esperar boton o timeout
    espera = 0
    while not hub.buttons.pressed() and espera < 3000:
        wait(50)
        espera += 50

    if hub.buttons.pressed():
        # Verificar si es press largo (salir)
        hold = 0
        while hub.buttons.pressed() and hold < 2000:
            wait(50)
            hold += 50
        if hold >= 2000:
            print("Saliendo. Angulo final: " + str(angulo_total))
            break
        # Press corto = subir
        brazo.run_angle(200, -30, then=Stop.HOLD)
        angulo_total -= 30
        print("  SUBIR -> " + str(angulo_total))
    else:
        # Timeout = bajar
        brazo.run_angle(200, 30, then=Stop.HOLD)
        angulo_total += 30
        print("  BAJAR -> " + str(angulo_total))

print("")
print("Usar este valor en base_config.py:")
print("BRAZO_ARRIBA = " + str(angulo_total))
