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

def build_water_wheel(origin, col):
    """
    Builds an authentic 4.2m diameter medieval wooden water wheel with
    central iron-strapped axle, 16 radial spokes, dual outer rims, and 16 bucket paddles.
    """
    mesh = bpy.data.meshes.new("Watermill_Water_Wheel_Mesh")
    bm = bmesh.new()

    mat_wood = get_mat("M_Wood_AgedOak")
    mat_dark = get_mat("M_Wood_DarkTimber", "M_Wood_AgedOak")
    mat_iron = get_mat("M_Iron_Rusted", "M_Wood_AgedOak")

    radius_outer = 2.1
    radius_inner = 1.85
    width = 1.35
    num_spokes = 16
    axle_radius = 0.35
    axle_length = 2.4

    # 1. Central Axle
    add_cylinder(
        bm,
        radius=axle_radius,
        depth=axle_length,
        segments=16,
        matrix=Matrix.Rotation(math.radians(90), 4, 'X'),
        mat_idx=0
    )

    # 2. Iron Axle Straps / Bands
    for y_band in [-0.5, 0.5]:
        add_cylinder(
            bm,
            radius=axle_radius + 0.02,
            depth=0.12,
            segments=16,
            matrix=Matrix.Translation(Vector((0, y_band, 0))) @ Matrix.Rotation(math.radians(90), 4, 'X'),
            mat_idx=2
        )

    # 3. Dual Outer Wooden Rims
    half_w = width * 0.5
    for y_offset in [-half_w, half_w]:
        for i in range(num_spokes):
            angle1 = (2 * math.pi / num_spokes) * i
            angle2 = (2 * math.pi / num_spokes) * (i + 1)
            mid_angle = (angle1 + angle2) * 0.5

            seg_len = (radius_outer * 2 * math.pi) / num_spokes * 1.05
            add_cube(
                bm,
                matrix=Matrix.Translation(Vector((
                    math.cos(mid_angle) * (radius_outer + radius_inner) * 0.5,
                    y_offset,
                    math.sin(mid_angle) * (radius_outer + radius_inner) * 0.5
                ))) @ Matrix.Rotation(-mid_angle, 4, 'Y') @ Matrix.Scale(radius_outer - radius_inner, 4, Vector((0, 0, 1))) @ Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @ Matrix.Scale(seg_len, 4, Vector((1, 0, 0))),
                mat_idx=1
            )

    # 4. Radial Oak Spokes
    spoke_len = radius_inner - axle_radius
    spoke_mid_r = axle_radius + spoke_len * 0.5
    for y_offset in [-half_w, half_w]:
        for i in range(num_spokes):
            angle = (2 * math.pi / num_spokes) * i
            add_cube(
                bm,
                matrix=Matrix.Translation(Vector((
                    math.cos(angle) * spoke_mid_r,
                    y_offset,
                    math.sin(angle) * spoke_mid_r
                ))) @ Matrix.Rotation(-angle, 4, 'Y') @ Matrix.Scale(spoke_len, 4, Vector((0, 0, 1))) @ Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.14, 4, Vector((1, 0, 0))),
                mat_idx=0
            )

    # 5. Bucket Paddles
    paddle_width = width - 0.05
    for i in range(num_spokes):
        angle = (2 * math.pi / num_spokes) * i
        paddle_angle = angle + math.radians(15)
        paddle_r = radius_inner + (radius_outer - radius_inner) * 0.5
        add_cube(
            bm,
            matrix=Matrix.Translation(Vector((
                math.cos(angle) * paddle_r,
                0,
                math.sin(angle) * paddle_r
            ))) @ Matrix.Rotation(-paddle_angle, 4, 'Y') @ Matrix.Scale(radius_outer - radius_inner + 0.15, 4, Vector((0, 0, 1))) @ Matrix.Scale(paddle_width, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((1, 0, 0))),
            mat_idx=0
        )

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Watermill_Water_Wheel", mesh)
    obj.location = origin
    obj.data.materials.append(mat_wood)
    obj.data.materials.append(mat_dark)
    obj.data.materials.append(mat_iron)
    col.objects.link(obj)
    return obj

