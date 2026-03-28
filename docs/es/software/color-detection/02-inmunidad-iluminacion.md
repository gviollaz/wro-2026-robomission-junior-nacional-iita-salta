# Inmunidad ante Cambios de Iluminación — Técnicas Avanzadas

## El problema real en competencia

En WRO, el robot se calibra en la sala de práctica a las 9am con luz natural, pero la ronda es a las 3pm bajo lámparas fluorescentes. O peor: la mesa de competencia está al lado de una ventana y una mitad tiene sol directo. Los equipos novatos recalibran cada ronda. Los equipos ganadores usan técnicas que hacen que sus lecturas sean **inmunes a la iluminación**.

## Estrategia 1: Cromaticidad normalizada (RGB normalizado)

### La idea matemática

Cuando la luz cambia, los valores R, G, B cambian proporcionalmente. Si la luz es el doble de fuerte, R, G y B se duplican. Pero si dividimos cada canal por la suma total, eliminamos ese factor:

```
r' = R / (R + G + B)
g' = G / (R + G + B)
b' = B / (R + G + B)
```

Estos valores `r', g', b'` se llaman **cromaticidad** y son prácticamente constantes ante cambios de iluminación porque el factor de escala se cancela al dividir.

### Ejemplo numérico

```
Pieza ROJA en sala oscura:   R=80,  G=15, B=10  → sum=105 → r'=0.76, g'=0.14, b'=0.10
Pieza ROJA bajo lámpara:     R=200, G=38, B=25  → sum=263 → r'=0.76, g'=0.14, b'=0.10
Pieza ROJA con sol directo:  R=350, G=65, B=44  → sum=459 → r'=0.76, g'=0.14, b'=0.10

¡Los tres dan la MISMA cromaticidad!
```

### Implementación en Pybricks

Pybricks no expone RGB directamente en su API pública, pero podemos **convertir HSV a RGB** para aplicar la normalización:

```python
def hsv_a_rgb(h, s, v):
    """
    Convierte HSV (Pybricks format: h=0-359, s=0-100, v=0-100)
    a RGB (0-255).
    """
    s_f = s / 100.0
    v_f = v / 100.0
    
    c = v_f * s_f
    h_sector = h / 60.0
    x = c * (1 - abs(h_sector % 2 - 1))
    m = v_f - c
    
    if h_sector < 1:
        r, g, b = c, x, 0
    elif h_sector < 2:
        r, g, b = x, c, 0
    elif h_sector < 3:
        r, g, b = 0, c, x
    elif h_sector < 4:
        r, g, b = 0, x, c
    elif h_sector < 5:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


def cromaticidad(sensor):
    """
    Lee el sensor y retorna cromaticidad normalizada (r', g', b').
    Estos valores son inmunes a cambios de iluminación.
    Cada valor está entre 0.0 y 1.0 y los tres suman 1.0.
    """
    hsv = sensor.hsv()
    r, g, b = hsv_a_rgb(hsv.h, hsv.s, hsv.v)
    
    total = r + g + b
    if total == 0:
        return 0.33, 0.33, 0.33  # Negro total → sin info de color
    
    return r / total, g / total, b / total
```

### Clasificador por cromaticidad

```python
import math

# Colores de referencia en cromaticidad (CALIBRAR con tu sensor)
CROMATICIDAD_REF = {
    "ROJO":     (0.76, 0.14, 0.10),
    "AZUL":     (0.12, 0.18, 0.70),
    "VERDE":    (0.15, 0.65, 0.20),
    "AMARILLO": (0.52, 0.40, 0.08),
}

def distancia_crom(c1, c2):
    """Distancia euclidiana entre dos cromaticidades."""
    return math.sqrt(
        (c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2
    )

def clasificar_por_cromaticidad(sensor, umbral=0.15):
    """
    Clasifica el color usando cromaticidad normalizada.
    Inmune a cambios de iluminación.
    
    umbral: distancia máxima para aceptar un color (0.15 es típico).
    Valores más bajos = más estricto.
    """
    cr, cg, cb = cromaticidad(sensor)
    
    mejor_nombre = "DESCONOCIDO"
    mejor_dist = 9999
    
    for nombre, ref in CROMATICIDAD_REF.items():
        d = distancia_crom((cr, cg, cb), ref)
        if d < mejor_dist and d < umbral:
            mejor_dist = d
            mejor_nombre = nombre
    
    return mejor_nombre, (cr, cg, cb)
```

### Limitaciones de la cromaticidad

