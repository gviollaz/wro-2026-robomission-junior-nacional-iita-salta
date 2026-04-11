# Análisis equipo Lau Xiao 🇹🇼 — referencia WRO 2026 Junior

**Fuente**: canal YouTube 【Lego】Lau Xiao (~1.21K subs), video "WRO 2026 Junior - MBC Hue12 Sensor Test" (261 views, abr 2026). Hashtags: `#wro2026 #legospike #lauxiao #junior`. **Origen: Taiwán** (bandera ROC visible).

## Hardware identificado (análisis visual)

| Componente | Observación |
|---|---|
| **Hub** | LEGO SPIKE Prime (confirmado por `#legospike` y terminal "Pybricks Hub" en imagen 4) |
| **Firmware** | **Pybricks** (título ventana: "Pybricks Hub") |
| **Sensor estrella: MBC Hue12** | Módulo con pantalla LCD color integrada mostrando "RUN MODE" y vista tipo cámara con 3 recuadros azules. Detector multi-color de 12 tonos ("Hue12"). Montado en torre Technic alta al frente, vista cenital del campo |
| **Conexión MBC Hue12** | **Cable flat ribbon blanco custom** (NO LPF2 estándar). Bus propietario del ecosistema MBC |
| **Array de línea frontal** | PCB con LEDs verdes encendidos, montado abajo-frente. ~8 sensores IR estilo QTR/Hiwonder |
| **Motores** | 2 LEGO grandes traseros (diferencial) + probable 3ro para elevador frontal |
| **Chasis** | 100% LEGO Technic, sin piezas 3D visibles |

## Software

**Editor de bloques custom (imagen 4)**: bloques amarillos con nombres como `Black Line Value set to 20`, `Gyro Turn (180 100 0 1)`, `Gyro Move (0 50 50 0 0 510 0 1)`. Es un **DSL visual propietario** que compila a Pybricks — NO es Pybricks Blocks estándar ni Scratch. Patrón 7-8 parámetros por bloque típico de librerías `gyroStraight(dist, speed, accel, decel, kp, ki, kd, stopMode)`.

**Output terminal (imagen 4)**: `2 Gre 5 Yel 1 Red 3 Blk` repetido → el Hue12 cuenta objetos por color en tiempo real (torres verde/amarillo/rojo/negro visibles en campo imagen 3). Detección multi-objeto con clasificación, no solo color puntual.

## Ventaja competitiva del MBC Hue12

**Display LCD integrado** = calibración in-situ en la mesa de competencia sin PC. Crítico cuando cambia la iluminación del venue (problema típico que hace perder rondas). El sensor resuelve en un solo dispositivo lo que nosotros resolvemos con OpenMV H7 + LMS-ESP32 + PUPRemote.

**Desventaja**: ecosistema cerrado. Búsqueda web de "MBC Hue12" no arrojó resultados indexados — probablemente vendido solo en Shopee Taiwan / Taobao / canales locales del club Lau Xiao. Ata al equipo al stack propietario MBC (editor de bloques + sensor + librería de movimiento).

## Comparación vs arquitectura IITA recomendada

| Componente | Lau Xiao | IITA Junior |
|---|---|---|
| Hub | SPIKE Prime | SPIKE Prime ✅ |
| Firmware | Pybricks | Pybricks ✅ |
| Array línea | PCB custom ~8 IR | Hiwonder 8-ch I2C ✅ |
| Visión color | **MBC Hue12** (display integrado) | OpenMV H7 R2 |
| Bridge al hub | Bus flat propietario | LMS-ESP32 + PUPRemote |
| Editor | Bloques MBC → Pybricks | Python Pybricks directo |
| Chasis | LEGO Technic puro | LEGO Technic + 3D impreso |

**Veredicto**: misma filosofía arquitectónica (SPIKE+Pybricks+sensores externos). Diferencia clave = MBC Hue12 con display. Nuestro OpenMV da más flexibilidad (MicroPython programable, detección de blobs/líneas/formas genéricas) a cambio de no tener display embebido — se puede compensar mostrando la imagen en la laptop durante calibración.

## Lecciones aplicables para IITA Junior

1. **Montar la cámara en torre alta al frente**, vista cenital del campo → copiar el patrón de Lau Xiao para detectar torres de colores en el challenge Heritage Heroes
2. **Array de línea debajo-frente del robot**, no centrado → mejora anticipación en curvas
3. **Chasis LEGO Technic puro es competitivo** — no obsesionarse con piezas 3D custom esta temporada
4. **Librería de movimiento tipo "gyroStraight/gyroTurn" con PID** → implementar en Pybricks un wrapper similar con parámetros `(dist, speed, accel, decel, kp, ki, kd)`
5. **Calibración in-situ**: si no tenemos display embebido, armar un script Pybricks que muestre valores en la pantalla 5×5 del hub y permita ajustar thresholds con los botones

## Canal recomendado para seguir

**YouTube: 【Lego】Lau Xiao** — todo el contenido es WRO Junior con SPIKE+Pybricks, referencia pública más cercana a nuestra categoría. Suscribir a los chicos del equipo.

## Pendiente investigar (próxima sesión)

- MBC Hue12 en Shopee Taiwan / Taobao: precio, ¿envía a Argentina?
- ¿Existe repo GitHub público del ecosistema MBC o de Lau Xiao?
- ¿El editor de bloques amarillos es open source o comercial?
- Contactar a Lau Xiao vía comentarios YouTube preguntando por BOM público

---
_Análisis generado desde 5 screenshots del video, 2026-04-11. No se pudo ver el video directamente ni encontrar documentación pública del MBC Hue12._
