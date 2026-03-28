# Detección de Colores en WRO RoboMission — Guía Completa

## ¿Por qué es difícil detectar colores?

El sensor de color de SPIKE Prime no "ve" colores como nuestros ojos. Mide la luz que rebota de una superficie y la descompone en componentes. El problema es que la misma pieza LEGO roja puede verse distinta según la luz del salón, la distancia del sensor, el ángulo, y hasta la carga de la batería. Los equipos ganadores de WRO no confían en el `color()` por defecto — calibran sus propios colores.

## Índice

| Sección | Contenido |
|---------|----------|
| 1 | RGB vs HSV: por qué HSV es mejor para robots |
| 2 | Cómo mide colores el sensor SPIKE Prime |
| 3 | Método Pybricks: `detectable_colors()` con HSV calibrado |
| 4 | Método avanzado: distancia euclidiana en espacio HSV |
| 5 | Protocolo de lectura: parar, esperar, leer, promediar |
| 6 | Feedback no-bloqueante: beep + luz + display sin frenar |
| 7 | Ubicación física del sensor |
| 8 | Programa de calibración interactivo |
| 9 | Problemas comunes y soluciones |

---

## 1. RGB vs HSV: por qué HSV es mejor

### RGB (Rojo, Verde, Azul)

El sensor mide cuánta luz roja, verde y azul rebota. El problema es que si la luz ambiente cambia, los TRES valores cambian. Una pieza roja en una sala oscura tiene RGB muy diferente a la misma pieza en una sala iluminada.

### HSV (Tono, Saturación, Valor/Brillo)

- **H (Hue/Tono):** QUÉ color es (0-359°, como un círculo de colores). Rojo≈30°, Amarillo≈60°, Verde≈120°, Azul≈220°
- **S (Saturación):** Qué tan "puro" es el color (0=gris, 100=color puro)
- **V (Value/Brillo):** Qué tan brillante es (0=negro, 100=brillante)

**La ventaja clave:** cuando la luz ambiente cambia, el **Hue casi no cambia**. Solo cambian S y V. Entonces si comparamos por Hue, somos mucho más inmunes a diferencias de iluminación.

```
Misma pieza roja:
  Sala oscura:    H=355, S=80, V=30  ← V bajo pero H sigue siendo ~355
  Sala iluminada: H=358, S=85, V=75  ← V alto pero H sigue siendo ~358
  Bajo lámpara:   H=352, S=90, V=95  ← H sigue siendo ~352-358
```

Por eso **siempre trabajamos en HSV**, no en RGB.

---

## 2. Cómo mide el sensor SPIKE Prime

El sensor de color de SPIKE Prime tiene 3 LEDs (luz propia) y un fotodetector. Pybricks ofrece:

```python
sensor = ColorSensor(Port.D)

sensor.color()       # Retorna Color.RED, Color.BLUE, etc. (redondeado)
sensor.hsv()         # Retorna Color(h=XXX, s=XXX, v=XXX) (valor crudo)
sensor.reflection()  # Retorna 0-100 (solo brillo, para líneas)
```

`color()` internamente llama a `hsv()` y busca el color más cercano de la lista `detectable_colors()`. Nosotros podemos personalizar esa lista.

---

## 3. Método Pybricks: `detectable_colors()` con HSV calibrado

Este es el método recomendado por Pybricks y el que usan los equipos de FLL/WRO más exitosos.

### Paso 1: Medir HSV de cada color objetivo

```python
from pybricks.pupdevices import ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait

sensor = ColorSensor(Port.D)

while True:
    hsv = sensor.hsv()
    print("H=", hsv.h, "S=", hsv.s, "V=", hsv.v)
    wait(500)
```

Poné cada objeto de color debajo del sensor a la distancia real de competencia. Anotá los valores H, S, V de cada uno.

### Paso 2: Definir colores personalizados

```python
from pybricks.parameters import Color

# Valores MEDIDOS con tu sensor, a la distancia real
Color.MI_ROJO    = Color(h=355, s=82, v=45)
Color.MI_AZUL    = Color(h=218, s=85, v=50)
Color.MI_VERDE   = Color(h=140, s=70, v=35)
Color.MI_AMARILLO = Color(h=55, s=65, v=90)
Color.MI_BLANCO  = Color(h=0,   s=0,  v=95)
Color.MI_NEGRO   = Color(h=0,   s=0,  v=8)
Color.NADA       = Color(h=0,   s=0,  v=0)

mis_colores = (
    Color.MI_ROJO, Color.MI_AZUL, Color.MI_VERDE,
    Color.MI_AMARILLO, Color.MI_BLANCO, Color.MI_NEGRO,
    Color.NADA
)

sensor.detectable_colors(mis_colores)
```

