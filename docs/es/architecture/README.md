# Arquitectura del Robot - Junior

## Requisitos

- Caber en 250 x 250 x 250 mm antes del inicio
- LEGO Spike Prime con firmware Pybricks
- Sensor de color para detectar artefactos randomizados
- Sensor de distancia (opcional) para alineacion
- Brazo elevador para apilar torres amarillas
- Garra/pinza para manipular objetos

## Diseno propuesto

> TODO: completar cuando se defina el diseno.

### Chasis
- Base diferencial (2 motores de traccion)
- Ruedas grandes (56mm)

### Accesorios
- **Brazo elevador** (motor dedicado) para apilar tapas amarillas sobre bases
- **Garra/pinza** para agarrar visitantes, torres, artefactos
- **Barredora** ancha para limpiar particulas de adoquines
- Sensor de color apuntando hacia abajo

### Puertos
| Puerto | Componente |
|--------|------------|
| A | Motor izquierdo (COUNTERCLOCKWISE) |
| B | Motor derecho |
| C | Motor brazo elevador |
| D | Motor garra/pinza |
| E | Sensor de color |
| F | Sensor de distancia (opcional) |

## Consideraciones clave

- **Torres amarillas (50 pts)** son la mision mas dificil y valiosa: requieren elevar la tapa y colocarla sobre la base con precision
- La **barredora** para adoquines debe cubrir al menos 1/3 del area por pasada
- Priorizar consistencia sobre velocidad
- Planificar rutas que eviten barreras y loro (bonus 30 pts)
