// =====================================================
// CONFIGURACIÓN DE DIMENSIONES — WRO Junior 2026
// Heritage Heroes — Objetos del juego
// =====================================================
//
// ⚠️ MEDIDAS ESTIMADAS — ACTUALIZAR CON CALIBRE DIGITAL
// Después de armar los objetos reales, medir y reemplazar
// los valores marcados con // MEDIR
//
// Sistema LEGO:
//   1 stud = 8mm pitch
//   1 plate = 3.2mm alto
//   1 brick = 9.6mm alto (3 plates)
//   Ancho pieza = studs × 8 - 0.2mm
// =====================================================

// --- Visitantes (el más ancho define apertura mínima de garra) ---
visitante_ancho = 24;    // mm, ~3 studs // MEDIR
visitante_prof  = 16;    // mm, ~2 studs // MEDIR
visitante_alto  = 48;    // mm, ~5 bricks // MEDIR

// --- Torre amarilla BASE (fija en el campo, NO se mueve) ---
torre_am_base_ancho = 32;   // mm, ~4 studs // MEDIR
torre_am_base_prof  = 32;   // mm, ~4 studs // MEDIR
torre_am_base_alto  = 32;   // mm, ~3.3 bricks // MEDIR
torre_am_base_studs = 16;   // mm, zona de encaje 2×2 studs // MEDIR

// --- Torre amarilla TECHO (el robot la recoge y apila) ---
torre_am_top_ancho = 32;    // mm // MEDIR
torre_am_top_prof  = 32;    // mm // MEDIR
torre_am_top_alto  = 32;    // mm // MEDIR
torre_am_top_hueco = 16.2;  // mm, hueco inferior para encajar // MEDIR CRITICO

// --- Torres rojas (se transportan completas) ---
torre_roja_ancho = 24;   // mm, ~3 studs // MEDIR
torre_roja_prof  = 24;   // mm // MEDIR
torre_roja_alto  = 58;   // mm, ~6 bricks // MEDIR

// --- Artefactos (5 colores, base idéntica) ---
artefacto_ancho = 16;    // mm, ~2 studs // MEDIR
artefacto_prof  = 16;    // mm // MEDIR
artefacto_alto  = 32;    // mm, ~3.3 bricks // MEDIR

// --- Partículas de suciedad (para dimensionar la pala) ---
dirt_diametro = 8;       // mm, 1×1 round // MEDIR
dirt_alto     = 3.2;     // mm, 1 plate // MEDIR

// --- El objeto más ancho define la apertura de la garra ---
objeto_max_ancho = max(visitante_ancho, torre_am_top_ancho, 
                       torre_roja_ancho, artefacto_ancho);

echo(str("Objeto más ancho: ", objeto_max_ancho, "mm"));
echo(str("Apertura mínima garra: ", objeto_max_ancho + 10, "mm"));
