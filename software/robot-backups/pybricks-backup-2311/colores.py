# ============================================================================
# Detector de color por minimos cuadrados con sensibilidad por color
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5
# Fecha:       2026-08-23 16:46
# Rev:         v2
# Hardware:    LEGO SPIKE Prime + sensor de color estandar (Pybricks)
#
# DESCRIPCION:
#   Clasifica un objeto por color comparando la lectura contra una tabla de
#   colores medidos, en el espacio "cono HSV". Agrega DOS perillas por color
#   para subir o bajar la sensibilidad de cada uno por separado.
#
# ============================================================================
#
#  QUE PERILLA TOCAR SEGUN EL SINTOMA
#  ----------------------------------
#     "el rojo me lo lee amarillo"        ->  VENTAJA["rojo"]      (por color)
#     "no lo ve, me dice duda seguido"    ->  radio de ese color   (por color)
#     "de cerca casi todo me da duda"     ->  TOLERANCIA_BRILLO    (global)
#     "de lejos el azul se vuelve negro"  ->  PESO_BRILLO          (global)
#     "ve un color donde no hay nada"     ->  bajar el radio, o subir V_MINIMO
#
#  Las dos primeras son POR COLOR y pelean contra cosas distintas: la VENTAJA
#  pelea contra los OTROS COLORES (decide quien gana el duelo) y el radio pelea
#  contra la DUDA (decide si se acepta al ganador). Son dos numeros y no uno a
#  proposito: si fuera uno solo, subirle la sensibilidad al rojo para ganarle al
#  amarillo lo volveria tambien mas permisivo, y fabricarias un falso positivo
#  mientras arreglas la confusion.
#
#  Las dos siguientes son GLOBALES y las dos tratan el mismo tema: que el brillo
#  cambia cuando el objeto esta a otra distancia, y eso NO significa que sea
#  otro color.
#
# ============================================================================
#
#  COMO SE USA DESDE BLOQUES (Pybricks Code)
#  -----------------------------------------
#  Este archivo es un programa de tipo Python, hermano del programa de bloques
#  (pestania "files", boton +). Desde los bloques se trae con la seccion
#  "External tasks":   from colores import detectar_estable
#  Restricciones reales de Pybricks, verificadas en su documentacion y su
#  codigo [IA 2026-08-23]:
#    - no existe "import *": se importa funcion por funcion;
#    - el nombre del archivo no puede llevar guion medio;
#    - importar EJECUTA lo que esta fuera de funciones (por eso el sensor se
#      crea aca abajo y un puerto mal puesto falla al arrancar, no en medio
#      de la ronda);
#    - si el programa de bloques usa multitarea, asume que lo importado es
#      async. Estas funciones son sincronicas. (pybricks/support issue #1635)
#
# ============================================================================

from pybricks.pupdevices import ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait
from umath import sin, cos, pi

# >>> EDITAR: puerto del sensor. Si esta mal, el import falla al arrancar. <<<
sensor = ColorSensor(Port.F)


# ---------------------------------------------------------------------------
# TABLA MEDIDA  --  la escribe calibrar.py. No editar a mano salvo el radio.
# ---------------------------------------------------------------------------
# (codigo, nombre, x, y, z, radio)
#
#   x, y, z = centro del color en el cono HSV (lo mide calibrar.py)
#   radio   = hasta que distancia del centro se sigue aceptando este color.
#             calibrar.py lo calcula como RUIDO_EN_RADIOS veces el ruido medido.
#
# [MEDIDO EN BANCO 2026-08-23 18:00] Tabla medida con calibrar.py v2 sobre el
# robot real (sensor en puerto B), 4 presentaciones por color, reapoyando la
# pieza entre una y otra. Ruido medido: 0.6 a 1.3 segun el color; ruido de
# "nada": 0.0 exacto, el sensor entrega 0 cuando no hay nada adelante.
# Todos los radios quedaron en el piso de 8 porque 3*ruido daba menos.
#
# ATENCION AL AMARILLO: se midio con brillo 99 sobre un maximo de 100, o sea
# con el sensor AL BORDE DE SATURAR. Si la pieza se acerca mas, la lectura no
# puede subir y el tono se ensucia porque los canales RGB tambien se clipean.
# La solucion es alejar el sensor y recalibrar los seis colores de nuevo.
#
# Comparada con la tabla anterior, el peor par de los 15 paso de 1.8 a 3.6
# ruidos de margen, y la separacion negro/nada de 7 a 14.
COLORES = (
    (1, "amarillo",  32,  28, 64, 8),
    (2, "blanco",    0,  0, 99, 8),
    (3, "azul",     -37, -26, 63, 8),
    (4, "negro",      -2,   -1, 28,  8),
    (0, "nada",       0,   0,  1,  8),
)