### Paso 3: Usar normalmente

```python
color = sensor.color()  # Ahora retorna MI_ROJO, MI_AZUL, etc.
```

Pybricks internamente calcula la **distancia** en el espacio HSV cilíndrico entre la lectura actual y cada color definido, y retorna el más cercano.

**Tip de equipos ganadores:** Solo incluir en la lista los colores que realmente vas a usar en la misión. Menos colores = menos confusión.

---

## 4. Método avanzado: clasificador por distancia euclidiana con sensibilidad por color

El `detectable_colors()` de Pybricks es bueno, pero trata todos los colores igual. A veces necesitás que el robot sea más "exigente" con algunos colores (por ejemplo, distinguir rojo de naranja requiere más precisión que distinguir rojo de azul).

### La idea: distancia ponderada en espacio HSV

Para cada color objetivo, definimos no solo el H, S, V esperado sino también los **pesos** (qué tan importante es cada componente para ese color).

```python
import math

# Definición de colores con pesos (sensibilidad)
# Formato: (nombre, h, s, v, peso_h, peso_s, peso_v, umbral_max)
COLORES_OBJETIVO = [
    ("ROJO",     355, 82, 45,  2.0, 1.0, 0.5,  60),
    ("AZUL",     218, 85, 50,  2.0, 1.0, 0.5,  60),
    ("VERDE",    140, 70, 35,  2.0, 1.0, 0.5,  60),
    ("AMARILLO",  55, 65, 90,  2.0, 0.8, 0.3,  50),
    ("BLANCO",     0,  5, 95,  0.1, 2.0, 1.5,  40),
    ("NEGRO",      0,  5,  8,  0.1, 0.5, 2.0,  30),
]

def distancia_hue(h1, h2):
    """Distancia circular en hue (0-360 es cíclico)."""
    d = abs(h1 - h2)
    return min(d, 360 - d)

def clasificar_color(sensor):
    """
    Lee el sensor y retorna el nombre del color más cercano,
    o "DESCONOCIDO" si ninguno está suficientemente cerca.
    """
    hsv = sensor.hsv()
    h, s, v = hsv.h, hsv.s, hsv.v
    
    mejor_nombre = "DESCONOCIDO"
    mejor_distancia = 9999
    
    for nombre, ch, cs, cv, wh, ws, wv, umbral in COLORES_OBJETIVO:
        dh = distancia_hue(h, ch) * wh
        ds = abs(s - cs) * ws
        dv = abs(v - cv) * wv
        dist = math.sqrt(dh*dh + ds*ds + dv*dv)
        
        if dist < mejor_distancia and dist < umbral:
            mejor_distancia = dist
            mejor_nombre = nombre
    
    return mejor_nombre
```

### ¿Por qué pesos diferentes?

| Color | Hue importante? | Saturación importante? | Brillo importante? |
|-------|----------------|----------------------|---------------------|
| Rojo, Azul, Verde | SÍ (peso alto) | Medio | Bajo |
| Blanco | NO (H es ruidoso) | SÍ (debe ser baja) | SÍ (debe ser alto) |
| Negro | NO (H es ruidoso) | Bajo | SÍ (debe ser bajo) |
| Amarillo vs Naranja | MUY alto | Medio | Bajo |

Para blanco y negro, el Hue es basura (cuando S es baja, H es ruidoso e inestable). Por eso le damos peso bajo al H y alto al V.

### ¿Qué es el umbral_max?

Es la distancia máxima permitida para aceptar un color. Si la lectura está más lejos que el umbral de TODOS los colores, retorna "DESCONOCIDO". Esto evita clasificar erróneamente un color que no está en nuestra lista.

---

## 5. Protocolo de lectura: parar, esperar, leer, promediar

El error #1 de equipos novatos es **leer el color mientras el robot se mueve**. El sensor necesita ~50ms para tomar una buena lectura, y si el robot se mueve, la lectura se contamina con el color adyacente.

