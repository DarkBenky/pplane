import math
import numpy as np
import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "models" / "boat"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOP_Z = 300.0
KEEL_Z = 114.0
CHINE_Z = 145.0
TOP_Y = 188.0
CHINE_Y = 145.0

X_INBOARD = 110.0
X_OUTBOARD = 350.0
X_CAVITY_END = 345.0
TAPER_START = 335.0
TAPER_END_SCALE = 0.55

SKIN = 4.0
CLEARANCE = 1.0
RECESS_X0, RECESS_X1 = 190.0, 270.0
RECESS_Y = 125.0
RECESS_DEPTH = 1.2
FILL_HOLE_D = 24.0
VENT_HOLE_D = 8.0
FILL_HOLE_X = 150.0
VENT_HOLE_X = 300.0
FILL_HOLE_Y = 90.0
VENT_HOLE_Y = 80.0


def scale_at(x):
    if x <= TAPER_START:
        return 1.0
    t = min(max((x - TAPER_START) / (X_OUTBOARD - TAPER_START), 0.0), 1.0)
    return 1.0 + (TAPER_END_SCALE - 1.0) * t


def base_profile(x):
    s = scale_at(x)
    return [(-TOP_Y * s, TOP_Z), (TOP_Y * s, TOP_Z), (CHINE_Y * s, CHINE_Z), (0.0, KEEL_Z), (-CHINE_Y * s, CHINE_Z)]


def signed_area(points):
    return 0.5 * sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points)))


def line_intersection(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return (px, py)


def offset_polygon(points, distance):
    pts = list(points)
    if signed_area(pts) > 0:
        pts.reverse()
    n = len(pts)
    lines = []
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        nx, ny = -dy / length, dx / length
        lines.append(((x0 + distance * nx, y0 + distance * ny), (x1 + distance * nx, y1 + distance * ny)))
    return [line_intersection(lines[i - 1][0], lines[i - 1][1], lines[i][0], lines[i][1]) for i in range(n)]


def loft(profiles, xs):
    n = len(profiles[0])
    vertices = []
    for x, profile in zip(xs, profiles):
        for y, z in profile:
            vertices.append([x, y, z])
    faces = []
    for i in range(len(xs) - 1):
        for j in range(n):
            jn = (j + 1) % n
            a = i * n + j
            b = i * n + jn
            c = (i + 1) * n + j
            d = (i + 1) * n + jn
            faces.append([a, b, d])
            faces.append([a, d, c])
    for cap_index, x in [(0, xs[0]), (len(xs) - 1, xs[-1])]:
        base = cap_index * n
        center = len(vertices)
        vertices.append([x, np.mean([p[0] for p in profiles[cap_index]]), np.mean([p[1] for p in profiles[cap_index]])])
        for j in range(n):
            if cap_index == 0:
                faces.append([center, (j + 1) % n, j])
            else:
                faces.append([center, base + j, base + (j + 1) % n])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def box_at(extents, center):
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def cyl_z(radius, height, x, y, z, sections=64):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    mesh.apply_translation([x, y, z])
    return mesh


def make_full_cap():
    xs_outer = [110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0,
                210.0, 220.0, 230.0, 240.0, 250.0, 260.0, 270.0, 280.0, 290.0, 300.0,
                310.0, 320.0, 330.0, 335.0, 340.0, 345.0, 350.0]
    xs_cavity = [109.0] + [x for x in xs_outer if x <= X_CAVITY_END]
    outer = [offset_polygon(base_profile(x), SKIN) for x in xs_outer]
    inner = [offset_polygon(base_profile(x), CLEARANCE) for x in xs_cavity]
    outer_mesh = loft(outer, xs_outer)
    inner_mesh = loft(inner, xs_cavity)
    cap = trimesh.boolean.difference([outer_mesh, inner_mesh], engine="manifold")

    cuts = []
    for y in (-FILL_HOLE_Y, FILL_HOLE_Y):
        cuts.append(cyl_z(FILL_HOLE_D / 2.0, 12.0, FILL_HOLE_X, y, TOP_Z + SKIN - 1.0, 64))
    for y in (-VENT_HOLE_Y, VENT_HOLE_Y):
        cuts.append(cyl_z(VENT_HOLE_D / 2.0, 12.0, VENT_HOLE_X, y, TOP_Z + SKIN - 1.0, 48))
    recess = box_at([RECESS_X1 - RECESS_X0, 2.0 * RECESS_Y, RECESS_DEPTH + 1.0],
                    [(RECESS_X0 + RECESS_X1) / 2.0, 0.0, TOP_Z + SKIN + 0.5 - (RECESS_DEPTH + 1.0) / 2.0])
    cuts.append(recess)
    cap = trimesh.boolean.difference([cap] + cuts, engine="manifold")
    return cap


def split_half(cap, sign):
    cutter = box_at([460.0, 340.0, 420.0], [230.0, sign * 170.0, 210.0])
    half = trimesh.boolean.intersection([cap, cutter], engine="manifold")
    half.fix_normals()
    if half.volume < 0:
        half.invert()
    return half


def mirror_y(mesh):
    mirrored = mesh.copy()
    vertices = mirrored.vertices.copy()
    vertices[:, 1] *= -1.0
    mirrored = trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=True)
    mirrored.fix_normals()
    if mirrored.volume < 0:
        mirrored.invert()
    return mirrored


def export(mesh, name):
    path = OUT_DIR / name
    mesh.export(path)
    print(f"{name}: watertight={mesh.is_watertight} volume={mesh.volume:.1f} mm3 bounds={mesh.bounds.round(2).tolist()}")
    return path


def main():
    cap = make_full_cap()
    export(cap, "boat_bow_stern_cap_full.stl")
    port = split_half(cap, 1.0)
    export(port, "boat_bow_stern_cap_port.stl")
    export(mirror_y(port), "boat_bow_stern_cap_starboard.stl")
    print("3 mm skin (4 mm outside the old hull, 1 mm liner clearance), open inboard end for foam; same cap at bow and stern.")
    print("Port/starboard halves fit a 256 mm printer. Rotate 180 deg for the stern.")


if __name__ == "__main__":
    main()