# ---------------------------------------------------------------------------
# PERILLA 1: VENTAJA  --  contra los OTROS COLORES
# ---------------------------------------------------------------------------
# Es un regalo de distancia en el duelo. NO cambia la distancia real, solo
# quien gana la comparacion.
#
#   0     = pelea de igual a igual (identico al detector anterior)
#   subir = ese color gana el duelo mas seguido
#
# Cuanto se mueve: la frontera entre dos colores se corre exactamente la MITAD
# de la diferencia de ventajas, y ese corrimiento NO depende de que tan lejos
# esten los centros. Darle +2 al rojo corre la frontera rojo/amarillo 1 unidad
# hacia el amarillo.
#
# Paso util: 2. Rango sano: -6 a +6. Correr chequear() despues de cada cambio.
# Preferir SUBIR el color que falla antes que BAJAR al vecino: bajar al vecino
# le saca territorio contra todos los demas, no solo contra el que te molesta.
VENTAJA = {
    "amarillo": 0,
    "blanco":    0,
    "azul":     0,
    # [MEDIDO EN BANCO 2026-08-23] El negro es un IMAN: en el cono, cualquier
    # color que se lee mas oscuro se desliza hacia el origen, que es donde vive
    # el negro. Medido con esta tabla y ventaja 0, un color se vuelve negro al
    # bajar a: amarillo 23%, verde 26%, azul 25%, rojo 21% de su brillo. Eso es
    # lo que pasa cada vez que una pieza entra o sale del campo del sensor.
    # Con -6 ninguno se vuelve negro ni bajando al 10%, y el negro DE VERDAD
    # sigue ganando entre el 60% y el 140% de su brillo. Con -9 el negro real
    # ya empieza a perder: -6 es el borde util.
    "negro":   -6,
    "nada":     0,
}

# ---------------------------------------------------------------------------
# PERILLAS GLOBALES
# ---------------------------------------------------------------------------
# GANANCIA multiplica el radio de TODOS los colores a la vez. Es la palanca de
# emergencia, no la sintonia fina: moverla deshace el trabajo de los radios.
# [IA 2026-08-23] Con GANANCIA=2.5 y radios de 3 ruidos, la burbuja de
# aceptacion mide 7.5 ruidos: a esa altura practicamente nunca contesta "nada".
# Bajarla a 1.0 o 1.5 esta por probar en banco con el mecanismo armado.
GANANCIA = 2.5

# Cuantos ruidos vale un radio. Lo usa chequear() para traducir radio -> ruido.
# Tiene que coincidir con el multiplicador que use calibrar.py.
RUIDO_EN_RADIOS = 3

