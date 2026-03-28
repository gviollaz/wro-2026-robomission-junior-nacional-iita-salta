# Estrategias de posicionamiento y navegacion para RoboMission Junior 2026

## Objetivo

Este documento explica una estrategia **simple de entender** y **fuerte en competencia** para ubicar el robot dentro del tablero usando una combinacion de:

1. **odometria** (distancia y giro estimados),
2. **giroscopio** (para mantener rumbo),
3. **alineacion con paredes** (referencia fisica),
4. **alineacion con lineas o marcas del piso** usando sensor de color,
5. **deteccion de colores de artefactos** con HSV.

La idea principal es esta:

> **Los robots mas consistentes no dependen de una sola tecnica.**
> Usan odometria para ir rapido entre zonas y usan referencias fisicas o visuales para corregir errores acumulados.

---

## 1. Que nos ensena la competencia

La categoria RoboMission tiene **aleatorizacion**. En Junior 2026 cambian artefactos y particulas, asi que no alcanza con memorizar un camino fijo. El robot debe tomar decisiones y corregirse durante la ronda.

Ademas, los puntajes altos en finales internacionales muestran que los equipos fuertes no hacen una sola corrida buena: logran **muchas corridas altas**. Eso indica **repetibilidad**, no solo velocidad.

**Leccion para el equipo:**
- primero construir una base **estable y repetible**,
- despues aumentar velocidad,
- nunca al reves.

---

## 2. Arquitectura recomendada de navegacion

Conviene pensar la navegacion en **tres capas**.

### Capa A - Movimiento largo por odometria
Se usa para salir de base y llegar cerca de una zona.

Ejemplos:
- avanzar 420 mm,
- girar 88 grados,
- avanzar 180 mm.

Esta capa es rapida, pero acumula error por:
- deslizamiento de ruedas,
- flexion del chasis,
- bateria distinta,
- pequeños golpes,
- diferencia real entre rueda izquierda y derecha.

### Capa B - Correccion local con referencias
Cuando el robot llega cerca de una zona, conviene **re-anclar** la posicion con una referencia real:
- pared,
- borde fisico,
- linea negra,
- marca de color,
- area con reflexion conocida.

Esto reduce mucho el error acumulado.

### Capa C - Accion fina sobre la mision
Recien despues de re-alinear conviene:
- dejar una torre,
- poner una tapa amarilla,
- soltar un visitante,
- leer el color de un artefacto,
- barrer particulas.

**Regla practica:**
> no ejecutar una accion delicada inmediatamente despues de una trayectoria larga; antes, corregir posicion.

---

## 3. Odometria: que es y como usarla bien

La odometria estima donde esta el robot a partir de:
- rotacion de motores,
- diametro de rueda,
- distancia entre ruedas.

En Pybricks, la `DriveBase` necesita esos datos para estimar distancias y giros.

### Lo mas importante
La odometria solo funciona bien si el robot esta **bien medido y bien calibrado**.

### Orden correcto
1. medir el diametro real de rueda,
2. medir el `axle_track` real,
3. probar avance largo,
4. corregir diametro de rueda,
5. probar giro de 360 grados,
6. corregir `axle_track`,
7. repetir.

### Regla practica de competencia
- usar odometria para tramos largos,
- usar correcciones por pared o linea cada vez que el robot cambie de zona,
- no encadenar demasiados movimientos largos sin re-referencia.

---

## 4. Arranque suave y detencion suave

Muchos errores aparecen al principio o al final del movimiento.

### Problemas de un arranque brusco
- patina la rueda,
- se mueve la carga,
- el robot gira un poco aunque no deberia,
- pierde alineacion antes de empezar.

### Problemas de una frenada brusca
- la carga sigue por inercia,
- la torre se cae,
- el robot rebota,
- el sensor pasa de largo una linea.

### Recomendacion
Usar perfiles de velocidad distintos para:
- desplazamiento rapido entre zonas,
- acercamiento final,
- maniobra delicada.

### Tres perfiles utiles
- **rapido:** para viajar sin carga delicada,
- **normal:** para la mayoria de recorridos,
- **lento:** para captura, deposito y alineacion fina.

### Idea clave para alumnos
> Ir mas lento en el ultimo 20% del movimiento suele dar mas puntos que intentar ganar 0.2 segundos.

---

## 5. Alineacion con paredes

La pared es una referencia muy poderosa porque no depende de la luz ni del color del piso.

### Objetivo
Lograr que el robot quede:
- con angulo conocido,
- con una cara bien apoyada,
- y con una posicion repetible antes de la siguiente accion.

### Metodo recomendado
1. acercarse con velocidad baja,
2. tocar suave con una cara plana del robot,
3. esperar un instante corto,
4. retroceder unos milimetros si hace falta,
5. resetear distancia/angulo si esa posicion es una referencia conocida.

### Buenas practicas mecanicas
- tener una cara frontal o lateral **recta y robusta**,
- evitar piezas flexibles en la superficie que toca la pared,
- no usar la garra como referencia geometrica principal,
- si es posible, apoyar en dos puntos separados para “cuadrar” mejor el chasis.

### Error comun
Chocar fuerte contra la pared para “asegurarse”.
Eso suele empeorar la repetibilidad.

**Mejor:** tocar suave, con poca aceleracion y poca velocidad.

---

## 6. Alineacion con lineas o marcas usando sensor de color

El sensor de color sirve para dos cosas distintas:

