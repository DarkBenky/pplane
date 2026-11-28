"""Buck-boost converter case - body + press-fit lid.

Geometry taken from the drawing (plan / front / side):

  outer         79.7 x 54 x 44 mm   (44 = 2 floor + 40 inside + 2 lid)
  inside        75.7 x 50 x 40 mm   (walls and floor 2 mm)
  front         fully open          (75.7 x 40, "the inside, open to the front")
  floor window  24 x 35 mm          centred, 15 mm from the inside front face,
                                    flush with the inside back face
  feet          4 x flared pads, 10 mm top -> 14 mm bottom, 9 mm tall
                (bottom faces flush with the 79.7 x 54 outline)
  lid           2 mm plate + 3 mm locating lip, 0.2 mm clearance per side

Coordinates: X centred, -Y = front, +Y = back, Z = 0 at the bottom of the case
(floor underside); the feet reach down to Z = -9.  Each STL is exported sitting
on Z = 0 so it can be sliced as-is.
"""

import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "models" / "buck-boost-converter"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTER_W = 79.7
OUTER_D = 54.0
WALL = 2.0
FLOOR = 2.0
INNER_H = 40.0
LID_T = 2.0

BODY_H = FLOOR + INNER_H          # 42.0
TOTAL_H = BODY_H + LID_T          # 44.0
INNER_W = OUTER_W - 2.0 * WALL    # 75.7
INNER_D = OUTER_D - 2.0 * WALL    # 50.0

HOLE_W = 24.0
HOLE_D = 35.0
HOLE_FRONT_GAP = 15.0             # inside front face -> window front edge

FOOT_H = 9.0
FOOT_TOP = 10.0                   # narrow end, tucked under the floor
FOOT_BOTTOM = 14.0                # wide end on the bench (stability)
FOOT_OVERHANG = 0.0               # > 0 lets the pads stick out past the outline
FOOT_BITE = 0.6                   # let the feet bite into the floor (clean union)
FOOT_CX = OUTER_W / 2.0 - FOOT_BOTTOM / 2.0 + FOOT_OVERHANG
FOOT_CY = OUTER_D / 2.0 - FOOT_BOTTOM / 2.0 + FOOT_OVERHANG

LID_LIP_T = 2.0
LID_LIP_H = 3.0
LID_CLEARANCE = 0.2               # per side

PLA_DENSITY = 1.24                # g/cm3


def box(min_corner, max_corner):
    lo = trimesh.PointCloud([min_corner]).bounds[0]
    hi = trimesh.PointCloud([max_corner]).bounds[0]
    return trimesh.creation.box(bounds=[lo, hi])


def tapered_pad(cx, cy, top, bottom, z_top, z_bottom):
    """Square frustum, top face `top` wide, bottom face `bottom` wide."""
    ht = top / 2.0
    hb = bottom / 2.0
    vertices = [
        [cx - ht, cy - ht, z_top], [cx + ht, cy - ht, z_top],
        [cx + ht, cy + ht, z_top], [cx - ht, cy + ht, z_top],
        [cx - hb, cy - hb, z_bottom], [cx + hb, cy - hb, z_bottom],
        [cx + hb, cy + hb, z_bottom], [cx - hb, cy + hb, z_bottom],
    ]
    faces = [
        [0, 1, 2], [0, 2, 3],          # top
        [4, 6, 5], [4, 7, 6],          # bottom
        [0, 4, 5], [0, 5, 1],          # -Y
        [1, 5, 6], [1, 6, 2],          # +X
        [2, 6, 7], [2, 7, 3],          # +Y
        [3, 7, 4], [3, 4, 0],          # -X
    ]
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    mesh.fix_normals()
    if mesh.volume < 0.0:
        mesh.invert()
    return mesh


