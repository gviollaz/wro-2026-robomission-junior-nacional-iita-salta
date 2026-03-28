# Diseño físico del robot para WRO RoboMission

## Objetivo

Este documento resume mejores prácticas de **construcción física** para un robot de WRO RoboMission, adaptadas al contexto de este repo:

- plataforma actual: **LEGO SPIKE Prime + Pybricks**,
- arquitectura esperada: **robot diferencial** de dos ruedas motrices,
- categoría objetivo: **RoboMission Junior 2026**.

La meta no es construir “el robot más impresionante”, sino un robot que haga esto:

1. **salga siempre igual**,
2. **gire siempre parecido**,
3. **tolere pequeños errores del tablero**,
4. **no se deforme cuando toca pared o empuja objetos**,
5. **sea fácil de calibrar y reparar**.

La idea central es muy simple:

> **En RoboMission, la repetibilidad vale más que la complejidad.**

---

## 1. Punto de partida: qué robot conviene construir

Para este repo y este tipo de juego, la arquitectura más razonable suele ser:

- **2 ruedas motrices**,
- **1 apoyo pasivo** adicional (caster, patín o apoyo de seguridad),
- chasis **compacto y rígido**,
- caras frontal y lateral **planas** para usar como referencia contra pared,
- accesorios simples para capturar, levantar y depositar objetos.

¿Por qué?

Porque Pybricks está muy bien preparado para una `DriveBase` de dos ruedas motrices y un apoyo pasivo, y porque esa arquitectura suele dar una buena combinación entre:

- simplicidad mecánica,
- facilidad de calibración,
- espacio para accesorios,
- precisión suficiente para nivel nacional e incluso internacional si está bien trabajada.

---

## 2. Antes de elegir piezas: pensar la estrategia del tablero

La construcción física no se diseña en el vacío. Primero hay que responder:

- ¿el robot va a priorizar velocidad o robustez?
- ¿necesita empujar, levantar, agarrar o barrer?
- ¿necesita pasar por zonas angostas?
- ¿va a usar pared, líneas o color como referencias?
- ¿necesita leer color en el piso, en objetos, o ambas cosas?

### Regla de diseño muy útil
No empezar por el brazo o la garra.

Empezar por:
1. **base de tracción**,
2. **estabilidad**,
3. **sensores**,
4. recién después **mecanismos de misión**.

Muchos equipos pierden tiempo diseñando un accesorio brillante sobre una base que todavía no va recta.

---

## 3. Elección del tren de tracción

## 3.1. 2 ruedas motrices + apoyo pasivo

### Ventajas
- más fácil de modelar y programar,
- muy compatible con `DriveBase` de Pybricks,
- menor complejidad mecánica,
- menos rozamiento lateral que una base con demasiadas ruedas fijas,
- más espacio para mecanismos.

### Desventajas
- necesita cuidar bien el apoyo pasivo,
- si el peso queda mal distribuido, una rueda puede perder tracción,
- puede volverse inestable si el accesorio delantero es muy pesado.

### Recomendación
Para este repo, esta debería ser la **opción por defecto**.

## 3.2. 4 ruedas en contacto con el piso

Puede parecer “más estable”, pero no siempre conviene.

### Ventajas
- más apoyo total,
- puede dar sensación de robot más firme.

### Desventajas
- más fricción,
- más riesgo de rozamiento desigual,
- más posibilidades de que una rueda cargue diferente que otra,
- más error al girar si no está muy bien construida.

En un robot diferencial, el deslizamiento de ruedas perjudica la precisión de trayectoria. Por eso, agregar apoyos o fricción sin una razón clara puede empeorar la repetibilidad.

### Recomendación
No usar 4 ruedas apoyadas “porque sí”. Solo vale la pena si una misión concreta realmente lo exige y si el equipo sabe controlar bien el rozamiento extra.

---

## 4. Selección de ruedas

## 4.1. Diámetro de rueda

El diámetro de rueda cambia mucho el carácter del robot.

### Ruedas más grandes
**Ventajas**
- más distancia recorrida por vuelta,
- mayor velocidad lineal para el mismo giro del motor,
- pasan mejor pequeñas irregularidades o bordes.

**Desventajas**
- menos ventaja mecánica en la rueda,
- menor “fuerza útil” en el contacto con el piso para el mismo torque del motor,
- más sensibilidad a errores pequeños de calibración,
- el robot suele quedar más alto.

