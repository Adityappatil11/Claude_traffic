// =================================================================
// Premium Desktop Traffic Light Tower (Open-Chamber Edition)
// No MCU rails — maximum internal space for easy wire bundling
// Units: Millimeters (mm)
// =================================================================

$fn = 60; // Smooth curve resolution

// --- Main Enclosure Dimensions ---
body_w = 44.0;       // Outer Width (X)
body_d = 38.0;       // Outer Depth (Y)
body_h = 76.0;       // Tower Height (Z)
wall   = 2.2;        // Wall thickness
floor_t= 2.0;        // Base floor thickness
corner_r = 4.5;      // Smooth outer corner radius

// --- Tiered Anti-Tip Pedestal Base ---
base_w1 = 58.0; base_d1 = 50.0; base_h1 = 2.5; // Bottom tier
base_w2 = 50.0; base_d2 = 44.0; base_h2 = 2.5; // Step tier

// --- Component Specifications ---
led_dia = 5.0;                  // 5mm LED press fit
led_z   = [60, 46, 32];         // Red (60), Yellow (46), Blue (32)
visor_proj = 5.5;               // Sun hood projection length
visor_wall = 1.2;

// Buzzer Retainer Ring (Bottom Face)
buzzer_od = 10.5;               // Sized for 10.2mm buzzer
buzzer_wall = 1.2;
buzzer_depth = 4.0;
buzzer_z = 15.0;                // Centered below all 3 LEDs

// Rear Micro-USB Cutout
usb_w = 12.0;
usb_h = 8.0;

// --- Helper: Rounded Solid Box ---
module rounded_box(w, d, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=h);
        translate([w - r, r, 0]) cylinder(r=r, h=h);
        translate([r, d - r, 0]) cylinder(r=r, h=h);
        translate([w - r, d - r, 0]) cylinder(r=r, h=h);
    }
}

// --- MODULE: Curved Sun Visor Hood ---
module traffic_visor() {
    difference() {
        // Outer hood cylinder angled 14 degrees downward
        rotate([90, 0, 0])
            rotate([14, 0, 0])
                cylinder(d = led_dia + (2 * visor_wall), h = visor_proj, center = false);

        // Hollow interior for LED lens
        rotate([90, 0, 0])
            rotate([14, 0, 0])
                translate([0, 0, -1])
                    cylinder(d = led_dia, h = visor_proj + 3, center = false);

        // Trim bottom half
        translate([-(led_dia + 6)/2, -(visor_proj + 4), -(led_dia + 6)])
            cube([led_dia + 6, visor_proj + 6, led_dia + 6]);
    }
}

// --- MODULE 1: Main Traffic Light Chassis ---
module traffic_light_chassis() {
    union() {
        difference() {
            union() {
                // Tiered Pedestal Base
                translate([-(base_w1 - body_w)/2, -(base_d1 - body_d)/2, 0])
                    rounded_box(base_w1, base_d1, base_h1, corner_r + 2);

                translate([-(base_w2 - body_w)/2, -(base_d2 - body_d)/2, base_h1])
                    rounded_box(base_w2, base_d2, base_h2, corner_r + 1);

                // Main Tower
                translate([0, 0, base_h1 + base_h2])
                    rounded_box(body_w, body_d, body_h - (base_h1 + base_h2), corner_r);
            }

            // Wide, Open Hollow Internal Cavity (Clean space for all components)
            translate([wall, wall, floor_t + base_h1 + base_h2])
                rounded_box(body_w - (2 * wall), body_d - (2 * wall), body_h + 10, max(0.5, corner_r - wall));

            // Rear Opening (Full vertical back access)
            translate([wall + 1.2, body_d - wall - 2, floor_t + base_h1 + base_h2])
                cube([body_w - 2*(wall + 1.2), wall + 5, body_h]);

            // Rear Wall Door Rails
            translate([wall - 0.2, body_d - wall - 1.4, floor_t + base_h1 + base_h2])
                cube([1.6, 1.4, body_h]);

            translate([body_w - wall - 1.4, body_d - wall - 1.4, floor_t + base_h1 + base_h2])
                cube([1.6, 1.4, body_h]);

            // Front Face: 3x LED Lens Holes
            for (z = led_z) {
                translate([body_w / 2, wall + 2, z])
                    rotate([90, 0, 0])
                    cylinder(d = led_dia, h = wall + 5);
            }

            // Front Face: Acoustic Buzzer Rosette
            for (ang = [0:45:315]) {
                translate([(body_w / 2) + 2.8 * cos(ang), wall + 2, buzzer_z + 2.8 * sin(ang)])
                    rotate([90, 0, 0])
                    cylinder(d = 1.3, h = wall + 5);
            }
            translate([body_w / 2, wall + 2, buzzer_z])
                rotate([90, 0, 0])
                cylinder(d = 1.6, h = wall + 5);
        }

        // Add 3x Outward Traffic Visors
        for (z = led_z) {
            translate([body_w / 2, 0, z])
                traffic_visor();
        }

        // Internal Buzzer Retaining Cup (Holds buzzer firmly in place)
        translate([body_w / 2, wall, buzzer_z])
            rotate([-90, 0, 0])
                difference() {
                    cylinder(d = buzzer_od + (2 * buzzer_wall), h = buzzer_depth);
                    translate([0, 0, -0.5])
                        cylinder(d = buzzer_od, h = buzzer_depth + 1.0);
                }
    }
}

// --- MODULE 2: Slide-in Rear Access Door ---
module slide_in_back_door() {
    door_w = body_w - 2 * wall + 2 * 1.2 - 0.5;
    door_h = body_h - (floor_t + base_h1 + base_h2) - 0.3;

    difference() {
        union() {
            cube([door_w, 2.0, door_h]);
            cube([0.9, 1.1, door_h]);
            translate([door_w - 0.9, 0, 0])
                cube([0.9, 1.1, door_h]);
        }

        // Micro-USB Cutout at bottom
        translate([(door_w / 2) - (usb_w / 2), -1, -0.1])
            cube([usb_w, 6.0, usb_h]);

        // Top finger notch for easy opening
        translate([(door_w / 2) - 7.5, 1.2, door_h - 6.0])
            cube([15.0, 1.5, 2.5]);
    }
}

// --- MODULE 3: Top Snap-On Lid ---
module top_enclosure_lid() {
    union() {
        rounded_box(body_w, body_d, 2.2, corner_r);

        translate([wall + 0.25, wall + 0.25, 2.2])
            rounded_box(
                body_w - 2*(wall + 0.25),
                body_d - 2*(wall + 0.25),
                2.8,
                max(0.5, corner_r - wall)
            );
    }
}

// =================================================================
// Render Scene
// =================================================================
traffic_light_chassis();

// Rear Door
translate([body_w + 16, 0, 0])
    slide_in_back_door();

// Removable Top Lid
translate([body_w + 16, body_d + 10, 0])
    top_enclosure_lid();