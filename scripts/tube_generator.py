import numpy as np
import trimesh
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COVER_DIR = REPO_ROOT / "models" / "covers"
OUT_DIR = REPO_ROOT / "models" / "duct"
COVERS = ["male-cover.stl", "female-cover.stl"]
Z_TOP = 69.105
Z_SEAT = 63.454
Z_SAMPLE = 40.0
HEIGHT = 25.0
TOP_CHAMFER = 0.5
SECTIONS = 240
SMOOTH_DEG = 3


def outer_radius(mesh, z, angles):
    tri = mesh.triangles
    v0 = tri[:, 0]
    e1 = tri[:, 1] - v0
    e2 = tri[:, 2] - v0
    values = np.full(len(angles), np.nan)
    for i, ang in enumerate(angles):
        th = np.radians(ang)
        d = np.array([np.cos(th), np.sin(th), 0.0])
        origin = np.array([0.0, 0.0, z]) + d * 400.0
        direction = -d
        p = np.cross(direction, e2)
        det = np.einsum("ij,ij->i", e1, p)
        good_det = np.abs(det) > 1e-12
        inv = np.where(good_det, 1.0 / det, 0.0)
        t = np.subtract(origin, v0)
        u = np.einsum("ij,ij->i", t, p) * inv
        q = np.cross(t, e1)
        v = np.einsum("j,ij->i", direction, q) * inv
        tt = np.einsum("ij,ij->i", e2, q) * inv
        hit = good_det & (u >= -1e-9) & (u <= 1.0 + 1e-9) & (v >= -1e-9) & (u + v <= 1.0 + 1e-9) & (tt > 1e-6)
        if hit.any():
            values[i] = 400.0 - tt[hit].min()
    return values


def smooth_circular(values, window):
    if window <= 1:
        return values
    kernel = np.ones(window) / window
    padded = np.concatenate([values[-window:], values, values[:window]])
    return np.convolve(padded, kernel, mode="same")[window:-window]


def cover_outline():
    angles = np.arange(0.0, 360.0, 1.0)
    samples = []
    for name in COVERS:
        mesh = trimesh.load(COVER_DIR / name, force="mesh")
        samples.append(outer_radius(mesh, Z_SAMPLE, angles))
    stack = np.vstack(samples)
    outline = np.nanmax(stack, axis=0)
    missing = np.isnan(outline)
    if missing.any():
        known = np.where(~missing)[0]
        outline[missing] = np.interp(np.where(missing)[0], known, outline[known], period=len(outline))
    return angles, smooth_circular(outline, SMOOTH_DEG)


def make_tube(angles, outline, wall, seat_rise, height, top_chamfer):
    section_angles = np.linspace(0.0, 360.0, SECTIONS, endpoint=False)
    radius_outer = np.interp(section_angles, angles, outline, period=360.0)
    radius_inner = radius_outer - wall
    vertices = []
    for i in range(SECTIONS):
        th = np.radians(section_angles[i])
        cos_t = np.cos(th)
        sin_t = np.sin(th)
        ring = [
            (radius_outer[i], 0.0),
            (radius_outer[i], height - top_chamfer),
            (radius_outer[i] - top_chamfer, height),
            (radius_inner[i] + top_chamfer, height),
            (radius_inner[i], height - top_chamfer),
            (radius_inner[i], -seat_rise),
        ]
        for radius, z in ring:
            vertices.append([radius * cos_t, radius * sin_t, z])
    points_per_ring = 6
    faces = []
    for i in range(SECTIONS):
        j = (i + 1) % SECTIONS
        for k in range(points_per_ring):
            m = (k + 1) % points_per_ring
            a = i * points_per_ring + k
            b = i * points_per_ring + m
            c = j * points_per_ring + k
            d = j * points_per_ring + m
            faces.append([a, c, d])
            faces.append([a, d, b])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    if mesh.volume < 0.0:
        mesh.invert()
    return mesh


def export(mesh, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    mesh.export(path)
    print(f"{name}: watertight={mesh.is_watertight} volume={mesh.volume:.1f} mm3 mass_pla={mesh.volume * 1.24 / 1000.0:.1f} g")
    return path


def main():
    angles, outline = cover_outline()
    wall = 6.35
    seat_rise = (Z_TOP - Z_SEAT)
    tube = make_tube(angles, outline, wall, seat_rise, HEIGHT, TOP_CHAMFER)
    ring = make_tube(angles, outline, wall, seat_rise, 8.0, TOP_CHAMFER)
    export(tube, "extension_tube.stl")
    export(ring, "tube_fit_test.stl")
    print(f"outline radius min={outline.min():.3f} max={outline.max():.3f} (OD {2*outline.min():.2f} .. {2*outline.max():.2f})")
    print(f"bore radius min={outline.min()-wall:.3f} max={outline.max()-wall:.3f}")
    print(f"wall={wall:.2f} mm  seat rise={seat_rise:.3f} mm  seat angle={np.degrees(np.arctan2(seat_rise, wall)):.2f} deg from horizontal")
    print(f"height above cover={HEIGHT:.1f} mm  total axial={HEIGHT + seat_rise:.2f} mm")


if __name__ == "__main__":
    main()
