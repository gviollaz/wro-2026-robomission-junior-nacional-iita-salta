// =====================================================
// BRACKET DE MOTOR POLOLU N20 MICRO METAL GEARMOTOR
// Para montaje en chasis del robot WRO
// =====================================================
// Compatible con: Pololu 30:1, 50:1, 100:1 HPCB 6V
// con encoder integrado (back connector)
// Dimensiones motor: 10×12×26mm (sin eje)
// Eje de salida: 3mm D-shaft, 9mm largo
// =====================================================

// === DIMENSIONES DEL MOTOR POLOLU N20 ===
motor_ancho = 10;         // mm
motor_alto  = 12;         // mm 
motor_largo = 26;         // mm (sin eje, sin encoder)
motor_largo_total = 33;   // mm (con encoder back connector)
motor_eje_d = 3;          // mm, D-shaft
motor_eje_largo = 9;      // mm

// Agujeros de montaje del motor
motor_mount_d = 1.6;      // mm (M1.6 threads en faceplate)
motor_mount_sep_x = 8.5;  // mm entre agujeros
motor_mount_sep_y = 0;    // mm (alineados verticalmente)

// === PARÁMETROS DEL BRACKET ===
bracket_pared = 2.5;      // mm, espesor de pared
bracket_base  = 3;        // mm, espesor de la base de montaje

// Insertos para montaje al chasis
chasis_mount_d = 3.2;     // mm (inserto M2)
chasis_mount_sep = 20;    // mm, distancia entre agujeros de montaje al chasis

// === MÓDULO BRACKET ===
module bracket_pololu_n20() {
    // Bracket en U que abraza el motor
    
    ancho_int = motor_ancho + 0.3;  // tolerancia 0.15mm por lado
    alto_int  = motor_alto + 0.3;
    largo_bracket = motor_largo_total + 2;  // espacio para encoder
    
    ancho_ext = ancho_int + 2 * bracket_pared;
    alto_ext  = alto_int + bracket_base;
    
    difference() {
        union() {
            // Base del bracket
            translate([-ancho_ext/2, 0, 0])
                cube([ancho_ext, largo_bracket, bracket_base]);
            
            // Pared izquierda
            translate([-ancho_ext/2, 0, 0])
                cube([bracket_pared, largo_bracket, alto_ext]);
            
            // Pared derecha
            translate([ancho_int/2, 0, 0])
                cube([bracket_pared, largo_bracket, alto_ext]);
            
            // Tapa frontal (donde sale el eje)
            translate([-ancho_ext/2, -bracket_pared, 0])
                cube([ancho_ext, bracket_pared, alto_ext]);
        }
        
        // Cavidad para el motor
        translate([-ancho_int/2, 0, bracket_base])
            cube([ancho_int, largo_bracket + 0.1, alto_int + 0.1]);
        
        // Agujero para el eje del motor (faceplate)
        translate([0, -bracket_pared - 0.1, bracket_base + alto_int/2])
            rotate([-90, 0, 0])
                cylinder(d=motor_eje_d + 2, h=bracket_pared + 0.2, $fn=20);
        
        // Agujeros de montaje del motor (M1.6) en faceplate
        for (dx = [-motor_mount_sep_x/2, motor_mount_sep_x/2])
            translate([dx, -bracket_pared - 0.1, bracket_base + alto_int/2])
                rotate([-90, 0, 0])
                    cylinder(d=motor_mount_d, h=bracket_pared + 0.2, $fn=16);
        
        // Agujeros de montaje al chasis (M2 insertos)
        for (dx = [-chasis_mount_sep/2, chasis_mount_sep/2])
            translate([dx, largo_bracket/2, -0.1])
                cylinder(d=chasis_mount_d, h=bracket_base + 0.2, $fn=20);
        
        // Ventana lateral para cables del encoder
        translate([ancho_int/2 - 0.1, largo_bracket - 10, bracket_base + 2])
            cube([bracket_pared + 0.2, 8, alto_int - 4]);
    }
}

// === RENDER ===
bracket_pololu_n20();

// Para visualizar con el motor (no exportar):
// %translate([- motor_ancho/2, 0, bracket_base + 0.15])
//     cube([motor_ancho, motor_largo_total, motor_alto]);
