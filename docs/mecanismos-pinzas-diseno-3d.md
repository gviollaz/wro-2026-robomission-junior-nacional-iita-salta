# Mecanismos, Pinzas y Diseño 3D para WRO Junior 2026

## Respuestas directas a las preguntas de Gustavo

---

## 1. ¿Qué mecanismos son los más convenientes?

### Los 3 mecanismos que necesita este robot

| Mecanismo | Función en Heritage Heroes | Requisitos |
|-----------|---------------------------|------------|
| **Garra** | Agarrar visitantes, torres, artefactos, cables | Apertura variable (15-50mm), agarre firme, depósito vertical |
| **Brazo elevador** | Subir objetos para transportar, bajar para depositar, apilar torres | 3+ posiciones, velocidad variable (rápido para transporte, lento para apilado) |
| **Pala barredora** | Barrer 10 partículas de suciedad del cobblestone | Ancho ≥60mm, se pliega cuando no está en uso |

### Tipos de mecanismos de garra para competencia

**Tipo A: Pinza paralela (rack-and-pinion)**

El servo gira un engranaje central que mueve dos dedos en sentidos opuestos. Los dedos se desplazan de forma paralela (no rotan), lo que da agarre uniforme a objetos de diferentes tamaños.

```
Vista frontal:
  Abierta:          Cerrada:
  ┃      ┃         ┃    ┃
  ┃      ┃   →→    ┃[OBJ]┃
  ┃      ┃         ┃    ┃
  ┗━━━━━━┛         ┗━━━━┛
```

Ventajas: agarre paralelo, presión uniforme, fácil de imprimir en 3D.
Desventajas: recorrido limitado (~50mm máx), requiere engranajes precisos.
**Recomendación para WRO: ⭐⭐⭐⭐⭐ La mejor opción.**

**Tipo B: Pinza angular (linkage/4-bar)**

El servo rota un brazo que abre y cierra dos dedos pivotantes. Es el mecanismo más simple: un servo, dos barras, dos pivotes.

```
Vista frontal:
  Abierta:          Cerrada:
   ╲    ╱            │    │
    ╲  ╱      →→     │[OBJ]│
     ╲╱              │    │
     ●               ●
   (pivote)        (pivote)
```

Ventajas: simple de construir, tolerante a imprecisiones.
Desventajas: la presión de agarre varía con la apertura, objetos pequeños se escapan.
**Recomendación para WRO: ⭐⭐⭐⭐ Buena para prototipo rápido.**

**Tipo C: Pinza de compliance (dedos flexibles)**

Dedos impresos en TPU flexible que se deforman al cerrar. No necesitan linkage — el servo empuja una placa que comprime los dedos flexibles contra el objeto.

Ventajas: agarra objetos de cualquier forma, auto-centrado, ultra simple.
Desventajas: poca fuerza de agarre, no sirve para depositar vertical (no sujeta firme).
**Recomendación para WRO: ⭐⭐ Solo para barrer, no para agarrar.**

**Tipo D: Garra en V (converging fingers)**

Dos dedos en forma de V que al cerrarse guían el objeto al centro. Combina la auto-centrado de la compliance con la firmeza de la pinza angular.

```
Vista superior:
  Abierta:           Cerrando:          Cerrada:
   ╲         ╱        ╲       ╱          ╲   ╱
    ╲       ╱          ╲ [OBJ]╱           ╲[O]╱
     ╲     ╱            ╲    ╱             ╲╱
      ╲   ╱              ╲  ╱              V
```

Ventajas: tolerancia de ±15mm al posicionamiento (el objeto se centra solo), agarre firme.
Desventajas: los objetos muy grandes no caben, requiere diseño cuidadoso del ángulo de V.
**Recomendación para WRO: ⭐⭐⭐⭐⭐ Ideal para objetos WRO que varían en tamaño.**

### Recomendación definitiva: GARRA EN V con dedos duales (PLA + TPU)

