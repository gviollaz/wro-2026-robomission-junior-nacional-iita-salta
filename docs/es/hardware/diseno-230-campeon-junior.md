# Diseño para 230/230 — Heritage Heroes WRO Junior 2026

## Análisis con mentalidad de campeón mundial

> Junior es donde WRO se pone serio. Las torres amarillas que hay que **apilar** (poner el techo sobre la base) valen 50 puntos y son el desafío mecánico más difícil de la temporada 2026. Los equipos que resuelvan el apilado consistente ganan. Los que no, se quedan en 130 puntos.

---

## 1. Desglose del juego: 230 puntos posibles

### Scoring completo

| # | Misión | Pts máx | Objetos | Desafío clave |
|---|--------|---------|---------|---------------|
| 3.1 | Visitantes a zonas de color | 40 | 4 visitantes → 4 zonas (verde, rojo, negro, azul) | Transporte a múltiples destinos dispersos por el campo |
| 3.2a | Torres rojas en target | 30 | 2 torres rojas → 2 áreas rojas (esquina sup-izq → derecha) | Transporte de objetos altos, deben quedar parados |
| 3.2b | Torres amarillas (apilar) | **50** | 2 techos amarillos → sobre 2 bases amarillas | **APILAR techo sobre base. El desafío definitorio.** |
| 3.3 | Artefactos al museo | 60 | 4 de 5 artefactos (aleatorio) → spots de color en museo | Detección de color + transporte, 4 aleatorios de 5 posibles |
| 3.4 | Limpiar adoquines | 20 | 10 partículas negras aleatorias → fuera del cobblestone | Barrido de área, partículas pequeñas dispersas |
| 3.5 | Bonus (no tocar) | 30 | 2 barreras + 1 loro → no mover ni dañar | Ruta limpia |
| | **TOTAL** | **230** | | |

### Análisis de retorno por esfuerzo

| Misión | Pts | Complejidad mecánica | Complejidad software | Retorno |
|--------|-----|---------------------|---------------------|---------|
| Bonus (no tocar) | 30 | Nula | Media (ruta limpia) | ⭐⭐⭐⭐⭐ |
| Visitantes | 40 | Baja (empujar/llevar) | Media (4 destinos) | ⭐⭐⭐⭐ |
| Limpiar adoquines | 20 | Baja (barrer) | Baja-Media | ⭐⭐⭐⭐ |
| Torres rojas | 30 | Media (transportar vertical) | Media | ⭐⭐⭐ |
| Artefactos museo | 60 | Media (agarrar+detectar color) | Alta (aleatorio) | ⭐⭐⭐ |
| **Torres amarillas** | **50** | **MUY ALTA (apilar)** | **Alta** | ⭐⭐ |

---

## 2. El problema central: apilar las torres amarillas

Las torres amarillas valen **50 puntos** (25 cada una) y son el factor decisivo. El robot debe:

1. Recoger el techo amarillo (esquina superior izquierda del campo)
2. Transportarlo al otro lado del campo (zona derecha)
3. Colocarlo **encima** de la base amarilla que ya está en su target area
4. La base NO debe moverse de su posición al poner el techo
5. El conjunto torre+techo debe quedar **vertical** y **completamente adentro** del área

### ¿Por qué es tan difícil?

- La base es un objeto pequeño LEGO (~3-4 studs). Poner algo encima requiere alineación de ±2mm.
- Si el robot empuja la base al depositar el techo, la base se sale del área y pierde puntos.
- El techo debe encajar (no solo apoyarse), lo que requiere alineación vertical precisa.
- Hay 2 torres, en posiciones diferentes, con bases en posiciones potencialmente apretadas.

### Las 3 filosofías de apilado

**Filosofía A: Apilado desde arriba (top-down)**
El brazo levanta el techo alto por encima de la base y lo baja verticalmente hasta que encaje.

Requiere: brazo largo con recorrido vertical amplio, alineación XY precisa, sensor de posición o dead-reckoning perfecto.

**Filosofía B: Apilado por deslizamiento (slide-on)**
El robot se acerca a la base desde un lado, el techo viene "empujado" horizontalmente y un mecanismo lo guía para que se deslice sobre la base.

Requiere: geometría del mecanismo que guíe el techo, la base tiene que tener una forma que lo permita.

**Filosofía C: Apilado por posicionamiento secuencial**
El robot primero reposiciona la base (si necesario), luego coloca el techo al lado, y después usa un mecanismo para empujar el techo sobre la base.

