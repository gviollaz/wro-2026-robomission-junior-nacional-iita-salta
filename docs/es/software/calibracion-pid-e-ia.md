# Calibracion PID y uso de IA en este repo

## Objetivo

Este documento tiene dos metas:

1. explicar **como calibrar mejor el movimiento** del robot,
2. explicar **como usar IA de forma util y ordenada** con este repo.

La idea no es “usar IA para que escriba codigo magico”, sino usarla como:
- revisor tecnico,
- ayudante para analizar pruebas,
- generador de variantes de rutina,
- mentor para documentar mejor.

---

## 1. Antes del PID: primero mecanica sana

Muchos equipos intentan tocar constantes PID demasiado pronto.

Eso es un error.

Si el robot tiene:
- ruedas flojas,
- chasis torcido,
- sensor de color mal montado,
- juego mecanico en brazo o garra,
- bateria con mucha variacion,

entonces **ningun PID lo va a salvar**.

### Orden correcto de trabajo
1. mecanica,
2. mediciones reales de ruedas y ancho,
3. velocidades y aceleraciones,
4. gyro,
5. referencias con pared/linea,
6. recien ahi PID fino,
7. por ultimo optimizacion de tiempo.

---

## 2. Que significan P, I y D

### P - Proporcional
Corrige segun el error actual.

- si el error es grande, corrige fuerte,
- si el error es chico, corrige poco.

**Muy bajo:** el robot corrige lento.

**Muy alto:** el robot oscila o “serrucha”.

### I - Integral
Corrige errores pequeños que quedan sostenidos en el tiempo.

Sirve para eliminar sesgos, por ejemplo:
- una rueda apenas mas fuerte,
- una inclinacion minima,
- un pequeño desvio sistematico.

**Muy alto:** el robot acumula demasiado y se pasa.

### D - Derivativo
Frena la correccion cuando el error cambia muy rapido.

Sirve para:
- suavizar,
- evitar sobrepaso,
- estabilizar curvas o correcciones fuertes.

**Muy alto:** el robot se vuelve nervioso o demasiado sensible al ruido.

### Explicacion simple para alumnos
- **P** empuja,
- **I** compensa errores persistentes,
- **D** amortigua.

---

## 3. Calibracion base de la DriveBase

Antes de tocar PID fino, hacer esto:

### Paso 1 - calibrar distancia
Mandar al robot avanzar una distancia larga conocida, por ejemplo 1000 mm.

- si avanza menos de lo pedido, ajustar el diametro de rueda,
- si avanza mas de lo pedido, ajustar en sentido contrario.

### Paso 2 - calibrar giro
Mandar al robot girar 360 grados.

- si gira de menos, corregir `axle_track`,
- si gira de mas, corregir al reves.

### Paso 3 - repetir
No tocar todo junto.

Primero distancia, despues giro, despues volver a verificar distancia.

---

## 4. Velocidad y aceleracion: la calibracion que mas puntos da

En Pybricks, la velocidad y la aceleracion ya son una forma de “control”.

Muchas veces el robot mejora mas al cambiar:
- velocidad maxima,
- aceleracion,
- desaceleracion,

que al tocar valores PID internos.

### Recomendacion practica
Tener tres modos:

```python
def velocidad_lenta():
    robot.settings(
        straight_speed=120,
        straight_acceleration=60,
        turn_rate=60,
        turn_acceleration=40
    )

def velocidad_normal():
    robot.settings(
        straight_speed=250,
        straight_acceleration=150,
        turn_rate=120,
        turn_acceleration=80
    )

def velocidad_rapida():
    robot.settings(
        straight_speed=400,
        straight_acceleration=200,
        turn_rate=180,
        turn_acceleration=100
    )
```

Eso ya existe en el repo y es una muy buena base para entrenar.

---

## 5. Gyro: cuando activarlo y como probarlo

La `DriveBase` de Pybricks puede usar el giroscopio para avanzar recto y girar con mejor precision.

### Recomendacion
Probar cada rutina en dos versiones:
- con gyro,
- sin gyro.

No asumir que el gyro siempre mejora todo.