### El protocolo correcto

```python
def leer_color_preciso(sensor, robot, lecturas=5, espera_ms=50):
    """
    1. Para el robot
    2. Espera a que se estabilice
    3. Toma N lecturas
    4. Retorna el color más frecuente (voto mayoritario)
    """
    robot.stop()
    wait(200)  # Esperar a que el robot esté realmente quieto
    
    votos = {}
    for i in range(lecturas):
        c = sensor.color()
        nombre = str(c)
        votos[nombre] = votos.get(nombre, 0) + 1
        wait(espera_ms)
    
    # Retornar el color con más votos
    ganador = max(votos, key=votos.get)
    confianza = votos[ganador] / lecturas * 100
    
    return sensor.color(), confianza
```

### Versión con promedio HSV (más robusta)

```python
def leer_hsv_promedio(sensor, robot, lecturas=5, espera_ms=50):
    """
    Toma N lecturas HSV y promedia. Más robusto que voto mayoritario.
    """
    robot.stop()
    wait(200)
    
    sum_h, sum_s, sum_v = 0, 0, 0
    
    # Para promediar Hue (que es circular), usamos truco de sin/cos
    import math
    sum_sin_h, sum_cos_h = 0, 0
    
    for i in range(lecturas):
        hsv = sensor.hsv()
        rad = hsv.h * math.pi / 180
        sum_sin_h += math.sin(rad)
        sum_cos_h += math.cos(rad)
        sum_s += hsv.s
        sum_v += hsv.v
        wait(espera_ms)
    
    # Promedio circular de Hue
    avg_h = math.atan2(sum_sin_h / lecturas, sum_cos_h / lecturas)
    avg_h = (avg_h * 180 / math.pi) % 360
    avg_s = sum_s / lecturas
    avg_v = sum_v / lecturas
    
    return int(avg_h), int(avg_s), int(avg_v)
```

---

## 6. Feedback no-bloqueante

En competencia, querés saber qué color detectó el robot sin frenarlo. Pybricks ofrece varias opciones:

### Luz del hub (instantánea, no-bloqueante)

```python
# Esto NO frena el programa
hub.light.on(Color.RED)    # Detectó rojo
hub.light.on(Color.BLUE)   # Detectó azul
hub.light.on(Color.GREEN)  # Detectó verde
```

### Display de la matriz (no-bloqueante)

```python
# Mostrar una letra en la pantalla 5x5
hub.display.char("R")  # Detectó Rojo
hub.display.char("A")  # Detectó Azul
hub.display.number(3)  # Detectó el 3er color
```

### Beep corto usando duración negativa (no-bloqueante)

```python
# Duración NEGATIVA = el beep arranca y el programa sigue inmediatamente
hub.speaker.beep(500, -1)  # Arranca beep a 500Hz, no espera
wait(100)                   # Dejar que suene 100ms mientras el robot hace otras cosas
hub.speaker.beep(0, 0)      # Silenciar (frecuencia 0)
```

### Combinación para feedback rápido por color

```python
def feedback_color(hub, color_nombre):
    """Feedback visual+sonoro no-bloqueante según color detectado."""
    FEEDBACK = {
        "ROJO":     (Color.RED,   "R", 440),   # La, 1 pip
        "AZUL":     (Color.BLUE,  "A", 660),   # Mi, tono alto
        "VERDE":    (Color.GREEN, "V", 550),   # Do#
        "AMARILLO": (Color.YELLOW,"Y", 880),   # La agudo
        "BLANCO":   (Color.WHITE, "B", 330),   # Mi grave
        "NEGRO":    (Color.NONE,  "N", 220),   # La grave
    }
    
    if color_nombre in FEEDBACK:
        luz, letra, freq = FEEDBACK[color_nombre]
        hub.light.on(luz)
        hub.display.char(letra)
        hub.speaker.beep(freq, -1)  # No-bloqueante
```

### Multitasking: beep en paralelo con movimiento

```python
from pybricks.tools import multitask, run_task, wait

async def pip_doble(hub):
    """Dos beeps cortos sin frenar el programa principal."""
    await hub.speaker.beep(600, 80)
    await wait(50)
    await hub.speaker.beep(600, 80)

async def mision(robot, sensor, hub):
    await robot.straight(200)
    # Leer color y dar feedback en paralelo con el siguiente movimiento
    color = sensor.color()
    await multitask(
        robot.straight(100),          # Sigue moviéndose
        pip_doble(hub),                # Suena al mismo tiempo
    )

run_task(mision(robot, sensor, hub))
```

