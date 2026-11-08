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

* 3 mm outer skin, sitting 4 mm outside the original hull envelope
* 1 mm clearance to the existing `boatinside` liner (no collision)
* Hollow foam cavity, open at the inboard end
* Outboard nose tapered over the last 15 mm to 55 % of the original width
* One Ø24 mm foam-fill hole and one Ø8 mm vent hole per half
* 1.2 mm deep recessed deck panel
* Port half: ≈240 × 193 × 194 mm; fits the 256 mm build cube
* Full cap: ≈240 × 386 × 194 mm; use it for fit checks or split it in the slicer

## Foam filling

1. Dry-fit the port/starboard pair over the existing inside liner.
2. Glue/bond the centre seam and the inboard joint to the hull; tape the open
   inboard end and centre seam so foam cannot escape.
3. Pour low-expansion polyurethane foam through the Ø24 mm hole. Stop when it
   reaches the Ø8 mm vent.
4. Let it cure, trim the excess, and sand/fair the 4 mm step at the inboard joint
   if you want it flush with the middle hull.

Regenerate with `scripts/boat_end_cap_generator.py`.
