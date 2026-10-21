import numpy as np
import trimesh
from pathlib import Path
from scipy.interpolate import PchipInterpolator
from trimesh.transformations import rotation_matrix

ARM_HEIGHT = 25.87175
TIP_RADIUS = 63.25
TIP_WIDTH = 2.324
ROOT_WIDTH = 8.0
ARM_START = -2.0
HOLE_CENTER_RADIUS = 27.577
HOLE_DIAMETER = 4.0
HOLE_DEPTH = 7.5
CHAMFER_RADIUS = 2.4
CHAMFER_DEPTH = 0.5
RING_RADIUS = 34.0
RING_THICKNESS = 1.2
CORNER_RADIUS = 1.0
OUT_DIR = Path(__file__).resolve().parent
ASSEMBLY_OFFSET = np.array([0.0, -1.6201, 54.8102])

WIDTH_KNOTS_R = np.array([0, 8, 16, 18, 20, 30, 31.5, 32, 34, 36, 38, 45, 55, 61, TIP_RADIUS])
WIDTH_KNOTS_W = np.array([8.0, 6.4, 4.6, 4.2, 8.0, 8.0, 8.0, 7.4, 6.8, 5.6, 3.8, 3.2, 3.0, 2.6, TIP_WIDTH])
WIDTH_FUNCTION = PchipInterpolator(WIDTH_KNOTS_R, WIDTH_KNOTS_W, extrapolate=True)
RADIAL_STATIONS = np.unique(np.r_[np.arange(ARM_START, TIP_RADIUS, 0.5), TIP_RADIUS, WIDTH_KNOTS_R[(WIDTH_KNOTS_R > ARM_START) & (WIDTH_KNOTS_R < TIP_RADIUS)]])


def arm_width(radius):
    radius = np.asarray(radius, dtype=float)
    return np.where(radius < 0.0, ROOT_WIDTH, WIDTH_FUNCTION(np.clip(radius, 0.0, TIP_RADIUS)))


def rounded_rect(width, height, corner_radius, segments=8):
    corner_radius = float(min(corner_radius, width / 2.0 - 1e-6, height / 2.0 - 1e-6))
    corners = [
        (width / 2.0 - corner_radius, -height / 2.0 + corner_radius, -90.0, 0.0),
        (width / 2.0 - corner_radius, height / 2.0 - corner_radius, 0.0, 90.0),
        (-width / 2.0 + corner_radius, height / 2.0 - corner_radius, 90.0, 180.0),
        (-width / 2.0 + corner_radius, -height / 2.0 + corner_radius, 180.0, 270.0),
    ]
    points = []
    for center_x, center_z, angle_start, angle_end in corners:
        for angle in np.linspace(np.radians(angle_start), np.radians(angle_end), segments):
            points.append([center_x + corner_radius * np.cos(angle), center_z + corner_radius * np.sin(angle)])
    return np.array(points)


def make_arm(theta):
    polygons = []
    for radius in RADIAL_STATIONS:
        width = float(arm_width(radius))
        corner_radius = min(CORNER_RADIUS, width / 2.0 - 0.01)
        polygons.append(rounded_rect(width, ARM_HEIGHT, corner_radius, segments=8))
    point_count = len(polygons[0])
    vertices = []
    for radius, polygon in zip(RADIAL_STATIONS, polygons):
        for tangent, height in polygon:
            vertices.append([radius, tangent, height])
    faces = []
    for station in range(len(RADIAL_STATIONS) - 1):
        for point in range(point_count):
            a = station * point_count + point
            b = station * point_count + (point + 1) % point_count
            c = (station + 1) * point_count + point
            d = (station + 1) * point_count + (point + 1) % point_count
            faces.append([a, b, d])
            faces.append([a, d, c])
    inner_center = len(vertices)
    vertices.append([RADIAL_STATIONS[0], 0.0, 0.0])
    for point in range(point_count):
        faces.append([inner_center, (point + 1) % point_count, point])
    outer_center = len(vertices)
    vertices.append([RADIAL_STATIONS[-1], 0.0, 0.0])
    base = (len(RADIAL_STATIONS) - 1) * point_count
    for point in range(point_count):
        faces.append([outer_center, base + point, base + (point + 1) % point_count])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    if mesh.volume < 0.0:
        mesh.invert()
    if abs(theta) > 1e-12:
        mesh.apply_transform(rotation_matrix(theta, [0.0, 0.0, 1.0]))
    return mesh