Requiere: mecanismo de dos etapas, más tiempo pero más controlable.

---

## 3. Restricciones Junior 2026

| Restricción | Valor |
|-------------|-------|
| Tamaño inicio | 25×25×25 cm |
| Peso | 1500 g |
| Motores | **5** (1 más que Elementary) |
| Sensores | Sin límite de cantidad |
| Cámaras | **✅ Permitidas en Junior** |
| Controladores | 1 |
| Tiempo por ronda | 2 minutos |

El motor extra y la posibilidad de cámara son ventajas significativas sobre Elementary.

---

## 4. Tres diseños de robot campeón mundial

### DISEÑO α: "El Arquitecto" — Especialista en apilado

> Filosofía: Resolver el problema más difícil primero. Si el apilado funciona, todo lo demás es fácil.

**Distribución de 5 motores:**

| Motor | Puerto | Función |
|-------|--------|---------|
| A | Tracción izquierda | Motor Grande |
| B | Tracción derecha | Motor Grande |
| C | Garra (abrir/cerrar) | Motor Mediano |
| D | Brazo vertical (subir/bajar) | Motor Mediano, reducción 5:1 |
| E | Mecanismo de alineación fino | Motor Mediano, recorrido corto |

**Concepto mecánico:**

```
Vista lateral:

    ┌─[Motor E: ajuste fino lateral]
    │
    ├─[Motor D: brazo vertical, 5:1 reducción]
    │    │
    │    └──[Motor C: garra]
    │         │
    │    ┌────┴────┐
    │    │  OBJETO │  ← Puede levantar hasta 15cm
    │    └─────────┘
    │
  ┌─┤──────────────┐
  │ │  SPIKE HUB   │
  │ └──────────────┘
  │ [A]──⊙──[B]
  └──◎ rueda loca
```

El Motor E es el diferenciador: un mecanismo de ajuste lateral de ±10mm que permite micro-correcciones de posición cuando el brazo está arriba. Esto resuelve el problema de alineación del apilado.

**Secuencia de apilado:**
1. Navegar a la base amarilla con gyro (posición conocida)
2. Alinear usando sensor de color del piso (detectar el borde del área target)
3. Brazo sube el techo a posición ALTA (15cm)
4. Motor E ajusta posición lateral si es necesario
5. Brazo baja LENTO (50°/s) hasta que el techo toque la base
6. Garra abre LENTO → techo queda sobre base
7. Retroceder sin tocar

**Sensores:**
- Puerto E: Color sensor PISO (8mm, para líneas y zonas)
- Puerto F: Color sensor OBJETOS (en el brazo, para artefactos)
- Gyro del hub (para navegación precisa)

**Fortalezas:** El mejor para los 50 puntos de torres amarillas. El mecanismo de ajuste fino es el secreto que los otros diseños no tienen.

**Debilidades:** El motor extra para ajuste fino deja menos flexibilidad mecánica. La limpieza de adoquines requiere una solución pasiva (empujador frontal).

**Puntaje esperado:** 210-230 (excelente en torres, bueno en todo lo demás)

---

### DISEÑO β: "El Barrendero" — Máxima cobertura del campo

> Filosofía: Hacer muchas misiones parciales es mejor que pocas misiones perfectas. Cubrir todo el campo eficientemente.

**Distribución de 5 motores:**

| Motor | Puerto | Función |
|-------|--------|---------|
| A | Tracción izquierda | Motor Grande |
| B | Tracción derecha | Motor Grande |
| C | Garra frontal (abrir/cerrar) | Motor Mediano |
| D | Brazo elevador | Motor Mediano, reducción 3:1 |
| E | Pala/barredor trasero (sube/baja) | Motor Mediano |

**Concepto mecánico:**

```
Vista superior:

         ┌──GARRA──┐  ← Frente: agarra objetos
         │ [Motor C]│
    ┌────┴─────────┴────┐
    │   SPIKE HUB       │
    │   [Motor D: brazo]│
    │                   │
    │  [A]──⊙──[B]     │
    └───────┬───────────┘
            │
    ┌───────┴───────┐
    │  PALA BARRER  │  ← Atrás: barre partículas de suciedad
    │  [Motor E]    │     Se baja al pasar por los adoquines
    └───────────────┘
```

El robot tiene **dos herramientas**: garra frontal para objetos y pala trasera para barrer. La pala se baja cuando pasa por los adoquines y empuja las 10 partículas de suciedad fuera del área.

