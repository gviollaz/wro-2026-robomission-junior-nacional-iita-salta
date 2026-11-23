# ============================================================================
# Validador de programas de BLOQUES de Pybricks Code
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5.5
# Fecha:       2026-11-23 22:35
# Rev:         v1
# Hardware:    ninguno - corre en la PC con Python 3
#
# DESCRIPCION:
#   Revisa un programa de bloques (.py exportado de Pybricks Code: la primera
#   linea es el workspace en JSON) contra programas REALES del equipo, antes
#   de importarlo en el editor. Se corre desde la raiz del repo con:
#     python software/tools/bloques/validar_bloques.py
#            software/robot-backups/pybricks-backup-2311
#            software/programs/ejemplo_colores_bloques.py
#
# ============================================================================
#
#  POR QUE EXISTE
#  --------------
#  Un bloque mal armado puede trabar el editor en un bucle de recarga
#  (pybricks/support issue #1589). Los tipos de bloque no estan documentados,
#  asi que la unica referencia confiable son archivos que el editor ya produjo.
#  Este programa exige que cada tipo, campo, entrada y variable del archivo
#  aparezca igual en esos programas reales.
#
#  Es MAS ESTRICTO que el editor [IA 2026-11-23]: corrido sobre los propios
#  programas del equipo, avisa ids de bloque repetidos (el editor los genera
#  en valores por defecto y los abre igual) y variables de funcion sin usar.
#  Que un archivo pase NO prueba que el editor lo abra: es un filtro previo.
#
# ============================================================================
import collections, glob, json, os, sys

carpeta, archivo = sys.argv[1], sys.argv[2]
errores = []

def cargar(f):
    l = open(f, encoding="utf-8").readline()
    if "# pybricks blocks file:" not in l:
        return None
    return json.loads(l.split("# pybricks blocks file:", 1)[1])

# ---- esquema aprendido de los programas reales ----
esq = collections.defaultdict(lambda: {"fields": set(), "inputs": set(), "extra": set(), "keys": set(),
                                       "var_tipos": collections.defaultdict(set), "valores": collections.defaultdict(set)})
raiz_claves = set(); refs = 0
def aprender(js):
    vt = {v["id"]: v["type"] for v in js["variables"]}
    def cam(b):
        # recorre SOLO bloques: inputs -> block/shadow, next -> block. Lo que
        # esta en "fields" son referencias a variables, no bloques.
        if isinstance(b, list):
            for v in b: cam(v)
            return
        if isinstance(b, dict):
            if isinstance(b.get("type"), str) and "id" in b:
                e = esq[b["type"]]
                e["keys"] |= set(b.keys()); e["fields"] |= set(b.get("fields", {}))
                e["inputs"] |= set(b.get("inputs", {}))
                if isinstance(b.get("extraState"), dict):
                    e["extra"] |= set(b["extraState"])
                for k, v in b.get("fields", {}).items():
                    if isinstance(v, dict) and "id" in v:
                        e["var_tipos"][k].add(vt.get(v["id"], "?"))
                    elif k in ("OP", "OP1", "CALL_TYPE", "ICON", "SEP"):
                        e["valores"][k].add(v)
            for inp in b.get("inputs", {}).values():
                for k in ("block", "shadow"):
                    if k in inp: cam(inp[k])
            if "next" in b: cam(b["next"]["block"])
    cam(js["blocks"]["blocks"])
for f in sorted(glob.glob(os.path.join(carpeta, "*.py"))):
    js = cargar(f)
    if js:
        refs += 1; raiz_claves |= set(js.keys()); aprender(js)

# ---- el archivo a validar ----
js = cargar(archivo)
if js is None:
    sys.exit("no es un archivo de bloques")
if set(js.keys()) != raiz_claves:
    errores.append("claves raiz %s distintas de las reales %s" % (sorted(js), sorted(raiz_claves)))
if js["blocks"].get("languageVersion") != 0:
    errores.append("languageVersion distinto de 0")
variables = {v["id"]: v for v in js["variables"]}
if len(variables) != len(js["variables"]):
    errores.append("ids de variable repetidos")
