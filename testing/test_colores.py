# ============================================================================
# Tests de colores.py que corren en la PC, sin robot
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5
# Fecha:       2026-08-23 17:30
# Rev:         v2
# Hardware:    ninguno - corre en la PC con Python 3
#
# DESCRIPCION:
#   Carga software/programs/colores.py sacandole los imports de Pybricks y
#   prueba la matematica del clasificador con puntos inventados, en los dos
#   modos. Se corre con "python testing/test_colores.py" desde la raiz.
#
# ============================================================================
#
#  Por que se carga asi y no con import: colores.py tiene que vivir en la raiz
#  del proyecto del hub e importar pybricks, que no existe en la PC. Sacar las
#  tres lineas de import y ejecutar el resto deja UNA sola copia de la
#  matematica -- si se copiaran las formulas aca, se pudririan por separado.
#
# ============================================================================

import math
import os
import random
import sys

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "software", "programs", "colores.py")

fallos = []


def cargar():
    """Ejecuta colores.py sin las partes que necesitan un hub."""
    fuente = open(RUTA, encoding="utf-8").read()
    limpio = []
    for linea in fuente.split("\n"):
        if linea.startswith("from pybricks") or linea.startswith("from umath"):
            continue
        if linea.startswith("sensor = ColorSensor"):
            continue
        limpio.append(linea)
    ns = {
        "sin": math.sin, "cos": math.cos, "pi": math.pi,
        "wait": lambda ms: None,
        "sensor": None,
    }
    exec("\n".join(limpio), ns)
    return ns


def check(nombre, condicion, detalle=""):
    if condicion:
        print("  OK   ", nombre)
    else:
        print("  FALLA", nombre, "->", detalle)
        fallos.append(nombre)


def modo(m):
    # "esfera" = el detector viejo (el brillo pesa igual que el color)
    # "color"  = el brillo pesa poco
    ns["PESO_BRILLO"] = 1.0 if m == "esfera" else 0.2


def leer(punto):
    """Fuerza una lectura concreta y devuelve el codigo detectado."""
    ns["medir"] = lambda muestras=4: punto
    return ns["detectar_color"]()


# ---------------------------------------------------------------------------
ns = cargar()
COLORES = ns["COLORES"]
VENTAJA = ns["VENTAJA"]
competir = ns["competir"]
_xyz = ns["_xyz"]
DUDA = ns["DUDA"]

# Copia de la configuracion REAL del archivo. Varios tests la pisan a proposito
# (poner todas las VENTAJA en 0 para comparar contra el algoritmo viejo, o subir
# una a 1000 para probar un limite) y despues hay que devolverla, porque si no
# los tests siguientes evaluan una configuracion que no existe en ningun lado.
# [IA 2026-08-23] Pasó: sin esto, el test del iman del negro corria con la
# VENTAJA del negro en 0 y acusaba al codigo de un defecto que no tenia.
VENTAJA_REAL = dict(VENTAJA)

def restaurar_ventajas():
    for k, v in VENTAJA_REAL.items():
        VENTAJA[k] = v

# HSV de cada color, recuperado de la tabla (v=z, s=100*r/v, h=atan2(y,x)).
HSV = {}
for cod, n, x, y, z, r in COLORES:
    if z == 0:
        continue
    rad = math.hypot(x, y)
    HSV[n] = (math.degrees(math.atan2(y, x)) % 360, min(100.0, 100.0*rad/z), z)


print("=== 1. el docstring no puede divergir de la tabla ===")
# Este es EL test que importa: el bug que rompio la version anterior fue un
# docstring que decia 1=rojo cuando la tabla decia 1=amarillo. Los codigos
# quedaban corridos y el robot depositaba todo en la zona equivocada, sin
# ningun sintoma visible en el sensor.
doc = ns["detectar_color"].__doc__.split("\n")[0]
esperado = " | ".join(str(c[0]) + " " + c[1] for c in
                      sorted(COLORES, key=lambda c: c[0])) + " | -1 duda"
check("primera linea del docstring == tabla COLORES",
      doc.strip() == esperado,
      "docstring dice [" + doc.strip() + "] y la tabla pide [" + esperado + "]")