### Ruedas más chicas
**Ventajas**
- más torque útil en el contacto con el piso,
- mejor control fino en maniobras lentas,
- centro de gravedad más bajo,
- robot más compacto.

**Desventajas**
- menos velocidad lineal,
- menos despeje,
- pueden sufrir más cuando el robot tiene que empujar fuerte y recorrer distancias largas rápidamente.

### Recomendación práctica
Para un robot tipo SPIKE/Pybricks de RoboMission, una rueda **intermedia** suele ser el mejor compromiso. En este repo ya aparece una configuración base con **56 mm** de diámetro, y eso es una base razonable para empezar y comparar contra otras opciones.

### Regla simple para alumnos
- si el robot es torpe, pesado o empuja mucho: probar más chico,
- si el robot ya es estable y falta velocidad: probar más grande,
- si no hay una razón fuerte: quedarse en un tamaño medio.

## 4.2. Ancho y agarre de la rueda

No solo importa el diámetro. También importa cuánto agarra la rueda.

### Mucho agarre
**Ventajas**
- mejor salida,
- menos patinaje al empujar,
- mejor tracción en rectas.

**Desventajas**
- puede hacer más bruscos algunos giros,
- si hay mala distribución de peso, el robot puede desviarse más,
- una rueda muy “agarrada” y otra no tanto generan comportamiento desigual.

### Poco agarre
**Ventajas**
- giros más suaves,
- menos tendencia a “pelearse” con el piso.

**Desventajas**
- más patinaje,
- peor empuje,
- peor repetibilidad en aceleraciones.

### Recomendación
- usar **el mismo tipo de neumático** a ambos lados,
- revisar desgaste,
- evitar combinaciones improvisadas de ruedas distintas,
- probar siempre con la carga real del robot.

---

## 5. Separación entre ruedas y huella del robot

En Pybricks, `axle_track` es la distancia entre los puntos donde las ruedas tocan el suelo. Ese valor importa tanto para programar como para diseñar.

## 5.1. Robot angosto
**Ventajas**
- compacto,
- gira rápido,
- cabe mejor entre elementos,
- deja más espacio para accesorios laterales.

**Desventajas**
- menos estabilidad lateral,
- más riesgo de inclinación si el brazo sube mucho o lleva peso arriba,
- peor comportamiento si toca paredes con un frente largo.

## 5.2. Robot más ancho
**Ventajas**
- más estable lateralmente,
- mejor plataforma para brazo y accesorios,
- más fácil apoyar una cara plana contra pared.

**Desventajas**
- ocupa más espacio,
- puede limitar el paso por zonas ajustadas,
- puede exigir más trabajo de calibración si el diseño genera rozamientos extra.

### Recomendación
Buscar un ancho **moderado**:
- lo bastante ancho para ser estable,
- lo bastante compacto para no sufrir con la caja de inicio ni con el campo.

No diseñar “al límite” del tamaño permitido si no hace falta.

---

## 6. Centro de gravedad y distribución del peso

Un robot que se ve firme en la mesa puede comportarse mal en el tablero si el peso está mal puesto.

## 6.1. Bajar el centro de gravedad
Un centro de gravedad bajo ayuda a que el robot sea más estable.

### Cómo lograrlo
- hub lo más bajo posible,
- motores grandes cerca del plano principal del chasis,
- evitar estructuras altas decorativas o innecesarias,
- no poner masa arriba si no aporta función,
- usar brazos livianos y rígidos.

### Por qué importa
Si el centro de gravedad sube:
- el robot cabecea más al arrancar y frenar,
- el sensor de piso cambia de altura,
- un brazo levantado cambia mucho la estabilidad,
- el robot es más sensible a choques.

## 6.2. Repartir bien el peso sobre las ruedas motrices
El robot debe tener suficiente peso sobre las ruedas que empujan.

### Demasiado poco peso en ruedas motrices
- patina,
- deriva,
- falla al empujar,
- pierde precisión.

### Demasiado peso mal localizado
- aumenta fricción en apoyos no motrices,
- el robot se vuelve pesado de mover,
- los giros pierden limpieza.

### Recomendación práctica
Buscar que el peso esté:
- **centrado izquierda-derecha**,
- levemente favoreciendo la tracción de las ruedas motrices,
- sin sobrecargar en exceso el frente o la cola.

### Prueba útil
Levantar apenas una punta del robot y sentir:
- si una rueda parece “flotar”, hay mala distribución;
- si el frente se clava demasiado, el accesorio delantero pesa mucho;
- si la cola cae demasiado, el apoyo pasivo está cargando de más.

