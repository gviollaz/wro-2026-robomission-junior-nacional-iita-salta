# ============================================================================
# Calibrador de la tabla de colores  --  WRO Junior 2026
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5
# Fecha:       2026-08-23 16:46
# Rev:         v2
# Hardware:    LEGO SPIKE Prime + sensor de color estandar (Pybricks)
#
# DESCRIPCION:
#   Mide el centro y el ruido de cada color y emite la fila lista para pegar en
#   la tabla COLORES de colores.py. Mide sobre VARIAS presentaciones del objeto,
#   no sobre una sola, porque lo que mueve la lectura en cancha es volver a
#   apoyar la pieza, no el temblor del sensor quieto.
#
# ============================================================================
#
#  COMO SE USA
#  -----------
#  1. Armar el mecanismo COMPLETO. Se calibra con el robot como va a competir:
#     misma altura de sensor, misma sombra, misma luz. Calibrar el sensor suelto
#     y despues montarlo tira toda esta medicion a la basura.
#  2. Correr este programa.
#  3. Para cada color: apoyar el objeto, apretar una FLECHA (izq o der), sacarlo,
#     volver a apoyarlo, apretar de nuevo. Cuatro veces por color.
#     LA PANTALLA DEL HUB GUIA: muestra el numero de toma que espera (1,2,3,4),
#     un guion mientras mide (no mover) y una K cuando termino ese color.
#     Suena un pitido al empezar cada toma y otro mas agudo al terminarla.
#  4. Copiar la fila que imprime y pegarla en COLORES de colores.py.
#  5. Al final correr chequear() y mirar los avisos.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.parameters import Button
from pybricks.tools import wait

# Se importa de colores.py para que la matematica viva en UN solo lugar:
# si el cono cambia alla, la calibracion cambia con el.
from colores import sensor, _xyz, COLORES, RUIDO_EN_RADIOS, chequear

hub = PrimeHub()

LETRAS = {"amarillo": "A", "verde": "V", "azul": "Z",
          "negro": "N", "rojo": "R", "nada": "-"}

PRESENTACIONES = 4    # cuantas veces se apoya el objeto de nuevo
MUESTRAS = 10         # cuantas lecturas por presentacion
ESPERA_MS = 25        # [MEDIDO 2026-08-23] el sensor entrega un dato
                      # nuevo cada 20 ms en promedio; con 12 ms el 57% de las
                      # lecturas salian repetidas y el ruido medido era falso.


def esperar_boton(marca="?"):
    """Espera a que se apriete y se suelte una FLECHA (izquierda o derecha).

    Muestra `marca` en la pantalla del hub mientras espera. Esa senial es
    imprescindible cuando el programa se lanza desde la PC con pybricksdev:
    los mensajes de print() van a la terminal de la PC, NO a los ojos de quien
    esta parado al lado del robot poniendo las piezas. Sin algo en la pantalla,
    el robot parece colgado.

    [IA 2026-08-23] NO se puede usar el boton central: la documentacion de
    Pybricks dice que "normally, the center button is used to stop a running
    script". Con el central el programa se corta en vez de avanzar.
    """
    hub.display.char(marca)
    flechas = (Button.LEFT, Button.RIGHT)
    while True:
        apretados = hub.buttons.pressed()
        if any(b in apretados for b in flechas):
            break
        wait(50)
    while hub.buttons.pressed():
        wait(50)
    hub.speaker.beep(600, 80)
    hub.display.char("-")          # midiendo: no mover


def tomar_muestras(n):
    """Devuelve (lista de puntos xyz, cuantas lecturas salieron repetidas).

    Las repetidas importan: hsv() no dispara una medicion nueva, devuelve el
    ultimo dato que llego del sensor. Si la espera es mas corta que el refresco
    real, se lee el MISMO valor varias veces y el promedio no limpia nada; peor
    todavia, el ruido medido sale artificialmente chico y los radios salen
    apretados. [IA 2026-08-23] Pybricks no documenta cada cuanto se actualiza,
    por eso se mide en vez de suponerlo.
    """
    puntos = []
    repetidas = 0
    anterior = None
    for _ in range(n):
        m = sensor.hsv()
        crudo = (m.h, m.s, m.v)
        if crudo == anterior:
            repetidas += 1
        anterior = crudo
        puntos.append(_xyz(m.h, m.s, m.v))
        wait(ESPERA_MS)
    return puntos, repetidas


def centro_de(puntos):
    sx = sy = sz = 0
    for p in puntos:
        sx += p[0]; sy += p[1]; sz += p[2]
    n = len(puntos)
    return sx / n, sy / n, sz / n


