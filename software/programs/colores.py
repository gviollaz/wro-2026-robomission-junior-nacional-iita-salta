# ============================================================================
# Detector de color por minimos cuadrados con sensibilidad por color
# ============================================================================
#
# Autor:       Gustavo Viollaz
# Herramienta: Claude Opus 5 (v2) / Claude Opus 5.5 (v3)
# Fecha:       2026-11-23 21:20
# Rev:         v3
# Hardware:    LEGO SPIKE Prime + sensor de color estandar (Pybricks) en el
#              PUERTO F (el sensor de artefactos)
#
# DESCRIPCION:
#   Clasifica el artefacto que tiene adelante comparando la lectura contra una
#   tabla de colores medidos, en el espacio "cono HSV". Hay DOS conjuntos de
#   colores (perfiles), cada uno con SU tabla medida y SU sensibilidad por
#   color: "naba" (negro, azul, blanco, amarillo) y "rva" (rojo, verde,
#   amarillo). Las funciones sirven con y sin multitarea.
#
# ============================================================================
#
#  DE DONDE VIENE ESTA VERSION  [IA 2026-11-23]
#  ---------------------------------------------
#  Parte del colores.py que CORRE EN EL ROBOT (backup de Pybricks Code
#  "pybricks-backup-2311"), no del que estaba en el repo: el del robot tiene
#  el sensor en el puerto F y la tabla de negro/azul/blanco/amarillo. Ese
#  conjunto es ahora el perfil "naba", que es el que se usa si no se pide otro:
#  detectar_color() sin argumentos decide igual que antes, asi que los
#  programas de bloques que ya la llaman no cambian.
#
# ============================================================================
#
#  QUE PERILLA TOCAR SEGUN EL SINTOMA
#  ----------------------------------
#     "el azul me lo lee negro"           ->  "ventaja" del azul en SU perfil
#     "no lo ve, me dice duda seguido"    ->  radio de ese color en SU tabla
#     "de cerca casi todo me da duda"     ->  TOLERANCIA_BRILLO    (global)
#     "de lejos el azul se vuelve negro"  ->  PESO_BRILLO          (global)
#     "ve un color donde no hay nada"     ->  bajar el radio, o subir V_MINIMO
#
#  Las dos primeras son POR COLOR Y POR CONJUNTO: el amarillo de "naba" y el
#  de "rva" tienen cada uno su medicion, su radio y su ventaja, porque compiten
#  contra colores distintos. La ventaja pelea contra los OTROS COLORES DE ESE
#  CONJUNTO (decide quien gana el duelo) y el radio pelea contra la DUDA
#  (decide si se acepta al ganador). Son dos numeros y no uno a proposito: si
#  fuera uno solo, subirle la sensibilidad al rojo para ganarle al amarillo lo
#  volveria tambien mas permisivo, y fabricarias un falso positivo mientras
#  arreglas la confusion.
#
#  Las dos siguientes son GLOBALES y las dos tratan el mismo tema: que el brillo
#  cambia cuando el objeto esta a otra distancia, y eso NO significa que sea
#  otro color.
#
# ============================================================================
#
#  COMO SE USA DESDE BLOQUES (Pybricks Code)
#  -----------------------------------------
#  Este archivo es un programa de tipo Python, hermano del programa de bloques.
#  [IA 2026-11-23] Asi esta hecho HOY en los programas del robot (WRO_2311 y
#  los anteriores, leidos del backup): en el Setup hay un bloque de import
#  "from colores import detectar_color", y se llama con el bloque de llamada
#  como funcion COMUN (en el archivo: CALL_TYPE "CLASS_CALL_METHOD_SYNC"),
#  SIN argumentos, y el resultado se guarda en la variable "coloractual".
#
#  Para usar cada conjunto se importa la funcion de ese conjunto, igual que hoy
#  se importa detectar_color:
#      from colores import detectar_naba     -> 1 amarillo 2 blanco 3 azul
#                                               4 negro    0 nada  -1 duda
#      from colores import detectar_rva      -> 1 amarillo 5 rojo  6 verde
#                                               0 nada    -1 duda
#  Son funciones SIN argumentos a proposito: en ningun programa del backup se
#  le pasa un argumento a una funcion importada, asi que no esta comprobado que
#  el bloque de llamada lo permita.
#
#  Restricciones de Pybricks, verificadas en su documentacion y su codigo
#  [IA 2026-08-23]:
#    - no existe "import *": se importa funcion por funcion;
#    - el nombre del archivo no puede llevar guion medio;
#    - importar EJECUTA lo que esta fuera de funciones (por eso el sensor se
#      crea aca abajo y un puerto mal puesto falla al arrancar, no en medio
#      de la ronda).
#  [IA 2026-11-23] Lo que decia v2 ("si el programa de bloques usa multitarea,
#  asume que lo importado es async", pybricks/support issue #1635) quedo
#  viejo: el issue se cerro el 2026-10-08 con "This works with the updated
#  import blocks", y por eso el bloque de llamada guarda si la llamada es
#  comun o async. Los programas de hoy no usan multitarea: llamada comun.
#
# ============================================================================
#
#  MULTITAREA (run_task / multitask)
#  ---------------------------------
#  [IA 2026-11-23] Verificado en la documentacion de Pybricks (tools,
#  "Multitasking") y en el codigo del firmware (pybricks-micropython).
#
#  1. Dentro de run_task, sensor.hsv() y wait() NO devuelven un color ni
#     esperan: devuelven una espera pendiente que se espera con await. Por eso
#     v2 no servia dentro de una tarea: se cortaba con AttributeError en "m.h".
#     Las funciones de v3 que tocan el sensor se fijan solas si hay tareas
#     corriendo (run_task() sin argumentos lo dice, desde el firmware 3.4.0b3)
#     y se usan IGUAL QUE wait():
#         sin multitarea:         c = detectar_rva()
#         dentro de una tarea:    c = await detectar_rva()
#     En bloques: llamada comun en un programa sin multitarea (como hoy), y
#     llamada async si el programa pasa a usar multitarea.
#     Olvidarse el await dentro de una tarea NO da error: devuelve una espera
#     que nunca corre, y "c == 5" da falso para siempre. Es la misma trampa que
#     con wait() y con los motores; el modulo no tiene forma de detectarla.
#
#  2. Las tareas se turnan: una tarea le cede el lugar a las otras SOLO en un
#     await. Por eso aca ningun lazo lee el sensor sin un await adentro.
#
#  3. UN SOLO DUENO POR SENSOR. Para mirar el color todo el tiempo mientras el
#     robot hace otra cosa, una tarea lo lee (vigilar) y las demas le preguntan
#     a visto(), que no toca el sensor:
#         await multitask(vigilar("naba"), mision(), race=True)
#     race=True corta al vigilante (que no termina nunca) cuando termina la
#     mision. visto() contesta DUDA si su dato es viejo: si el vigilante se
#     trabo, el robot no tiene que seguir creyendo lo que vio hace un segundo.
#
#  4. Para frenar al ver un color:
#         robot.drive(150, 0)                  # arranca y sigue de largo
#         c = await esperar_color((1, 5, 6), perfil="rva", tiempo_max_ms=4000)
#         robot.hold()                         # c = None: no lo vio a tiempo
#     La otra forma, multitask(robot.straight(600), esperar_color(...),
#     race=True), tiene una trampa: segun el codigo del firmware, cuando gana
#     el color el straight se corta con stop(), que deja los motores SUELTOS
#     (COAST) y el robot sigue rodando por inercia hasta la orden siguiente.
#     Si se usa, poner robot.hold() en la linea de abajo.
#
#  5. No escribir race=False a mano: antes del firmware 4.0.0b3 eso hacia que
#     multitask se comportara como race=True (pybricks/support issue #2468).
#     Para esperar a todas las tareas, no pasar race.
#
# ============================================================================

