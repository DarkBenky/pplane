import trimesh
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "models" / "test-stand"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SPAN = 180.0
ARM_WIDTH = 45.0
BASE_HEIGHT = 40.0
WALL = 3.0
LID_THICKNESS = 8.0
COLUMN_DIAMETER = 10.0
COLUMN_RADIUS = 75.0
MOTOR_RADIUS = 21.9
INSERT_HOLE_DIAMETER = 4.0
BASE_INSERT_DEPTH = 7.5
MOTOR_INSERT_DEPTH = 8.0
LID_SCREW_DIAMETER = 3.4
LID_COUNTERBORE_DIAMETER = 6.0
LID_COUNTERBORE_DEPTH = 3.0
MOTOR_BOSS_DIAMETER = 10.0
MOTOR_BOSS_HEIGHT = 3.5
MOTOR_CENTER_POCKET_DIAMETER = 16.0
MOTOR_CENTER_POCKET_DEPTH = 2.5
LID_LIP_HEIGHT = 2.0
LID_LIP_THICKNESS = 2.0
LID_LIP_CLEARANCE = 0.2
INSERT_FLANGE_COUNTERBORE_DIAMETER = 5.8
INSERT_FLANGE_COUNTERBORE_DEPTH = 0.7


def box_at(extents, center):
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def plus_prism(span, arm_width, height, z_center):
    horizontal = box_at([span, arm_width, height], [0.0, 0.0, z_center])
    vertical = box_at([arm_width, span, height], [0.0, 0.0, z_center])
    return trimesh.boolean.union([horizontal, vertical], engine="manifold")


def cyl_at(radius, height, z_center, x, y, sections=64):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    mesh.apply_translation([x, y, z_center])
    return mesh


def make_base():
    outer = plus_prism(SPAN, ARM_WIDTH, BASE_HEIGHT, BASE_HEIGHT / 2.0)
    cavity = plus_prism(SPAN - 2.0 * WALL, ARM_WIDTH - 2.0 * WALL, BASE_HEIGHT - WALL, WALL + (BASE_HEIGHT - WALL) / 2.0)
    base = trimesh.boolean.difference([outer, cavity], engine="manifold")
    columns = []
    holes = []
    for x, y in [(COLUMN_RADIUS, 0.0), (-COLUMN_RADIUS, 0.0), (0.0, COLUMN_RADIUS), (0.0, -COLUMN_RADIUS)]:
        columns.append(cyl_at(COLUMN_DIAMETER / 2.0, BASE_HEIGHT, BASE_HEIGHT / 2.0, x, y))
        holes.append(cyl_at(INSERT_HOLE_DIAMETER / 2.0, BASE_INSERT_DEPTH + 1.0, BASE_HEIGHT - (BASE_INSERT_DEPTH - 1.0) / 2.0, x, y, sections=48))
        holes.append(cyl_at(INSERT_FLANGE_COUNTERBORE_DIAMETER / 2.0, INSERT_FLANGE_COUNTERBORE_DEPTH, BASE_HEIGHT - INSERT_FLANGE_COUNTERBORE_DEPTH / 2.0, x, y, sections=48))
    base = trimesh.boolean.union([base] + columns, engine="manifold")
    base = trimesh.boolean.difference([base] + holes, engine="manifold")
    return base