### Donde suele ayudar mucho
- tramos largos rectos,
- giros repetidos,
- secuencias de varios movimientos consecutivos,
- robot con carga desbalanceada.

### Donde hay que vigilar
- muchas maniobras seguidas en el mismo sentido,
- golpes contra pared,
- hub mal orientado en el robot,
- rutinas que terminan con `hold` y dejan ruedas “peleando” por mantener posicion.

---

## 6. Ajuste fino del PID

Pybricks documenta que la `DriveBase` usa controladores para:
- **distancia**,
- **heading**.

Tambien documenta atributos como `heading_control` y `distance_control`.

### Recomendacion realista para equipo escolar

#### Nivel 1 - no tocar PID interno todavia
Trabajar con:
- buena mecanica,
- `use_gyro(True)` cuando convenga,
- `robot.settings(...)`,
- referencias por pared y linea,
- velocidades distintas por contexto.

Este nivel ya alcanza para construir un robot competitivo a nivel nacional.

#### Nivel 2 - tocar PID solo si ya hay estabilidad
Recién cuando el robot ya es consistente, se puede probar ajuste fino.

### Metodo simple de calibracion
1. dejar `I` y `D` bajos o cercanos a default,
2. subir `P` de a poco hasta que corrija firme,
3. si oscila, bajar `P`,
4. sumar un poco de `D` si hace falta amortiguar,
5. sumar muy poca `I` solo si hay sesgo persistente,
6. medir siempre con varias repeticiones, no con una sola corrida buena.

### Regla de oro
> cada cambio de PID se valida con al menos 5 a 10 repeticiones.

---

## 7. Opcion avanzada: PID manual para avance recto

A veces conviene hacer un control propio con `drive(speed, turn_rate)`.

### Idea general
- fijar un angulo objetivo,
- leer heading actual,
- calcular error,
- aplicar una correccion de giro mientras se avanza.

Ejemplo conceptual:

```python
angulo_objetivo = 0
kp = 2.0
kd = 0.6
error_anterior = 0

while robot.distance() < 300:
    error = angulo_objetivo - hub.imu.heading()
    derivada = error - error_anterior
    correccion = kp * error + kd * derivada
    robot.drive(180, correccion)
    error_anterior = error

robot.stop()
```

### Ventajas
- da mucho control,
- sirve para experimentar,
- ayuda a entender de verdad la dinamica del robot.

### Desventajas
- exige mas pruebas,
- puede empeorar si se usa sin metodo,
- es facil perder tiempo de temporada afinando de mas.

---

## 8. Calibracion de sensor de color

Este repo ya tiene un script `software/calibration/calibrar_color.py`.

Eso es correcto porque en RoboMission 2026 hay colores y objetos randomizados que conviene medir en el material real.

### Procedimiento recomendado
1. medir todos los colores del juego,
2. registrar `h`, `s`, `v` y `reflection`,
3. repetir varias veces,
4. comparar con distintas iluminaciones del aula o torneo,
5. guardar rangos seguros, no un unico numero.

### Para lineas o bordes
Usar sobre todo `reflection()`.

### Para artefactos de distintos colores
Usar `hsv()` y, si conviene, configurar colores detectables medidos de antemano.

---

## 9. Como registrar pruebas sin complicarse

Un equipo mejora mas rapido cuando anota datos.

### Log minimo sugerido
Por cada prueba anotar:
- nombre de rutina,
- bateria aproximada,
- version del codigo,
- velocidad usada,
- si uso gyro,
- si hubo pared o linea como referencia,
- resultado (ok / fallo),
- tipo de fallo.

### Tipos de fallo utiles
- giro corto,
- giro largo,
- deriva recta,
- detecto tarde la linea,
- detecto mal color,
- agarro mal,
- deposito mal,
- golpeo barrera.

Con 20 o 30 registros ya aparecen patrones muy claros.

---

## 10. Uso inteligente de IA en este repo

El repo tiene reglas claras en `AI-INSTRUCTIONS.md`:
- declarar IA en cada PR si se uso,
- incluir fuentes si la IA aporta hechos o datos,
- no subir informacion sensible,
- probar siempre en robot o simulacion antes de mergear.