from pybricks.pupdevices import ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait, StopWatch
from umath import sin, cos, pi

# run_task() sin argumentos dice si el programa esta corriendo tareas. Se
# importa con red de seguridad: si el firmware no lo tiene, el modulo carga
# igual y funciona como v2 (solo sin multitarea).
try:
    from pybricks.tools import run_task as _run_task
except ImportError:
    _run_task = None

# >>> EDITAR: puerto del sensor. Si esta mal, el import falla al arrancar. <<<
# [IA 2026-11-23] F es como esta en el robot (programas del backup 2311: el
# Setup de los bloques tambien crea SENSORFRENTE en F). El repo decia B, que
# en el robot es el motor de traccion izquierdo.
sensor = ColorSensor(Port.F)


# ---------------------------------------------------------------------------
# CODIGOS  --  el numero que devuelve cada color, IGUAL en todos los perfiles
# ---------------------------------------------------------------------------
# Los programas de bloques comparan estos numeros ("coloractual == 2"): NO
# cambiar los que ya existen. 1 a 4 y 0 son los que usa hoy el robot; rojo y
# verde son nuevos. -1 (DUDA, mas abajo) es "hay algo pero no se reconoce".
CODIGOS = {
    "nada": 0,
    "amarillo": 1,
    "blanco": 2,
    "azul": 3,
    "negro": 4,
    "rojo": 5,
    "verde": 6,
}


# ---------------------------------------------------------------------------
# TABLAS MEDIDAS  --  una por conjunto. Las escribe calibrar.py.
# ---------------------------------------------------------------------------
# (codigo, nombre, x, y, z, radio)
#
#   x, y, z = centro del color en el cono HSV (lo mide calibrar.py)
#   radio   = hasta que distancia del centro se sigue aceptando este color.
#             calibrar.py lo calcula como RUIDO_EN_RADIOS veces el ruido medido.
#
# Cada conjunto se calibra POR SEPARADO, con las piezas de ese conjunto: el
# amarillo de "naba" y el de "rva" son dos mediciones distintas. No editar a
# mano salvo el radio.

