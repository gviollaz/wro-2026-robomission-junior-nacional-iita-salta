# Software - Junior (Pybricks Python)

## Plataforma

- **Firmware:** Pybricks (instalado en Spike Prime)
- **IDE:** [code.pybricks.com](https://code.pybricks.com)
- **Lenguaje:** Python (MicroPython)

## Estructura de programas

```
software/
  programs/
    main.py                  # Programa principal de competencia
    base_config.py           # Configuracion base del robot
    mision_visitantes.py     # Mision 1: guiar visitantes
    mision_torres.py         # Mision 2: reconstruir torres
    mision_artefactos.py     # Mision 3: artefactos al museo
    mision_adoquines.py      # Mision 4: limpiar adoquines
  calibration/
    calibrar_color.py        # Calibracion sensor de color
    calibrar_distancias.py   # Verificar distancias DriveBase
    calibrar_brazo.py        # Calibrar angulos del brazo
  tools/
    test_motores.py          # Test basico de motores
    test_sensores.py         # Test de sensores
```

## Conceptos clave Pybricks (Python)

- **DriveBase**: `straight()`, `turn()`, `curve()`, `drive()`
- **Motor.run_angle()**: brazo/garra con angulo exacto
- **ColorSensor.hsv()**: deteccion precisa de colores (H, S, V)
- **UltrasonicSensor.distance()**: alineacion con objetos
- **hub.imu**: giroscopio para corregir drift en giros
- **multitask()**: ejecutar lectura de sensores mientras se mueve
- **StopWatch()**: controlar tiempo restante de la ronda

## Estrategia de misiones (por prioridad de puntos)

1. **Torres amarillas** (50 pts) - Dificil pero vale mucho
2. **Artefactos al museo** (60 pts) - Requiere sensor color
3. **Visitantes** (40 pts) - Relativamente facil
4. **Torres rojas** (30 pts) - Facil
5. **Limpiar adoquines** (20 pts) - Facil con barredora
6. **Bonus** (30 pts) - No tocar barreras ni loro
