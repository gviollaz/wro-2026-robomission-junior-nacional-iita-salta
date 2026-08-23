# ============================================================================
# Diagnostico: distinguir un objeto NEGRO de NO HABER NADA
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5
# Fecha:       2026-08-23 16:46
# Rev:         v1
# Hardware:    LEGO SPIKE Prime + sensor de color estandar (Pybricks)
#
# DESCRIPCION:
#   Mide las dos situaciones (objeto negro apoyado / sensor al aire) por cuatro
#   caminos distintos y dice cual de los cuatro las separa mejor CON este
#   mecanismo y esta luz. Reemplaza la especulacion por un numero medido.
#
# ============================================================================
#
#  POR QUE ESTE PROGRAMA EXISTE
#  ----------------------------
#  Un objeto negro cerca y el aire lejos devuelven casi lo mismo, por la misma
#  razon: vuelve poca luz. En la tabla calibrada estan a 7 unidades de
#  distancia, con un ruido de ~2.7: el margen es de 1.3 ruidos, el peor de los
#  15 pares de la tabla. Es el unico par que ninguna perilla arregla.
#
#  Hay cuatro caminos posibles y NO se sabe cual gana sin medirlo:
#    1. brillo (v)      - el eje que ya se usa
#    2. reflexion       - la medida de luz reflejada, calibrada por el firmware
#    3. luz ambiente    - un objeto a 10 mm TAPA la luz del salon; el aire no
#    4. estabilidad     - lejos casi todo es ruido; sobre el negro la lectura
#                         es chica pero repetible
#
#  Y hay una quinta que no se mide con software: ACERCAR EL SENSOR. La luz que
#  vuelve de una superficie cae con el cuadrado de la distancia, asi que a la
#  mitad de distancia el negro cuadruplica su brillo mientras el aire sigue en
#  cero. Si este programa dice que ningun eje separa bien, ese es el camino.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.tools import wait

from colores import sensor

hub = PrimeHub()

MUESTRAS = 30
ESPERA_MS = 20


def esperar_boton():
    while not hub.buttons.pressed():
        wait(50)
    while hub.buttons.pressed():
        wait(50)


def medir_situacion(titulo, instruccion):
    print("")
    print("===", titulo, "===")
    print(" ", instruccion)
    print("  apretar boton cuando este listo")
    esperar_boton()

    brillo = []
    reflexion = []
    ambiente = []
    for _ in range(MUESTRAS):
        brillo.append(sensor.hsv().v)
        reflexion.append(sensor.reflection())
        ambiente.append(sensor.ambient())
        wait(ESPERA_MS)
    print("  listo")
    return {"brillo": brillo, "reflexion": reflexion, "ambiente": ambiente}


def promedio(xs):
    return sum(xs) / len(xs)


def rms(xs):
    m = promedio(xs)
    return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5


def separacion(a, b):
    """Cuantos ruidos de distancia hay entre las dos situaciones.

    Es la unica cifra que importa: una diferencia grande entre promedios no
    sirve de nada si el ruido de cada lado es igual de grande.
    """
    ruido = (rms(a) + rms(b)) / 2
    if ruido < 0.001:
        ruido = 0.001
    return abs(promedio(a) - promedio(b)) / ruido


def main():
    print("=== NEGRO vs NADA - diagnostico de banco ===")
    print("Se mide con el MECANISMO ARMADO y la luz de siempre.")

    negro = medir_situacion(
        "OBJETO NEGRO",
        "apoyar el artefacto negro como queda cuando el robot lo captura")
    nada = medir_situacion(
        "NADA",
        "sacar el objeto: el sensor al aire, como cuando no llego bien")

    print("")
    print("=== RESULTADO ===")
    print("%-12s %8s %8s %8s %8s   %s" %
          ("eje", "negro", "ruido", "nada", "ruido", "separacion"))
    ranking = []
    for eje in ("brillo", "reflexion", "ambiente"):
        s = separacion(negro[eje], nada[eje])
        ranking.append((s, eje))
        print("%-12s %8.1f %8.1f %8.1f %8.1f   %6.1f ruidos" %
              (eje, promedio(negro[eje]), rms(negro[eje]),
               promedio(nada[eje]), rms(nada[eje]), s))

    # el cuarto camino: la estabilidad misma como senial
    r_negro = rms(negro["brillo"])
    r_nada = rms(nada["brillo"])
    print("")
    print("estabilidad del brillo: negro", round(r_negro, 2),
          "| nada", round(r_nada, 2))
    if r_nada > 2 * r_negro:
        print("  -> al aire la lectura TIEMBLA mucho mas. Sirve como senial:")
        print("     si el ruido de N lecturas es alto, no hay objeto.")
    else:
        print("  -> la estabilidad no separa: este camino no sirve aca.")

    ranking.sort()
    mejor = ranking[-1]
    print("")
    print("MEJOR EJE:", mejor[1], "con", round(mejor[0], 1), "ruidos de separacion")
    if mejor[0] < 3:
        print("  NINGUN eje separa bien (hace falta 3 o mas).")
        print("  El camino que queda es mecanico: ACERCAR EL SENSOR al objeto.")
        print("  A la mitad de distancia el negro cuadruplica su brillo y el")
        print("  aire sigue en cero. Volver a correr este programa despues.")
    elif mejor[1] != "brillo":
        print("  Conviene agregar este eje a la decision de colores.py:")
        print("  hoy solo se usa el brillo, y este eje separa mejor.")
    else:
        print("  El brillo alcanza. No hace falta tocar nada mas.")


main()
