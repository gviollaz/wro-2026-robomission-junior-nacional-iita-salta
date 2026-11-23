# ============================================================
#  colores.py — detector de color propio (minimos cuadrados)
#  Espacio "cono HSV":  x = s*v/100*cos(h)   y = s*v/100*sin(h)   z = v
#  Gana el punto mas cercano; tol POR COLOR = radio de aceptacion
#  (la "sensibilidad" de ESE color: mas grande = detecta mas facil).
# ============================================================
from pybricks.pupdevices import ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait
from umath import sin, cos, pi

# >>> EDITAR: puerto del sensor. Si esta mal, el import falla al arrancar. <<<
sensor = ColorSensor(Port.F)

# Tabla: (codigo, nombre, x, y, z, tol)
# VALORES DE FABRICA — calibrar con calibrar.py ANTES de competir.
COLORES = (
    (1, "amarillo",  34,  44, 80, 15),
    (2, "blanco",    -2,  0, 89, 15),
    (3, "azul",     -30, -22, 46, 15),
    (4, "negro",      -2,   -1, 20,  5),
    (0, "nada",       0,   0,  1,  3),
)
GANANCIA = 3.0   # perilla global: >1 acepta mas facil TODOS los colores

def _xyz(h, s, v):
    # croma pesada por brillo: a oscuras el tono es ruido y queda anulado
    rad = h * pi / 180
    c = s * v / 100
    return c * cos(rad), c * sin(rad), v

def medir(muestras=4):
    # promedia en x,y,z (promediar el tono directo falla: es circular)
    if muestras < 1:
        muestras = 1
    sx = sy = sz = 0
    for _ in range(muestras):
        m = sensor.hsv()
        x, y, z = _xyz(m.h, m.s, m.v)
        sx += x; sy += y; sz += z
        wait(12)     # el sensor entrega dato nuevo cada ~10 ms
    return sx / muestras, sy / muestras, sz / muestras

def detectar_color(muestras=4):
    """0 sin color | 1 rojo | 2 amarillo | 3 verde | 4 azul | 5 negro"""
    x, y, z = medir(muestras)
    # 1) gana el mas cercano (minimos cuadrados puros, fronteras fijas)
    mejor_cod = 0
    mejor_tol = 1
    mejor_d2 = -1
    for cod, _n, cx, cy, cz, tol in COLORES:
        d2 = (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2
        if mejor_d2 < 0 or d2 < mejor_d2:
            mejor_d2 = d2
            mejor_cod = cod
            mejor_tol = tol
    # 2) acepta solo si cae dentro de la burbuja del ganador
    t = mejor_tol * GANANCIA
    if t < 1:
        t = 1
    if mejor_d2 > t * t:
        return 0
    return mejor_cod

def detectar_estable(muestras=3):
    """Antirrebote: devuelve el color solo si 2 de 3 lecturas coinciden."""
    a = detectar_color(muestras)
    b = detectar_color(muestras)
    if a == b:
        return a
    c = detectar_color(muestras)
    if c == a or c == b:
        return c
    return 0

def chequear():
    """Avisa si las burbujas de dos colores se tocan o se tapan."""
    avisos = 0
    n = len(COLORES)
    for i in range(n):
        for j in range(i + 1, n):
            a = COLORES[i]; b = COLORES[j]
            d = ((a[2]-b[2])**2 + (a[3]-b[3])**2 + (a[4]-b[4])**2) ** 0.5
            ta = a[5] * GANANCIA; tb = b[5] * GANANCIA
            if ta >= d or tb >= d:
                print("PELIGRO:", a[1], "y", b[1], "- una burbuja tapa a la otra (dist", round(d), ")")
                avisos += 1
            elif ta + tb >= d:
                print("ojo:", a[1], "y", b[1], "- burbujas se tocan (dist", round(d), ")")
                avisos += 1
    if avisos == 0:
        print("tabla OK: sin solapamientos")