"""Generate thin end-cap plates from the existing boatend placeholder blocks.

The old boatend/boatend2 meshes are solid blocks that fill the front end of the
boat.  Cutting a thin 2 mm slice from their outboard face gives just the end
cap, with no long side walls.  The slice is normalised to x = 0..2 mm so it can
be placed or rotated at either end of the boat.
"""

import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BOAT_DIR = BASE_DIR / "models" / "boat"

SLICE_X0 = 348.0
SLICE_X1 = 350.0
THICKNESS = SLICE_X1 - SLICE_X0


def clean(mesh):
    mesh.merge_vertices()
    trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def mirror_y(mesh):
    vertices = mesh.vertices.copy()
    vertices[:, 1] *= -1.0
    mirrored = trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=True)
    return clean(mirrored)


def slice_plate(source):
    block = trimesh.load(BOAT_DIR / source, force="mesh", process=True)
    cutter = trimesh.creation.box(extents=[THICKNESS, 500.0, 300.0])
    cutter.apply_translation([(SLICE_X0 + SLICE_X1) / 2.0, 0.0, 200.0])
    plate = trimesh.boolean.intersection([block, cutter], engine="manifold")
    plate = clean(plate)
    plate.apply_translation([-SLICE_X0, 0.0, 0.0])
    return plate


def export(mesh, name):
    path = BOAT_DIR / name
    mesh.export(path)
    print(f"{name}: watertight={mesh.is_watertight} volume={mesh.volume:.1f} mm3 bounds={mesh.bounds.round(2).tolist()}")
    return path


def main():
    port = slice_plate("boatend.stl")
    starboard = mirror_y(port)
    full = trimesh.boolean.union([port, starboard], engine="manifold")
    full = clean(full)

    export(full, "boat_bow_stern_cap_full.stl")
    export(port, "boat_bow_stern_cap_port.stl")
    export(starboard, "boat_bow_stern_cap_starboard.stl")
    print(f"{THICKNESS:.0f} mm thin end plates; no side walls. Same plate at both ends.")


if __name__ == "__main__":
    main()