def build_mill_building(origin, col):
    """
    Builds the authentic medieval watermill building:
    - Stone lower level with arched water sluice and axle portal
    - Timber-framed second floor with overhanging eaves
    - Steep pitched gable roof with hoist dormer
    """
    mat_stone = get_mat("M_Stone_Rough", "M_Stone_AshlarGrey")
    mat_wood = get_mat("M_Wood_DarkTimber", "M_Wood_AgedOak")
    mat_plaster = get_mat("M_Plaster_Cream", "M_Plaster_Lime")
    mat_tile = get_mat("M_Clay_Terracotta", "M_Stone_Rubble")

    bm = bmesh.new()

    bw, bl, bh_stone, bh_timber = 7.2, 5.8, 3.2, 3.0

    # 1. Stone Lower Level
    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((0, 0, bh_stone * 0.5))) @ Matrix.Scale(bw, 4, Vector((1, 0, 0))) @ Matrix.Scale(bl, 4, Vector((0, 1, 0))) @ Matrix.Scale(bh_stone, 4, Vector((0, 0, 1))),
        mat_idx=0
    )

    # 2. Axle Arch Inset / Sluice Cutout on river-facing side
    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((-bw * 0.5 + 0.6, -bl * 0.2, 1.2))) @ Matrix.Scale(1.8, 4, Vector((1, 0, 0))) @ Matrix.Scale(2.2, 4, Vector((0, 1, 0))) @ Matrix.Scale(2.0, 4, Vector((0, 0, 1))),
        mat_idx=0
    )

    # 3. Timber-Framed Upper Level (with 0.3m jetty overhang)
    tw, tl = bw + 0.4, bl + 0.4
    z_timber = bh_stone + bh_timber * 0.5
    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((0, 0, z_timber))) @ Matrix.Scale(tw, 4, Vector((1, 0, 0))) @ Matrix.Scale(tl, 4, Vector((0, 1, 0))) @ Matrix.Scale(bh_timber, 4, Vector((0, 0, 1))),
        mat_idx=2
    )

    # Timber Corner Posts
    for cx in [-tw * 0.5, tw * 0.5]:
        for cy in [-tl * 0.5, tl * 0.5]:
            add_cube(
                bm,
                matrix=Matrix.Translation(Vector((cx, cy, z_timber))) @ Matrix.Scale(0.24, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.24, 4, Vector((0, 1, 0))) @ Matrix.Scale(bh_timber + 0.1, 4, Vector((0, 0, 1))),
                mat_idx=1
            )

    # Jetty Sill Beam
    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((0, 0, bh_stone))) @ Matrix.Scale(tw + 0.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(tl + 0.2, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.28, 4, Vector((0, 0, 1))),
        mat_idx=1
    )

    # 4. Gable Roof
    roof_h = 3.2
    z_roof_base = bh_stone + bh_timber
    overhang = 0.5
    rw = tw + overhang * 2
    rl = tl + overhang * 2

    for side, sign in [("south", -1), ("north", 1)]:
        slope_angle = math.radians(45) * sign
        add_cube(
            bm,
            matrix=Matrix.Translation(Vector((0, sign * (tl * 0.25 + 0.1), z_roof_base + roof_h * 0.5))) @ Matrix.Rotation(slope_angle, 4, 'X') @ Matrix.Scale(rw, 4, Vector((1, 0, 0))) @ Matrix.Scale(rl * 0.65, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.18, 4, Vector((0, 0, 1))),
            mat_idx=3
        )

    # Roof Ridge Beam
    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((0, 0, z_roof_base + roof_h + 0.1))) @ Matrix.Scale(rw + 0.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.3, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.3, 4, Vector((0, 0, 1))),
        mat_idx=3
    )

    # 5. Hoist Lucarne Beam
    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((-tw * 0.5 - 0.8, 0, z_roof_base + roof_h * 0.6))) @ Matrix.Scale(2.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.2, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.25, 4, Vector((0, 0, 1))),
        mat_idx=1
    )

    # 6. Chimney
    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((tw * 0.4, tl * 0.45, z_roof_base + roof_h * 0.6))) @ Matrix.Scale(0.9, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.9, 4, Vector((0, 1, 0))) @ Matrix.Scale(roof_h + 1.2, 4, Vector((0, 0, 1))),
        mat_idx=0
    )

    mesh = bpy.data.meshes.new("Watermill_Building_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Watermill_Main_Building", mesh)
    obj.location = origin
    obj.data.materials.append(mat_stone)
    obj.data.materials.append(mat_wood)
    obj.data.materials.append(mat_plaster)
    obj.data.materials.append(mat_tile)
    col.objects.link(obj)
    return obj