---

## 7. Robot liviano, pero no frágil

“Liviano” no significa “débil”.

El objetivo correcto es:

> **quitar peso donde no aporta rigidez ni función**

### Dónde sí conviene invertir piezas
- unión entre hub y chasis,
- soporte de motores de tracción,
- ejes con engranajes,
- soporte de sensores,
- base de mecanismos que empujan o levantan.

### Dónde conviene ahorrar piezas
- torres estéticas,
- decoraciones,
- vigas largas sin función,
- capas dobles innecesarias,
- carenados que solo ocupan espacio.

### Regla simple
- piezas cerca de la transmisión: calidad estructural,
- piezas lejos de la transmisión: simplificar,
- piezas altas: revisar dos veces si de verdad hacen falta.

---

## 8. Cómo construir rigidez sin hacer un “tanque”

## 8.1. Cerrar marcos
Un cuadro cerrado es más rígido que una tira larga de vigas.

### Buenas prácticas
- usar marcos o rectángulos cerrados alrededor de la base,
- unir ambos lados del chasis con travesaños,
- evitar ejes largos sostenidos solo de un lado,
- apoyar engranajes y poleas con estructura cercana.

## 8.2. Dar dos apoyos a ejes y engranajes
Cuando un eje transmite fuerza, conviene que tenga soporte a ambos lados o lo más cerca posible del engranaje.

### Si no se hace
- el eje flexa,
- el engranaje se separa,
- aparece ruido, salto o pérdida de precisión.

## 8.3. Evitar voladizos largos
Todo brazo largo sin apoyo extra:
- flexa,
- vibra,
- cambia la geometría real del robot,
- hace menos precisa la colocación de objetos.

### Recomendación
Si una pieza se extiende mucho hacia adelante:
- usar guías laterales,
- reforzar la base,
- reducir peso en la punta,
- considerar apoyo pasivo o patín de seguridad si el brazo genera cabeceo.

---

## 9. Apoyos pasivos: caster, patines y piezas que casi rozan la lona

Pybricks contempla de manera natural una base con dos ruedas motrices y **un apoyo pasivo**.

## 9.1. Ball caster o rueda loca
### Ventajas
- simple,
- muy usado,
- fácil de integrar,
- baja exigencia de programación.

### Desventajas
- puede ensuciarse,
- puede vibrar o “titubear” si está mal montado,
- si carga demasiado peso, introduce fricción no deseada.

LEGO incluso recomienda limpiar el ball caster periódicamente.

## 9.2. Patines o deslizadores
A veces conviene usar una pieza lisa o un pequeño apoyo de bajo rozamiento.

### Ventajas
- muy bajos,
- simples,
- pueden servir como “tope de seguridad” para que el robot no vuelque o no incline demasiado al frenar.

### Desventajas
- agregan fricción si apoyan demasiado,
- pueden afectar giros,
- si están mal simétricos, el robot deriva.

## 9.3. Piezas que casi rozan la lona
Esto puede ser muy útil si se hace bien.

### Cuándo convienen
- cuando el robot levanta objetos y cambia mucho la carga,
- cuando el brazo delantero tiende a hacer cabecear el robot,
- cuando se quiere limitar la inclinación sin convertir ese apoyo en la carga principal.

### Cómo conviene usarlas
- que estén **muy cerca** del piso, pero no cargando peso grande todo el tiempo,
- usar superficies lisas,
- colocarlas simétricamente cuando sea posible,
- verificarlas en aceleración, frenado y giros.

### Riesgo
Si apoyan demasiado:
- aumentan fricción,
- el robot deja de girar igual,
- cambian las calibraciones.

### Conclusión práctica
Los apoyos “casi tocando” son buenos como **seguro anti-balanceo**, no como sustituto de un chasis bien equilibrado.

---

## 10. Ubicación del hub y de los motores

## 10.1. Hub
El hub concentra batería, puertos e IMU.

### Recomendación
- montarlo **centrado y bajo**,
- proteger el botón de inicio/parada para que sea accesible,
- dejar cables ordenados y cortos,
- fijarlo de manera rígida para que la IMU siempre tenga la misma orientación física.

## 10.2. Motores de tracción
Conviene que estén bien integrados al chasis principal.

### Recomendación
- estructura rígida alrededor de cada motor,
- sin torsión en el soporte,
- ejes cortos y bien apoyados,
- simetría izquierda/derecha.

## 10.3. Motores de mecanismos
Hay que ubicarlos según la función, pero con una regla general:

> **si el motor puede ir cerca de la carga, mejor**

¿Por qué?
Porque así se evitan transmisiones largas, flexibles y con juego.

Solo alejar el motor cuando haya una razón clara de empaquetado o balance.

---

## 11. Sensores: dónde conviene ponerlos

## 11.1. Sensor de color/reflexión para el piso

Este sensor es crítico si se usa para:
- seguir líneas,
- detectar bordes,
- encontrar marcas,
- corregir posición en el piso.

LEGO indica que el sensor de color puede leer color alrededor de **16 mm ± 8 mm** con distinta confianza según el color, y que para luz reflejada recomienda **8–16 mm** para mejores resultados.

### Recomendación de montaje
- rígido,
- sin vibración,
- siempre a la misma altura,
- idealmente protegido de luz lateral,
- con una geometría sencilla de medir y reproducir.

### Dónde ubicarlo
#### Opción A - un poco adelante del eje motriz
Es la opción más común.

**Ventajas**
- “ve” la línea antes de que el centro del robot la sobrepase,
- útil para buscar marcas y luego frenar.

**Desventajas**
- requiere compensar el offset geométrico,
- si el robot cabecea, cambia la altura del sensor.

#### Opción B - más cerca del centro geométrico
**Ventajas**
- más coherente con la posición real del robot,
- menos sensibilidad a algunas oscilaciones.

**Desventajas**
- puede ver la línea tarde para ciertas maniobras rápidas.

### Recomendación general
Para este tipo de robot, suele convenir un sensor de piso:
- cerca del eje longitudinal del robot,
- ligeramente adelantado respecto a la referencia principal,
- con soporte muy rígido,
- y calibrado a la altura real final del robot.

## 11.2. Sensor de color para detectar objetos
Leer un objeto no es lo mismo que leer el piso.

### Regla clave
El color del objeto debe leerse en una geometría controlada:
- misma distancia,
- mismo ángulo,
- misma iluminación,
- mismo fondo, en lo posible.

### Dónde conviene ponerlo
- en una “ventana” o túnel de lectura,
- en una entrada de objeto guiada,
- en un mecanismo donde el objeto siempre se presenta igual.

### Mejor práctica
Si el presupuesto de puertos y piezas lo permite, separar funciones:
- **un sensor optimizado para piso**,
- **otro sensor o posición dedicada para objetos**.

### Si solo hay un sensor
Entonces el diseño mecánico debe decidir qué función es más crítica:
- navegación por piso,
- o clasificación de objetos.

En ese caso, conviene diseñar una rutina o soporte que acerque el objeto al sensor de forma repetible.

## 11.3. Sensor ultrasónico: ¿sí o no?

El sensor ultrasónico puede medir distancia y también detectar presencia de otras señales ultrasónicas. Pero LEGO advierte que a veces hay interferencias por otros sensores u objetos dentro de su campo de visión. Pybricks además indica que, si no hay lectura válida, puede devolver **2000 mm**.

### Ventajas del ultrasónico
- permite detectar objetos o paredes sin tocar,
- útil para aproximaciones gruesas,
- puede ayudar en presencia/ausencia,
- sirve como sensor secundario cuando no conviene chocar o cuando el objeto está adelantado.

### Desventajas
- menos confiable que una buena referencia por pared para alineación final,
- sensible a la geometría del objeto,
- puede sufrir interferencias,
- no siempre da la misma lectura en superficies anguladas o poco favorables,
- ocupa espacio frontal valioso.

### Recomendación realista
Usarlo como:
- ayuda para aproximación,
- filtro de presencia,
- medición gruesa.

No usarlo como única referencia de precisión final si hay una pared, línea o tope mecánico mejor.

---

## 12. Diseño de caras de referencia

Un robot competitivo no solo “se mueve”. También **se apoya bien**.

### Qué conviene tener
- una cara frontal recta,
- una cara lateral útil,
- esquinas que no se enganchen,
- piezas resistentes al toque repetido.

### Para qué sirve
- alinearse con paredes,
- corregir ángulo,
- usar toques suaves repetibles,
- posicionarse antes de depositar.

### Error común
Hacer un frente lleno de puntas, garras y piezas asimétricas.

Eso complica la alineación física.

### Mejor idea
Tener una “cara de trabajo” limpia y predecible, incluso si luego los mecanismos salen desde esa base.

---

## 13. Mecanismos: levantar, sujetar, empujar y barrer

## 13.1. Mecanismos de empuje
Son los más simples y, muchas veces, los más confiables.