print("=== 2. modo esfera: identico al detector anterior ===")
# Migracion segura: la version anterior hacia argmin de la distancia AL
# CUADRADO. Con ventajas en 0 tiene que coincidir en todos los puntos, porque
# elevar al cuadrado no cambia el orden de numeros no negativos.
modo("esfera")
for k in VENTAJA:
    VENTAJA[k] = 0
random.seed(7)
discrepancias = 0
comparados = 0
saltados = 0
for _ in range(20000):
    x = random.uniform(-40, 40); y = random.uniform(-40, 40); z = random.uniform(0, 70)
    viejo, mejor_d2 = None, None
    for cod, _n, cx, cy, cz, _r in COLORES:
        d2 = (x-cx)**2 + (y-cy)**2 + (z-cz)**2
        if mejor_d2 is None or d2 < mejor_d2:
            mejor_d2, viejo = d2, cod
    if viejo == 0:
        # "nada" ya no compite en el duelo: ahora lo decide la compuerta
        # V_MINIMO. Esos puntos quedan fuera de la comparacion a proposito.
        saltados += 1
        continue
    comparados += 1
    if competir(x, y, z)["codigo"] != viejo:
        discrepancias += 1
check("puntos al azar (sin la zona de 'nada'): mismo ganador que el viejo",
      discrepancias == 0,
      str(discrepancias) + " discrepancias sobre " + str(comparados))
print("   comparados:", comparados, "| saltados por caer en 'nada':", saltados)

print("=== 3. la VENTAJA corre la frontera la mitad de la diferencia ===")
def frontera(nombre_a, nombre_b):
    a = [c for c in COLORES if c[1] == nombre_a][0]
    b = [c for c in COLORES if c[1] == nombre_b][0]
    d = math.dist(a[2:5], b[2:5])
    for i in range(200001):
        t = i / 200000.0
        p = [a[2] + (b[2]-a[2])*t, a[3] + (b[3]-a[3])*t, a[4] + (b[4]-a[4])*t]
        if competir(*p)["nombre"] != nombre_a:
            return t * d
    return d

base = frontera("verde", "azul")
VENTAJA["verde"] = 4
corrida = frontera("verde", "azul")
check("subir 4 la VENTAJA del verde corre la frontera 2.0",
      abs((corrida - base) - 2.0) < 0.02,
      "se corrio " + str(round(corrida - base, 3)))
VENTAJA["verde"] = 0

print("=== 4. el rojo esta sobre la costura 0/360 y aun asi clasifica bien ===")
# El rojo de la tabla esta medido en h=352. Una lectura del MISMO rojo que caiga
# del otro lado (h=3) tiene que dar rojo igual. Con resta de tonos daria 349 de
# distancia y elegiria cualquier otra cosa.
for m in ("esfera", "color"):
    modo(m)
    for h in (352, 358, 0, 3, 8):
        r = competir(*_xyz(h, 91, 32))
        check("modo " + m + ": h=" + str(h) + " clasifica rojo",
              r["nombre"] == "rojo", "dio " + r["nombre"])

print("=== 5. ninguna VENTAJA puede fabricar una aceptacion lejos de todo ===")
# La aceptacion NO usa la ventaja. Una ventaja enorme puede hacer ganar el
# duelo, pero no puede hacer que se acepte un punto que no se parece a nada.
for m in ("esfera", "color"):
    modo(m)
    VENTAJA["rojo"] = 1000
    check("modo " + m + ": punto lejisimos con ventaja 1000 da duda",
          leer((200.0, 200.0, 200.0)) == DUDA, "dio " + str(leer((200.0, 200.0, 200.0))))
    VENTAJA["rojo"] = 0

print("=== 6. EL SINTOMA REPORTADO: mismo color a otra distancia ===")
restaurar_ventajas()
# 6a. azul lejos (menos brillo). En modo esfera se convierte en negro: es el
#     bug reportado desde el banco. En modo color tiene que seguir siendo azul.
h_az, s_az, v_az = HSV["azul"]
punto_lejos = _xyz(h_az, s_az, v_az * 0.4)
modo("esfera")
duelo_esfera = competir(*punto_lejos)["nombre"]
modo("color")
duelo_color = competir(*punto_lejos)["nombre"]
print("   azul al 40% de brillo, quien gana el DUELO -> con el brillo pesando",
      "1.0:", duelo_esfera, "| pesando 0.2:", duelo_color)
