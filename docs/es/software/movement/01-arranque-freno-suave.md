# 01 - Arranque Suave, Freno Suave y Perfiles de Velocidad

## ¿Por qué no arrancar a toda velocidad?

Cuando le decís al robot "andá a 300 mm/s", los motores intentan llegar a esa velocidad instantáneamente. Esto causa:

- **Patinaje de ruedas**: las ruedas giran más rápido de lo que el piso permite → el robot se desvía
- **Error de odometría**: el encoder del motor cuenta grados que la rueda no recorrió → la distancia medida es incorrecta
- **Sacudones mecánicos**: las piezas LEGO se aflojan con el tiempo por los golpes

Los equipos ganadores de WRO usan **aceleración progresiva**: el robot empieza lento y sube la velocidad gradualmente.

## DriveBase.settings(): tu mejor amigo

Pybricks tiene un sistema de control de velocidad integrado. Con `robot.settings()` configurás la aceleración máxima:

```python
robot.settings(
    straight_speed=200,
    straight_acceleration=150,
    turn_rate=120,
    turn_acceleration=80
)
```

### Perfiles recomendados para WRO

```python
def perfil_preciso():
    robot.settings(straight_speed=120, straight_acceleration=80,
                   turn_rate=80, turn_acceleration=60)

def perfil_normal():
    robot.settings(straight_speed=200, straight_acceleration=150,
                   turn_rate=120, turn_acceleration=80)

def perfil_rapido():
    robot.settings(straight_speed=350, straight_acceleration=200,
                   turn_rate=150, turn_acceleration=100)
```

## Velocidad máxima real del SPIKE Prime

Motores SPIKE: ~1000°/s. Con ruedas 56mm: máx ~488 mm/s. Usar máximo 80% = ~350-400 mm/s. Si configurás más, Pybricks no tiene espacio para correcciones y el robot se desvía.

## Freno suave: el secreto de la odometría precisa

### Técnica 1: Reducir velocidad antes de frenar

```python
def avanzar_preciso(distancia_mm, velocidad=200):
    ZONA_FRENADO = 50
    if distancia_mm > ZONA_FRENADO * 2:
        perfil_normal()
        robot.straight(distancia_mm - ZONA_FRENADO)
        perfil_preciso()
        robot.straight(ZONA_FRENADO)
    else:
        perfil_preciso()
        robot.straight(distancia_mm)
```

### Técnica 2: Stop modes

```python
robot.straight(200)                    # Stop.HOLD: posición precisa
robot.straight(200, then=Stop.BRAKE)   # Frena sin mantener
robot.straight(200, then=Stop.COAST)   # Transición suave
```

| Situación | Stop recomendado |
|-----------|------------------|
| Antes de recoger objeto | HOLD |
| Antes de girar | COAST o BRAKE |
| Final de misión | HOLD |
| Entre movimientos rápidos | BRAKE |

## Curvas en vez de giro + recto

```python
# Más fluido que turn(90) + straight(100):
robot.curve(radius=80, angle=90)
```

## Reglas de oro

1. Nunca superes 80% de la velocidad máxima del motor
2. Usá aceleración < 200 mm/s² para evitar patinaje
3. Frenar suave antes de posiciones críticas
4. Preferí curvas a giro+recto cuando sea posible
5. Probá cada perfil y medí la desviación con el giroscopio
