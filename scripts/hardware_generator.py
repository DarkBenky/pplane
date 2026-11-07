import numpy as np
import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "models" / "hardware"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INSERT_BODY_D = 3.95
INSERT_BODY_L = 5.92
INSERT_BORE_D = 2.4
INSERT_CHAMFER_OUTER = 0.3
INSERT_CHAMFER_INNER = 0.2

SCREW_HEAD_D = 5.5
SCREW_HEAD_L = 3.0
SCREW_LENGTH = 10.0
SCREW_CORE_D = 2.5
SCREW_MAJOR_D = 3.0
SCREW_PITCH = 0.5
SCREW_SOCKET_AF = 2.5
SCREW_SOCKET_DEPTH = 1.6

NUT_AF = 5.5
NUT_HEIGHT = 2.4
NUT_BORE_D = 2.5

WASHER_OD = 7.0
WASHER_ID = 3.2
WASHER_T = 1.0


def cyl(radius, height, z, sections=64):
    m = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    m.apply_translation([0.0, 0.0, z])
    return m


def hexprism(across_flats, height, z, sections=6):
    radius = across_flats / np.sqrt(3.0)
    m = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    m.apply_translation([0.0, 0.0, z])
    return m


def helix_tube(path_radius, tube_radius, pitch, height, section_steps=8, steps_per_turn=32):
    turns = height / pitch
    count = int(turns * steps_per_turn) + 1
    t = np.linspace(0.0, 2.0 * np.pi * turns, count)
    z = np.linspace(0.0, height, count)
    centers = np.column_stack([path_radius * np.cos(t), path_radius * np.sin(t), z])
    tangents = np.gradient(centers, axis=0)
    tangents /= np.linalg.norm(tangents, axis=1)[:, None]
    normals = np.zeros_like(centers)
    binormals = np.zeros_like(centers)
    for i, tangent in enumerate(tangents):
        reference = np.array([0.0, 0.0, 1.0]) if abs(tangent[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
        normal = np.cross(tangent, reference)
        normal /= np.linalg.norm(normal)
        binormal = np.cross(tangent, normal)
        normals[i] = normal
        binormals[i] = binormal
    angles = np.linspace(0.0, 2.0 * np.pi, section_steps, endpoint=False)
    vertices = []
    for i in range(count):
        for angle in angles:
            point = centers[i] + tube_radius * (np.cos(angle) * normals[i] + np.sin(angle) * binormals[i])
            vertices.append(point)
    faces = []
    for i in range(count - 1):
        for j in range(section_steps):
            a = i * section_steps + j
            b = i * section_steps + (j + 1) % section_steps
            c = (i + 1) * section_steps + j
            d = (i + 1) * section_steps + (j + 1) % section_steps
            faces.append([a, b, d])
            faces.append([a, d, c])
    start_center = len(vertices)
    vertices.append(centers[0])
    end_center = len(vertices)
    vertices.append(centers[-1])
    for j in range(section_steps):
        faces.append([start_center, (j + 1) % section_steps, j])
        base = (count - 1) * section_steps
        faces.append([end_center, base + j, base + (j + 1) % section_steps])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    if mesh.volume < 0.0:
        mesh.invert()
    return mesh


def revolve_profile(profile, radius_modifier=None, sections=96):
    profile = np.asarray(profile, dtype=float)
    count = len(profile)
    angles = np.linspace(0.0, 2.0 * np.pi, sections, endpoint=False)
    vertices = []
    for theta in angles:
        for radius, z in profile:
            radius = radius_modifier(radius, theta) if radius_modifier else radius
            vertices.append([radius * np.cos(theta), radius * np.sin(theta), z])
    faces = []
    for j in range(sections):
        j_next = (j + 1) % sections
        for i in range(count):
            i_next = (i + 1) % count
            a = j * count + i
            b = j * count + i_next
            c = j_next * count + i
            d = j_next * count + i_next
            faces.append([a, b, d])
            faces.append([a, d, c])
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    if mesh.volume < 0.0:
        mesh.invert()
    return mesh


def make_insert():
    outer = INSERT_BODY_D / 2.0
    inner = INSERT_BORE_D / 2.0
    height = INSERT_BODY_L
    profile = [
        (inner, INSERT_CHAMFER_INNER),
        (inner + INSERT_CHAMFER_INNER, 0.0),
        (outer - INSERT_CHAMFER_OUTER, 0.0),
        (outer, INSERT_CHAMFER_OUTER),
        (outer, height - INSERT_CHAMFER_OUTER),
        (outer - INSERT_CHAMFER_OUTER, height),
        (inner + INSERT_CHAMFER_INNER, height),
        (inner, height - INSERT_CHAMFER_INNER),
    ]
    return revolve_profile(profile)


def make_screw():
    shank = cyl(SCREW_CORE_D / 2.0, SCREW_LENGTH, SCREW_LENGTH / 2.0, sections=48)
    head = cyl(SCREW_HEAD_D / 2.0, SCREW_HEAD_L, SCREW_LENGTH + SCREW_HEAD_L / 2.0, sections=64)
    thread = helix_tube(SCREW_MAJOR_D / 2.0 - 0.15, 0.15, SCREW_PITCH, SCREW_LENGTH)
    mesh = trimesh.boolean.union([shank, head, thread], engine="manifold")
    socket = hexprism(SCREW_SOCKET_AF, SCREW_SOCKET_DEPTH + 0.1, SCREW_LENGTH + SCREW_HEAD_L - SCREW_SOCKET_DEPTH / 2.0)
    mesh = trimesh.boolean.difference([mesh, socket], engine="manifold")
    return mesh


def make_nut():
    mesh = hexprism(NUT_AF, NUT_HEIGHT, NUT_HEIGHT / 2.0, sections=6)
    bore = cyl(NUT_BORE_D / 2.0, NUT_HEIGHT + 2.0, NUT_HEIGHT / 2.0, sections=48)
    mesh = trimesh.boolean.difference([mesh, bore], engine="manifold")
    return mesh


def make_washer():
    mesh = cyl(WASHER_OD / 2.0, WASHER_T, WASHER_T / 2.0, sections=64)
    bore = cyl(WASHER_ID / 2.0, WASHER_T + 2.0, WASHER_T / 2.0, sections=48)
    mesh = trimesh.boolean.difference([mesh, bore], engine="manifold")
    return mesh


def export(mesh, name):
    path = OUT_DIR / name
    mesh.export(path)
    print(f"{name}: watertight={mesh.is_watertight} volume={mesh.volume:.1f} mm3 mass_pla={mesh.volume * 1.24 / 1000.0:.2f} g")
    return path


def main():
    export(make_insert(), "m3_heat_insert.stl")
    export(make_screw(), "m3_screw_10mm.stl")
    export(make_nut(), "m3_hex_nut.stl")
    export(make_washer(), "m3_washer.stl")


if __name__ == "__main__":
    main()
