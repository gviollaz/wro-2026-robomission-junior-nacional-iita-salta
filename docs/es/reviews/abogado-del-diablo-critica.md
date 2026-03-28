# Abogado del Diablo — Análisis Crítico del Diseño IITA WRO Bot v1

## Premisa

> Este documento ataca sistemáticamente cada decisión de diseño del robot Nivel 3+. El objetivo es encontrar los puntos de falla ANTES de construir, no después. Si una crítica no tiene respuesta convincente, el diseño debe cambiar.

---

## 1. CRÍTICA FUNDAMENTAL: ¿Estamos sobrediseñando?

### El problema

Diseñamos un robot con Teensy 4.1 + ESP32-S3 + 3 Dynamixel + BNO055 + 2× VL53L5CX + 7 sensores de color + cámara + PCB custom + chasis aluminio. Es un robot de investigación universitaria, no un robot de competencia de chicos de 11-15 años.

**Los equipos que ganan el mundial de WRO Junior usan SPIKE Prime con LEGO.** No usan PCBs custom, no usan Dynamixel, no usan doble procesador. Ganan con EXCELENTE estrategia, MUCHA práctica, y un robot SIMPLE que funciona SIEMPRE.

### La pregunta incómoda

¿Estamos compensando falta de horas de práctica con complejidad de hardware? Porque si es así, estamos perdiendo. Un SPIKE Prime con 300 horas de práctica le gana a nuestro robot custom con 50 horas de práctica. Cada componente extra es un punto de falla extra.

### Veredicto

**Riesgo ALTO.** La complejidad del Nivel 3+ es injustificable para un equipo que compite por primera vez con hardware custom. La recomendación original de "Nivel 2 para nacional, Nivel 3 para mundial" era correcta. No debimos dejarnos llevar por la emoción técnica.

### Alternativa

Empezar con SPIKE Prime + BNO055 + piezas 3D (Nivel 2). Solo si el equipo demuestra que domina el juego con SPIKE y necesita más precisión, migrar a Nivel 3. NUNCA al revés.

---

## 2. CRÍTICA: Arquitectura dual (Teensy + ESP32) es innecesaria

### El problema

Propusimos dos procesadores "porque cada uno hace lo que mejor sabe". Pero esto introduce:

- **Protocolo de comunicación inter-MCU**: hay que diseñar, implementar, y debuggear un protocolo UART entre Teensy y ESP32. Si hay un bug en este protocolo, el robot entero falla.
- **Sincronización temporal**: el Teensy necesita datos de sensores del ESP32 con baja latencia. Si el ESP32 tarda 5ms en responder, el PID de navegación usa datos viejos.
- **Dos cadenas de compilación**: firmware en Arduino (Teensy) + firmware en Arduino/MicroPython (ESP32). Dos IDEs, dos procesos de upload, dos fuentes de bugs.
- **Duplicación de hardware**: dos reguladores 3.3V, dos conectores USB, dos bootloaders.

### La pregunta incómoda

¿El ESP32-S3 solo no puede hacer todo? Con PID a 1kHz en un core y sensores en el otro, probablemente sí. La latencia de ISR del ESP32-S3 es ~2µs, suficiente para encoders de 358 CPR a 500 RPM (un pulso cada 5.6ms). No necesitamos los 0.1µs del Teensy.

### Veredicto

**Riesgo MEDIO-ALTO.** La arquitectura dual agrega complejidad sin beneficio proporcional. Un ESP32-S3 solo hace el 95% del trabajo.

### Alternativa

**Un solo ESP32-S3-N16R8** (16MB flash, 8MB PSRAM):
- Core 0: PID motores a 1kHz + encoders via PCNT + Dynamixel TTL
- Core 1: BNO055 + VL53L5CX + color array + cámara + lógica de misión
- WiFi para debug (se desactiva en competencia)
- Un solo firmware, un solo IDE, un solo upload

Si en testing el ESP32-S3 no puede con todo (que lo dudo), ENTONCES agregar el Teensy. No antes.

---

## 3. CRÍTICA: Los Dynamixel XL330 son overkill para este robot

### El problema

Los Dynamixel XL330 cuestan $24 cada uno (×3 = $72, el 22% del presupuesto total). ¿Qué hacen que un servo MG90S de $5 no pueda hacer?

- **Control de posición**: un MG90S con feedback de posición (FS90R con potenciómetro) da posición con ±2° de precisión. ¿Necesitamos los ±0.088° del Dynamixel?
- **Control de corriente**: sí, la detección de contacto por corriente es útil para el apilado de torres. Pero se puede lograr con un sensor de corriente INA219 ($3) en serie con un MG90S.
- **Daisy-chain**: ahorramos cables pero agregamos complejidad de protocolo (Dynamixel SDK).

### La pregunta incómoda