1. **ver una linea o marca del piso** por reflexion,
2. **detectar un color especifico** con HSV.

No es lo mismo.

### 6.1. Ver una linea por reflexion
Para detectar una linea negra o una zona mas oscura, conviene usar `reflection()`.

### Umbral recomendado
Tomar varias mediciones de:
- piso claro,
- linea oscura,

y usar como umbral el promedio entre ambos valores.

Ejemplo:
- piso: 62,
- linea: 18,
- umbral sugerido: 40.

### Estrategia muy util
En vez de confiar solo en “frenar justo arriba de la linea”, usar esta secuencia:

1. avanzar hasta detectar la linea,
2. seguir unos milimetros mas,
3. retroceder lento hasta el borde deseado,
4. guardar esa referencia.

Esto mejora mucho la repetibilidad.

### 6.2. Ver colores de artefactos con HSV
Cuando el objetivo es distinguir artefactos de distinto color, conviene usar `hsv()` o configurar colores detectables medidos sobre el objeto real.

### Reglas importantes
- medir siempre a la misma altura,
- medir con el mismo angulo,
- evitar que entre luz lateral variable,
- hacer calibracion sobre el material real del juego,
- guardar rangos o colores calibrados, no valores “de memoria”.

---

## 7. Avance recto con giroscopio

Aunque la odometria sirve para avanzar, muchas veces el robot se desvía un poco. Por eso conviene usar el giroscopio para mantener el rumbo.

### Dos formas de usarlo

#### Opcion 1 - usar la DriveBase con gyro activado
Es la opcion mas simple y recomendable para empezar.

Sirve para:
- avanzar recto con menos drift,
- girar con mejor precision,
- mantener mejor el angulo entre maniobras.

#### Opcion 2 - hacer una correccion manual tipo PID
Es util cuando se quiere controlar en detalle el avance con `drive(speed, turn_rate)`.

La idea es:
- fijar un angulo objetivo,
- medir el error actual,
- aplicar una correccion al giro mientras el robot avanza.

Ejemplo conceptual:

```python
error = angulo_objetivo - hub.imu.heading()
correccion = kp * error + kd * derivada
robot.drive(velocidad, correccion)
```

### Cuando usar cada una
- **equipo principiante o intermedio:** usar primero `use_gyro(True)` y construir rutina estable.
- **equipo avanzado:** usar PID manual solo en tramos donde realmente agregue valor.

---

## 8. Alineacion fina antes de depositar objetos

Antes de soltar un objeto, conviene definir un “ritual” fijo.

Ejemplo:
1. llegar por odometria,
2. corregir con pared o linea,
3. avanzar lento los ultimos milimetros,
4. detener suave,
5. ejecutar brazo/garra,
6. retroceder limpio.

Esto parece mas lento, pero en realidad aumenta los puntos porque reduce fallas.

---

## 9. Estrategia de tablero recomendada

### Estrategia robusta
- usar una salida de base simple,
- llegar a una primera referencia fuerte,
- desde ahi dividir el tablero en zonas,
- re-alinear al entrar en cada zona,
- ejecutar la mision local,
- volver a una referencia conocida antes de ir a la siguiente.

### Estrategia fragil
- hacer una sola mega-rutina larga,
- depender solo de distancias absolutas,
- no corregir despues de empujar o cargar objetos,
- usar demasiada velocidad en maniobras delicadas.

---

## 10. Secuencia de entrenamiento recomendada

### Etapa 1 - exactitud mecanica
- que avance 500 mm bien,
- que gire 90 grados bien,
- que gire 180 grados bien.

### Etapa 2 - referencias
- tocar pared y quedar cuadrado,
- detectar linea siempre en el mismo lugar,
- identificar colores reales del set.

### Etapa 3 - combinaciones
- odometria + pared,
- odometria + linea,
- giro + linea,
- pared + deposito.

### Etapa 4 - misiones completas
- medir consistencia en 10 repeticiones,
- anotar porcentaje de exito,
- recien despues aumentar velocidad.

---

## 11. Checklist rapido para alumnos

Antes de competir, preguntar:

- ¿El robot arranca sin patinar?
- ¿El robot frena sin rebotar?
- ¿La rueda esta bien medida?
- ¿El ancho entre ruedas esta calibrado?
- ¿El gyro mejora o empeora esta rutina?
- ¿La rutina tiene una referencia real antes de la accion importante?
- ¿El sensor de color fue calibrado en el tablero real?
- ¿La maniobra funciona 8 o 9 veces de 10?

Si la respuesta es “no” en varias de estas preguntas, todavia no conviene acelerar.

---

## 12. Conclusiones

La formula mas competitiva para RoboMission no es “solo line following” ni “solo odometria”.

La estrategia mas fuerte suele ser:

- **odometria para ir rapido**,
- **gyro para mantener rumbo**,
- **paredes y lineas para corregir**,
- **HSV para decidir por color**,
- **velocidad baja al final de cada accion delicada**.

En otras palabras:

> **rapido entre zonas, preciso dentro de la zona.**

---

## Fuentes consultadas

- WRO 2026 Season / Robots Meet Culture
- WRO 2026 RoboMission Junior Game Rules (Heritage Heroes)
- WRO Scoring System - International Final 2025 RoboMission Junior
- Pybricks Documentation: DriveBase, use_gyro, state, settings
- Pybricks Documentation: ColorSensor, reflection, hsv, detectable colors
- `software/programs/base_config.py`
- `software/calibration/calibrar_color.py`
