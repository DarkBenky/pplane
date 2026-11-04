# pplane — ducted fan parts

STL models, parametric generators and sliced files for the ducted-fan assembly
(fan rotor, duct covers, stator cross and duct extension).

## Layout

```
models/
  fan/      fanV2.stl, fanV2.3mf, Propeller Generator.stl
  covers/   male-cover.stl, female-cover.stl (+ -fixed versions), female-cover.3mf
  cross/    cross.stl (original), cross_v2.stl, cross_v2_assembly.stl
  duct/     extension_tube.stl, tube_fit_test.stl
  hardware/ m3_heat_insert.stl, m3_screw_10mm.stl, m3_hex_nut.stl, m3_washer.stl
  test-stand/ motor_test_stand_base.stl, motor_test_stand_lid.stl
scripts/    cross_generator.py, fix_cover_pins.py, tube_generator.py,
            hardware_generator.py, test_stand_generator.py
backups/    pre-edit copies of the models above (not printed)
prints/     sliced gcode, PLA
cad/        engine.blend — Blender assembly / inspection scene
docs/photos reference photos of the printed parts and caliper/protractor measurements
```

## Scripts

All scripts read and write inside `models/`, so they can be run from anywhere.
Python: `/home/user/miniconda3/bin/python` (needs `numpy`, `scipy`, `trimesh`, `manifold3d`).

| script | reads | writes |
| --- | --- | --- |
| `scripts/cross_generator.py` | – | `models/cross/cross_v2.stl`, `cross_v2_assembly.stl` |
| `scripts/fix_cover_pins.py` | `models/covers/male-cover.stl`, `female-cover.stl` | `models/covers/*-fixed.stl` |
| `scripts/tube_generator.py` | `models/covers/*-cover.stl` | `models/duct/extension_tube.stl`, `tube_fit_test.stl` |
| `scripts/hardware_generator.py` | – | `models/hardware/m3_*.stl` |
| `scripts/test_stand_generator.py` | – | `models/test-stand/motor_test_stand_*.stl` |

`fix_cover_pins.py` is **not idempotent** — run it on the *original* covers only
(the `-fixed` files already in the repo are the result; running it again adds the
pins a second time).

## Key dimensions

**Fan (`fanV2.stl`)** — bore enlarged from 12.0 to **12.6 mm** (r 6.3, 90-sided).
Bottom opening stays 12.8 mm. Watertight, ~84k triangles.

**Cross (`cross_v2.stl`)** — arms 25.87 mm high, tip radius 63.25 mm,
M3 heat-insert holes Ø4.0 × 7.5 mm with Ø4.8 chamfer; **hole span 39.0 mm**
(clear gap between chamfer rims), hole centres at r 21.9 mm.
Mid-height diamond ring at r 34 mm with a 0.8 mm web down to a 2 mm bell-mouth base
(support-free print). 36.8 cm³ ≈ 45.6 g PLA.

**Covers (`male-cover.stl` / `female-cover.stl`)** — half shells, roughly
Ø139.6 mm; wall **6.35 mm**; bore r 61.75 (male) / 64.99 (female);
top rim at z 69.105 with a **41.7° bell-mouth chamfer** running down to
(r − 6.35, z 63.454). Pins fixed to Ø2.4 / sockets Ø2.6, centred, ≈1.2 mm walls.

**Extension tube (`extension_tube.stl`)** — 25 mm tall collar added on top of the
covers. Same 6.35 mm wall, outer surface follows the real cover outline (sampled
from both halves), bottom face is the same **41.7° cone** so it seats flush in the
cover's bell mouth and is held with hot glue. 73.6 cm³ ≈ 91 g PLA.
Verified seat gap vs the cover: 0.01–0.02 mm. `tube_fit_test.stl` is an 8 mm tall
version of the same seat for a quick fit check.

**Hardware references (`models/hardware/`)** — generic M3 parts for fit checks
in CAD/slicer. Heat insert: body Ø4.6 × 5.2 mm, flange Ø5.6 × 0.5 mm, Ø2.5 bore.
M3×10 socket-head screw: head Ø5.5 × 3.0 mm, 2.5 mm hex socket, 10 mm shank.
Hex nut: 5.5 mm A/F × 2.4 mm. Washer: Ø7.0 × Ø3.2 × 1.0 mm. These are reference
geometry only — use real steel hardware in the assembly. The heat insert is an
interference fit: its 4.6 mm body is installed into a 4.0 mm hole with heat, and
its 5.6 mm flange needs a Ø5.8 × 0.7 mm counterbore to sit flush. The cross's
Ø4.8 mm entry chamfer is smaller than that flange; open it to Ø5.8 × 0.7 mm if
you want the insert flush (this reduces the clear hole span slightly).

**Motor test stand (`models/test-stand/`)** — plus-shaped sand-ballast base
180 × 180 mm, 40 mm tall, 3 mm walls, ~446 cm³ cavity (~713 g dry sand), four
Ø10 mm columns at r 75 with Ø4.0 × 7.5 mm heat-insert holes and Ø5.8 × 0.7 mm
flange counterbores. Plus-shaped lid 180 × 180 × 8 mm with the same 4 × M3
motor pattern as the cross: holes at r 21.9 mm (same 43.8 mm centers; 39 mm
clear between the cross's chamfer rims), 8 mm deep with Ø5.8 × 0.7 mm flange counterbores, 3.5 mm bosses, a
Ø16 × 2.5 mm centering pocket, and a 2 mm lip that seats inside the cavity to
align and seal the lid. Four Ø3.4 through-holes with Ø6 × 3 mm counterbores at
r 75. Base ≈164 g PLA, lid ≈143 g PLA; ≈1.02 kg with sand. Motor screws
M3 × 8; base screws M3 × 10.

## Printing notes

* Duct parts: print the tube **upside down** (flat top face on the bed); the seat
  cone then becomes a ~42° overhang — fine on most printers, add support if needed.
* The cross prints support-free upright; the 2 mm base needs a brim.
* Test-stand base: print upright as modeled, no supports. Test-stand lid: print
  **flipped** (motor face on the bed, bosses up); the Ø16 × 2.5 mm center pocket
  bridges at 2.5 mm — fine on most printers, or drill it out afterwards.
* Fill the test-stand cavity with dry sand (or lead shot for more mass) before
  screwing the lid down. A plastic bag liner keeps sand contained and dry.
* Fan blades are thin (median ~0.8 mm, some edges ~0.3 mm). SLM in AlSi10Mg is
  risky at that wall thickness — MJF/SLS PA12 or SLA works better.
