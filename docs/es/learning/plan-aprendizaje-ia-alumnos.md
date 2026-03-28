# Plan A: Robot de Campeón con IA como Copiloto Educativo

## La tesis: niños + IA > ingenieros solos

> En 2024, diseñar un robot con PCB custom, control PID, sensor fusion, y servos inteligentes requería un ingeniero electrónico con 5+ años de experiencia. En 2026, un alumno de 13 años con Claude como copiloto puede hacerlo. No porque la IA haga el trabajo por él, sino porque la IA le EXPLICA cada decisión mientras la toman juntos.

> No ocultamos el uso de IA. Lo mostramos como la herramienta más poderosa de aprendizaje que existe. Los jueces de WRO no evalúan si el equipo trabajó solo — evalúan si el equipo ENTIENDE lo que hizo.

Este documento es el plan de aprendizaje para que los alumnos de IITA pasen de "no sé qué es un encoder" a "diseñé un robot con PCB custom y puedo explicar cada componente" en 14 semanas, con IA como copiloto en cada paso.

---

## 1. Filosofía: la IA no reemplaza, amplifica

### Lo que la IA hace por los alumnos

- **Explica conceptos a su nivel**: "¿Qué es PID?" → Claude lo explica con la analogía de la ducha caliente, no con ecuaciones diferenciales
- **Genera código comentado**: cada línea tiene un comentario que el alumno puede leer y entender
- **Diseña piezas 3D parametrizadas**: el alumno cambia UN número y entiende cómo afecta al diseño
- **Responde preguntas en tiempo real**: el alumno pregunta "¿por qué el motor vibra?" y Claude diagnostica
- **Documenta todo**: cada decisión queda explicada en el repo, no en la cabeza del coach

### Lo que la IA NO hace por los alumnos

- **No arma el robot**: las manos son de los alumnos. Soldar, atornillar, cablear, imprimir — todo lo hacen ellos
- **No corre los programas**: el alumno es quien presiona el botón, observa qué pasa, y decide qué cambiar
- **No toma decisiones estratégicas**: "¿Hacemos primero las torres o los visitantes?" — eso lo decide el equipo
- **No calibra**: el alumno mide con el calibre, anota el número, y lo pone en el código
- **No practica**: las 200+ horas de ensayo son del equipo, no de la IA

### La metáfora

La IA es como un libro de texto infinito que además responde preguntas. Ningún juez de WRO descalifica a un equipo por haber leído un libro. La diferencia es que este "libro" se adapta al nivel del alumno y responde en tiempo real.

---

## 2. El plan de 14 semanas

### FASE 0: Fundamentos (Semanas 1-2)

**Objetivo:** Los alumnos entienden electricidad básica, programación, y mecánica antes de tocar el robot.

#### Semana 1: Electricidad y electrónica

| Día | Actividad | Con IA | Sin IA |
|-----|-----------|--------|--------|
| Lun | ¿Qué es voltaje, corriente, resistencia? | Claude explica con analogía del agua | Alumno mide voltajes con multímetro |
| Mar | ¿Qué es un motor DC? ¿Cómo gira? | Claude muestra diagrama | Alumno conecta motor a pila y lo ve girar |
| Mié | ¿Qué es PWM? ¿Cómo varía velocidad? | Claude explica con ejemplo de luz dimmer | Alumno controla LED con potenciómetro |
| Jue | ¿Qué es un encoder? ¿Cómo cuenta? | Claude anima un disco encoder | Alumno gira motor a mano y lee pulsos |
| Vie | ¿Qué es I2C? ¿Cómo hablan los chips? | Claude dibuja el bus | Alumno conecta sensor BNO055 y lee datos |

**Evaluación:** El alumno puede explicar con sus palabras qué es voltaje, PWM, encoder, e I2C. Si no puede, repetir la semana.

#### Semana 2: Programación básica

