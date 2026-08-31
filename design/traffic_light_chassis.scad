// =================================================================
// PART 1: Main Traffic Light Chassis
// Units: Millimeters (mm)
// =================================================================

$fn = 60;

// --- Dimensions ---
body_w = 44.0;
body_d = 38.0;
body_h = 76.0;
wall   = 2.2;
floor_t= 2.0;
corner_r = 4.5;

base_w1 = 58.0; base_d1 = 50.0; base_h1 = 2.5;
base_w2 = 50.0; base_d2 = 44.0; base_h2 = 2.5;

led_dia = 5.0;
led_z   = [60, 46, 32];
visor_proj = 5.5;
visor_wall = 1.2;

buzzer_od = 10.5;
buzzer_wall = 1.2;
buzzer_depth = 4.0;
buzzer_z = 15.0;

module rounded_box(w, d, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=h);
        translate([w - r, r, 0]) cylinder(r=r, h=h);
        translate([r, d - r, 0]) cylinder(r=r, h=h);
        translate([w - r, d - r, 0]) cylinder(r=r, h=h);
    }
}

module traffic_visor() {
    difference() {
        rotate([90, 0, 0])
            rotate([14, 0, 0])
                cylinder(d = led_dia + (2 * visor_wall), h = visor_proj, center = false);

        rotate([90, 0, 0])
            rotate([14, 0, 0])
                translate([0, 0, -1])
                    cylinder(d = led_dia, h = visor_proj + 3, center = false);

        translate([-(led_dia + 6)/2, -(visor_proj + 4), -(led_dia + 6)])
            cube([led_dia + 6, visor_proj + 6, led_dia + 6]);
    }
}

module traffic_light_chassis() {
    union() {
        difference() {
            union() {
                translate([-(base_w1 - body_w)/2, -(base_d1 - body_d)/2, 0])
                    rounded_box(base_w1, base_d1, base_h1, corner_r + 2);

                translate([-(base_w2 - body_w)/2, -(base_d2 - body_d)/2, base_h1])
                    rounded_box(base_w2, base_d2, base_h2, corner_r + 1);

                translate([0, 0, base_h1 + base_h2])
                    rounded_box(body_w, body_d, body_h - (base_h1 + base_h2), corner_r);
            }

            translate([wall, wall, floor_t + base_h1 + base_h2])
                rounded_box(body_w - (2 * wall), body_d - (2 * wall), body_h + 10, max(0.5, corner_r - wall));

            translate([wall + 1.2, body_d - wall - 2, floor_t + base_h1 + base_h2])
                cube([body_w - 2*(wall + 1.2), wall + 5, body_h]);

            translate([wall - 0.2, body_d - wall - 1.4, floor_t + base_h1 + base_h2])
                cube([1.6, 1.4, body_h]);

            translate([body_w - wall - 1.4, body_d - wall - 1.4, floor_t + base_h1 + base_h2])
                cube([1.6, 1.4, body_h]);

            for (z = led_z) {
                translate([body_w / 2, wall + 2, z])
                    rotate([90, 0, 0])
                    cylinder(d = led_dia, h = wall + 5);
            }

            for (ang = [0:45:315]) {
                translate([(body_w / 2) + 2.8 * cos(ang), wall + 2, buzzer_z + 2.8 * sin(ang)])
                    rotate([90, 0, 0])
                    cylinder(d = 1.3, h = wall + 5);
            }
            translate([body_w / 2, wall + 2, buzzer_z])
                rotate([90, 0, 0])
                cylinder(d = 1.6, h = wall + 5);
        }

        for (z = led_z) {
            translate([body_w / 2, 0, z])
                traffic_visor();
        }

        translate([body_w / 2, wall, buzzer_z])
            rotate([-90, 0, 0])
                difference() {
                    cylinder(d = buzzer_od + (2 * buzzer_wall), h = buzzer_depth);
                    translate([0, 0, -0.5])
                        cylinder(d = buzzer_od, h = buzzer_depth + 1.0);
                }
    }
}

// Render Chassis
traffic_light_chassis();