**Estrategia de ruta:**
1. Arrancar → barrer adoquines en el camino hacia las torres (mata 2 pájaros de un viaje)
2. Llevar torres rojas a sus targets
3. Recoger techos amarillos → apilar sobre bases
4. Barrer el resto de suciedad al volver
5. Recoger artefactos → museo
6. Llevar visitantes a sus zonas

**Sensores:**
- Puerto E: Color PISO
- Puerto F: Color OBJETOS (en brazo)
- Opcionalmente: cámara vía LMS-ESP32 para detección de artefactos

**Fortalezas:** La pala trasera limpia 20 puntos de suciedad "gratis" mientras hace otras misiones. Cubre todo el campo eficientemente.

**Debilidades:** El apilado de torres amarillas no tiene el ajuste fino del Diseño α. Depende más de la precisión de navegación.

**Puntaje esperado:** 190-220 (muy bueno en cobertura total, regular en apilado)

---

### DISEÑO γ: "El Visionario" — Cámara + máxima inteligencia

> Filosofía: Usar la cámara (permitida en Junior) para ver el campo, identificar objetos, y tomar decisiones en tiempo real. El robot más inteligente, no el más mecánico.

**Distribución de 5 motores:**

| Motor | Puerto | Función |
|-------|--------|---------|
| A | Tracción izquierda | Motor Grande |
| B | Tracción derecha | Motor Grande |
| C | Garra universal (abrir/cerrar) | Motor Mediano |
| D | Brazo elevador (4 posiciones) | Motor Mediano, reducción 3:1 |
| E | Empujador/barrendero plegable | Motor Mediano |

**Hardware adicional:**
- LMS-ESP32 + HuskyLens (o OpenMV) en Puerto F
- Sensor Color piso en Puerto E

**Concepto mecánico:**

```
Vista lateral:

  [CÁMARA HuskyLens/OpenMV]  ← Montada arriba, mira hacia adelante-abajo
        │                        Ve artefactos, torres, visitantes, suciedad
  ┌─────┤ [Motor D: brazo]
  │     └──[Motor C: garra]
  │
  │  ┌──────────────┐
  │  │  SPIKE HUB   │
  │  │  + LMS-ESP32 │  ← Conectada en Puerto F
  │  └──────────────┘
  │  [A]──⊙──[B]
  │
  └──[Motor E: empujador plegable trasero]
```

**La ventaja de la cámara:**

Sin cámara, el robot tiene que ir a CADA artefacto y leer su color con el sensor a 15mm. Con cámara, el robot ve los 4 artefactos desde lejos y sabe cuáles son ANTES de llegar. Esto ahorra 10-15 segundos y permite planificar la ruta óptima.

Además, la cámara puede:
- Ver si la suciedad ya fue barrida (no perder tiempo en zonas limpias)
- Verificar que las torres quedaron bien después de depositarlas
- Detectar si un visitante se cayó al transportarlo
- Ajustar la aproximación a un objeto viendo su posición exacta

**Sensores:**
- Puerto E: Sensor Color PISO
- Puerto F: LMS-ESP32 → HuskyLens/OpenMV (PUPRemote)
- Gyro del hub

**Estrategia de ruta con visión:**
1. Arrancar → cámara escanea el campo mientras se mueve
2. Identificar colores de artefactos AL PASAR (sin detenerse)
3. Planificar ruta óptima considerando posiciones reales de objetos
4. Ejecutar misiones en orden optimizado por cercanía
5. Verificar cada depósito con la cámara

**Fortalezas:** El robot más inteligente. Ahorra tiempo en detección, puede adaptarse a errores, y la cámara da una ventaja enorme en los artefactos aleatorios.

**Debilidades:** Complejidad de integración (LMS-ESP32 + cámara + Pybricks). Si la cámara falla, necesita fallback al sensor de color. El apilado de torres sigue siendo mecánico.

**Puntaje esperado:** 200-230 (excelente en artefactos y eficiencia de ruta, depende de fiabilidad de cámara)

---

## 5. Comparativa de los 3 diseños

