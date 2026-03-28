# Guía Completa de Seguimiento de Línea para WRO RoboMission

## ¿Para quién es esta guía?

Esta guía es para equipos de WRO RoboMission (Elementary y Junior) que usan robots LEGO SPIKE Prime programados con **Pybricks Python** o **bloques**. Explica todo lo que necesitás saber para que tu robot siga líneas negras sobre fondo blanco con precisión y confianza.

## Índice

| # | Documento | ¿Qué vas a aprender? |
|---|-----------|----------------------|
| 01 | [Fundamentos](01-fundamentos.md) | Cómo funciona el sensor de color, calibración, qué es el "borde" de una línea |
| 02 | [Seguimiento con 1 sensor](02-un-sensor.md) | Control P y PID, seguir borde izquierdo o derecho |
| 03 | [Seguimiento con 2 sensores](03-dos-sensores.md) | Sensores a los costados de la línea, detección de intersecciones |
| 04 | [Seguimiento con 3 sensores](04-tres-sensores.md) | Sensor central + dos laterales, la configuración más poderosa |
| 05 | [Intersecciones y bifurcaciones](05-intersecciones.md) | Contar cruces, detenerse en la N-ésima, desviarse a izquierda o derecha |
| 06 | [Encontrar línea y alinearse](06-encontrar-y-alinear.md) | Buscar la línea desde cualquier posición, alinearse al final |
| 07 | [Estrategias de competición](07-estrategias-competicion.md) | Combinar todo para resolver misiones WRO |

## Configuración de referencia (SPIKE Prime + Pybricks)

```
         [SPIKE Prime Hub]
              |
    +---------+---------+
    |                   |
Motor Izq (A)    Motor Der (B)
    |                   |
  Rueda               Rueda
  
Sensores de color: Puerto(s) C, D, E según configuración
Diámetro rueda: 56 mm (ruedas grandes SPIKE)
Distancia entre ruedas (axle_track): depende del robot (medir!)
```

## Convenciones usadas en esta guía

- **Negro** = línea a seguir (reflexión baja, ~5-15%)
- **Blanco** = superficie del tapete (reflexión alta, ~85-95%)
- **Borde** = zona de transición entre negro y blanco (~45-55%)
- **Intersección** = punto donde la línea se cruza con otra línea
- **Bifurcación** = punto donde la línea se divide en dos direcciones
- **Izquierda/Derecha** = desde la perspectiva del robot mirando hacia adelante

## Consejo de oro

> **Siempre calibrá tu sensor antes de cada competencia.** La luz del ambiente cambia entre salas y momentos del día. Un robot bien calibrado es un robot confiable.
