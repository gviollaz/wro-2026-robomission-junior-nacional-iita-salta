# Plan de validación del robot IITA v1

## 1. Filosofía

No se valida por una corrida espectacular sino por repetibilidad.

Cada modificación de hardware o software debe pasar por:

1. prueba unitaria del módulo;
2. prueba de integración parcial;
3. corrida completa SAFE;
4. corrida completa FULL;
5. registro de falla dominante.

## 2. Ensayos unitarios

### Navegación

- 20 rectas de 500 mm
- error lateral máximo aceptable: 12 mm
- 20 giros a 90 grados
- error angular máximo aceptable: 3 grados

### Frente de captura

- 20 capturas de visitante
- 20 capturas de artefacto
- tasa mínima aceptable: 90%

### Túnel de lectura

- 20 lecturas por color
- exactitud mínima aceptable: 95% por color en condiciones controladas

### Elevador

- 20 subidas y bajadas
- 20 intentos de colocación de tapa
- éxito mínimo: 85%

## 3. Ensayos de integración

### Macro A

- visitante verde + primer artefacto + museo

### Macro B

- torres rojas + tapas amarillas

### Macro C

- visitantes negro y azul + suciedad tardía

Cada macro debe probarse 15 veces antes de entrar a corrida completa.

## 4. Corridas completas

### SAFE

- 20 corridas
- randomización real o simulada de artefactos y suciedad
- registrar puntos, tiempo y fallas

### FULL

- 10 corridas
- registrar puntos, tiempo y fallas

## 5. Métricas obligatorias por corrida

- puntaje total
- tiempo total
- bonus sí/no
- cantidad de artefactos correctos
- tapas amarillas sí/no
- barrera dañada sí/no
- recuperación utilizada sí/no
- causa principal de pérdida

## 6. Criterio de promoción a competencia

El robot pasa a "versión lista" cuando:

- SAFE >= 85% de éxito global;
- bonus >= 95%;
- tiempo medio SAFE < 95 s;
- FULL >= 70% con 4 artefactos o equivalente en puntaje esperado.

## 7. Lista de fallas a vigilar

- lectura errónea del negro;
- entrada doble al túnel;
- tapa amarilla inclinada;
- empuje lateral sobre torre roja;
- suciedad lanzada contra barrera roja;
- deriva acumulada tras retroceso largo;
- caster sucio o frenado.