def make_ring():
    outer_radius = RING_RADIUS + RING_THICKNESS / 2.0
    inner_radius = RING_RADIUS - RING_THICKNESS / 2.0
    outer = trimesh.creation.cylinder(radius=outer_radius, height=ARM_HEIGHT, sections=192)
    inner = trimesh.creation.cylinder(radius=inner_radius, height=ARM_HEIGHT + 2.0, sections=192)
    mesh = trimesh.boolean.difference([outer, inner], engine="manifold")
    mesh.fix_normals()
    if mesh.volume < 0.0:
        mesh.invert()
    return mesh


def make_frustum(radius_bottom, radius_top, z_bottom, z_top, sections=64):
    vertices = []
    faces = []
    for radius, height in [(radius_bottom, z_bottom), (radius_top, z_top)]:
        for index in range(sections):
            angle = 2.0 * np.pi * index / sections
            vertices.append([radius * np.cos(angle), radius * np.sin(angle), height])
    for index in range(sections):
        next_index = (index + 1) % sections
        faces.append([index, next_index, sections + next_index])
        faces.append([index, sections + next_index, sections + index])
    bottom_center = len(vertices)
    vertices.append([0.0, 0.0, z_bottom])
    for index in range(sections):
        next_index = (index + 1) % sections
        faces.append([bottom_center, next_index, index])
    top_center = len(vertices)
    vertices.append([0.0, 0.0, z_top])
    for index in range(sections):
        next_index = (index + 1) % sections
        faces.append([top_center, sections + index, sections + next_index])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    if mesh.volume < 0.0:
        mesh.invert()
    return mesh


def make_hole_drill(x, y):
    top = ARM_HEIGHT / 2.0
    cylinder = trimesh.creation.cylinder(radius=HOLE_DIAMETER / 2.0, height=HOLE_DEPTH + 1.0, sections=64)
    cylinder.apply_translation([x, y, top - HOLE_DEPTH + (HOLE_DEPTH + 1.0) / 2.0])
    chamfer = make_frustum(HOLE_DIAMETER / 2.0, CHAMFER_RADIUS, top - CHAMFER_DEPTH, top + 0.01, sections=64)
    chamfer.apply_translation([x, y, 0.0])
    drill = trimesh.boolean.union([cylinder, chamfer], engine="manifold")
    return drill


def main():
    arms = [make_arm(theta) for theta in [0.0, np.pi / 2.0, np.pi, -np.pi / 2.0]]
    ring = make_ring()
    cross = trimesh.boolean.union(arms + [ring], engine="manifold")
    for theta in [0.0, np.pi / 2.0, np.pi, -np.pi / 2.0]:
        x = HOLE_CENTER_RADIUS * np.cos(theta)
        y = HOLE_CENTER_RADIUS * np.sin(theta)
        cross = trimesh.boolean.difference([cross, make_hole_drill(x, y)], engine="manifold")
    if not cross.is_watertight:
        raise RuntimeError("generated mesh is not watertight")
    centered_path = OUT_DIR / "cross_v2.stl"
    assembly_path = OUT_DIR / "cross_v2_assembly.stl"
    cross.export(centered_path)
    assembly = cross.copy()
    assembly.apply_translation(ASSEMBLY_OFFSET)
    assembly.export(assembly_path)
    print(f"volume_mm3={cross.volume:.1f}")
    print(f"mass_pla_g={cross.volume * 1.24 / 1000.0:.1f}")
    print(f"faces={len(cross.faces)}")
    print(f"saved={centered_path}")
    print(f"saved={assembly_path}")


if __name__ == "__main__":
    main()
