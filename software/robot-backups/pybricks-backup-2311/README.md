# Backup del robot — 2026-11-23

Copia **tal cual** de la exportación de Pybricks Code que se hizo el 2026-11-23 (`pybricks-backup-2311.zip`, guardada en el disco del coach junto con los papeles de la final de WRO 2026). Es lo que corría en el robot ese día.

**No se edita.** Sirve para dos cosas:
- saber qué había en el robot cuando se hizo cada cambio;
- ser la referencia del validador de bloques (`software/tools/bloques/validar_bloques.py`), que compara los programas nuevos contra estos.

## Qué tiene

- `WRO_*.py`, `elementary3008.py`, `wrocolores_chino.py`, `wroelementary*.py`: son programas de **bloques**. La primera línea es el workspace del editor en JSON y el resto es el Python que el editor genera. El de la competencia en esa fecha es `WRO_2311_ORIGINAL.py`.
- `colores.py`, `calibrar.py`, `cancha.py`, `pruebacolores.py` y otros: los programas Python que se usaban junto con los bloques.

## En qué se diferenciaba del resto del repo ese día

[IA 2026-11-23] Comparado contra el repo a mano y con programas:

- **`colores.py`:** el sensor estaba en el **puerto F** (el repo decía B). La tabla era de negro, azul, blanco y amarillo, con el **blanco en el código 2**. No tenía la regla de margen mínimo.
- **Cableado** (Setup de los bloques):
  - motores de tracción en **B** (izquierdo, antihorario) y **E**;
  - motores auxiliares en C y D;
  - sensor de artefactos en **F** y sensor de piso en **A**;
  - `DriveBase(55, 176)`.

  `software/programs/base_config.py` y `docs/es/diseno_robot_iita_v1.md` no coinciden con esto.
- **Bloques:**
  - los 23 programas de bloques importan de `colores` solo `detectar_color`, con llamada común y sin argumentos;
  - ninguno usa multitarea;
  - en `WRO_2311_ORIGINAL.py` el color se lee en `PARTE_DE_LAS_NOTAS`; `deteccion_de_colores` está definida pero no se llama.

Lo que vino después (detector v3 con conjuntos `naba` y `rva`) está en `software/programs/`, y la explicación de uso en `software/programs/README_colores.md`.