El apilado de torres depende de la **precisión de posicionamiento del robot** (odometría + gyro), no de la precisión del servo. Si el robot llega ±5mm desviado a la torre, la resolución de 0.088° del Dynamixel no sirve de nada. Lo que importa es que el robot esté en el lugar correcto, no que el servo sea ultra preciso.

### Veredicto

**Riesgo MEDIO.** Los Dynamixel son superiores pero su costo y complejidad de integración pueden no justificarse. Un equipo principiante va a sufrir más con el protocolo Dynamixel que con la mecánica del apilado.

### Alternativa A (más barata)

3× MG996R ($5/u = $15 total) + 1× INA219 para detección de corriente en la garra ($3). Total: $18 en vez de $72. Ahorro: $54 que se pueden invertir en más horas de práctica (comprando tapetes extra o piezas de repuesto).

### Alternativa B (compromiso)

1× Dynamixel XL330 solo para la garra (donde la detección de corriente realmente importa) + 2× servos genéricos para brazo y pala. Total: $34 en vez de $72.

---

## 4. CRÍTICA: 7 sensores de color en el piso son excesivos

### El problema

Propusimos 7× VEML6040 con un TCA9548A multiplexor. Esto agrega:
- 8 componentes extra (7 sensores + 1 mux)
- Complejidad de PCB (ruteo de 7 sensores en la cara inferior)
- Complejidad de firmware (secuencia de lectura multiplexada)
- Puntos de falla (un sensor que falla afecta la detección)
- Costo: ~$16 extra

### La pregunta incómoda

¿En qué momento de Heritage Heroes 2026 necesitamos detectar líneas con 7 sensores? Las misiones son:
1. Visitantes → los llevamos a zonas de COLOR, no a líneas
2. Torres → posiciones CONOCIDAS, navegamos por odometría
3. Artefactos → detectar color del OBJETO, no del piso
4. Suciedad → barrer ciego, no necesita sensores de piso
5. Bonus → no tocar cosas, no necesita sensores

El único uso real sería detectar los bordes de las zonas de color del tapete. Pero con BNO055 + encoders de alta resolución, la odometría es suficiente para navegar a coordenadas conocidas. No es un robot seguidor de líneas; es un robot de navegación autónoma.

### Veredicto

**Riesgo MEDIO.** Los 7 sensores de color agregan más complejidad que valor para ESTE juego. En un juego con mucho seguimiento de línea serían imprescindibles.

### Alternativa

**2 sensores de color** (uno frontal para detectar zonas del tapete, uno en la garra para leer artefactos). Total: 2× TCS34725 = $16 (igual precio, mucho menos complejidad). Si necesitamos detección de línea básica, 2 sensores alcanzan para un PID de seguimiento.

---

## 5. CRÍTICA: 2× VL53L5CX (64 zonas cada uno) son excesivos

### El problema

Cada VL53L5CX cuesta ~$20 y requiere mucha RAM para procesar (la librería usa ~30KB). ¿Necesitamos realmente 128 puntos de profundidad?

### La pregunta incómoda

¿Qué información de los 128 puntos usa realmente el robot? En Heritage Heroes:
- "¿Hay un objeto adelante?" → 1 punto de distancia alcanza (VL53L1X a $12)
- "¿A qué distancia está la pared?" → 1 punto
- "¿Dónde está la torre para apilar?" → tal vez 4×4 zonas alcanzan

### Veredicto

**Riesgo BAJO-MEDIO.** Los VL53L5CX son increíbles pero probablemente subutilizados. Un VL53L5CX adelante (para buscar objetos) + un VL53L1X atrás (para distancia a pared) sería suficiente y $8 más barato.

### Alternativa

1× VL53L5CX frontal ($20) + 1× VL53L1X trasero ($12) = $32 (vs $40 por 2× VL53L5CX). Misma funcionalidad práctica.

---

## 6. CRÍTICA: El chasis de aluminio CNC es frágil ante cambios

### El problema

Una placa de aluminio cortada con láser es rígida y precisa. Pero si cambiamos la posición de UN motor o UN sensor, hay que pedir OTRA placa. Con PLA, reimprimir lleva 1 hora. Con aluminio, pedir, esperar 10-15 días, pagar de nuevo.

### La pregunta incómoda

¿Cuántas veces vamos a cambiar el diseño mecánico durante la temporada? Si la respuesta es "más de 2 veces", el aluminio es un problema.

### Veredicto

**Riesgo ALTO para etapa de prototipado, BAJO para versión final.** No pedir aluminio hasta que el diseño esté congelado.

### Alternativa

1. Prototipar TODO en PLA+ de 3mm (barato, rápido, iterable)
2. Solo cuando el diseño lleve 2+ semanas sin cambios, pedir la versión en aluminio
3. La versión aluminio es para la competencia, no para desarrollo

---