| Día | Actividad | Con IA | Sin IA |
|-----|-----------|--------|--------|
| Lun | Variables, if/else, loops en Arduino | Claude genera ejercicios adaptativos | Alumno escribe "hola mundo" que prende LED |
| Mar | Funciones: encapsular acciones | Claude explica por qué dividir código | Alumno crea función `prender_led(pin)` |
| Mié | Leer sensores: analogRead, digitalRead | Claude genera código comentado | Alumno lee potenciómetro y muestra en serial |
| Jue | Controlar motor con DRV8833 | Claude explica el H-bridge | Alumno hace girar motor para adelante y atrás |
| Vie | **Mini-proyecto**: robot que avanza 1 segundo y frena | Claude guía paso a paso | Alumno construye y programa solo |

**Evaluación:** El alumno puede escribir un programa que lea un sensor y controle un motor basándose en la lectura.

### FASE 1: Construir el robot base (Semanas 3-5)

**Objetivo:** Robot que se mueve recto, gira, y sigue una línea básica.

#### Semana 3: Tracción + odometría

**Concepto clave que el alumno aprende: FEEDBACK**

"El motor gira, pero ¿cuánto giró? Sin encoder, no sabés. Con encoder, contás pulsos. Es como caminar con los ojos cerrados vs abiertos."

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| Montar motores Pololu en brackets 3D | Cómo funciona el bracket, tolerancias | Atornillar, verificar que giran libres |
| Conectar DRV8833 | Diagrama de conexión, por qué cada pin | Cablear en breadboard, verificar con multímetro |
| Leer encoders | Qué es cuadratura, por qué 2 canales | Girar rueda a mano, ver pulsos en serial monitor |
| PID de velocidad | Analogía: termostato de heladera | Cambiar Kp y ver qué pasa. "Si Kp sube, ¿qué pasa?" |
| Calibrar wheel_diameter | Por qué el diámetro importa | Medir con calibre, marcar 1 metro, contar pulsos |

**Ejercicio práctico:** El robot avanza exactamente 500mm. El alumno mide con regla. Si se pasa o se queda corto, el alumno ajusta el wheel_diameter. Repetir hasta que el error sea <5mm.

**Pregunta que el alumno debe poder responder:** "¿Qué pasa si la rueda se gasta y el diámetro cambia 0.5mm?"

#### Semana 4: Giroscopio + navegación

**Concepto clave: DRIFT Y CORRECCIÓN**

"El giroscopio del celular sabe para dónde mirás. Pero si lo dejás un rato, se confunde. El BNO055 tiene un magnetómetro que lo corrige, como una brújula."

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| Conectar BNO055 por I2C | Qué hace la fusión de sensores onboard | Conectar 4 cables, verificar dirección I2C |
| Leer heading en tiempo real | Qué son yaw/pitch/roll | Girar el sensor a mano, ver números cambiar |
| Giro preciso de 90° | Cómo usar heading como feedback | Programar giro, medir con escuadra, ajustar |
| Navegar a coordenadas (x, y) | Trigonometría básica (sin/cos) | Marcar puntos en el piso, robot va a cada uno |
| Fusionar odometría + gyro | Por qué no confiar en uno solo | Comparar: solo encoders vs solo gyro vs fusión |

**Ejercicio práctico:** El robot hace un cuadrado de 300×300mm y vuelve al punto de inicio. Medir el error de retorno. Debe ser <10mm.

**Pregunta que el alumno debe poder responder:** "¿Por qué el robot se desvía más cuando solo usa encoders y no tiene giroscopio?"

#### Semana 5: Sensor de distancia + primeras misiones

**Concepto clave: PERCEPCIÓN**

"El robot es ciego si solo cuenta pasos. Con el sensor ToF, puede VER a qué distancia está la pared o un objeto. Es como darle un bastón al robot."

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| Conectar VL53L5CX | Cómo funciona Time-of-Flight (luz que rebota) | Apuntar sensor a objetos, ver distancias |
| Mapa 8×8 de profundidad | Qué significa cada celda de la grilla | Visualizar el mapa en serial, entender FOV |
| Posicionarse frente a un objeto | Algoritmo: avanzar hasta distancia X | Poner objeto en el piso, robot se posiciona solo |
| Primera misión simple | Arquitectura de misión por funciones | Programar "ir a punto A, agarrar, llevar a B" |

### FASE 2: Mecanismos inteligentes (Semanas 6-8)

**Objetivo:** Garra que agarra, brazo que sube, pala que barre. El alumno entiende POR QUÉ cada mecanismo funciona así.

#### Semana 6: Dynamixel + garra

