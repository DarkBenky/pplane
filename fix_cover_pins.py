import numpy as np
import trimesh
from pathlib import Path
from trimesh.creation import box

BASE_DIR = Path(__file__).resolve().parent
MALE_SOURCE = BASE_DIR / "male-cover.stl"
FEMALE_SOURCE = BASE_DIR / "female-cover.stl"
MALE_OUTPUT = BASE_DIR / "male-cover-fixed.stl"
FEMALE_OUTPUT = BASE_DIR / "female-cover-fixed.stl"

PIN_SIZE = 2.4
SOCKET_SIZE = 2.6
PIN_Z_CENTERS = [7.78484, 55.78484]
OLD_PIN_HALF_Z = 1.837
PIN_HALF_Z = PIN_SIZE / 2.0
SOCKET_HALF_Z = SOCKET_SIZE / 2.0
FLANGE_CENTER_X = 67.28041
OLD_PIN_X_OUTER = 68.30
OLD_PIN_X_INNER = 64.755
MALE_REMOVAL_Y_MIN = -5.30
MALE_REMOVAL_Y_MAX = -1.65
MALE_PIN_TIP_Y = -5.2228
MALE_PIN_BASE_Y = -1.65
FEMALE_FILL_Y_MIN = -5.30
FEMALE_FILL_Y_MAX = -1.55
FEMALE_SOCKET_FRONT_Y = -1.50
FEMALE_SOCKET_BACK_Y = -5.35


def make_box(xmin, xmax, ymin, ymax, zmin, zmax):
    mesh = box(extents=[xmax - xmin, ymax - ymin, zmax - zmin])
    mesh.apply_translation([(xmin + xmax) / 2.0, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0])
    return mesh


def side_bounds(side):
    if side < 0:
        return -OLD_PIN_X_OUTER, -OLD_PIN_X_INNER
    return OLD_PIN_X_INNER, OLD_PIN_X_OUTER


def pin_x_bounds(side):
    center = side * FLANGE_CENTER_X
    return min(center - PIN_SIZE / 2.0, center + PIN_SIZE / 2.0), max(center - PIN_SIZE / 2.0, center + PIN_SIZE / 2.0)


def socket_x_bounds(side):
    center = side * FLANGE_CENTER_X
    return min(center - SOCKET_SIZE / 2.0, center + SOCKET_SIZE / 2.0), max(center - SOCKET_SIZE / 2.0, center + SOCKET_SIZE / 2.0)


def male_cutters():
    cutters = []
    for side in [-1, 1]:
        xmin, xmax = side_bounds(side)
        for zc in PIN_Z_CENTERS:
            cutters.append(make_box(xmin, xmax, MALE_REMOVAL_Y_MIN, MALE_REMOVAL_Y_MAX, zc - OLD_PIN_HALF_Z, zc + OLD_PIN_HALF_Z))
    return cutters


def male_pins():
    pins = []
    for side in [-1, 1]:
        xmin, xmax = pin_x_bounds(side)
        for zc in PIN_Z_CENTERS:
            pins.append(make_box(xmin, xmax, MALE_PIN_TIP_Y, MALE_PIN_BASE_Y, zc - PIN_HALF_Z, zc + PIN_HALF_Z))
    return pins


def female_fillers():
    fillers = []
    for side in [-1, 1]:
        xmin, xmax = side_bounds(side)
        for zc in PIN_Z_CENTERS:
            fillers.append(make_box(xmin, xmax, FEMALE_FILL_Y_MIN, FEMALE_FILL_Y_MAX, zc - OLD_PIN_HALF_Z, zc + OLD_PIN_HALF_Z))
    return fillers


def female_cutters():
    cutters = []
    for side in [-1, 1]:
        xmin, xmax = socket_x_bounds(side)
        for zc in PIN_Z_CENTERS:
            cutters.append(make_box(xmin, xmax, FEMALE_SOCKET_BACK_Y, FEMALE_SOCKET_FRONT_Y, zc - SOCKET_HALF_Z, zc + SOCKET_HALF_Z))
    return cutters


def main():
    male = trimesh.load(MALE_SOURCE, force="mesh")
    female = trimesh.load(FEMALE_SOURCE, force="mesh")
    male = trimesh.boolean.difference([male] + male_cutters(), engine="manifold")
    male = trimesh.boolean.union([male] + male_pins(), engine="manifold")
    female = trimesh.boolean.union([female] + female_fillers(), engine="manifold")
    female = trimesh.boolean.difference([female] + female_cutters(), engine="manifold")
    if not male.is_watertight or not female.is_watertight:
        raise RuntimeError("generated cover mesh is not watertight")
    male.export(MALE_OUTPUT)
    female.export(FEMALE_OUTPUT)
    print(f"male watertight={male.is_watertight} faces={len(male.faces)} saved={MALE_OUTPUT}")
    print(f"female watertight={female.is_watertight} faces={len(female.faces)} saved={FEMALE_OUTPUT}")


if __name__ == "__main__":
    main()
