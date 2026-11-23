# ============================================================================
# Prueba en vivo del detector de color - muestra una letra por color
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5
# Fecha:       2026-08-23 17:05
# Rev:         v1
# Hardware:    LEGO SPIKE Prime + sensor de color estandar en el PUERTO B
#
# DESCRIPCION:
#   Corre en un lazo infinito: lee el sensor y muestra en la pantalla del hub
#   una letra distinta por cada color, un guion cuando no hay nada y un signo
#   de pregunta cuando ve algo pero no lo reconoce. Sirve para pasear el robot
#   por la cancha e ir viendo que detecta.
#
# ============================================================================
#
#  COMO SE USA
#  -----------
#  Subir al hub ESTE archivo junto con colores.py (los dos en la raiz del
#  proyecto de Pybricks Code) y ejecutar este. Se corta con el boton de stop.
#
#  LO QUE MUESTRA LA PANTALLA
#  --------------------------
#      A = amarillo        N = negro
#      V = verde           R = rojo
#      Z = aZul            - = nada (no hay objeto adelante)
#                          ? = duda (hay algo pero no lo reconoce)
#
#  El guion y el signo de pregunta NO son lo mismo, y esa diferencia es el
#  punto de toda la prueba:
#      "-"  el sensor esta lejos de todo. El robot tendria que AVANZAR.
#      "?"  hay algo adelante que no cae dentro de ningun color conocido.
#           El robot tendria que RELEER o reacomodarse. Si aparece seguido
#           sobre un objeto que si esta, falta calibrar ese color o el radio
#           quedo chico.
#
#  En la consola, ademas, cada vez que CAMBIA lo detectado imprime por que:
#  quien gano, contra quien, y por cuanta diferencia. Si gana por poco, ese es
#  el par que hay que separar (o donde subir la VENTAJA en colores.py).
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.tools import wait

from colores import detectar_color, detectar_estable, nombre_de, explicar, DUDA

hub = PrimeHub()

# Una letra por codigo. Los codigos salen de la tabla COLORES de colores.py.
LETRAS = {
    0: "-",        # nada
    1: "A",        # amarillo
    2: "V",        # verde
    3: "Z",        # azul
    4: "N",        # negro
    5: "R",        # rojo
    DUDA: "?",     # vio algo pero no lo reconoce
}

# True  = usa detectar_estable (2 de 3 lecturas iguales). Es lo que va a usar
#         la mision: mas confiable, un poco mas lento.
# False = usa detectar_color (una lectura). Reacciona mas rapido y deja ver el
#         parpadeo real del sensor, que es lo que conviene mirar al calibrar.
ANTIRREBOTE = True

MUESTRAS = 3          # lecturas que promedia cada deteccion
ESPERA_MS = 100       # pausa entre vueltas del lazo


def main():
    print("=== PRUEBA DE COLORES EN VIVO ===")
    print("A=amarillo  V=verde  Z=azul  N=negro  R=rojo  -=nada  ?=duda")
    print("modo:", "antirrebote (2 de 3)" if ANTIRREBOTE else "lectura directa")
    print("cortar con el boton de stop")
    print("")

    anterior = None
    while True:
        if ANTIRREBOTE:
            codigo = detectar_estable(MUESTRAS)
        else:
            codigo = detectar_color(MUESTRAS)

        hub.display.char(LETRAS.get(codigo, "?"))

        # Solo se imprime cuando cambia: si imprimiera siempre, la consola se
        # llena y no se ve el momento en que cambio.
        if codigo != anterior:
            print(">>", nombre_de(codigo), "(codigo", str(codigo) + ")")
            # [IA 2026-08-23] Con ANTIRREBOTE, explicar() describe la ULTIMA de
            # las 2 o 3 lecturas del voto, que no siempre es la que gano. Para
            # mirar el duelo exacto de una lectura, poner ANTIRREBOTE = False.
            explicar()
            anterior = codigo

        wait(ESPERA_MS)


main()
