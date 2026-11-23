# ============================================================================
# Tests de los CONJUNTOS (perfiles) y la MULTITAREA de colores.py, en la PC
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5.5
# Fecha:       2026-11-23 22:00
# Rev:         v1
# Hardware:    ninguno - corre en la PC con Python 3
#
# DESCRIPCION:
#   Prueba lo nuevo de colores.py v3: los dos conjuntos con su tabla, su
#   ventaja y su margen; las funciones sin argumentos para bloques; y las
#   funciones que sirven con multitarea (await, esperar_color, vigilar). La
#   multitarea se prueba con un simulador chico del lazo de tareas de
#   Pybricks, con reloj virtual. Se corre con
#   "python testing/test_colores_tareas.py" desde la raiz del repo.
#
# ============================================================================
#
#  QUE PRUEBA Y QUE NO
#  -------------------
#  Prueba la LOGICA: que cada conjunto use su tabla y sus perillas, que los
#  codigos sean los que esperan los bloques, que las tareas se turnen, que
#  esperar_color gane una carrera contra un straight, y que la version con
#  await de cada funcion conteste lo mismo que la comun.
#
#  NO prueba Pybricks ni el sensor. El simulador imita lo que dicen la
#  documentacion y el firmware [IA 2026-11-23]: dentro de run_task,
#  sensor.hsv() y wait() devuelven una espera pendiente; multitask(race=True)
#  cierra las tareas que pierden, y cerrar un straight deja los motores
#  sueltos. Si Pybricks hiciera otra cosa, estos tests no se enterarian: eso
#  se cierra en el robot.
#
#  La tabla de "rva" todavia no esta medida. Para probar la mecanica se usa
#  una de PRUEBA armada con los valores de la nacional (2026-08-23) para rojo,
#  verde y amarillo: NO dice nada de como se van a leer en el robot de hoy.
#
# ============================================================================

import io
import math
import os
import random
import sys
import types
from contextlib import redirect_stdout

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "software", "programs", "colores.py")

fallos = []


def check(nombre, condicion, detalle=""):
    if condicion:
        print("  OK   ", nombre)
    else:
        print("  FALLA", nombre, "->", detalle)
        fallos.append(nombre)


# ---------------------------------------------------------------------------
# SIMULADOR DEL LAZO DE TAREAS (reloj virtual: cada vuelta del lazo = 1 ms)
# ---------------------------------------------------------------------------

class _Sim:
    def __init__(self):
        self.t = 0              # ms virtuales
        self.activo = False     # True mientras corre run_task
        self.robots = []


SIM = _Sim()


class _Espera:
    """wait(ms) dentro de una tarea: cede el turno hasta que pase el tiempo."""
    def __init__(self, ms):
        self.hasta = SIM.t + ms

    def __await__(self):
        while SIM.t < self.hasta:
            yield None


def wait(ms):
    if SIM.activo:
        return _Espera(ms)       # como Pybricks: devuelve la espera, no espera
    SIM.t += ms                  # sin tareas: bloquea (el tiempo pasa de golpe)
    for r in SIM.robots:
        r.avanzar(ms)
    return None


class _Listo:
    """Lectura del sensor dentro de una tarea: el dato ya esta, no cede turno."""
    def __init__(self, valor):
        self.valor = valor

    def __await__(self):
        return self.valor
        yield  # (convierte __await__ en generador)


class StopWatch:
    def __init__(self):
        self.t0 = SIM.t

    def time(self):
        return SIM.t - self.t0


class _Color:
    def __init__(self, h, s, v):
        self.h, self.s, self.v = h, s, v


class SensorFalso:
    """Devuelve el HSV que diga escena(t_ms, n_lectura). Como Pybricks, dentro
    de una tarea hsv() devuelve una espera pendiente y no el color."""
    def __init__(self, escena):
        self.escena = escena
        self.lecturas = 0

    def _leer(self):
        self.lecturas += 1
        h, s, v = self.escena(SIM.t, self.lecturas)
        return _Color(h, s, v)

    def hsv(self):
        if SIM.activo:
            return _Listo(self._leer())
        return self._leer()