La garra tiene dedos de PLA rígido con puntas recubiertas de TPU flexible. La geometría en V centra el objeto, el PLA da estructura, el TPU da grip. El Dynamixel XL330 con control de corriente detecta cuándo el objeto está agarrado.

---

## 2. ¿Hay pinzas que se puedan comprar?

### Pinzas comerciales compatibles con Dynamixel XL330

| Producto | Precio | Compatibilidad | ¿Para WRO? |
|----------|--------|----------------|-----------|
| **ROBOTIS FPX330-H101 Frame** | ~$5 | XL330 nativo, plastic frame | ⭐⭐⭐ Base para custom |
| **ROBOTIS FPX330-H102 Frame** | ~$5 | XL330 nativo, hinge frame | ⭐⭐⭐ Para brazo |
| Lynxmotion SES-V2 Gripper | ~$20 | Genérico (servo horn) | ⭐⭐ Demasiado grande |
| DFRobot SER0043 Micro Gripper | ~$8 | SG90 micro servo | ⭐⭐ Débil para WRO |
| **Low Cost Robot Gripper (open source)** | ~$0 (3D print) | XL330 nativo | ⭐⭐⭐⭐⭐ Custom para la misión |

### Los frames oficiales de ROBOTIS para XL330

ROBOTIS vende frames plásticos diseñados específicamente para los XL330. Son baratos (~$5 cada uno) y permiten construir articulaciones, brazos y garras modulares:

- **FPX330-H101**: Frame tipo horn (fijación radial al eje del servo)
- **FPX330-H102**: Frame tipo hinge (rotación libre en un eje)
- **FPX330-S101/S102**: Side frames para montaje lateral

**Estrategia recomendada:** Comprar los frames ROBOTIS como base estructural y diseñar los dedos de la garra en 3D impreso. Los frames dan la interfaz mecánica perfecta con el XL330, los dedos custom se optimizan para los objetos específicos de Heritage Heroes 2026.

### El proyecto "Low Cost Robot" (open source, XL330)

El proyecto de Alexander Koch (github.com/AlexanderKoch-Koch/low_cost_robot) es un brazo robótico completo basado en XL330 con **garra 3D impresa**. Los archivos STL son open source. La garra es exactamente del tipo que necesitamos: paralela, con grip tape, impresa en PLA.

Esto se puede adaptar directamente para nuestro robot WRO.

---

## 3. ¿Cómo diseñar las estructuras 3D?

### Software recomendado (de más fácil a más potente)

| Software | Precio | Curva de aprendizaje | Para qué |
|----------|--------|---------------------|----------|
| **Onshape** | Gratis (edu) | ⭐⭐⭐ Media | **Recomendado para IITA**. Cloud, colaborativo, parametric CAD |
| **Fusion 360** | Gratis (edu/hobby) | ⭐⭐⭐ Media | Simulación mecánica, CAM, renderizado |
| TinkerCAD | Gratis | ⭐ Fácil | Solo para piezas muy simples |
| FreeCAD | Gratis (open source) | ⭐⭐⭐⭐ Alta | Potente pero interfaz difícil |
| SolidWorks | ~$4000/año | ⭐⭐⭐⭐⭐ Profesional | Industria estándar, overkill para esto |
| OpenSCAD | Gratis | ⭐⭐⭐ (programadores) | CAD paramétrico por código, ideal para Claude |

### Proceso de diseño para piezas del robot WRO

**Paso 1: Medir los objetos del juego**

Antes de diseñar la garra, medir con calibre digital TODOS los objetos de Heritage Heroes:
- Visitantes: ancho, alto, profundidad de la base
- Torres rojas: diámetro, altura
- Torres amarillas: dimensiones de base y techo, tolerancia del encaje
- Artefactos: base y altura de los 5 tipos
- Partículas de suciedad: diámetro, altura

**Paso 2: Diseñar la garra alrededor de los objetos**

