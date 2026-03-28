// =====================================================
// GARRA TIPO V PARA DYNAMIXEL XL330-M288-T
// WRO Junior 2026 — Heritage Heroes
// =====================================================
// Diseño: pinza convergente en V con dedos PLA + TPU
// Motor: Dynamixel XL330-M288-T (20×34×26mm, eje 8mm)
// Montaje: frames ROBOTIS FPX330-H101
// =====================================================

use <config_objetos.scad>

// === PARÁMETROS DE LA GARRA (ajustar según pruebas) ===

// Apertura
garra_apertura_max = 55;      // mm, apertura total cuando abierta
garra_apertura_min = 10;      // mm, apertura cuando cerrada al máximo
garra_angulo_v     = 12;      // grados, ángulo de convergencia V

// Dedos
dedo_largo    = 45;           // mm, largo del dedo desde pivote
dedo_ancho    = 10;           // mm, ancho del dedo (perfil)
dedo_alto     = 40;           // mm, profundidad del dedo (para agarrar objetos altos)
dedo_espesor  = 3;            // mm, espesor pared del dedo

// Grip TPU
tpu_espesor   = 1.5;          // mm, espesor del recubrimiento TPU
tpu_alto      = 30;           // mm, altura de la zona de grip

// Dynamixel XL330
xl330_ancho   = 20;           // mm (datasheet)
xl330_largo   = 34;           // mm (datasheet)
xl330_alto    = 26;           // mm (datasheet)
xl330_eje_d   = 8;            // mm, diámetro del eje de salida
xl330_mount_d = 2.5;          // mm, tornillos de montaje M2.5
xl330_mount_sep = 18;         // mm, distancia entre agujeros de montaje

// Base de montaje
base_ancho = 40;              // mm
base_largo = 36;              // mm  
base_alto  = 4;               // mm, espesor placa base

// Insertos metálicos
inserto_d = 3.2;              // mm, diámetro agujero para inserto M2
inserto_h = 4;                // mm, profundidad del inserto

// === MÓDULOS ===

module dedo_pla() {
    // Cuerpo del dedo en PLA
    // Forma: L invertida — parte vertical agarra, parte horizontal monta
    difference() {
        union() {
            // Parte vertical del dedo (la que agarra)
            cube([dedo_ancho, dedo_espesor, dedo_alto]);
            
            // Labio interior en V (guía el objeto al centro)
            translate([0, 0, 0])
                rotate([0, 0, garra_angulo_v])
                    cube([dedo_ancho, dedo_espesor/2, dedo_alto * 0.7]);
        }
        
        // Ranura para insert TPU
        translate([dedo_ancho/2 - tpu_espesor/2, -0.1, 
                   (dedo_alto - tpu_alto)/2])
            cube([tpu_espesor, dedo_espesor + 0.2, tpu_alto]);
    }
}

module tpu_grip() {
    // Pieza de TPU que se inserta en la ranura del dedo PLA
    // Imprime por separado en TPU 95A
    cube([tpu_espesor - 0.1, dedo_espesor - 0.2, tpu_alto]);
}

module base_montaje_xl330() {
    difference() {
        // Placa base
        translate([-base_ancho/2, -base_largo/2, 0])
            cube([base_ancho, base_largo, base_alto]);
        
        // Agujero central para eje XL330
        translate([0, 0, -0.1])
            cylinder(d=xl330_eje_d + 0.5, h=base_alto + 0.2, $fn=32);
        
        // Agujeros de montaje XL330 (patrón cuadrado)
        for (dx = [-xl330_mount_sep/2, xl330_mount_sep/2])
            for (dy = [-xl330_mount_sep/2, xl330_mount_sep/2])
                translate([dx, dy, -0.1])
                    cylinder(d=xl330_mount_d + 0.1, h=base_alto + 0.2, $fn=20);
        
        // Agujeros para montaje al brazo (M2 insertos)
        for (dx = [-base_ancho/2 + 4, base_ancho/2 - 4])
            translate([dx, 0, -0.1])
                cylinder(d=inserto_d, h=inserto_h + 0.1, $fn=20);
    }
}

module soporte_sensor_color() {
    // Soporte para TCS34725 montado entre los dedos
    // El sensor mira hacia el objeto cuando la garra está abierta
    difference() {
        cube([20, 15, 3]);
        // Agujeros montaje sensor (M2)
        translate([5, 7.5, -0.1]) cylinder(d=2.2, h=3.2, $fn=16);
        translate([15, 7.5, -0.1]) cylinder(d=2.2, h=3.2, $fn=16);
        // Ventana para el sensor
        translate([7, 4, -0.1]) cube([6, 7, 3.2]);
    }
}

module garra_completa() {
    // Ensamble completo de la garra
    
    // Base de montaje
    color("gray") base_montaje_xl330();
    
    // Dedo izquierdo
    color("white")
        translate([-garra_apertura_max/2, -dedo_largo/2, base_alto])
            rotate([0, 0, garra_angulo_v])
                dedo_pla();
    
    // Dedo derecho (espejado)
    color("white")
        translate([garra_apertura_max/2 - dedo_ancho, -dedo_largo/2, base_alto])
            rotate([0, 0, -garra_angulo_v])
                dedo_pla();
    
    // TPU grips (color naranja para visualizar)
    color("orange", 0.7)
        translate([-garra_apertura_max/2 + dedo_ancho/2 - tpu_espesor/2, 
                   -dedo_largo/2 - 0.05, 
                   base_alto + (dedo_alto - tpu_alto)/2])
            tpu_grip();
    
    color("orange", 0.7)
        translate([garra_apertura_max/2 - dedo_ancho/2 - tpu_espesor/2, 
                   -dedo_largo/2 - 0.05, 
                   base_alto + (dedo_alto - tpu_alto)/2])
            tpu_grip();
    
    // Soporte sensor color (entre dedos, arriba)
    color("green", 0.5)
        translate([-10, -dedo_largo/2, base_alto + dedo_alto + 2])
            soporte_sensor_color();
}

// === RENDER ===
garra_completa();

// === EXPORTAR PIEZAS INDIVIDUALES ===
// Descomentar UNA línea a la vez para exportar cada pieza como STL:
// dedo_pla();              // → dedo_pla.stl (imprimir ×2 en PLA+)
// tpu_grip();              // → tpu_grip.stl (imprimir ×2 en TPU 95A)
// base_montaje_xl330();    // → base_montaje.stl (imprimir ×1 en PLA+)
// soporte_sensor_color();  // → soporte_sensor.stl (imprimir ×1 en PLA)