# ---------------------------------------------------------------------------
# PERILLA 3: PESO_BRILLO  --  cuanto pesa el brillo en el duelo
# ---------------------------------------------------------------------------
# EL PROBLEMA QUE RESUELVE
# En el cono, los tres ejes son proporcionales al brillo. Entonces el MISMO
# objeto leido mas cerca (mas luz) o mas lejos (menos luz) NO se queda quieto:
# se corre sobre la recta que une el origen con su centro. Medido sobre esta
# misma tabla [IA 2026-08-23]: con 20% mas de brillo el amarillo ya se alejo 15
# unidades de su centro, y con 50% se alejo 37, mas que su limite de aceptacion.
# Si el brillo pesa igual que el color, ese corrimiento se cuenta como si fuera
# otro color: de cerca sale duda y de lejos el azul se vuelve negro.
#
# LA SOLUCION
# La diferencia entre la lectura y el centro se parte en dos pedazos:
#     error de BRILLO -> cuanto se corrio A LO LARGO de su recta
#                        (el objeto esta mas cerca o mas lejos que al calibrar)
#     error de COLOR  -> cuanto se corrio DE COSTADO, saliendo de la recta
#                        (esto si es genuinamente otro color)
# y en el duelo el brillo entra multiplicado por PESO_BRILLO:
#
#     puntaje = raiz( error_color^2 + (PESO_BRILLO * error_brillo)^2 ) - VENTAJA
#
#   1.0  = el brillo pesa igual que el color (el detector viejo, exacto)
#   0.2  = el brillo pesa la quinta parte  <- recomendado para arrancar
#   0.0  = el brillo no cuenta nada en el duelo
#
# POR QUE NO CERO. Con peso cero, dos colores que estan sobre la MISMA recta y
# solo se diferencian por brillo se vuelven indistinguibles. Pasa de verdad: el
# blanco del tapete y el negro son los dos casi sin color, o sea que sus rectas
# son casi la misma y solo cambia el brillo. Con un peso chico pero no nulo el
# detector degrada de a poco en vez de depender solo de la compuerta.
PESO_BRILLO = 0.2

# Cuanto puede cambiar el brillo respecto del calibrado sin que sea duda.
# 0.8 = el objeto puede verse hasta 80% mas brillante o mas apagado.
# Es la perilla que pide el sintoma "me dice duda casi siempre".
# [MEDIDO EN BANCO 2026-08-23] Con 0.5, en una validacion en vivo de 60 s
# hubo 21 dudas y 19 fueron POR BRILLO, con excesos de alrededor de 1.5 veces
# el limite. Con 0.8 esas entran.
# NO SUBIR ESTO SOLO. Aflojar la aceptacion no cambia quien GANA el duelo:
# convierte una duda (barata: se relee) en la respuesta que el duelo eligio. Y
# el duelo, con el brillo bajo, elige negro. Por eso este 0.8 va junto con la
# VENTAJA negativa del negro de mas arriba; sin ella, aflojar aca fabrica
# negros equivocados en vez de dudas.
TOLERANCIA_BRILLO = 0.8

# Debajo de este brillo se considera que no hay objeto adelante.
# [MEDIDO EN BANCO 2026-08-23] Con la tabla actual: "nada" da brillo 0 exacto,
# sin ninguna variacion en 40 lecturas, y el negro da 14. El limite no va en el
# punto medio (7) sino mas abajo, porque TOLERANCIA_BRILLO deja que el negro se
# lea hasta 50% mas apagado, o sea hasta 7: un limite en 7 le comeria el borde.
# Con 5 el negro conserva todo su rango y "nada" sigue estando a 5 de distancia
# con ruido cero.
V_MINIMO = 5

# Codigo que devuelven las funciones cuando NO se puede decidir.
# Es distinto de 0 (nada) a proposito: son dos situaciones con reacciones
# opuestas. Con 0 el robot tiene que AVANZAR (no hay objeto); con DUDA tiene
# que RELEER o reacomodarse (hay algo pero no se reconoce).
DUDA = -1

# Diagnostico del ultimo duelo, para explicar(). No tocar.
_ultimo = None


# ---------------------------------------------------------------------------
# MEDICION
# ---------------------------------------------------------------------------

def _xyz(h, s, v):
    """Pasa el HSV al cono: la croma queda pesada por el brillo.

    A oscuras el tono es puro ruido, y multiplicarlo por el brillo lo anula
    solo. Ademas resuelve que el tono sea circular: el rojo de esta tabla esta
    medido en h=352, a 8 grados de la costura 0/360, donde una resta de tonos
    daria 350 en vez de 8.
    """
    rad = h * pi / 180
    c = s * v / 100
    return c * cos(rad), c * sin(rad), v


