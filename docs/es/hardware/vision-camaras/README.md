# Visión por Cámara para WRO RoboMission Junior — Guía Completa

## Regla WRO 2026 importante

> **"The usage of cameras is limited to the age groups Junior and Senior."**
> — WRO 2026 RoboMission General Rules, sección 5.2 Sensors

Las cámaras están **permitidas en Junior y Senior**, pero **prohibidas en Elementary**.

## 1. Comparativa de cámaras (4 opciones)

| Característica | HuskyLens | OpenMV H7+ | ESP32-CAM / LMS-ESP32 | Pixy2 |
|---------------|-----------|------------|----------------------|-------|
| **Precio** | ~$55 | ~$65-85 | ~$8-15 (CAM) / ~$40 (LMS-ESP32) | ~$60 |
| **Procesador** | Kendryte K210 | STM32H743 (Cortex-M7) | Xtensa LX6/LX7 dual-core | NXP LPC4330 |
| **Resolución** | 320×240 | 640×480 | 1600×1200 (OV2640) / 2MP (OV5640) | 316×208 |
| **FPS real (procesando)** | 11-30 | 30-85 | 10-25 (MicroPython) / 30+ (Arduino) | 60 |
| **WiFi** | ❌ No | ❌ No | ✅ Sí (802.11 b/g/n) | ❌ No |
| **BLE** | ❌ No | ❌ No | ✅ Sí (BLE 4.2/5.0) | ❌ No |
| **Comunicación con SPIKE** | UART/I2C (cable) | UART/SPI (cable) | **PUPRemote vía LPF2 (cable, emula sensor LEGO)** | UART/SPI |
| **Programación** | Menú on-screen | MicroPython (IDE propia) | MicroPython / Arduino / ESP-IDF | Arduino/Python |
| **ML/AI** | Sí (built-in) | Sí (TF Lite) | Sí (TF Lite Micro, ESP-NN) | No |
| **Display integrado** | Sí (2") | No ($20 extra) | No (pero stream WiFi a PC/celular) | No |
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ (con LMS-ESP32) | ⭐⭐⭐⭐ |
| **Flexibilidad** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (total) | ⭐⭐ |
| **Alimentación** | 5V (problema con SPIKE) | 3.3V-5V | 3.3V-5V (LMS-ESP32 provee 5V) | 5V |
| **Comunidad LEGO** | ⭐⭐⭐ Buena | ⭐⭐⭐⭐ Muy buena (WRO FE) | ⭐⭐⭐⭐⭐ Enorme (Arduino+LEGO) | ⭐⭐ |

---

## 2. ESP32-CAM: la opción más versátil y económica

### ¿Qué es?

El ESP32-CAM es un módulo que combina un microcontrolador ESP32 con una cámara OV2640 (2 megapíxeles), WiFi, BLE, y slot para SD card, todo por ~$8-15 USD. Es la opción más barata con diferencia.

### Variantes populares

| Módulo | Precio | Cámara | RAM PSRAM | Ventaja |
|--------|--------|--------|-----------|---------|
| AI-Thinker ESP32-CAM | ~$8 | OV2640 (2MP) | 4MB | La más barata, enorme comunidad |
| XIAO ESP32S3 Sense | ~$15 | OV2640 (2MP) | 8MB | Más compacto, USB-C, ESP32-S3 (mejor AI) |
| Freenove ESP32-S3-WROOM | ~$12 | OV2640 | 8MB | Buena documentación |
| ESP32-CAM con OV5640 | ~$15 | OV5640 (5MP) | 4-8MB | Mejor calidad de imagen |

### La ventaja clave: WiFi para debugging en tiempo real

Con las otras cámaras, para ver qué detecta la cámara hay que conectarla a la PC con cable USB. El robot no puede moverse mientras depurás.

Con ESP32-CAM:
- La cámara **transmite video por WiFi a tu celular o laptop** mientras el robot se mueve
- Podés ver exactamente qué ve, qué detecta, y por qué se confunde
- No hay cables extra: el robot funciona 100% autónomo
- Podés cambiar parámetros (umbrales de color, exposición) **desde el celular** sin tocar el robot

```
                    WiFi (debugging/streaming)
ESP32-CAM  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ▶  📱 Celular / 💻 Laptop
    │                                            (ver lo que ve la cámara)
    │ I2C / UART (datos: color, x, y)
    ▼
LMS-ESP32  ───── cable LPF2 ─────▶  SPIKE Prime Hub
(puente)                              (lógica de misión)
```

### Conexión con SPIKE Prime via LMS-ESP32

La placa **LMS-ESP32** de AntonsMindstorms es un ESP32 con conector LEGO LPF2 incorporado. Funciona como puente entre cualquier electrónica y el SPIKE:

1. La ESP32-CAM procesa la imagen y obtiene: qué color, dónde está, qué tamaño
2. Envía esos datos por I2C o UART a la LMS-ESP32
3. La LMS-ESP32 usa **PUPRemote** para emular un sensor LEGO
4. Desde Pybricks, se lee como si fuera un sensor más: `PUPDevice(Port.A)`

**¿Por qué es más confiable que HuskyLens directo?**
- La LMS-ESP32 provee 5V estables (no brownouts)
- PUPRemote emula un sensor LEGO nativo → Pybricks lo ve sin hacks
- La conexión es por cable LPF2 (el mismo que los motores LEGO) → ultra confiable
- Si la comunicación falla, se detecta inmediatamente (no se queda colgada)

### Alternativa: todo en una sola ESP32

Si usás la LMS-ESP32 directamente (sin ESP32-CAM separada), podés:
- Conectar una cámara OV2640 directo a los GPIO de la LMS-ESP32
- Todo el procesamiento + comunicación en una sola placa
- Más compacto, menos cables

Limitación: la LMS-ESP32 v2 tiene menos RAM (2MB) que una ESP32-CAM dedicada (4-8MB PSRAM), lo que limita la resolución procesable.

### Programación de la ESP32-CAM

**Con MicroPython (más fácil, compatible con el ecosistema IITA):**
```python
# En la ESP32-CAM (firmware MicroPython + camera module)
import camera
import network
from machine import UART

# Inicializar cámara
camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
camera.framesize(camera.FRAME_QVGA)  # 320x240

# WiFi para streaming/debugging
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("IITA_Robot", "password")

# UART para enviar datos al LMS-ESP32
uart = UART(1, baudrate=115200, tx=14, rx=15)

while True:
    img = camera.capture()
    # Procesar imagen (detección de color, blob, etc.)
    color_id, cx, cy = procesar_imagen(img)
    # Enviar al SPIKE via LMS-ESP32
    uart.write("%d,%d,%d\n" % (color_id, cx, cy))
```

**Con Arduino (más rápido, más librerías de visión):**
```cpp
#include "esp_camera.h"
#include "img_converters.h"
// Más librerías para procesamiento de imagen
// Comunicación con LMS-ESP32 por Serial
```

### Web server integrado para debugging

```python
# La ESP32-CAM puede servir una página web con video en vivo
# Accesible desde cualquier navegador: http://192.168.1.x
# Mientras el robot corre su misión autónomamente
```

---

## 3. Recomendación para IITA Junior

### Decisión según nivel del equipo

| Nivel | Recomendación | Por qué |
|-------|--------------|---------|
| **Recién empieza con visión** | HuskyLens + LMS-ESP32 | Menú visual, aprende con botón, sin programar cámara |
| **Sabe Python básico** | ESP32-CAM + LMS-ESP32 | Barato, WiFi para debug, totalmente personalizable |
| **Python avanzado** | OpenMV H7 + breakout board | Máximo rendimiento, IDE profesional, estándar WRO FE |
| **Máxima versatilidad/presupuesto bajo** | LMS-ESP32 + cámara OV2640 | Todo integrado, WiFi, BLE, la más económica |

### Plan progresivo recomendado para IITA

1. **Empezar:** HuskyLens + LMS-ESP32 (plug-and-play, detecta colores en minutos)
2. **Evolucionar:** ESP32-CAM (agrega WiFi debugging, scripts custom)
3. **Competir:** OpenMV H7 si necesitan TF Lite o máxima velocidad

---

## 4. Conexión física con SPIKE Prime

### El problema de alimentación (aplica a TODAS las cámaras)

SPIKE Prime entrega 3.3V en los pines de datos. Las cámaras necesitan 5V. La solución universal: **LMS-ESP32 breakout board** con conversor buck DC-DC.

```
SPIKE Hub                LMS-ESP32 Board              Cámara
┌────────┐   cable LPF2   ┌─────────────┐   cables    ┌──────────┐
│ Puerto A │──────────────▶│ Buck 5V     │────────────▶│ HuskyLens│
│          │               │ PUPRemote   │   I2C/UART  │ OpenMV   │
│          │               │ ESP32 onboard│            │ ESP32-CAM│
└────────┘               └─────────────┘              └──────────┘
```

La LMS-ESP32 funciona como puente universal para CUALQUIER cámara. El SPIKE solo ve un "sensor" en el puerto.

---

## 5. Comunicación y protocolo

### Con LMS-ESP32 + PUPRemote (recomendado para Pybricks)

**En la LMS-ESP32 (o ESP32 con la cámara):**
```python
from pupremote import PUPRemoteSensor

p = PUPRemoteSensor()
p.add_channel('color', to_hub_fmt='BBhh')  # id, confianza, x, y

while True:
    color_id, conf, cx, cy = leer_camara()
    p.update_channel('color', color_id, conf, cx, cy)
    p.process()
```

**En Pybricks (SPIKE):**
```python
from pupremote_hub import PUPRemoteHub

cam = PUPRemoteHub(Port.A)
cam.add_channel('color', 'BBhh')

while True:
    datos = cam.call('color')
    if datos:
        color_id, conf, cx, cy = datos
        print("Color:", color_id, "en x:", cx, "y:", cy)
```

### HuskyLens via LMS-ESP32

AntonsMindstorms tiene una integración específica donde la LMS-ESP32 se conecta a HuskyLens por I2C y reenvía los datos al SPIKE via PUPRemote. Funciona con Pybricks directamente.

---

## 6. Configuración y entrenamiento

### HuskyLens: menú on-screen (sin código)
1. Seleccionar "Color Recognition" en menú
2. Apuntar al objeto → mantener botón → color aprendido
3. Guardar en SD card

### OpenMV: IDE con Threshold Editor
1. Conectar por USB → OpenMV IDE
2. Tools → Machine Vision → Threshold Editor
3. Ajustar umbrales LAB visualmente
4. Copiar al script

### ESP32-CAM: calibrar por WiFi
1. Subir script de calibración a la ESP32
2. Conectarse al web server desde el celular
3. Ver la imagen en vivo y ajustar umbrales
4. Los umbrales se guardan en SD o flash

### Pixy2: PixyMon por USB
1. Conectar → PixyMon → click en color → ajustar signature

---

## 7. Ubicación, montaje e iluminación

### Montaje recomendado

Frente del robot, inclinada ~30° hacia abajo. Ve objetos a 10-30cm y parcialmente el piso.

### Iluminación — el enemigo #1

| Problema | Solución |
|----------|----------|
| Reflejos del tapete | Inclinar cámara para evitar reflexión especular |
| Sombras del robot | Montar cámara alta o agregar LEDs |
| Fluorescentes parpadean | Exposición fija, promediar frames |
| Luz variable entre rondas | Calibrar in-situ, guardar en SD |

**Truco OpenMV/ESP32:** Fijar exposición y balance de blancos:
```python
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_auto_exposure(False, exposure_us=15000)
```

---

## 8. Qué hacen los equipos ganadores

### WRO Future Engineers
- **OpenMV H7** es la cámara más popular (recomendada en docs oficiales WRO FE)
- SPIKE + OpenMV es combo oficial en la guía WRO FE Getting Started
- Umbrales en espacio LAB, exposición fija, scripts <50ms/frame

### RoboCup Junior
- Escudo físico contra luz, calibración in-situ obligatoria
- Múltiples perfiles de umbrales (uno por condición de luz)
- Redundancia: cámara + sensores como backup

### Tendencia 2025-2026
- Cada vez más equipos usan **ESP32 + cámara** por el costo y la versatilidad
- WiFi debugging se está volviendo estándar en equipos competitivos
- Modelos TF Lite pre-entrenados para clasificación de objetos WRO

---

## 9. Estrategias para misiones WRO con cámara

### Clasificar objetos a distancia (la ventaja clave)
Sin cámara: acercarse, parar, leer a 8-16mm. Con cámara: ver color a 15-30cm mientras se mueve.

### Seguimiento de línea anticipado
La cámara ve la línea ADELANTE del robot → puede anticipar curvas.

### Identificar formas o patrones
Imposible con sensor de color. Cámara obligatoria.

### April Tags / QR codes
HuskyLens tiene April Tags built-in. OpenMV/ESP32 pueden leer QR.

---

## 10. Problemas comunes

| Problema | Solución |
|----------|----------|
| HuskyLens brownout | LMS-ESP32 con buck 5V |
| Colores cambian entre rondas | Calibrar in-situ, exposición fija |
| Datos corruptos | Cables cortos, baudrate correcto |
| Pybricks no soporta UART | Usar PUPRemote via LMS-ESP32 |
| Reflejos del tapete | Inclinar cámara |
| Procesamiento lento | Bajar resolución, limitar ROI |

## Preguntas clave antes de agregar cámara

1. ¿El sensor de color LEGO alcanza? Si sí, no complicar.
2. ¿Hay objetos que distinguir a distancia? Cámara necesaria.
3. ¿Hay formas/patrones? Cámara obligatoria.
4. ¿Tienen 2-3 semanas para aprender? Mínimo necesario.
5. ¿Presupuesto? ESP32-CAM+LMS-ESP32 ~$50, HuskyLens+LMS-ESP32 ~$95, OpenMV ~$85-105.

## Recursos

- LMS-ESP32 board + PUPRemote: antonsmindstorms.com
- WRO FE Getting Started (SPIKE + OpenMV): world-robot-olympiad-association.github.io/future-engineers-gs/
- OpenMV IDE: openmv.io
- ESP32-CAM MicroPython: docs.micropython.org
- Pybricks PUPRemote: github.com/antonvh/PUPRemote