## 7. CRÍTICA: La garra tipo V puede fallar con objetos irregulares

### El problema

La garra en V funciona bien con objetos simétricos (cubos, cilindros). Pero los objetos WRO son LEGO irregulares con studs, esquinas, y partes que sobresalen. Un stud que se traba en el labio de la V puede impedir que el objeto se centre.

### La pregunta incómoda

¿Probamos la garra con los objetos REALES o solo con la teoría? Porque en LEGO, los studs sobresalen 1.8mm y tienen diámetro 4.8mm. Un dedo de garra que roza un stud puede mover el objeto en vez de centrarlo.

### Veredicto

**Riesgo ALTO.** NUNCA diseñar la garra sin tener los objetos reales en la mano. La geometría teórica en V es bonita pero los detalles del LEGO la pueden arruinar.

### Alternativa

Diseñar 3 garras diferentes e imprimir las 3. Probar cada una con los 8 tipos de objetos (visitante, torre roja, torre amarilla base, torre amarilla techo, artefacto ×5). La que funcione 9/10 veces con TODOS los objetos es la ganadora. Esto cuesta $3 de filamento y un sábado de pruebas. Es la inversión más valiosa de todo el proyecto.

---

## 8. CRÍTICA: El firmware FreeRTOS dual-core es complejo para un equipo escolar

### El problema

Propusimos un firmware con FreeRTOS, tareas en cores separados, comunicación por queues, mutexes para variables compartidas. Esto es ingeniería de software embebido de nivel universitario.

### La pregunta incómoda

¿Quién programa esto? Si es Gustavo (el coach), los alumnos no van a entender el código. En WRO, los jueces preguntan a los ALUMNOS cómo funciona el robot. Si los alumnos no pueden explicar el firmware, pierden puntos en el Technical Summary y pueden ser descalificados.

### Veredicto

**Riesgo MUY ALTO.** Este es probablemente el riesgo más grande de todo el diseño. Un robot que los alumnos no entienden es un robot que no debería existir en WRO.

### Alternativa

**Arduino loop() simple** con máquina de estados:
```cpp
void loop() {
    leer_sensores();      // ~2ms
    actualizar_pid();     // ~0.5ms
    ejecutar_mision();    // ~1ms
    // Total: ~3.5ms → 285Hz (más que suficiente)
}
```

Sin FreeRTOS, sin tareas, sin cores separados. Un solo loop que los alumnos pueden seguir línea por línea. La frecuencia de 285Hz es suficiente para PID de motores N20 con encoder de 358 CPR.

Solo usar FreeRTOS si el loop simple NO alcanza (que es improbable para este robot).

---

## 9. CRÍTICA: No tenemos tapete ni objetos reales

### El problema

Diseñamos un robot para un juego que no practicamos en condiciones reales. No tenemos:
- Tapete oficial WRO 2026 (o impresión a escala real)
- Objetos de juego armados y medidos
- Mesa con railing de 5cm
- Experiencia de cómo se comportan los objetos al empujar/agarrar

### La pregunta incómoda

¿De qué sirve un robot de $330 con 128 sensores ToF si no sabemos cómo se comporta una torre LEGO cuando un servo la empuja? La respuesta a esa pregunta solo viene de PROBAR CON EL OBJETO REAL.

### Veredicto

**Riesgo CRÍTICO.** Este es el error #1 de los equipos novatos: invertir en hardware antes de invertir en práctica. El tapete cuesta ~$30 (impresión en lona) y los objetos se arman con el brick set (~$40). Total $70 que tienen 10× más impacto que $70 en sensores.

### Alternativa

**Primer gasto: tapete + brick set. Segundo gasto: hardware del robot.** No al revés.

---

## 10. CRÍTICA: OpenSCAD no es el mejor CAD para un equipo educativo

### El problema

OpenSCAD es CAD por código. Es poderoso pero NO visual. Los alumnos de 11-15 años necesitan ver y manipular el diseño en 3D, no escribir código.

### La pregunta incómoda

¿Los alumnos van a poder modificar el diseño de la garra si necesitan cambiar algo en competencia? Con OpenSCAD necesitan entender el código. Con Onshape o Tinkercad, mueven un cubo con el mouse.

### Veredicto

**Riesgo MEDIO.** OpenSCAD es ideal para Claude (genero código) pero no para los alumnos (necesitan interfaz visual).

### Alternativa

**Workflow híbrido:**
1. Claude genera .scad como punto de partida
2. Se exporta como .step (vía FreeCAD)
3. Se importa en **Onshape** (gratis, cloud, visual)
4. Los alumnos pueden modificar visualmente en Onshape
5. Se exporta como .stl para imprimir

O directamente: Claude describe las dimensiones y los alumnos modelan en Onshape desde cero. Esto es más lento pero los alumnos APRENDEN CAD, que es parte del objetivo educativo de WRO.

