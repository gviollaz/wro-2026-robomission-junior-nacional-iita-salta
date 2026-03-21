# AI-INSTRUCTIONS

Este repo permite uso de IA bajo reglas IITA.

## Reglas generales

- Declarar IA en cada PR si se uso.
- Incluir fuentes si la IA aporta hechos/valores/reglas/datos.
- No subir datos sensibles a herramientas externas.
- Probar en robot o simulacion antes de mergear.

## Header obligatorio en TODOS los archivos de codigo

```python
# ============================================================================
# [Titulo descriptivo del programa]
# ============================================================================
#
# Autor:       [Nombre completo]
# Herramienta: [IA modelo exacto | "Codigo escrito manualmente"]
# Fecha:       [YYYY-MM-DD HH:MM]
# Rev:         [v1, v2, v3...]
# Hardware:    [Hub y componentes]
#
# DESCRIPCION:
#   [Que hace el programa en 2-3 lineas]
#
# ============================================================================
```

### Reglas del header

1. **OBLIGATORIO** en todo archivo de codigo.
2. El **Autor** es siempre la persona humana, nunca la IA.
3. La **Herramienta** debe ser especifica: "Claude Opus 4.6", "ChatGPT 4o", etc.
4. La **Fecha** incluye hora.
5. Al modificar, actualizar **Rev** y **Fecha**.
