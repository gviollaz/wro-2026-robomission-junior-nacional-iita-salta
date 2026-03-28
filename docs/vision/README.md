# Visión por Cámara para WRO RoboMission Junior — Guía Completa

## Regla WRO 2026 importante

> **"The usage of cameras is limited to the age groups Junior and Senior."**
> — WRO 2026 RoboMission General Rules, sección 5.2 Sensors

Las cámaras están **permitidas en Junior y Senior**, pero **prohibidas en Elementary**. Este documento es exclusivo para el equipo Junior de IITA.

## Índice

| Sección | Contenido |
|---------|-----------|
| 1 | Comparativa: HuskyLens vs OpenMV vs Pixy2 |
| 2 | Recomendación para IITA Junior |
| 3 | Conexión física con SPIKE Prime |
| 4 | Comunicación UART y protocolo |
| 5 | Configuración y entrenamiento de la cámara |
| 6 | Programación en Pybricks |
| 7 | Ubicación, montaje e iluminación |
| 8 | Qué hacen los equipos ganadores |
| 9 | Estrategias para misiones WRO |
| 10 | Problemas comunes y soluciones |

---

## 1. Comparativa de cámaras

### Las tres opciones principales

| Característica | HuskyLens | OpenMV H7+ | Pixy2 |
|---------------|-----------|------------|-------|
| **Fabricante** | DFRobot | OpenMV LLC | Charmed Labs |
| **Precio** | ~$55 USD | ~$65 USD ($85 con display) | ~$60 USD |
| **Procesador** | Kendryte K210 (RISC-V + NPU) | STM32H743 (ARM Cortex-M7) | NXP LPC4330 (ARM Cortex-M4) |
| **Resolución** | 320x240 | 640x480 (configurable) | 316x208 |
| **FPS** | 11-30 (según algoritmo) | 30-85 (según algoritmo) | 60 |
| **Comunicación** | UART / I2C | UART / SPI / I2C | UART / SPI / I2C |
| **Programación** | Menú on-screen (low-code) | MicroPython (IDE propia) | Arduino/Python libs |
| **ML/AI** | Sí (clasificación objetos built-in) | Sí (TensorFlow Lite) | No (solo color/forma) |
| **Display integrado** | Sí (2", color, live feed) | No (shield opcional ~$20) | No |
| **Funciones built-in** | 7 (color, línea, cara, objeto, tag, clasificación, tracking) | Ilimitadas (programable) | 3 (color, línea, código) |
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ Muy fácil | ⭐⭐ Requiere programar | ⭐⭐⭐⭐ Fácil |
| **Flexibilidad** | ⭐⭐ Limitada a funciones built-in | ⭐⭐⭐⭐⭐ Total (Python) | ⭐⭐ Limitada |
| **Con SPIKE Prime** | Funciona (necesita 5V externo) | Funciona (con breakout board) | Funciona (UART directo) |
| **Almacenamiento** | SD card (modelos aprendidos) | SD card (scripts + modelos) | Flash interna |

### Funciones detalladas

**HuskyLens** — 7 funciones built-in:
1. Reconocimiento de color (blob tracking)
2. Seguimiento de línea
3. Reconocimiento facial
4. Tracking de objetos (por forma)
5. Reconocimiento de objetos (clasificación)
6. Reconocimiento de tags (April Tags)
7. Clasificación de objetos (ML)

**OpenMV** — Funciones ilimitadas (programable en MicroPython):
- Todo lo que HuskyLens hace, más:
- Redes neuronales custom (TensorFlow Lite)
- Visión estéreo (con 2 cámaras)
- Lectura de códigos QR y de barras
- Detección de bordes, esquinas, template matching
- Acceso pixel por pixel
- Histogramas de color
- Filtros y transformaciones de imagen

**Pixy2** — 3 funciones:
1. Detección de color (signatures, hasta 7 colores)
2. Seguimiento de línea (con intersecciones y códigos)
3. Lectura de códigos de barras simples

---

## 2. Recomendación para IITA Junior

### Opción A: HuskyLens (recomendada para empezar)

**Ventajas:**
- No requiere programar la cámara (menú on-screen)
- Display integrado muestra qué ve en tiempo real
- Aprende colores/objetos con un botón (sin código)
- Protocolo UART bien documentado
- Más barata

**Desventajas:**
- Necesita alimentación 5V externa (SPIKE da 3.3V, insuficiente → brownouts)
- Interfaz de menú poco intuitiva
- No se puede personalizar los algoritmos
- Rendimiento inferior a OpenMV en condiciones de luz difíciles

**Ideal para:** Equipos que recién empiezan con visión, misiones simples de clasificación por color.

### Opción B: OpenMV H7 (recomendada para equipos con experiencia Python)

**Ventajas:**
- Totalmente programable en MicroPython
- IDE propia con live feed en la PC (ves lo que ve la cámara)
- Redes neuronales custom (TensorFlow Lite)
- Mejor rendimiento en condiciones de luz variable
- Acceso a cada pixel, histogramas, filtros
- Comunidad WRO Future Engineers la usa extensamente

**Desventajas:**
- Requiere programar la cámara por separado (IDE propia)
- Más cara (especialmente con display)
- Curva de aprendizaje más alta

**Ideal para:** Equipos que quieren máximo rendimiento y ya manejan Python.

### Opción C: Pixy2 (opción legacy, no recomendada para 2026)

**Ventajas:**
- Hardware robusto, 60 FPS
- Buena detección de color por signatures
- Protocolo SPI muy rápido

**Desventajas:**
- Sin ML/AI, sin clasificación
- Software PixyMon requiere PC para configurar
- No tan activo en desarrollo como las otras dos
- No agrega funcionalidad que el sensor de color SPIKE no tenga (para color simple)

**Recomendación IITA:** Empezar con HuskyLens. Si el equipo avanza y necesita más, migrar a OpenMV.

---

## 3. Conexión física con SPIKE Prime

### El problema de la alimentación

El SPIKE Prime entrega 3.3V en los pines de datos del puerto. Las cámaras necesitan 5V (HuskyLens) o al menos 3.3V estable (OpenMV). La solución es usar un **breakout board con conversor buck DC-DC**.

### Opción recomendada: SPIKE-OpenMV Breakout Board

Esta placa (de AntonsMindstorms/WROBd) se conecta a un puerto del SPIKE y provee:
- 5V estables desde la batería del hub (vaía M+ a 100% PWM)
- Pines UART (TX/RX) para comunicación
- Compatible con HuskyLens Y OpenMV

```
SPIKE Hub                Breakout Board              Cámara
┌────────┐   cable LPF2   ┌─────────────┐   4 cables  ┌─────────┐
│ Puerto F │───────────▶│ Buck 5V    │─────────▶│ HuskyLens│
│          │             │ UART TX/RX │            │ u OpenMV │
└────────┘             └─────────────┘            └─────────┘
```

### Conexión HuskyLens (4 cables)

| Cable HuskyLens | Breakout Board | Función |
|----------------|----------------|----------|
| Rojo (5V) | 5V | Alimentación |
| Negro (GND) | GND | Tierra |
| Verde (TX) | RX | Datos cámara → hub |
| Azul (RX) | TX | Datos hub → cámara |

### Conexión OpenMV H7 (header directo)

La breakout board tiene header compatible con el pinout de OpenMV. Se enchufa directamente.

### Sin breakout board (DIY con soldering)

Se puede soldar un cable LPF2 cortado a un conversor buck 3.3V→5V. Requiere habilidad de soldadura.

---

## 4. Comunicación UART y protocolo

### HuskyLens: protocolo binario

HuskyLens usa un protocolo binario propietario sobre UART a 9600 baud (default). La biblioteca de AntonsMindstorms para SPIKE abstrae esto:

```python
# En LEGO MINDSTORMS Robot Inventor firmware
from projects.mpy_robot_tools import pyhuskylens

lens = pyhuskylens.HuskyLens(Port.F)
lens.knock()  # Verificar conexión

# Cambiar algoritmo
lens.algorithm(pyhuskylens.COLOR_RECOGNITION)

# Leer objetos detectados
bloques = lens.get_blocks()
for b in bloques:
    print("ID:", b.ID, "X:", b.x, "Y:", b.y, "W:", b.width, "H:", b.height)
```

### OpenMV: protocolo custom

OpenMV se programa con su propio IDE (OpenMV IDE). El script corre EN la cámara y envía datos por UART al SPIKE.

**En la cámara (OpenMV IDE):**
```python
import sensor, image, time
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)  # 320x240
sensor.skip_frames(time=2000)

uart = UART(3, 115200)

# Definir umbrales de color en LAB
rojo_lab = (30, 100, 15, 127, 15, 127)
azul_lab = (10, 50, -20, 20, -80, -20)

while True:
    img = sensor.snapshot()
    blobs = img.find_blobs([rojo_lab, azul_lab], 
                           pixels_threshold=100,
                           area_threshold=100)
    if blobs:
        b = max(blobs, key=lambda x: x.pixels())
        # Enviar: color_id, cx, cy, area
        uart.write("%d,%d,%d,%d\n" % (b.code(), b.cx(), b.cy(), b.pixels()))
    else:
        uart.write("0,0,0,0\n")
    time.sleep_ms(50)
```

**En el SPIKE (Pybricks/MINDSTORMS):**
```python
# Leer datos de la cámara via UART
data = uart.readline()
if data:
    parts = data.decode().strip().split(",")
    color_id = int(parts[0])
    cx = int(parts[1])
    cy = int(parts[2])
    area = int(parts[3])
```

### Nota sobre Pybricks

A marzo 2026, Pybricks **no tiene soporte nativo de puerto serial UART** en sus APIs públicas. Las bibliotecas de cámara funcionan con:
- LEGO MINDSTORMS Robot Inventor firmware (MicroPython)
- SPIKE App v3 (Python)
- PUPRemote (biblioteca de AntonsMindstorms para Pybricks vía hack de puerto)

Si el equipo usa Pybricks, necesitará la biblioteca **PUPRemote** o cambiar a MINDSTORMS firmware para la cámara.

---

## 5. Configuración y entrenamiento

### HuskyLens: aprender colores

1. Encender HuskyLens (botón o alimentación)
2. Seleccionar "Color Recognition" en el menú (rueda/botón)
3. Apuntar al objeto de color deseado
4. Mantener presionado el botón de aprendizaje hasta que aparezca el recuadro
5. Soltar → color aprendido como ID 1
6. Para otro color: presionar brevemente (no mantener) → cambia a "Learn Again"
7. Repetir → ID 2, ID 3, etc.
8. Guardar en SD card para no perder entre reinicios

### OpenMV: calibrar umbrales de color

1. Abrir OpenMV IDE en la PC
2. Conectar cámara por USB
3. Ejecutar script de vista previa
4. Usar Tools → Machine Vision → Threshold Editor
5. Ajustar umbrales LAB hasta que solo el color deseado esté blanco
6. Copiar umbrales al script

### Pixy2: signatures

1. Conectar Pixy2 por USB a PC
2. Abrir PixyMon
3. Apuntar al objeto, hacer clic en el color deseado
4. Ajustar signature hasta que solo detecte el color deseado
5. Guardar en flash

---

## 6. Programación en Pybricks / SPIKE Python

### Arquitectura recomendada

```
┌────────────────┐      UART       ┌────────────────┐
│   Cámara        │ ─────────▶ │   SPIKE Prime   │
│ (procesa imagen)│   datos      │ (lógica misión) │
│                │  color,x,y   │                │
└────────────────┘              └────────────────┘
```

La cámara hace TODO el procesamiento de imagen. El SPIKE solo recibe datos simples (qué color, dónde está) y toma decisiones de movimiento.

---

## 7. Ubicación, montaje e iluminación

### Dónde montar la cámara

```
Vista lateral del robot:

  Cámara mirando hacia adelante-abajo (~30-45°)
        ○───
       /     \
      /  FOV  \
     /  ~60°   \
══════════════════  Piso / objetos
```

| Posición | Ventajas | Desventajas |
|----------|----------|-------------|
| **Frente, mirando adelante** | Ve objetos a distancia | No ve el piso debajo |
| **Frente, inclinada 30-45°** | Ve objetos Y piso cercano | Campo de visión mezclado |
| **Arriba, mirando abajo** | Vista cenital del área | No ve objetos altos |
| **Costado, mirando lateral** | Detecta objetos al pasar | Campo limitado |

**Recomendación:** Frente del robot, inclinada ~30° hacia abajo. Esto permite ver objetos a 10-30cm de distancia y parcialmente el piso.

### Altura de montaje

| Altura desde piso | Qué ve a 20cm de distancia |
|-------------------|----------------------------|
| 5cm | Solo piso y objetos muy bajos |
| 8-10cm | Objetos de 2-3cm de alto, piso cercano |
| 12-15cm | Objetos estándar WRO (cubos LEGO) |
| 18-20cm | Vista amplia pero lejos de objetos pequeños |

### Iluminación

**El enemigo #1 de la visión por cámara es la luz variable.**

| Problema | Solución |
|----------|----------|
| Reflejos del tapete blanco | Inclinar cámara para evitar reflexión directa |
| Sombras del propio robot | Montar cámara alta o con LEDs propios |
| Luz de ventanas lateral | Pedir mesa alejada de ventanas |
| Fluorescentes parpadean | Usar exposición fija (OpenMV) o promediar frames |
| Diferentes salas en competencia | Calibrar en el lugar, guardar en SD |

**Truco avanzado (OpenMV):** Fijar exposición y balance de blancos para que la cámara no se auto-ajuste:
```python
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_auto_exposure(False, exposure_us=15000)
```

---

## 8. Qué hacen los equipos ganadores

### WRO Future Engineers (referencia)

La categoría Future Engineers REQUIERE cámara. Los equipos top usan:
- **OpenMV H7** es la cámara más popular (recomendada en la documentación oficial WRO FE)
- SPIKE Prime + OpenMV es un combo recomendado en la guía oficial WRO FE Getting Started
- Umbrales de color en espacio LAB (más robusto que RGB)
- Exposición y balance de blancos fijos
- Scripts optimizados para <50ms por frame

### RoboCup Junior Soccer

Los equipos de RoboCup Junior Soccer Open usan cámaras para:
- Detectar la pelota naranja infrarroja
- Detectar arcos amarillo/azul
- Lectura rápida (<20ms por ciclo)
- Comunicación I2C o UART a alta velocidad con el controlador principal

Buenas prácticas de RoboCup:
- Escudo físico contra luz ambiental alrededor de la cámara
- Calibración in-situ obligatoria
- Múltiples umbrales guardados (uno por condición de luz)
- Redundancia: cámara + sensores IR/color como backup

### FIRST Robotics / FLL

En FLL, las cámaras no están permitidas (solo sensores LEGO). Pero en FIRST Tech Challenge y FIRST Robotics:
- Visión OpenCV con Raspberry Pi
- Modelos pre-entrenados para detección de objetos específicos
- Pipeline: captura → resize → filtro color → blob detection → decisión

---

## 9. Estrategias para misiones WRO Junior con cámara

### Caso 1: Clasificar objetos por color a distancia

**Sin cámara:** el robot tiene que acercarse a cada objeto, detenerse, y leer con el sensor de color a 8-16mm.

**Con cámara:** el robot ve el color del objeto a 15-30cm de distancia, MIENTRAS se mueve. Puede planificar la ruta antes de llegar.

```python
# Pseudocódigo: clasificar objeto a distancia
cam_data = leer_camara()  # color_id, cx, cy, area

if cam_data.color_id == 1:  # Rojo
    # Ir directo a recoger, ya sé que es rojo
    ir_a_objeto(cam_data.cx)
elif cam_data.color_id == 2:  # Azul
    # Ignorar o llevar a otra zona
    esquivar_objeto()
```

### Caso 2: Seguimiento de línea con cámara

**Ventaja:** la cámara ve la línea ADELANTE del robot, no debajo. Puede anticipar curvas.

**Funciona bien con:** HuskyLens (line tracking built-in) o OpenMV (`find_lines()`).

### Caso 3: Identificar patrones o formas

Si la misión requiere distinguir formas (círculo vs cuadrado) o patrones, una cámara es la única opción. El sensor de color no puede hacer esto.

### Caso 4: April Tags / QR codes

Si la misión usa marcadores impresos, HuskyLens tiene reconocimiento de April Tags built-in. OpenMV puede leer QR codes y April Tags.

---

## 10. Problemas comunes y soluciones

| Problema | Causa | Solución |
|----------|-------|----------|
| HuskyLens se apaga solo (brownout) | Insuficiente corriente desde SPIKE (3.3V) | Usar breakout board con buck 5V |
| Cámara detecta colores distintos entre rondas | Luz ambiente cambió | Calibrar en el lugar, exposición fija |
| Datos llegan lentos o corruptos | Baudrate incorrecto o ruido en cables | Verificar baudrate, cables cortos, blindados |
| Pybricks no soporta UART nativo | Limitación de Pybricks API | Usar PUPRemote o MINDSTORMS firmware |
| Cámara ve reflejos del tapete | Ángulo de cámara incorrecto | Inclinar para evitar reflexión especular |
| Objeto fuera del campo de visión | Cámara mal orientada | Ajustar ángulo, usar lente gran angular |
| Falsos positivos (detecta color donde no hay) | Umbrales muy amplios | Ajustar umbrales más estrictos |
| Demora en procesamiento (>100ms) | Resolución muy alta o muchos blobs | Bajar resolución, limitar ROI |

## Antes de decidir si usar cámara

Preguntas clave para el equipo:

1. **¿La misión 2026 requiere distinguir colores que el sensor LEGO no puede?** Si el sensor de color alcanza, no complicar con cámara.
2. **¿Hay objetos que distinguir a distancia?** Si sí, la cámara es la única opción.
3. **¿Hay formas o patrones que identificar?** Cámara obligatoria.
4. **¿El equipo tiene tiempo para aprender a usar la cámara?** Al menos 2-3 semanas de práctica.
5. **¿Tienen el hardware (breakout board, cables)?** Presupuesto ~$80-120 USD total.

## Plan de acción para IITA Junior

1. **Semana 1-2:** Conseguir HuskyLens + breakout board. Probar conexión básica.
2. **Semana 3-4:** Aprender colores de los objetos WRO 2026. Probar detección.
3. **Semana 5-6:** Integrar con el programa de misión. Probar en el tapete real.
4. **Si necesitan más:** Migrar a OpenMV con scripts custom.

## Recursos

- WRO FE Getting Started (SPIKE + OpenMV): https://world-robot-olympiad-association.github.io/future-engineers-gs/
- AntonsMindstorms HuskyLens + SPIKE: antonsmindstorms.com
- OpenMV IDE: openmv.io
- Pixy2 docs: pixycam.com/pixy2
- WRO 2026 General Rules: wro-association.org