# Negro, azul, blanco, amarillo.
# [IA 2026-11-23] Copiada tal cual del colores.py que corre en el robot (backup
# 2311). No se sabe cuando ni con que firmware se midio.
TABLA_NABA = (
    (1, "amarillo",  32,  28, 64, 8),
    (2, "blanco",     0,   0, 99, 8),
    (3, "azul",     -37, -26, 63, 8),
    (4, "negro",     -2,  -1, 28, 8),
    (0, "nada",       0,   0,  1, 8),
)
FIRMWARE_NABA = "?"

# Rojo, verde, amarillo.
# [IA 2026-11-23] FALTA MEDIR: correr calibrar.py con PERFIL = "rva" y pegar
# aca lo que imprime. Mientras este vacia, detectar_rva() contesta -1 (duda)
# siempre, y chequear("rva") lo avisa.
TABLA_RVA = ()
FIRMWARE_RVA = "?"

# Por que importa el firmware: el 4.0.0b3 (2025-12-05) CAMBIO la cuenta del
# HSV del sensor de color SPIKE ("User code should measure HSV values again",
# CHANGELOG de pybricks-micropython). Una tabla medida de un lado de un cambio
# asi y usada del otro da colores corridos, sin ningun error. chequear() lo
# compara con el firmware del hub. "?" = no se anoto.


# ---------------------------------------------------------------------------
# PERILLA 1: VENTAJA  --  contra los OTROS COLORES DEL CONJUNTO
# ---------------------------------------------------------------------------
# Es un regalo de distancia en el duelo. NO cambia la distancia real, solo
# quien gana la comparacion. Cada conjunto tiene la suya (en PERFILES, abajo):
# la ventaja del amarillo en "naba" pelea contra blanco, azul y negro; la del
# amarillo en "rva", contra rojo y verde.
#
#   0     = pelea de igual a igual
#   subir = ese color gana el duelo mas seguido (frente a los de su conjunto)
#
# Cuanto se mueve: con PESO_BRILLO = 1 la frontera entre dos colores se corre
# exactamente la MITAD de la diferencia de ventajas, medida sobre la recta que
# une sus centros. [IA 2026-11-23] Con el PESO_BRILLO = 0.2 que se usa se corre
# MAS, y distinto en cada par: 1 / (ka + kb) por unidad, con ka y kb entre 0.2
# y 1 segun que tan alineada este esa recta con el brillo de cada color.
# Calculado con TABLA_NABA (sin banco), por cada unidad de ventaja:
#     amarillo/blanco 0.56   blanco/azul 0.56   azul/negro 0.94
#     blanco/negro    2.33   <- el par mas sensible: ver PERFILES
# (v2 decia "exactamente la mitad" en general: eso vale solo con
# PESO_BRILLO = 1.)
#
# Paso util: 2. "Rango sano" NO es un numero fijo: depende de que tan cerca
# esten los colores. [IA 2026-11-23] Ejemplo con la tabla de la nacional:
# con el negro en -6, darle +6 al verde ya hacia que el centro del negro se
# leyera verde. Correr chequear(perfil) despues de cada cambio: un margen
# negativo es justamente eso.
# Preferir SUBIR el color que falla antes que BAJAR al vecino: bajar al vecino
# le saca territorio contra todos los demas, no solo contra el que te molesta.


# ---------------------------------------------------------------------------
# PERFILES  --  cada conjunto con su tabla, su ventaja y su margen
# ---------------------------------------------------------------------------
# "colores": lo que se calibra y lo que puede aparecer delante del sensor en
#            esa situacion. El perfil SUPONE que no aparece ningun otro: un
#            color de afuera se leeria como el mas parecido de adentro.
# "margen":  MARGEN_MINIMO de ese conjunto (ver la perilla 4, mas abajo).
PERFILES = {
    "naba": {
        "colores": ("amarillo", "blanco", "azul", "negro", "nada"),
        "tabla": TABLA_NABA,
        "firmware": FIRMWARE_NABA,
        "ventaja": {
            "amarillo": 0,
            "blanco": 0,
            "azul": 0,
            # El negro es un IMAN: en el cono, cualquier color que se lee mas
            # oscuro se desliza hacia el origen, que es donde vive el negro.
            # [MEDIDO EN BANCO 2026-08-23, con la tabla de la nacional] -6 era
            # el borde util: ningun color se volvia negro ni bajando al 10%.
            # [IA 2026-11-23] Calculado con TABLA_NABA, sin banco: con -6 el
            # amarillo se vuelve negro recien por debajo del 13% de su brillo y
            # el azul del 15%, pero el BLANCO por debajo del 45%. Blanco y
            # negro estan sobre el mismo eje sin color y solo los separa el
            # brillo, que pesa 0.2: es el par mas fragil del conjunto.
            "negro": -6,
            "nada": 0,
        },
        # [IA 2026-11-23] En 0 porque asi corre hoy en el robot: el colores.py
        # del backup no tenia la regla de margen minimo. Prenderla cambia
        # respuestas cerca de las fronteras por -1, y el programa de bloques
        # hace otra cosa con -1. Probarla en banco antes de prenderla aca.
        "margen": 0,
    },
    "rva": {
        "colores": ("rojo", "verde", "amarillo", "nada"),
        "tabla": TABLA_RVA,
        "firmware": FIRMWARE_RVA,
        # [PROVISORIO 2026-11-23] Todas en 0 hasta tener la tabla medida.
        "ventaja": {"rojo": 0, "verde": 0, "amarillo": 0, "nada": 0},
        "margen": 1,
    },
}

