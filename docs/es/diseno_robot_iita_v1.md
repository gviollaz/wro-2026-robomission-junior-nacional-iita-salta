# Diseño concreto de robot IITA v1 para WRO RoboMission Junior 2026

Fecha: 2026-03-28  
Plataforma objetivo: LEGO SPIKE Prime + Pybricks  
Objetivo: priorizar una solución robusta, rápida y repetible para Nacional Argentina.

## 1. Decisión de arquitectura

Se propone un robot diferencial 2WD, con dos ruedas motrices laterales, una rueda loca o patín trasero, dos sensores de color externos y dos actuadores auxiliares.

Arquitectura elegida:

- Hub SPIKE Prime centrado y accesible desde arriba.
- Tracción diferencial con 2 motores grandes.
- Módulo frontal pasivo de captura y guiado.
- Elevador frontal superior para tapas amarillas y estabilización de torres rojas.
- Compuerta o eyector corto para ordenar el flujo interno de visitantes y artefactos.
- Sensor de piso para referencias de navegación.
- Sensor de color frontal en túnel oscuro para lectura confiable de artefactos.

Razones de esta elección:

1. Minimiza complejidad y deriva frente a una base mecanum.
2. Deja suficientes puertos para sensores sin sacrificar actuadores críticos.
3. Permite combinar varias misiones con un mismo frente mecánico.
4. Facilita una rutina SAFE y una rutina FULL sin cambiar hardware.

## 2. Objetivos de puntaje por modo de juego

### Modo SAFE

Meta de puntaje de diseño: 170 a 195 puntos.

Prioridades:

- Visitantes completos.
- Torres rojas.
- Tapas amarillas.
- Bonus intacto.
- 2 o 3 artefactos confiables.
- Suciedad solamente si la pasada no compromete bonus.

### Modo FULL

Meta de puntaje de diseño: 200 a 230 puntos.

Prioridades:

- Todo lo anterior.
- 4 artefactos completos.
- Barrido tardío de suciedad hacia áreas seguras.

## 3. Configuración concreta del robot

### 3.1 Dimensiones objetivo

Configuración de salida:

- Largo: 190 mm
- Ancho: 160 mm
- Alto: 245 mm

Configuración expandida en juego:

- Largo máximo operativo: 290 mm
- Ancho máximo operativo: 210 mm
- Alto máximo operativo: 310 mm

Objetivo de peso:

- Ideal: 1050 a 1180 g
- Máximo deseado de diseño: 1250 g

No conviene acercarse al límite reglamentario de 1,5 kg; el robot gana tracción pero empeora frenado, rebota más al tocar objetos y aumenta el riesgo de mover barreras o descentrar torres.

### 3.2 Distribución de puertos

- Puerto A: motor de tracción izquierdo
- Puerto B: motor de tracción derecho
- Puerto C: motor elevador frontal
- Puerto D: motor compuerta / selector / micro-eyector
- Puerto E: sensor de color de piso
- Puerto F: sensor de color frontal de artefactos

### 3.3 Sensores

Sensor de piso:

- Ubicación: adelante-izquierda, protegido dentro del chasis
- Altura objetivo: 10 a 12 mm sobre la lona
- Uso: detección de referencias, corrección de posición, salida de adoquinado, líneas límite y control de consistencia

Sensor frontal de artefactos:

- Ubicación: centrado en un túnel oscuro frontal
- Altura objetivo respecto al objeto: 8 a 12 mm
- Uso: lectura de color una vez que el artefacto ya está aislado del fondo del tapete
- Recomendación: túnel con paredes negras mate o cobertor que reduzca luz ambiente

## 4. Módulos mecánicos

## 4.1 Base motriz

Diseño:

- Dos motores grandes con transmisión 1:1.
- Ruedas medianas con buen agarre.
- Distancia inicial entre centros de rueda: 128 a 132 mm.
- Centro de gravedad ligeramente adelantado respecto al eje de tracción para mejorar empuje frontal, pero sin descargar demasiado el patín trasero.

Objetivo dinámico:

- Velocidad alta en rectas cortas.
- Frenado limpio.
- Giro controlado por heading con IMU.

## 4.2 Frente pasivo multifunción

El frente es la pieza más importante del robot.

Debe resolver cuatro tareas con la misma geometría:

- guiar visitantes;
- capturar artefactos;
- apartar suciedad del adoquinado;
- presentar piezas al módulo elevador sin golpes.

Diseño recomendado:

- Labio inferior tipo pala, bajo y liso.
- Dos alas laterales con chaflán suave para centrar piezas.
- Canal central de captura.
- Túnel oscuro por encima del canal para lectura de color.

Ventaja:

Se reduce la necesidad de garras complejas. La geometría pasiva hace la mayor parte del trabajo.

## 4.3 Módulo elevador para tapas amarillas y control de torres

Recomendación:

- 1 motor mediano.
- Brazo tipo paralelogramo corto o elevador lineal guiado.
- Cuna superior con embudo centrador.
- Tope mecánico duro para cero absoluto.

