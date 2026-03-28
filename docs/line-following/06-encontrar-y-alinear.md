# 06 - Encontrar Línea y Alinearse con Precisión

## El problema: el robot no siempre empieza sobre la línea

En WRO RoboMission, después de hacer una tarea el robot puede quedar lejos de una línea. Necesitamos estrategias para encontrar líneas, alinearse, y posicionarse sobre el borde.

## Estrategia 1: Avanzar hasta encontrar la línea

```python
def avanzar_hasta_linea(sensor, velocidad=150):
    UMBRAL_NEGRO = 30
    robot.drive(velocidad, 0)
    while sensor.reflection() > UMBRAL_NEGRO:
        wait(10)
    robot.stop()
```

### Versión con distancia máxima (más segura)

```python
def avanzar_hasta_linea_seguro(sensor, velocidad=150, max_mm=500):
    UMBRAL_NEGRO = 30
    robot.reset()
    robot.drive(velocidad, 0)
    while sensor.reflection() > UMBRAL_NEGRO:
        if robot.distance() > max_mm:
            robot.stop()
            return False
        wait(10)
    robot.stop()
    return True
```

## Estrategia 2: Buscar línea en barrido (sweep)

Si no sabés dónde está la línea, el robot gira a un lado y otro ampliando el ángulo.

```python
def buscar_linea_barrido(sensor, angulo_max=120, velocidad_giro=80):
    UMBRAL_NEGRO = 30
    for angulo in range(30, angulo_max + 1, 30):
        # Girar a la derecha
        robot.drive(0, velocidad_giro)
        inicio = robot.angle()
        while abs(robot.angle() - inicio) < angulo:
            if sensor.reflection() < UMBRAL_NEGRO:
                robot.stop()
                return True
            wait(10)
        # Girar a la izquierda (el doble)
        robot.drive(0, -velocidad_giro)
        inicio = robot.angle()
        while abs(robot.angle() - inicio) < angulo * 2:
            if sensor.reflection() < UMBRAL_NEGRO:
                robot.stop()
                return True
            wait(10)
        # Volver al centro
        robot.drive(0, velocidad_giro)
        inicio = robot.angle()
        while abs(robot.angle() - inicio) < angulo:
            wait(10)
    robot.stop()
    return False
```

## Estrategia 3: Avanzar y barrer (combinada)

```python
def buscar_linea_avanzando(sensor, paso_mm=50, max_pasos=10, angulo_barrido=60):
    for i in range(max_pasos):
        robot.straight(paso_mm)
        if buscar_linea_barrido(sensor, angulo_barrido):
            return True
    return False
```

## Alineación perpendicular (squaring)

Usa 2 sensores para que ambos queden sobre la línea simultáneamente.

```python
def alinear_perpendicular(sensor_izq, sensor_der, left_motor, right_motor, velocidad=80):
    UMBRAL_NEGRO = 30
    izq_ok = False
    der_ok = False
    left_motor.run(velocidad)
    right_motor.run(velocidad)
    while not (izq_ok and der_ok):
        if sensor_izq.reflection() < UMBRAL_NEGRO and not izq_ok:
            left_motor.stop()
            izq_ok = True
        if sensor_der.reflection() < UMBRAL_NEGRO and not der_ok:
            right_motor.stop()
            der_ok = True
        wait(10)
    left_motor.stop()
    right_motor.stop()
```

### Alineación doble pasada (más preciso)

```python
def alinear_preciso(sensor_izq, sensor_der, left_motor, right_motor, repeticiones=2):
    for i in range(repeticiones):
        alinear_perpendicular(sensor_izq, sensor_der, left_motor, right_motor, velocidad=80)
        if i < repeticiones - 1:
            robot.straight(-30)
            wait(200)
    alinear_perpendicular(sensor_izq, sensor_der, left_motor, right_motor, velocidad=40)
```

```
Alineación paso a paso:

Paso 1: Robot torcido          Paso 2: Der llega primero
  [S_L]    [S_R]                [S_L]    [S_R]
    ○        ○                    ○      ──○──
═══════════════════             ═══════════════════

Paso 3: Izq llega → ¡Alineado!
  [S_L]    [S_R]
  ──○──    ──○──
═══════════════════
```

## Secuencia completa: encontrar → alinear → seguir

```python
def iniciar_seguimiento(sensor_centro, sensor_izq, sensor_der,
                         left_motor, right_motor, borde="izquierdo"):
    # Paso 1: Encontrar la línea
    encontrada = avanzar_hasta_linea_seguro(sensor_centro)
    if not encontrada:
        return False
    # Paso 2: Pasar y retroceder para alinear
    robot.straight(50)
    robot.straight(-80)
    # Paso 3: Alinear perpendicular
    alinear_preciso(sensor_izq, sensor_der, left_motor, right_motor)
    # Paso 4: Girar 90° para quedar paralelo
    robot.turn(-90 if borde == "izquierdo" else 90)
    # Paso 5: Encontrar la línea de nuevo
    avanzar_hasta_linea(sensor_centro)
    return True
```

## Detenerse y alinearse al final

```python
def detenerse_alineado(sensor_izq, sensor_der, sensor_centro,
                        left_motor, right_motor, borde="izquierdo"):
    UMBRAL_NEGRO = 25
    while True:
        seguir_linea_3s(borde)
        if (sensor_izq.reflection() < UMBRAL_NEGRO or
            sensor_der.reflection() < UMBRAL_NEGRO):
            robot.stop()
            break
        wait(10)
    alinear_preciso(sensor_izq, sensor_der, left_motor, right_motor)
```

## Tips para competencia

1. Calibrá los umbrales en el lugar de competencia
2. La alineación doble vale la pena por la precisión
3. Velocidad baja para buscar y alinear (~80 mm/s)
4. Siempre tené un plan B si no encontrás la línea
5. Probá con la batería en distintos niveles de carga
