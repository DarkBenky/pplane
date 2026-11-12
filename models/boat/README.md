# Boat bow/stern end caps

The old `boatend.stl` … `boatend4.stl` files are solid placeholder blocks.
These are the replacement **thin end plates** — just the end face of the boat,
with no side walls, sleeve, or added nose:

| file | use |
| --- | --- |
| `boat_bow_stern_cap_full.stl` | full-width fit/assembly reference |
| `boat_bow_stern_cap_port.stl` | printable port half (+Y) |
| `boat_bow_stern_cap_starboard.stl` | printable starboard half (−Y) |

Use **the same port/starboard pair at both ends**; rotate the pair 180° about Z
for the stern.

## Design

* Thin 2 mm plates cut from the outboard face of the original `boatend`
  placeholder, so the outline is the boat's existing end face.
* No side walls, no sleeve over the liner, and no long nose — this is only the
  part that closes the end/start of the boat.
* The profile keeps the existing sheer edge and V/keel bottom.
* Port half: 2 × 188.48 × 186.06 mm; full plate: 2 × 375.19 × 186.06 mm.
* Both halves fit the 256 mm build cube easily. Print flat with the large face
  on the bed and the 2 mm thickness vertical.
* The plate is solid. Foam the hull before bonding it, or drill a fill hole
  through the plate if you want to pour foam through the cap.
* Port and starboard are exact mirrors. The same pair is used at bow and stern;
  rotate it 180° about Z for the stern.

## Fitting

1. Dry-fit the port/starboard plates against the boat's end face (the old
   `boatend` placeholder position).
2. Glue/bond the centre seam and the perimeter to the hull. The plate butts
   against the end; it does not slide over the liner.
3. If printing the halves, glue the centre seam before final fitting.

The plate clears both `boatinside` and `boatinside2` with 0 mm³ intersection.

Regenerate with `scripts/boat_end_cap_generator.py`.

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