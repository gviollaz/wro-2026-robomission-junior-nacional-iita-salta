# 02 - Odometría Precisa: Que el Robot Sepa Dónde Está

## ¿Qué es la odometría?

La **odometría** es cómo el robot calcula cuánto avanzó y cuánto giró, midiendo las vueltas de sus ruedas. Es como el cuentákilómetros de un auto.

## Los dos valores que definen todo

```python
robot = DriveBase(motor_izq, motor_der,
    wheel_diameter=56,   # Diámetro de la rueda en mm
    axle_track=112)      # Distancia entre puntos de contacto rueda-piso
```

Si estos números están mal, **todo está mal**.

## Cómo medir wheel_diameter

### Método 1: Calibre (lo mejor)
Medí el diámetro con calibre incluyendo la goma.

### Método 2: Cinta
1. Marcá un punto en la rueda y en el piso
2. Rodá una vuelta completa
3. `diámetro = distancia / π`

### Método 3: Calibración por software (el más preciso)

```python
# Avanzar 1000mm con valor nominal
robot.straight(1000)
# Medir distancia real
# diámetro_correcto = diámetro_puesto × (1000 / distancia_real)
# Ejemplo: 56 × (1000 / 985) = 56.85 mm
```

## Cómo medir axle_track

```python
# Girar 10 vueltas (3600°) y ver si queda alineado
robot.turn(3600)
# Si giró de más → axle_track muy chico → subir
# Si giró de menos → axle_track muy grande → bajar
```

**Tip:** Calibrar axle_track SIN giroscopio primero, activar gyro después.

## Fuentes de error

| Error | Solución |
|-------|----------|
| Patinaje de ruedas | Arranque suave, ruedas limpias |
| Compresión de goma | Calibrar con robot armado y con peso |
| Desgaste desigual | Revisar y rotar ruedas |
| Juego mecánico (backlash) | Transmisión directa |
| Superficie irregular | Usar giroscopio para compensar |

## Combinar odometría con giroscopio

```python
robot.use_gyro(True)
# Distancia → ruedas (odometría)
# Dirección → giroscopio
# = lo mejor de ambos mundos
```

## Combinar con sensores

```python
def avanzar_hasta_linea_o_distancia(sensor, distancia_max, velocidad=150):
    robot.reset()
    robot.drive(velocidad, 0)
    while True:
        if sensor.reflection() < 25:
            robot.stop()
            return "linea"
        if robot.distance() >= distancia_max:
            robot.stop()
            return "distancia"
        wait(10)
```

## Orden de calibración

1° wheel_diameter → 2° axle_track → 3° heading_correction → 4° activar gyro
