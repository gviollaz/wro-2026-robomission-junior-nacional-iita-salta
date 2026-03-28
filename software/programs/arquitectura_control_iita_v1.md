# Arquitectura de control IITA v1 para Pybricks

## 1. Estructura de software recomendada

```text
software/
  calibration/
    robot_profile.py
    color_profiles.py
    imu_profile.py
  programs/
    main_safe.py
    main_full.py
    primitives.py
    mechanisms.py
    missions.py
    recovery.py
```

## 2. Configuración base

```python
PORT_LEFT_DRIVE = Port.A
PORT_RIGHT_DRIVE = Port.B
PORT_LIFT = Port.C
PORT_GATE = Port.D
PORT_FLOOR_SENSOR = Port.E
PORT_FRONT_SENSOR = Port.F
```

## 3. Perfil del robot

Parámetros que deben quedar externalizados:

- `wheel_diameter_mm`
- `axle_track_mm`
- `default_speed_mm_s`
- `default_acc_mm_s2`
- `turn_speed_deg_s`
- `imu_heading_correction`
- `floor_line_white`
- `floor_line_black`
- `lift_home_deg`
- `lift_pick_deg`
- `lift_place_deg`
- `gate_hold_deg`
- `gate_release_deg`

## 4. Primitivas críticas

### Movimiento

- `reset_pose()`
- `drive_mm(distance_mm, speed=None, accel=None)`
- `drive_until_reflection(target, relation)`
- `turn_to_heading(target_deg)`
- `arc_mm(radius_mm, angle_deg)`
- `bump_settle()` para quitar tensión mecánica antes de medir o soltar

### Sensorial

- `read_floor_reflection()`
- `read_artifact_hsv()`
- `classify_artifact_color()`
- `is_sensor_stable(samples=5)`

### Mecanismos

- `lift_home()`
- `lift_pick()`
- `lift_place_roof()`
- `gate_hold()`
- `gate_release()`
- `gate_jiggle()` para destrabar sin mover la base

## 5. Estados de misión

Estados recomendados:

- `START`
- `VISITORS_EARLY`
- `ARTIFACT_SCAN_1`
- `MUSEUM_DELIVERY`
- `RED_TOWERS`
- `YELLOW_TOPS`
- `ARTIFACT_SCAN_2`
- `VISITORS_LATE`
- `DIRT_SWEEP`
- `PARK_OR_FINISH`
- `RECOVERY`

## 6. Estrategia de clasificación de artefactos

No tomar decisión por una sola lectura.

Proceso recomendado:

1. Capturar artefacto en túnel.
2. Esperar 80 a 120 ms para estabilidad.
3. Medir 5 a 7 veces HSV.
4. Eliminar lectura extrema.
5. Promediar.
6. Redondear al color más cercano entre perfiles configurados.

## 7. Recovery

Todo plan debe tener recuperación local antes de abortar:

- si no detecta color válido, repetir lectura una vez;
- si gate no libera, `gate_jiggle()`;
- si heading excede tolerancia, re-referenciar con línea;
- si tapa amarilla no quedó estable, no insistir más de una vez.

## 8. Dos programas oficiales

### `main_safe.py`

Debe ser el programa de clasificación del equipo.

Criterio:

- maximiza puntaje esperado;
- evita suciedad si el robot no viene limpio;
- protege bonus;
- termina con margen.

### `main_full.py`

Programa para rondas donde el robot ya mostró estabilidad.

Criterio:

- agrega 4° artefacto y barrido tardío;
- asume calibración fina;
- tolera una sola recuperación larga.

## 9. Logging mínimo recomendado

En pantalla o consola:

- estado actual;
- color leído;
- heading;
- tiempo acumulado;
- evento de recovery.

Esto acelera mucho el ajuste en práctica.
