# Perfiles de calibración IITA v1

## 1. IMU

Objetivo:

- heading confiable para rectas cortas y giros repetidos.

Proceso:

1. Dejar el robot quieto varios segundos al encender.
2. Confirmar que el IMU esté listo.
3. Medir 10 giros completos reales.
4. Registrar lo que reporta el hub para 360 grados.
5. Cargar `heading_correction` con el promedio.

Tabla sugerida:

| Perfil | Mesa | Giros medidos | Reporte medio | heading_correction |
|---|---|---:|---:|---:|
| base | oficial 1 | 10 | 357.2 | 357.2 |
| base | oficial 2 | 10 | 358.4 | 358.4 |

## 2. Sensor de piso

Altura objetivo:

- 10 a 12 mm

Registrar:

| Perfil | Blanco | Negro | Umbral sugerido |
|---|---:|---:|---:|
| base | 78 | 12 | 45 |

## 3. Sensor frontal de color

No calibrar colores sobre el tapete. Calibrar con el artefacto dentro del túnel.

Registrar para cada color:

- 10 lecturas HSV;
- mediana;
- rango tolerado.

Tabla sugerida:

| Color | H mediana | S mediana | V mediana | Tolerancia H |
|---|---:|---:|---:|---:|
| rojo | 0 | 0 | 0 | 0 |
| amarillo | 0 | 0 | 0 | 0 |
| verde | 0 | 0 | 0 | 0 |
| azul | 0 | 0 | 0 | 0 |
| negro | 0 | 0 | 0 | 0 |

## 4. Elevador

Registrar ángulos:

| Estado | Ángulo |
|---|---:|
| home | 0 |
| pick | 0 |
| carry | 0 |
| place roof | 0 |
| stabilize tower | 0 |

## 5. DriveBase

Registrar:

| Parámetro | Valor |
|---|---:|
| wheel_diameter_mm | 0 |
| axle_track_mm | 0 |
| straight speed | 0 |
| straight accel | 0 |
| turn speed | 0 |

## 6. Criterio de congelamiento

No cambiar calibraciones el día de competencia por intuición. Solo actualizar si hubo medición nueva controlada.
