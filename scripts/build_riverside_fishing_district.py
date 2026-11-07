import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix

def create_or_get_collection(name, parent_name=None):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        if parent_name and bpy.data.collections.get(parent_name):
            bpy.data.collections[parent_name].children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

def get_mat(name, fallback="M_Wood_AgedOak"):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.get(fallback)
    if not mat and len(bpy.data.materials) > 0:
        mat = bpy.data.materials[0]
    return mat

def add_cube(bm, matrix, mat_idx=0):
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=matrix)
    for v in res['verts']:
        for f in v.link_faces:
            f.material_index = mat_idx
    return res

def add_cylinder(bm, radius, depth, segments=16, matrix=Matrix.Identity(4), mat_idx=0):
    res = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth,
        matrix=matrix
    )
    for v in res['verts']:
        for f in v.link_faces:
            f.material_index = mat_idx
    return res

def add_grid(bm, matrix, x_seg=8, y_seg=8, mat_idx=0):
    res = bmesh.ops.create_grid(bm, x_segments=x_seg, y_segments=y_seg, size=1.0, matrix=matrix)
    for v in res['verts']:
        for f in v.link_faces:
            f.material_index = mat_idx
    return res

def build_fishing_dock(origin, col):
    """
    Constructs a detailed wooden fishing pier extending into the river with
    vertical oak pilings, cross-timbers, deck planks, and mooring bollards.
    """
    mat_wood = get_mat("M_Wood_AgedOak")
    mat_moss = get_mat("M_Stone_Waterline_Moss", "M_Wood_DarkTimber")
    bm = bmesh.new()

    pier_len = 5.6
    pier_w = 2.2
    deck_thick = 0.08
    deck_z = 0.35

    piling_x_offsets = [0.4, 2.0, 3.8, 5.2]
    for px in piling_x_offsets:
        for py in [-pier_w * 0.45, pier_w * 0.45]:
            add_cylinder(
                bm,
                radius=0.14,
                depth=2.2,
                segments=12,
                matrix=Matrix.Translation(Vector((px, py, -0.6))),
                mat_idx=1
            )

    for px in [1.2, 2.9, 4.5]:
        add_cube(
            bm,
            matrix=Matrix.Translation(Vector((px, 0, deck_z - 0.14))) @ Matrix.Scale(0.18, 4, Vector((1, 0, 0))) @ Matrix.Scale(pier_w + 0.1, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.2, 4, Vector((0, 0, 1))),
            mat_idx=0
        )

    num_planks = 26
    plank_w = pier_len / num_planks
    for i in range(num_planks):
        px = i * plank_w + plank_w * 0.5
        tilt = math.radians((i % 3 - 1) * 0.4)
        add_cube(
            bm,
            matrix=Matrix.Translation(Vector((px, 0, deck_z))) @ Matrix.Rotation(tilt, 4, 'Z') @ Matrix.Scale(plank_w * 0.92, 4, Vector((1, 0, 0))) @ Matrix.Scale(pier_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(deck_thick, 4, Vector((0, 0, 1))),
            mat_idx=0
        )

    for by in [-pier_w * 0.4, pier_w * 0.4]:
        add_cylinder(
            bm,
            radius=0.12,
            depth=0.65,
            segments=12,
            matrix=Matrix.Translation(Vector((pier_len - 0.4, by, deck_z + 0.3))),
            mat_idx=0
        )

    mesh = bpy.data.meshes.new("Riverside_Fishing_Dock_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Riverside_Fishing_Dock", mesh)
    obj.location = origin
    obj.data.materials.append(mat_wood)
    obj.data.materials.append(mat_moss)
    col.objects.link(obj)
    return obj

def build_fishing_boat(origin, col):
    """
    Constructs an authentic clinker-built wooden medieval fishing skiff
    with curved prow, thwarts (benches), and pair of wooden oars.
    """
    mat_wood = get_mat("M_Wood_AgedOak")
    mat_dark = get_mat("M_Wood_DarkTimber")
    bm = bmesh.new()

    boat_len = 3.8
    boat_w = 1.35
    boat_h = 0.65

    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((0, 0, -boat_h * 0.45))) @ Matrix.Scale(boat_len, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.16, 4, Vector((0, 0, 1))),
        mat_idx=1
    )

    num_ribs = 10
    for i in range(num_ribs):
        t = i / (num_ribs - 1)
        x = (t - 0.5) * boat_len
        width_fac = math.sin(t * math.pi) * boat_w
        if width_fac < 0.2:
            width_fac = 0.2

        for side, sign in [("port", -1), ("starboard", 1)]:
            add_cube(
                bm,
                matrix=Matrix.Translation(Vector((x, sign * width_fac * 0.5, 0))) @ Matrix.Scale(boat_len / num_ribs * 1.05, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @ Matrix.Scale(boat_h, 4, Vector((0, 0, 1))),
                mat_idx=0
            )

    for x_thwart in [-0.8, 0.0, 0.9]:
        add_cube(
            bm,
            matrix=Matrix.Translation(Vector((x_thwart, 0, 0.05))) @ Matrix.Scale(0.24, 4, Vector((1, 0, 0))) @ Matrix.Scale(boat_w * 0.85, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.05, 4, Vector((0, 0, 1))),
            mat_idx=0
        )

    for sign, angle in [(-1, 25), (1, -25)]:
        add_cylinder(
            bm,
            radius=0.035,
            depth=2.4,
            segments=8,
            matrix=Matrix.Translation(Vector((0.1, sign * 0.7, 0.3))) @ Matrix.Rotation(math.radians(angle), 4, 'Z') @ Matrix.Rotation(math.radians(15), 4, 'Y'),
            mat_idx=1
        )

    mesh = bpy.data.meshes.new("Riverside_Fishing_Boat_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Riverside_Fishing_Boat", mesh)
    obj.location = origin
    obj.rotation_euler = Euler((0, math.radians(-3), math.radians(18)), 'XYZ')
    obj.data.materials.append(mat_wood)
    obj.data.materials.append(mat_dark)
    col.objects.link(obj)
    return obj

def build_fishing_props(origin, col):
    """
    Creates drying fish nets on cedar A-frames, coiled hemp ropes, and fish crates.
    """
    mat_wood = get_mat("M_Wood_AgedOak")
    mat_burlap = get_mat("M_Burlap_Hessian", "M_Plaster_Cream")
    mat_iron = get_mat("M_Iron_Rusted")
    bm = bmesh.new()

    for side_x in [-1.4, 1.4]:
        add_cylinder(
            bm,
            radius=0.08,
            depth=2.2,
            segments=10,
            matrix=Matrix.Translation(Vector((side_x, 0, 1.1))),
            mat_idx=0
        )

    add_cylinder(
        bm,
        radius=0.06,
        depth=3.1,
        segments=10,
        matrix=Matrix.Translation(Vector((0, 0, 2.0))) @ Matrix.Rotation(math.radians(90), 4, 'Y'),
        mat_idx=0
    )

    add_grid(
        bm,
        matrix=Matrix.Translation(Vector((0, 0, 1.1))) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Scale(2.8, 4, Vector((1, 0, 0))) @ Matrix.Scale(1.6, 4, Vector((0, 0, 1))),
        x_seg=8,
        y_seg=8,
        mat_idx=1
    )

    add_cylinder(
        bm,
        radius=0.35,
        depth=0.15,
        segments=16,
        matrix=Matrix.Translation(Vector((-1.8, 0.4, 0.1))),
        mat_idx=1
    )

    mesh = bpy.data.meshes.new("Riverside_Fishing_Gear_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Riverside_Fishing_Gear", mesh)
    obj.location = origin
    obj.data.materials.append(mat_wood)
    obj.data.materials.append(mat_burlap)
    obj.data.materials.append(mat_iron)
    col.objects.link(obj)
    return obj

def build_riverside_fishing_district():
    print("==================================================")
    print("BUILDING RIVERSIDE FISHING DISTRICT (WEST TRANQUIL POOL)")
    print("==================================================")

    col = create_or_get_collection("03_RIVERSIDE_FISHING_DISTRICT")

    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    # Place in open tranquil pool west of church (X = -22 to -26, Y = 23 to 26)
    dock_loc = Vector((-21.0, 25.2, -1.3))
    boat_loc = Vector((-24.5, 23.5, -1.55))
    gear_loc = Vector((-19.8, 26.2, -0.9))

    dock = build_fishing_dock(dock_loc, col)
    # Dock extends out toward negative X
    dock.rotation_euler = Euler((0, 0, math.radians(165)), 'XYZ')

    boat = build_fishing_boat(boat_loc, col)
    gear = build_fishing_props(gear_loc, col)

    print("Riverside Fishing District build complete!")
    return dock, boat

if __name__ == "__main__":
    build_riverside_fishing_district()