**Concepto clave: SERVO INTELIGENTE**

"Un servo normal es como un brazo que va a una posición y se queda. Un Dynamixel es como un brazo que siente cuánta fuerza hace. Si apretás mucho, para. Si no toca nada, sigue."

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| Protocolo Dynamixel 2.0 | Qué es half-duplex, por qué ID único | Conectar, escanear con Dynamixel Wizard, cambiar ID |
| Control de posición | Cómo el servo sabe dónde está (encoder absoluto 4096 pasos) | Mover garra a posiciones, anotar ángulos |
| Control de corriente | Qué es corriente, por qué indica fuerza | Cerrar garra vacía vs con objeto, comparar corriente |
| Detección de agarre | Umbral de corriente → "tengo algo" | Programar: cerrar garra, si corriente > X → agarré |
| Imprimir garra V1 | Por qué la forma en V centra el objeto | Diseñar en Onshape (o modificar .scad), imprimir |

**Ejercicio práctico:** La garra agarra una torre LEGO 10 de 10 veces sin fallar. Si falla, el alumno identifica POR QUÉ y modifica el diseño.

**Pregunta que el alumno debe poder responder:** "¿Cómo sabe el robot que agarró el objeto sin usar una cámara?"

#### Semana 7: Brazo + apilado de torres

**Concepto clave: PRECISIÓN MECÁNICA**

"Apilar una torre es el desafío más difícil del juego. No es un problema de software ni de sensores. Es un problema de que cada pieza del mecanismo hace EXACTAMENTE lo mismo cada vez."

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| Diseñar brazo con reducción | Por qué engranajes dan fuerza pero quitan velocidad | Probar brazo con y sin reducción, sentir la diferencia |
| 3 posiciones del brazo | Por qué ABAJO, TRANSPORTE, ALTO | Programar posiciones, verificar repetibilidad (10 veces) |
| Secuencia de apilado | Cada paso y por qué en ese orden | Practicar apilado manual primero, después automático |
| Detección de contacto | Corriente del Dynamixel al tocar la base | Ver gráfico de corriente en tiempo real mientras apila |
| Prueba de estrés apilado | Qué significa "confiabilidad" en números | 50 intentos de apilado, anotar éxitos/fallos, calcular % |

**LA PRUEBA DEFINITIVA:** El alumno apila la torre amarilla 8 de 10 veces. Si no lo logra, no seguir con otras misiones — el apilado es lo que separa a los campeones.

#### Semana 8: Pala + sensor de color + misiones combinadas

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| Pala barredora: diseño y montaje | Por qué ancha, por qué plegable | Imprimir, montar, probar barrido de partículas |
| Sensor TCS34725: lectura RGBC | Qué son R, G, B, C y por qué no alcanza con R/G/B | Leer colores de los 5 artefactos, calibrar |
| Normalización de color | Por qué r/(R+G+B) es inmune a luz | Leer mismo objeto con luz fuerte y débil, comparar |
| Programa de misión completo | Máquina de estados, timeouts, fallbacks | Programar todas las misiones, cada una como función |

### FASE 3: Integración y PCB (Semanas 9-11)

**Objetivo:** Pasar de breadboard a PCB definitiva. El alumno entiende POR QUÉ una PCB es mejor que cables sueltos.

#### Semana 9: Diseño de PCB

**Concepto clave: DE PROTOTIPO A PRODUCTO**

"Los cables en breadboard funcionan en el escritorio. En competencia, una vibración desconecta un cable y el robot muere. La PCB es un circuito permanente donde nada se desconecta."

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| ¿Qué es una PCB? Capas, trazas, vías | Analogía: las calles de una ciudad para electricidad | Ver PCBs reales (de un celular roto, de Arduino) |
| KiCad básico: esquemático | Cómo dibujar el circuito en la computadora | Dibujar el circuito del robot (con ayuda de Claude) |
| KiCad: ruteo de PCB | Cómo las líneas del esquemático se vuelven trazas de cobre | Rutear componentes principales (Claude guía, alumno ejecuta) |
| Revisión DRC | Qué errores buscar antes de fabricar | Correr DRC, entender cada error, corregir |
| Enviar a JLCPCB | Cómo se fabrica una PCB industrialmente | Generar Gerbers, subir a JLCPCB, hacer pedido |

