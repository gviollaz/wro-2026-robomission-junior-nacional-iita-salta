# 04 - Seguimiento de Línea con 3 Sensores

## ¿Por qué 3 sensores?

Con 3 sensores tenés **lo mejor de ambos mundos**:

- El sensor **central** sigue el borde de la línea (como con 1 sensor) → navegación suave
- Los sensores **laterales** detectan intersecciones → conteo confiable sin confundir con curvas

```
          Dirección de avance
                ↑
   [S_Izq]   [S_Centro]   [S_Der]
      ○          ○           ○
 Blanco  │████ NEGRO ████│  Blanco
         │   ↑            │
         │   sensor centro│
         │   sigue borde  │
```

## Ubicación física de los sensores

### Configuración recomendada

```
  ┌─────────────────────────────┐
  │         SPIKE HUB           │
  │                             │
  ├──┐                     ┌──┤
  │  │ Motor Izq   Motor Der│  │
  │  └──┐             ┌──┘  │
  │     ⊙             ⊙     │  ← Ruedas
  │                         │
  │  ○       ○       ○      │
  │ S_Izq  S_Centro  S_Der  │  ← Sensores de color
  │                         │
  │  ←2cm→  ←2cm→  ←2cm→   │
  └─────────────────────────────┘
         Frente del robot

Separación típica entre sensores: 15-25 mm
El sensor central debe estar sobre el BORDE de la línea
Los laterales deben estar en zona BLANCA cuando están sobre la línea
```

### Medidas clave

- **Sensor central**: sobre el borde de la línea (izquierdo o derecho)
- **Sensor lateral izquierdo**: ~15-20mm a la izquierda del central, sobre blanco
- **Sensor lateral derecho**: ~15-20mm a la derecha del central, sobre blanco
- **Distancia al piso**: 5-15mm (lo más cerca posible sin tocar)

**Dato WRO:** Las líneas del tapete tienen ~20mm de ancho. Los sensores laterales deben estar lo suficientemente lejos para no ver la línea en condiciones normales, pero lo suficientemente cerca para detectar intersecciones rápido.

## El algoritmo completo

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
sensor_centro = ColorSensor(Port.D)
sensor_der = ColorSensor(Port.E)

# --- Calibración ---
NEGRO = 10
BLANCO = 90
UMBRAL = (NEGRO + BLANCO) / 2
UMBRAL_INTERSECCION = 25  # Para sensores laterales

# --- Parámetros PID (para sensor central) ---
VELOCIDAD = 180
Kp = 1.5
Ki = 0.01
Kd = 5.0

# --- Variables de estado ---
error_anterior = 0
integral = 0

def leer_todo():
    """Lee los 3 sensores y retorna un diccionario"""
    return {
        "izq": sensor_izq.reflection(),
        "centro": sensor_centro.reflection(),
        "der": sensor_der.reflection(),
        "inter_izq": sensor_izq.reflection() < UMBRAL_INTERSECCION,
        "inter_der": sensor_der.reflection() < UMBRAL_INTERSECCION,
    }

def seguir_linea_3s(borde="izquierdo"):
    """Un ciclo de seguimiento con sensor central. Llamar en while loop."""
    global error_anterior, integral
    
    if borde == "izquierdo":
        error = sensor_centro.reflection() - UMBRAL
    else:
        error = UMBRAL - sensor_centro.reflection()
    
    integral = max(-100, min(100, integral + error))
    P = Kp * error
    I = Ki * integral
    D = Kd * (error - error_anterior)
    error_anterior = error
    
    correccion = P + I + D
    robot.drive(VELOCIDAD, correccion)

def resetear_pid():
    """Resetear estado del PID (llamar al cambiar de tramo)"""
    global error_anterior, integral
    error_anterior = 0
    integral = 0
```

## Seguir línea y detenerse en la N-ésima intersección

```python
def seguir_hasta_interseccion(lado="izquierda", numero=1,
                               borde="izquierdo", velocidad=180):
    """
    Sigue la línea con el sensor central y se detiene cuando 
    detecta la N-ésima intersección del lado indicado usando
    los sensores laterales.
    
    lado: "izquierda", "derecha" o "ambas" (cruce en T o +)
    numero: en qué intersección parar (1, 2, 3...)
    borde: "izquierdo" o "derecho" (qué borde sigue el sensor central)
    """
    global VELOCIDAD
    vel_original = VELOCIDAD
    VELOCIDAD = velocidad
    resetear_pid()
    
    conteo = 0
    en_interseccion = False
    
    while True:
        lecturas = leer_todo()
        
        # Seguimiento con sensor central
        seguir_linea_3s(borde)
        
        # Detección de intersección con sensores laterales
        if lado == "izquierda":
            detectado = lecturas["inter_izq"]
        elif lado == "derecha":
            detectado = lecturas["inter_der"]
        else:  # "ambas"
            detectado = lecturas["inter_izq"] and lecturas["inter_der"]
        
        # Anti-rebote (debounce)
        if detectado and not en_interseccion:
            conteo += 1
            en_interseccion = True
            hub.light.on(Color.GREEN)  # Feedback visual
            
            if conteo >= numero:
                robot.stop()
                VELOCIDAD = vel_original
                hub.light.off()
                return conteo
        
        elif not detectado:
            en_interseccion = False
            hub.light.off()
        
        wait(10)
    
    VELOCIDAD = vel_original