- **No distingue blanco de negro** (ambos tienen cromaticidad ~(0.33, 0.33, 0.33))
- **No funciona en negro total** (R+G+B = 0, división por cero)
- **Colores pastel** (baja saturación) tienen cromaticidad cercana a gris

**Solución:** Usar cromaticidad para colores cromáticos (rojo, azul, verde, amarillo) y el valor V directo para distinguir blanco/negro.

---

## Estrategia 2: HSV con descarte inteligente de V

Esta es la estrategia más simple y práctica para Pybricks.

### La idea

V (brillo) es lo que más cambia con la iluminación. Si lo ignoramos para colores cromáticos y solo lo usamos para blanco/negro, somos inmunes.

```python
def clasificar_inmune(sensor, colores_ref):
    """
    Clasificador que ignora V para colores cromáticos
    y solo usa V para blanco/negro.
    
    colores_ref: lista de (nombre, h, s, v, es_cromatico)
    """
    hsv = sensor.hsv()
    h, s, v = hsv.h, hsv.s, hsv.v
    
    # Paso 1: ¿Es acromático? (blanco, negro, gris)
    if s < 20:
        if v > 60:
            return "BLANCO"
        elif v < 15:
            return "NEGRO"
        else:
            return "GRIS"
    
    # Paso 2: Es cromático → clasificar SOLO por H y S (ignorar V)
    mejor = "DESCONOCIDO"
    mejor_d = 9999
    
    for nombre, ch, cs, cv, es_crom in colores_ref:
        if not es_crom:
            continue
        # Solo usar H y S, NO V
        dh = min(abs(h - ch), 360 - abs(h - ch))  # Circular
        ds = abs(s - cs)
        d = dh * 2.0 + ds * 1.0  # H pesa más
        if d < mejor_d:
            mejor_d = d
            mejor = nombre
    
    return mejor

# Ejemplo de uso
MIS_COLORES = [
    # (nombre,  H,   S,   V,  es_cromatico)
    ("ROJO",   355, 82,  45, True),
    ("AZUL",   218, 85,  50, True),
    ("VERDE",  140, 70,  35, True),
    ("AMARILLO",55, 65,  90, True),
    ("BLANCO",  0,   5,  95, False),
    ("NEGRO",   0,   5,   8, False),
]
```

### ¿Por qué funciona?

Cuando la iluminación cambia:
- **H** (tono): casi no cambia → lo usamos como discriminador principal
- **S** (saturación): cambia un poco (baja en salas oscuras, sube con luz directa) → lo usamos con peso medio
- **V** (brillo): cambia MUCHO → lo ignoramos para colores cromáticos

---

## Estrategia 3: Calibración adaptativa rápida con muestra de referencia

Los mejores equipos llevan una **pieza LEGO blanca de referencia** pegada al robot donde el sensor la puede leer.

### La idea

Antes de cada lectura importante, el robot lee la pieza blanca de referencia. Esto le dice "cuánta luz hay ahora". Luego normaliza la lectura del objeto relativa a la referencia.

```python
def calibrar_referencia(sensor, robot):
    """
    Lee la pieza blanca de referencia montada en el robot.
    Retorna el V de referencia.
    """
    # Mover sensor a posición de referencia (girar brazo, etc.)
    # O simplemente leer el piso blanco del tapete
    robot.stop()
    wait(200)
    ref_v = sensor.hsv().v
    return ref_v

def leer_normalizado(sensor, ref_v):
    """
    Lee color normalizado relativo a la referencia.
    Si ref_v era 80 y ahora leo V=40, el factor es 80/40=2.0
    → la iluminación bajó a la mitad.
    """
    hsv = sensor.hsv()
    
    if ref_v > 0 and hsv.v > 0:
        factor = ref_v / hsv.v  # Solo informativo, no modificamos H
    
    # H no necesita normalización (ya es inmune)
    # S normalizamos ligeramente
    s_norm = min(100, int(hsv.s * (80 / max(ref_v, 1))))
    
    return hsv.h, s_norm, hsv.v
```

### Cuándo usar esta técnica

- Cuando el robot tiene que leer colores en **diferentes zonas** del tapete con iluminación diferente
- Cuando las rondas son a **diferentes horas** y la luz natural cambia
- Cuando hay **sombras parciales** en el tapete

---

## Estrategia 4: Lectura múltiple con rechazo de outliers

En vez de promediar todas las lecturas, descartamos las que son muy diferentes (probablemente causadas por ruido o transiciones).