**Momento WOW:** Cuando la PCB llegue (semana 11), el alumno va a tener en la mano un circuito que ÉL diseñó. Esto es transformador.

**Pregunta que el alumno debe poder responder:** "¿Qué pasa si dos trazas de cobre se tocan? ¿Por qué las capas internas son planos de GND?"

#### Semana 10: Firmware definitivo

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| Arquitectura del firmware | Por qué setup() y loop(), por qué funciones separadas | Escribir el esqueleto (Claude genera, alumno entiende cada línea) |
| Máquina de estados para misiones | Qué es un estado, transiciones, condiciones | Dibujar la máquina de estados en papel antes de programar |
| Timeouts y fallbacks | Por qué cada acción necesita un tiempo máximo | Probar: ¿qué pasa si el sensor no lee? ¿El robot se traba? |
| WiFi dashboard para debug | Ver sensores en el celular en tiempo real | Conectar al robot por WiFi, ver datos en vivo |
| Code review con IA | "Explicame qué hace esta función" | Alumno lee código y explica, Claude corrige entendimiento |

**Ejercicio crítico:** El alumno lee el programa completo línea por línea y explica qué hace cada una. Si hay una línea que no entiende, PARAR y explicar hasta que la entienda. No se avanza con código que el alumno no comprende.

#### Semana 11: PCB llega + ensamble final

| Actividad | IA explica | Alumno hace |
|-----------|-----------|-------------|
| Inspección visual de la PCB | Qué buscar (cortocircuitos, pads faltantes) | Mirar con lupa, comparar con diseño |
| Soldadura de componentes | Técnica de soldadura SMD con cautín | Soldar (con supervisión del coach) |
| Prueba de continuidad | Por qué probar antes de encender | Multímetro en cada conexión crítica |
| Primer encendido | Qué puede salir mal (cortocircuito, componente al revés) | Conectar batería con ojo en el multímetro |
| Migrar firmware de breadboard a PCB | Debería ser idéntico (mismos pines) | Cargar programa, verificar que todo funciona |

### FASE 4: Competencia (Semanas 12-14)

#### Semana 12-13: Pruebas intensivas en tapete real

| Actividad | Cantidad |
|-----------|----------|
| Ejecuciones completas del programa | 50+ |
| Prueba de cada randomización | 5 combinaciones de artefactos |
| Prueba con batería baja (30%) | 5 ejecuciones |
| Prueba en mesa diferente | 10 ejecuciones |
| Cronometrar cada misión | Registrar tiempos |
| Calcular puntaje promedio | Tabla de resultados |

#### Semana 14: Preparación para competencia

| Actividad | Quién |
|-----------|-------|
| Ensayo de presentación ante jueces | Los 3 alumnos |
| Cada alumno explica una parte del robot | Alumno 1: mecánica, Alumno 2: electrónica, Alumno 3: software |
| Technical Summary escrito | Equipo (con guía de Claude) |
| Kit de herramientas + repuestos preparado | Equipo |
| Simulacro de competencia (3 rondas, timer) | Equipo |

---

## 3. Cómo integrar la IA visiblemente en el Technical Summary

### Lo que escribir en el Technical Summary de WRO

> "Nuestro equipo utilizó inteligencia artificial (Claude, de Anthropic) como herramienta de aprendizaje y asistencia de diseño durante todo el proceso de desarrollo del robot. La IA nos ayudó a:
>
> 1. **Aprender conceptos nuevos**: PID, sensor fusion, protocolos de comunicación I2C y TTL
> 2. **Diseñar el circuito electrónico**: el esquemático fue creado con asistencia de IA y verificado por el equipo
> 3. **Generar código parametrizado**: los archivos OpenSCAD de las piezas 3D fueron generados por IA y modificados por nosotros según las medidas reales
> 4. **Depurar problemas**: cuando el robot no funcionaba como esperábamos, le preguntábamos a la IA y ella nos guiaba en el diagnóstico
>
> Sin embargo, todas las decisiones de diseño, la construcción física, la calibración, la estrategia de misiones, y las horas de práctica fueron realizadas íntegramente por el equipo. La IA fue nuestro copiloto, no nuestro piloto."