Eso esta muy bien y conviene respetarlo siempre.

---

## 11. Tres skills practicos de IA para este repo

No hace falta una IA “magica”. Alcanzan tres modos de trabajo bien definidos.

### Skill 1 - Revisor de rutina
**Objetivo:** revisar una rutina y encontrar errores de logica o fragilidad.

**Entrada:**
- archivo Python,
- descripcion de la mision,
- resultado observado.

**Salida esperada:**
- posibles fallas,
- mejoras concretas,
- chequeos de seguridad,
- lugares donde conviene bajar velocidad o agregar referencia.

**Prompt base:**

```text
Actua como mentor WRO RoboMission. Revisa este archivo y detecta:
1) errores de logica,
2) movimientos fragiles,
3) puntos donde falta re-alineacion,
4) lugares donde conviene usar velocidad lenta,
5) riesgos por drift o rebote.
Responde con cambios concretos y breves.
```

### Skill 2 - Analista de calibracion
**Objetivo:** analizar resultados de prueba y proponer ajustes.

**Entrada:**
- tabla de pruebas,
- valores HSV o reflection,
- descripcion del error.

**Salida esperada:**
- hipotesis ordenadas,
- siguiente experimento minimo,
- parametros a tocar primero.

**Prompt base:**

```text
Analiza estos resultados de calibracion como coach de WRO.
No me des teoria general: indicame la causa mas probable,
que parametro tocar primero y que prueba corta hacer despues.
```

### Skill 3 - Diseñador de estrategia
**Objetivo:** convertir reglas y tablero en una estrategia por capas.

**Entrada:**
- objetivo de puntaje,
- misiones prioritarias,
- fortalezas del robot,
- limitaciones actuales.

**Salida esperada:**
- propuesta de orden de misiones,
- referencias de re-alineacion,
- puntos donde usar odometria, pared, linea o color,
- riesgos y plan B.

**Prompt base:**

```text
Diseña una estrategia de ronda para WRO RoboMission Junior 2026.
Quiero una secuencia robusta, no solo rapida.
Marca donde conviene:
- usar odometria,
- corregir con pared,
- corregir con linea,
- leer color,
- bajar velocidad.
```

---

## 12. Flujo recomendado de IA para el equipo

### Flujo corto y util
1. correr prueba real,
2. anotar que fallo,
3. pasar a la IA el archivo + observacion,
4. pedir solo **una** mejora concreta,
5. volver a probar,
6. comparar.

### Lo que no conviene hacer
- pedir “reescribime todo el robot”,
- mezclar 10 cambios a la vez,
- copiar codigo sin entender,
- aceptar recomendaciones sin probar en tablero.

---

## 13. Recomendacion final para el equipo

La IA suma mas valor cuando el equipo ya sabe formular bien el problema.

Preguntas buenas producen respuestas utiles:
- “¿por que deriva a la derecha en los ultimos 20 cm?”
- “¿conviene re-alinear con pared o con linea antes de soltar la torre?”
- “¿que variable tocar primero si detecta tarde la linea negra?”

Preguntas vagas producen respuestas vagas.

---

## 14. Conclusiones

Para competir mejor:

- primero mecanica,
- despues calibracion de rueda y ancho,
- despues velocidad y aceleracion,
- despues gyro,
- despues referencias reales,
- recien al final PID fino.

Y para usar IA bien:

- pedir revisiones concretas,
- dar contexto real del tablero,
- pasar resultados de prueba,
- validar siempre en robot.

En resumen:

> **la repetibilidad gana mas rondas que la complejidad.**

---

## Fuentes consultadas

- Pybricks Documentation: DriveBase, use_gyro, settings, heading_control, distance_control, state
- Pybricks Documentation: motor control / control.pid / control limits
- Pybricks Documentation: ColorSensor, reflection, hsv, detectable colors
- WRO 2026 Season / Robots Meet Culture
- WRO 2026 RoboMission Junior Game Rules (Heritage Heroes)
- WRO Scoring System - International Final 2025 RoboMission Junior
- `AI-INSTRUCTIONS.md`
- `software/programs/base_config.py`
- `software/calibration/calibrar_color.py`
