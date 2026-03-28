# =============================================================================
# Reorganización del repo WRO Junior (PowerShell)
# Repo: gviollaz/wro-2026-robomission-junior-nacional-iita-salta
#
# INSTRUCCIONES:
#   1. Hacer Pull del repo primero (IITA Git Panel o "git pull")
#   2. Abrir PowerShell en la carpeta raíz del repo
#   3. Ejecutar: .\reorganizar-repo-junior.ps1
#   4. Copiar los archivos nuevos (README.md, docs/es/index.md, etc.)
#   5. git add -A
#   6. git commit -m "refactor: reorganizar docs — consolidar en docs/es/"
#   7. git push (o ACP desde IITA Git Panel)
# =============================================================================

Write-Host "=== Paso 1: Crear carpetas nuevas ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "docs/es/hardware/vision-camaras"
New-Item -ItemType Directory -Force -Path "docs/es/software/line-following"
New-Item -ItemType Directory -Force -Path "docs/es/software/movement"
New-Item -ItemType Directory -Force -Path "docs/es/software/color-detection"
New-Item -ItemType Directory -Force -Path "docs/es/reviews"
New-Item -ItemType Directory -Force -Path "docs/es/learning"

Write-Host "=== Paso 2: Mover docs sueltos de docs/ raiz ===" -ForegroundColor Cyan

# -> competition/
git mv "docs/dimensiones-objetos-wro-junior-2026.md" "docs/es/competition/"

# -> hardware/
git mv "docs/diseno-230-campeon-junior.md" "docs/es/hardware/"
git mv "docs/nivel3-plus-robot-definitivo.md" "docs/es/hardware/"
git mv "docs/nivel3-robot-custom-profundidad.md" "docs/es/hardware/"
git mv "docs/hardware-tres-niveles-junior.md" "docs/es/hardware/"
git mv "docs/mecanismos-pinzas-diseno-3d.md" "docs/es/hardware/"
git mv "docs/planos-robot-y-circuito.md" "docs/es/hardware/"
git mv "docs/seleccion-bateria-driver-encoders.md" "docs/es/hardware/"

# -> reviews/
git mv "docs/abogado-del-diablo-critica.md" "docs/es/reviews/"
git mv "docs/ALTERNATIVA-SONADA-README.md" "docs/es/reviews/"

# -> learning/
git mv "docs/plan-aprendizaje-ia-alumnos.md" "docs/es/learning/"

Write-Host "=== Paso 3: Mover series tematicas -> docs/es/software/ ===" -ForegroundColor Cyan

# line-following/ (8 archivos)
git mv "docs/line-following/README.md" "docs/es/software/line-following/"
git mv "docs/line-following/01-fundamentos.md" "docs/es/software/line-following/"
git mv "docs/line-following/02-un-sensor.md" "docs/es/software/line-following/"
git mv "docs/line-following/03-dos-sensores.md" "docs/es/software/line-following/"
git mv "docs/line-following/04-tres-sensores.md" "docs/es/software/line-following/"
git mv "docs/line-following/05-intersecciones.md" "docs/es/software/line-following/"
git mv "docs/line-following/06-encontrar-y-alinear.md" "docs/es/software/line-following/"
git mv "docs/line-following/07-estrategias-competicion.md" "docs/es/software/line-following/"

# movement/ (5 archivos)
git mv "docs/movement/README.md" "docs/es/software/movement/"
git mv "docs/movement/01-arranque-freno-suave.md" "docs/es/software/movement/"
git mv "docs/movement/02-odometria-precisa.md" "docs/es/software/movement/"
git mv "docs/movement/03-giroscopio.md" "docs/es/software/movement/"
git mv "docs/movement/04-calibracion-pid.md" "docs/es/software/movement/"

# color-detection/ (2 archivos)
git mv "docs/color-detection/README.md" "docs/es/software/color-detection/"
git mv "docs/color-detection/02-inmunidad-iluminacion.md" "docs/es/software/color-detection/"

Write-Host "=== Paso 4: Mover vision/ -> docs/es/hardware/vision-camaras/ ===" -ForegroundColor Cyan
git mv "docs/vision/README.md" "docs/es/hardware/vision-camaras/"
git mv "docs/vision/02-regla-wireless-wro.md" "docs/es/hardware/vision-camaras/"

Write-Host "=== Paso 5: Limpiar stubs vacios de docs/en/ ===" -ForegroundColor Cyan
git rm "docs/en/architecture/README.md"
git rm "docs/en/hardware/README.md"
git rm "docs/en/onboarding/README.md"

Write-Host ""
Write-Host "=== LISTO ===" -ForegroundColor Green
Write-Host "Ahora copia los archivos nuevos encima:" -ForegroundColor Yellow
Write-Host "  - README.md (reemplaza el actual)"
Write-Host "  - docs\es\index.md (reemplaza el actual)"
Write-Host "  - docs\es\reviews\README.md (nuevo)"
Write-Host "  - docs\es\learning\README.md (nuevo)"
Write-Host "  - docs\en\index.md (reemplaza el actual)"
Write-Host ""
Write-Host "Luego:" -ForegroundColor Yellow
Write-Host "  git add -A"
Write-Host "  git commit -m 'refactor: reorganizar docs - consolidar en docs/es/'"
Write-Host "  git push"
