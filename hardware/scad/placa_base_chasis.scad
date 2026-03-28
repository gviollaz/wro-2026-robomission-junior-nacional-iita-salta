// =====================================================
// PLACA BASE DEL CHASIS — IITA WRO Bot v1
// Para corte láser en aluminio 2mm o impresión 3D
// =====================================================
// Dimensiones: 80×90mm
// Material: Aluminio 6061 T6 de 2mm (corte láser)
//           o PLA+ 3mm (impresión 3D)
// =====================================================

// === DIMENSIONES GENERALES ===
chasis_ancho = 80;        // mm
chasis_largo = 90;        // mm
chasis_espesor = 2;       // mm (aluminio) o 3mm (PLA)
chasis_radio = 4;         // mm, radio de esquinas

// === POSICIONES DE MONTAJE ===

// Motores Pololu N20 (brackets)
motor_y = 45;             // mm desde borde frontal
motor_x_offset = 35;     // mm desde centro (cada lado)
motor_mount_d = 3.2;     // mm (inserto M2)
motor_mount_sep = 20;    // mm entre agujeros del bracket

// PCB inferior (Teensy) — 4 standoffs
pcb_mount_d = 2.2;       // mm (tornillo M2)
pcb_mount_x = 30;        // mm desde centro
pcb_mount_y_front = 15;  // mm desde borde frontal
pcb_mount_y_back = 75;   // mm desde borde frontal

// Ball caster trasero
caster_y = 80;            // mm desde borde frontal
caster_d = 12;            // mm, agujero para ball caster

// Dynamixel brazo (lateral)
dxl_brazo_x = -chasis_ancho/2 + 5;  // borde izquierdo
dxl_brazo_y = 35;
dxl_mount_d = 2.7;       // mm (M2.5)
dxl_mount_sep = 18;      // mm

// Batería LiPo (ventana central para bajar CG)
batt_ancho = 30;          // mm
batt_largo = 50;          // mm
batt_y = 40;              // mm desde borde frontal

// Sensor array color (agujeros para sensores VEML6040)
sensor_count = 7;
sensor_spacing = 10;      // mm entre sensores
sensor_d = 4;             // mm, agujero para sensor
sensor_y = 75;            // mm desde borde frontal

// === MÓDULO PLACA BASE ===
module placa_base_2d() {
    // Versión 2D para exportar DXF (corte láser)
    difference() {
        // Contorno con esquinas redondeadas
        offset(r=chasis_radio) 
            offset(r=-chasis_radio)
                square([chasis_ancho, chasis_largo], center=true);
        
        // Agujeros montaje motores (izq y der)
        for (lado = [-1, 1])
            for (dy = [-motor_mount_sep/2, motor_mount_sep/2])
                translate([lado * motor_x_offset, motor_y - chasis_largo/2 + dy])
                    circle(d=motor_mount_d, $fn=20);
        
        // Agujeros montaje PCB (4 esquinas)
        for (dx = [-pcb_mount_x, pcb_mount_x])
            for (dy = [pcb_mount_y_front, pcb_mount_y_back])
                translate([dx, dy - chasis_largo/2])
                    circle(d=pcb_mount_d, $fn=20);
        
        // Agujero ball caster
        translate([0, caster_y - chasis_largo/2])
            circle(d=caster_d, $fn=32);
        
        // Ventana batería (reduce peso + acceso batería)
        translate([-batt_ancho/2, batt_y - chasis_largo/2 - batt_largo/2])
            offset(r=2) offset(r=-2)
                square([batt_ancho, batt_largo]);
        
        // Agujeros sensores color array
        for (i = [0:sensor_count-1])
            translate([i * sensor_spacing - (sensor_count-1) * sensor_spacing/2,
                       sensor_y - chasis_largo/2])
                circle(d=sensor_d, $fn=20);
        
        // Agujeros montaje Dynamixel brazo (izquierda)
        for (dy = [-dxl_mount_sep/2, dxl_mount_sep/2])
            translate([dxl_brazo_x + chasis_ancho/2, 
                       dxl_brazo_y - chasis_largo/2 + dy])
                circle(d=dxl_mount_d, $fn=20);
    }
}

module placa_base_3d() {
    // Versión 3D (para visualización o impresión)
    linear_extrude(height=chasis_espesor)
        placa_base_2d();
}

// === RENDER ===
// Para corte láser: exportar como DXF
// projection() placa_base_2d();  // Descomentar y exportar DXF

// Para visualización 3D:
placa_base_3d();

// Para exportar DXF para corte láser:
// 1. Descomentar la línea projection()
// 2. En OpenSCAD: Design → Export as DXF
// 3. Enviar el .dxf al servicio de corte láser
