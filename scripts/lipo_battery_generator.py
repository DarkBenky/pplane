import numpy as np
import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "models" / "battery"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LIPO_L = 113.0
LIPO_W = 43.0
LIPO_H = 37.0
CORNER_RADIUS = 4.0
EDGE_CHAMFER = 1.2

LABEL_L = 82.0
LABEL_W = 27.0
LABEL_DEPTH = 0.5
CELL_DOT_D = 6.0
CELL_DOT_DEPTH = 0.4
CELL_DOT_X = [-43.0, -29.0, -15.0, -1.0, 13.0, 27.0]

BOTTOM_FOOT = 8.0
BOTTOM_RECESS = 0.8

XT90_W = 20.0
XT90_H = 12.0
XT90_DEPTH = 8.0
XT90_Z = 22.0
BULLET_D = 5.5
BULLET_DEPTH = 5.0
BULLET_Y = 6.0

BALANCE_W = 22.0
BALANCE_H = 8.0
BALANCE_DEPTH = 5.0
BALANCE_Z = 8.0
BALANCE_PINS = 7
BALANCE_PIN_W = 1.2
BALANCE_PIN_PITCH = 3.0
BALANCE_PIN_DEPTH = 3.0
BALANCE_PIN_H = 5.5


def rounded_rect_points(length, width, radius, sections_per_corner=12):
    radius = min(radius, length / 2.0, width / 2.0)
    cx = length / 2.0 - radius
    cy = width / 2.0 - radius
    points = []
    corners = [
        (cx, -cy, -0.5 * np.pi, 0.0),
        (cx, cy, 0.0, 0.5 * np.pi),
        (-cx, cy, 0.5 * np.pi, np.pi),
        (-cx, -cy, np.pi, 1.5 * np.pi),
    ]
    for x0, y0, a0, a1 in corners:
        for angle in np.linspace(a0, a1, sections_per_corner + 1):
            points.append([x0 + radius * np.cos(angle), y0 + radius * np.sin(angle)])
    return np.array(points)


def rounded_prism(length, width, radius, levels, sections_per_corner=16):
    outlines = []
    for _, inset in levels:
        outlines.append(rounded_rect_points(length - 2.0 * inset, width - 2.0 * inset, max(radius - inset, 0.05), sections_per_corner))
    count = len(outlines[0])
    vertices = []
    for (z, _), points in zip(levels, outlines):
        for x, y in points:
            vertices.append([x, y, z])
    faces = []
    for level in range(len(levels) - 1):
        for i in range(count):
            j = (i + 1) % count
            a = level * count + i
            b = level * count + j
            c = (level + 1) * count + i
            d = (level + 1) * count + j
            faces.append([a, b, d])
            faces.append([a, d, c])
    bottom_center = len(vertices)
    vertices.append([0.0, 0.0, levels[0][0]])
    for i in range(count):
        faces.append([bottom_center, (i + 1) % count, i])
    top_center = len(vertices)
    top_base = (len(levels) - 1) * count
    vertices.append([0.0, 0.0, levels[-1][0]])
    for i in range(count):
        faces.append([top_center, top_base + i, top_base + (i + 1) % count])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    if mesh.volume < 0.0:
        mesh.invert()
    return mesh


def box_at(extents, center):
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def cyl_at(radius, height, z, x=0.0, y=0.0, sections=64):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    mesh.apply_translation([x, y, z])
    return mesh


def cyl_x(radius, length, x, y, z, sections=64):
    mesh = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [0.0, 1.0, 0.0]))
    mesh.apply_translation([x, y, z])
    return mesh


def make_lipo():
    body = rounded_prism(
        LIPO_L,
        LIPO_W,
        CORNER_RADIUS,
        [
            (0.0, EDGE_CHAMFER * 0.67),
            (EDGE_CHAMFER * 0.67, 0.0),
            (LIPO_H - EDGE_CHAMFER, 0.0),
            (LIPO_H, EDGE_CHAMFER),
        ],
    )
    cuts = []
    label = rounded_prism(LABEL_L, LABEL_W, 3.0, [(0.0, 0.0), (LABEL_DEPTH, 0.0)])
    label.apply_translation([-8.0, 0.0, LIPO_H - LABEL_DEPTH])
    cuts.append(label)
    for x in CELL_DOT_X:
        cuts.append(cyl_at(CELL_DOT_D / 2.0, CELL_DOT_DEPTH, LIPO_H - LABEL_DEPTH - CELL_DOT_DEPTH / 2.0, x, 0.0, sections=48))

    xt90 = box_at([XT90_DEPTH, XT90_W, XT90_H], [LIPO_L / 2.0 - XT90_DEPTH / 2.0, 0.0, XT90_Z])
    cuts.append(xt90)
    for y in (-BULLET_Y, BULLET_Y):
        cuts.append(cyl_x(BULLET_D / 2.0, BULLET_DEPTH, LIPO_L / 2.0 - XT90_DEPTH - BULLET_DEPTH / 2.0, y, XT90_Z))

    balance = box_at([BALANCE_DEPTH, BALANCE_W, BALANCE_H], [LIPO_L / 2.0 - BALANCE_DEPTH / 2.0, 0.0, BALANCE_Z])
    cuts.append(balance)
    pin_start = -(BALANCE_PINS - 1) * BALANCE_PIN_PITCH / 2.0
    for i in range(BALANCE_PINS):
        y = pin_start + i * BALANCE_PIN_PITCH
        cuts.append(box_at(
            [BALANCE_PIN_DEPTH, BALANCE_PIN_W, BALANCE_PIN_H],
            [LIPO_L / 2.0 - BALANCE_DEPTH - BALANCE_PIN_DEPTH / 2.0, y, BALANCE_Z],
        ))

    recess = rounded_prism(
        LIPO_L - 2.0 * BOTTOM_FOOT,
        LIPO_W - 2.0 * BOTTOM_FOOT,
        3.0,
        [(0.0, 0.0), (BOTTOM_RECESS + 0.1, 0.0)],
    )
    recess.apply_translation([0.0, 0.0, -0.1])
    cuts.append(recess)

    mesh = trimesh.boolean.difference([body] + cuts, engine="manifold")
    return mesh


def main():
    mesh = make_lipo()
    path = OUT_DIR / "lipo_6s_113x43x37.stl"
    mesh.export(path)
    print(f"{path.name}: watertight={mesh.is_watertight} volume={mesh.volume:.1f} mm3")
    print(f"bounds={mesh.bounds.round(2).tolist()} extents={mesh.extents.round(2).tolist()}")
    print(f"L={LIPO_L} W={LIPO_W} H={LIPO_H}; XT90 socket + {BALANCE_PINS}-pin balance socket on +X end")


if __name__ == "__main__":
    main()
