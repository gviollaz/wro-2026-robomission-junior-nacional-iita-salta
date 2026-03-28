# 03 - Seguimiento de Línea con 2 Sensores

## ¿Por qué usar 2 sensores?

Con 1 sensor podés seguir la línea, pero no podés detectar intersecciones ni saber cuándo llegaste al final. Con **2 sensores** separados, el robot puede:

- Seguir la línea de forma más estable
- **Detectar intersecciones** (cuando un sensor lateral ve negro)
- **Alinearse** perpendicular a una línea
- Saber si llegó al **final** de la línea

## Dos formas de ubicar los sensores

### Opción A: Sensores a los costados de la línea ("a caballo")

```
         Dirección de avance
              ↑
        [Sensor L]  [Sensor R]
            ○          ○
   Blanco   │██ NEGRO ██│   Blanco
            │           │
```

Los sensores van uno a cada lado de la línea. Ambos deberían ver **blanco** cuando el robot está centrado.

### Opción B: Un sensor sobre la línea + uno al costado

```
         Dirección de avance
              ↑
        [Sensor L]  [Sensor R]
            ○          ○
   Blanco   │████ NEGRO ████│   Blanco
            │  ↑             │
            │  sensor L      │
            │  sobre la línea│
```

Un sensor sigue el borde (como con 1 sensor) y el otro detecta intersecciones.

**Recomendación para WRO:** La Opción A es más fácil de programar y más versátil.

## Seguimiento con 2 sensores "a caballo" — Método diferencial

### La idea

Cuando el robot está centrado, **ambos sensores ven blanco** (reflexión similar). Si se desvía a la izquierda, el sensor izquierdo empieza a ver negro. Si se desvía a la derecha, el sensor derecho ve negro.

```
error = sensor_izquierdo.reflection() - sensor_derecho.reflection()
```

- **error = 0** → ambos ven igual → ir derecho
- **error positivo** → izquierdo ve más blanco que derecho → desviado a la derecha → corregir izquierda
- **error negativo** → derecho ve más blanco que izquierdo → desviado a la izquierda → corregir derecha

### Código PID con 2 sensores

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=112)

sensor_izq = ColorSensor(Port.C)
sensor_der = ColorSensor(Port.D)

# --- Parámetros ---
VELOCIDAD = 200   # mm/s (podemos ir más rápido con 2 sensores)
Kp = 0.8          # Suele ser menor que con 1 sensor
Ki = 0.005
Kd = 4.0

# --- Variables ---
error_anterior = 0
integral = 0

while True:
    # Error = diferencia entre sensores
    error = sensor_izq.reflection() - sensor_der.reflection()
    
    # PID
    integral = max(-100, min(100, integral + error))
    P = Kp * error
    I = Ki * integral
    D = Kd * (error - error_anterior)
    error_anterior = error
    
    correccion = P + I + D
    robot.drive(VELOCIDAD, correccion)
    wait(10)
```

### Ventajas del método diferencial

- **Más estable** que con 1 sensor porque tiene "dos ojos"
- **Auto-calibrado parcial**: como restamos un sensor del otro, diferencias de iluminación ambiente se cancelan
- **Más rápido**: puede ir a mayor velocidad porque corrige antes de perder la línea

## Detección de intersecciones con 2 sensores

Con los sensores "a caballo", una intersección se detecta cuando **uno o ambos sensores ven negro**.

```
Situación normal (sobre la línea):
  Sensor L = blanco (alto)    Sensor R = blanco (alto)

Intersección a la izquierda:
  Sensor L = NEGRO (bajo!)    Sensor R = blanco (alto)

Intersección a la derecha:
  Sensor L = blanco (alto)    Sensor R = NEGRO (bajo!)

Cruce (intersección en T o +):
  Sensor L = NEGRO (bajo!)    Sensor R = NEGRO (bajo!)

Fin de línea (ambos en blanco, ninguna línea):
  Sensor L = blanco (alto)    Sensor R = blanco (alto)
  (pero no había línea en el medio tampoco)
```

### Código para detectar intersecciones

```python
UMBRAL_NEGRO = 25  # Si la reflexión es menor a esto, es negro

def es_negro(sensor):
    """Retorna True si el sensor está sobre negro"""
    return sensor.reflection() < UMBRAL_NEGRO

def detectar_interseccion(sensor_izq, sensor_der):
    """
    Detecta qué tipo de intersección hay.
    Retorna: "ninguna", "izquierda", "derecha", "ambas"
    """
    izq_negro = es_negro(sensor_izq)
    der_negro = es_negro(sensor_der)
    
    if izq_negro and der_negro:
        return "ambas"       # Cruce en T, + o fin ancho
    elif izq_negro:
        return "izquierda"   # Bifurcación a la izquierda
    elif der_negro:
        return "derecha"     # Bifurcación a la derecha
    else:
        return "ninguna"     # Seguir normal