---

## 11. CRÍTICA: No consideramos el factor humano de competencia

### El problema

En competencia, el equipo tiene:
- Manos que tiemblan (nervios)
- 3 minutos de check-time (no 30 minutos)
- Mesa diferente a la de práctica
- Luz diferente a la de práctica
- Un robot que quizás no funcionó en la ronda anterior

### La pregunta incómoda

¿Nuestro robot con 2 procesadores, 3 Dynamixel, y PCB custom se puede diagnosticar y reparar en 3 minutos? Si un cable JST se desconecta, ¿el equipo sabe cuál de los 15 cables es?

### Veredicto

**Riesgo ALTO.** Un SPIKE Prime tiene 6 cables (A-F) y los alumnos saben identificar cada uno por color. Nuestro robot custom tiene 15+ cables y los alumnos necesitan un diagrama para saber cuál es cuál.

### Alternativa

- **Etiquetar CADA cable** con un número y color
- **Diagrama de cableado plastificado** pegado en la caja del robot
- **LED de diagnóstico**: al encender, el robot verifica cada sensor/motor y enciende un LED verde por cada uno que funciona, rojo por cada fallo
- **Conectores con llave** (JST con pestaña) para que no se puedan conectar al revés

---

## 12. RESUMEN: Ranking de riesgos

| # | Riesgo | Nivel | Impacto si falla |
|---|--------|-------|-----------------|
| 1 | No tener tapete ni objetos reales | **CRÍTICO** | Todo el diseño es teórico |
| 2 | Firmware complejo que alumnos no entienden | **MUY ALTO** | Descalificación potencial |
| 3 | Sobrediseño (Nivel 3+ cuando Nivel 2 alcanza) | **ALTO** | Meses de desarrollo perdidos |
| 4 | Garra no probada con objetos reales | **ALTO** | 0 puntos en misiones de agarre |
| 5 | Aluminio no iterable en prototipado | **ALTO** | Semanas perdidas esperando piezas |
| 6 | Diagnóstico imposible en competencia | **ALTO** | Robot roto sin poder reparar |
| 7 | Arquitectura dual innecesaria | **MEDIO-ALTO** | Bugs de comunicación |
| 8 | Dynamixel overkill para este juego | **MEDIO** | Presupuesto mal asignado |
| 9 | 7 sensores color innecesarios | **MEDIO** | Complejidad sin beneficio |
| 10 | OpenSCAD inaccesible para alumnos | **MEDIO** | Alumnos no pueden modificar |
| 11 | VL53L5CX subutilizados | **BAJO-MEDIO** | $8 desperdiciados |

---

## 13. EL DISEÑO CORREGIDO: Qué cambiaría

### Prioridad 0: ANTES de cualquier hardware

1. Comprar/imprimir tapete WRO 2026 ($30-50)
2. Armar objetos con brick set ($40)
3. Medir todos los objetos con calibre
4. Practicar misiones A MANO (mover objetos para entender el juego)

### Prioridad 1: Robot Nivel 2 funcional (semana 1-4)

SPIKE Prime + BNO055 via LMS-ESP32 + garra 3D impresa. Este robot FUNCIONA para el nacional. Practicar 100+ horas con él.

### Prioridad 2: Evaluar si Nivel 3 vale la pena (semana 5-6)

Si el SPIKE llega a 200+ puntos consistentes y el equipo identifica que la precisión mecánica es el limitante (no la estrategia ni la práctica), ENTONCES considerar Nivel 3.

### Prioridad 3: Nivel 3 simplificado (semana 7-12)

Si se decide ir a Nivel 3, usar la versión simplificada:
- **1× ESP32-S3** (no dual con Teensy)
- **2× Pololu 30:1 HPCB** + **1× DRV8833**
- **1× Dynamixel XL330** (solo garra) + **2× MG996R** (brazo + pala)
- **1× BNO055** + **1× VL53L5CX** + **1× TCS34725**
- **Chasis PLA** (no aluminio, hasta versión final)
- **Arduino loop()** simple (no FreeRTOS)
- **Costo total: ~$180** (vs $330 del diseño original)

Esta versión tiene el 80% del rendimiento con el 50% de la complejidad y el 55% del costo.

---

## 14. LA LECCIÓN

> El mejor robot de WRO no es el que tiene la mejor electrónica. Es el que tiene el mejor equilibrio entre hardware suficiente, software entendido por los alumnos, y cientos de horas de práctica en el tapete real.

> Diseñar un robot de competencia es un ejercicio de RESTRICCIÓN, no de maximización. Cada componente que agregás tiene que justificar su existencia con puntos de competencia reales, no con elegancia técnica.

> Si un componente no suma directamente al menos 10 puntos de competencia con >80% de confiabilidad, no va en el robot.