def build_flume_sluice(origin, col):
    """
    Constructs the elevated timber flume that delivers
    water from the upstream river weir onto the water wheel.
    """
    mat_wood = get_mat("M_Wood_AgedOak")
    mat_moss = get_mat("M_Stone_Waterline_Moss", "M_Wood_DarkTimber")
    bm = bmesh.new()

    flume_len = 7.5
    flume_w = 1.4
    flume_depth = 0.55

    add_cube(
        bm,
        matrix=Matrix.Translation(Vector((flume_len * 0.5, 0, 0))) @ Matrix.Scale(flume_len, 4, Vector((1, 0, 0))) @ Matrix.Scale(flume_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 0, 1))),
        mat_idx=1
    )

    for sign in [-1, 1]:
        add_cube(
            bm,
            matrix=Matrix.Translation(Vector((flume_len * 0.5, sign * (flume_w * 0.5 - 0.05), flume_depth * 0.5))) @ Matrix.Scale(flume_len, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.1, 4, Vector((0, 1, 0))) @ Matrix.Scale(flume_depth, 4, Vector((0, 0, 1))),
            mat_idx=1
        )

    for x_sup in [1.5, 4.5, 7.0]:
        h_sup = 1.8 - x_sup * 0.1
        add_cube(
            bm,
            matrix=Matrix.Translation(Vector((x_sup, 0, -h_sup * 0.5))) @ Matrix.Scale(0.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(flume_w + 0.4, 4, Vector((0, 1, 0))) @ Matrix.Scale(h_sup, 4, Vector((0, 0, 1))),
            mat_idx=0
        )

    mesh = bpy.data.meshes.new("Watermill_Sluice_Flume_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Watermill_Sluice_Flume", mesh)
    obj.location = origin
    obj.data.materials.append(mat_wood)
    obj.data.materials.append(mat_moss)
    col.objects.link(obj)
    return obj

def build_mill_cargo_props(origin, col):
    """
    Creates stacks of burlap flour sacks, grain barrels, and wooden delivery platform.
    """
    mat_burlap = get_mat("M_Burlap_Hessian", "M_Plaster_Cream")
    mat_wood = get_mat("M_Wood_AgedOak")
    mat_iron = get_mat("M_Iron_Rusted")

    # 1. Delivery Platform
    bm_deck = bmesh.new()
    deck_w, deck_l = 4.2, 2.5
    add_cube(
        bm_deck,
        matrix=Matrix.Translation(Vector((0, 0, 0.2))) @ Matrix.Scale(deck_w, 4, Vector((1, 0, 0))) @ Matrix.Scale(deck_l, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.35, 4, Vector((0, 0, 1))),
        mat_idx=0
    )
    m_deck = bpy.data.meshes.new("Watermill_Platform_Mesh")
    bm_deck.to_mesh(m_deck)
    bm_deck.free()
    platform = bpy.data.objects.new("Watermill_Delivery_Platform", m_deck)
    platform.location = origin
    platform.data.materials.append(mat_wood)
    col.objects.link(platform)

    # 2. Stack of Flour Sacks
    bm_sacks = bmesh.new()
    sack_locs = [
        Vector((-1.0, -0.4, 0.5)),
        Vector((-0.5, -0.4, 0.5)),
        Vector((0.0, -0.4, 0.5)),
        Vector((-0.75, -0.4, 0.9)),
        Vector((-0.25, -0.4, 0.9)),
        Vector((-0.5, -0.4, 1.3))
    ]
    for sl in sack_locs:
        add_cube(
            bm_sacks,
            matrix=Matrix.Translation(sl) @ Matrix.Scale(0.65, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.48, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.42, 4, Vector((0, 0, 1))),
            mat_idx=0
        )

    m_sacks = bpy.data.meshes.new("Watermill_Flour_Sacks_Mesh")
    bm_sacks.to_mesh(m_sacks)
    bm_sacks.free()
    sacks_obj = bpy.data.objects.new("Watermill_Flour_Sacks", m_sacks)
    sacks_obj.location = origin
    sacks_obj.data.materials.append(mat_burlap)
    col.objects.link(sacks_obj)

    # 3. Grain Barrels
    bm_bar = bmesh.new()
    bar_locs = [
        Vector((1.0, -0.3, 0.65)),
        Vector((1.0, 0.5, 0.65)),
        Vector((0.4, 0.6, 0.65))
    ]
    for bl in bar_locs:
        add_cylinder(
            bm_bar,
            radius=0.38,
            depth=0.9,
            segments=16,
            matrix=Matrix.Translation(bl),
            mat_idx=0
        )

    m_bar = bpy.data.meshes.new("Watermill_Barrels_Mesh")
    bm_bar.to_mesh(m_bar)
    bm_bar.free()
    bar_obj = bpy.data.objects.new("Watermill_Grain_Barrels", m_bar)
    bar_obj.location = origin
    bar_obj.data.materials.append(mat_wood)
    col.objects.link(bar_obj)

def build_watermill_district():
    print("==================================================")
    print("BUILDING WATERMILL DISTRICT")
    print("==================================================")

    col = create_or_get_collection("03_WATERMILL_DISTRICT")

    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    wheel_loc = Vector((15.4, 23.8, 0.4))
    mill_loc = Vector((19.8, 25.2, 0.2))
    flume_loc = Vector((15.0, 24.2, 1.8))
    cargo_loc = Vector((17.2, 21.6, 0.1))

    wheel = build_water_wheel(wheel_loc, col)
    mill = build_mill_building(mill_loc, col)
    flume = build_flume_sluice(flume_loc, col)
    build_mill_cargo_props(cargo_loc, col)

    print("Watermill District build complete!")
    return wheel, mill

if __name__ == "__main__":
    build_watermill_district()
