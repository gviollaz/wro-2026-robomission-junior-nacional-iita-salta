# ============================================================================
# Genera el programa de bloques de ejemplo de los conjuntos de colores
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5.5
# Fecha:       2026-11-23 22:35
# Rev:         v1
# Hardware:    ninguno - corre en la PC con Python 3
#
# DESCRIPCION:
#   Arma software/programs/ejemplo_colores_bloques.py copiando la FORMA de
#   los bloques de un programa real del equipo (import, llamada comun,
#   "si / si no si", pitidos). Los ids salen con semilla fija: corriendolo de
#   nuevo da el mismo archivo. Desde la raiz del repo:
#     python software/tools/bloques/armar_ejemplo_bloques.py
#            software/robot-backups/pybricks-backup-2311/WRO_2311_ORIGINAL.py
#            software/programs/ejemplo_colores_bloques.py
#   Despues validarlo con validar_bloques.py.
#
# ============================================================================
import json, random, sys

ref = json.loads(open(sys.argv[1], encoding="utf-8").readline()
                 .split("# pybricks blocks file:", 1)[1])
salida = sys.argv[2]

rnd = random.Random(2311)
SEGUROS = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
           "!#$%()*+,-./:;=?@[]^_`{|}~")
usados = set()


def nid():
    while True:
        i = "".join(rnd.choice(SEGUROS) for _ in range(20))
        if i not in usados:
            usados.add(i)
            return i


# ---------------- variables ----------------
variables = [v for v in ref["variables"] if v["type"] == "ColorDef"]   # las crea el editor
def var(nombre, tipo):
    v = {"name": nombre, "id": nid(), "type": tipo}
    variables.append(v)
    return v

V_HUB = var("prime hub", "PrimeHub")
V_COLOR = var("coloractual", "Any")
V_NABA = var("detectar_naba", "FunctionImported")
V_RVA = var("detectar_rva", "FunctionImported")
F_LEER_NABA = var("detectar y guardar color NABA", "Function")
F_LEER_RVA = var("detectar y guardar color RVA", "Function")
F_MOSTRAR_NABA = var("mostrar color NABA", "Function")
F_MOSTRAR_RVA = var("mostrar color RVA", "Function")


def ref_var(v):
    return {"id": v["id"], "name": v["name"], "type": v["type"]}


# ---------------- bloques (formas copiadas de los programas reales) ----------------
def numero(n):
    return {"type": "blockMathNumber", "id": nid(), "fields": {"NUM": n}}


def texto(t):
    return {"type": "text", "id": nid(), "fields": {"TEXT": t}}


def leer_coloractual():
    return {"type": "blockVariableGetValue", "id": nid(), "inputs": {"VAR": {"shadow": {
        "type": "variables_get_any", "id": nid(), "fields": {"VAR": ref_var(V_COLOR)}}}}}


def igual(n):
    """coloractual == n, como en PARTE DE LAS NOTAS"""
    return {"type": "blockLogicCompare", "id": nid(), "fields": {"OP1": "EQ"},
            "inputs": {"A": {"shadow": numero(0), "block": leer_coloractual()},
                       "B": {"shadow": numero(n)}}}


def o(a, b):
    """a or b, como el "0 o 4" del programa del robot"""
    return {"type": "blockLogicOperation", "id": nid(), "fields": {"OP": "OR"},
            "inputs": {"A": {"shadow": {"type": "blockLogicTrue", "id": nid()}, "block": a},
                       "B": {"shadow": {"type": "blockLogicTrue", "id": nid()}, "block": b}}}


def esperar(ms):
    return {"type": "blockWaitTime", "id": nid(), "inputs": {"VALUE0": {"shadow": {
        "type": "unit_time", "id": nid(), "fields": {"VALUE0": ms}}}}}


def imprimir(t):
    return {"type": "blockPrint", "id": nid(), "extraState": {"optionLevel": 0},
            "inputs": {"TEXT0": {"shadow": texto(t)}}}


def imprimir_con_color(t):
    """print(t, coloractual), como en "detectar y guardar color" """
    return {"type": "blockPrint", "id": nid(), "extraState": {"optionLevel": 1},
            "fields": {"SEP": "SEP_SPACE"},
            "inputs": {"TEXT0": {"shadow": texto(t)},
                       "TEXT1": {"shadow": texto("abc"), "block": leer_coloractual()}}}


