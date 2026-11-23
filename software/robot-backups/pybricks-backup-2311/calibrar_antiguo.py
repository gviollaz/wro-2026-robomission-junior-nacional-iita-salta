# calibrar.py — presenta cada objeto frente al sensor, con el MECANISMO ARMADO.
# Cada ~1 seg imprime una linea lista para pegar en COLORES de colores.py.
# Sacar y volver a poner el objeto varias veces; elegir una linea tipica.
from colores import medir, chequear
from pybricks.tools import wait

chequear()   # revisa la tabla actual
print("--- Presenta un color y anota la linea sugerida ---")
while True:
    pts = []
    sx = sy = sz = 0
    for _ in range(8):
        p = medir(3)
        pts.append(p)
        sx += p[0]; sy += p[1]; sz += p[2]
        wait(60)
    cx = sx / 8; cy = sy / 8; cz = sz / 8
    disp = 0.0
    for p in pts:
        d = ((p[0]-cx)**2 + (p[1]-cy)**2 + (p[2]-cz)**2) ** 0.5
        if d > disp:
            disp = d
    tol = 3 * disp           # burbuja = 3x el ruido medido
    tol = 8 if tol < 8 else round(tol)
    print("(COD, 'NOMBRE',", round(cx), ",", round(cy), ",", round(cz), ",", tol, "),   # ruido:", round(disp, 1))