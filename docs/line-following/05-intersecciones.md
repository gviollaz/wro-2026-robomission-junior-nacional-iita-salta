# 05 - Intersecciones y Bifurcaciones

## ¿Qué es una intersección?

Una intersección es un punto donde **una línea se cruza con otra**. En los tapetes de WRO RoboMission, encontrás varios tipos:

```
CRUCE EN T (izquierda)     CRUCE EN T (derecha)      CRUCE EN +
                                                        │
━━━━━━┓                        ┏━━━━━━                ━━┿━━
      ┃                        ┃                        │
      ┃                        ┃                        │

CURVA A 90° (izquierda)    CURVA A 90° (derecha)     FIN DE LÍNEA
                                                        
━━━━━━┓                        ┏━━━━━━                ━━━━━━╸
      ┃                        ┃                      (la línea se termina)
      ┃                        ┃

BIFURCACIÓN EN Y           LÍNEA RECTA CON MARCA
     ╱                     
━━━━┫                      ━━━━━━━━━━━━━━━━━━━━
     ╲                          ┃
                                ┃ (marca perpendicular)
```

## El desafío: ¿Cómo sabe el robot dónde está?

El robot no puede "ver" el mapa completo. Solo sabe lo que **sus sensores detectan en ese instante**. Por eso necesitamos estrategias claras.

## Estrategia 1: Contar intersecciones por lado

El robot sigue la línea y **cuenta cuántas intersecciones pasan** de cada lado. Cuando llega a la que buscamos, se detiene o toma una acción.

### Ejemplo práctico

```
INICIO
  │
  │  ← Intersección 1 izq.
  ├──────────
  │
  │  ← Intersección 2 izq.
  ├──────────
  │
  │         ── Intersección 1 der. →
  ├──────────────────
  │
  FIN
```

```python
seguir_hasta_interseccion(lado="izquierda", numero=2)  # Para en la 2da izq.
seguir_hasta_interseccion(lado="derecha", numero=1)     # Para en la 1ra der.
```

## Estrategia 2: Acciones en intersecciones

### Acción A: Detenerse

```python
def parar_en_interseccion(lado, numero, borde="izquierdo"):
    seguir_hasta_interseccion(lado, numero, borde)
    robot.stop()
```

### Acción B: Girar 90° y tomar la nueva línea

```python
def girar_en_interseccion(lado_deteccion, numero, lado_giro, borde="izquierdo"):
    seguir_hasta_interseccion(lado_deteccion, numero, borde)
    robot.straight(40)
    if lado_giro == "izquierda":
        robot.turn(-90)
    else:
        robot.turn(90)
    robot.straight(25)
    resetear_pid()
```

### Acción C: Pasar de largo

```python
def seguir_ignorando_intersecciones(distancia_mm):
    robot.reset()
    resetear_pid()
    while robot.distance() < distancia_mm:
        seguir_linea_3s("izquierdo")
        wait(10)
    robot.stop()
```

### Acción D: Girar con búsqueda de línea (más preciso)

```python
def girar_buscando_linea(lado_deteccion, numero, lado_giro, borde="izquierdo"):
    seguir_hasta_interseccion(lado_deteccion, numero, borde)
    robot.straight(40)
    if lado_giro == "izquierda":
        vel_giro = -80
    else:
        vel_giro = 80
    # Fase 1: Girar hasta salir de la línea actual (ver blanco)
    robot.drive(0, vel_giro)
    while sensor_centro.reflection() < 60:
        wait(10)
    # Fase 2: Seguir girando hasta encontrar la nueva línea (ver negro)
    while sensor_centro.reflection() > 30:
        wait(10)
    robot.stop()
    resetear_pid()
```

## Problemas comunes y soluciones

### Problema 1: Cuenta intersecciones de más
**Solución:** Usar debounce + distancia mínima entre intersecciones:

```python
def seguir_hasta_interseccion_v2(lado, numero, borde="izquierdo", distancia_minima=30):
    conteo = 0
    en_interseccion = False
    robot.reset()
    distancia_ultima = 0
    while True:
        seguir_linea_3s(borde)
        lecturas = leer_todo()
        if lado == "izquierda":
            detectado = lecturas["inter_izq"]
        elif lado == "derecha":
            detectado = lecturas["inter_der"]
        else:
            detectado = lecturas["inter_izq"] and lecturas["inter_der"]
        distancia_actual = robot.distance()
        if (detectado and not en_interseccion and
            distancia_actual - distancia_ultima > distancia_minima):
            conteo += 1
            en_interseccion = True
            distancia_ultima = distancia_actual
            if conteo >= numero:
                robot.stop()
                return conteo
        elif not detectado:
            en_interseccion = False
        wait(10)
```

### Problema 2: No detecta una intersección
**Solución:** Reducir velocidad, alejar sensores laterales del centro, bajar umbral.

### Problema 3: Confunde curva con intersección
**Solución:** Usar 3 sensores (central sigue, laterales detectan).

### Problema 4: Después de girar, no encuentra la nueva línea
**Solución:** Usar `girar_buscando_linea` en vez de ángulo fijo.

## Diagrama de flujo

```
INICIO TRAMO → Seguir línea PID → ¿Sensor lateral detecta negro?
  ↑ NO                                    ↓ SÍ
  └────────────────────── ¿Es nueva? (debounce)
                              ↓ SÍ
                         conteo += 1 → ¿conteo == objetivo?
                                            ↓ SÍ
                                      EJECUTAR ACCIÓN
```
