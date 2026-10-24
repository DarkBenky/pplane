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
scripts/    cross_generator.py, fix_cover_pins.py, tube_generator.py
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

## Printing notes

* Duct parts: print the tube **upside down** (flat top face on the bed); the seat
  cone then becomes a ~42° overhang — fine on most printers, add support if needed.
* The cross prints support-free upright; the 2 mm base needs a brim.
* Fan blades are thin (median ~0.8 mm, some edges ~0.3 mm). SLM in AlSi10Mg is
  risky at that wall thickness — MJF/SLS PA12 or SLA works better.