### Ventajas
- robustos,
- rápidos,
- toleran variaciones pequeñas,
- fáciles de calibrar.

### Desventajas
- no sirven para todo,
- pueden mover más de un objeto si la geometría no está bien controlada.

### Cuándo convienen
- partículas,
- elementos livianos,
- objetos que solo hay que reubicar, no levantar.

## 13.2. Mecanismos de sujeción
Se usan cuando hay que agarrar un objeto y evitar que se escape.

### Buenas prácticas
- usar embudos o guías para autocentrado,
- diseñar una “boca” generosa para capturar,
- usar topes mecánicos para que la posición cerrada sea siempre la misma,
- evitar dedos demasiado largos y flexibles.

## 13.3. Mecanismos de elevación
Cuando hay que subir piezas, la rigidez importa mucho.

### Buenas prácticas
- brazo corto si es posible,
- centro de masa del accesorio cerca de la base,
- topes mecánicos repetibles,
- revisar que al subir no cambie mucho la estabilidad del robot.

### Regla útil
Siempre que sea posible, la precisión final debería depender más de:
- **topes mecánicos**,
- **guías**,
- **geometría pasiva**,

que de “caer justo” solo por software.

---

## 14. Transmisión de movimiento: directa, engranajes, cadenas y cardanes

## 14.1. Transmisión directa
### Ventajas
- simple,
- poca pérdida,
- menos juego,
- más fácil de mantener.

### Desventajas
- menos libertad de ubicación del motor,
- a veces no entra bien en el empaque.

### Recomendación
Siempre que se pueda, es la opción preferida.

## 14.2. Engrananajes
Pybricks permite incluso declarar trenes de engranajes al inicializar motores, lo que ayuda a reflejar correctamente la relación entre el motor y la salida.

### Ventajas
- precisos,
- compactos,
- ideales para relaciones de velocidad/torque,
- buenos para mecanismos que necesitan repetibilidad angular.

### Desventajas
- piden buen alineado,
- si el eje está mal soportado, hacen ruido y pierden eficiencia,
- pueden agregar juego si el armado es flojo.

### Cuándo convienen
- garras,
- elevadores,
- selectores,
- mecanismos sincronizados.

## 14.3. Cadenas
### Ventajas
- permiten llevar movimiento a otra zona del robot,
- útiles cuando el motor no entra donde está la herramienta,
- toleran mejor algunos recorridos largos que una cascada de engranajes.

### Desventajas
- más juego que una transmisión corta por engranajes,
- exigen tensión adecuada,
- pueden perder precisión si el mecanismo necesita posicionamiento angular muy fino.

### Cuándo convienen
- barridos,
- mecanismos largos,
- cuando hay que rodear obstáculos del chasis.

## 14.4. Cardanes o juntas universales
### Ventajas
- dejan transmitir movimiento entre ejes que no están perfectamente alineados,
- sirven cuando una articulación o la geometría del chasis obliga a cambiar ángulo.

### Desventajas
- agregan juego y fricción,
- a ángulos altos empeoran la regularidad,
- no son la primera opción si se puede resolver con engranajes bien alineados.

### Cuándo convienen
- cuando el empaque obliga,
- cuando la herramienta se mueve respecto al motor,
- cuando un eje recto sería muy incómodo de montar.

### Recomendación general
- **directa** si entra,
- **engranajes** si se necesita precisión y relación mecánica,
- **cadenas** si hay que rutear movimiento a distancia,
- **cardanes** solo cuando la geometría los justifica.

---

## 15. ¿Conviene usar un motor para dos funciones distintas?

A veces sí. Pero solo bajo ciertas condiciones.

## 15.1. Cuándo puede convenir
- cuando las funciones nunca ocurren al mismo tiempo,
- cuando ahorrar peso o espacio es muy importante,
- cuando existe un selector mecánico confiable,
- cuando la secuencia es siempre la misma.

## 15.2. Cuándo no conviene
- si las dos funciones deben ser independientes,
- si a veces hay que sostener una pieza mientras se mueve otra cosa,
- si el cambio entre funciones puede trabarse,
- si el equipo todavía está luchando con la base de tracción.

## 15.3. Ejemplos donde sí puede funcionar
- un motor que primero posiciona un selector y luego mueve el mecanismo seleccionado,
- un motor que levanta y, en otra parte del ciclo, libera,
- un motor con retorno pasivo por gravedad, goma o resorte.