### Por qué esto NO es trampa

Las reglas de WRO 2026 dicen:

> "The construction and coding of the robot may be done only by the team members. The task of the coach is to accompany the team organizationally and to support them in advance in case of questions or problems, but not to do the construction and coding."

La IA es una HERRAMIENTA, como un libro, un tutorial de YouTube, o un curso online. Los alumnos no le piden a Claude que construya el robot — le piden que les ENSEÑE cómo hacerlo. Después lo hacen ellos.

Análogamente: usar una calculadora en un examen de matemáticas no es trampa si el examen evalúa que entiendas el concepto, no que hagas aritmética mental. WRO evalúa que el equipo entienda y pueda explicar su robot, no que haya inventado cada concepto desde cero.

---

## 4. Lo que los alumnos habrán aprendido al final

### Habilidades técnicas

| Semana | Lo que aprenden | Nivel equivalente |
|--------|----------------|-------------------|
| 1-2 | Electricidad, programación básica, sensores | Secundaria técnica |
| 3-5 | PID, odometría, sensor fusion, navegación autónoma | 1er año ingeniería |
| 6-8 | Servos inteligentes, diseño 3D, detección de color, protocolos seriales | 2do año ingeniería |
| 9-11 | Diseño de PCB, fabricación industrial, firmware embebido | 3er-4to año ingeniería |
| 12-14 | Testing, robustez, presentación técnica, trabajo en equipo | Nivel profesional junior |

**En 14 semanas, alumnos de 13 años habrán tocado temas de 4 años de ingeniería.** No con la profundidad de un ingeniero, pero sí con la comprensión suficiente para HACER funcionar un robot de competencia y EXPLICAR cómo funciona.

### Habilidades blandas

- **Aprender a aprender con IA**: la habilidad más valiosa del siglo XXI
- **Formular buenas preguntas**: "el motor vibra" vs "el motor vibra cuando gira a más de 300 RPM con carga"
- **Iterar**: diseñar → probar → fallar → entender por qué → rediseñar
- **Documentar**: escribir qué hicieron y por qué, para que otros (y ellos mismos en el futuro) entiendan
- **Presentar**: explicar un sistema complejo a un juez en 5 minutos
- **Trabajar en equipo**: dividir responsabilidades, comunicar avances, resolver conflictos

### Lo que van a poder decir ante los jueces

**Juez:** "¿Cómo funciona el control PID de los motores?"

**Alumno:** "PID significa proporcional, integral, derivativo. Es como cuando ajustás la ducha: si el agua está muy fría, abrís mucho el caliente (proporcional). Si lleva rato fría, abrís un poco más (integral). Si el agua está calentándose rápido, abrís menos para no pasarte (derivativo). Nuestro robot hace lo mismo con la velocidad de las ruedas: mide cuántos pulsos del encoder llegan por segundo, compara con la velocidad que quiere, y ajusta el PWM del motor 1000 veces por segundo."

**Juez:** "¿Cómo sabe el robot que agarró la torre?"

**Alumno:** "El Dynamixel XL330 mide la corriente que consume. Cuando la garra se cierra en el aire, la corriente es baja. Cuando toca un objeto y aprieta, la corriente sube. Nosotros pusimos un umbral: si la corriente pasa de 200 miliamperes, es que agarró algo. Lo probamos con todos los objetos y calibramos el umbral."

**Juez:** "Usaron inteligencia artificial para diseñar el robot. ¿Eso no es trampa?"

**Alumno:** "La IA nos enseñó los conceptos y nos ayudó a generar el código base. Pero nosotros tomamos todas las decisiones: qué sensores usar, dónde ponerlos, cómo diseñar la garra, qué estrategia de misiones seguir. Además, nosotros armamos, soldamos, calibramos, y practicamos 200 horas. La IA no puede hacer nada de eso. Es como preguntarle a un profesor — el profesor te explica, pero el examen lo rendís vos."

---

## 5. El mensaje para el mundo

### Lo que IITA está demostrando

1. **La IA democratiza la ingeniería.** Un instituto en Salta, Argentina, puede competir con equipos de Corea, Alemania y Singapur porque la IA nivela el acceso al conocimiento.

