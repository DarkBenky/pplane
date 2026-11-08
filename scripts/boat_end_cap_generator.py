import math
import numpy as np
import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "models" / "boat"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOP_Z = 300.0
KEEL_Z = 108.0
CHINE_Z = 145.0
TOP_Y = 188.0
CHINE_Y = 133.0
FLAT_Y = 60.0

X_INBOARD = 255.0
X_OUTBOARD = 500.0
X_STEM_START = 480.0
TAPER_START = 340.0
NOSE_TIP_SCALE = 0.005
RAKE_STEM = 15.0
JOINT_END = 280.0
JOINT_SKIN = 2.5

# The inside liner ends at x = 340.  The cap starts well inboard of that,
# covers the front 85 mm of the liner, and carries the bow forward to x = 500.
ROCKER_START = 340.0
ROCKER_HEIGHT = 70.0

SKIN = 3.0
CLEARANCE = 1.5
FILL_HOLE_D = 24.0
VENT_HOLE_D = 8.0
FILL_HOLE_X = 300.0
VENT_HOLE_X = 390.0
FILL_HOLE_Y = 90.0
VENT_HOLE_Y = 50.0


def scale_at(x):
    if x <= TAPER_START:
        return 1.0
    t = min(max((x - TAPER_START) / (X_OUTBOARD - TAPER_START), 0.0), 1.0)
    return 1.0 - (1.0 - NOSE_TIP_SCALE) * t


def rocker_at(x):
    if x <= ROCKER_START:
        return 0.0
    return ROCKER_HEIGHT * smoothstep((x - ROCKER_START) / (X_OUTBOARD - ROCKER_START))


def smoothstep(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def skin_at(x):
    return JOINT_SKIN + (SKIN - JOINT_SKIN) * smoothstep((x - X_INBOARD) / (JOINT_END - X_INBOARD))


def clearance_at(x):
    return CLEARANCE


def base_profile(x):
    s = scale_at(x)
    dz = rocker_at(x)
    return [(-TOP_Y * s, TOP_Z), (TOP_Y * s, TOP_Z), (CHINE_Y * s, CHINE_Z + dz), (FLAT_Y * s, CHINE_Z + dz), (0.0, KEEL_Z + dz), (-FLAT_Y * s, CHINE_Z + dz), (-CHINE_Y * s, CHINE_Z + dz)]


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
    # 2 mm stations; 255 ... 480, followed by a solid tip to 500.  The cavity
    # starts 1 mm inboard of the cap so the existing liner can slide inside it.
    xs_shell = [X_INBOARD + 2.0 * i for i in range(108)] + [X_STEM_START]
    xs_cavity = [X_INBOARD - 1.0] + xs_shell
    outer = [offset_polygon(base_profile(x), skin_at(x)) for x in xs_shell]
    inner = [offset_polygon(base_profile(x), clearance_at(x)) for x in xs_cavity]
    for x, profile in zip(xs_shell, outer):
        profile[4] = (0.0, KEEL_Z + rocker_at(x) - skin_at(x))
    for x, profile in zip(xs_cavity, inner):
        profile[4] = (0.0, KEEL_Z + rocker_at(x) - clearance_at(x))
    shell = trimesh.boolean.difference([loft(outer, xs_shell), loft(inner, xs_cavity)], engine="manifold")

    # Fine solid tip closing the last 10 mm of the continuous taper.
    nose_section = outer[-1]
    xs_nose = [X_STEM_START + i for i in range(21)]
    nose_profiles = []
    for x in xs_nose:
        t = (x - X_STEM_START) / (X_OUTBOARD - X_STEM_START)
        factor = 1.0 - (1.0 - NOSE_TIP_SCALE) * t
        nose_profiles.append([(y * factor, z) for y, z in nose_section])
    nose = loft(nose_profiles, xs_nose)
    top = TOP_Z + SKIN
    bottom = KEEL_Z + rocker_at(X_STEM_START) - SKIN
    vertices = nose.vertices.copy()
    t = np.clip((vertices[:, 0] - X_STEM_START) / (X_OUTBOARD - X_STEM_START), 0.0, 1.0)
    zfrac = (top - vertices[:, 2]) / (top - bottom)
    vertices[:, 0] = X_STEM_START + (X_OUTBOARD - X_STEM_START) * t * (1.0 - (RAKE_STEM / (X_OUTBOARD - X_STEM_START)) * zfrac)
    nose = trimesh.Trimesh(vertices=vertices, faces=nose.faces, process=True)
    nose.fix_normals()
    cap = trimesh.boolean.union([shell, nose], engine="manifold")

    cuts = []
    for y in (-FILL_HOLE_Y, FILL_HOLE_Y):
        cuts.append(cyl_z(FILL_HOLE_D / 2.0, 12.0, FILL_HOLE_X, y, TOP_Z + SKIN - 1.0, 64))
    for y in (-VENT_HOLE_Y, VENT_HOLE_Y):
        cuts.append(cyl_z(VENT_HOLE_D / 2.0, 12.0, VENT_HOLE_X, y, TOP_Z + SKIN - 1.0, 48))
    cap = trimesh.boolean.difference([cap] + cuts, engine="manifold")
    return cap


def split_half(cap, sign):
    cutter = box_at([400.0, 340.0, 420.0], [380.0, sign * 170.0, 210.0])
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
    starboard = mirror_y(port)
    starboard.merge_vertices()
    trimesh.repair.fill_holes(starboard)
    trimesh.repair.fix_normals(starboard)
    export(starboard, "boat_bow_stern_cap_starboard.stl")
    print("1.5 mm skin, flat-pad/V hull section, straight sharp taper to a fine raked tip, open inboard end for foam; same cap at both ends.")
    print("Port/starboard halves fit a 256 mm printer. Rotate 180 deg for the stern.")


if __name__ == "__main__":
    main()
