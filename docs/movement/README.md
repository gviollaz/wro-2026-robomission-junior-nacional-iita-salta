# Guía de Mejores Prácticas de Movimiento para WRO RoboMission

## ¿Para quién es esta guía?

Para equipos WRO RoboMission (Elementary, Junior, Senior) que usan SPIKE Prime con Pybricks. Cubre las técnicas que usan los equipos ganadores para mover el robot con máxima precisión y repetibilidad.

## Índice

| # | Documento | ¿Qué vas a aprender? |
|---|-----------|----------------------|
| 01 | [Arranque y freno suave](01-arranque-freno-suave.md) | Aceleración progresiva, frenado preciso, perfiles de velocidad |
| 02 | [Odometría precisa](02-odometria-precisa.md) | Calibrar ruedas, compensar errores, medir distancias con precisión |
| 03 | [Giroscopio: guía completa](03-giroscopio.md) | Inicialización, calibración, heading_correction, limitaciones |
| 04 | [Calibración de PID](04-calibracion-pid.md) | Método Ziegler-Nichols simplificado, calibrar PID de color y giro |

## ¿Por qué importa la precisión del movimiento?

La diferencia entre un equipo que gana y uno que pierde es la **repetibilidad**. Si tu robot hace la misma misión 10 veces y las 10 la completa, vas a ganar.

Los equipos ganadores de WRO Internacional comparten estas características:
- **Movimientos predecibles**: el robot hace lo mismo cada vez
- **Calibración rigurosa**: calibran ruedas, sensores y giroscopio antes de cada ronda
- **Perfiles de velocidad**: no arrancan ni frenan de golpe
- **Uso inteligente del giroscopio**: para ir derecho y girar con precisión
- **Código modular**: funciones reutilizables para cada tipo de movimiento

## Orden de calibración

1. `wheel_diameter` → avanzar 1000mm, medir real, ajustar
2. `axle_track` → girar 3600° (10 vueltas), ajustar
3. `heading_correction` → girar 360° a mano, leer valor
4. Activar `use_gyro(True)` DESPUÉS de calibrar
5. Calibrar PID de seguimiento de línea con robot calibrado
6. Calibrar sensores de color en el tapete de competencia

## Regla de oro

> **Medí, no adivinés.** El diámetro de la rueda no es 56mm porque lo dice la caja — medilo con calibre. El axle_track no es 112mm porque parece — medilo. Cada milímetro importa.