2. **Los chicos no necesitan menos tecnología, necesitan más contexto.** Darle un ESP32 a un chico sin contexto es inútil. Darle un ESP32 + un copiloto IA que le explica cada paso es transformador.

3. **La transparencia genera respeto, no penalización.** Decir "usamos IA" en el Technical Summary no es una confesión — es una declaración de metodología innovadora. Los equipos que lo ocultan pierden la oportunidad de ser pioneros.

4. **El futuro de la educación STEM es humano + IA.** No IA reemplazando humanos. No humanos rechazando IA. Humanos amplificados por IA, haciendo cosas que ninguno podría hacer solo.

### La frase para el banner de IITA

> **"Construido por niños. Potenciado por IA. Explicado por ellos."**

---

## 6. Registro de aprendizaje: el "diario de viaje"

Cada alumno mantiene un cuaderno (físico o digital) donde anota:

### Formato de entrada diaria

```
Fecha: ___________

¿Qué aprendí hoy?
[explicar en sus propias palabras]

¿Qué le pregunté a la IA?
[copiar la pregunta exacta]

¿Qué entendí de la respuesta?
[explicar con sus palabras, NO copiar la respuesta]

¿Qué no entendí todavía?
[ser honesto — lo que no entendés hoy lo vas a entender mañana]

¿Qué hice con mis manos hoy?
[construir, soldar, medir, calibrar, programar, probar]
```

Este diario es la PRUEBA de que el aprendizaje fue real. Si un juez pregunta "¿cómo aprendieron PID?", el alumno abre el diario y muestra la entrada del día que lo aprendió, con SU explicación en SUS palabras.

---

## 7. División de roles en el equipo

### 3 alumnos, 3 especialidades

| Alumno | Especialidad | Qué domina | Qué presenta ante jueces |
|--------|-------------|-----------|-------------------------|
| **Alumno 1: "El Mecánico"** | Hardware + mecánica | Motores, garra, brazo, chasis, impresión 3D | "Cómo construimos el robot y por qué cada pieza está donde está" |
| **Alumno 2: "El Electrónico"** | Circuito + sensores | PCB, sensores, batería, cableado, soldadura | "Cómo funciona el circuito, qué mide cada sensor, cómo se alimenta" |
| **Alumno 3: "El Programador"** | Software + estrategia | Firmware, PID, navegación, misiones, calibración | "Cómo piensa el robot, cómo decide, cómo resuelve las misiones" |

Todos aprenden de todo (las sesiones son conjuntas), pero cada uno se ESPECIALIZA y puede explicar su área en profundidad. Esto es exactamente lo que hacen los equipos profesionales de ingeniería.

---

## 8. Evaluaciones semanales (el alumno se evalúa a sí mismo)

### Rúbrica de autoevaluación

Cada viernes, cada alumno se puntúa:

| Criterio | 1 (No) | 2 (Más o menos) | 3 (Sí) |
|----------|--------|-----------------|--------|
| ¿Puedo explicar lo que hicimos esta semana SIN mirar notas? | | | |
| ¿Si me preguntan "por qué", puedo dar una razón técnica? | | | |
| ¿Hice algo con mis manos (no solo miré)? | | | |
| ¿Le hice al menos 3 preguntas a la IA esta semana? | | | |
| ¿Entendí las respuestas de la IA o solo las copié? | | | |
| ¿Puedo enseñarle a un compañero lo que aprendí? | | | |

Si algún criterio es 1, el alumno identifica qué necesita y la próxima semana empieza por ahí.

---

## 9. Plan B: si el Nivel 3 no llega a tiempo

El documento `abogado-del-diablo-critica.md` queda como Plan B. Si en la semana 8 el robot custom no funciona confiablemente:

1. Volver a SPIKE Prime + BNO055 (Nivel 2)
2. Migrar la estrategia y el software de misiones (la lógica es la misma)
3. Los alumnos NO pierden lo aprendido — saben electrónica, PID, sensor fusion, diseño 3D
4. El aprendizaje vale más que el robot

> **Lo que importa no es ganar WRO. Lo que importa es que estos chicos salgan del proceso sabiendo cosas que el 99% de los adultos no sabe. Si además ganan, mejor. Pero el trofeo real es el conocimiento.**