| Aspecto | α El Arquitecto | β El Barrendero | γ El Visionario |
|---------|----------------|-----------------|-----------------|
| Torres amarillas (50 pts) | ⭐⭐⭐⭐⭐ Ajuste fino | ⭐⭐⭐ Sin ajuste | ⭐⭐⭐ Sin ajuste |
| Torres rojas (30 pts) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Visitantes (40 pts) | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Artefactos (60 pts) | ⭐⭐⭐ Sensor color | ⭐⭐⭐ Sensor color | ⭐⭐⭐⭐⭐ Cámara ve todo |
| Suciedad (20 pts) | ⭐⭐ Pasivo/empujar | ⭐⭐⭐⭐⭐ Pala dedicada | ⭐⭐⭐ Empujador plegable |
| Bonus (30 pts) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Complejidad mecánica | ⭐⭐⭐⭐⭐ Muy alta | ⭐⭐⭐ Media | ⭐⭐⭐⭐ Alta |
| Complejidad software | ⭐⭐⭐ Media | ⭐⭐⭐ Media | ⭐⭐⭐⭐⭐ Muy alta |
| Fiabilidad esperada | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Techo de puntos | 230 | 220 | 230 |
| Piso de puntos (peor caso) | 150 | 160 | 130 |

### Recomendación para IITA

**Si el equipo tiene buen nivel mecánico:** Diseño α (El Arquitecto). Los 50 puntos de torres amarillas son la diferencia entre ganar y perder a nivel internacional.

**Si el equipo quiere máxima confiabilidad:** Diseño β (El Barrendero). La pala trasera es genial porque limpia 20 puntos de suciedad sin esfuerzo extra mientras hace otras misiones.

**Si el equipo tiene experiencia en programación y hardware extra:** Diseño γ (El Visionario). La cámara es una ventaja enorme pero requiere semanas de integración.

**La combinación campeona: α + elementos de β** — El mecanismo de ajuste fino del Arquitecto con la pala plegable del Barrendero (reemplazando el Motor E por un mecanismo pasivo de barrido que se pliega con un solo motor que también hace el ajuste fino cuando no barre).

---

## 6. Misión por misión: cómo lograr puntaje máximo

### 3.1 Visitantes (40 pts)

Los 4 visitantes están en la calle (esquina inferior izquierda). Van a 4 destinos dispersos:
- Verde → excavación (abajo)
- Rojo → museo (arriba)
- Negro → cobblestone (negro, arriba del cobblestone)
- Azul → cobblestone (azul, abajo del cobblestone)

**Estrategia:** Los visitantes son relativamente simples de transportar. La clave es hacerlo EN EL CAMINO hacia otras misiones, no como viaje dedicado. Al ir a buscar techos amarillos (arriba-izquierda), llevar el visitante rojo al museo (arriba). Al ir a los adoquines, llevar negro y azul. Al volver al inicio, llevar verde a excavación.

### 3.2 Torres (80 pts total)

**Torres rojas (30 pts):** Están arriba-izquierda, van a la derecha. Son objetos altos que deben quedar parados. Similar a los cables del Elementary — la garra las agarra, el brazo las levanta, las deposita vertical.

**Torres amarillas (50 pts):** El desafío definitorio. El robot recoge el techo (arriba-izquierda), lo lleva al otro lado del campo, y lo apila sobre la base. El secreto del puntaje máximo está acá.

### 3.3 Artefactos (60 pts)

5 artefactos posibles, 4 en el campo por ronda (1 se descarta aleatoriamente). Los colores son azul, rojo, verde, negro, amarillo. Van a spots de color correspondiente en el museo.

**Randomización:** De los 5 artefactos posibles, solo 4 están en el campo. El robot necesita:
1. Detectar cuáles 4 están presentes (y cuál falta)
2. Leer el color de cada uno
3. Llevar cada uno al spot correcto

**Con cámara (Diseño γ):** Escaneo visual de los 4 artefactos en segundos.
**Sin cámara:** Ir a cada posición, leer con sensor de color, llevar al destino. 4 viajes.

### 3.4 Suciedad (20 pts)

10 partículas negras pequeñas distribuidas aleatoriamente en el área de adoquines. El robot debe sacarlas del cobblestone.

**Estrategia elegante:** Un empujador ancho (pala) que barre TODA el área de adoquines en 2-3 pasadas. No necesita agarrar partículas individuales — las empuja fuera del área marrón. Las líneas que delimitan las zonas de visitantes NO son parte del cobblestone, así que las partículas pueden terminar ahí.

### 3.5 Bonus (30 pts)

2 barreras y 1 loro. Si el robot no los toca, son 30 puntos gratis. Están en el lado derecho del campo (zona de adoquines). La ruta del robot debe pasar LEJOS de estos objetos.

