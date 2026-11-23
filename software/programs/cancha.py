# ============================================================================
# Prueba de cancha: canta y muestra el color detectado, sin parar
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5 (v1) / Claude Opus 5.5 (v2)
# Fecha:       2026-11-23 21:40
# Rev:         v2
# Hardware:    LEGO SPIKE Prime + sensor de color estandar (puerto: el que
#              diga colores.py; en el robot, F)
#
# DESCRIPCION:
#   Lazo infinito para probar el detector sobre la cancha real: muestra una
#   letra por color en la pantalla del hub y toca un sonido distinto cada vez
#   que el color cambia. Sirve para pasear el robot por el tapete y escuchar
#   que ve, sin PC y sin mirar la pantalla.
#
# ============================================================================
#
#  PARA QUE SIRVE
#  --------------
#  El hub no habla: Pybricks no tiene texto a voz. Pero para cancha un sonido
#  por color es mejor que una voz, porque se reconoce mas rapido y no tapa lo
#  que esta diciendo el equipo. La regla es: MAS AGUDO = MAS CLARO.
#
#      B  blanco     dos pitidos muy agudos
#      A  amarillo   un pitido muy agudo
#      R  rojo       dos pitidos agudos
#      V  verde      un pitido medio
#      Z  azul       un pitido grave
#      N  negro      dos pitidos muy graves
#      -  nada       un tic corto y bajito (no hay objeto adelante)
#      ?  duda       dos tonos que no combinan: vio algo y no lo reconoce
#
#  SOLO SUENA CUANDO CAMBIA. Si sonara todo el tiempo, en cinco minutos nadie
#  lo escucharia mas, que es lo mismo que no tener sonido.
#
#  COMO SE USA
#  -----------
#  Este archivo va a la raiz del proyecto de Pybricks Code, al lado de
#  colores.py. Se arranca y se pasea el robot. Se corta con el boton central.
#
#  QUE MIRAR
#  ---------
#  1. Que cada color suene igual siempre, en todo el tapete. Si un color canta
#     distinto segun donde este el robot, la luz del lugar lo esta moviendo.
#  2. Cuantas veces canta "duda". Duda no es un error: es el robot avisando que
#     no esta seguro. Un color equivocado cantado con confianza es MUCHO peor.
#  3. Si canta "negro" donde no hay nada negro. Ese es el sintoma de que la
#     pieza se esta leyendo demasiado oscura, o sea demasiado lejos.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.tools import wait

from colores import detectar_estable, nombre_de, DUDA

hub = PrimeHub()

# letra que se muestra y sonido que se toca, por codigo de color
# (frecuencia en Hz, duracion en ms) repetido las veces que haga falta
# [IA 2026-11-23] Codigos segun CODIGOS de colores.py: el 2 es BLANCO desde
# que el robot usa la tabla de negro/azul/blanco/amarillo; verde paso al 6.
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

MUESTRAS = 3          # lecturas que promedia cada deteccion
ESPERA_MS = 60        # pausa entre vueltas del lazo

# Que conjunto de colores.py se escucha: "naba" o "rva". None = "naba".
PERFIL = None


def cantar(codigo):
    for frecuencia, duracion in SONIDOS.get(codigo, ((520, 70), (390, 70))):
        hub.speaker.beep(frecuencia, duracion)


def main():
    print("=== PRUEBA DE CANCHA ===")
    print("B=blanco A=amarillo R=rojo V=verde Z=azul N=negro -=nada ?=duda")
    print("conjunto:", PERFIL if PERFIL else "el por defecto (naba)")
    print("Se corta con el boton central.")

    anterior = None
    while True:
        codigo = detectar_estable(MUESTRAS, PERFIL)
        hub.display.char(LETRAS.get(codigo, "?"))
        if codigo != anterior:
            cantar(codigo)
            print(nombre_de(codigo))
            anterior = codigo
        wait(ESPERA_MS)


main()