ids = collections.Counter(); def_funciones = collections.Counter(); llamadas = []; metodos = []
def revisar(b, camino):
    if isinstance(b, dict):
        if isinstance(b.get("type"), str) and "id" in b:
            t = b["type"]; ids[b["id"]] += 1
            if t not in esq:
                errores.append("%s: tipo %s no aparece en ningun programa real" % (camino, t)); return
            e = esq[t]
            for k in b:
                if k not in e["keys"]: errores.append("%s %s: clave '%s' nunca vista" % (camino, t, k))
            for k in b.get("fields", {}):
                if k not in e["fields"]: errores.append("%s %s: campo '%s' nunca visto" % (camino, t, k))
            for k in b.get("inputs", {}):
                if k not in e["inputs"]: errores.append("%s %s: entrada '%s' nunca vista" % (camino, t, k))
            if isinstance(b.get("extraState"), dict):
                for k in b["extraState"]:
                    if k not in e["extra"]: errores.append("%s %s: extraState '%s' nunca visto" % (camino, t, k))
            for k, v in b.get("fields", {}).items():
                if isinstance(v, dict) and "id" in v:
                    var = variables.get(v["id"])
                    if var is None:
                        errores.append("%s %s: campo %s apunta a una variable que no existe" % (camino, t, k))
                    elif var["type"] not in e["var_tipos"][k]:
                        errores.append("%s %s: variable de tipo %s, en los reales es %s" % (camino, t, var["type"], sorted(e["var_tipos"][k])))
                    for extra_k in ("name", "type"):
                        if extra_k in v and var and v[extra_k] != var[extra_k]:
                            errores.append("%s %s: %s '%s' no coincide con la variable '%s'" % (camino, t, extra_k, v[extra_k], var[extra_k]))
                elif k in e["valores"] and e["valores"][k] and v not in e["valores"][k]:
                    errores.append("%s %s: %s='%s' nunca visto (reales: %s)" % (camino, t, k, v, sorted(e["valores"][k])))
            if t == "variables_setup_function": def_funciones[b["fields"]["VAR"]["id"]] += 1
            if t == "blockFunctionCallerStatement": llamadas.append(b["fields"]["VAR"]["id"])
            if t == "blockFunctionCallValue": metodos.append(b["fields"]["METHOD"])
            if t == "blockIfElse":
                n = b["extraState"]["optionLevel"]
                faltan = [x for x in ["IF" + str(i) for i in range(n)] if x not in b["inputs"]]
                if faltan: errores.append("%s blockIfElse optionLevel %d sin %s" % (camino, n, faltan))
        for nombre_in, inp in b.get("inputs", {}).items():
            for k in ("block", "shadow"):
                if k in inp: revisar(inp[k], camino + "/" + b.get("type", "?") + "." + nombre_in + "." + k)
        if "next" in b: revisar(b["next"]["block"], camino + "/next")
    elif isinstance(b, list):
        for i, v in enumerate(b): revisar(v, camino + "[" + str(i) + "]")
top = js["blocks"]["blocks"]
revisar(top, "")
for b in top:
    if "x" not in b or "y" not in b: errores.append("bloque de arriba sin x/y: " + b["type"])
tipos_top = collections.Counter(b["type"] for b in top)
if tipos_top["blockGlobalSetup"] != 1 or tipos_top["blockGlobalStart"] != 1:
    errores.append("tiene que haber exactamente un Setup y un Start")
rep = [i for i, n in ids.items() if n > 1]
if rep: errores.append("ids de bloque repetidos: %d" % len(rep))
for fid, n in def_funciones.items():
    if n != 1: errores.append("funcion %s definida %d veces" % (variables[fid]["name"], n))
for fid in llamadas:
    if fid not in def_funciones: errores.append("se llama a una funcion no definida: " + str(variables.get(fid)))
importadas = {v["name"] for v in js["variables"] if v["type"] == "FunctionImported"}
for m in metodos:
    if m not in importadas: errores.append("llamada a funcion importada inexistente: " + m)
for v in js["variables"]:
    if v["type"] == "Function" and v["id"] not in def_funciones:
        errores.append("variable de funcion sin definicion: " + v["name"])
print("programas reales usados como referencia:", refs)
print("bloques:", sum(ids.values()), "| tipos distintos:", len({t for t in tipos_top}), "arriba,", "funciones:", len(def_funciones),
      "| llamadas a importadas:", sorted(set(metodos)))
if errores:
    print("ERRORES (%d):" % len(errores)); [print("  -", x) for x in errores[:40]]; sys.exit(1)
print("VALIDO contra los programas reales")