```

### Ejemplos de uso

```python
# Seguir línea y parar en la 2da intersección a la izquierda
seguir_hasta_interseccion(lado="izquierda", numero=2)

# Seguir línea y parar en la 1ra intersección a la derecha
seguir_hasta_interseccion(lado="derecha", numero=1)

# Seguir línea y parar en el 3er cruce (ambos lados)
seguir_hasta_interseccion(lado="ambas", numero=3)

# Seguir por borde derecho y parar en 1ra intersección izquierda
seguir_hasta_interseccion(lado="izquierda", numero=1, borde="derecho")
```

## Seguir línea y DESVIARSE en una intersección

A veces no querés parar en la intersección sino **girar** y tomar la otra línea.

```python
def seguir_y_girar(lado_giro="izquierda", en_interseccion_numero=1,
                    borde="izquierdo", velocidad=180):
    """
    Sigue la línea y cuando llega a la N-ésima intersección,
    gira para tomar la nueva línea.
    
    lado_giro: "izquierda" o "derecha"
    en_interseccion_numero: en cuál intersección girar
    """
    # Primero, llegar a la intersección
    seguir_hasta_interseccion(
        lado=lado_giro, 
        numero=en_interseccion_numero,
        borde=borde,
        velocidad=velocidad
    )
    
    # Ahora girar
    if lado_giro == "izquierda":
        angulo_giro = -90  # Negativo = izquierda
    else:
        angulo_giro = 90   # Positivo = derecha
    
    # Avanzar un poco para que el centro del robot esté en la intersección
    robot.straight(30)  # Ajustar según geometría del robot
    
    # Girar
    robot.turn(angulo_giro)
    
    # Avanzar un poco para encontrar la nueva línea
    robot.straight(20)
    
    # Resetear PID para el nuevo tramo
    resetear_pid()
```

### Versión avanzada: girar y buscar la línea

```python
def girar_y_buscar_linea(angulo, sensor_busqueda, velocidad_giro=100):
    """
    Gira el robot y se detiene cuando el sensor de búsqueda
    encuentra la línea. Más preciso que girar un ángulo fijo.
    
    angulo: ángulo aproximado (positivo = derecha, negativo = izquierda)
    sensor_busqueda: el sensor que debe encontrar la línea
    """
    UMBRAL_NEGRO = 30
    
    # Girar un poco primero para salir de la línea actual
    robot.turn(angulo * 0.5)
    
    # Ahora girar lento hasta encontrar la nueva línea
    if angulo > 0:
        robot.drive(0, velocidad_giro)  # Girar derecha
    else:
        robot.drive(0, -velocidad_giro)  # Girar izquierda
    
    # Esperar a que el sensor encuentre negro
    while sensor_busqueda.reflection() > UMBRAL_NEGRO:
        wait(10)
    
    robot.stop()
    resetear_pid()
```

## Detección de fin de línea

Con 3 sensores podés detectar confiablemente cuándo la línea se terminó:

```python
def seguir_hasta_fin_de_linea(borde="izquierdo", velocidad=150):
    """
    Sigue la línea hasta que los 3 sensores vean blanco
    (la línea se terminó).
    """
    global VELOCIDAD
    VELOCIDAD = velocidad
    resetear_pid()
    
    UMBRAL_BLANCO = 70  # Si los 3 están arriba de esto → no hay línea
    contador_blanco = 0
    
    while True:
        seguir_linea_3s(borde)
        
        # Verificar si los 3 sensores ven blanco
        if (sensor_izq.reflection() > UMBRAL_BLANCO and
            sensor_centro.reflection() > UMBRAL_BLANCO and
            sensor_der.reflection() > UMBRAL_BLANCO):
            contador_blanco += 1
            # Esperar varias lecturas para confirmar (evitar falso positivo)
            if contador_blanco > 5:
                robot.stop()
                return
        else:
            contador_blanco = 0
        
        wait(10)
```

## Tabla comparativa: 1 vs 2 vs 3 sensores

| Capacidad | 1 Sensor | 2 Sensores | 3 Sensores |
|-----------|----------|------------|------------|
| Seguir línea | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Velocidad máxima | Baja | Alta | Alta |
| Detectar intersección | ❌ | ⚠️ Confusión con curvas | ✅ Confiable |
| Contar intersecciones | ❌ | ⚠️ | ✅ |
| Distinguir curva de intersección | ❌ | ❌ | ✅ |
| Detectar fin de línea | ❌ | ⚠️ | ✅ |
| Alinearse en línea | ❌ | ✅ | ✅ |
| Puertos usados | 1 | 2 | 3 |
| Complejidad del código | Baja | Media | Media-Alta |

## Recomendación para WRO RoboMission

**Usá 3 sensores siempre que puedas.** En WRO RoboMission, los puertos de SPIKE Prime son limitados (6 puertos para todo), así que necesitás planificar:

- 2 puertos para motores de tracción
- 3 puertos para sensores de color
- 1 puerto para motor de mecanismo (brazo, pinza, etc.)

Esto usa todos los 6 puertos. Si necesitás más motores para mecanismos, podrías bajar a 2 sensores y usar el puerto libre para otro motor.
