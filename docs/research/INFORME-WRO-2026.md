# Informe WRO 2026 — Hardware upgrade IITA Salta

Ver el informe completo en el artifact generado en la sesión de Claude del 2026-04-11.

## Resumen ejecutivo

**Reglamento WRO 2026**: hardware libre desde 2025. Junior permite cámaras y 5 motores; Elementary NO permite cámaras, máx 4 motores. Comunicación inalámbrica entre componentes PROHIBIDA (LMS-ESP32 debe ir por cable LPF2).

**Arquitectura recomendada Junior**: SPIKE Prime + Pybricks + LMS-ESP32 v2.0 (puente LPF2) + Hiwonder 8-ch IR I2C (array de línea) + OpenMV H7 R2 (visión).

## BOM Junior P0+P1 (~$164 USD)

| Componente | USD | Fuente |
|---|---|---|
| LMS-ESP32 v2.0 | 32 + 15 envío | antonsmindstorms.com |
| SPIKE Breakout Board | 27 | antonsmindstorms.com |
| OpenMV Cam H7 R2 | 60 | AliExpress SingTown |
| Hiwonder 8-ch IR I2C | 13 | AliExpress |
| Cables LPF2 + jumpers | 10 | AliExpress |

## Protocolo técnico

LMS-ESP32 emula sensor LEGO tipo 62 via librería PUPRemote. Init 2400 baud → 115200. Max 16 bytes por intercambio (suficiente para 8×int16 del array de línea). Código Pybricks:

```python
from pupremote_hub import PUPRemoteHub
from pybricks.parameters import Port
hub = PUPRemoteHub(Port.A)
hub.add_channel('line', to_hub_fmt="8h")
while True:
    hub.process()
    line = hub.read_channel('line')
```

## Recursos clave

- PUPRemote: github.com/antonvh/PUPRemote
- LPF2 spec: github.com/pybricks/technical-info
- Kai Morich WRO info: github.com/kai-morich/lms-esp32-pybricks-info
- OFDL Taiwan: github.com/ofdl-robotics-tw
- Reglamento: wro-association.org/wp-content/uploads/WRO-2026-RoboMission-General-Rules.pdf

## Acción inmediata

1. Pedir LMS-ESP32 + Breakout Board a antonsmindstorms.com (~€100)
2. Pedir OpenMV + Hiwonder + Geekservo en AliExpress (~$110)
3. Verificar reglas nacionales Argentina 2026 con FUNDESTEAM
4. Mientras llegan: flashear Pybricks, practicar Heritage Heroes, estudiar PUPRemote