check("el duelo con brillo pesado 1.0 se equivoca (era el bug del banco)",
      duelo_esfera != "azul", "gano " + duelo_esfera + ", esperaba que fallara")
check("el duelo con brillo pesado 0.2 acierta el azul",
      duelo_color == "azul", "gano " + duelo_color)
# [IA 2026-08-23] Antes este caso daba duda: 60% de caida se pasaba de la
# TOLERANCIA_BRILLO de 0.5. Con 0.8 entra, y entra como AZUL. Eso es lo que se
# buscaba: la lectura es genuinamente azul, solo esta mas lejos.
check("al 40% de brillo se acepta como azul (no duda, y sobre todo no negro)",
      ns["nombre_de"](leer(punto_lejos)) == "azul",
      "dio " + ns["nombre_de"](leer(punto_lejos)))
# mas alla de la tolerancia si tiene que dudar
check("al 15% de brillo (fuera de tolerancia) da duda",
      leer(_xyz(h_az, s_az, v_az * 0.15)) == DUDA,
      "dio " + ns["nombre_de"](leer(_xyz(h_az, s_az, v_az * 0.15))))
# dentro de la tolerancia (60% de brillo = 40% de caida) tiene que dar azul
check("azul al 60% de brillo (dentro de tolerancia) sigue siendo azul",
      ns["nombre_de"](leer(_xyz(h_az, s_az, v_az * 0.6))) == "azul",
      "dio " + ns["nombre_de"](leer(_xyz(h_az, s_az, v_az * 0.6))))

# 6b. objetos CERCA (mas brillo). El amarillo es el peor caso porque su centro
#     es el mas lejano al origen.
for nombre, factor in (("amarillo", 1.4), ("rojo", 1.4), ("azul", 1.4),
                       ("verde", 1.4), ("amarillo", 0.7), ("rojo", 0.7)):
    h, s, v = HSV[nombre]
    modo("color")
    got = ns["nombre_de"](leer(_xyz(h, s, v * factor)))
    check("modo color: " + nombre + " al " + str(int(factor*100)) +
          "% de brillo sigue siendo " + nombre, got == nombre, "dio " + got)

modo("esfera")
h, s, v = HSV["amarillo"]
esf = ns["nombre_de"](leer(_xyz(h, s, v * 1.4)))
print("   (referencia: el mismo amarillo al 140% en modo esfera da:", esf + ")")

print("=== 6c. EL IMAN DEL NEGRO: un color oscuro no puede volverse negro ===")
restaurar_ventajas()   # los tests 2, 3 y 5 pisaron las VENTAJA a proposito
# En el cono, un color leido mas oscuro se desliza hacia el origen, que es donde
# vive el negro. Sin proteccion, todo color se vuelve negro por debajo del ~25%
# de su brillo, y eso pasa cada vez que una pieza entra o sale del campo del
# sensor. La VENTAJA negativa del negro es lo que lo impide. Un negro equivocado
# vale 0 puntos en la mision; una duda solo cuesta releer.
modo("color")
for nombre in ("amarillo", "verde", "azul", "rojo"):
    h, s_, v = HSV[nombre]
    malos = []
    for pct in (60, 50, 40, 30, 20, 15):
        got = ns["nombre_de"](leer(_xyz(h, s_, v * pct / 100.0)))
        if got == "negro":
            malos.append(str(pct) + "%")
    check(nombre + " nunca se vuelve negro al oscurecerse", not malos,
          "se volvio negro a: " + ", ".join(malos))
# y el negro de verdad tiene que seguir ganando en su propio rango
h, s_, v = HSV["negro"]
for pct in (60, 80, 100, 120, 140):
    got = ns["nombre_de"](leer(_xyz(h, s_, v * pct / 100.0)))
    check("el negro real sigue siendo negro al " + str(pct) + "%",
          got == "negro", "dio " + got)

