> En el repo, los archivos de este paquete estan en `software/programs/` y el backup del robot en `software/robot-backups/pybricks-backup-2311/`. El ZIP para importar existe solo en la copia del disco del coach (`WRO 2026 final puerto rico/pybricks-colores-v3-2311`).

# Detector de colores v3 — robot de la final WRO 2026

Paquete para Pybricks Code. Agrega al robot **dos conjuntos de colores** para el sensor de artefactos (puerto F), cada uno con su propia calibración y su propia sensibilidad, sin cambiar lo que ya hace el programa de hoy.

> Preparado el 2026-11-23 por Gustavo Viollaz con ayuda de IA (Claude Opus 5.5), siguiendo las reglas IITA de declarar el uso de IA. Código fuente y pruebas: repo `wro-2026-robomission-junior-nacional-iita-salta`, carpeta `software/programs/`.

---

## Qué hay en la carpeta

| Archivo | Qué es |
|---|---|
| `colores.py` | El detector. Reemplaza al `colores.py` que hoy está en Pybricks Code. |
| `calibrar.py` | El calibrador. Mide **un conjunto por vez**. |
| `pruebacolores.py` | Prueba en vivo: una letra por color en la pantalla del hub. |
| `cancha.py` | Prueba de cancha: un sonido distinto por color. |
| `cancha_tareas.py` | Opcional: lo mismo que `cancha.py`, hecho con multitarea. |
| `ejemplo_colores_bloques.py` | Programa de **bloques** de ejemplo: lee una pieza de cada conjunto y la anuncia. |
| `pybricks-colores-v3-2311.zip` | Todos los `.py` de arriba juntos, para importarlos de una sola vez. |

## Qué cambia y qué no

- **`detectar_color()` sigue dando lo mismo que hoy.** En la PC se comparó con el `colores.py` del robot (backup del 23/11) en 100.000 lecturas y no hubo ni una diferencia. Los programas de la competencia (`WRO_2311_ORIGINAL` y los anteriores) **no hay que tocarlos**.
- Ahora hay **dos conjuntos**, cada uno con su función para usar desde bloques:

| Conjunto | Colores | Función para bloques | Qué devuelve |
|---|---|---|---|
| `naba` | negro, azul, blanco, amarillo | `detectar_naba` | 1 amarillo · 2 blanco · 3 azul · 4 negro · 0 nada · -1 duda |
| `rva` | rojo, verde, amarillo | `detectar_rva` | 1 amarillo · 5 rojo · 6 verde · 0 nada · -1 duda |

- Los números son **los mismos en todos lados**: el amarillo es 1 en los dos conjuntos, y 1, 2, 3, 4, 0 y -1 son los de siempre.
- `naba` es exactamente lo que hoy usa el robot (misma tabla), y es lo que contesta `detectar_color()`.
- `rva` **viene sin calibrar**: hasta hacer el paso 2, `detectar_rva()` contesta siempre -1 (duda).

---

## Paso 0 — Backup (no saltearlo)

1. En Pybricks Code: exportar todos los programas (backup en ZIP). El del 23/11 ya está en `pybricks-backup-2311.zip`, al lado de esta carpeta.
2. Importar reemplaza los archivos que se llaman igual: `colores.py`, `calibrar.py`, `pruebacolores.py` y `cancha.py`. Los programas de competencia no se tocan, porque tienen otro nombre.

## Paso 1 — Importar en Pybricks Code

- Importar `pybricks-colores-v3-2311.zip`, o los `.py` uno por uno.
- Si pregunta si reemplazar un archivo que ya existe, contestar que sí **solo para los de esta carpeta**.

## Paso 2 — Calibrar rojo / verde / amarillo

Se hace **con el robot armado como compite** (misma altura del sensor, mismo tope) y con **las piezas de ese conjunto**. Cada conjunto tiene su propia calibración: el amarillo de `rva` se mide aparte del amarillo de `naba`.

1. Abrir `calibrar.py` y dejar `PERFIL = "rva"`.
2. Correrlo. Para cada color la pantalla del hub muestra una letra: **R** rojo, **V** verde, **A** amarillo y **-** nada.
   - Apoyar la pieza como queda cuando el robot la captura y apretar una **FLECHA** (izquierda o derecha).
   - **No usar el botón central: corta el programa.**
   - Sacar la pieza, volver a apoyarla y apretar otra vez. Son 4 veces por color.
   - Para "nada", dejar el sensor sin pieza delante.
3. Al final imprime algo así:
   ```
   TABLA_RVA = (
       (5, "rojo", ...),
       ...
   )
   FIRMWARE_RVA = "4.1.3"
   ```
   Copiar esas líneas y reemplazar **las del mismo nombre** en `colores.py`.
4. Volver a correr `calibrar.py` y leer los avisos del principio. `PELIGRO` o `FALTA MEDIR` hay que resolverlos; los `ojo` son informativos.

Para recalibrar `naba`, lo mismo con `PERFIL = "naba"` (letras **A**, **B**, **Z** azul, **N** y **-**). Ojo: así se reemplaza la tabla que hoy usa el robot.

## Paso 3 — Probar

- `pruebacolores.py` con `PERFIL = "rva"`: presentar rojo, verde y amarillo y mirar la letra. **A** amarillo, **B** blanco, **Z** azul, **N** negro, **R** rojo, **V** verde, **-** nada, **?** duda.
- Lo mismo con `PERFIL = "naba"`.
- En la consola explica cada cambio: quién ganó, contra quién y por cuánto.

