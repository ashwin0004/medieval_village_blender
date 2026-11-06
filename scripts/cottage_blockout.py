"""
Medieval Fantasy Village - Main Cottage Detailed Blockout
Builds the complete, architecturally authentic medieval timber & stone cottage.
Dimensions:
- Width: 6.8 m (ground floor) / 7.3 m (jetted upper floor) / 8.2 m (roof eaves)
- Depth: 8.4 m (ground floor) / 8.9 m (jetted upper floor) / 9.6 m (roof eaves)
- Total Height: 8.25 m (ridge) / 9.55 m (chimney pots)

Key Architectural Features:
- Rubble stone foundation plinth with dressed stone quoins & water table chamfer
- Stepped stone entrance stairs
- Ground floor heavy stone masonry with dressed lintels, sills & corner quoins
- Cantilevered medieval jetty with exposed joists, dragon beams & carved corbel brackets
- Half-timber framing (corner posts, mid-girts, wall plates, studs, diagonal St. Andrew's cross braces)
- Textured lime plaster infill panels
- Steep 52-degree pitched roof with stepped overlapping clay tile courses, ridge tiles, carved bargeboards & finials
- Massive stepped stone chimney stack with weathering drip courses and dual terracotta pots
- Leaded glass windows with stone/timber mullions and operable wood shutters
- Detailed interior: flagstone & oak floors, summer spine beam, fireplace hearth, cooking pot, trestle table, benches, upper bed & wooden stairs
- Exterior props: banded barrels, storage crates, stacked firewood, wall lantern, climbing ivy & flower box
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler

def clear_collection_objects(col_name):
    col = bpy.data.collections.get(col_name)
    if col:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

def clear_all_cottage_objects():
    cols = [
        "01_Foundation",
        "02_Ground_Floor",
        "03_Timber_Framing",
        "04_Upper_Walls",
        "05_Roof",
        "06_Doors_Windows",
        "07_Chimney",
        "08_Interior",
        "09_Exterior_Props",
    ]
    for c in cols:
        clear_collection_objects(c)

    for obj in list(bpy.data.objects):
        if obj.name.startswith("Cottage_") or obj.name.startswith("Prop_"):
            bpy.data.objects.remove(obj, do_unlink=True)

def apply_modifiers(obj, bevel_width=0.018, segments=2):
    if hasattr(obj.data, 'shade_smooth'):
        obj.data.shade_smooth()
    bev = obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = bevel_width
    bev.segments = segments
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35.0)
    bev.miter_outer = 'MITER_SHARP'

    wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    wn.keep_sharp = True

def assign_material(obj, mat_name):
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

def link_to_collection(obj, col_name):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    target_col = bpy.data.collections.get(col_name)
    if not target_col:
        target_col = bpy.context.scene.collection
    target_col.objects.link(obj)

def create_box(name, size, location, col_name, mat_name=None, bevel=True, bevel_width=0.02):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(mesh)
    bm.free()

    obj.location = location
    link_to_collection(obj, col_name)

    if bevel:
        apply_modifiers(obj, bevel_width=bevel_width)
    if mat_name:
        assign_material(obj, mat_name)

    return obj

def build_foundation():
    col = "01_Foundation"
    mat = "M_Rough_Stone"

    # Main Stone Plinth: 7.0m x 8.6m x 0.85m (Z from 0.0 to 0.85m)
    create_box("Cottage_Foundation_Plinth", (7.0, 8.6, 0.85), (0.0, 0.0, 0.425), col, mat, bevel_width=0.04)

    # Chamfered stone water-table trim running along the top of the foundation
    create_box("Cottage_Foundation_WaterTable", (7.16, 8.76, 0.12), (0.0, 0.0, 0.86), col, mat, bevel_width=0.03)

    # Irregular dressed stone corner quoins along the foundation corners
    quoins = [
        ((-3.52, -4.32), 0.25),
        ((-3.52, -4.32), 0.55),
        ((3.52, -4.32), 0.25),
        ((3.52, -4.32), 0.55),
        ((-3.52, 4.32), 0.25),
        ((-3.52, 4.32), 0.55),
        ((3.52, 4.32), 0.25),
        ((3.52, 4.32), 0.55),
    ]
    for i, ((qx, qy), qz) in enumerate(quoins):
        create_box(f"Cottage_Foundation_Quoin_{i:02d}", (0.55, 0.55, 0.26), (qx, qy, qz), col, mat, bevel_width=0.03)

    # Front Entrance Steps (3 tiers leading to front doorway at X = -0.6)
    steps = [
        ("Cottage_Step_01", (1.70, 0.45, 0.28), (-0.60, -5.00, 0.14)),
        ("Cottage_Step_02", (1.50, 0.45, 0.28), (-0.60, -4.68, 0.42)),
        ("Cottage_Step_03", (1.30, 0.45, 0.28), (-0.60, -4.36, 0.70)),
    ]
    for name, size, loc in steps:
        create_box(name, size, loc, col, mat, bevel_width=0.03)

def build_ground_floor_masonry():
    col = "02_Ground_Floor"
    mat = "M_Rough_Stone"

    # Wall thickness: 0.42m. Height: 2.70m (Z = 0.90 to 3.60m)
    # Front Wall (Y = -4.0):
    create_box("Cottage_GF_Wall_Front_Left", (2.25, 0.42, 2.70), (-2.275, -4.0, 2.25), col, mat)
    create_box("Cottage_GF_Wall_Front_Mid", (1.15, 0.42, 2.70), (0.55, -4.0, 2.25), col, mat)
    create_box("Cottage_GF_Wall_Front_Right", (1.25, 0.42, 2.70), (2.775, -4.0, 2.25), col, mat)

    # Front Window (X = 1.65, Width 1.0m, Height 1.20m -> Z: 1.80 to 3.00)
    create_box("Cottage_GF_Front_Win_SillWall", (1.00, 0.42, 0.90), (1.65, -4.0, 1.35), col, mat)
    create_box("Cottage_GF_Front_Win_LintelWall", (1.00, 0.42, 0.60), (1.65, -4.0, 3.30), col, mat)
    create_box("Cottage_GF_Door_Lintel_Stone", (1.35, 0.50, 0.50), (-0.60, -4.0, 3.35), col, mat, bevel_width=0.03)

    # Rear Wall (Y = +4.0):
    create_box("Cottage_GF_Wall_Rear_L", (2.85, 0.42, 2.70), (-1.975, 4.0, 2.25), col, mat)
    create_box("Cottage_GF_Wall_Rear_R", (2.85, 0.42, 2.70), (1.975, 4.0, 2.25), col, mat)
    create_box("Cottage_GF_Rear_Win_SillWall", (1.10, 0.42, 0.90), (0.0, 4.0, 1.35), col, mat)
    create_box("Cottage_GF_Rear_Win_LintelWall", (1.10, 0.42, 0.60), (0.0, 4.0, 3.30), col, mat)

    # Left Wall (X = -3.2):
    create_box("Cottage_GF_Wall_Left_1", (0.42, 2.40, 2.70), (-3.2, -2.80, 2.25), col, mat)
    create_box("Cottage_GF_Wall_Left_2", (0.42, 2.20, 2.70), (-3.2, 0.00, 2.25), col, mat)
    create_box("Cottage_GF_Wall_Left_3", (0.42, 2.40, 2.70), (-3.2, 2.80, 2.25), col, mat)
    create_box("Cottage_GF_Left_Win1_Sill", (0.42, 0.70, 1.05), (-3.2, -1.45, 1.425), col, mat)
    create_box("Cottage_GF_Left_Win1_Lintel", (0.42, 0.70, 0.55), (-3.2, -1.45, 3.325), col, mat)
    create_box("Cottage_GF_Left_Win2_Sill", (0.42, 0.70, 1.05), (-3.2, 1.45, 1.425), col, mat)
    create_box("Cottage_GF_Left_Win2_Lintel", (0.42, 0.70, 0.55), (-3.2, 1.45, 3.325), col, mat)

    # Right Wall (X = +3.2):
    create_box("Cottage_GF_Wall_Right_F", (0.42, 2.70, 2.70), (3.2, -2.65, 2.25), col, mat)
    create_box("Cottage_GF_Wall_Right_B", (0.42, 2.70, 2.70), (3.2, 2.65, 2.25), col, mat)
    create_box("Cottage_GF_Fireplace_Opening_Wall", (0.42, 0.60, 2.70), (3.2, 0.00, 3.35), col, mat)

    # Interlocking Ground Floor Corner Quoins
    for qi in range(5):
        qz = 1.15 + qi * 0.55
        create_box(f"Cottage_GF_CornerQuoin_FL_{qi}", (0.48, 0.48, 0.32), (-3.22, -4.02, qz), col, mat, bevel_width=0.025)
        create_box(f"Cottage_GF_CornerQuoin_BL_{qi}", (0.48, 0.48, 0.32), (-3.22, 4.02, qz), col, mat, bevel_width=0.025)

def build_jetty_and_framing():
    col_wood = "03_Timber_Framing"
    col_plaster = "04_Upper_Walls"
    mat_wood = "M_Aged_Oak"
    mat_plaster = "M_Plaster_Historic"

    # 1. Jetty Cantilever Floor Joists & Bressummers (Z = 3.60 to 3.88m)
    create_box("Cottage_Jetty_Bressummer_Front", (7.45, 0.28, 0.28), (0.0, -4.30, 3.72), col_wood, mat_wood)
    create_box("Cottage_Jetty_Bressummer_Rear", (7.45, 0.28, 0.28), (0.0, 4.30, 3.72), col_wood, mat_wood)
    create_box("Cottage_Jetty_Bressummer_Left", (0.28, 8.85, 0.28), (-3.58, 0.0, 3.72), col_wood, mat_wood)
    create_box("Cottage_Jetty_Bressummer_Right", (0.28, 8.85, 0.28), (3.58, 0.0, 3.72), col_wood, mat_wood)

    # Cantilevered timber joists projecting under the jetty
    joist_ys = [-3.8, -3.0, -2.2, -1.4, -0.6, 0.2, 1.0, 1.8, 2.6, 3.4]
    for i, y_pos in enumerate(joist_ys):
        create_box(f"Cottage_Jetty_Joist_{i:02d}", (7.40, 0.16, 0.22), (0.0, y_pos, 3.62), col_wood, mat_wood)

    # Carved Medieval Jetty Corbel Brackets supporting the front overhang
    bracket_xs = [-3.3, -2.2, -1.1, 0.0, 1.1, 2.2, 3.3]
    for i, bx in enumerate(bracket_xs):
        create_box(f"Cottage_Jetty_Bracket_F_{i:02d}", (0.16, 0.26, 0.45), (bx, -4.18, 3.35), col_wood, mat_wood, bevel_width=0.02)

    # 2. Upper Floor Half-Timber Framing (Z = 3.88 to 6.25m -> Height 2.37m)
    corner_posts = [
        ("Cottage_CornerPost_FL", (-3.50, -4.20, 5.06)),
        ("Cottage_CornerPost_FR", (3.50, -4.20, 5.06)),
        ("Cottage_CornerPost_BL", (-3.50, 4.20, 5.06)),
        ("Cottage_CornerPost_BR", (3.50, 4.20, 5.06)),
    ]
    for name, loc in corner_posts:
        create_box(name, (0.24, 0.24, 2.38), loc, col_wood, mat_wood)

    # Top Wall Plates (Z = 6.25m)
    create_box("Cottage_WallPlate_Front", (7.45, 0.24, 0.22), (0.0, -4.20, 6.20), col_wood, mat_wood)
    create_box("Cottage_WallPlate_Rear", (7.45, 0.24, 0.22), (0.0, 4.20, 6.20), col_wood, mat_wood)
    create_box("Cottage_WallPlate_Left", (0.24, 8.85, 0.22), (-3.50, 0.0, 6.20), col_wood, mat_wood)
    create_box("Cottage_WallPlate_Right", (0.24, 8.85, 0.22), (3.50, 0.0, 6.20), col_wood, mat_wood)

    # Intermediate Horizontal Girt Timbers (Z = 4.95m)
    create_box("Cottage_MidGirt_Front", (7.25, 0.18, 0.18), (0.0, -4.20, 4.95), col_wood, mat_wood)
    create_box("Cottage_MidGirt_Rear", (7.25, 0.18, 0.18), (0.0, 4.20, 4.95), col_wood, mat_wood)
    create_box("Cottage_MidGirt_Left", (0.18, 8.65, 0.18), (-3.50, 0.0, 4.95), col_wood, mat_wood)
    create_box("Cottage_MidGirt_Right", (0.18, 8.65, 0.18), (3.50, 0.0, 4.95), col_wood, mat_wood)

    # Vertical Studs
    for i, sx in enumerate([-2.35, -0.75, 0.0, 0.75, 2.35]):
        create_box(f"Cottage_Stud_Front_{i:02d}", (0.18, 0.18, 2.38), (sx, -4.20, 5.06), col_wood, mat_wood)
        create_box(f"Cottage_Stud_Rear_{i:02d}", (0.18, 0.18, 2.38), (sx, 4.20, 5.06), col_wood, mat_wood)

    for i, sy in enumerate([-2.8, -1.4, 0.0, 1.4, 2.8]):
        create_box(f"Cottage_Stud_Left_{i:02d}", (0.18, 0.18, 2.38), (-3.50, sy, 5.06), col_wood, mat_wood)
        create_box(f"Cottage_Stud_Right_{i:02d}", (0.18, 0.18, 2.38), (3.50, sy, 5.06), col_wood, mat_wood)

    # Diagonal Braces (Fachwerk St. Andrew's Cross & Corner Braces)
    def add_brace(name, loc, size, rot_euler):
        obj = create_box(name, size, loc, col_wood, mat_wood)
        obj.rotation_euler = rot_euler
        return obj

    add_brace("Cottage_Brace_Front_L1", (-2.95, -4.20, 4.45), (0.14, 0.14, 1.35), (0, math.radians(45), 0))
    add_brace("Cottage_Brace_Front_R1", (2.95, -4.20, 4.45), (0.14, 0.14, 1.35), (0, math.radians(-45), 0))
    add_brace("Cottage_Brace_Front_L2", (-2.95, -4.20, 5.60), (0.14, 0.14, 1.35), (0, math.radians(-45), 0))
    add_brace("Cottage_Brace_Front_R2", (2.95, -4.20, 5.60), (0.14, 0.14, 1.35), (0, math.radians(45), 0))

    add_brace("Cottage_Brace_Left_F", (-3.50, -3.55, 4.45), (0.14, 0.14, 1.35), (math.radians(-45), 0, 0))
    add_brace("Cottage_Brace_Left_B", (-3.50, 3.55, 4.45), (0.14, 0.14, 1.35), (math.radians(45), 0, 0))
    add_brace("Cottage_Brace_Right_F", (3.50, -3.55, 4.45), (0.14, 0.14, 1.35), (math.radians(-45), 0, 0))
    add_brace("Cottage_Brace_Right_B", (3.50, 3.55, 4.45), (0.14, 0.14, 1.35), (math.radians(45), 0, 0))

    # 3. Lime Plaster Infill Panels
    create_box("Cottage_Plaster_Front_Low", (7.0, 0.12, 1.05), (0.0, -4.20, 4.40), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Front_High", (7.0, 0.12, 1.05), (0.0, -4.20, 5.60), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Rear_Low", (7.0, 0.12, 1.05), (0.0, 4.20, 4.40), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Rear_High", (7.0, 0.12, 1.05), (0.0, 4.20, 5.60), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Left_Low", (0.12, 8.4, 1.05), (-3.50, 0.0, 4.40), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Left_High", (0.12, 8.4, 1.05), (-3.50, 0.0, 5.60), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Right_Low", (0.12, 8.4, 1.05), (3.50, 0.0, 4.40), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Right_High", (0.12, 8.4, 1.05), (3.50, 0.0, 5.60), col_plaster, mat_plaster)

def build_roof_structure():
    col_roof = "05_Roof"
    mat_tile = "M_Clay_Tile"
    mat_wood = "M_Aged_Oak"
    mat_plaster = "M_Plaster_Historic"

    # 1. Triangular Plaster Gables
    def make_triangular_gable(name, y_pos, y_thickness=0.18):
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        v_bl = bm.verts.new((-3.50, y_pos, 6.25))
        v_br = bm.verts.new((3.50, y_pos, 6.25))
        v_ap = bm.verts.new((0.0, y_pos, 8.22))
        f = bm.faces.new((v_bl, v_br, v_ap))
        res = bmesh.ops.extrude_face_region(bm, geom=[f])
        verts_ext = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=Vector((0, y_thickness, 0)), verts=verts_ext)
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(name, mesh)
        link_to_collection(obj, col_roof)
        apply_modifiers(obj, bevel_width=0.02)
        assign_material(obj, mat_plaster)
        return obj

    make_triangular_gable("Cottage_Gable_Front_Plaster", -4.26, -0.15)
    make_triangular_gable("Cottage_Gable_Rear_Plaster", 4.26, 0.15)

    # Gable Timber Framework
    create_box("Cottage_Gable_TieBeam_F", (7.45, 0.22, 0.22), (0.0, -4.30, 6.25), col_roof, mat_wood)
    create_box("Cottage_Gable_KingPost_F", (0.22, 0.22, 1.85), (0.0, -4.30, 7.20), col_roof, mat_wood)
    create_box("Cottage_Gable_TieBeam_B", (7.45, 0.22, 0.22), (0.0, 4.30, 6.25), col_roof, mat_wood)
    create_box("Cottage_Gable_KingPost_B", (0.22, 0.22, 1.85), (0.0, 4.30, 7.20), col_roof, mat_wood)

    # 2. Left and Right Roof Planes
    def create_roof_slope_mesh(name, x_eave, x_ridge, y_start, y_end, z_eave, z_ridge, thickness=0.16):
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()

        dx = x_ridge - x_eave
        dz = z_ridge - z_eave
        length = math.sqrt(dx**2 + dz**2)
        nx = -dz / length if dx > 0 else dz / length
        nz = abs(dx) / length

        v1 = bm.verts.new((x_eave, y_start, z_eave))
        v2 = bm.verts.new((x_eave, y_end, z_eave))
        v3 = bm.verts.new((x_ridge, y_end, z_ridge))
        v4 = bm.verts.new((x_ridge, y_start, z_ridge))

        f_top = bm.faces.new((v1, v2, v3, v4))

        res = bmesh.ops.extrude_face_region(bm, geom=[f_top])
        verts_ext = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=Vector((-nx * thickness, 0, -nz * thickness)), verts=verts_ext)

        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(name, mesh)
        link_to_collection(obj, col_roof)
        apply_modifiers(obj, bevel_width=0.025)
        assign_material(obj, mat_tile)
        return obj

    create_roof_slope_mesh("Cottage_Roof_Slope_Left", -4.20, -0.02, -4.85, 4.85, 6.00, 8.24)
    create_roof_slope_mesh("Cottage_Roof_Slope_Right", 4.20, 0.02, -4.85, 4.85, 6.00, 8.24)

    # 3. Stepped Overlapping Clay Tile Courses
    slope_angle = math.atan2(2.24, 4.18)
    for c_i in range(5):
        t = (c_i + 0.5) / 5.0
        # Left side
        lx = -4.18 + t * 4.18
        lz = 6.00 + t * 2.24
        t_l = create_box(
            f"Cottage_Roof_TileCourse_L_{c_i:02d}",
            (0.70, 9.75, 0.05),
            (lx, 0.0, lz + 0.09),
            col_roof,
            mat_tile,
            bevel_width=0.015
        )
        t_l.rotation_euler = (0, -slope_angle, 0)

        # Right side
        rx = 4.18 - t * 4.18
        rz = 6.00 + t * 2.24
        t_r = create_box(
            f"Cottage_Roof_TileCourse_R_{c_i:02d}",
            (0.70, 9.75, 0.05),
            (rx, 0.0, rz + 0.09),
            col_roof,
            mat_tile,
            bevel_width=0.015
        )
        t_r.rotation_euler = (0, slope_angle, 0)

    # 4. Ridge Capping Beam & Clay Ridge Tiles
    create_box("Cottage_Roof_Ridge_Cap", (0.35, 9.90, 0.22), (0.0, 0.0, 8.32), col_roof, mat_tile, bevel_width=0.03)

    # 5. Ornamental Carved Bargeboards along Gable Edges
    def create_bargeboard(name, x_eave, x_ridge, y_pos, z_eave, z_ridge):
        dx = x_ridge - x_eave
        dz = z_ridge - z_eave
        length = math.sqrt(dx**2 + dz**2)
        slope = math.atan2(dz, abs(dx))
        rot_y = -slope if x_eave < 0 else slope

        cx = (x_eave + x_ridge) * 0.5
        cz = (z_eave + z_ridge) * 0.5

        obj = create_box(name, (length + 0.12, 0.08, 0.32), (cx, y_pos, cz), col_roof, mat_wood, bevel_width=0.02)
        obj.rotation_euler = (0, rot_y, 0)
        return obj

    # Front Bargeboards
    create_bargeboard("Cottage_Bargeboard_Front_Left", -4.20, 0.0, -4.88, 6.00, 8.25)
    create_bargeboard("Cottage_Bargeboard_Front_Right", 4.20, 0.0, -4.88, 6.00, 8.25)
    # Rear Bargeboards
    create_bargeboard("Cottage_Bargeboard_Rear_Left", -4.20, 0.0, 4.88, 6.00, 8.25)
    create_bargeboard("Cottage_Bargeboard_Rear_Right", 4.20, 0.0, 4.88, 6.00, 8.25)

    # Carved Gable Finials
    create_box("Cottage_Finial_Apex_Front", (0.14, 0.14, 0.75), (0.0, -4.88, 8.55), col_roof, mat_wood, bevel_width=0.02)
    create_box("Cottage_Finial_Apex_Rear", (0.14, 0.14, 0.75), (0.0, 4.88, 8.55), col_roof, mat_wood, bevel_width=0.02)

    # 6. Entrance Porch Canopy over Front Entrance
    p_roof = create_box("Cottage_Porch_Canopy_Roof", (1.90, 1.15, 0.08), (-0.60, -4.72, 3.28), col_roof, mat_tile)
    p_roof.rotation_euler = (math.radians(24.0), 0, 0)
    create_box("Cottage_Porch_Bracket_L", (0.12, 0.70, 0.70), (-1.45, -4.45, 3.00), col_roof, mat_wood)
    create_box("Cottage_Porch_Bracket_R", (0.12, 0.70, 0.70), (0.25, -4.45, 3.00), col_roof, mat_wood)

def build_stone_chimney():
    col = "07_Chimney"
    mat_stone = "M_Rough_Stone"
    mat_tile = "M_Clay_Tile"

    # Massive exterior stone chimney stack on the right gable (X = +3.4m to +4.7m)
    create_box("Cottage_Chimney_Base", (1.30, 2.40, 3.85), (3.92, 0.0, 1.925), col, mat_stone, bevel_width=0.05)
    create_box("Cottage_Chimney_Shoulder_1", (1.38, 2.48, 0.22), (3.92, 0.0, 3.88), col, mat_stone, bevel_width=0.04)
    create_box("Cottage_Chimney_MidStack", (1.12, 1.85, 2.35), (3.82, 0.0, 5.08), col, mat_stone, bevel_width=0.04)
    create_box("Cottage_Chimney_Shoulder_2", (1.18, 1.92, 0.20), (3.82, 0.0, 6.28), col, mat_stone, bevel_width=0.03)
    create_box("Cottage_Chimney_UpperStack", (0.95, 1.35, 2.58), (3.78, 0.0, 7.60), col, mat_stone, bevel_width=0.03)
    create_box("Cottage_Chimney_Crown", (1.10, 1.50, 0.22), (3.78, 0.0, 8.95), col, mat_stone, bevel_width=0.03)

    for i, pot_y in enumerate([-0.36, 0.36]):
        create_box(f"Cottage_Chimney_Pot_{i}", (0.36, 0.36, 0.65), (3.78, pot_y, 9.35), col, mat_tile, bevel_width=0.02)
        create_box(f"Cottage_Chimney_PotRim_{i}", (0.42, 0.42, 0.08), (3.78, pot_y, 9.65), col, mat_tile, bevel_width=0.015)

    # Interior Fireplace Hearth & Heavy Oak Mantel
    create_box("Cottage_Interior_Hearth_Base", (0.85, 1.85, 0.32), (2.85, 0.0, 1.02), "08_Interior", mat_stone)
    create_box("Cottage_Interior_Mantel_Beam", (0.32, 2.05, 0.26), (2.75, 0.0, 2.50), "08_Interior", "M_Aged_Oak")

def build_doors_and_windows():
    col = "06_Doors_Windows"
    mat_wood = "M_Aged_Oak"
    mat_iron = "M_Wrought_Iron"
    mat_glass = "M_Leaded_Glass"
    mat_stone = "M_Rough_Stone"

    # Front Entrance Door
    create_box("Cottage_Door_PlankLeaf", (1.02, 0.08, 2.10), (-0.60, -4.06, 1.95), col, mat_wood, bevel_width=0.015)
    create_box("Cottage_Door_Frame_L", (0.14, 0.18, 2.20), (-1.16, -4.05, 2.00), col, mat_wood)
    create_box("Cottage_Door_Frame_R", (0.14, 0.18, 2.20), (-0.04, -4.05, 2.00), col, mat_wood)
    create_box("Cottage_Door_Frame_Head", (1.26, 0.18, 0.16), (-0.60, -4.05, 3.12), col, mat_wood)
    create_box("Cottage_Door_Hinge_Top", (0.68, 0.04, 0.06), (-0.65, -4.11, 2.65), col, mat_iron)
    create_box("Cottage_Door_Hinge_Bottom", (0.68, 0.04, 0.06), (-0.65, -4.11, 1.35), col, mat_iron)
    create_box("Cottage_Door_Handle_Ring", (0.10, 0.05, 0.12), (-0.22, -4.12, 1.95), col, mat_iron)

    # Ground Floor Front Window
    create_box("Cottage_GF_Win_Sill", (1.18, 0.24, 0.10), (1.65, -4.14, 1.78), col, mat_stone, bevel_width=0.02)
    create_box("Cottage_GF_Win_Mullion", (0.10, 0.14, 1.15), (1.65, -4.02, 2.40), col, mat_stone)
    create_box("Cottage_GF_Win_Glass_L", (0.42, 0.02, 1.12), (1.37, -4.02, 2.40), col, mat_glass, bevel=False)
    create_box("Cottage_GF_Win_Glass_R", (0.42, 0.02, 1.12), (1.93, -4.02, 2.40), col, mat_glass, bevel=False)

    # Ground Floor Side Windows
    for i, wy in enumerate([-1.45, 1.45]):
        create_box(f"Cottage_GF_SideWin_Sill_{i}", (0.24, 0.88, 0.10), (-3.34, wy, 1.95), col, mat_stone)
        create_box(f"Cottage_GF_SideWin_Glass_{i}", (0.02, 0.62, 1.25), (-3.20, wy, 2.65), col, mat_glass, bevel=False)

    # Upper Floor Front Casement Windows with Open Shutters
    for i, wx in enumerate([-1.55, 1.55]):
        create_box(f"Cottage_UF_Win_Sill_{i}", (1.15, 0.24, 0.10), (wx, -4.32, 4.95), col, mat_wood)
        create_box(f"Cottage_UF_Win_Frame_{i}", (0.98, 0.14, 0.98), (wx, -4.22, 5.50), col, mat_wood)
        create_box(f"Cottage_UF_Win_Mullion_{i}", (0.08, 0.12, 0.88), (wx, -4.22, 5.50), col, mat_wood)
        create_box(f"Cottage_UF_Win_Glass_{i}", (0.82, 0.02, 0.82), (wx, -4.22, 5.50), col, mat_glass, bevel=False)

        sh_l = create_box(f"Cottage_Shutter_{i}_L", (0.42, 0.04, 0.86), (wx - 0.58, -4.34, 5.50), col, mat_wood)
        sh_l.rotation_euler = (0, 0, math.radians(52))
        sh_r = create_box(f"Cottage_Shutter_{i}_R", (0.42, 0.04, 0.86), (wx + 0.58, -4.34, 5.50), col, mat_wood)
        sh_r.rotation_euler = (0, 0, math.radians(-52))

def build_interior_architecture():
    col = "08_Interior"
    mat_stone = "M_Rough_Stone"
    mat_wood = "M_Aged_Oak"
    mat_iron = "M_Wrought_Iron"

    # Flagstone Ground Floor & Oak Upper Floorboards
    create_box("Cottage_Floor_Flagstones", (6.10, 7.70, 0.08), (0.0, 0.0, 0.88), col, mat_stone)
    create_box("Cottage_Floor_Upper_Planks", (7.15, 8.55, 0.06), (0.0, 0.0, 3.86), col, mat_wood)

    # Summer Spine Beam
    create_box("Cottage_GF_Spine_SummerBeam", (0.36, 8.20, 0.32), (0.0, 0.0, 3.45), col, mat_wood)

    # Interior Stone Partition
    create_box("Cottage_Interior_Partition_GF", (0.36, 4.20, 2.60), (1.10, 0.0, 2.20), col, mat_stone)

    # Wooden Staircase
    for st in range(10):
        sz = 0.92 + st * 0.28
        sy = 1.40 + st * 0.24
        create_box(f"Cottage_Stair_Tread_{st:02d}", (0.95, 0.28, 0.08), (-2.55, sy, sz), col, mat_wood)
    stair_rail = create_box("Cottage_Stair_Handrail", (0.08, 2.70, 0.12), (-2.05, 2.55, 2.48), col, mat_wood)
    stair_rail.rotation_euler = (math.radians(-44), 0, 0)

    # Upper floor roof tie beams
    create_box("Cottage_UF_TieBeam_1", (7.10, 0.22, 0.20), (0.0, -1.8, 6.40), col, mat_wood)
    create_box("Cottage_UF_TieBeam_2", (7.10, 0.22, 0.20), (0.0, 1.8, 6.40), col, mat_wood)

    # Interior Furniture Blockout:
    # 1. Ground Floor Heavy Trestle Dining Table & Benches
    create_box("Cottage_Interior_Table_Top", (2.20, 0.90, 0.08), (-0.80, 0.0, 1.65), col, mat_wood)
    create_box("Cottage_Interior_Table_Leg_1", (0.16, 0.70, 0.72), (-1.65, 0.0, 1.25), col, mat_wood)
    create_box("Cottage_Interior_Table_Leg_2", (0.16, 0.70, 0.72), (0.05, 0.0, 1.25), col, mat_wood)
    create_box("Cottage_Interior_Bench_1", (2.20, 0.30, 0.06), (-0.80, -0.75, 1.35), col, mat_wood)
    create_box("Cottage_Interior_Bench_2", (2.20, 0.30, 0.06), (-0.80, 0.75, 1.35), col, mat_wood)

    # 2. Fireplace Hanging Cooking Pot & Iron Grate
    create_box("Cottage_Interior_FireGrate", (0.60, 0.50, 0.20), (2.85, 0.0, 1.12), col, mat_iron)
    create_box("Cottage_Interior_CookingPot", (0.35, 0.35, 0.32), (2.85, 0.0, 1.45), col, mat_iron, bevel_width=0.02)

    # 3. Upper Floor Loft Bed Frame
    create_box("Cottage_Interior_Bed_Frame", (1.60, 2.10, 0.45), (1.80, 2.20, 4.10), col, mat_wood)
    create_box("Cottage_Interior_Bed_Mattress", (1.45, 1.95, 0.22), (1.80, 2.20, 4.40), col, "M_Plaster_Historic")

def build_exterior_props():
    col = "09_Exterior_Props"
    mat_wood = "M_Aged_Oak"
    mat_iron = "M_Wrought_Iron"
    mat_stone = "M_Rough_Stone"
    mat_lantern = "M_Lantern_Glow"

    # 1. Cluster of 3 Barrels with iron hoops
    def make_barrel(name, loc, radius=0.38, height=0.92):
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=radius, radius2=radius*0.86, depth=height)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        obj.location = loc
        link_to_collection(obj, col)
        apply_modifiers(obj, bevel_width=0.015)
        assign_material(obj, mat_wood)

        for h_z in [-0.28, 0.0, 0.28]:
            create_box(f"{name}_Hoop_{h_z}", (radius*2.06, radius*2.06, 0.04), (loc[0], loc[1], loc[2] + h_z), col, mat_iron, bevel=False)
        return obj

    make_barrel("Cottage_Prop_Barrel_01", (-3.95, -1.80, 0.46))
    make_barrel("Cottage_Prop_Barrel_02", (-3.95, -2.65, 0.46))
    b3 = make_barrel("Cottage_Prop_Barrel_03", (-3.95, -2.20, 1.32))
    b3.rotation_euler = (0, math.radians(90), math.radians(18))

    # 2. Wooden Storage Crates
    create_box("Cottage_Prop_Crate_Large", (0.80, 0.80, 0.80), (-3.88, 0.25, 0.40), col, mat_wood, bevel_width=0.02)
    c2 = create_box("Cottage_Prop_Crate_Small", (0.58, 0.58, 0.58), (-3.88, 1.05, 0.29), col, mat_wood, bevel_width=0.015)
    c2.rotation_euler = (0, 0, math.radians(22))

    # 3. Stacked Split Firewood under eave
    create_box("Cottage_Prop_Firewood_Stack", (0.65, 2.30, 0.88), (3.85, -2.75, 0.44), col, mat_wood, bevel_width=0.03)

    # 4. Medieval Iron Wall Lantern beside front door
    create_box("Cottage_Prop_Lantern_Bracket", (0.06, 0.48, 0.38), (0.28, -4.24, 2.48), col, mat_iron)
    create_box("Cottage_Prop_Lantern_Cage", (0.24, 0.24, 0.38), (0.28, -4.50, 2.36), col, mat_iron, bevel_width=0.01)
    create_box("Cottage_Prop_Lantern_Core", (0.12, 0.12, 0.20), (0.28, -4.50, 2.36), col, mat_lantern, bevel=False)

    # 5. Wooden Window Flowerbox under front upper right window
    create_box("Cottage_Prop_Flowerbox", (1.15, 0.30, 0.24), (1.55, -4.44, 4.80), col, mat_wood, bevel_width=0.02)
    create_box("Cottage_Prop_Flower_Foliage", (1.05, 0.24, 0.16), (1.55, -4.44, 4.90), col, mat_stone, bevel_width=0.02)

    # 6. Exterior Decorative Stones / Boulders at Corner of Foundation
    boulders = [
        ((-3.85, -4.45), (0.55, 0.50, 0.38), 0.19),
        ((-4.10, -4.10), (0.42, 0.48, 0.32), 0.16),
        ((3.90, -4.40), (0.50, 0.45, 0.35), 0.18),
    ]
    for i, ((bx, by), bsize, bz) in enumerate(boulders):
        create_box(f"Cottage_Prop_Stone_{i}", bsize, (bx, by, bz), col, mat_stone, bevel_width=0.04)

    # 7. Climbing Ivy Vine Blockout on Left Stone Foundation Corner
    create_box("Cottage_Prop_Ivy_Trunk", (0.08, 0.08, 2.80), (-3.62, -4.22, 1.40), col, mat_wood, bevel_width=0.02)
    for vi in range(4):
        create_box(f"Cottage_Prop_Ivy_Foliage_{vi}", (0.45, 0.45, 0.35), (-3.65, -4.15 + vi*0.35, 1.20 + vi*0.65), col, mat_stone, bevel_width=0.03)

def build_complete_cottage():
    print("--- Clearing previous cottage objects ---")
    clear_all_cottage_objects()

    print("--- Building Detailed Medieval Cottage ---")
    build_foundation()
    build_ground_floor_masonry()
    build_jetty_and_framing()
    build_roof_structure()
    build_stone_chimney()
    build_doors_and_windows()
    build_interior_architecture()
    build_exterior_props()
    print("--- Detailed cottage blockout successfully built! ---")

if __name__ == '__main__':
    build_complete_cottage()