def medir(muestras=4):
    """Promedia varias lecturas y devuelve el punto (x, y, z) en el cono.

    Se promedia en x,y,z y NO en h,s,v: promediar el tono directo falla porque
    es circular (el promedio de 359 y 1 da 180, que es cian).
    """
    if muestras < 1:
        muestras = 1
    sx = sy = sz = 0
    for _ in range(muestras):
        m = sensor.hsv()
        x, y, z = _xyz(m.h, m.s, m.v)
        sx += x; sy += y; sz += z
        # [MEDIDO EN BANCO 2026-08-23] hsv() NO dispara una medicion nueva:
        # devuelve el ultimo dato que llego del sensor, y cuesta 0.1 ms. Ritmo
        # real medido contra el hub: 149 datos nuevos en 3 s, o sea uno cada
        # 20 ms EN PROMEDIO. La mediana es 10 ms pero la distribucion tiene
        # cola larga (maximo 158 ms), asi que la mediana engania: con espera de
        # 12 ms, el 57% de las lecturas salieron repetidas y promediar 4 valia
        # como promediar 2. Con 20 ms cada muestra es casi siempre nueva.
        wait(20)
    return sx / muestras, sy / muestras, sz / muestras


# ---------------------------------------------------------------------------
# CLASIFICACION
# ---------------------------------------------------------------------------

def competir(x, y, z):
    """El duelo, sin tocar el sensor. Devuelve el diccionario del resultado.

    Separada de medir() a proposito: asi la matematica se puede probar en una
    PC con puntos inventados, sin robot.
    """
    ganador = None
    segundo = None
    for cod, nombre, cx, cy, cz, radio in COLORES:
        if cod == 0:
            # "nada" no tiene recta propia (su centro es el origen) y no es un
            # color: lo decide la compuerta de brillo, no el duelo.
            continue

        dx = x - cx
        dy = y - cy
        dz = z - cz
        dist = (dx * dx + dy * dy + dz * dz) ** 0.5
        mag = (cx * cx + cy * cy + cz * cz) ** 0.5

        if mag > 0:
            # proyeccion sobre la recta del color: es el error de BRILLO
            e_brillo = (dx * cx + dy * cy + dz * cz) / mag
            # lo que sobra, perpendicular: es el error de COLOR
            resto = dist * dist - e_brillo * e_brillo
            e_color = resto ** 0.5 if resto > 0 else 0.0
        else:
            e_brillo = 0.0
            e_color = dist

        # el brillo entra pesado: con PESO_BRILLO=1 esto da exactamente la
        # distancia de siempre, porque error_color^2 + error_brillo^2 = dist^2
        pb = PESO_BRILLO * e_brillo
        puntaje = (e_color * e_color + pb * pb) ** 0.5 - VENTAJA.get(nombre, 0)

        fila = (puntaje, dist, cod, nombre, radio, e_color, e_brillo, mag)
        if ganador is None or puntaje < ganador[0]:
            segundo = ganador
            ganador = fila
        elif segundo is None or puntaje < segundo[0]:
            segundo = fila

    # La aceptacion mira los dos errores POR SEPARADO, y no usa la VENTAJA:
    # asi ninguna ventaja puede fabricar un color donde no lo hay, y ademas se
    # puede decir CUAL de los dos motivos causo la duda.
    lim_color = max(1, ganador[4] * GANANCIA)
    lim_brillo = TOLERANCIA_BRILLO * ganador[7]
    aceptado = ganador[5] <= lim_color and abs(ganador[6]) <= lim_brillo

    return {
        "codigo": ganador[2],
        "nombre": ganador[3],
        "dist": ganador[1],
        "e_color": ganador[5],
        "e_brillo": ganador[6],
        "radio": ganador[4],
        "limite": lim_color,
        "lim_brillo": lim_brillo,
        "aceptado": aceptado,
        "segundo": segundo[3] if segundo else "-",
        "ventaja": segundo[0] - ganador[0] if segundo else 0,
    }