## Paso 4 — Usarlo desde bloques

Igual que hoy se usa `detectar_color`:

1. **Setup:** agregar un bloque de import **nuevo** con módulo `colores` y función `detectar_rva`, igual al que ya existe para `detectar_color`.
   - **No renombren el import que ya está:** en el editor, renombrar una variable la cambia en todos lados y rompería las llamadas a `detectar_color`.
2. **Función:** copiar la función "detectar y guardar color" (espera 200 ms, guarda el color en `coloractual` e imprime). Llamarla, por ejemplo, "detectar y guardar color RVA", y en su bloque de llamada elegir `detectar_rva`. La llamada es **común**, como la que ya tienen.
3. **Decisiones:** comparar `coloractual` con **5** rojo, **6** verde, **1** amarillo, **0** nada y **-1** duda.

El programa `ejemplo_colores_bloques` tiene todo esto armado y se puede mirar en el editor.

> Los nombres exactos de los menús del editor no están confirmados: los bloques se describen por cómo están guardados en los programas del equipo.

---

## El programa de ejemplo en bloques

- **Qué hace:** pide una pieza negra, azul, blanca o amarilla; la lee con `detectar_naba`; la anuncia con un texto y un pitido. Después hace lo mismo con una pieza roja, verde o amarilla y `detectar_rva`. No mueve motores.
- **Cómo correrlo:** con `colores.py` importado en el mismo Pybricks Code. Mientras `rva` no esté calibrado, la segunda lectura va a decir "duda".
- **Cómo se armó:** copiando la forma de los bloques de `WRO_2311_ORIGINAL` (import, llamada común, "si / si no si" con "0 o 4", pitidos). Se validó con un programa contra los 23 programas de bloques del equipo: todos los tipos de bloque, campos y variables son los que el editor ya usa. Su parte Python se ejecutó en un hub simulado en la PC.
- **Lo que no se hizo:** abrirlo en el editor real (en la PC no hay licencia de bloques). Por eso va después del backup. Si al abrirlo el editor hace algo raro, borrar ese programa y avisar.

## Si un color se confunde (sensibilidad)

Todo está en `colores.py`, en `PERFILES`, **dentro del conjunto que corresponde**:

- **`ventaja`** de un color: subirla de a 2 hace que ese color le gane más seguido **a los otros de su mismo conjunto**. Es lo que hay que tocar cuando un color se lee como otro.
- **radio** (último número de su fila en la tabla): subirlo hace que se acepte más seguido. Es lo que hay que tocar cuando da duda (-1) seguido sobre una pieza que sí está.
- Después de cada cambio, correr `calibrar.py` y leer los avisos: un "margen negativo" quiere decir que ese color ya no puede ganar.
- En `naba`, el par **blanco / negro** es el más sensible: cada punto de ventaja corre esa frontera mucho más que en los otros pares.

## Multitarea (para más adelante)

Hoy los programas del robot **no** usan multitarea, y por eso la llamada es "común". Si algún programa la usa:

- En bloques, la llamada a `detectar_rva` / `detectar_naba` va como llamada **async**.
- En Python, se escribe `c = await detectar_rva()`. Si se olvida el `await`, no da error: devuelve algo que nunca es un color.
- `cancha_tareas.py` muestra cómo leer el sensor en una tarea mientras otras hacen otra cosa.

## Lo que hay que saber antes de competir

- **Blanco con poca luz → negro.** En `naba`, un blanco que se lee con menos del ~45 % del brillo con que se calibró se clasifica como **negro (4)**, no como duda. Le pasa a una pieza más lejos, torcida o tapada a medias. El programa lo manda a la rama "0 o 4". Esto ya pasa hoy. Está calculado en la PC y revisado por dos caminos, pero falta probarlo en el robot: presentar el blanco un poco más lejos y mirar qué dice `pruebacolores.py`.
- **Margen mínimo apagado en `naba`,** igual que hoy. Cerca de las fronteras (sobre todo blanco/negro) el detector contesta un color aunque gane por muy poco. Prenderlo daría más -1, y el programa hace otra cosa con -1: probarlo en banco antes.
- **Firmware.** `calibrar.py` anota con qué firmware se calibró. Si se actualiza el firmware de Pybricks, hay que recalibrar: el 4.0.0b3 cambió la cuenta del color y no se sabe con qué firmware se midió la tabla de `naba`.
- **Memoria.** El `colores.py` nuevo ocupa el doble que el anterior (unos 8 KB compilado, contra 4 KB). Cargar el programa completo de competencia en el hub y confirmar que arranca.
- **Si algo falla en la competencia:** volver a importar `colores.py` desde `pybricks-backup-2311`.

## Qué se probó y qué no

| Prueba | Resultado |
|---|---|
| Tests en la PC (matemática del detector, conjuntos, bloques, multitarea) | 56 + 56, todos pasan |
| `detectar_color()` comparada con el `colores.py` del robot | 100.000 lecturas, 0 diferencias |
| Compilación con el compilador de MicroPython | todos los programas compilan |
| `calibrar.py`, `pruebacolores.py`, `cancha.py` y el ejemplo en un hub simulado | corren y dan lo esperado |
| Programa de bloques contra los 23 programas reales | válido |
| **En el robot** | **nada todavía**: lo cierra el equipo |