print("=== 6d. NADIE GANA POR UN PELO: la regla del margen minimo ===")
# [VERIFICACION ADVERSARIAL 2026-08-23] Sin margen minimo, verde y azul se
# intercambiaban ACEPTADOS, sin pasar nunca por duda: en el empate el error de
# color es 13.88 contra verde y 13.72 contra azul, y los dos entran en el limite
# de 20. Un corrimiento de tono convertia un verde en azul con toda confianza.
restaurar_ventajas()
verde = [c for c in COLORES if c[1] == "verde"][0]
azul = [c for c in COLORES if c[1] == "azul"][0]
banda = 0
for i in range(101):
    t = i / 100.0
    p = (verde[2]+(azul[2]-verde[2])*t, verde[3]+(azul[3]-verde[3])*t,
         verde[4]+(azul[4]-verde[4])*t)
    if leer(p) == DUDA:
        banda += 1
check("entre verde y azul hay una banda de duda (no un salto seco)",
      banda >= 3, "la banda mide " + str(banda) + "% del trayecto")
# y cada color calibrado tiene que seguir ganando en su propio centro
for cod, nombre, x, y, z, r in COLORES:
    if cod == 0:
        continue
    check(nombre + " en su centro exacto se detecta como " + nombre,
          ns["nombre_de"](leer((float(x), float(y), float(z)))) == nombre,
          "dio " + ns["nombre_de"](leer((float(x), float(y), float(z)))))

print("=== 7. la compuerta de brillo separa nada de los colores ===")
restaurar_ventajas()
modo("color")
check("brillo por debajo de V_MINIMO devuelve 0 (nada)",
      leer((0.0, 0.0, ns["V_MINIMO"] - 0.1)) == 0,
      "dio " + str(leer((0.0, 0.0, ns["V_MINIMO"] - 0.1))))
h, s, v = HSV["negro"]
check("el negro calibrado NO cae en la compuerta",
      ns["nombre_de"](leer(_xyz(h, s, v))) == "negro",
      "dio " + ns["nombre_de"](leer(_xyz(h, s, v))))
check("DUDA no vale 0", DUDA != 0)

print("=== 8. un color que no existe en la tabla da duda, no un color al azar ===")
restaurar_ventajas()
# Un tono naranja intenso no esta en la tabla: tiene que salir duda, no "rojo".
modo("color")
naranja = _xyz(25, 90, 45)
g_orig = ns["GANANCIA"]
# [IA 2026-08-23] Con la tabla vieja este caso daba "amarillo" con GANANCIA=2.5
# y era el argumento para bajarla. Con la tabla recalibrada da "duda" sin tocar
# la ganancia: el problema era la tabla, no el numero.
print("   con GANANCIA =", g_orig, "el naranja da:", ns["nombre_de"](leer(naranja)))
ns["GANANCIA"] = 1.0
check("con GANANCIA=1.0 el naranja (h=25) da duda", leer(naranja) == DUDA,
      "dio " + ns["nombre_de"](leer(naranja)))
ns["GANANCIA"] = g_orig

print("=== 9. cuanto infla el radio el metodo viejo (maximo) vs el nuevo (RMS) ===")
# No es aprobado/reprobado: es el numero que justifica el cambio en calibrar.py.
random.seed(11)
razones = []
for _ in range(4000):
    pts = [(random.gauss(0,1), random.gauss(0,1), random.gauss(0,1)) for _ in range(8)]
    cx = sum(p[0] for p in pts)/8; cy = sum(p[1] for p in pts)/8; cz = sum(p[2] for p in pts)/8
    ds = [math.dist(p, (cx,cy,cz)) for p in pts]
    rms = (sum(d*d for d in ds)/8) ** 0.5
    razones.append(max(ds)/rms)
print("  el maximo de 8 muestras es en promedio",
      round(sum(razones)/len(razones), 2), "veces el RMS")

print("")
if fallos:
    print("FALLARON", len(fallos), "tests:", ", ".join(fallos))
    sys.exit(1)
print("todos los tests pasaron")