def detectar_color(muestras=4):
    """0 nada | 1 amarillo | 2 verde | 3 azul | 4 negro | 5 rojo | -1 duda

    [IA 2026-08-23] Estos codigos NO estan escritos a mano: salen de la tabla
    COLORES de arriba. Si cambias la tabla, cambia tambien esta linea y los
    bloques. testing/test_colores.py falla si esta linea y la tabla divergen.

    CAMBIO RESPECTO DE LA VERSION ANTERIOR: cuando el ganador queda fuera de su
    radio, ahora devuelve -1 (duda) en vez de 0 (nada). Los bloques que trataban
    el 0 como "seguir de largo" hay que revisarlos: con -1 corresponde releer.
    """
    global _ultimo
    x, y, z = medir(muestras)

    # COMPUERTA DE BRILLO: sin luz que vuelva no hay objeto adelante. Se decide
    # antes del duelo porque "no hay nada" no es un color: es la ausencia de uno.
    if z < V_MINIMO:
        _ultimo = {"codigo": 0, "nombre": "nada", "dist": 0.0, "e_color": 0.0,
                   "e_brillo": 0.0, "radio": 0, "limite": 0, "lim_brillo": 0,
                   "aceptado": True, "segundo": "-", "ventaja": 0,
                   "compuerta": z}
        return 0

    r = competir(x, y, z)
    _ultimo = r

    if r["codigo"] == 0:
        return 0
    if not r["aceptado"]:
        return DUDA
    return r["codigo"]


def detectar_estable(muestras=3):
    """Antirrebote: devuelve el color solo si 2 de 3 lecturas coinciden.

    Si las tres discrepan devuelve -1 (duda), no 0: que el sensor no se ponga
    de acuerdo consigo mismo NO es lo mismo que no haber nada adelante.
    """
    a = detectar_color(muestras)
    b = detectar_color(muestras)
    if a == b:
        return a
    c = detectar_color(muestras)
    if c == a or c == b:
        return c
    return DUDA


def nombre_de(cod):
    """Traduce el codigo a texto, para imprimir. -1 es duda."""
    if cod == DUDA:
        return "duda"
    for c in COLORES:
        if c[0] == cod:
            return c[1]
    return "?"


def explicar():
    """Imprime POR QUE dio lo que dio la ultima deteccion.

    Es la herramienta para tunear: dice quien gano, contra quien, y por cuanto.
    Si la ventaja sobre el segundo es chica, ese es el par que hay que separar.
    """
    if _ultimo is None:
        print("todavia no hubo ninguna deteccion")
        return
    r = _ultimo

    if "compuerta" in r:
        print("nada: el brillo fue", round(r["compuerta"], 1),
              "y la compuerta V_MINIMO esta en", V_MINIMO)
        return

    print("gano:", r["nombre"], "| 2do:", r["segundo"],
          "| le gano por:", round(r["ventaja"], 1))

    print("  error de COLOR: ", round(r["e_color"], 1),
          "de", round(r["limite"], 1), "permitido")
    print("  error de BRILLO:", round(r["e_brillo"], 1),
          "de", round(r["lim_brillo"], 1), "permitido",
          "(+ = mas cerca que al calibrar, - = mas lejos)")
    # decir CUAL de los dos causo la duda es la mitad del valor de esto
    if not r["aceptado"]:
        if r["e_color"] > r["limite"]:
            print("  RECHAZADO POR COLOR -> recalibrar ese color,",
                  "o subir su radio en COLORES")
        else:
            print("  RECHAZADO POR BRILLO -> el objeto esta a otra distancia",
                  "que cuando se calibro. Arreglar el tope mecanico,",
                  "o subir TOLERANCIA_BRILLO")
    else:
        print("  ACEPTADO")

    if r["ventaja"] < 2:
        print("  OJO: gano por muy poco. Ese es el par a separar,",
              "o donde subir la VENTAJA.")


# ---------------------------------------------------------------------------
# CHEQUEO DE LAS TABLAS
# ---------------------------------------------------------------------------

def _puntaje_contra(fila_a, fila_b):
    """Que puntaje saca el centro de A cuando compite contra el color B.

    [IA 2026-08-23] Usa EXACTAMENTE la misma cuenta que el duelo, PESO_BRILLO
    incluido. Una version anterior de este chequeo miraba solo la parte
    perpendicular y avisaba de pares que en realidad estan bien separados por
    brillo (negro y rojo, por ejemplo): un aviso falso entrena al equipo a no
    leer los avisos.

    Como el centro de A saca puntaje 0 contra si mismo, este numero ES el
    margen de A frente a B.
    """
    ax, ay, az = fila_a[2], fila_a[3], fila_a[4]
    bx, by, bz = fila_b[2], fila_b[3], fila_b[4]
    mag_b = (bx*bx + by*by + bz*bz) ** 0.5
    dx, dy, dz = ax - bx, ay - by, az - bz
    dist2 = dx*dx + dy*dy + dz*dz
    if mag_b == 0:
        return dist2 ** 0.5
    e_brillo = (dx*bx + dy*by + dz*bz) / mag_b
    resto = dist2 - e_brillo * e_brillo
    e_color = resto ** 0.5 if resto > 0 else 0.0
    pb = PESO_BRILLO * e_brillo
    return (e_color * e_color + pb * pb) ** 0.5


