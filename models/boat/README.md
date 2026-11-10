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