Función principal:

- Tomar o estabilizar la tapa amarilla.
- Depositarla verticalmente sobre la torre amarilla sin empujar la base.

Función secundaria:

- Acompañar el transporte de torres rojas altas, agregando guía media para evitar vuelco.

## 4.4 Compuerta / selector / eyector interno

Recomendación:

- 1 motor mediano.
- Movimiento corto de 40 a 70 grados.
- Modo 1: retener pieza en túnel para lectura.
- Modo 2: liberar hacia museo o hacia guía de visitante.
- Modo 3: separar una pieza atascada.

Este motor no debe intentar hacer una clasificación compleja; debe ser simple, rápido y repetible.

## 5. Vista superior conceptual

```text
            [ Elevador / cuna tapas amarillas ]
                     _________
                    /         \
   ala izquierda   /  túnel    \   ala derecha
  ________________/  sensor F   \________________
 /                                              \
|   pala frontal / canal de captura / barrido    |
|                                                |
|   sensor E                       Hub SPIKE     |
|                                                |
|  Motor A                          Motor B      |
|                                                |
 \___________________patín/caster________________/
```

## 6. Estrategia de secuencia recomendada

### Ruta SAFE

1. Resolver visitante verde temprano, porque comparte vecindad con excavación y libera espacio.
2. Capturar primer bloque de artefactos accesibles.
3. Llevar visitante rojo junto con artefactos al museo en el mismo macro-viaje.
4. Resolver torres rojas.
5. Resolver tapas amarillas con rutina lenta y precisa.
6. Dejar visitantes negro y azul para la parte final.
7. Barrer suciedad solo si el bonus está protegido y el tiempo restante es cómodo.

### Ruta FULL

1. Verde temprano.
2. Barrido de artefactos 1 y 2.
3. Entrega museo + rojo.
4. Torres rojas.
5. Tapas amarillas.
6. Artefactos 3 y 4.
7. Negro y azul al final.
8. Suciedad hacia áreas negro y azul o líneas no-adoquinadas, evitando la barrera roja.

## 7. Decisiones tácticas clave

### 7.1 Negro y azul al final

Las áreas de visitante negro y azul convienen como zonas seguras de expulsión de suciedad. Por eso no conviene ocuparlas temprano si la rutina incluye barrido.

### 7.2 Artefactos: leer después de aislar

No se debe leer el color del artefacto contra el piso del campo. Primero se lo encierra en el túnel, luego se mide HSV y recién después se decide la descarga.

### 7.3 Tapas amarillas: precisión mecánica antes que software

La colocación de techos amarillos debe depender más de embudos, guías y topes que de una odometría perfecta. El último centímetro debe autocentrarse.

### 7.4 Suciedad: misión condicional

La suciedad suma poco respecto al riesgo de perder bonus. Se activa solo cuando el frente y la trayectoria fueron validados al 90% o más.

## 8. Diseño del software para este robot

La arquitectura recomendada tiene tres capas:

1. primitivas de movimiento;
2. acciones de mecanismo;
3. planes de misión.

Primitivas mínimas:

- `drive_mm(mm, speed, accel)`
- `turn_to_heading(deg, speed)`
- `seek_line(reflection_target)`
- `capture_until_contact_or_line()`
- `scan_artifact_color()`
- `place_yellow_roof()`
- `stabilize_red_tower()`
- `sweep_to_safe_zone()`

Planes de misión:

- `safe_run()`
- `full_run()`
- `recover_from_misalignment()`

## 9. Puntos de calibración obligatorios

- diámetro efectivo de rueda;
- axle track real;
- heading correction del IMU;
- altura exacta del sensor de piso;
- perfiles HSV del sensor frontal;
- ángulos de home, pick y place del elevador;
- tiempos máximos permitidos por acción antes de recovery.

## 10. Criterios de aceptación para declarar el robot competitivo

El robot no se considera listo para final nacional hasta cumplir esto:

- SAFE run con 20 corridas: 85% o más de éxito total.
- Bonus intacto: 95% o más.
- Tapas amarillas: 85% o más.
- Tres artefactos correctos: 80% o más.
- Visitantes completos: 90% o más.
- Tiempo medio SAFE: menos de 95 s.

Y para FULL run:

- 10 corridas con randomización real.
- 70% o más de éxito de 4 artefactos.
- Tiempo medio FULL: menos de 110 s.

## 11. Recomendación final

Si el equipo tiene que elegir entre un robot espectacular o un robot repetible, elegir el repetible.

La mejor versión ganadora para este repo, hoy, es:

- base diferencial simple;
- frente pasivo inteligente;
- dos sensores de color;
- un elevador muy bien guiado;
- una compuerta pequeña para ordenar flujo;
- una ruta SAFE que ya gane y una FULL para pelear arriba.

Ese equilibrio es el que mejor convierte confiabilidad en puntos.