La garra no es un diseño genérico. Se diseña específicamente para los objetos más difíciles de agarrar. Las dimensiones internas de la garra son función directa de las dimensiones de los objetos.

**Paso 3: Prototipo rápido**

Imprimir la primera versión en PLA con baja calidad (0.3mm layer, 15% infill). Probar con los objetos reales. Iterar el diseño 3-5 veces. Solo la versión final se imprime en alta calidad.

**Paso 4: Versión final**

Imprimir en PLA+ (más resistente) o PETG (más flexible) con 0.2mm layer, 40% infill, 3 paredes. Agregar insertos metálicos M2 para los tornillos del XL330.

### Parámetros de impresión por pieza

| Pieza | Material | Layer | Infill | Paredes | Soportes |
|-------|----------|-------|--------|---------|----------|
| Chasis base | PLA+ | 0.2mm | 40% gyroid | 3 (1.2mm) | No |
| Garra dedos (cuerpo) | PLA+ | 0.2mm | 40% | 3 | Sí (en voladizos) |
| Garra puntas (grip) | TPU 95A | 0.2mm | 30% | 2 | No |
| Brazo | PETG | 0.2mm | 50% | 4 | Sí |
| Pala barredora | PLA | 0.2mm | 20% | 2 | No |
| Soporte motor | PETG | 0.15mm | 60% | 4 | Sí |
| Soporte sensor | PLA | 0.2mm | 20% | 2 | No |
| Ruedas (llanta) | PLA+ | 0.1mm | 100% | — | No |
| Ruedas (banda) | TPU 70A | 0.2mm | 100% | — | No |

---

## 4. ¿Puedo generar modelos 3D?

### Lo que SÍ puedo hacer

**Generar archivos OpenSCAD (.scad) completos y listos para fabricar.**

OpenSCAD es un lenguaje de programación para diseño 3D paramétrico. Yo escribo el código, vos lo abrís en OpenSCAD (gratis, openscad.org), lo renderizás, y exportás como STL para imprimir o enviar a fabricar.

Esto es extremadamente poderoso porque:
- El diseño es **paramétrico**: cambiás una variable (ej: ancho de garra) y todo se recalcula
- Es **reproducible**: el código es el diseño, no hay ambigüedad
- Se puede **versionar en Git**: el código .scad va al repo como cualquier otro archivo
- Puedo generar **piezas complejas** con uniones, engranajes, agujeros de montaje, etc.

**Ejemplo de lo que puedo generar:**

```scad
// Garra tipo V para WRO 2026 Heritage Heroes
// Diseñada para Dynamixel XL330-M288-T

// Parámetros (MODIFICAR según objetos reales)
garra_apertura_max = 50;    // mm
garra_largo_dedo = 40;      // mm
garra_angulo_v = 15;        // grados
xl330_shaft_d = 8;          // mm (eje de salida XL330)
xl330_mount_holes = 2.5;    // mm (tornillos M2.5)
tpu_grip_thickness = 1.5;   // mm

module dedo_garra() {
    difference() {
        // Cuerpo del dedo (PLA)
        hull() {
            translate([0,0,0]) cube([8, garra_largo_dedo, 12]);
            translate([3,garra_largo_dedo-5,0]) cube([2, 5, 12]);
        }
        // Ranura para TPU grip
        translate([0.5, 5, -0.1])
            cube([tpu_grip_thickness, garra_largo_dedo-10, 12.2]);
    }
}

module garra_completa() {
    // Dedo izquierdo (rotado por ángulo V)
    rotate([0, 0, garra_angulo_v])
        dedo_garra();
    // Dedo derecho (espejado)
    mirror([1,0,0])
        rotate([0, 0, garra_angulo_v])
            dedo_garra();
    // Base de montaje para XL330
    translate([-15, -10, 0])
        xl330_mount_plate();
}
```

### Lo que NO puedo hacer