# El perfil que se usa cuando no se pide ninguno: el que el robot usaba antes
# de que hubiera perfiles. Asi detectar_color() sin argumentos no cambio.
PERFIL_POR_DEFECTO = "naba"

# Nombres de v2 (una sola tabla), para programas viejos que los importen.
COLORES = PERFILES[PERFIL_POR_DEFECTO]["tabla"]
VENTAJA = PERFILES[PERFIL_POR_DEFECTO]["ventaja"]


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
# se corre sobre la recta que une el origen con su centro. Medido con la tabla
# de la nacional [IA 2026-08-23]: con 20% mas de brillo el amarillo ya se
# alejo 15 unidades de su centro, y con 50% se alejo 37, mas que su limite de
# aceptacion. Si el brillo pesa igual que el color, ese corrimiento se cuenta
# como si fuera otro color: de cerca sale duda y de lejos el azul se vuelve
# negro.
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
# blanco y el negro son los dos casi sin color, o sea que sus rectas son casi
# la misma y solo cambia el brillo. Con un peso chico pero no nulo el detector
# degrada de a poco en vez de depender solo de la compuerta. [IA 2026-11-23]
# El costo de que sea chico se ve en "naba": la frontera blanco/negro cae
# cerca de la mitad del brillo del blanco (ver la ventaja del negro).
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
# VENTAJA negativa del negro; sin ella, aflojar aca fabrica negros equivocados
# en vez de dudas.
TOLERANCIA_BRILLO = 0.8

# ---------------------------------------------------------------------------
# PERILLA 4: MARGEN_MINIMO  --  por cuanto tiene que ganar el ganador
# ---------------------------------------------------------------------------
# Si el primero le gana al segundo por menos que esto, se contesta DUDA en vez
# del ganador. Es el seguro contra el error mas caro de todos: contestar un
# color equivocado CON CONFIANZA. Cada perfil puede tener el suyo ("margen" en
# PERFILES); este es el que usa un perfil que no dice nada.
#
# [VERIFICACION ADVERSARIAL 2026-08-23, con la tabla de la nacional] Sin esto,
# verde y azul se intercambiaban sin pasar nunca por duda: en el punto de
# empate los dos quedaban dentro de su limite de aceptacion, y un corrimiento
# sistematico de tono convertia un verde en azul, aceptado, sin ninguna senial.
# Con 1 aparecia una banda de duda entre los dos y el negro conservaba el
# 60-180% de su brillo; con 2 perdia la mitad de su rango util.
#   0 = apagado (el ganador contesta siempre, aunque gane por un pelo)
MARGEN_MINIMO = 1

# Debajo de este brillo se considera que no hay objeto adelante.
# [MEDIDO EN BANCO 2026-08-23, con la tabla de la nacional] "nada" daba brillo
# 0 exacto y el negro 14; 5 dejaba al negro todo su rango.
# [IA 2026-11-23] Con TABLA_NABA: "nada" da 1 y el negro 28. Con
# TOLERANCIA_BRILLO = 0.8 el negro se acepta hasta el 20% de su brillo (5.6):
# 5 sigue quedando por debajo, pero justo. chequear() lo revisa por perfil.
V_MINIMO = 5

# Codigo que devuelven las funciones cuando NO se puede decidir.
# Es distinto de 0 (nada) a proposito: son dos situaciones con reacciones
# opuestas. Con 0 el robot tiene que AVANZAR (no hay objeto); con DUDA tiene
# que RELEER o reacomodarse (hay algo pero no se reconoce).
DUDA = -1

# Diagnostico del ultimo duelo de cada perfil, para explicar(). No tocar.
# Es un diccionario (perfil -> resultado) porque con multitarea dos tareas
# pueden estar detectando con perfiles distintos al mismo tiempo.
_ultimo = {}

# Lo que ve cada vigilante (perfil -> estado). Lo llena vigilar(). No tocar.
_visto = {}

# Un ganador sin segundo (perfil de un solo color) no tiene contra quien medir
# el margen: se toma como margen enorme, no como cero (cero seria duda siempre).
_SIN_RIVAL = 999


# ---------------------------------------------------------------------------
# MEDICION
# ---------------------------------------------------------------------------