class _Multi:
    """multitask: da una vuelta a cada tarea por vuelta del lazo. Con race,
    cuando termina una CIERRA a las demas (como pb_type_task.c)."""
    def __init__(self, corrutinas, race):
        # Pybricks acepta corrutinas y tambien las esperas de motores y
        # DriveBase: a esas ultimas se las recorre con su __await__()
        self.cs = [c if hasattr(c, "send") else c.__await__()
                   for c in corrutinas]
        self.race = race

    def __await__(self):
        n = len(self.cs)
        res = [None] * n
        fin = [False] * n
        while True:
            for i, c in enumerate(self.cs):
                if fin[i]:
                    continue
                try:
                    c.send(None)
                except StopIteration as e:
                    fin[i] = True
                    res[i] = e.value
            if all(fin) or (self.race and any(fin)):
                for i, c in enumerate(self.cs):
                    if not fin[i]:
                        c.close()
                return tuple(res)
            yield None


def multitask(*corrutinas, race=False):
    return _Multi(corrutinas, race)


def run_task(corrutina=None, limite_ms=120000):
    if corrutina is None:
        return SIM.activo        # la consulta sin argumentos
    SIM.activo = True
    try:
        while True:
            try:
                corrutina.send(None)
            except StopIteration as e:
                return e.value
            SIM.t += 1
            for r in SIM.robots:
                r.avanzar(1)
            if SIM.t > limite_ms:
                raise RuntimeError("la simulacion no termino")
    finally:
        SIM.activo = False


class RobotFalso:
    """DriveBase de juguete sobre una recta. estado: quieto, andando,
    sostenido (hold) o suelto (coast)."""
    def __init__(self):
        self.x = 0.0
        self.vel = 0.0
        self.estado = "quieto"
        SIM.robots.append(self)

    def avanzar(self, ms):
        if self.estado == "andando":
            self.x += self.vel * ms / 1000.0

    def drive(self, vel, giro):
        self.vel = vel
        self.estado = "andando"

    def hold(self):
        self.estado = "sostenido"

    def straight(self, mm, vel=150):
        rob = self

        class _Recta:
            def __await__(self_):
                meta = rob.x + mm
                rob.vel = vel
                rob.estado = "andando"
                try:
                    while rob.x < meta:
                        yield None
                    rob.estado = "sostenido"
                except GeneratorExit:
                    rob.estado = "suelto"   # el close() del firmware es stop()
                    raise
        return _Recta()


# ---------------------------------------------------------------------------
# CARGA DE colores.py
# ---------------------------------------------------------------------------

def cargar():
    fuente = open(RUTA, encoding="utf-8").read()
    limpio = []
    for linea in fuente.split("\n"):
        if linea.startswith("from pybricks") or linea.startswith("from umath"):
            continue
        if linea.startswith("sensor = ColorSensor"):
            continue
        limpio.append(linea)
    ns = {"sin": math.sin, "cos": math.cos, "pi": math.pi,
          "wait": wait, "StopWatch": StopWatch, "sensor": None}
    exec("\n".join(limpio), ns)
    # el import protegido de run_task fallo en la PC (no hay pybricks): se
    # conecta el del simulador, que es lo que contesta "hay tareas?"
    ns["_run_task"] = run_task
    return ns


ns = cargar()
# leer() reemplaza medir por una lectura fija; reiniciar() la devuelve. Sin
# esto, un esperar_color() sin tareas queda en un lazo sin wait() donde el
# reloj virtual no avanza y su tiempo maximo nunca llega (paso una vez).
MEDIR_REAL = ns["medir"]
DUDA = ns["DUDA"]
CODIGOS = ns["CODIGOS"]
PERFILES = ns["PERFILES"]
_xyz = ns["_xyz"]
nombre_de = ns["nombre_de"]
decidir = ns["decidir"]

