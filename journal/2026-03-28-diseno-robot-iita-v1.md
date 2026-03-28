# Registro de decisión - Diseño de robot IITA v1

Fecha: 2026-03-28

## Decisiones tomadas

1. Se mantiene la plataforma SPIKE Prime + Pybricks.
2. Se elige base diferencial en lugar de mecanum.
3. Se privilegia frente pasivo multifunción.
4. Se reservan dos sensores de color: piso y artefactos.
5. Se descarta por ahora el sensor de distancia para no sacrificar lectura de color.
6. Se define estrategia de doble programa: SAFE y FULL.
7. Se decide dejar visitantes negro y azul para el final si la rutina incluye suciedad.
8. Se decide leer artefactos dentro de un túnel oscuro y no contra el tapete.
9. Se decide usar topes mecánicos duros para home del elevador.
10. Se define que la suciedad será una misión condicional y tardía.

## Motivos

- mayor confiabilidad;
- menos deriva;
- menor complejidad de cableado y puertos;
- mejor tasa de repetición;
- menor riesgo de perder bonus.

## Próximo sprint sugerido

1. Construir V1 con frente, túnel y navegación.
2. Cerrar calibración de sensor frontal.
3. Construir elevador V2.
4. Registrar 20 SAFE runs.
5. Optimizar peso y rigidez para V3.
