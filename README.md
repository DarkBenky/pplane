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
  battery/  lead_acid_12v_7.2ah.stl, lipo_6s_113x43x37.stl
  reference/ build_volume_256.stl, build_volume_256_frame.stl
  boat/     bow/stern foam-fill caps (+ existing boat parts)
scripts/    cross_generator.py, fix_cover_pins.py, tube_generator.py,
            hardware_generator.py, test_stand_generator.py, battery_generator.py,
            lipo_battery_generator.py, build_volume_generator.py,
            boat_end_cap_generator.py
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
| `scripts/battery_generator.py` | – | `models/battery/lead_acid_12v_7.2ah.stl` |
| `scripts/lipo_battery_generator.py` | – | `models/battery/lipo_6s_113x43x37.stl` |
| `scripts/build_volume_generator.py` | – | `models/reference/build_volume_256*.stl` |
| `scripts/boat_end_cap_generator.py` | – | `models/boat/boat_bow_stern_cap_*.stl` |

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
in CAD/slicer. Heat insert (measured kit part): body Ø3.95 × 5.92 mm, Ø2.4 bore,
0.3 mm outer / 0.2 mm bore lead-in chamfers, no flange. M3×10 socket-head screw:
head Ø5.5 × 3.0 mm, 2.5 mm hex socket, 10 mm shank. Hex nut: 5.5 mm A/F ×
2.4 mm. Washer: Ø7.0 × Ø3.2 × 1.0 mm. These are reference geometry only — use
real steel hardware in the assembly. The 4.0 mm insert holes in the cross and
test stand are a light slip fit for this 3.95 mm insert (0.05 mm clearance); if
it feels loose after heat-setting, add a drop of CA glue or use a 3.7–3.8 mm
hole. The test stand's Ø5.8 × 0.7 mm counterbores act as lead-ins for this
flangeless insert.

**Battery (`models/battery/lead_acid_12v_7.2ah.stl`)** — 12 V 7.2 Ah SLA
reference: **151.2 × 65.6 × 99.4 mm** overall (L × W × H). Case is 94.4 mm
tall; two 5 mm terminal posts bring the overall height to 99.4 mm. 3 mm corner
radius, 1 mm top/bottom edge chamfers, six vent-cap recesses, 0.8 mm recessed
bottom, and raised +/− marks. Terminals are at x +55 mm, y ±20 mm, with
10 × 1.2 mm spade tabs (positive at −Y). 99.4 mm is treated as the overall
height including terminals; if it is the case-only height, set `CASE_HEIGHT`
to 99.4 in `scripts/battery_generator.py`.

**6S LiPo (`models/battery/lipo_6s_113x43x37.stl`)** — hardcase reference:
**113 × 43 × 37 mm** (L × W × H), 4 mm corner radius, 1.2 mm top / 0.8 mm bottom
edge chamfers, 0.5 mm top label recess with six cell dots, and a 0.8 mm recessed
bottom. The +X end has a recessed XT90-style socket (20 × 12 × 8 mm) with two
Ø5.5 mm bullet holes and a recessed 22 × 8 × 5 mm balance socket with seven
1.2 mm pins. Connectors are recessed so the outer envelope stays exactly
113 × 43 × 37 mm; add external lead loops if you need wire clearance in a
holder.

**Motor test stand (`models/test-stand/`)** — plus-shaped sand-ballast base
180 × 180 mm, 40 mm tall, 3 mm walls, ~446 cm³ cavity (~713 g dry sand), four
Ø10 mm columns at r 75 with Ø4.0 × 7.5 mm heat-insert holes and Ø5.8 × 0.7 mm
lead-in counterbores. Plus-shaped lid 180 × 180 × 8 mm with the same 4 × M3
motor pattern as the cross: holes at r 21.9 mm (same 43.8 mm centers; 39 mm
clear between the cross's chamfer rims), 8 mm deep with Ø5.8 × 0.7 mm lead-in counterbores, 3.5 mm bosses, a
Ø16 × 2.5 mm centering pocket, and a 2 mm lip that seats inside the cavity to
align and seal the lid. Four Ø3.4 through-holes with Ø6 × 3 mm counterbores at
r 75. Base ≈164 g PLA, lid ≈143 g PLA; ≈1.02 kg with sand. Motor screws
M3 × 8; base screws M3 × 10.

**Build volume (`models/reference/`)** — 256 × 256 × 256 mm envelope for a
256 mm-class printer. `build_volume_256.stl` is the solid cube;
`build_volume_256_frame.stl` is a 12-edge cage with 3 mm square beams inside the
same envelope (250 mm clear inside the beams). Both are centred on X/Y and sit
on Z=0, so their bounds are X/Y −128…+128 mm and Z 0…256 mm.

**Boat end caps (`models/boat/`)** — foam-fill bow/stern caps. 3 mm skin
sitting 4 mm outside the original hull, 1 mm clearance to the inside liner,
open inboard end, tapered outboard nose, Ø24 fill + Ø8 vent per half, and a
1.2 mm recessed deck panel. Printable port/starboard halves are ≈240 × 193 ×
194 mm and fit the 256 mm build cube; the full cap is ≈240 × 386 × 194 mm.
Use the same pair at bow and stern and rotate 180° for the stern. Details in
`models/boat/README.md`.

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
* Battery and build-volume STLs are reference envelopes for holder/part design,
  not functional objects to print.
