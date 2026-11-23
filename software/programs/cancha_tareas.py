# ============================================================================
# Prueba de cancha CON MULTITAREA: un vigilante lee, otras tareas reaccionan
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5.5
# Fecha:       2026-11-23 21:45
# Rev:         v1
# Hardware:    LEGO SPIKE Prime + sensor de color estandar (el puerto lo
#              define colores.py; en el robot, F)
#
# DESCRIPCION:
#   Lo mismo que cancha.py, pero armado como lo usaria una mision con tareas
#   en paralelo: UNA tarea es la duena del sensor (vigilar) y las demas solo
#   le preguntan a visto(). Sirve para probar en banco que el patron anda y
#   para medir el ritmo real de lectura con varias tareas corriendo.
#
# ============================================================================
#
#  QUE CORRE EN PARALELO
#  ---------------------
#    1. vigilar(PERFIL)  lee el sensor sin parar (es de colores.py)
#    2. cantar()         cuando cambia lo visto: letra en pantalla + sonido
#    3. informar()       cada 2 s imprime el ritmo del vigilante
#  Las tres se turnan: cada una cede el lugar en sus await. En cancha.py el
#  sonido frena la lectura mientras suena; aca el vigilante sigue leyendo,
#  porque el sonido se espera con await.
#
#  QUE MIRAR
#  ---------
#  1. Que cada color cante igual que en cancha.py.
#  2. El ritmo del vigilante (lecturas por segundo). [A VERIFICAR EN BANCO]
#     Tendria que andar cerca de 50: una lectura cada ~20 ms, que es la espera
#     de medir() y el ritmo al que el sensor entrega datos nuevos (medido el
#     2026-08-23, ver colores.py). Si con las otras tareas baja mucho, alguna
#     tarda en ceder el lugar.
#  3. Que al presentar y sacar una pieza la letra cambie enseguida.
#
#  Se corta con el boton central.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.tools import wait, multitask, run_task

from colores import vigilar, visto, informe_vigia, nombre_de, DUDA

hub = PrimeHub()

# Que conjunto de colores.py se vigila: "naba" o "rva". None = "naba".
PERFIL = None

# letra y sonido por codigo, igual que cancha.py (codigos de CODIGOS)
LETRAS = {0: "-", 1: "A", 2: "B", 3: "Z", 4: "N", 5: "R", 6: "V", DUDA: "?"}
SONIDOS = {
    2: ((1500, 60), (1500, 60)),          # blanco: doble muy agudo
    1: ((1200, 120),),                    # amarillo: agudo
    5: ((1000, 90), (1000, 90)),          # rojo: doble agudo
    6: ((700, 120),),                     # verde: medio
    3: ((450, 140),),                     # azul: grave
    4: ((250, 90), (250, 90)),            # negro: doble muy grave
    0: ((160, 40),),                      # nada: tic corto
    DUDA: ((520, 70), (390, 70)),         # duda: dos tonos que no combinan
}


async def cantar():
    """Muestra y canta cada vez que cambia lo que vio el vigilante."""
    anterior = None
    while True:
        codigo = visto(PERFIL)            # no toca el sensor: lo lee vigilar
        if codigo != anterior:
            hub.display.char(LETRAS.get(codigo, "?"))
            print(nombre_de(codigo))
            anterior = codigo
            for frecuencia, duracion in SONIDOS.get(codigo, SONIDOS[DUDA]):
                await hub.speaker.beep(frecuencia, duracion)
        await wait(20)


async def informar():
    """Cada 2 segundos, cuanto esta leyendo el vigilante."""
    while True:
        await wait(2000)
        informe_vigia(PERFIL)


async def main():
    print("=== PRUEBA DE CANCHA CON TAREAS ===")
    print("conjunto:", PERFIL if PERFIL else "el por defecto (naba)")
    print("B=blanco A=amarillo R=rojo V=verde Z=azul N=negro -=nada ?=duda")
    # Sin race: las tres corren hasta que se aprieta el boton central.
    # (No escribir race=False: ver MULTITAREA en colores.py, punto 5.)
    await multitask(vigilar(PERFIL), cantar(), informar())


run_task(main())