---

## 7. Presupuesto de tiempo para 230 pts

| Viaje | Acciones | Tiempo est. |
|-------|----------|-------------|
| 1 | Start → visitantes → llevar verde a excavación + rojo hacia museo | 15s |
| 2 | Recoger techo amarillo 1 + torre roja 1 → depositar torre roja → apilar techo sobre base 1 | 20s |
| 3 | Recoger techo amarillo 2 + torre roja 2 → depositar torre roja → apilar techo sobre base 2 | 20s |
| 4 | Barrer adoquines (2-3 pasadas con pala) + llevar visitantes negro y azul | 18s |
| 5 | Escanear artefactos → recoger 2 artefactos → museo | 18s |
| 6 | Recoger 2 artefactos restantes → museo | 15s |
| 7 | Retorno seguro (evitar bonus objects) | 5s |
| **Total** | | **111s** ✅ |
| **Margen** | | **9s** |

Apretado pero factible. El apilado de torres (viajes 2-3) es lo que más tiempo consume porque requiere precisión.

---

## 8. Robustez mecánica específica para Junior

### Principio #1: El apilado requiere repetibilidad mecánica perfecta

El mecanismo de apilado se prueba **50 veces** antes de considerarlo listo. Si falla más de 2 de 50, hay que rediseñar. No ajustar el software — el problema es mecánico.

### Principio #2: Reducción de engranajes en el brazo

Para el apilado, el brazo necesita bajar el techo LENTO y controlado. Un Motor Mediano sin reducción gira muy rápido incluso a baja velocidad. Con reducción 5:1, el movimiento es suave y preciso.

### Principio #3: Garra con "dedos" largos para objetos variados

Los objetos de este juego son muy variados: visitantes (pequeños), torres (altos y cilíndricos), artefactos (medianos con base), techos (forma irregular). La garra necesita dedos largos (~40mm) que se adapten a todas estas formas.

### Principio #4: La pala barredora debe ser más ancha que el cobblestone

El área de adoquines tiene un ancho específico. La pala debe cubrirlo en 2-3 pasadas. Calcular el ancho exacto del cobblestone y diseñar la pala para cubrir al menos 60% en una pasada.

### Principio #5: Cables internos del SPIKE protegidos

Con 5 motores + 2 sensores, hay 7 cables saliendo del hub. Organizar con clips LEGO, pasar por canales Technic, y asegurar que ninguno quede suelto donde pueda engancharse.

---

## 9. Plan de pruebas para 230

### Prueba definitoria: apilado de torres amarillas

| Prueba | Criterio | Intentos |
|--------|----------|----------|
| Apilar techo sobre base (posición ideal) | 9/10 éxitos | 10 |
| Apilar con base desplazada 3mm | 7/10 éxitos | 10 |
| Apilar con base desplazada 5mm | 5/10 éxitos | 10 |
| Apilar las 2 torres en una ronda | 8/10 rondas ambas OK | 10 |
| Apilar después de navegar 1m con el techo | 8/10 éxitos | 10 |

Si el apilado no pasa estas pruebas, NO seguir con el resto. Resolver esto primero.

### Programa completo

| Prueba | Criterio | Intentos |
|--------|----------|----------|
| Programa completo, randomización aleatoria | >200 pts promedio | 20 |
| Peor escenario (artefactos difíciles + suciedad dispersa) | >170 pts | 10 |
| Con batería al 30% | >180 pts | 5 |
| En mesa diferente | >180 pts | 5 |
| Las 5 combinaciones de artefacto faltante | >190 pts en todas | 5 |

---

## 10. Resumen ejecutivo

| Decisión | Recomendación | Justificación |
|----------|--------------|---------------|
| Diseño base | α (Arquitecto) + pala de β | Los 50 pts de torres amarillas definen el campeonato |
| Motor para apilado | Motor Mediano con reducción 5:1 | Precisión y control > velocidad |
| Cámara | Evaluar después de resolver torres | No agregar complejidad si las torres no funcionan |
| Sensor de color | 2: piso (E) + objetos (F) | Necesario para artefactos sin cámara |
| Prioridad de desarrollo | Torres → artefactos → visitantes → suciedad → bonus | Las torres primero, siempre |
| Meta de puntaje | 210+ consistente en 2 de 3 rondas | Apuntar a 230, aceptar 210 como piso |