def _xyz(h, s, v):
    """Pasa el HSV al cono: la croma queda pesada por el brillo.

    A oscuras el tono es puro ruido, y multiplicarlo por el brillo lo anula
    solo. Ademas resuelve que el tono sea circular: el rojo esta cerca de la
    costura 0/360, donde una resta de tonos daria 350 en vez de 10.
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


async def medir_tarea(muestras=4):
    """medir() para usar dentro de una tarea: la MISMA cuenta, pero esperando
    con await, asi las otras tareas siguen corriendo mientras tanto.

    [IA 2026-11-23] medir() no sirve dentro de una tarea: ahi sensor.hsv()
    devuelve una espera pendiente y no un color (documentacion de Pybricks y
    firmware: pb_type_async_wait_or_await "returns an awaitable operation if
    the runloop is active"), y medir() se corta con AttributeError en m.h.

    Si cambias la cuenta de medir(), cambiala aca tambien:
    testing/test_colores_tareas.py falla si las dos dan distinto.
    """
    if muestras < 1:
        muestras = 1
    sx = sy = sz = 0
    for _ in range(muestras):
        m = await sensor.hsv()
        x, y, z = _xyz(m.h, m.s, m.v)
        sx += x; sy += y; sz += z
        await wait(20)        # el mismo ritmo que medir(): ver la medicion alla
    return sx / muestras, sy / muestras, sz / muestras


# ---------------------------------------------------------------------------
# AUXILIARES DE PERFILES Y TAREAS
# ---------------------------------------------------------------------------

def _clave(perfil):
    """Nombre del perfil, con None convertido al perfil por defecto."""
    return PERFIL_POR_DEFECTO if perfil is None else perfil


def _perfil(perfil):
    """(colores, tabla, ventaja, margen) del perfil. None = el por defecto."""
    p = PERFILES.get(_clave(perfil))
    if p is None:
        raise ValueError("perfil desconocido: " + str(perfil) +
                         " (los que hay estan en PERFILES)")
    return (p["colores"], p["tabla"], p.get("ventaja", {}),
            p.get("margen", MARGEN_MINIMO))


def _fila(nombre, tabla):
    """La fila de ese color en la tabla, o None si todavia no se midio."""
    for c in tabla:
        if c[1] == nombre:
            return c
    return None


def _en_tarea():
    """True si el programa esta corriendo tareas (run_task / multitask)."""
    if _run_task is None:
        return False
    try:
        return bool(_run_task())
    except Exception:
        # [IA 2026-11-23] Firmware anterior a 3.4.0b3: no acepta la pregunta
        # sin argumentos (se espera TypeError, pero no esta probado en un hub
        # viejo). Ante CUALQUIER error se contesta "no hay tareas", que es
        # exactamente como funcionaba v2: en plena ronda, mejor eso que cortar
        # el programa por una pregunta.
        return False


def _es_objetivo(cod, objetivo):
    """objetivo puede ser un codigo (4) o varios en una tupla ((1, 5))."""
    if isinstance(objetivo, int):
        return cod == objetivo
    return cod in objetivo


# ---------------------------------------------------------------------------
# CLASIFICACION
# ---------------------------------------------------------------------------

def competir(x, y, z, perfil=None):
    """El duelo, sin tocar el sensor. Devuelve el diccionario del resultado.

    Separada de medir() a proposito: asi la matematica se puede probar en una
    PC con puntos inventados, sin robot.

    perfil: que tabla y que VENTAJA se usan (ver PERFILES). Sin perfil, el
    PERFIL_POR_DEFECTO.
    """
    _colores, tabla, ventaja, _margen = _perfil(perfil)
    ganador = None
    segundo = None
    for cod, nombre, cx, cy, cz, radio in tabla:
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
        puntaje = (e_color * e_color + pb * pb) ** 0.5 - ventaja.get(nombre, 0)

        fila = (puntaje, dist, cod, nombre, radio, e_color, e_brillo, mag)
        if ganador is None or puntaje < ganador[0]:
            segundo = ganador
            ganador = fila
        elif segundo is None or puntaje < segundo[0]:
            segundo = fila

    if ganador is None:
        # la tabla del perfil no tiene ningun color medido (por ejemplo,
        # TABLA_RVA antes de calibrar): no hay a quien elegir
        return {"codigo": DUDA, "nombre": "duda", "dist": 0.0, "e_color": 0.0,
                "e_brillo": 0.0, "radio": 0, "limite": 0, "lim_brillo": 0,
                "aceptado": False, "segundo": "-", "ventaja": 0,
                "sin_candidatos": True}

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
        "ventaja": segundo[0] - ganador[0] if segundo else _SIN_RIVAL,
    }


def decidir(x, y, z, perfil=None):
    """La decision completa sobre un punto YA medido, sin tocar el sensor.

    Devuelve (codigo, diagnostico). Es exactamente lo que hace detectar_color()
    despues de medir; esta separada para que chequear() y los tests de la PC
    usen la MISMA cuenta que el robot.
    """
    # COMPUERTA DE BRILLO: sin luz que vuelva no hay objeto adelante. Se decide
    # antes del duelo porque "no hay nada" no es un color: es la ausencia de uno.
    if z < V_MINIMO:
        return 0, {"codigo": 0, "nombre": "nada", "dist": 0.0, "e_color": 0.0,
                   "e_brillo": 0.0, "radio": 0, "limite": 0, "lim_brillo": 0,
                   "aceptado": True, "segundo": "-", "ventaja": 0,
                   "compuerta": z}

    r = competir(x, y, z, perfil)
    margen = _perfil(perfil)[3]

    if r["codigo"] == 0:
        return 0, r
    if not r["aceptado"]:
        return DUDA, r
    if r["ventaja"] < margen:
        # gano por muy poco: entre dos colores parecidos, contestar el que
        # salio primero por un pelo es tirar una moneda con cara de certeza
        return DUDA, r
    return r["codigo"], r


def detectar_color(muestras=4, perfil=None):
    """0 nada | 1 amarillo | 2 blanco | 3 azul | 4 negro | 5 rojo | 6 verde | -1 duda

    [IA 2026-08-23] Estos codigos NO estan escritos a mano: salen de CODIGOS.
    Si cambias CODIGOS, cambia tambien esta linea y los bloques.
    testing/test_colores.py falla si esta linea y CODIGOS divergen.

    Sin perfil usa PERFIL_POR_DEFECTO ("naba"), o sea que contesta lo mismo que
    el detectar_color() que ya usan los programas de bloques del robot.

    [IA 2026-11-23] Sirve con y sin multitarea, igual que wait(): dentro de una
    tarea se escribe "await detectar_color(...)".
    """
    if _en_tarea():
        return _detectar_color_tarea(muestras, perfil)
    return _detectar_color_ahora(muestras, perfil)


def _detectar_color_ahora(muestras, perfil):
    x, y, z = medir(muestras)
    cod, r = decidir(x, y, z, perfil)
    _ultimo[_clave(perfil)] = r
    return cod


async def _detectar_color_tarea(muestras, perfil):
    x, y, z = await medir_tarea(muestras)
    cod, r = decidir(x, y, z, perfil)
    _ultimo[_clave(perfil)] = r
    return cod


# ---------------------------------------------------------------------------
# PARA BLOQUES  --  una funcion SIN argumentos por conjunto
# ---------------------------------------------------------------------------
# Se importan desde el Setup de los bloques ("from colores import ...") y se
# llaman como hoy se llama detectar_color. Misma lectura que detectar_color():
# 4 muestras promediadas, unos 80 ms.

def detectar_naba():
    """1 amarillo | 2 blanco | 3 azul | 4 negro | 0 nada | -1 duda"""
    return detectar_color(4, "naba")


def detectar_rva():
    """1 amarillo | 5 rojo | 6 verde | 0 nada | -1 duda"""
    return detectar_color(4, "rva")


def detectar_estable(muestras=3, perfil=None):
    """Antirrebote: devuelve el color solo si 2 de 3 lecturas coinciden.

    Si las tres discrepan devuelve -1 (duda), no 0: que el sensor no se ponga
    de acuerdo consigo mismo NO es lo mismo que no haber nada adelante.

    [IA 2026-11-23] v3: perfil y multitarea igual que detectar_color().
    """
    if _en_tarea():
        return _detectar_estable_tarea(muestras, perfil)
    a = _detectar_color_ahora(muestras, perfil)
    b = _detectar_color_ahora(muestras, perfil)
    if a == b:
        return a
    c = _detectar_color_ahora(muestras, perfil)
    return _voto(a, b, c)


async def _detectar_estable_tarea(muestras, perfil):
    a = await _detectar_color_tarea(muestras, perfil)
    b = await _detectar_color_tarea(muestras, perfil)
    if a == b:
        return a
    c = await _detectar_color_tarea(muestras, perfil)
    return _voto(a, b, c)


def _voto(a, b, c):
    """La tercera lectura desempata. Si las tres discrepan: duda."""
    if c == a or c == b:
        return c
    return DUDA


def esperar_color(objetivo, perfil=None, confirmaciones=2, muestras=1,
                  tiempo_max_ms=0):
    """Espera hasta ver `objetivo`: un codigo (4) o varios en una tupla (1, 5).

    Devuelve el codigo que vio, o None si pasaron tiempo_max_ms sin verlo
    (0 = sin limite). Pide `confirmaciones` lecturas IGUALES seguidas para no
    frenar por una lectura suelta en el borde entre dos colores. Con
    muestras=1 cada lectura tarda unos 20 ms, asi que 2 confirmaciones a
    150 mm/s son unos 6 mm de recorrido entre ver el color y decidir.

    Sin multitarea bloquea hasta verlo; con multitarea se escribe con await y
    las otras tareas siguen corriendo. Ejemplo en MULTITAREA, punto 4.
    """
    if _en_tarea():
        return _esperar_color_tarea(objetivo, perfil, confirmaciones,
                                    muestras, tiempo_max_ms)
    reloj = StopWatch()
    candidato = None
    seguidas = 0
    while True:
        cod = _detectar_color_ahora(muestras, perfil)
        if _es_objetivo(cod, objetivo):
            if cod == candidato:
                seguidas += 1
            else:
                candidato = cod
                seguidas = 1
            if seguidas >= confirmaciones:
                return cod
        else:
            candidato = None
            seguidas = 0
        if tiempo_max_ms > 0 and reloj.time() >= tiempo_max_ms:
            return None


async def _esperar_color_tarea(objetivo, perfil, confirmaciones, muestras,
                               tiempo_max_ms):
    # misma logica que la version sin tareas de esperar_color(), con await
    reloj = StopWatch()
    candidato = None
    seguidas = 0
    while True:
        cod = await _detectar_color_tarea(muestras, perfil)
        if _es_objetivo(cod, objetivo):
            if cod == candidato:
                seguidas += 1
            else:
                candidato = cod
                seguidas = 1
            if seguidas >= confirmaciones:
                return cod
        else:
            candidato = None
            seguidas = 0
        if tiempo_max_ms > 0 and reloj.time() >= tiempo_max_ms:
            return None


def vigilar(perfil=None, muestras=1, confirmaciones=2):
    """TAREA DE FONDO: lee el sensor sin parar y deja el ultimo color a mano.

    Corre en paralelo con la mision, que pregunta visto() sin tocar el sensor:
        await multitask(vigilar("naba"), mision(), race=True)
    race=True corta al vigilante (que no termina nunca solo) cuando la mision
    termina. Un color recien se da por visto con `confirmaciones` lecturas
    iguales seguidas.

    Solo tiene sentido con tareas: sin multitarea se quedaria leyendo para
    siempre y el programa no avanzaria. Por eso ahi da error en vez de colgarse.
    """
    if not _en_tarea():
        raise RuntimeError("vigilar() es una tarea: va adentro de "
                           "run_task / multitask")
    return _vigilar_tarea(perfil, muestras, confirmaciones)


async def _vigilar_tarea(perfil, muestras, confirmaciones):
    e = {"codigo": DUDA, "reloj": StopWatch(), "t": 0, "lecturas": 0,
         "candidato": None, "seguidas": 0}
    _visto[_clave(perfil)] = e
    while True:
        cod = await _detectar_color_tarea(muestras, perfil)
        e["lecturas"] += 1
        e["t"] = e["reloj"].time()
        if cod == e["candidato"]:
            e["seguidas"] += 1
        else:
            e["candidato"] = cod
            e["seguidas"] = 1
        if e["seguidas"] >= confirmaciones:
            e["codigo"] = cod


def visto(perfil=None, max_edad_ms=200):
    """Ultimo color CONFIRMADO por vigilar(perfil). No toca el sensor.

    Devuelve DUDA si no hay un vigilante de ese perfil, o si su ultima lectura
    tiene mas de max_edad_ms: un dato viejo no se usa como si fuera nuevo.
    Funcion comun (no lleva await), con o sin tareas.
    """
    e = _visto.get(_clave(perfil))
    if e is None:
        return DUDA
    if e["reloj"].time() - e["t"] > max_edad_ms:
        return DUDA
    return e["codigo"]


def informe_vigia(perfil=None):
    """Imprime que ve el vigilante, cuantas lecturas lleva y a que ritmo.

    El ritmo es el dato a mirar en banco: dice cuanto se lleva el resto de
    las tareas. Si baja mucho, alguna tarea esta tardando en ceder el lugar.
    """
    e = _visto.get(_clave(perfil))
    if e is None:
        print("no hay vigilante del perfil", _clave(perfil))
        return
    t = e["reloj"].time()
    ritmo = e["lecturas"] * 1000 / t if t > 0 else 0
    print("vigia", _clave(perfil), "| ve:", nombre_de(e["codigo"]),
          "| lecturas:", e["lecturas"], "|", round(ritmo, 1), "por segundo",
          "| la ultima hace", t - e["t"], "ms")


def nombre_de(cod):
    """Traduce el codigo a texto, para imprimir. -1 es duda."""
    if cod == DUDA:
        return "duda"
    for nombre in CODIGOS:
        if CODIGOS[nombre] == cod:
            return nombre
    return "?"


def explicar(perfil=None):
    """Imprime POR QUE dio lo que dio la ultima deteccion.

    Es la herramienta para tunear: dice quien gano, contra quien, y por cuanto.
    Si la ventaja sobre el segundo es chica, ese es el par que hay que separar.

    [IA 2026-11-23] v3: explica la ultima deteccion DE ESE perfil (con
    multitarea, otra tarea pudo haber detectado con otro perfil despues).
    """
    r = _ultimo.get(_clave(perfil))
    if r is None:
        print("todavia no hubo ninguna deteccion con el perfil", _clave(perfil))
        return

    if "sin_candidatos" in r:
        print("duda: la tabla del perfil", _clave(perfil), "esta vacia.",
              "Calibrarla con calibrar.py y correr chequear(perfil).")
        return

    if "compuerta" in r:
        print("nada: el brillo fue", round(r["compuerta"], 1),
              "y la compuerta V_MINIMO esta en", V_MINIMO)
        return

    print("perfil", _clave(perfil), "| gano:", r["nombre"], "| 2do:",
          r["segundo"], "| le gano por:", round(r["ventaja"], 1))

    print("  error de COLOR: ", round(r["e_color"], 1),
          "de", round(r["limite"], 1), "permitido")
    print("  error de BRILLO:", round(r["e_brillo"], 1),
          "de", round(r["lim_brillo"], 1), "permitido",
          "(+ = mas cerca que al calibrar, - = mas lejos)")
    # decir CUAL de los dos causo la duda es la mitad del valor de esto
    if not r["aceptado"]:
        if r["e_color"] > r["limite"]:
            print("  RECHAZADO POR COLOR -> recalibrar ese color,",
                  "o subir su radio en la tabla del perfil")
        else:
            print("  RECHAZADO POR BRILLO -> el objeto esta a otra distancia",
                  "que cuando se calibro. Arreglar el tope mecanico,",
                  "o subir TOLERANCIA_BRILLO")
    elif r["ventaja"] < _perfil(perfil)[3]:
        print("  DUDA POR MARGEN: gano por menos que el margen del perfil")
    else:
        print("  ACEPTADO")

    if r["ventaja"] < 2:
        print("  OJO: gano por muy poco. Ese es el par a separar,",
              "o donde subir la ventaja en el perfil.")


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


def chequear(perfil=None):
    """Revisa un perfil y avisa donde la clasificacion puede fallar.

    Mide lo que de verdad decide el resultado: donde cae la FRONTERA entre cada
    par de colores, comparada con el ruido de la medicion. Un solape de radios
    no puede provocar una confusion entre dos colores; una frontera adentro del
    ruido, si.

    [IA 2026-11-23] v3: revisa UN perfil (sin argumento, el por defecto): que
    sus colores esten medidos y con el codigo de CODIGOS, los margenes con SU
    ventaja, que "nada" quede debajo de la compuerta, y el firmware.
    """
    avisos = 0
    clave = _clave(perfil)
    colores, tabla, ventaja, margen = _perfil(perfil)
    print("perfil", clave, "->", ", ".join(colores), "| margen:", margen)

    # 1) la tabla, los colores del perfil, CODIGOS y la ventaja tienen que
    #    hablar de lo mismo
    for nombre in colores:
        if nombre not in CODIGOS:
            print("ERROR:", nombre, "no tiene codigo en CODIGOS")
            avisos += 1
        if _fila(nombre, tabla) is None:
            print("FALTA MEDIR:", nombre, "- correr calibrar.py con PERFIL =",
                  '"' + clave + '"')
            avisos += 1
        if nombre not in ventaja:
            print("ojo:", nombre, "no tiene ventaja en el perfil: vale 0")
    for c in tabla:
        if c[1] not in colores:
            print("ERROR:", c[1], "esta en la tabla pero no en los colores",
                  "del perfil")
            avisos += 1
        elif CODIGOS.get(c[1]) != c[0]:
            print("ERROR:", c[1], "tiene el codigo", c[0], "en la tabla y",
                  CODIGOS.get(c[1]), "en CODIGOS: los bloques recibirian",
                  "otro numero")
            avisos += 1
    for nombre in ventaja:
        if nombre not in colores:
            print("ERROR:", nombre, "tiene ventaja en el perfil pero no esta",
                  "entre sus colores (typo?)")
            avisos += 1

    print("PESO_BRILLO =", PESO_BRILLO, "| GANANCIA =", GANANCIA,
          "| TOLERANCIA_BRILLO =", TOLERANCIA_BRILLO)

    # 2) que margen tiene cada color contra cada rival, con la MISMA cuenta
    #    que usa el duelo. Se mira el peor de los dos sentidos.
    #    "nada" no compite: lo maneja V_MINIMO.
    filas = [c for c in tabla if c[0] != 0]
    n = len(filas)
    for i in range(n):
        for j in range(i + 1, n):
            a = filas[i]
            b = filas[j]
            # margen de A contra B, corrido por la diferencia de ventajas
            dv = (ventaja.get(a[1], 0) - ventaja.get(b[1], 0))
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

    # 3) la compuerta de brillo: "nada" tiene que quedar debajo, y el borde
    #    oscuro de cada color (lo que deja TOLERANCIA_BRILLO), arriba
    for c in tabla:
        if c[0] == 0:
            if c[4] >= V_MINIMO:
                print("PELIGRO: 'nada' se midio con brillo", c[4],
                      "y la compuerta V_MINIMO esta en", V_MINIMO,
                      ": no la separa")
                avisos += 1
        elif c[4] * (1 - TOLERANCIA_BRILLO) < V_MINIMO:
            print("ojo:", c[1], "se acepta hasta brillo",
                  round(c[4] * (1 - TOLERANCIA_BRILLO), 1),
                  "pero debajo de", V_MINIMO, "ya es 'nada'")

    # 4) las perillas globales
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

    # 5) con que firmware se midio la tabla
    avisos += _chequear_firmware(PERFILES[clave].get("firmware", "?"))

    if avisos == 0:
        print("tablas OK")
    return avisos


def _chequear_firmware(firmware_tabla):
    """Avisa si la tabla se midio con otro firmware que el del hub."""
    fw = None
    try:
        from pybricks import version
        fw = version[1]
    except ImportError:
        pass
    if firmware_tabla == "?":
        print("ojo: no esta anotado con que firmware se midio la tabla.",
              "El hub tiene:", fw if fw else "?")
        print("     El firmware 4.0.0b3 cambio la cuenta del HSV: una tabla",
              "medida de un lado y usada del otro da colores corridos.")
        return 1
    if fw is not None and fw != firmware_tabla:
        print("PELIGRO: la tabla se midio con el firmware", firmware_tabla,
              "y el hub tiene", fw + ".",
              "Si entre medio cambio la cuenta del HSV, la tabla no vale:",
              "volver a calibrar.")
        return 1
    return 0
