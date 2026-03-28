# 01 - Fundamentos del Seguimiento de Línea

## ¿Qué es seguir una línea?

Imaginate que caminás por una vereda con los ojos cerrados y solo podés tocar el borde del cordón con un pie. Si tu pie toca el cordón, girás un poquito hacia afuera. Si tu pie no lo toca, girás un poquito hacia adentro. Así vas caminando en zigzag siguiendo el borde del cordón.

**Tu robot hace exactamente lo mismo**, pero en lugar de un pie usa un **sensor de color** que mira hacia abajo, y en lugar de un cordón sigue el **borde de una línea negra** sobre fondo blanco.

## ¿Cómo funciona el sensor de color?

El sensor de color de SPIKE Prime tiene una lucecita que ilumina el piso y mide **cuánta luz rebota** (se refleja). Esto se llama **reflexión**.

```
Superficie blanca → mucha luz rebota    → reflexión ALTA (85-95%)
Superficie negra  → poca luz rebota     → reflexión BAJA (5-15%)
Borde de la línea → algo de luz rebota  → reflexión MEDIA (45-55%)
```

### Visualización del sensor sobre la línea

```
  Blanco    Borde Izq    Negro    Borde Der    Blanco
  ~~~~~~~~|............|████████|............|~~~~~~~~
   90%        50%         10%       50%         90%
     ↑                                          ↑
  Reflexión alta                          Reflexión alta
```

## ¿Qué es el UMBRAL (threshold)?

El **umbral** es el valor de reflexión que está justo en el medio entre negro y blanco. Es el valor que el robot busca mantener debajo del sensor.

```
UMBRAL = (valor_negro + valor_blanco) / 2
```

**Ejemplo:** Si negro = 8 y blanco = 92, entonces:
```
UMBRAL = (8 + 92) / 2 = 50
```

Cuando el sensor lee exactamente el umbral, el robot va derecho. Cuando lee más o menos que el umbral, el robot corrige girando.

## Calibración: el paso más importante

**¿Por qué calibrar?** Porque los valores de negro y blanco cambian según:
- La luz del ambiente (sol, lámparas, hora del día)
- La distancia del sensor al piso
- El desgaste del tapete
- La batería del hub (afecta la intensidad de la luz del sensor)

### Programa de calibración en Pybricks

```python
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import ColorSensor
from pybricks.parameters import Port, Button
from pybricks.tools import wait

hub = PrimeHub()
sensor = ColorSensor(Port.C)  # Ajustá el puerto

# --- Paso 1: Medir NEGRO ---
print("Poné el sensor sobre la línea NEGRA")
print("Presioná el botón izquierdo del hub")

while Button.LEFT not in hub.buttons.pressed():
    wait(50)
wait(500)  # Esperar medio segundo para estabilizar

negro = sensor.reflection()
print("Negro =", negro)

# --- Paso 2: Medir BLANCO ---
print("Poné el sensor sobre el fondo BLANCO")
print("Presioná el botón derecho del hub")

while Button.RIGHT not in hub.buttons.pressed():
    wait(50)
wait(500)

blanco = sensor.reflection()
print("Blanco =", blanco)

# --- Resultado ---
umbral = (negro + blanco) / 2
print("=== RESULTADOS ===")
print("Negro:", negro)
print("Blanco:", blanco)
print("Umbral:", umbral)
print("Rango:", blanco - negro)

# Verificar que los valores son razonables
if blanco - negro < 30:
    print("¡CUIDADO! El rango es muy chico.")
    print("Revisá la altura del sensor o la superficie.")
```

### ¿Qué valores son buenos?

| Medición | Valor típico | ¿Preocupante? |
|----------|-------------|---------------|
| Negro | 5-15 | Si es mayor a 25, el sensor está lejos del piso |
| Blanco | 80-95 | Si es menor a 60, el sensor está lejos o hay poca luz |
| Rango (blanco - negro) | > 50 | Si es menor a 30, va a ser difícil seguir la línea |
| Umbral | 40-55 | Debe estar entre negro y blanco |

## ¿Qué es el "borde" de la línea?

La línea negra tiene **dos bordes**: el izquierdo y el derecho. Cuando seguimos una línea con 1 sensor, en realidad seguimos **uno de los bordes**, no el centro.

```
         BORDE IZQUIERDO         BORDE DERECHO
              ↓                       ↓
  Blanco     |██████ NEGRO ██████|     Blanco
  ~~~~~~~~~~~|████████████████████|~~~~~~~~~~~
              ←  ancho de línea  →
              (aprox. 20mm en WRO)
```

### ¿Por qué importa qué borde seguimos?

Si el robot sigue el **borde izquierdo**:
- Cuando ve más negro (reflexión baja) → gira a la **izquierda** (hacia el blanco)
- Cuando ve más blanco (reflexión alta) → gira a la **derecha** (hacia el negro)

Si el robot sigue el **borde derecho**:
- Cuando ve más negro (reflexión baja) → gira a la **derecha** (hacia el blanco)
- Cuando ve más blanco (reflexión alta) → gira a la **izquierda** (hacia el negro)

**La diferencia entre seguir borde izquierdo y derecho es simplemente invertir el signo de la corrección.**

## Conceptos clave para recordar

1. **Reflexión** = cuánta luz rebota del piso (0% a 100%)
2. **Umbral** = punto medio entre negro y blanco
3. **Error** = diferencia entre lo que lee el sensor y el umbral
4. **Corrección** = cuánto tiene que girar el robot para volver al borde
5. **Calibrar** = medir negro y blanco antes de competir
6. **Borde** = la zona de transición entre negro y blanco

## ¿Qué sigue?

En el siguiente documento aprenderás a programar un seguidor de línea con **1 sensor** usando control proporcional (P) y PID.
