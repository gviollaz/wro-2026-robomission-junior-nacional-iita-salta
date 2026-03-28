# 07 - Estrategias de Competición WRO RoboMission

## Filosofía de navegación en WRO

En WRO RoboMission, el tapete tiene líneas negras que conectan zonas. Tu robot navega entre estas zonas para completar misiones. La clave es combinar las técnicas en una **biblioteca de movimientos**.

## La biblioteca de movimientos

Pensá en tu programa como una **receta de cocina**: cada paso es un movimiento simple.

```python
# Tu "caja de herramientas":
seguir_hasta_interseccion(lado, numero, borde, velocidad)
seguir_y_girar(lado_giro, en_interseccion_numero, borde, velocidad)
seguir_hasta_fin_de_linea(borde, velocidad)
avanzar_hasta_linea(sensor, velocidad)
alinear_perpendicular(sensor_izq, sensor_der, ...)
robot.straight(distancia_mm)
robot.turn(angulo)
```

## Patrones comunes en WRO

### Patrón 1: Ida y vuelta por un ramal

```python
def ida_y_vuelta_ramal(interseccion_num, lado, tarea_func):
    girar_en_interseccion(lado, interseccion_num, lado)
    seguir_hasta_fin_de_linea()
    tarea_func()
    robot.turn(180)
    seguir_hasta_interseccion(lado="ambas", numero=1)
    if lado == "derecha":
        robot.straight(40)
        robot.turn(-90)
    else:
        robot.straight(40)
        robot.turn(90)
    avanzar_hasta_linea(sensor_centro)
```

### Patrón 2: Navegación con decisión (randomización WRO)

```python
def navegar_con_decision(sensor_decision):
    color = sensor_decision.color()
    if color == Color.RED:
        girar_en_interseccion("izquierda", 1, "izquierda")
    elif color == Color.BLUE:
        girar_en_interseccion("derecha", 1, "derecha")
    elif color == Color.GREEN:
        seguir_hasta_interseccion("ambas", 1)
```

## Velocidad adaptativa

```python
VELOCIDAD_RAPIDA = 250    # Tramos rectos largos
VELOCIDAD_NORMAL = 180    # Seguimiento general
VELOCIDAD_PRECISA = 100   # Cerca de intersecciones
VELOCIDAD_BUSQUEDA = 80   # Buscando líneas, alineando

def seguir_con_frenado(lado, numero, borde="izquierdo"):
    for i in range(numero - 1):
        seguir_hasta_interseccion(lado, 1, borde, velocidad=VELOCIDAD_RAPIDA)
        robot.straight(30)
    seguir_hasta_interseccion(lado, 1, borde, velocidad=VELOCIDAD_PRECISA)
```

## Estructura recomendada del programa

```python
# ============================================
# PROGRAMA WRO ROBOMISSION - [NOMBRE EQUIPO]
# ============================================

# --- 1. IMPORTS ---
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Direction, Button, Color
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# --- 2. INICIALIZACIÓN ---
hub = PrimeHub()
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=112)
sensor_izq = ColorSensor(Port.C)
sensor_centro = ColorSensor(Port.D)
sensor_der = ColorSensor(Port.E)
brazo = Motor(Port.F)

# --- 3. CONSTANTES ---
NEGRO = 10
BLANCO = 90

# --- 4. FUNCIONES DE NAVEGACIÓN ---
# (todas las funciones de seguimiento, intersecciones, etc.)

# --- 5. FUNCIONES DE TAREAS ---
def tarea_zona_a():
    brazo.run_angle(200, 180)
    wait(500)
    brazo.run_angle(200, -180)

# --- 6. PROGRAMA PRINCIPAL ---
def main():
    while Button.CENTER not in hub.buttons.pressed():
        wait(50)
    wait(500)
    
    # Paso 1: Salir del inicio
    avanzar_hasta_linea(sensor_centro)
    # Paso 2: Ir a zona A
    seguir_hasta_interseccion("derecha", 2)
    # ... etc.
    
    print("¡Misión completa!")

# --- 7. EJECUTAR ---
main()
```

## Checklist de competición

- [ ] ¿Batería cargada?
- [ ] ¿Calibraste negro y blanco en el tapete de competición?
- [ ] ¿Sensores a la altura correcta?
- [ ] ¿Ruedas limpias?
- [ ] ¿Programa arranca con un botón del hub?
- [ ] ¿Robot cabe en 250mm × 250mm × 250mm?
- [ ] ¿Probaste con tapete desalineado?
- [ ] ¿Hay plan B si algo falla?

## Errores comunes en competencia

| Error | Causa | Solución |
|-------|-------|----------|
| Se pierde en la primera curva | Kp bajo o velocidad alta | Bajar velocidad, subir Kp |
| Cuenta intersecciones de más | Sin debounce | Agregar debounce + distancia mínima |
| No detecta intersección | Velocidad muy alta | Bajar velocidad, ajustar umbral |
| Se desalinea después de girar | Giro impreciso | Usar girar_buscando_linea |
| Diferente al de práctica | Diferente iluminación | ¡Calibrar en el lugar! |
| Patina en curvas | Ruedas sucias | Limpiar ruedas, reducir velocidad |

## Consejo final

> **La constancia gana competencias, no la velocidad.** Un robot que completa la misión lento pero siempre, le gana a uno que a veces la hace rápido pero a veces se pierde. Primero hacelo funcionar, después hacelo rápido.
