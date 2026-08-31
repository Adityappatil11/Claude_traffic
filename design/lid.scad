// =================================================================
// PART 3: Top Snap-On Enclosure Lid
// Units: Millimeters (mm)
// =================================================================

$fn = 60;

body_w   = 44.0;
body_d   = 38.0;
wall     = 2.2;
corner_r = 4.5;

module rounded_box(w, d, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=h);
        translate([w - r, r, 0]) cylinder(r=r, h=h);
        translate([r, d - r, 0]) cylinder(r=r, h=h);
        translate([w - r, d - r, 0]) cylinder(r=r, h=h);
    }
}

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

// Render Lid
top_enclosure_lid();