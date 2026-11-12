"""Split the boat bench interiors into a body and separately printable leg frames.

The lower supports are cut off at z = 193.4, where they meet the seat body.
They can be two long leg frames (regular benches) or one long frame plus two
free-standing legs (the hole variants).  The body gets one-layer (0.2 mm)
alignment pockets at all four leg positions, 0.5 mm larger than the matching
keys, plus an engraved dot code (1-4) next to every pocket.

The leg pieces get matching raised keys and engraved dots on their outward
faces.  The dot counts tell you which leg goes where: 1 = low-X/low-Y,
2 = high-X/low-Y, 3 = low-X/high-Y, 4 = high-X/high-Y.

The original boatinside/boatinside2 files are not modified.
"""

import numpy as np
import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BOAT_DIR = BASE_DIR / "models" / "boat"
LEG_DIR = BOAT_DIR / "legs_inside"
LEG_DIR.mkdir(parents=True, exist_ok=True)

CUT_Z = 200.0
LAYER = 0.2          # one 0.2 mm layer
CLEARANCE = 0.5      # 0.5 mm around each leg post
DOT_R = 0.6
DOT_DEPTH = 0.35
DOT_SPACING = 1.35


def clean(mesh):
    mesh.merge_vertices()
    trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def box(extents, center):
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def cyl_x(radius, height, x, y, z, sections=24):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    mesh.apply_translation([x, y, z])
    return mesh


def cyl_z(radius, height, x, y, z, sections=24):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    mesh.apply_translation([x, y, z])
    return mesh


def split_at(mesh):
    b = mesh.bounds
    cx, cy = (b[0][0] + b[1][0]) / 2.0, (b[0][1] + b[1][1]) / 2.0
    lower_box = box([600.0, 600.0, CUT_Z - b[0][2] + 20.0],
                    [cx, cy, (b[0][2] - 20.0 + CUT_Z) / 2.0])
    upper_box = box([600.0, 600.0, b[1][2] - CUT_Z + 20.0],
                    [cx, cy, (CUT_Z + b[1][2] + 20.0) / 2.0])
    lower = clean(trimesh.boolean.intersection([mesh, lower_box], engine="manifold"))
    upper = clean(trimesh.boolean.intersection([mesh, upper_box], engine="manifold"))
    return upper, lower


def top_box(frame):
    """Top contact footprint of one lower leg component."""
    v = frame.vertices
    v = v[v[:, 2] > CUT_Z - 0.8]
    return (float(v[:, 0].min()), float(v[:, 0].max()),
            float(v[:, 1].min()), float(v[:, 1].max()))


def label_for(x, y, bounds):
    mid_x = (bounds[0][0] + bounds[1][0]) / 2.0
    mid_y = (bounds[0][1] + bounds[1][1]) / 2.0
    if y < mid_y:
        return 1 if x < mid_x else 2
    return 3 if x < mid_x else 4


def component_contacts(frame, bounds):
    """Return (x_center, y_center, label, outward_x_face) contact points."""
    x0, x1, y0, y1 = top_box(frame)
    cy = (y0 + y1) / 2.0
    out = []
    if x1 - x0 < 50.0:
        # A short, free-standing leg: one key in the middle.
        xc = (x0 + x1) / 2.0
        label = label_for(xc, cy, bounds)
        x_face = x0 if label in (1, 3) else x1
        out.append((xc, cy, label, x_face))
    else:
        # A long rail: one key at each end.
        for xc, x_face in ((x0 + 8.0, x0), (x1 - 8.0, x1)):
            out.append((xc, cy, label_for(xc, cy, bounds), x_face))
    return out


def add_leg_features(leg, contacts):
    key_h = LAYER + 0.3
    dots = []
    for xc, cy, label, x_face in contacts:
        key = box([8.0, 2.0, key_h], [xc, cy, CUT_Z - 0.3 + key_h / 2.0])
        leg = trimesh.boolean.union([leg, key], engine="manifold")
        for i in range(label):
            y = cy + (i - (label - 1) / 2.0) * DOT_SPACING
            dots.append(cyl_x(DOT_R, DOT_DEPTH + 0.2, x_face, y, CUT_Z - 5.0))
    if dots:
        leg = trimesh.boolean.difference([leg] + dots, engine="manifold")
    return clean(leg)


def add_body_features(body, contacts):
    pockets = []
    dots = []
    center_y = (body.bounds[0][1] + body.bounds[1][1]) / 2.0
    for xc, cy, label, _ in contacts:
        # 10 x 3 pocket around an 8 x 2 key = 0.5 mm clearance every side.
        pockets.append(box([10.0, 3.0, LAYER], [xc, cy, CUT_Z + LAYER / 2.0]))
        side = 1.0 if cy < center_y else -1.0
        # label dots sit just inboard of the pocket on the body underside
        y = cy + side * 4.5
        for i in range(label):
            yy = y + (i - (label - 1) / 2.0) * DOT_SPACING
            dots.append(cyl_z(DOT_R, DOT_DEPTH + 0.2, xc, yy, CUT_Z + DOT_DEPTH / 2.0))
    body = trimesh.boolean.difference([body] + pockets + dots, engine="manifold")
    return clean(body)


def process(name):
    mesh = trimesh.load(BOAT_DIR / name, force="mesh", process=True)
    body, lower = split_at(mesh)
    parts = sorted(lower.split(only_watertight=False),
                   key=lambda p: (p.bounds[0][1], p.bounds[0][0]))
    parts = [clean(f) for f in parts if f.volume > 1000]

    contacts_per_part = [component_contacts(f, mesh.bounds) for f in parts]
    all_contacts = [c for cs in contacts_per_part for c in cs]
    if len(all_contacts) != 4:
        raise RuntimeError(f"{name}: expected 4 alignment keys, got {len(all_contacts)}")

    body = add_body_features(body, all_contacts)
    parts = [add_leg_features(f, cs) for f, cs in zip(parts, contacts_per_part)]

    stem = Path(name).stem.rstrip("_")
    out_body = BOAT_DIR / f"{stem}_optimized.stl"
    body.export(out_body)
    print(f"{out_body.name}: watertight={body.is_watertight} vol={body.volume:.1f} bounds={body.bounds.round(1).tolist()}")
    for i, frame in enumerate(parts, start=1):
        out_leg = LEG_DIR / f"{stem}_leg_{i}.stl"
        frame.export(out_leg)
        print(f"legs_inside/{out_leg.name}: watertight={frame.is_watertight} vol={frame.volume:.1f} bounds={frame.bounds.round(1).tolist()}")


def main():
    for name in ("boatinside.stl", "boatinside2.stl",
                 "boatinside_hole_.stl", "boatinside_hole2.stl"):
        process(name)


if __name__ == "__main__":
    main()