---

## 7. Ubicación física del sensor

### Para detectar objetos (no líneas)

```
  Robot avanzando →
  
  ┌─────────────┐
  │   [Sensor]   │  ← Apuntando HACIA ADELANTE o HACIA ABAJO
  │    ○↓        │     según si detecta objetos laterales o piso
  │             │
  └─────────────┘
```

**Distancia óptima al objeto:** 8-16mm. El sensor SPIKE Prime tiene una "ventana dulce" donde los LEDs iluminan bien y el detector tiene buena señal.

### Factores que afectan la lectura

| Factor | Efecto | Solución |
|--------|--------|----------|
| Distancia > 20mm | S y V bajan, H se vuelve ruidoso | Acercar sensor o usar tubo guía |
| Distancia < 5mm | Sensor satura (V=100 siempre) | Alejar un poco |
| Ángulo no perpendicular | Reflexión despareja | Montar sensor perpendicular al objeto |
| Luz ambiente (ventanas, lámparas) | Cambia S y V | Usar tubo/capuchón oscuro, calibrar en el lugar |
| Superficie brillante vs mate | Reflexión especular confunde | Calibrar con el material real |
| Batería baja | LEDs del sensor más débiles | Cargar antes de competencia |

### El truco del "tubo oscuro"

Algunos equipos ganadores ponen un pequeño tubo de piezas LEGO Technic alrededor del sensor para bloquear la luz ambiente. Esto hace que el sensor solo vea la luz de sus propios LEDs reflejada, eliminando la interferencia del ambiente.

---

## 8. Programa de calibración interactivo

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import ColorSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

hub = PrimeHub()
sensor = ColorSensor(Port.D)

colores_medidos = []
nombres = ["ROJO", "AZUL", "VERDE", "AMARILLO", "BLANCO", "NEGRO"]

print("=== CALIBRACIÓN DE COLORES ===")
print("Poné cada objeto debajo del sensor")
print("a la distancia REAL de competencia")
print("")

for nombre in nombres:
    print("Color:", nombre)
    print("Presioná CENTRO cuando esté listo")
    
    while Button.CENTER not in hub.buttons.pressed():
        # Mostrar lectura en vivo
        hsv = sensor.hsv()
        hub.display.char(nombre[0])
        wait(100)
    
    wait(300)
    
    # Tomar 10 lecturas y promediar
    sum_h, sum_s, sum_v = 0, 0, 0
    for i in range(10):
        hsv = sensor.hsv()
        sum_h += hsv.h
        sum_s += hsv.s
        sum_v += hsv.v
        wait(50)
    
    h = sum_h // 10
    s = sum_s // 10
    v = sum_v // 10
    
    colores_medidos.append((nombre, h, s, v))
    print(nombre, ": H=", h, "S=", s, "V=", v)
    hub.speaker.beep(600, 100)
    wait(500)

print("")
print("=== RESULTADOS ===")
print("Copiá esto a tu programa:")
print("")
for nombre, h, s, v in colores_medidos:
    print("Color.MI_" + nombre, "= Color(h=" + str(h) + ", s=" + str(s) + ", v=" + str(v) + ")")
```

---

## 9. Problemas comunes y soluciones

| Problema | Causa | Solución |
|----------|-------|----------|
| Confunde rojo con naranja | Hue muy cercano (~350 vs ~15) | Subir peso de H, bajar umbral_max |
| Ve todo BLANCO | Sensor muy lejos, V siempre alto | Acercar a 8-16mm |
| Ve todo NEGRO | Sensor tapado o muy cerca | Verificar montaje, alejar a 8mm |
| Color cambia entre rondas | Luz del salón diferente | Recalibrar en el lugar, usar tubo oscuro |
| Lento para leer | Muchas lecturas de promedio | Reducir a 3-5 lecturas, 30ms entre cada una |
| Lee color del tapete, no del objeto | Sensor apunta al piso | Apuntar al objeto, no al piso |

## Regla de oro

> **Calibrá en el lugar de competencia, con los objetos reales, a la distancia real.** Un color calibrado en tu casa no sirve en el salón de competencia.