def chequear():
    """Revisa las dos tablas y avisa donde la clasificacion puede fallar.

    Mide lo que de verdad decide el resultado: donde cae la FRONTERA entre cada
    par de colores, comparada con el ruido de la medicion. Un solape de radios
    no puede provocar una confusion entre dos colores; una frontera adentro del
    ruido, si.
    """
    avisos = 0

    # 1) las dos tablas tienen que hablar de los mismos colores
    for _cod, nombre, _cx, _cy, _cz, _r in COLORES:
        if nombre not in VENTAJA:
            print("ERROR:", nombre, "esta en COLORES pero NO en VENTAJA")
            avisos += 1
    for nombre in VENTAJA:
        visto = False
        for c in COLORES:
            if c[1] == nombre:
                visto = True
        if not visto:
            print("ERROR:", nombre, "esta en VENTAJA pero NO en COLORES (typo?)")
            avisos += 1

    print("PESO_BRILLO =", PESO_BRILLO, "| GANANCIA =", GANANCIA,
          "| TOLERANCIA_BRILLO =", TOLERANCIA_BRILLO)

    # 2) que margen tiene cada color contra cada rival, con la MISMA cuenta
    #    que usa el duelo. Se mira el peor de los dos sentidos.
    n = len(COLORES)
    for i in range(n):
        for j in range(i + 1, n):
            a = COLORES[i]
            b = COLORES[j]
            if a[0] == 0 or b[0] == 0:
                continue           # "nada" no compite: lo maneja V_MINIMO
            # margen de A contra B, corrido por la diferencia de ventajas
            dv = (VENTAJA.get(a[1], 0) - VENTAJA.get(b[1], 0))
            m_a = _puntaje_contra(a, b) + dv
            m_b = _puntaje_contra(b, a) - dv
            sep = m_a if m_a < m_b else m_b
            perdedor = a[1] if m_a < m_b else b[1]
            ruido = a[5] / RUIDO_EN_RADIOS
            if b[5] / RUIDO_EN_RADIOS > ruido:
                ruido = b[5] / RUIDO_EN_RADIOS
            if sep <= 0:
                print("PELIGRO:", a[1], "y", b[1], "- el margen de", perdedor,
                      "es negativo: nunca va a poder ganar")
                avisos += 1
            elif sep < ruido:
                print("PELIGRO:", a[1], "y", b[1], "- margen de", perdedor,
                      "=", round(sep, 1), ", menor que su ruido de",
                      round(ruido, 1))
                avisos += 1
            elif sep < 2 * ruido:
                print("ojo:", a[1], "y", b[1], "- margen de", perdedor, "=",
                      round(sep, 1), "contra un ruido de", round(ruido, 1))
                avisos += 1

    # 3) las perillas globales
    veces = RUIDO_EN_RADIOS * GANANCIA
    if veces > 5:
        print("ojo: GANANCIA =", GANANCIA, "-> el limite de color de TODOS mide",
              round(veces, 1), "veces el ruido. Tan grande casi nunca duda.")
        avisos += 1
    if PESO_BRILLO > 0.5:
        print("ojo: PESO_BRILLO =", PESO_BRILLO, "-> el brillo pesa casi como el",
              "color. Acercar o alejar el objeto va a dar duda.")
        avisos += 1
    if V_MINIMO <= 0:
        print("ojo: con V_MINIMO en", V_MINIMO, "nunca va a contestar 'nada'.")
        avisos += 1

    if avisos == 0:
        print("tablas OK")
    return avisos
