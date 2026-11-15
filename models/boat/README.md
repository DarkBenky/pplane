# Boat bow/stern caps

The old `boatend.stl` … `boatend4.stl` files are solid placeholder blocks.
These are the replacement foam-fill caps:

| file | use |
| --- | --- |
| `boat_bow_stern_cap_full.stl` | full-width fit/assembly reference |
| `boat_bow_stern_cap_port.stl` | printable port half (+Y) |
| `boat_bow_stern_cap_starboard.stl` | printable starboard half (−Y) |

Use **the same port/starboard pair at both ends**; rotate the pair 180° about Z
for the stern.

## Design

* 1.5 mm printed skin, 2.5…3 mm outside the original hull envelope
* 1.5 mm clearance to the existing `boatinside` liner (verified 0 mm³
  intersection with both liner versions)
* The section is copied from the hull's front cross-section: 188 mm half-width
  at the sheer, flat pads y = 60…133 mm at z = 145 mm, and a central V down to
  z = 108 mm; the skin is offset outward from that section
* The cap starts at x = 255 — over the front 85 mm of the existing liner — so
  no liner trimming is needed. It extends to x = 500, i.e. 160 mm beyond the
  liner end at x ≈ 340.
* The plan is a straight taper from full width at x = 340 to a 0.5 % wide tip
  at x = 500. There is no neck or separate nose step; the top view is one
  continuous sharp V.
* The keel rises 70 mm from x = 340 to x = 500 (rocker); the last 20 mm is a
  solid tip raked back 15 mm at the bottom.
* Hollow foam cavity, open at the inboard end; the solid tip closes the bow
* One Ø24 mm foam-fill hole and one Ø8 mm vent hole per half
* No deck recess — the top is a clean, continuous shell
* Port half: 245 × 192.25 × 198 mm (x 255…500, y 0…192.25, z 105…303); fits
  the 256 mm build cube with an 11 mm margin
* Full cap: 245 × 384.5 × 198 mm; use it for fit checks or split it in the
  slicer
* The same pair is used at bow and stern; rotate it 180° about Z for the stern

## Bow length

The cap slides over the front of the existing liner rather than stopping at its
end. It starts at x = 255 and runs to x = 500, so the bow is 160 mm longer than
the liner while still being a drop-in part. The sides run straight from x = 340
to the fine tip at x = 500, the keel rises 70 mm over that run, and the solid
tip is raked back 15 mm at the bottom. To change the length or sharpness, edit
`X_INBOARD`, `X_OUTBOARD`, `NOSE_TIP_SCALE`, `ROCKER_HEIGHT` and `RAKE_STEM`
and re-run the generator.

## Foam filling

1. Dry-fit the port/starboard pair over the existing inside liner.
2. Glue/bond the centre seam and the inboard joint to the hull; tape the open
   inboard end and centre seam so foam cannot escape.
3. Pour low-expansion polyurethane foam through the Ø24 mm hole. Stop when it
   reaches the Ø8 mm vent.
4. Let it cure, trim the excess, and sand/fair the 2.5…3 mm step at the inboard
   join if you want it flush with the middle hull.

Regenerate with `scripts/boat_bow_stern_generator.py`.

# Legacy thin end plates

The earlier **thin 2 mm end plates** are kept as well. They are flat plates cut
from the outboard face of the original `boatend` placeholder — just the end
face of the boat, with no side walls, sleeve, or added nose.

| file | use |
| --- | --- |
| `thin_end_plates/boat_bow_stern_cap_full.stl` | full-width fit/assembly reference |
| `thin_end_plates/boat_bow_stern_cap_port.stl` | printable port half (+Y) |
| `thin_end_plates/boat_bow_stern_cap_starboard.stl` | printable starboard half (−Y) |

Port half: 2 × 188.48 × 186.06 mm; full plate: 2 × 375.19 × 186.06 mm. Both
halves fit the 256 mm build cube easily. Print flat with the large face on the
bed. The plate is solid; foam the hull before bonding it, or drill a fill hole
through the plate. The plate clears both `boatinside` and `boatinside2` with
0 mm³ intersection.

Regenerate with `scripts/boat_end_cap_generator.py` (writes only to
`thin_end_plates/`, so it does not touch the current foam-fill caps).

# Optimized bench interiors

The two inside benches (`boatinside.stl` and `boatinside2.stl`) are split into
printable bodies and separate leg frames:

| file | use |
| --- | --- |
| `boatinside_optimized.stl` | bench body without legs (−Y side) |
| `boatinside2_optimized.stl` | bench body without legs (+Y side) |
| `boatinside_hole_optimized.stl` | hole bench body without legs (+Y side) |
| `boatinside_hole2_optimized.stl` | hole bench body without legs (−Y side) |
| `legs_inside/boatinside_leg_1.stl` | leg frame, low-Y rail, labels 1 + 2 |
| `legs_inside/boatinside_leg_2.stl` | leg frame, high-Y rail, labels 3 + 4 |
| `legs_inside/boatinside2_leg_1.stl` | leg frame, low-Y rail, labels 1 + 2 |
| `legs_inside/boatinside2_leg_2.stl` | leg frame, high-Y rail, labels 3 + 4 |
| `legs_inside/boatinside_hole_leg_1.stl` | loose leg, label 1 |
| `legs_inside/boatinside_hole_leg_2.stl` | loose leg, label 2 |
| `legs_inside/boatinside_hole_leg_3.stl` | leg frame, labels 3 + 4 |
| `legs_inside/boatinside_hole2_leg_1.stl` | leg frame, labels 1 + 2 |
| `legs_inside/boatinside_hole2_leg_2.stl` | loose leg, label 3 |
| `legs_inside/boatinside_hole2_leg_3.stl` | loose leg, label 4 |

The original `boatinside*.stl` files (including the hole variants) are unchanged.

## Alignment

Each body has four shallow pockets on the underside, one at each end of the
two rail contact strips. They are **one 0.2 mm layer deep** and **0.5 mm larger
than the matching key** on the leg frame in every direction. The leg pieces
have 0.2 mm raised keys at their mounting positions. Drop the keys into the pockets and
glue; no supports are needed for the pockets or keys.

Each pocket and rail end has an engraved dot code:

* **1** = low-X / low-Y post
* **2** = high-X / low-Y post
* **3** = low-X / high-Y post
* **4** = high-X / high-Y post

A dot count of 1–4 is the symbol; match the body dots to the leg dots. The
regular benches have two leg frames (`leg_1` = 1 + 2, `leg_2` = 3 + 4). The
hole benches have three pieces each because one rail already contains holes.

## Printing

* Body: print as modeled, bottom down. The 0.2 mm pockets are shallow recesses
  in the bottom face and need no support.
* Leg frames: print **on their side** with the long rail flat on the bed. The
  key and dot details then print without supports.
* Dry-fit each leg frame to its body before gluing; the 0.5 mm clearance is
  intentionally loose so the frame drops in without force.

Regenerate with `scripts/boat_inside_split_generator.py`.
