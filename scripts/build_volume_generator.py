import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "models" / "reference"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CUBE = 256.0
BEAM = 3.0


def box_at(extents, center):
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def make_solid():
    return box_at([CUBE, CUBE, CUBE], [0.0, 0.0, CUBE / 2.0])


def make_frame():
    inset = BEAM / 2.0
    offset = CUBE / 2.0 - inset
    parts = []
    for y in (-offset, offset):
        for z in (inset, CUBE - inset):
            parts.append(box_at([CUBE, BEAM, BEAM], [0.0, y, z]))
    for x in (-offset, offset):
        for z in (inset, CUBE - inset):
            parts.append(box_at([BEAM, CUBE, BEAM], [x, 0.0, z]))
    for x in (-offset, offset):
        for y in (-offset, offset):
            parts.append(box_at([BEAM, BEAM, CUBE], [x, y, CUBE / 2.0]))
    return trimesh.boolean.union(parts, engine="manifold")


def export(mesh, name):
    path = OUT_DIR / name
    mesh.export(path)
    print(f"{name}: watertight={mesh.is_watertight} volume={mesh.volume:.1f} mm3")
    print(f"  bounds={mesh.bounds.round(2).tolist()} extents={mesh.extents.round(2).tolist()}")
    return path


def main():
    export(make_solid(), "build_volume_256.stl")
    export(make_frame(), "build_volume_256_frame.stl")
    print(f"envelope {CUBE:.0f} x {CUBE:.0f} x {CUBE:.0f} mm, centered on X/Y, bed at Z=0")


if __name__ == "__main__":
    main()
