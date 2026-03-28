# Hardware concreto del robot IITA v1

## 1. Resumen

Robot diferencial con 4 actuadores totales:

- 2 motores grandes de tracción
- 2 motores medianos auxiliares
- 2 sensores de color
- 1 hub SPIKE Prime

## 2. Módulos físicos

### Módulo A: chasis principal

Objetivo:

- rigidez torsional;
- centro de gravedad bajo;
- montaje rápido;
- acceso directo al botón del hub.

Especificación:

- bastidor rectangular tipo escalera con doble larguero;
- refuerzo transversal delante del hub;
- refuerzo corto encima del eje de motores;
- piso interior libre para cableado y compuerta.

### Módulo B: tracción

Configuración:

- motor grande izquierdo en el lateral izquierdo;
- motor grande derecho en el lateral derecho;
- transmisión directa 1:1;
- ruedas iguales y nuevas o pareadas por desgaste.

Buenas prácticas:

- no mezclar neumáticos con distinto desgaste;
- no apretar demasiado ejes o separadores;
- revisar juego lateral en cada jornada.

### Módulo C: apoyo trasero

Opción preferida:

- caster o patín único centrado.

Objetivo:

- bajo arrastre;
- comportamiento repetible al retroceder;
- mantenimiento simple.

Si se usa ball caster, limpiarlo con frecuencia para que el polvo del piso no cambie la deriva.

### Módulo D: frente pasivo

Características obligatorias:

- ancho suficiente para interceptar piezas sin perder maniobrabilidad;
- borde inferior liso;
- alas con ángulo suave;
- canal central auto-centrante.

Geometría sugerida:

- frente útil: 135 a 150 mm;
- profundidad del frente: 45 a 65 mm;
- inclinación del labio: suave, para no montar sobre piezas;
- canal central más estrecho que la boca de entrada, para centrar.

### Módulo E: túnel de lectura

Diseño:

- pared lateral izquierda y derecha;
- techo corto;
- sensor frontal centrado;
- compuerta detrás o debajo del sensor.

Objetivo:

- aislar el artefacto del color del tapete;
- reducir luz ambiente;
- fijar distancia de lectura.

### Módulo F: elevador

Recomendación mecánica:

- movimiento corto;
- alta rigidez;
- topes físicos en home y place;
- posibilidad de microajuste del ángulo de entrega.

Se recomienda que la cuna tenga:

- una V suave o embudo;
- laterales que impidan que la tapa amarilla gire;
- un borde delantero que la sostenga sin tapar demasiado la visión del conductor en práctica.

## 3. Distribución de masas

Objetivo:

- 55 a 60% del peso sobre el eje motriz;
- 40 a 45% repartido hacia el frente y apoyo trasero.

No conviene cargar demasiado el frente: mejora empuje, pero empeora la entrada fina a tapas amarillas y hace más agresivo el contacto con barreras.

## 4. Diseño para mantenimiento rápido

Todo módulo debe poder desmontarse en menos de 5 minutos:

- frente;
- elevador;
- sensor frontal;
- rueda o patín.

Cada cable debe estar identificado por color o etiqueta de puerto.

## 5. Componentes opcionales muy recomendables

Si el reglamento local los mantiene permitidos y el equipo puede fabricarlos bien:

- embudo impreso 3D para tapas amarillas;
- cubierta negra impresa para el túnel del sensor frontal;
- separadores simétricos para fijar altura exacta del sensor de piso.

## 6. Tres versiones mecánicas a construir

### V1: base de validación

Objetivo: cerrar navegación y frente.

Sin elevador sofisticado. Solo geometría de captura y sensor frontal.

### V2: base competitiva

Objetivo: integrar elevador y compuerta.

Ya debe poder hacer SAFE run.

### V3: base final

Objetivo: aligerar, rigidizar y bajar tiempos.

Eliminar piezas innecesarias, simplificar soportes, cerrar topes y mejorar cableado.
