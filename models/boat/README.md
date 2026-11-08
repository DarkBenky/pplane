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

Regenerate with `scripts/boat_end_cap_generator.py`.