```

## Seguir línea y contar intersecciones

Este es uno de los patrones más útiles en WRO: seguir la línea y detenerse en la N-ésima intersección.

```python
def seguir_hasta_interseccion(robot, sensor_izq, sensor_der,
                               lado="izquierda", numero=1,
                               velocidad=150, kp=0.8, kd=4.0):
    """
    Sigue la línea y se detiene cuando detecta la N-ésima
    intersección del lado indicado.
    
    lado: "izquierda", "derecha" o "ambas"
    numero: en cuál intersección detenerse (1, 2, 3...)
    """
    UMBRAL_NEGRO = 25
    conteo = 0
    en_interseccion = False  # Para no contar la misma 2 veces
    error_anterior = 0
    
    while True:
        refl_izq = sensor_izq.reflection()
        refl_der = sensor_der.reflection()
        
        # --- Seguimiento de línea (PID diferencial) ---
        error = refl_izq - refl_der
        D = kd * (error - error_anterior)
        error_anterior = error
        correccion = kp * error + D
        robot.drive(velocidad, correccion)
        
        # --- Detección de intersección ---
        if lado == "izquierda":
            interseccion_detectada = refl_izq < UMBRAL_NEGRO
        elif lado == "derecha":
            interseccion_detectada = refl_der < UMBRAL_NEGRO
        else:  # "ambas"
            interseccion_detectada = (refl_izq < UMBRAL_NEGRO and 
                                      refl_der < UMBRAL_NEGRO)
        
        if interseccion_detectada and not en_interseccion:
            # Entramos a una nueva intersección
            conteo += 1
            en_interseccion = True
            print("Intersección", conteo, "de", lado)
            
            if conteo >= numero:
                robot.stop()
                return conteo
        
        elif not interseccion_detectada:
            # Salimos de la intersección
            en_interseccion = False
        
        wait(10)
```

### ¿Qué es el "debounce" (anti-rebote)?

La variable `en_interseccion` es muy importante. Sin ella, el robot podría contar la **misma intersección varias veces** porque el sensor pasa varios milisegundos sobre el negro de la intersección.

```
Sin debounce:
  Sensor entra al negro: conteo = 1
  Sensor sigue en negro: conteo = 2  ← ¡ERROR! Es la misma
  Sensor sigue en negro: conteo = 3  ← ¡ERROR!
  Sensor sale del negro

Con debounce:
  Sensor entra al negro: conteo = 1, en_interseccion = True
  Sensor sigue en negro: en_interseccion ya es True → no contar
  Sensor sale del negro: en_interseccion = False
  (Listo para la próxima intersección)
```

## Alineación con 2 sensores

Cuando el robot llega a una línea perpendicular y necesita alinearse (ponerse derecho), puede usar los 2 sensores para **cuadrar** (squaring):

```python
def alinear_en_linea(robot, left_motor, right_motor, 
                      sensor_izq, sensor_der, velocidad=100):
    """
    Avanza hasta que ambos sensores estén sobre la línea,
    alineando el robot perpendicular a ella.
    """
    UMBRAL_NEGRO = 25
    
    izq_encontro = False
    der_encontro = False
    
    # Avanzar hasta que alguno encuentre la línea
    left_motor.run(velocidad)
    right_motor.run(velocidad)
    
    while not (izq_encontro and der_encontro):
        if sensor_izq.reflection() < UMBRAL_NEGRO:
            if not izq_encontro:
                left_motor.stop()
                izq_encontro = True
        
        if sensor_der.reflection() < UMBRAL_NEGRO:
            if not der_encontro:
                right_motor.stop()
                der_encontro = True
        
        wait(10)
    
    # Ambos sobre la línea → robot alineado
    left_motor.stop()
    right_motor.stop()
```

### ¿Cómo funciona la alineación?

```
Paso 1: Robot se acerca torcido a una línea perpendicular

     [S_L]    [S_R]
       ○        ○       ← ambos en blanco
       
  ═══════════════════   ← línea perpendicular

Paso 2: Sensor derecho llega primero → motor derecho frena

     [S_L]    [S_R]
       ○      ──○──     ← derecho sobre negro, motor der frena
              ═════
  ═══════════════════

Paso 3: Sensor izquierdo llega → motor izquierdo frena

     [S_L]    [S_R]
     ──○──    ──○──     ← ambos sobre negro → ¡alineado!
  ═══════════════════
```

## Resumen de capacidades con 2 sensores

| Capacidad | ¿Se puede? | Calidad |
|-----------|-----------|---------|
| Seguir línea | ✅ Sí | ⭐⭐⭐ Excelente |
| Detectar intersección izq. | ✅ Sí | ⭐⭐ Buena |
| Detectar intersección der. | ✅ Sí | ⭐⭐ Buena |
| Contar intersecciones | ✅ Sí | ⭐⭐ Buena |
| Alinearse en línea | ✅ Sí | ⭐⭐⭐ Excelente |
| Seguir + detectar al mismo tiempo | ⚠️ Parcial | ⭐ A veces se confunde |

**Limitación principal:** Cuando los sensores están "a caballo" de la línea, una intersección hace que un sensor vea negro, lo que **también se parece a una curva normal**. Esto puede causar falsos positivos. Para resolver esto → ver 3 sensores.
