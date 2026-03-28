# SKILL: Seguimiento de Línea en Bloques (SPIKE App / Pybricks Blocks)

## Descripción
Skill para guiar a estudiantes en programación por bloques de seguimiento de línea para SPIKE Prime en WRO RoboMission. Cubre los mismos conceptos que la skill Python pero adaptados a programación visual.

## Plataformas compatibles
1. **Pybricks Blocks** (recomendado): interfaz en pybricks.com, bloques = Pybricks Python 1:1
2. **LEGO SPIKE App 3**: Word Blocks basados en Scratch, requiere Bluetooth

## Variables necesarias

| Variable | Valor inicial | Descripción |
|----------|--------------|-------------|
| negro | 10 | Línea negra calibrada |
| blanco | 90 | Fondo blanco calibrado |
| umbral | 50 | (negro + blanco) / 2 |
| error | 0 | Diferencia lectura vs umbral |
| error_anterior | 0 | Para componente D |
| integral | 0 | Para componente I |
| correccion | 0 | Giro calculado |
| Kp | 1.5 | Ganancia proporcional |
| Kd | 5.0 | Ganancia derivativa |
| conteo | 0 | Contador intersecciones |
| en_interseccion | False | Anti-rebote |

## Programa 1: Seguir línea con 1 sensor (solo P)

```
CUANDO INICIE:
  [umbral = (negro + blanco) / 2]
  [Repetir por siempre]:
    [error = (reflexión sensor C) - umbral]
    [correccion = Kp × error]
    [Conducir a (150) mm/s girando a (correccion) °/s]
    [Esperar 0.01 segundos]
```

Borde derecho: `error = umbral - reflexión` (invertido)

## Programa 2: Seguir línea con PID

```
CUANDO INICIE:
  [umbral = (negro + blanco) / 2]
  [error_anterior = 0]
  [integral = 0]
  [Repetir por siempre]:
    [error = (reflexión sensor C) - umbral]
    [integral = integral + error]
    [Si integral > 100 entonces integral = 100]
    [Si integral < -100 entonces integral = -100]
    [correccion = Kp×error + Ki×integral + Kd×(error - error_anterior)]
    [error_anterior = error]
    [Conducir a (150) mm/s girando a (correccion) °/s]
    [Esperar 0.01 segundos]
```

## Programa 3: Seguir y parar en intersección (3 sensores)

```
CUANDO INICIE:
  [conteo = 0]
  [en_interseccion = Falso]
  [objetivo = 2]  ← En cuál intersección parar

  [Repetir por siempre]:
    --- Seguimiento PID con sensor central D ---
    [error = (reflexión sensor D) - umbral]
    [correccion = Kp×error + Kd×(error - error_anterior)]
    [error_anterior = error]
    [Conducir a (150) mm/s girando a (correccion) °/s]

    --- Detección con sensor lateral C ---
    [Si (reflexión sensor C) < 25 Y NO en_interseccion]:
      [conteo = conteo + 1]
      [en_interseccion = Verdadero]
      [Si conteo >= objetivo]:
        [Parar]
        [Detener este bucle]
    [Si (reflexión sensor C) >= 25]:
      [en_interseccion = Falso]
    [Esperar 0.01 segundos]
```

## Programa 4: Calibración interactiva

```
CUANDO INICIE:
  [Mostrar "NEGRO" en pantalla]
  [Esperar hasta que se presione botón izquierdo]
  [Esperar 0.5 segundos]
  [negro = reflexión sensor C]
  [Mostrar número (negro)]
  [Esperar 2 segundos]
  [Mostrar "BLANCO" en pantalla]
  [Esperar hasta que se presione botón derecho]
  [Esperar 0.5 segundos]
  [blanco = reflexión sensor C]
  [umbral = (negro + blanco) / 2]
  [Mostrar número (umbral)]
```

## Bloques personalizados (Mis Bloques)

### "Seguir Línea" (borde, velocidad)
Calcula error según borde, aplica PID, conduce.

### "Ir A Intersección" (lado, número)
Resetea conteo, repite seguir + detectar hasta alcanzar número.

### "Girar En Intersección" (lado_det, número, lado_giro)
Llama Ir A Intersección, avanza 40mm, gira ±90°, avanza 25mm.

## Mapeo bloques ↔ Python

| Bloque | Python |
|--------|--------|
| Reflexión sensor C | `sensor_c.reflection()` |
| Conducir a V girando C | `robot.drive(V, C)` |
| Avanzar D mm | `robot.straight(D)` |
| Girar A grados | `robot.turn(A)` |
| Parar | `robot.stop()` |
| Esperar T seg | `wait(T * 1000)` |
| Repetir por siempre | `while True:` |
| Si...entonces | `if ...:` |

## Consejos por nivel

### Elementary (8-12 años):
- Empezar solo con control P
- 1 sensor al principio
- Programas cortos que hagan UNA cosa
- Pantalla del hub para feedback
- Probar cada bloque personalizado por separado

### Junior (11-15 años):
- PID completo con 3 sensores
- Bloques personalizados para cada acción
- Programa principal = lista de llamadas a bloques
- Variables para configurar sin cambiar lógica
- Luz del hub para debugging

### Errores comunes:
- Olvidar "Esperar" en el bucle → hub se cuelga
- No resetear variables al cambiar tramo
- Umbral dentro del bucle (debería estar afuera)
- No usar anti-rebote → cuenta de más
- Velocidad alta para primer intento → empezar a 100 mm/s
