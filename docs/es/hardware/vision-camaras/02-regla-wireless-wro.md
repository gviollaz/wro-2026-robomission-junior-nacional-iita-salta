# ⚠️ Comunicación Inalámbrica en WRO RoboMission — PROHIBIDA

## La regla (WRO 2026 General Rules, sección 5.8)

> **"A robot must be autonomous and finish the missions by itself. Any radio communication, remote control and wired control systems are not allowed while the robot is running. No wireless communication is allowed between components within the robot."**

> **"Any wireless communication has to be [disabled] before the robot is placed in quarantine."**

Y el FAQ de WRO India (mismas reglas internacionales) refuerza:

> **"Teams must be able to demonstrate to the judges that Bluetooth, Wi-Fi and Internet on the Robot is switched off and how it is turned off in order to participate in that round."**

## ¿Qué significa para nosotros?

### ❌ PROHIBIDO durante la ronda oficial

- Bluetooth entre ESP32-CAM y LMS-ESP32 (o SPIKE)
- WiFi entre cualquier componente del robot
- BLE entre hub SPIKE y cualquier otro módulo
- Cualquier comunicación inalámbrica entre partes del robot

### ✅ PERMITIDO

- **Cable físico** entre todos los componentes (UART, I2C, SPI, LPF2)
- **WiFi/BLE durante práctica** (para debugging, calibración, streaming)
- Cable LPF2 de la LMS-ESP32 al SPIKE (es cable físico, no wireless)
- La cámara procesando imagen internamente (no es comunicación)

### ✅ ZONA GRIS (consultar al organizador nacional)

- WiFi de la ESP32-CAM usada SOLO como web server para que el equipo vea la cámara desde el celular durante práctica — pero desactivada para la ronda
- BLE del SPIKE Prime con Pybricks — se usa para cargar programas pero se puede desactivar durante la ronda

## ¿Por qué la idea del Bluetooth era tentadora?

La comunicación por cable entre ESP32-CAM y el SPIKE tiene estos problemas reales:

| Problema | Con cable | Con Bluetooth (PROHIBIDO) |
|----------|-----------|--------------------------|
| Brownouts | Comunes si no hay buck 5V | No aplica (cada uno su batería) |
| Cables se desconectan | Vibraciones los aflojan | No hay cables |
| Espacio en puertos | Ocupa un puerto del SPIKE | No ocupa puerto |
| Confiabilidad | Alta con LPF2, media con jumpers | Alta (BLE es robusto) |

La solución a estos problemas NO es Bluetooth (prohibido). Es usar **hardware correcto por cable**:

## La arquitectura correcta para WRO

```
ESP32-CAM                    LMS-ESP32                 SPIKE Prime
┌──────────┐    I2C/UART    ┌─────────────┐  cable    ┌──────────┐
│ Procesa   │──────cable────▶│ PUPRemote   │──LPF2───▶│ Pybricks │
│ imagen    │   (4 cables)  │ Buck 5V     │  (LEGO)  │ Misión   │
│ OV2640    │               │ ESP32 PICO  │          │          │
└──────────┘               └─────────────┘          └──────────┘
     │
     │ WiFi (SOLO durante práctica, desactivar para ronda)
     ▼
📱 Celular (debugging visual)
```

### Cómo desactivar WiFi/BLE antes de la ronda

**En la ESP32-CAM (MicroPython):**
```python
import network

# Al inicio del programa de competencia:
wifi = network.WLAN(network.STA_IF)
wifi.active(False)  # Desactivar WiFi

# También desactivar BLE si estaba activo
import bluetooth
bt = bluetooth.BLE()
bt.active(False)

# Ahora el robot es 100% autónomo, sin wireless
```

**En la ESP32-CAM (Arduino):**
```cpp
#include <WiFi.h>
#include <BLEDevice.h>

void setup() {
    WiFi.mode(WIFI_OFF);  // Desactivar WiFi
    btStop();              // Desactivar Bluetooth
    // Ahora solo comunicación por cable
}
```

### Tip para competencia

1. Tener **dos versiones del firmware** de la ESP32-CAM:
   - `cam_debug.py` — Con WiFi activado, streaming, web server (para práctica)
   - `cam_competition.py` — Sin WiFi/BLE, solo procesamiento + UART (para ronda)
2. Cambiar el firmware es tan simple como renombrar el archivo `main.py` en la SD
3. **Demostrar al juez** que el WiFi está apagado: mostrar el código, o que el celular no encuentra la red

## Alternativa: todo en una sola placa LMS-ESP32

Si la ESP32-CAM y la LMS-ESP32 son un problema de espacio/cables, se puede usar **solo la LMS-ESP32** con una cámara OV2640 conectada a sus GPIO. Así hay una sola placa, un solo cable al SPIKE, y cero comunicación inalámbrica.

```
LMS-ESP32 (con cámara OV2640 soldada)     SPIKE Prime
┌───────────────────────────┐    cable    ┌──────────┐
│ ESP32 PICO + OV2640       │────LPF2────▶│ Pybricks │
│ Procesa imagen + PUPRemote │   (LEGO)   │ Misión   │
│ WiFi OFF en competencia   │            │          │
└───────────────────────────┘            └──────────┘
```

Ventajas: mínimo cableado, una sola placa, imposible que se desconecte.
Desventajas: menos RAM (2MB vs 4-8MB), resolución más limitada.

## Resumen

| Comunicación | Práctica | Ronda oficial |
|-------------|----------|---------------|
| WiFi ESP32→Celular (debugging) | ✅ Sí | ❌ Desactivar |
| BLE ESP32→SPIKE | ✅ Sí | ❌ Prohibido |
| Bluetooth ESP32→ESP32 | ✅ Sí | ❌ Prohibido |
| Cable I2C/UART ESP32→ESP32 | ✅ Sí | ✅ Sí |
| Cable LPF2 LMS-ESP32→SPIKE | ✅ Sí | ✅ Sí |
| WiFi para cargar programa | ✅ Solo en pit area | ❌ No en mesa de competencia |
