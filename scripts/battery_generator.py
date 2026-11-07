import numpy as np
import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "models" / "battery"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BATTERY_L = 151.2
BATTERY_W = 65.6
BATTERY_H = 99.4
CASE_HEIGHT = 94.4
CORNER_RADIUS = 3.0
EDGE_CHAMFER = 1.0
BOTTOM_RECESS = 0.8
BOTTOM_FOOT = 10.0

VENT_COUNT = 6
VENT_DIAMETER = 12.0
VENT_DEPTH = 0.35

TERMINAL_X = 55.0
TERMINAL_Y = 20.0
TERMINAL_BASE_L = 16.0
TERMINAL_BASE_W = 8.0
TERMINAL_BASE_H = 2.0
TERMINAL_TAB_L = 10.0
TERMINAL_TAB_W = 1.2
TERMINAL_TAB_H = 3.0
MARK_SIZE = 5.0
MARK_THICKNESS = 0.8
MARK_HEIGHT = 0.4


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


def rounded_prism(length, width, radius, levels, sections_per_corner=12):
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


def make_case():
    return rounded_prism(
        BATTERY_L,
        BATTERY_W,
        CORNER_RADIUS,
        [
            (0.0, EDGE_CHAMFER),
            (EDGE_CHAMFER, 0.0),
            (CASE_HEIGHT - EDGE_CHAMFER, 0.0),
            (CASE_HEIGHT, EDGE_CHAMFER),
        ],
    )


def make_terminals():
    parts = []
    for y in (-TERMINAL_Y, TERMINAL_Y):
        base = rounded_prism(TERMINAL_BASE_L, TERMINAL_BASE_W, 1.0, [(0.0, 0.0), (TERMINAL_BASE_H, 0.0)])
        base.apply_translation([TERMINAL_X, y, CASE_HEIGHT])
        tab = box_at(
            [TERMINAL_TAB_L, TERMINAL_TAB_W, TERMINAL_TAB_H],
            [TERMINAL_X, y, CASE_HEIGHT + TERMINAL_BASE_H + TERMINAL_TAB_H / 2.0],
        )
        parts.extend([base, tab])
    return parts


def make_marks():
    plus_y = -TERMINAL_Y
    minus_y = TERMINAL_Y
    mark_z = CASE_HEIGHT + MARK_HEIGHT / 2.0
    plus_a = box_at([MARK_SIZE, MARK_THICKNESS, MARK_HEIGHT], [TERMINAL_X + 13.0, plus_y, mark_z])
    plus_b = box_at([MARK_THICKNESS, MARK_SIZE, MARK_HEIGHT], [TERMINAL_X + 13.0, plus_y, mark_z])
    minus = box_at([MARK_SIZE, MARK_THICKNESS, MARK_HEIGHT], [TERMINAL_X + 13.0, minus_y, mark_z])
    return [plus_a, plus_b, minus]


def make_battery():
    mesh = make_case()
    mesh = trimesh.boolean.union([mesh] + make_terminals() + make_marks(), engine="manifold")
    cuts = []
    vent_x = np.linspace(-60.0, 60.0, VENT_COUNT)
    for x in vent_x:
        cuts.append(cyl_at(VENT_DIAMETER / 2.0, VENT_DEPTH + 0.5, CASE_HEIGHT - VENT_DEPTH / 2.0 + 0.25, x, 0.0))
    recess = rounded_prism(
        BATTERY_L - 2.0 * BOTTOM_FOOT,
        BATTERY_W - 2.0 * BOTTOM_FOOT,
        2.0,
        [(0.0, 0.0), (BOTTOM_RECESS + 0.1, 0.0)],
    )
    recess.apply_translation([0.0, 0.0, -0.1])
    cuts.append(recess)
    mesh = trimesh.boolean.difference([mesh] + cuts, engine="manifold")
    return mesh


def main():
    mesh = make_battery()
    path = OUT_DIR / "lead_acid_12v_7.2ah.stl"
    mesh.export(path)
    print(f"{path.name}: watertight={mesh.is_watertight} volume={mesh.volume:.1f} mm3")
    print(f"bounds={mesh.bounds.round(2).tolist()} extents={mesh.extents.round(2).tolist()}")
    print(f"L={BATTERY_L} W={BATTERY_W} H={BATTERY_H}, case={CASE_HEIGHT}, terminals={TERMINAL_BASE_H + TERMINAL_TAB_H}")


if __name__ == "__main__":
    main()