def pitido(frecuencia, duracion):
    return {"type": "blockSpeakerBeep", "id": nid(), "inputs": {
        "VAR": {"shadow": {"type": "variables_get_speaker_hub", "id": nid(),
                           "fields": {"VAR": ref_var(V_HUB)}}},
        "VALUE0": {"shadow": {"type": "unit_frequency", "id": nid(), "fields": {"VALUE0": frecuencia}}},
        "VALUE1": {"shadow": {"type": "unit_time", "id": nid(), "fields": {"VALUE0": duracion}}}}}


def guardar_llamada(funcion_importada):
    """coloractual = funcion() con llamada COMUN, como hoy con detectar_color"""
    return {"type": "blockVariableSetValue", "id": nid(), "inputs": {
        "VAR": {"shadow": {"type": "variables_get_any", "id": nid(), "fields": {"VAR": ref_var(V_COLOR)}}},
        "VALUE0": {"shadow": numero(0),
                   "block": {"type": "blockFunctionCallValue", "id": nid(),
                             "extraState": {"optionLevel": 0},
                             "fields": {"CALL_TYPE": "CLASS_CALL_METHOD_SYNC",
                                        "METHOD": funcion_importada["name"]}}}}}


def llamar(funcion):
    return {"type": "blockFunctionCallerStatement", "id": nid(), "extraState": {"optionLevel": 0},
            "fields": {"ICON": "TASK", "VAR": {"id": funcion["id"]}}}


def cadena(*bloques):
    """encadena con "next" (cada bloque abajo del anterior)"""
    for a, b in zip(bloques, bloques[1:]):
        a["next"] = {"block": b}
    return bloques[0]


def si_cadena(ramas):
    """ramas = [(condicion, [bloques])...]: si / si no si ..., como el de 5 del robot"""
    b = {"type": "blockIfElse", "id": nid(), "extraState": {"optionLevel": len(ramas)}, "inputs": {}}
    for k, (cond, cuerpo) in enumerate(ramas):
        b["inputs"]["IF" + str(k)] = {"shadow": {"type": "blockLogicTrue", "id": nid()}, "block": cond}
        b["inputs"]["DO" + str(k)] = {"block": cadena(*cuerpo)}
    return b


def funcion(f, x, y, *cuerpo):
    return {"type": "variables_setup_function", "id": nid(), "x": x, "y": y,
            "extraState": {"optionLevel": 0},
            "fields": {"ICON": "TASK", "VAR": {"id": f["id"]}},
            "inputs": {"STACK": {"block": cadena(*cuerpo)}}}


setup = {"type": "blockGlobalSetup", "id": nid(), "x": 0, "y": 0, "deletable": False,
         "next": {"block": cadena(
             {"type": "variables_setup_imported_function", "id": nid(),
              "fields": {"FROM_MODULE": "colores", "VAR": {"id": V_NABA["id"]}}},
             {"type": "variables_setup_imported_function", "id": nid(),
              "fields": {"FROM_MODULE": "colores", "VAR": {"id": V_RVA["id"]}}},
             {"type": "variables_setup_any", "id": nid(), "fields": {"VAR": {"id": V_COLOR["id"]}},
              "inputs": {"VALUE0": {"shadow": numero(0)}}},
             {"type": "variables_set_prime_hub", "id": nid(), "extraState": {"optionLevel": 0},
              "fields": {"VAR": {"id": V_HUB["id"]}}})}}

start = {"type": "blockGlobalStart", "id": nid(), "x": 0, "y": 260, "deletable": False,
         "next": {"block": cadena(
             imprimir("Presentar una pieza NEGRA, AZUL, BLANCA o AMARILLA"),
             esperar(3000),
             llamar(F_LEER_NABA),
             llamar(F_MOSTRAR_NABA),
             imprimir("Presentar una pieza ROJA, VERDE o AMARILLA"),
             esperar(3000),
             llamar(F_LEER_RVA),
             llamar(F_MOSTRAR_RVA))}}

leer_naba = funcion(F_LEER_NABA, 700, 0,
                    esperar(200), guardar_llamada(V_NABA), imprimir_con_color("NABA detecto:"))
leer_rva = funcion(F_LEER_RVA, 700, 260,
                   esperar(200), guardar_llamada(V_RVA), imprimir_con_color("RVA detecto:"))