- **Generar archivos STL directamente**: STL es un formato binario de mallas triangulares. Yo genero el código fuente (OpenSCAD) y vos exportás el STL.
- **Diseñar en Fusion 360 / SolidWorks**: estos son programas interactivos con interfaz gráfica. Yo no tengo acceso a ellos.
- **Generar archivos STEP**: requiere un kernel de modelado sólido (como OpenCASCADE). OpenSCAD sí puede exportar STEP con plugins, pero es limitado.
- **Simular resistencia mecánica**: no puedo hacer FEA (análisis de elementos finitos). Para saber si una pieza aguanta, hay que imprimir y probar.

### Workflow recomendado para IITA

```
Claude genera → .scad (código OpenSCAD paramétrico)
          ↓
Gustavo abre → OpenSCAD (gratis, openscad.org)
          ↓
Ajusta parámetros → (medidas reales de objetos WRO)
          ↓
Renderiza + exporta → .stl
          ↓
Imprime → Cura/PrusaSlicer → Impresora 3D (PLA/TPU)
```

**Alternativa para metal:** El .scad se exporta como .step (con FreeCAD) y se envía a un servicio de CNC online como SendCutSend, Xometry, o PCBWay CNC. Cortan aluminio 6061 de 2mm con tolerancia de ±0.1mm.

---

## 5. ¿Se puede fabricar en metal?

### Opciones de fabricación en metal para piezas del robot

| Método | Material | Tolerancia | Costo | Tiempo | ¿Para qué pieza? |
|--------|----------|-----------|-------|--------|------------------|
| **Corte láser 2D** | Aluminio 2mm, acero 1mm | ±0.1mm | ~$5-15/pieza | 3-5 días | Placa base del chasis |
| **CNC 3-axis** | Aluminio 6061 | ±0.05mm | ~$20-50/pieza | 5-10 días | Brackets de motor, garra |
| SLS (sinterizado láser) | Nylon PA12 | ±0.1mm | ~$10-30/pieza | 5-7 días | Piezas complejas |
| MJF (Multi Jet Fusion) | Nylon PA12 | ±0.1mm | ~$8-20/pieza | 3-5 días | Similar a SLS, más barato |

### Servicios de fabricación accesibles desde Argentina

| Servicio | Qué ofrecen | Envío a AR | Precio |
|----------|-------------|-----------|--------|
| **JLCPCB 3D Printing** | SLS, MJF, SLA, FDM | DHL ~10 días | Desde $2/pieza |
| **PCBWay CNC** | CNC aluminio, acero | DHL ~10 días | Desde $15/pieza |
| SendCutSend | Corte láser 2D, doblado | Solo USA (usar forwarding) | Desde $5/pieza |
| Xometry | CNC, 3D print, inyección | Internacional | Desde $20/pieza |
| **MercadoLibre AR** | Corte láser local, CNC local | Inmediato | Variable |

### ¿Qué piezas conviene hacer en metal?

| Pieza | ¿Metal? | Justificación |
|-------|---------|---------------|
| Placa base chasis | **Sí** (aluminio 2mm corte láser) | Rigidez máxima, 0 flexión, 20g |
| Brackets de motor | **Sí** (aluminio CNC) | Alineación perfecta del eje del motor |
| Garra dedos | **No** (PLA + TPU) | Necesita flexibilidad, iteración rápida |
| Brazo | **Quizás** (aluminio si hay presupuesto) | La rigidez del brazo mejora el apilado |
| Pala barredora | **No** (PLA) | No necesita precisión |
| Ruedas | **No** (PLA + TPU) | Necesita elasticidad para tracción |

### La placa base en aluminio: la mejora más impactante

Una placa de aluminio 6061 de 2mm cortada con láser como base del robot:
- Peso: ~35g (para 80×90mm)
- Rigidez: 10× más que PLA del mismo espesor
- Tolerancia: ±0.1mm (perfecto para alinear motores)
- Costo: ~$5-10 en JLCPCB o servicio local

