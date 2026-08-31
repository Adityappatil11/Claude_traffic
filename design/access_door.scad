// =================================================================
// PART 2: Slide-in Rear Door Panel
// Units: Millimeters (mm)
// =================================================================

body_w = 44.0;
body_h = 76.0;
wall   = 2.2;
floor_t= 2.0;
base_h1 = 2.5;
base_h2 = 2.5;

usb_w = 12.0;
usb_h = 8.0;

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

        translate([(door_w / 2) - (usb_w / 2), -1, -0.1])
            cube([usb_w, 6.0, usb_h]);

        translate([(door_w / 2) - 7.5, 1.2, door_h - 6.0])
            cube([15.0, 1.5, 2.5]);
    }
}

// Render Door flat for printing
slide_in_back_door();