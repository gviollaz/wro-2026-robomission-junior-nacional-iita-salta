# SKILL: Detección de Colores en Pybricks Python para WRO

## Descripción
Skill para generar código Pybricks Python de detección de colores precisa para SPIKE Prime en WRO RoboMission. Cubre calibración HSV, `detectable_colors()`, clasificador por distancia euclidiana, protocolo de lectura, y feedback no-bloqueante.

## API de referencia

```python
sensor = ColorSensor(Port.D)
sensor.color()                    # Color más cercano de detectable_colors
sensor.hsv()                      # Color(h=0-359, s=0-100, v=0-100)
sensor.reflection()               # 0-100 (brillo)
sensor.detectable_colors(lista)   # Definir colores personalizados

hub.light.on(Color.RED)           # Luz no-bloqueante
hub.display.char("R")             # Display no-bloqueante
hub.display.number(3)             # Display no-bloqueante
hub.speaker.beep(freq, -duration) # Beep no-bloqueante (duración negativa)
```

## Reglas obligatorias al generar código de color

### 1. SIEMPRE usar HSV, nunca RGB crudo
```python
hsv = sensor.hsv()  # Correcto
# No hay método RGB público en Pybricks — HSV es lo que hay
```

### 2. SIEMPRE definir colores personalizados calibrados
```python
Color.MI_ROJO = Color(h=355, s=82, v=45)  # CALIBRAR
sensor.detectable_colors((Color.MI_ROJO, Color.MI_AZUL, ...))
```

### 3. SIEMPRE parar el robot antes de leer color de objetos
```python
robot.stop()
wait(200)  # Estabilizar
color = sensor.color()
```

### 4. SIEMPRE promediar múltiples lecturas
```python
def leer_color(sensor, n=5):
    votos = {}
    for i in range(n):
        c = str(sensor.color())
        votos[c] = votos.get(c, 0) + 1
        wait(50)
    return max(votos, key=votos.get)
```

### 5. Feedback no-bloqueante después de detectar
```python
hub.light.on(Color.RED)       # Instantáneo
hub.display.char("R")         # Instantáneo
hub.speaker.beep(500, -1)     # No espera
# El robot puede seguir moviéndose
```

### 6. Solo incluir colores necesarios para la misión
Menos colores en `detectable_colors` = menos confusión.

## Clasificador avanzado (distancia euclidiana HSV ponderada)

```python
import math

COLORES = [
    # (nombre, h, s, v, peso_h, peso_s, peso_v, umbral_max)
    ("ROJO",     355, 82, 45, 2.0, 1.0, 0.5, 60),
    ("AZUL",     218, 85, 50, 2.0, 1.0, 0.5, 60),
    ("VERDE",    140, 70, 35, 2.0, 1.0, 0.5, 60),
    ("AMARILLO",  55, 65, 90, 2.0, 0.8, 0.3, 50),
    ("BLANCO",     0,  5, 95, 0.1, 2.0, 1.5, 40),
    ("NEGRO",      0,  5,  8, 0.1, 0.5, 2.0, 30),
]

def dist_hue(h1, h2):
    d = abs(h1 - h2)
    return min(d, 360 - d)

def clasificar(sensor):
    hsv = sensor.hsv()
    h, s, v = hsv.h, hsv.s, hsv.v
    mejor, mejor_d = "DESCONOCIDO", 9999
    for nom, ch, cs, cv, wh, ws, wv, um in COLORES:
        d = math.sqrt((dist_hue(h,ch)*wh)**2 + ((s-cs)*ws)**2 + ((v-cv)*wv)**2)
        if d < mejor_d and d < um:
            mejor_d = d
            mejor = nom
    return mejor
```

**Pesos:**
- Colores cromáticos (rojo, azul, verde): peso alto en H, bajo en V
- Blanco: peso alto en S (baja) y V (alta), bajo en H (ruidoso)
- Negro: peso alto en V (bajo), bajo en H

## Promedio HSV con media circular para Hue

```python
import math

def leer_hsv_avg(sensor, n=5):
    sin_h, cos_h, ss, sv = 0, 0, 0, 0
    for _ in range(n):
        hsv = sensor.hsv()
        r = hsv.h * math.pi / 180
        sin_h += math.sin(r)
        cos_h += math.cos(r)
        ss += hsv.s
        sv += hsv.v
        wait(50)
    h = (math.atan2(sin_h/n, cos_h/n) * 180 / math.pi) % 360
    return int(h), int(ss/n), int(sv/n)
```

## Multitasking para feedback durante movimiento

```python
from pybricks.tools import multitask, run_task

async def beep_doble(hub):
    await hub.speaker.beep(600, 80)
    await wait(50)
    await hub.speaker.beep(600, 80)

async def mision(robot, sensor, hub):
    await robot.straight(200)
    robot.stop()
    wait(200)
    color = clasificar(sensor)
    # Feedback + siguiente movimiento en paralelo
    await multitask(
        robot.straight(100),
        beep_doble(hub),
    )

run_task(mision(robot, sensor, hub))
```

## Distancia óptima del sensor

- Objetos: 8-16mm (ventana dulce del sensor SPIKE)
- < 5mm: satura (V=100 siempre)
- > 20mm: señal débil, H ruidoso
- Usar tubo LEGO Technic para bloquear luz ambiente

## Errores a evitar

- NO leer color mientras el robot se mueve
- NO confiar en `color()` por defecto sin calibrar
- NO incluir colores innecesarios en detectable_colors
- NO ignorar que H es circular (360° ≈ 0°)
- NO asumir mismos valores HSV entre sesiones (recalibrar)