def make_body():
    outer = box([-OUTER_W / 2.0, -OUTER_D / 2.0, 0.0], [OUTER_W / 2.0, OUTER_D / 2.0, BODY_H])

    # Open top and open front: one cut from the outside front face to the inside
    # back face, starting on top of the floor.
    cavity = box(
        [-INNER_W / 2.0, -OUTER_D / 2.0 - 1.0, FLOOR],
        [INNER_W / 2.0, OUTER_D / 2.0 - WALL, BODY_H + 1.0],
    )

    # 24 x 35 floor window, centred in X, flush with the inside back face.
    hole_front = -INNER_D / 2.0 + HOLE_FRONT_GAP           # -10.0
    hole_back = OUTER_D / 2.0 - WALL                       # +25.0
    window = box(
        [-HOLE_W / 2.0, hole_front, -1.0],
        [HOLE_W / 2.0, hole_back, FLOOR + 1.0],
    )

    feet = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            feet.append(
                tapered_pad(
                    sx * FOOT_CX,
                    sy * FOOT_CY,
                    FOOT_TOP,
                    FOOT_BOTTOM,
                    FOOT_BITE,
                    -FOOT_H,
                )
            )

    body = trimesh.boolean.difference([outer, cavity, window], engine="manifold")
    body = trimesh.boolean.union([body] + feet, engine="manifold")
    return body


def make_lid():
    plate = box(
        [-OUTER_W / 2.0, -OUTER_D / 2.0, BODY_H],
        [OUTER_W / 2.0, OUTER_D / 2.0, BODY_H + LID_T],
    )
    # Locating lip: sits against the inside of the walls, 0.2 mm clearance.
    lip_outer = box(
        [-(INNER_W / 2.0 - LID_CLEARANCE), -(INNER_D / 2.0 - LID_CLEARANCE), BODY_H - LID_LIP_H],
        [INNER_W / 2.0 - LID_CLEARANCE, INNER_D / 2.0 - LID_CLEARANCE, BODY_H + 1.0],
    )
    lip_inner = box(
        [-(INNER_W / 2.0 - LID_CLEARANCE - LID_LIP_T), -(INNER_D / 2.0 - LID_CLEARANCE - LID_LIP_T), BODY_H - LID_LIP_H - 1.0],
        [INNER_W / 2.0 - LID_CLEARANCE - LID_LIP_T, INNER_D / 2.0 - LID_CLEARANCE - LID_LIP_T, BODY_H + 2.0],
    )
    lip = trimesh.boolean.difference([lip_outer, lip_inner], engine="manifold")
    return trimesh.boolean.union([plate, lip], engine="manifold")


def drop_to_bed(mesh):
    mesh = mesh.copy()
    mesh.apply_translation([0.0, 0.0, -mesh.bounds[0][2]])
    return mesh


def export(mesh, name, drop=True):
    mesh = drop_to_bed(mesh) if drop else mesh
    path = OUT_DIR / name
    mesh.export(path)
    print(
        f"{name}: watertight={mesh.is_watertight} "
        f"volume={mesh.volume:.1f} mm3 mass_pla={mesh.volume * PLA_DENSITY / 1000.0:.1f} g "
        f"bounds={mesh.extents.round(2).tolist()}"
    )
    return path


def main():
    body = make_body()
    lid = make_lid()

    assembly = trimesh.boolean.union([body, lid], engine="manifold")

    export(body, "buck_boost_case_body.stl")
    export(lid, "buck_boost_case_lid.stl")
    export(assembly, "buck_boost_case_assembly.stl")

    print(
        f"outer {OUTER_W} x {OUTER_D} x {TOTAL_H} mm, "
        f"inside {INNER_W} x {INNER_D} x {INNER_H} mm, "
        f"wall/floor {WALL}/{FLOOR} mm"
    )
    print(
        f"floor window {HOLE_W} x {HOLE_D} mm: y {-INNER_D / 2.0 + HOLE_FRONT_GAP:.1f}"
        f" .. {OUTER_D / 2.0 - WALL:.1f} (inside front face at y {-INNER_D / 2.0:.1f})"
    )
    print(
        f"feet: 4 x {FOOT_TOP} -> {FOOT_BOTTOM} mm flared pads, {FOOT_H} mm tall, "
        f"bottom centres at (+-{FOOT_CX:.2f}, +-{FOOT_CY:.2f}), "
        f"footprint {2.0 * FOOT_CX + FOOT_BOTTOM:.2f} x {2.0 * FOOT_CY + FOOT_BOTTOM:.2f} mm"
    )
    print(
        f"lid: {OUTER_W} x {OUTER_D} x {LID_T} mm plate + {LID_LIP_H} mm lip, "
        f"lip {INNER_W - 2.0 * LID_CLEARANCE:.1f} x {INNER_D - 2.0 * LID_CLEARANCE:.1f} mm, "
        f"clearance {LID_CLEARANCE} mm/side"
    )


if __name__ == "__main__":
    main()