def ruido_rms(puntos, centro):
    """Ruido = RMS de la distancia al centro.

    Se usa RMS y no el MAXIMO (que era lo que hacia el calibrador viejo). El
    maximo es un valor extremo: salta con una sola lectura mala y crece con la
    cantidad de muestras. El RMS es la desviacion tipica real y no depende de
    cuantas muestras se tomen. [IA 2026-08-23] Medido en testing/test_colores.py:
    con 8 muestras el maximo vale 1.5 veces el RMS.
    """
    s = 0.0
    for p in puntos:
        s += ((p[0]-centro[0])**2 + (p[1]-centro[1])**2 + (p[2]-centro[2])**2)
    return (s / len(puntos)) ** 0.5


def calibrar_un_color(codigo, nombre):
    """Mide un color sobre varias presentaciones. Devuelve la fila para pegar."""
    print("")
    print("=== ", nombre.upper(), " (codigo", codigo, ") ===")
    if codigo == 0:
        print("  Para 'nada': dejar el sensor SIN objeto adelante,")
        print("  apuntando a donde apunta cuando no llego bien.")
    else:
        print("  Apoyar el objeto como queda cuando el robot lo captura.")

    todos = []
    centros = []
    repetidas = 0
    for k in range(PRESENTACIONES):
        print("  presentacion", k + 1, "de", PRESENTACIONES, "- apretar una FLECHA")
        # en la primera toma la pantalla dice QUE color poner; despues, que
        # numero de toma se espera
        if k == 0:
            esperar_boton(LETRAS.get(nombre, "?"))
        else:
            esperar_boton(str(k + 1))
        puntos, rep = tomar_muestras(MUESTRAS)
        hub.speaker.beep(1000, 60)   # tomada
        repetidas += rep
        todos.extend(puntos)
        centros.append(centro_de(puntos))
        c = centros[-1]
        print("    x=", round(c[0]), " y=", round(c[1]), " z=", round(c[2]))
        if k < PRESENTACIONES - 1:
            print("    sacar el objeto y volver a apoyarlo")

    centro = centro_de(todos)
    ruido_total = ruido_rms(todos, centro)          # incluye el reposicionamiento
    ruido_quieto = ruido_rms(centros, centro_de(centros))  # solo entre centros

    radio = RUIDO_EN_RADIOS * ruido_total
    if radio < 8:
        radio = 8
    radio = round(radio)

    print("  ---")
    print("  ruido total (lo que importa): ", round(ruido_total, 1))
    print("  ruido entre presentaciones:   ", round(ruido_quieto, 1))
    if ruido_quieto > 0.6 * ruido_total:
        print("  >> la mayor parte del ruido es REPOSICIONAR, no el sensor.")
        print("     Se gana mas mejorando el tope mecanico que promediando mas.")
    total_lecturas = PRESENTACIONES * MUESTRAS
    # [IA 2026-08-23] Este numero es informativo, NO un problema. Una version
    # anterior avisaba "el ruido sale falso" cuando habia muchas repetidas,
    # razonando que la espera era mas corta que el refresco del sensor. Es una
    # inferencia invalida: con el objeto quieto y una salida cuantizada de 0 a
    # 100, dos lecturas NUEVAS pueden dar exactamente lo mismo. El aviso saltaba
    # en el caso bueno, que es la mejor forma de que nadie lea los avisos.
    print("  lecturas repetidas:", repetidas, "de", total_lecturas,
          "(normal con el objeto quieto)")

    # Lo que SI es un problema y no se veia: el sensor saturado.
    if centro[2] >= 95:
        print("  >> PELIGRO: brillo", round(centro[2]), "sobre un maximo de 100.")
        print("     El sensor esta al TOPE. Si la pieza se acerca un poco mas,")
        print("     la lectura no puede subir y el tono se distorsiona porque")
        print("     los canales RGB tambien se clipean. Alejar el sensor y")
        print("     recalibrar TODOS los colores, no solo este.")

    hub.speaker.beep(1400, 150)      # color terminado
    hub.display.char("K")
    fila = ("    (" + str(codigo) + ', "' + nombre + '", ' +
            str(round(centro[0])) + ", " + str(round(centro[1])) + ", " +
            str(round(centro[2])) + ", " + str(radio) + "),")
    print("  PEGAR ESTA LINEA EN COLORES:")
    print(fila)
    return fila


def main():
    print("=== CALIBRACION DE COLORES ===")
    print("Tabla que hay ahora:")
    chequear()

    filas = []
    for codigo, nombre, _x, _y, _z, _r in COLORES:
        filas.append(calibrar_un_color(codigo, nombre))

    print("")
    print("=== TABLA COMPLETA - reemplazar COLORES en colores.py ===")
    print("COLORES = (")
    for f in filas:
        print(f)
    print(")")
    print("")
    print("Despues de pegarla, volver a correr este programa y mirar los avisos")
    print("de chequear() al principio.")


main()