```python
def leer_con_rechazo(sensor, n=7, descartar=2):
    """
    Toma N lecturas, descarta las 'descartar' más extremas
    de cada lado, y promedia el resto.
    
    Con n=7, descartar=2: toma 7, descarta las 2 más altas
    y 2 más bajas, promedia las 3 del medio.
    """
    lecturas_h = []
    lecturas_s = []
    lecturas_v = []
    
    for i in range(n):
        hsv = sensor.hsv()
        lecturas_h.append(hsv.h)
        lecturas_s.append(hsv.s)
        lecturas_v.append(hsv.v)
        wait(30)
    
    # Ordenar y descartar extremos
    lecturas_s.sort()
    lecturas_v.sort()
    
    # Hue necesita tratamiento especial (circular)
    # Para simplificar, usamos la mediana
    lecturas_h.sort()
    h_mediana = lecturas_h[n // 2]
    
    centro = slice(descartar, n - descartar)
    s_avg = sum(lecturas_s[centro]) // (n - 2 * descartar)
    v_avg = sum(lecturas_v[centro]) // (n - 2 * descartar)
    
    return h_mediana, s_avg, v_avg
```

---

## Estrategia 5: Clasificación combinada (la más robusta)

Combinar las estrategias anteriores en un solo clasificador:

```python
import math

def clasificar_robusto(sensor, robot, colores_ref, n_lecturas=5):
    """
    Clasificador máximo nivel: combina múltiples técnicas.
    
    1. Para el robot y estabiliza
    2. Toma N lecturas con rechazo de outliers
    3. Separa cromáticos de acromáticos por S
    4. Para cromáticos: compara por H (inmune a luz)
    5. Para acromáticos: compara por V
    6. Retorna nombre + confianza
    """
    robot.stop()
    wait(200)
    
    # Tomar lecturas con rechazo
    lecturas = []
    for i in range(n_lecturas + 2):  # +2 para descartar
        hsv = sensor.hsv()
        lecturas.append((hsv.h, hsv.s, hsv.v))
        wait(40)
    
    # Descartar extremos por V (el más variable)
    lecturas.sort(key=lambda x: x[2])
    lecturas = lecturas[1:-1]  # Sacar el más oscuro y más brillante
    
    # Promediar
    avg_h = lecturas[len(lecturas)//2][0]  # Mediana para H
    avg_s = sum(l[1] for l in lecturas) // len(lecturas)
    avg_v = sum(l[2] for l in lecturas) // len(lecturas)
    
    # ¿Es acromático?
    if avg_s < 20:
        if avg_v > 60:
            return "BLANCO", 90
        elif avg_v < 15:
            return "NEGRO", 90
        else:
            return "GRIS", 70
    
    # Cromático: clasificar por H con peso alto, S medio, V bajo
    mejor = "DESCONOCIDO"
    mejor_d = 9999
    
    for nombre, ch, cs, cv, es_crom in colores_ref:
        if not es_crom:
            continue
        dh = min(abs(avg_h - ch), 360 - abs(avg_h - ch))
        ds = abs(avg_s - cs)
        d = dh * 2.5 + ds * 0.5  # H domina
        if d < mejor_d:
            mejor_d = d
            mejor = nombre
    
    # Confianza: inversa de la distancia (0-100)
    confianza = max(0, min(100, int(100 - mejor_d)))
    
    return mejor, confianza
```

---

## Posicionamiento del sensor: guía definitiva

### Para leer colores del PISO (líneas, zonas de color)

```
  Vista lateral del robot:
  
  ┌──────────┐
  │  ROBOT   │
  │          │
  └──────────┘
     │ Sensor apuntando recto hacia abajo
     ○
     │
     │ 5-12mm (distancia óptima)
  ═════════════  ← Piso / tapete
```

**Distancia óptima: 5-12mm del piso**

| Distancia | Resultado | Uso |
|-----------|-----------|-----|
| < 5mm | Sensor satura, V siempre ~100, S baja | NO usar |
| 5-8mm | Lectura fuerte, punto de luz pequeño (~8mm) | Para líneas finas |
| 8-12mm | Lectura balanceada, punto ~12mm | Óptimo para colores de piso |
| 12-16mm | Lectura más débil pero aún confiable | Aceptable |
| > 20mm | S y V bajan, H ruidoso | NO confiable |

**Cono de visión:** A 10mm del piso, el sensor "ve" un área de ~10-12mm de diámetro. A 20mm ve ~20mm de diámetro. Esto importa porque si el área es más grande que la zona de color, lee una mezcla.