## 15.4. Costos ocultos
Usar un motor para dos tareas ahorra hardware, pero agrega:
- más lógica,
- más calibración,
- más modos de falla,
- más dependencia de topes y “home” mecánico.

### Recomendación
Para equipos en crecimiento:
- mejor dos mecanismos simples que un sistema brillante pero difícil de depurar.

---

## 16. Diseño para capturar objetos con tolerancia

Un robot fuerte en competencia no supone que el objeto está perfecto.
Diseña para tolerar un pequeño error.

### Recursos que ayudan mucho
- guías en forma de embudo,
- paredes internas que centran,
- topes mecánicos,
- piezas con algo de cumplimiento pasivo,
- boca ancha al entrar y zona precisa al final.

### Idea importante
La herramienta no debería “acertarle” a un punto ideal mínimo.
Debería **aceptar una banda de error**.

Eso es diseño competitivo de verdad.

---

## 17. Sensores y mecanismos no deben molestarse entre sí

Error muy común:
- sensor de piso demasiado cerca de una rueda o de una pieza que vibra,
- ultrasónico tapado por la garra,
- cable rozando el sensor,
- brazo que al bajar cambia la luz del sensor de piso.

### Regla simple
Antes de cerrar el robot, revisar:
- líneas de visión de sensores,
- recorrido completo de brazos,
- vibraciones,
- cables sueltos,
- sombras o reflejos extraños.

---

## 18. Recomendación concreta para este repo

Si el equipo quiere una base fuerte y razonable para seguir construyendo, yo recomendaría este enfoque:

### Base
- diferencial 2WD,
- ruedas medias como punto de partida,
- apoyo pasivo limpio y liviano,
- chasis bajo y rígido,
- frente plano para alineación.

### Distribución
- hub centrado y bajo,
- motores de tracción bien simétricos,
- mecanismos de misión cerca del frente, pero sin sobrecargarlo,
- peso equilibrado izquierda/derecha.

### Sensores
- sensor de piso rígido, protegido y calibrado a altura final,
- sensor de color de objetos en geometría controlada si la misión lo exige,
- ultrasónico solo si una rutina concreta demuestra que aporta más de lo que complica.

### Mecanismos
- primero un empujador y/o capturador confiable,
- luego elevación si realmente suma puntos,
- usar guías y topes antes que intentar resolver todo por software.

---

## 19. Checklist de diseño físico antes de dar el robot por bueno

### Tracción y base
- ¿Las dos ruedas motrices cargan parecido?
- ¿El robot sale recto sin patinar?
- ¿El apoyo pasivo no frena de más?
- ¿El robot gira igual hacia ambos lados?

### Estructura
- ¿El chasis flexa al agarrarlo con la mano?
- ¿Los engranajes están bien soportados?
- ¿Hay ejes largos en voladizo?
- ¿El brazo vibra mucho al frenar?

### Sensores
- ¿La altura del sensor de piso es siempre la misma?
- ¿La luz ambiente cambia mucho la lectura?
- ¿El objeto se presenta siempre igual al sensor de color?
- ¿El ultrasónico está libre y apunta limpio?

### Balance
- ¿El robot cabecea al arrancar o frenar?
- ¿Se inclina cuando sube el brazo?
- ¿Alguna esquina roza demasiado el piso?

### Competencia real
- ¿Se puede reparar rápido?
- ¿Se puede recalibrar rápido?
- ¿El equipo entiende cómo está construido?
- ¿Un alumno puede explicar por qué cada pieza importante está donde está?

---

## 20. Conclusión final

Un buen robot de RoboMission no es el que tiene más mecanismos.
Es el que combina bien estas cuatro cosas:

1. **tracción limpia**,
2. **estructura rígida**,
3. **sensores bien ubicados**,
4. **mecanismos simples con tolerancia al error**.

La construcción física debe ayudar al software, no obligarlo a compensar un mal diseño.

Dicho de forma simple:

> **si el robot está bien construido, programar se vuelve mucho más fácil.**

Y al revés también:

> **cuando la mecánica está mal, ningún código “salva” la repetibilidad.**

---

## Fuentes base y referencias técnicas

- WRO Association - 2026 Season / RoboMission General Rules 2026
- Pybricks Documentation - `DriveBase`, `Motor`, `ColorSensor`, `UltrasonicSensor`
- LEGO Education SPIKE Prime - Technical Info / Tips & Tricks
- Documentación actual del repo en `docs/es/hardware/README.md`, `docs/es/software/README.md` y `software/programs/base_config.py`