# [MEDIDO EN BANCO 2026-08-23, con el montaje de la nacional] Solo para probar
# la mecanica de "rva" mientras su tabla real este vacia.
TABLA_RVA_PRUEBA = (
    (5, "rojo",      40,  -6, 45, 8),
    (6, "verde",    -21,  10, 34, 8),
    (1, "amarillo",  43,  54, 99, 8),
    (0, "nada",       0,   0,  0, 8),
)


def con_rva_de_prueba():
    PERFILES["rva"]["tabla"] = TABLA_RVA_PRUEBA


def sin_rva_de_prueba():
    PERFILES["rva"]["tabla"] = ns["TABLA_RVA"]


def fila(nombre, perfil):
    return [c for c in PERFILES[perfil]["tabla"] if c[1] == nombre][0]


def hsv_de(nombre, perfil, factor=1.0):
    """HSV del centro de un color de la tabla de un perfil, brillo escalado."""
    c = fila(nombre, perfil)
    rad = math.hypot(c[2], c[3])
    h = math.degrees(math.atan2(c[3], c[2])) % 360
    s = min(100.0, 100.0 * rad / c[4]) if c[4] else 0.0
    return (h, s, c[4] * factor)


def salida(fn, *a, **k):
    """Corre fn y devuelve (resultado, lo que imprimio)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        r = fn(*a, **k)
    return r, buf.getvalue()


def leer(punto, *args):
    """Fuerza una lectura (sin tareas) y devuelve lo que detecta."""
    ns["medir"] = lambda muestras=4: punto
    return ns["detectar_color"](*args)


def nueva_escena(fn):
    s = SensorFalso(fn)
    ns["sensor"] = s
    return s


def reiniciar():
    SIM.t = 0
    SIM.activo = False
    SIM.robots = []
    ns["_visto"].clear()
    ns["_ultimo"].clear()
    ns["medir"] = MEDIR_REAL


def punto_al_azar():
    return (random.uniform(-110, 110), random.uniform(-110, 110),
            random.uniform(0, 130))


# ===========================================================================
print("=== C1. sin perfil es 'naba': lo que el robot ya usa ===")
check("el perfil por defecto es naba", ns["PERFIL_POR_DEFECTO"] == "naba")
random.seed(23)
distintos = 0
codigos_vistos = set()
for _ in range(20000):
    p = punto_al_azar()
    a = leer(p)
    codigos_vistos.add(a)
    if a != leer(p, 4, "naba") or a != leer(p, 4, None):
        distintos += 1
    ns["medir"] = lambda muestras=4, p=p: p
    if a != ns["detectar_naba"]():
        distintos += 1
check("detectar_color(), detectar_color(4, 'naba') y detectar_naba() coinciden",
      distintos == 0, str(distintos) + " distintos")
check("sin perfil solo salen los codigos que espera el programa de bloques",
      codigos_vistos <= {DUDA, 0, 1, 2, 3, 4}, str(sorted(codigos_vistos)))

print("=== C2. un solo juego de codigos para todos los conjuntos ===")
check("los codigos de CODIGOS no se repiten",
      len(set(CODIGOS.values())) == len(CODIGOS))
check("los de hoy no cambiaron: 1 amarillo 2 blanco 3 azul 4 negro 0 nada",
      (CODIGOS["amarillo"], CODIGOS["blanco"], CODIGOS["azul"],
       CODIGOS["negro"], CODIGOS["nada"]) == (1, 2, 3, 4, 0))
for nombre_p, p in PERFILES.items():
    check("perfil " + nombre_p + ": todos sus colores tienen codigo",
          all(c in CODIGOS for c in p["colores"]))
    check("perfil " + nombre_p + ": cada fila usa el codigo de CODIGOS",
          all(CODIGOS.get(c[1]) == c[0] for c in p["tabla"]))

print("=== C3. 'rva' sin medir: contesta duda y chequear lo dice ===")
reiniciar()
nueva_escena(lambda t, n: (50.0, 70.0, 60.0))
check("detectar_rva() con la tabla vacia da duda", ns["detectar_rva"]() == DUDA)
_r, texto = salida(ns["explicar"], "rva")
check("explicar('rva') dice que la tabla esta vacia", "esta vacia" in texto, texto)
n_avisos, texto = salida(ns["chequear"], "rva")
check("chequear('rva') pide medir los 4 (rojo, verde, amarillo, nada)",
      texto.count("FALTA MEDIR") == 4 and n_avisos >= 4, texto[:300])

print("=== C4. 'rva' con una tabla de PRUEBA ===")
con_rva_de_prueba()
for nombre, cod in (("rojo", 5), ("verde", 6), ("amarillo", 1)):
    got = leer(_xyz(*hsv_de(nombre, "rva")), 4, "rva")
    check("rva: " + nombre + " en su centro da " + str(cod), got == cod,
          nombre_de(got))
check("el amarillo vale 1 en los dos conjuntos",
      leer(_xyz(*hsv_de("amarillo", "rva")), 4, "rva") ==
      leer(_xyz(*hsv_de("amarillo", "naba")), 4, "naba") == 1)
n_avisos, texto = salida(ns["chequear"], "rva")
check("con la tabla cargada ya no pide medir", "FALTA MEDIR" not in texto, texto)
sin_rva_de_prueba()

print("=== C5. cada conjunto con SU tabla: el amarillo se mide dos veces ===")
# el amarillo de "naba" (robot de hoy) y el de "rva" (tabla de prueba) estan
# en lugares distintos del cono: cada conjunto juzga con SU medicion
con_rva_de_prueba()
am_naba = _xyz(*hsv_de("amarillo", "naba"))
got_naba = leer(am_naba, 4, "naba")
check("el amarillo medido en naba da amarillo en naba", got_naba == 1,
      nombre_de(got_naba))
check("las dos mediciones del amarillo son distintas",
      fila("amarillo", "naba")[2:5] != fila("amarillo", "rva")[2:5])
sin_rva_de_prueba()

print("=== C6. la ventaja de un conjunto es frente a SUS colores ===")
con_rva_de_prueba()
def frontera(a_, b_, perfil):
    fa, fb = fila(a_, perfil), fila(b_, perfil)
    d = math.dist(fa[2:5], fb[2:5])
    for i in range(20001):
        t = i / 20000.0
        p = [fa[k] + (fb[k] - fa[k]) * t for k in (2, 3, 4)]
        if ns["competir"](*p, perfil=perfil)["nombre"] != a_:
            return t * d
    return d
def corrimiento(peso):
    ns["PESO_BRILLO"] = peso
    base = frontera("verde", "rojo", "rva")
    PERFILES["rva"]["ventaja"]["verde"] = 4
    corrida = frontera("verde", "rojo", "rva")
    PERFILES["rva"]["ventaja"]["verde"] = 0
    return corrida - base
naba_antes = dict(PERFILES["naba"]["ventaja"])
random.seed(5)
puntos = [punto_al_azar() for _ in range(3000)]
antes = [leer(p) for p in puntos]
peso_real = ns["PESO_BRILLO"]
c_esfera = corrimiento(1.0)
c_real = corrimiento(peso_real)
ns["PESO_BRILLO"] = peso_real
check("PESO_BRILLO=1: +4 al verde de rva corre la frontera verde/rojo 2.0",
      abs(c_esfera - 2.0) < 0.02, "se corrio " + str(round(c_esfera, 3)))
check("PESO_BRILLO real: la corre hacia el rojo, mas que la mitad (" +
      str(round(c_real, 2)) + ")", c_real > 2.0, str(round(c_real, 3)))
PERFILES["rva"]["ventaja"]["amarillo"] = 6      # tocar rva...
despues = [leer(p) for p in puntos]             # ...no mueve nada en naba
PERFILES["rva"]["ventaja"]["amarillo"] = 0
check("cambiar la ventaja de rva no cambia ninguna respuesta de naba",
      antes == despues and PERFILES["naba"]["ventaja"] == naba_antes)
sin_rva_de_prueba()

print("=== C7. el margen es por conjunto (naba en 0, como hoy en el robot) ===")
check("naba tiene margen 0 y rva margen 1",
      PERFILES["naba"]["margen"] == 0 and PERFILES["rva"]["margen"] == 1)
# un punto entre blanco y negro (el par mas fragil de naba) donde el ganador
# se acepta pero gana por un pelo: lo que el margen convertiria en duda
b, z = fila("blanco", "naba"), fila("negro", "naba")
casi = None
for i in range(4001):
    t = i / 4000.0
    p = tuple(b[k] + (z[k] - b[k]) * t for k in (2, 3, 4))
    r = ns["competir"](*p, perfil="naba")
    if r["aceptado"] and 0 < r["ventaja"] < 0.5:
        casi = p
        break
check("hay un punto blanco/negro que gana por un pelo", casi is not None)
if casi:
    check("con margen 0 (hoy) contesta el color", leer(casi, 4, "naba") != DUDA)
    PERFILES["naba"]["margen"] = 1
    check("con margen 1 ese mismo punto da duda", leer(casi, 4, "naba") == DUDA)
    PERFILES["naba"]["margen"] = 0

print("=== C8. errores que chequear() tiene que ver ===")
try:
    ns["competir"](0, 0, 50, perfil="rvaa")
    check("perfil con typo da error", False, "no dio error")
except ValueError as e:
    check("perfil con typo da ValueError con el nombre", "rvaa" in str(e), str(e))
tabla_mala = ns["TABLA_NABA"][:1] + ((6, "blanco", 0, 0, 99, 8),) + ns["TABLA_NABA"][2:]
PERFILES["naba"]["tabla"] = tabla_mala
_n, texto = salida(ns["chequear"], "naba")
check("un codigo cambiado en la tabla se avisa como ERROR",
      "ERROR: blanco tiene el codigo 6" in texto, texto[:300])
tabla_nada = ns["TABLA_NABA"][:4] + ((0, "nada", 0, 0, 9, 8),)
PERFILES["naba"]["tabla"] = tabla_nada
_n, texto = salida(ns["chequear"], "naba")
check("'nada' medida arriba de V_MINIMO se avisa", "'nada' se midio con brillo 9"
      in texto, texto[:300])
PERFILES["naba"]["tabla"] = ns["TABLA_NABA"]
PERFILES["solo_rojo"] = {"colores": ("rojo",), "tabla": TABLA_RVA_PRUEBA[:1],
                         "ventaja": {"rojo": 0}, "margen": 1}
c = leer(_xyz(*hsv_de("rojo", "solo_rojo")), 4, "solo_rojo")
check("conjunto de un solo color: su centro da ese color (no duda por margen)",
      c == 5, nombre_de(c))
del PERFILES["solo_rojo"]

print("=== C9. el firmware de cada tabla se controla ===")
_n, texto = salida(ns["_chequear_firmware"], "?")
check("tabla con firmware '?' avisa", _n == 1 and "no esta anotado" in texto)
falso = types.ModuleType("pybricks")
falso.version = ("primehub", "4.1.3", "v4.1.3 on 2026-11-06")
sys.modules["pybricks"] = falso
_n1, _t1 = salida(ns["_chequear_firmware"], "4.1.3")
_n2, t2 = salida(ns["_chequear_firmware"], "3.6.1")
del sys.modules["pybricks"]
check("mismo firmware que el de la tabla: sin aviso", _n1 == 0, _t1)
check("otro firmware: PELIGRO", _n2 == 1 and "PELIGRO" in t2, t2)

# ===========================================================================
print("=== T1. por que v2 no servia dentro de una tarea ===")
reiniciar()
nueva_escena(lambda t, n: hsv_de("azul", "naba"))
def medir_v2(muestras=4):
    # copia del lazo de medir(): asi era v2 adentro de una tarea
    sx = sy = sz = 0
    for _ in range(muestras):
        m = ns["sensor"].hsv()
        x, y, z = _xyz(m.h, m.s, m.v)
        sx += x; sy += y; sz += z
        wait(20)
    return sx / muestras, sy / muestras, sz / muestras
async def tarea_v2():
    return medir_v2()
try:
    run_task(tarea_v2())
    check("medir() comun adentro de una tarea se corta (AttributeError)", False,
          "no se corto")
except AttributeError:
    check("medir() comun adentro de una tarea se corta (AttributeError)", True)

print("=== T2. la misma funcion sirve con y sin tareas (tambien las de bloques) ===")
reiniciar()
nueva_escena(lambda t, n: hsv_de("azul", "naba"))
check("sin tareas: detectar_naba() devuelve 3 (azul)", ns["detectar_naba"]() == 3)
async def con_await():
    return await ns["detectar_naba"]()
check("con tareas: await detectar_naba() devuelve 3",
      run_task(con_await()) == 3)
async def sin_await():
    r = ns["detectar_naba"]()        # la trampa: falta el await
    es_espera = not isinstance(r, int)
    r.close()                        # (para que Python no se queje)
    return es_espera
check("la trampa: sin await adentro de una tarea NO es un codigo",
      run_task(sin_await()) is True)

print("=== T3. con y sin tareas dan lo mismo (paridad) ===")
# escena con ruido que depende del NUMERO de lectura, no del tiempo: asi las
# dos versiones ven exactamente la misma secuencia de datos
def ruidosa(t, n):
    random.seed(1000 + n)
    nombre = ("azul", "blanco", "azul", "negro", "amarillo")[(n // 7) % 5]
    h, s, v_ = hsv_de(nombre, "naba")
    return ((h + random.uniform(-6, 6)) % 360, max(0.0, s + random.uniform(-4, 4)),
            v_ * random.uniform(0.85, 1.15))
for nombre_fn, llamada in (
        ("medir", lambda: ns["medir"](4)),
        ("detectar_color", lambda: ns["detectar_color"](3)),
        ("detectar_naba", lambda: ns["detectar_naba"]()),
        ("detectar_estable", lambda: ns["detectar_estable"](2, "naba")),
        ("esperar_color", lambda: ns["esperar_color"]((2, 4), None, 2, 1, 3000))):
    reiniciar(); nueva_escena(ruidosa)
    sin_t = [llamada() for _ in range(25)]
    reiniciar(); nueva_escena(ruidosa)
    if nombre_fn == "medir":
        async def todas():
            return [await ns["medir_tarea"](4) for _ in range(25)]
    else:
        async def todas():
            return [await llamada() for _ in range(25)]
    con_t = run_task(todas())
    check(nombre_fn + ": 25 llamadas con tareas == sin tareas", sin_t == con_t,
          str(sin_t[:4]) + " vs " + str(con_t[:4]))

print("=== T4. avanzar hasta ver negro: drive + esperar_color + hold ===")
reiniciar()
rob = RobotFalso()
fondo = hsv_de("blanco", "naba")
nueva_escena(lambda t, n: hsv_de("negro", "naba") if 300 <= rob.x <= 330 else fondo)
async def mision():
    rob.drive(150, 0)
    c = await ns["esperar_color"](4, tiempo_max_ms=10000)
    rob.hold()
    return c
c = run_task(mision())
check("vio el negro", c == 4, str(c))
check("freno pasando apenas el borde (300 a 310 mm)", 300 <= rob.x <= 310,
      str(round(rob.x, 1)))
check("quedo sostenido", rob.estado == "sostenido", rob.estado)

print("=== T5. la carrera straight vs esperar_color, y su trampa ===")
reiniciar()
rob = RobotFalso()
nueva_escena(lambda t, n: hsv_de("negro", "naba") if 300 <= rob.x <= 330 else fondo)
async def carrera():
    return await multitask(rob.straight(600), ns["esperar_color"](4), race=True)
res = run_task(carrera())
check("gano el color: (None, 4)", res == (None, 4), str(res))
check("el straight quedo SUELTO (coast): por eso va robot.hold() despues",
      rob.estado == "suelto", rob.estado)
reiniciar()
rob = RobotFalso()
nueva_escena(lambda t, n: fondo)             # no hay negro en el camino
res = run_task(carrera())
check("sin negro, gana el straight y el robot queda sostenido",
      res[0] is None and res[1] is None and rob.estado == "sostenido",
      str(res) + " " + rob.estado)

print("=== T6. vigilar + visto: un dueno del sensor, varios que preguntan ===")
reiniciar()
secuencia = []
def escena_tiempo(t, n):
    if t < 500:
        return hsv_de("amarillo", "naba")
    if t < 1000:
        return hsv_de("azul", "naba")
    return hsv_de("blanco", "naba")
nueva_escena(escena_tiempo)
contador = [0]
async def mirar():
    while SIM.t < 1500:
        c = ns["visto"]()
        if not secuencia or secuencia[-1] != c:
            secuencia.append(c)
        await wait(10)
async def contar():
    while True:
        contador[0] += 1
        await wait(1)
async def principal():
    await multitask(ns["vigilar"](), mirar(), contar(), race=True)
run_task(principal())
nombres = [nombre_de(c) for c in secuencia]
print("   lo que fue viendo la mision:", nombres)
check("vio amarillo -> azul -> blanco en orden",
      [n for n in nombres if n != "duda"] == ["amarillo", "azul", "blanco"],
      str(nombres))
check("la tarea que cuenta no se freno (cedieron el turno): >1400 vueltas",
      contador[0] > 1400, str(contador[0]))
lecturas_vigia = ns["_visto"]["naba"]["lecturas"]
check("el vigilante leyo a ritmo de ~50 por segundo (60 a 80 en 1.5 s)",
      60 <= lecturas_vigia <= 80, str(lecturas_vigia))
_r, texto = salida(ns["informe_vigia"])
check("informe_vigia() imprime el ritmo", "por segundo" in texto, texto)

print("=== T7. visto() no entrega datos viejos ===")
SIM.t += 1000                                   # pasa 1 s sin vigilante
check("con el vigilante cortado, al rato visto() da duda",
      ns["visto"]() == DUDA, nombre_de(ns["visto"]()))
check("visto() de un perfil sin vigilante da duda", ns["visto"]("rva") == DUDA)
try:
    ns["vigilar"]()
    check("vigilar() sin tareas da error (no se cuelga)", False, "no dio error")
except RuntimeError:
    check("vigilar() sin tareas da error (no se cuelga)", True)

print("=== T8. dos conjuntos en paralelo no se pisan el diagnostico ===")
reiniciar()
con_rva_de_prueba()
nueva_escena(lambda t, n: hsv_de("amarillo", "naba"))
async def dos():
    return await multitask(ns["detectar_rva"](), ns["detectar_naba"]())
res = run_task(dos())
_r, t_rva = salida(ns["explicar"], "rva")
_r, t_naba = salida(ns["explicar"], "naba")
check("explicar('rva') y explicar('naba') hablan cada uno de su conjunto",
      "perfil rva" in t_rva and "perfil naba" in t_naba and
      "gano: amarillo" in t_naba, t_rva + " || " + t_naba)
sin_rva_de_prueba()

print("")
if fallos:
    print("FALLARON", len(fallos), "tests:", ", ".join(fallos))
    sys.exit(1)
print("todos los tests pasaron")