### Para leer colores de OBJETOS (cubos, piezas LEGO)

```
  Vista lateral:
  
  ┌──────────┐
  │  ROBOT   │
  │      ○──────  Sensor apuntando al frente
  │          │      8-16mm 
  └──────────┘     ┌───┐
                       │OBJ│  ← Objeto de color
  ═══════════════════════  ← Piso
```

**Distancia óptima al objeto: 8-16mm**

**Altura del sensor desde el piso:** Depende del tamaño del objeto.

| Objeto | Altura objeto | Altura sensor desde piso | Por qué |
|--------|--------------|--------------------------|--------|
| Cubo LEGO 2x2 | 19mm | 10-15mm | Centro del objeto |
| Cubo LEGO 2x4 | 19mm | 10-15mm | Centro del objeto |
| Pieza alta (3 bricks) | 29mm | 15-20mm | Centro del objeto |
| Bola | ~24mm diámetro | 12-16mm | Ecuadory |
| Marcador en piso | 0mm | 5-12mm | Como lectura de piso |

### El problema de la contaminación por el piso

```
  PROBLEMA: Sensor demasiado bajo, ve PISO + OBJETO mezclado
  
  ○ Sensor bajo (5mm del piso)                
  │\
  │ \  Cono de visión amplio
  │  \
  ════███════  El sensor ve el piso ROJO + objeto AZUL
      │OBJ│     Resultado: ¡DESCONOCIDO! (mezcla de colores)
  
  SOLUCIÓN: Sensor a la altura del CENTRO del objeto
  
      ○ Sensor a 12mm del piso
      │\
      │ \ Cono estrecho
      ███   Solo ve el OBJETO
      │OBJ│
  ═════════  El piso queda FUERA del cono
```

### Regla práctica: el sensor debe estar a la altura del CENTRO del objeto

Si el objeto mide 20mm de alto, el sensor debe estar a ~10mm del piso. Así el cono de visión apunta al centro del objeto y el piso queda fuera.

### El truco del escudo anti-piso

Si no podés poner el sensor a la altura exacta, poné piezas LEGO debajo del sensor formando una "pantalla" que bloquea la visión del piso:

```
  ○ Sensor
  │
  █ Pantalla negra (piezas LEGO Technic)
  │
  ███  Solo ve el objeto
  │OBJ│
  ══════
```

### Dos sensores: uno para piso, otro para objetos

Los equipos más exitosos usan **sensores dedicados**:
- **Sensor D** (apuntando abajo, 8mm del piso): para seguir líneas y leer zonas del tapete
- **Sensor E** (apuntando al frente, a 12mm del piso): para leer objetos

Nunca mezclan funciones. Cada sensor está optimizado para SU tarea.

---

## Resumen de estrategias de inmunización

| Estrategia | Inmunidad | Complejidad | Mejor para |
|-----------|-----------|-------------|------------|
| HSV H-only (ignorar V) | ⭐⭐⭐⭐ Alta | ⭐ Baja | Colores cromáticos básicos |
| Cromaticidad RGB normalizada | ⭐⭐⭐⭐⭐ Muy alta | ⭐⭐ Media | Cuando hay cambios de luz fuertes |
| Calibración adaptativa (referencia blanca) | ⭐⭐⭐⭐ Alta | ⭐⭐ Media | Zonas con iluminación variable |
| Lectura con rechazo de outliers | ⭐⭐⭐ Media | ⭐ Baja | Lecturas ruidosas |
| Tubo oscuro físico | ⭐⭐⭐⭐⭐ Muy alta | ⭐ Nula (hardware) | SIEMPRE recomendado |
| Sensor a altura de objeto | ⭐⭐⭐⭐⭐ Elimina contaminación | ⭐ Hardware | Lectura de objetos |

### Recomendación para IITA

**Nivel básico (empezar acá):**
1. Tubo oscuro alrededor del sensor
2. `detectable_colors()` con HSV calibrado
3. Protocolo parar-esperar-leer

**Nivel avanzado (para clasificaciones difíciles):**
1. Todo lo anterior +
2. Clasificador H-only para cromáticos, V para blanco/negro
3. Rechazo de outliers (7 lecturas, descartar 2 extremos)

**Nivel competitivo (para WRO Internacional):**
1. Todo lo anterior +
2. Cromaticidad normalizada para los colores críticos
3. Calibración adaptativa con referencia blanca
4. Sensor dedicado para objetos a la altura correcta