Los agujeros para motores, standoffs, y sensores se cortan en el mismo proceso. El resultado es una base absolutamente plana y rígida sobre la cual se monta todo.

---

## 6. Diseño modular: montar y desmontar rápido

### Sistema de montaje rápido para competencia

En WRO, entre rondas tenés que poder reparar y ajustar rápido. El robot debe desarmarse y armarse en menos de 5 minutos.

**Principios de diseño modular:**

1. **Tornillos accesibles desde arriba**: todos los tornillos de montaje se alcanzan sin dar vuelta el robot. Usar tornillos Allen M2/M2.5 con cabeza cilíndrica.

2. **Conexiones eléctricas con conector**: cada módulo (garra, brazo, pala) se conecta con un conector JST-SH que se desconecta sin herramientas. No soldar cables directamente al módulo.

3. **Guías de posición**: pins de alineación o features geométricas que garantizan que el módulo se monta en la posición exacta. No depender de "ojo" para alinear.

4. **Módulos intercambiables**: si se rompe un dedo de la garra, se reemplaza solo el dedo (no toda la garra). Tener 2-3 dedos de repuesto impresos.

### Sistema de unión recomendado

| Unión | Uso | Herramienta |
|-------|-----|-------------|
| **Inserto metálico M2 + tornillo Allen** | Motor a chasis, PCB a chasis | Llave Allen 1.5mm |
| **Inserto metálico M2.5 + tornillo Allen** | Dynamixel a bracket | Llave Allen 2mm |
| **Snap-fit (PLA)** | Tapas de sensores, cubiertas | Sin herramienta |
| **Imanes de neodimio 3×2mm** | Pala barredora (montaje magnético) | Sin herramienta |
| **Pin de alineación + tuerca cautiva** | Brazo a chasis (posición repetible) | Llave Allen |

### Kit de herramientas para competencia

- 1× Llave Allen 1.5mm
- 1× Llave Allen 2mm
- 1× Destornillador Phillips PH0
- 1× Pinza de punta fina
- 5× Tornillos M2×8 de repuesto
- 5× Tornillos M2.5×8 de repuesto
- 2× Dedos de garra de repuesto (impresos)
- 1× Cinta adhesiva de silicona (para grip de emergencia)
- 1× Batería LiPo de repuesto (cargada)

---

## 7. Plan de acción para diseño mecánico

| Semana | Tarea | Entregable |
|--------|-------|-----------|
| 1 | Medir todos los objetos WRO 2026 con calibre | Tabla de dimensiones |
| 1 | Instalar OpenSCAD, probar con pieza simple | Cubo con agujeros impreso |
| 2 | Claude genera código garra V para XL330 | Archivo .scad paramétrico |
| 2 | Imprimir garra v1 en PLA borrador | Prueba de agarre con objetos |
| 3 | Iterar garra (v2, v3 si necesario) | Garra que agarra 10/10 |
| 3 | Claude genera brazo elevador + pala | Archivos .scad |
| 4 | Imprimir brazo y pala, probar | Mecanismos funcionando |
| 5 | Diseñar chasis base (PLA o aluminio) | Archivo para corte láser o 3D |
| 5 | Ensamblar robot completo | Robot armado |
| 6 | Probar montaje/desmontaje rápido | <5 min de desarme y rearme |
| 7+ | Iterar según pruebas de misión | Versiones mejoradas |

---

## 8. Próximo paso concreto

Si querés, puedo generar ahora mismo los archivos OpenSCAD para:

1. **Garra tipo V** con montaje para XL330, dedos parametrizados, ranura para TPU grip
2. **Brazo elevador** con montaje XL330, 3 posiciones, soporte para sensor TCS34725
3. **Bracket de motor Pololu N20** con insertos M2
4. **Placa base del chasis** en 2D (para corte láser en aluminio o impresión 3D)

Solo necesito las medidas reales de los objetos del juego WRO 2026 (de las building instructions oficiales) para dimensionar correctamente la apertura de la garra.