def make_lid():
    lid = plus_prism(SPAN, ARM_WIDTH, LID_THICKNESS, BASE_HEIGHT + LID_THICKNESS / 2.0)
    bosses = []
    motor_holes = []
    lid_holes = []
    counterbores = []
    for x, y in [(MOTOR_RADIUS, 0.0), (-MOTOR_RADIUS, 0.0), (0.0, MOTOR_RADIUS), (0.0, -MOTOR_RADIUS)]:
        bosses.append(cyl_at(MOTOR_BOSS_DIAMETER / 2.0, MOTOR_BOSS_HEIGHT, BASE_HEIGHT - MOTOR_BOSS_HEIGHT / 2.0, x, y))
        motor_holes.append(cyl_at(INSERT_HOLE_DIAMETER / 2.0, MOTOR_INSERT_DEPTH + 1.0, BASE_HEIGHT + LID_THICKNESS - (MOTOR_INSERT_DEPTH - 1.0) / 2.0, x, y, sections=48))
        motor_holes.append(cyl_at(INSERT_FLANGE_COUNTERBORE_DIAMETER / 2.0, INSERT_FLANGE_COUNTERBORE_DEPTH, BASE_HEIGHT + LID_THICKNESS - INSERT_FLANGE_COUNTERBORE_DEPTH / 2.0, x, y, sections=48))
    for x, y in [(COLUMN_RADIUS, 0.0), (-COLUMN_RADIUS, 0.0), (0.0, COLUMN_RADIUS), (0.0, -COLUMN_RADIUS)]:
        lid_holes.append(cyl_at(LID_SCREW_DIAMETER / 2.0, LID_THICKNESS + 2.0, BASE_HEIGHT + LID_THICKNESS / 2.0, x, y, sections=48))
        counterbores.append(cyl_at(LID_COUNTERBORE_DIAMETER / 2.0, LID_COUNTERBORE_DEPTH, BASE_HEIGHT + LID_THICKNESS - LID_COUNTERBORE_DEPTH / 2.0, x, y, sections=48))
    lip_outer = plus_prism(SPAN - 2.0 * WALL - 2.0 * LID_LIP_CLEARANCE, ARM_WIDTH - 2.0 * WALL - 2.0 * LID_LIP_CLEARANCE, LID_LIP_HEIGHT, BASE_HEIGHT - LID_LIP_HEIGHT / 2.0)
    lip_inner = plus_prism(SPAN - 2.0 * WALL - 2.0 * LID_LIP_CLEARANCE - 2.0 * LID_LIP_THICKNESS, ARM_WIDTH - 2.0 * WALL - 2.0 * LID_LIP_CLEARANCE - 2.0 * LID_LIP_THICKNESS, LID_LIP_HEIGHT + 1.0, BASE_HEIGHT - LID_LIP_HEIGHT / 2.0)
    lip = trimesh.boolean.difference([lip_outer, lip_inner], engine="manifold")
    lid = trimesh.boolean.union([lid, lip] + bosses, engine="manifold")
    center_pocket = cyl_at(MOTOR_CENTER_POCKET_DIAMETER / 2.0, MOTOR_CENTER_POCKET_DEPTH, BASE_HEIGHT + LID_THICKNESS - MOTOR_CENTER_POCKET_DEPTH / 2.0, 0.0, 0.0, sections=64)
    lid = trimesh.boolean.difference([lid] + motor_holes + lid_holes + counterbores + [center_pocket], engine="manifold")
    return lid


def export(mesh, name):
    path = OUT_DIR / name
    mesh.export(path)
    print(f"{name}: watertight={mesh.is_watertight} volume={mesh.volume:.1f} mm3 mass_pla={mesh.volume * 1.24 / 1000.0:.1f} g")
    return path


def main():
    base = make_base()
    lid = make_lid()
    export(base, "motor_test_stand_base.stl")
    export(lid, "motor_test_stand_lid.stl")
    cavity = (SPAN - 2.0 * WALL) * (ARM_WIDTH - 2.0 * WALL) * 2.0 - (ARM_WIDTH - 2.0 * WALL) ** 2
    cavity *= (BASE_HEIGHT - WALL)
    print(f"base footprint={SPAN:.0f} x {SPAN:.0f} mm, base height={BASE_HEIGHT:.0f} mm, lid={LID_THICKNESS:.0f} mm")
    print(f"sand cavity approx={cavity / 1000.0:.0f} cm3, sand mass approx={cavity * 1.6 / 1000.0:.0f} g")
    print(f"motor holes r={MOTOR_RADIUS:.1f} mm (span {2 * MOTOR_RADIUS:.1f} mm), base screws r={COLUMN_RADIUS:.1f} mm")


if __name__ == "__main__":
    main()