mostrar_naba = funcion(F_MOSTRAR_NABA, 1500, 0, si_cadena([
    (igual(1), [imprimir("amarillo"), pitido(1200, 120)]),
    (igual(2), [imprimir("blanco"), pitido(1500, 60)]),
    (igual(3), [imprimir("azul"), pitido(450, 140)]),
    (o(igual(0), igual(4)), [imprimir("negro o nada"), pitido(250, 90)]),
    (igual(-1), [imprimir("duda: releer"), pitido(520, 70)]),
]))
mostrar_rva = funcion(F_MOSTRAR_RVA, 1500, 900, si_cadena([
    (igual(5), [imprimir("rojo"), pitido(1000, 90)]),
    (igual(6), [imprimir("verde"), pitido(700, 120)]),
    (igual(1), [imprimir("amarillo"), pitido(1200, 120)]),
    (igual(0), [imprimir("nada"), pitido(160, 40)]),
    (igual(-1), [imprimir("duda: releer"), pitido(520, 70)]),
]))

workspace = {"blocks": {"languageVersion": 0,
                        "blocks": [setup, start, leer_naba, leer_rva, mostrar_naba, mostrar_rva]},
             "variables": variables,
             "info": ref["info"],
             "workspaceOptions": {"scrollX": 0, "scrollY": 0, "scale": 0.7}}

PYTHON = '''# ============================================================================
# Ejemplo en bloques: leer una pieza de cada conjunto de colores
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5.5
# Fecha:       2026-11-23 22:30
# Rev:         v1
# Hardware:    LEGO SPIKE Prime + sensor de color de artefactos (puerto F,
#              lo crea colores.py)
#
# DESCRIPCION:
#   Programa de BLOQUES (la primera linea es el workspace del editor). Pide
#   una pieza negra/azul/blanca/amarilla y la lee con detectar_naba; despues
#   una roja/verde/amarilla con detectar_rva; anuncia cada una con texto y
#   pitido. Esta cabecera va debajo de la primera linea porque el formato de
#   bloques exige que la primera sea el JSON; el editor regenera esta parte
#   al guardar.
#
# ============================================================================

from pybricks.hubs import PrimeHub
from pybricks.tools import wait

from colores import detectar_naba
from colores import detectar_rva

# Set up.
coloractual = 0
prime_hub = PrimeHub()

def detectar_y_guardar_color_NABA():
    global coloractual
    wait(200)
    coloractual = detectar_naba()
    print('NABA detecto:', coloractual)

def detectar_y_guardar_color_RVA():
    global coloractual
    wait(200)
    coloractual = detectar_rva()
    print('RVA detecto:', coloractual)

def mostrar_color_NABA():
    if coloractual == 1:
        print('amarillo')
        prime_hub.speaker.beep(1200, 120)
    elif coloractual == 2:
        print('blanco')
        prime_hub.speaker.beep(1500, 60)
    elif coloractual == 3:
        print('azul')
        prime_hub.speaker.beep(450, 140)
    elif coloractual == 0 or coloractual == 4:
        print('negro o nada')
        prime_hub.speaker.beep(250, 90)
    elif coloractual == -1:
        print('duda: releer')
        prime_hub.speaker.beep(520, 70)
    else:
        pass

def mostrar_color_RVA():
    if coloractual == 5:
        print('rojo')
        prime_hub.speaker.beep(1000, 90)
    elif coloractual == 6:
        print('verde')
        prime_hub.speaker.beep(700, 120)
    elif coloractual == 1:
        print('amarillo')
        prime_hub.speaker.beep(1200, 120)
    elif coloractual == 0:
        print('nada')
        prime_hub.speaker.beep(160, 40)
    elif coloractual == -1:
        print('duda: releer')
        prime_hub.speaker.beep(520, 70)
    else:
        pass


# The main program starts here.
print('Presentar una pieza NEGRA, AZUL, BLANCA o AMARILLA')
wait(3000)
detectar_y_guardar_color_NABA()
mostrar_color_NABA()
print('Presentar una pieza ROJA, VERDE o AMARILLA')
wait(3000)
detectar_y_guardar_color_RVA()
mostrar_color_RVA()
'''

linea = "# pybricks blocks file:" + json.dumps(workspace, ensure_ascii=False, separators=(",", ":"))
open(salida, "w", encoding="utf-8", newline="\n").write(linea + "\n" + PYTHON)
print("escrito", salida, "| bloques:", len(usados), "ids | variables:", len(variables))
