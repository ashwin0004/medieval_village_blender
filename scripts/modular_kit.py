"""
Medieval Fantasy Village - Modular Architecture Kit
Procedurally constructs a complete, metric-aligned modular medieval architecture kit:
1. Stone Foundations (Straight 4m, Straight 2m, Corner 90)
2. Stone Walls Ground Floor (Solid 4m, Window 4m, Doorway 4m, Corner 90)
3. Timber & Plaster Upper Walls (Solid 4m, St. Andrew's Cross 4m, Window 4m, Corner 90, Jetty Floor 4m)
4. Gable Walls & Roof Panels (Triangular Gable 4m, Bargeboard Set, Clay Tile Roof 4m, Slate Roof 4m, Ridge Tiles 4m, Dormer Unit)
5. Door & Window Components (Arched Oak Frame, Plank Door with Iron Strap Hinges, Stone 2-Light Mullion, Timber Casement, Shutters)
6. Arches & Stairs (Roman Semicircular Stone Arch, Gothic Pointed Arch, Stone Steps 4-Tier, Timber Staircase)
7. Modular Chimney System (Base Hearth, Stackable Shaft 2m, Corbeled Crown with Dual Terracotta Pots)
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler

def get_or_create_collection(name, parent=None):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent is None:
            bpy.context.scene.collection.children.link(col)
        else:
            parent.children.link(col)
    return col

def clear_collection(col_name):
    col = bpy.data.collections.get(col_name)
    if col:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

def apply_modifiers(obj, bevel_width=0.016, segments=2):
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

def link_to_col(obj, col_name):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    target = bpy.data.collections.get(col_name)
    if not target:
        target = bpy.context.scene.collection
    target.objects.link(obj)

def create_box(name, size, location, col_name, mat_name=None, bevel=True, bevel_width=0.016):
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
    link_to_col(obj, col_name)

    if bevel:
        apply_modifiers(obj, bevel_width=bevel_width)
    if mat_name:
        assign_material(obj, mat_name)

    return obj

# ==============================================================================
# 1. FOUNDATIONS (Height: 0.85m, Depth: 0.50m)
# ==============================================================================
def build_foundations(base_x=0.0, base_y=0.0):
    col = "02_ARCHITECTURE_MODULAR/01_Foundations"
    mat_stone = "M_Stone_Rubble"
    mat_ashlar = "M_Stone_AshlarGrey"

    # Mod_Foundation_4m (Width: 4.0m, Depth: 0.50m, Height: 0.85m)
    # Origin at (0, 0, 0)
    f4_core = create_box("Mod_Foundation_4m_Core", (4.0, 0.50, 0.85), (base_x, base_y, 0.425), col, mat_stone, bevel_width=0.03)
    f4_cap = create_box("Mod_Foundation_4m_WaterTable", (4.08, 0.56, 0.10), (base_x, base_y, 0.85), col, mat_ashlar, bevel_width=0.02)
    # Dressed ashlar quoins at ends
    create_box("Mod_Foundation_4m_Quoin_L", (0.50, 0.52, 0.28), (base_x - 1.75, base_y, 0.20), col, mat_ashlar, bevel_width=0.025)
    create_box("Mod_Foundation_4m_Quoin_R", (0.50, 0.52, 0.28), (base_x + 1.75, base_y, 0.20), col, mat_ashlar, bevel_width=0.025)

    # Mod_Foundation_2m (Width: 2.0m, Depth: 0.50m, Height: 0.85m)
    x2 = base_x + 4.5
    f2_core = create_box("Mod_Foundation_2m_Core", (2.0, 0.50, 0.85), (x2, base_y, 0.425), col, mat_stone, bevel_width=0.03)
    f2_cap = create_box("Mod_Foundation_2m_WaterTable", (2.08, 0.56, 0.10), (x2, base_y, 0.85), col, mat_ashlar, bevel_width=0.02)

    # Mod_Foundation_Corner_90 (2.0m x 2.0m L-Corner)
    xc = base_x + 8.5
    # Arm X
    create_box("Mod_Foundation_Corner_ArmX", (2.0, 0.50, 0.85), (xc, base_y - 0.75, 0.425), col, mat_stone, bevel_width=0.03)
    # Arm Y
    create_box("Mod_Foundation_Corner_ArmY", (0.50, 1.5, 0.85), (xc + 0.75, base_y + 0.25, 0.425), col, mat_stone, bevel_width=0.03)
    create_box("Mod_Foundation_Corner_CapX", (2.06, 0.56, 0.10), (xc, base_y - 0.75, 0.85), col, mat_ashlar, bevel_width=0.02)
    create_box("Mod_Foundation_Corner_CapY", (0.56, 1.56, 0.10), (xc + 0.75, base_y + 0.25, 0.85), col, mat_ashlar, bevel_width=0.02)
    # Heavy corner stone
    create_box("Mod_Foundation_Corner_Quoin", (0.58, 0.58, 0.85), (xc + 0.75, base_y - 0.75, 0.425), col, mat_ashlar, bevel_width=0.03)

# ==============================================================================
# 2. STONE WALLS (Height: 2.75m, Thickness: 0.42m)
# ==============================================================================
def build_stone_walls(base_x=0.0, base_y=0.0):
    col = "02_ARCHITECTURE_MODULAR/02_Walls_Stone"
    mat_stone = "M_Stone_Rubble"
    mat_ashlar = "M_Stone_AshlarGrey"
    mat_glass = "M_Glass_Leaded"

    # 1. Solid Stone Wall 4m
    w_solid = create_box("Mod_Wall_Stone_Solid_4m", (4.0, 0.42, 2.75), (base_x, base_y, 1.375), col, mat_stone)
    # Top timber wall plate bed
    create_box("Mod_Wall_Stone_Solid_4m_Bed", (4.02, 0.44, 0.08), (base_x, base_y, 2.75), col, "M_Wood_AgedOak")

    # 2. Stone Wall with Window 4m (Centered 1.0m x 1.2m window opening)
    xw = base_x + 5.0
    create_box("Mod_Wall_Stone_Win_Left", (1.50, 0.42, 2.75), (xw - 1.25, base_y, 1.375), col, mat_stone)
    create_box("Mod_Wall_Stone_Win_Right", (1.50, 0.42, 2.75), (xw + 1.25, base_y, 1.375), col, mat_stone)
    create_box("Mod_Wall_Stone_Win_SillWall", (1.00, 0.42, 0.90), (xw, base_y, 0.45), col, mat_stone)
    create_box("Mod_Wall_Stone_Win_LintelWall", (1.00, 0.42, 0.65), (xw, base_y, 2.425), col, mat_stone)
    # Dressed stone window surround
    create_box("Mod_Wall_Stone_Win_Sill", (1.18, 0.24, 0.10), (xw, base_y - 0.14, 0.90), col, mat_ashlar, bevel_width=0.02)
    create_box("Mod_Wall_Stone_Win_Lintel", (1.24, 0.46, 0.22), (xw, base_y, 2.15), col, mat_ashlar, bevel_width=0.02)
    create_box("Mod_Wall_Stone_Win_Mullion", (0.10, 0.14, 1.15), (xw, base_y, 1.50), col, mat_ashlar)
    create_box("Mod_Wall_Stone_Win_Glass", (0.84, 0.02, 1.10), (xw, base_y, 1.50), col, mat_glass, bevel=False)

    # 3. Stone Wall with Arched Doorway 4m
    xd = base_x + 10.0
    create_box("Mod_Wall_Stone_Door_Left", (1.40, 0.42, 2.75), (xd - 1.30, base_y, 1.375), col, mat_stone)
    create_box("Mod_Wall_Stone_Door_Right", (1.40, 0.42, 2.75), (xd + 1.30, base_y, 1.375), col, mat_stone)
    create_box("Mod_Wall_Stone_Door_LintelWall", (1.20, 0.42, 0.55), (xd, base_y, 2.475), col, mat_stone)
    # Heavy stone voussoir arch lintel
    create_box("Mod_Wall_Stone_Door_ArchLintel", (1.36, 0.48, 0.36), (xd, base_y, 2.22), col, mat_ashlar, bevel_width=0.03)

    # 4. Stone Wall Corner 90 (2m x 2m L-shape with dressed ashlar quoins)
    xc = base_x + 14.5
    create_box("Mod_Wall_Stone_Corner_ArmX", (2.0, 0.42, 2.75), (xc, base_y - 0.79, 1.375), col, mat_stone)
    create_box("Mod_Wall_Stone_Corner_ArmY", (0.42, 1.58, 2.75), (xc + 0.79, base_y + 0.21, 1.375), col, mat_stone)
    for q_i in range(5):
        qz = 0.35 + q_i * 0.55
        create_box(f"Mod_Wall_Stone_Corner_Quoin_{q_i}", (0.50, 0.50, 0.32), (xc + 0.79, base_y - 0.79, qz), col, mat_ashlar, bevel_width=0.025)

# ==============================================================================
# 3. TIMBER FRAMING & PLASTER WALLS (Height: 2.40m, Width: 4.0m)
# ==============================================================================
def build_timber_walls(base_x=0.0, base_y=0.0):
    col = "02_ARCHITECTURE_MODULAR/03_Walls_Timber"
    mat_wood = "M_Wood_AgedOak"
    mat_plaster = "M_Plaster_Lime"
    mat_glass = "M_Glass_Leaded"

    # 1. Solid Half-Timber Wall with Studs & Plaster Infill
    # Structural framework
    create_box("Mod_Timber_Solid_4m_SolePlate", (4.0, 0.20, 0.18), (base_x, base_y, 0.09), col, mat_wood)
    create_box("Mod_Timber_Solid_4m_TopPlate", (4.0, 0.20, 0.18), (base_x, base_y, 2.31), col, mat_wood)
    create_box("Mod_Timber_Solid_4m_MidGirt", (4.0, 0.18, 0.16), (base_x, base_y, 1.20), col, mat_wood)
    # Vertical posts
    for i, sx in enumerate([-1.90, -0.95, 0.0, 0.95, 1.90]):
        create_box(f"Mod_Timber_Solid_4m_Post_{i}", (0.20, 0.20, 2.40), (base_x + sx, base_y, 1.20), col, mat_wood)
    # Recessed Plaster Infill Panels
    create_box("Mod_Timber_Solid_4m_Plaster_Low", (3.80, 0.12, 0.95), (base_x, base_y, 0.65), col, mat_plaster)
    create_box("Mod_Timber_Solid_4m_Plaster_High", (3.80, 0.12, 0.95), (base_x, base_y, 1.75), col, mat_plaster)

    # 2. Half-Timber Wall with St. Andrew's Cross Braces (Fachwerk)
    xb = base_x + 5.0
    create_box("Mod_Timber_Cross_4m_SolePlate", (4.0, 0.20, 0.18), (xb, base_y, 0.09), col, mat_wood)
    create_box("Mod_Timber_Cross_4m_TopPlate", (4.0, 0.20, 0.18), (xb, base_y, 2.31), col, mat_wood)
    create_box("Mod_Timber_Cross_4m_MidGirt", (4.0, 0.18, 0.16), (xb, base_y, 1.20), col, mat_wood)
    create_box("Mod_Timber_Cross_4m_Post_L", (0.20, 0.20, 2.40), (xb - 1.90, base_y, 1.20), col, mat_wood)
    create_box("Mod_Timber_Cross_4m_Post_M", (0.20, 0.20, 2.40), (xb, base_y, 1.20), col, mat_wood)
    create_box("Mod_Timber_Cross_4m_Post_R", (0.20, 0.20, 2.40), (xb + 1.90, base_y, 1.20), col, mat_wood)
    # Diagonal X-Braces
    def make_brace(name, loc, rot_y):
        b = create_box(name, (0.14, 0.14, 1.35), loc, col, mat_wood)
        b.rotation_euler = (0, rot_y, 0)
    make_brace("Mod_Timber_Cross_4m_Brace_L1", (xb - 0.95, base_y, 0.65), math.radians(45))
    make_brace("Mod_Timber_Cross_4m_Brace_L2", (xb - 0.95, base_y, 0.65), math.radians(-45))
    make_brace("Mod_Timber_Cross_4m_Brace_R1", (xb + 0.95, base_y, 0.65), math.radians(45))
    make_brace("Mod_Timber_Cross_4m_Brace_R2", (xb + 0.95, base_y, 0.65), math.radians(-45))
    # Upper arch braces
    make_brace("Mod_Timber_Cross_4m_Brace_U1", (xb - 0.95, base_y, 1.75), math.radians(45))
    make_brace("Mod_Timber_Cross_4m_Brace_U2", (xb + 0.95, base_y, 1.75), math.radians(-45))
    # Infill
    create_box("Mod_Timber_Cross_4m_Plaster_L", (1.80, 0.12, 2.10), (xb - 0.95, base_y, 1.20), col, mat_plaster)
    create_box("Mod_Timber_Cross_4m_Plaster_R", (1.80, 0.12, 2.10), (xb + 0.95, base_y, 1.20), col, mat_plaster)

    # 3. Half-Timber Wall with Integrated Casement Window & Shutters
    xw = base_x + 10.0
    create_box("Mod_Timber_Win_4m_SolePlate", (4.0, 0.20, 0.18), (xw, base_y, 0.09), col, mat_wood)
    create_box("Mod_Timber_Win_4m_TopPlate", (4.0, 0.20, 0.18), (xw, base_y, 2.31), col, mat_wood)
    create_box("Mod_Timber_Win_4m_Post_L", (0.20, 0.20, 2.40), (xw - 1.90, base_y, 1.20), col, mat_wood)
    create_box("Mod_Timber_Win_4m_Post_R", (0.20, 0.20, 2.40), (xw + 1.90, base_y, 1.20), col, mat_wood)
    # Window posts framing opening
    create_box("Mod_Timber_Win_4m_Jamb_L", (0.16, 0.18, 2.40), (xw - 0.65, base_y, 1.20), col, mat_wood)
    create_box("Mod_Timber_Win_4m_Jamb_R", (0.16, 0.18, 2.40), (xw + 0.65, base_y, 1.20), col, mat_wood)
    create_box("Mod_Timber_Win_4m_Sill", (1.20, 0.24, 0.12), (xw, base_y - 0.02, 0.85), col, mat_wood)
    create_box("Mod_Timber_Win_4m_Head", (1.20, 0.20, 0.14), (xw, base_y, 1.95), col, mat_wood)
    # Glass & mullion
    create_box("Mod_Timber_Win_4m_Mullion", (0.08, 0.12, 0.95), (xw, base_y, 1.40), col, mat_wood)
    create_box("Mod_Timber_Win_4m_Glass", (0.95, 0.02, 0.95), (xw, base_y, 1.40), col, mat_glass, bevel=False)
    # Shutters angled open
    sh_l = create_box("Mod_Timber_Win_4m_Shutter_L", (0.44, 0.04, 0.92), (xw - 0.68, base_y - 0.18, 1.40), col, mat_wood)
    sh_l.rotation_euler = (0, 0, math.radians(52))
    sh_r = create_box("Mod_Timber_Win_4m_Shutter_R", (0.44, 0.04, 0.92), (xw + 0.68, base_y - 0.18, 1.40), col, mat_wood)
    sh_r.rotation_euler = (0, 0, math.radians(-52))
    # Infill
    create_box("Mod_Timber_Win_4m_Plaster_L", (1.10, 0.12, 2.10), (xw - 1.25, base_y, 1.20), col, mat_plaster)
    create_box("Mod_Timber_Win_4m_Plaster_R", (1.10, 0.12, 2.10), (xw + 1.25, base_y, 1.20), col, mat_plaster)
    create_box("Mod_Timber_Win_4m_Plaster_B", (1.00, 0.12, 0.75), (xw, base_y, 0.45), col, mat_plaster)
    create_box("Mod_Timber_Win_4m_Plaster_T", (1.00, 0.12, 0.35), (xw, base_y, 2.15), col, mat_plaster)

    # 4. Cantilevered Timber Jetty Floor Section 4m
    xj = base_x + 14.5
    create_box("Mod_Jetty_Floor_4m_Bressummer", (4.0, 0.28, 0.28), (xj, base_y + 0.35, 0.14), col, mat_wood)
    for ji in range(5):
        j_x = xj - 1.80 + ji * 0.90
        create_box(f"Mod_Jetty_Floor_4m_Joist_{ji}", (0.16, 0.80, 0.22), (j_x, base_y, 0.11), col, mat_wood)
        create_box(f"Mod_Jetty_Floor_4m_Corbel_{ji}", (0.16, 0.28, 0.45), (j_x, base_y + 0.25, -0.22), col, mat_wood, bevel_width=0.02)
    create_box("Mod_Jetty_Floor_4m_Planks", (4.0, 0.80, 0.05), (xj, base_y, 0.27), col, mat_wood)

# ==============================================================================
# 4. GABLES & ROOF PANELS
# ==============================================================================
def build_gables_and_roofs(base_x=0.0, base_y=0.0):
    col = "02_ARCHITECTURE_MODULAR/04_Gables_Roofs"
    mat_wood = "M_Wood_AgedOak"
    mat_plaster = "M_Plaster_Lime"
    mat_clay = "M_Clay_Terracotta"
    mat_slate = "M_Slate_Dark"
    mat_glass = "M_Glass_Leaded"

    # 1. Triangular Gable Wall 4m (Width: 4.0m, Height: 2.0m)
    # Apex at (base_x, base_y, 2.0)
    mesh = bpy.data.meshes.new("Mod_Gable_Wall_Tri_4m")
    bm = bmesh.new()
    v1 = bm.verts.new((-2.0, 0.0, 0.0))
    v2 = bm.verts.new((2.0, 0.0, 0.0))
    v3 = bm.verts.new((0.0, 0.0, 2.0))
    f = bm.faces.new((v1, v2, v3))
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    verts_ext = [e for e in res['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=Vector((0, 0.16, 0)), verts=verts_ext)
    bm.to_mesh(mesh)
    bm.free()

    g_obj = bpy.data.objects.new("Mod_Gable_Wall_Tri_4m", mesh)
    g_obj.location = (base_x, base_y, 0.0)
    link_to_col(g_obj, col)
    apply_modifiers(g_obj, bevel_width=0.02)
    assign_material(g_obj, mat_plaster)

    # Gable Tie Beam & King Post
    create_box("Mod_Gable_TieBeam_4m", (4.20, 0.22, 0.20), (base_x, base_y, 0.0), col, mat_wood)
    create_box("Mod_Gable_KingPost_4m", (0.20, 0.20, 1.80), (base_x, base_y, 0.95), col, mat_wood)

    # 2. Gable Bargeboard Set with Carved Apex Finial
    xb = base_x + 4.5
    slope_angle = math.atan2(2.0, 2.0) # 45 deg
    slope_len = math.sqrt(2.0**2 + 2.0**2)
    bb_l = create_box("Mod_Bargeboard_Left", (slope_len + 0.15, 0.08, 0.28), (xb - 1.0, base_y, 1.0), col, mat_wood, bevel_width=0.02)
    bb_l.rotation_euler = (0, -slope_angle, 0)
    bb_r = create_box("Mod_Bargeboard_Right", (slope_len + 0.15, 0.08, 0.28), (xb + 1.0, base_y, 1.0), col, mat_wood, bevel_width=0.02)
    bb_r.rotation_euler = (0, slope_angle, 0)
    create_box("Mod_Bargeboard_Finial", (0.12, 0.12, 0.70), (xb, base_y, 2.25), col, mat_wood, bevel_width=0.02)

    # 3. Modular Clay Tile Roof Panel 4m (Width: 4.0m, Slope length: 3.5m)
    xr = base_x + 9.0
    r_panel = create_box("Mod_Roof_Panel_Clay_4m_Sarking", (4.0, 3.50, 0.14), (xr, base_y + 1.25, 1.20), col, mat_slate)
    r_panel.rotation_euler = (math.radians(-32.0), 0, 0)
    # Clay Tile courses overlay
    for c_i in range(5):
        t_y = base_y + c_i * 0.65
        t_z = 0.40 + c_i * 0.40
        tc = create_box(f"Mod_Roof_ClayCourse_{c_i}", (4.04, 0.55, 0.04), (xr, t_y, t_z), col, mat_clay, bevel_width=0.015)
        tc.rotation_euler = (math.radians(-32.0), 0, 0)

    # 4. Modular Slate Roof Panel 4m
    xs = base_x + 14.0
    s_panel = create_box("Mod_Roof_Panel_Slate_4m", (4.0, 3.50, 0.14), (xs, base_y + 1.25, 1.20), col, mat_slate)
    s_panel.rotation_euler = (math.radians(-32.0), 0, 0)
    for c_i in range(6):
        t_y = base_y + c_i * 0.52
        t_z = 0.35 + c_i * 0.33
        sc = create_box(f"Mod_Roof_SlateCourse_{c_i}", (4.04, 0.45, 0.03), (xs, t_y, t_z), col, mat_slate, bevel_width=0.01)
        sc.rotation_euler = (math.radians(-32.0), 0, 0)

    # 5. Half-Round Terracotta Ridge Tiles 4m
    x_rdg = base_x + 18.5
    for ri in range(9):
        ry = base_y - 1.80 + ri * 0.45
        create_box(f"Mod_Ridge_Tile_{ri}", (0.34, 0.44, 0.18), (x_rdg, ry, 0.10), col, mat_clay, bevel_width=0.02)

    # 6. Roof Dormer Window Unit
    xd = base_x + 22.0
    # Dormer base & timber cheeks
    create_box("Mod_Dormer_Cheek_L", (0.12, 1.40, 1.20), (xd - 0.65, base_y + 0.60, 0.60), col, mat_wood)
    create_box("Mod_Dormer_Cheek_R", (0.12, 1.40, 1.20), (xd + 0.65, base_y + 0.60, 0.60), col, mat_wood)
    create_box("Mod_Dormer_Gable", (1.42, 0.12, 0.65), (xd, base_y - 0.05, 1.50), col, mat_plaster)
    create_box("Mod_Dormer_Win_Frame", (1.10, 0.12, 0.90), (xd, base_y - 0.05, 0.75), col, mat_wood)
    create_box("Mod_Dormer_Glass", (0.90, 0.02, 0.75), (xd, base_y - 0.05, 0.75), col, mat_glass, bevel=False)
    # Pitched dormer roof
    d_roof_l = create_box("Mod_Dormer_Roof_L", (0.95, 1.55, 0.06), (xd - 0.40, base_y + 0.65, 1.65), col, mat_clay)
    d_roof_l.rotation_euler = (0, math.radians(-35.0), 0)
    d_roof_r = create_box("Mod_Dormer_Roof_R", (0.95, 1.55, 0.06), (xd + 0.40, base_y + 0.65, 1.65), col, mat_clay)
    d_roof_r.rotation_euler = (0, math.radians(35.0), 0)

# ==============================================================================
# 5. DOORS, WINDOWS & SHUTTERS
# ==============================================================================
def build_doors_and_windows(base_x=0.0, base_y=0.0):
    col = "02_ARCHITECTURE_MODULAR/05_Doors_Windows"
    mat_wood = "M_Wood_AgedOak"
    mat_ashlar = "M_Stone_AshlarGrey"
    mat_iron = "M_Iron_Wrought"
    mat_glass = "M_Glass_Leaded"

    # 1. Arched Oak Door Frame & Heavy Plank Door Leaf
    xd = base_x
    create_box("Mod_Door_Frame_L", (0.16, 0.20, 2.20), (xd - 0.58, base_y, 1.10), col, mat_wood)
    create_box("Mod_Door_Frame_R", (0.16, 0.20, 2.20), (xd + 0.58, base_y, 1.10), col, mat_wood)
    create_box("Mod_Door_Frame_Head", (1.32, 0.20, 0.18), (xd, base_y, 2.20), col, mat_wood)
    # Plank door leaf
    create_box("Mod_Door_Plank_Leaf", (1.00, 0.07, 2.05), (xd, base_y - 0.02, 1.05), col, mat_wood, bevel_width=0.015)
    # Wrought iron strap hinges & latch ring
    create_box("Mod_Door_Hinge_Top", (0.70, 0.03, 0.06), (xd - 0.10, base_y - 0.06, 1.75), col, mat_iron)
    create_box("Mod_Door_Hinge_Bottom", (0.70, 0.03, 0.06), (xd - 0.10, base_y - 0.06, 0.35), col, mat_iron)
    create_box("Mod_Door_Ring_Handle", (0.10, 0.05, 0.12), (xd + 0.35, base_y - 0.07, 1.05), col, mat_iron)

    # 2. Dressed Stone 2-Light Mullioned Window Frame
    xw = base_x + 3.0
    create_box("Mod_Window_Stone_Jamb_L", (0.14, 0.26, 1.30), (xw - 0.55, base_y, 0.65), col, mat_ashlar)
    create_box("Mod_Window_Stone_Jamb_R", (0.14, 0.26, 1.30), (xw + 0.55, base_y, 0.65), col, mat_ashlar)
    create_box("Mod_Window_Stone_Sill", (1.28, 0.32, 0.12), (xw, base_y - 0.04, 0.06), col, mat_ashlar, bevel_width=0.02)
    create_box("Mod_Window_Stone_Lintel", (1.28, 0.28, 0.18), (xw, base_y, 1.35), col, mat_ashlar, bevel_width=0.02)
    create_box("Mod_Window_Stone_Mullion", (0.10, 0.16, 1.20), (xw, base_y, 0.68), col, mat_ashlar)
    create_box("Mod_Window_Stone_Glass", (0.95, 0.02, 1.15), (xw, base_y, 0.68), col, mat_glass, bevel=False)

    # 3. Wooden Casement Window Frame with Leaded Glass
    xt = base_x + 6.0
    create_box("Mod_Window_Timber_Frame", (1.00, 0.14, 1.00), (xt, base_y, 0.50), col, mat_wood)
    create_box("Mod_Window_Timber_Sill", (1.15, 0.22, 0.08), (xt, base_y - 0.04, 0.04), col, mat_wood)
    create_box("Mod_Window_Timber_Mullion", (0.08, 0.12, 0.90), (xt, base_y, 0.50), col, mat_wood)
    create_box("Mod_Window_Timber_Glass", (0.84, 0.02, 0.84), (xt, base_y, 0.50), col, mat_glass, bevel=False)

    # 4. Pair of Operable Wooden Shutters
    xs = base_x + 8.5
    sh_l = create_box("Mod_Shutters_Left", (0.44, 0.04, 0.92), (xs - 0.45, base_y, 0.50), col, mat_wood)
    sh_l.rotation_euler = (0, 0, math.radians(50))
    sh_r = create_box("Mod_Shutters_Right", (0.44, 0.04, 0.92), (xs + 0.45, base_y, 0.50), col, mat_wood)
    sh_r.rotation_euler = (0, 0, math.radians(-50))
    create_box("Mod_Shutters_Hinge_TL", (0.32, 0.02, 0.04), (xs - 0.45, base_y - 0.03, 0.80), col, mat_iron, bevel=False)
    create_box("Mod_Shutters_Hinge_BL", (0.32, 0.02, 0.04), (xs - 0.45, base_y - 0.03, 0.20), col, mat_iron, bevel=False)
    create_box("Mod_Shutters_Hinge_TR", (0.32, 0.02, 0.04), (xs + 0.45, base_y - 0.03, 0.80), col, mat_iron, bevel=False)
    create_box("Mod_Shutters_Hinge_BR", (0.32, 0.02, 0.04), (xs + 0.45, base_y - 0.03, 0.20), col, mat_iron, bevel=False)

# ==============================================================================
# 6. ARCHES & STAIRS
# ==============================================================================
def build_arches_and_stairs(base_x=0.0, base_y=0.0):
    col = "02_ARCHITECTURE_MODULAR/06_Arches_Stairs"
    mat_ashlar = "M_Stone_AshlarGrey"
    mat_sandstone = "M_Stone_Sandstone"
    mat_wood = "M_Wood_AgedOak"

    # 1. Roman Semicircular Stone Arch (2.0m Span, 2.5m Total Height)
    xa = base_x
    create_box("Mod_Arch_Roman_Pillar_L", (0.45, 0.50, 1.50), (xa - 1.20, base_y, 0.75), col, mat_ashlar)
    create_box("Mod_Arch_Roman_Pillar_R", (0.45, 0.50, 1.50), (xa + 1.20, base_y, 0.75), col, mat_ashlar)
    create_box("Mod_Arch_Roman_Impost_L", (0.55, 0.58, 0.14), (xa - 1.20, base_y, 1.55), col, mat_sandstone)
    create_box("Mod_Arch_Roman_Impost_R", (0.55, 0.58, 0.14), (xa + 1.20, base_y, 1.55), col, mat_sandstone)

    # Voussoir Arch Ring
    num_voussoirs = 7
    for vi in range(num_voussoirs):
        angle = math.pi - (vi + 0.5) * (math.pi / num_voussoirs)
        vx = xa + 1.15 * math.cos(angle)
        vz = 1.60 + 0.90 * math.sin(angle)
        v_obj = create_box(f"Mod_Arch_Roman_Voussoir_{vi}", (0.38, 0.50, 0.28), (vx, base_y, vz), col, mat_ashlar, bevel_width=0.02)
        v_obj.rotation_euler = (0, -(angle - math.pi/2), 0)

    # 2. Gothic Pointed Arch (2.0m Span)
    xg = base_x + 4.5
    create_box("Mod_Arch_Gothic_Pillar_L", (0.45, 0.50, 1.60), (xg - 1.20, base_y, 0.80), col, mat_sandstone)
    create_box("Mod_Arch_Gothic_Pillar_R", (0.45, 0.50, 1.60), (xg + 1.20, base_y, 0.80), col, mat_sandstone)
    # Left Pointed Haunch
    haunch_l = create_box("Mod_Arch_Gothic_Haunch_L", (1.45, 0.50, 0.32), (xg - 0.55, base_y, 2.25), col, mat_sandstone, bevel_width=0.02)
    haunch_l.rotation_euler = (0, math.radians(-38.0), 0)
    haunch_r = create_box("Mod_Arch_Gothic_Haunch_R", (1.45, 0.50, 0.32), (xg + 0.55, base_y, 2.25), col, mat_sandstone, bevel_width=0.02)
    haunch_r.rotation_euler = (0, math.radians(38.0), 0)
    create_box("Mod_Arch_Gothic_Keystone", (0.32, 0.54, 0.40), (xg, base_y, 2.68), col, mat_sandstone)

    # 3. Straight Stone Steps (4 Tiers, Width: 2.0m)
    xs = base_x + 9.0
    for st in range(4):
        step_z = 0.14 + st * 0.25
        step_y = base_y - 0.40 + st * 0.32
        create_box(f"Mod_Stairs_Stone_Step_{st}", (2.0, 0.38, 0.26), (xs, step_y, step_z), col, mat_ashlar, bevel_width=0.025)

    # 4. Straight Flight Open-Tread Timber Staircase
    xt = base_x + 13.0
    for st in range(8):
        step_z = 0.10 + st * 0.25
        step_y = base_y - 0.80 + st * 0.24
        create_box(f"Mod_Stairs_Timber_Tread_{st}", (1.00, 0.26, 0.06), (xt, step_y, step_z), col, mat_wood)
    # Stringer carriage & handrail
    rail = create_box("Mod_Stairs_Timber_Rail", (0.08, 2.30, 0.10), (xt - 0.52, base_y, 1.20), col, mat_wood)
    rail.rotation_euler = (math.radians(-44.0), 0, 0)

# ==============================================================================
# 7. MODULAR CHIMNEYS
# ==============================================================================
def build_chimneys(base_x=0.0, base_y=0.0):
    col = "02_ARCHITECTURE_MODULAR/07_Chimneys"
    mat_stone = "M_Stone_Rubble"
    mat_ashlar = "M_Stone_AshlarGrey"
    mat_clay = "M_Clay_Terracotta"
    mat_wood = "M_Wood_AgedOak"

    # 1. Base Chimney Hearth Section (Width: 2.0m, Depth: 1.2m, Height: 2.5m)
    # Includes fireplace hearth opening
    xc1 = base_x
    create_box("Mod_Chimney_Base_Left", (0.45, 1.20, 2.50), (xc1 - 0.775, base_y, 1.25), col, mat_stone)
    create_box("Mod_Chimney_Base_Right", (0.45, 1.20, 2.50), (xc1 + 0.775, base_y, 1.25), col, mat_stone)
    create_box("Mod_Chimney_Base_Back", (1.10, 0.35, 2.50), (xc1, base_y + 0.425, 1.25), col, mat_stone)
    create_box("Mod_Chimney_Base_Lintel", (1.30, 1.20, 0.45), (xc1, base_y, 2.275), col, mat_ashlar, bevel_width=0.03)
    create_box("Mod_Chimney_Base_OakMantel", (1.45, 0.25, 0.20), (xc1, base_y - 0.62, 2.05), col, mat_wood)

    # 2. Stackable 2m Chimney Shaft with Weathering Drip Ledge
    xc2 = base_x + 3.5
    create_box("Mod_Chimney_Shaft_Body", (1.10, 0.90, 2.00), (xc2, base_y, 1.00), col, mat_stone, bevel_width=0.03)
    create_box("Mod_Chimney_Shaft_DripLedge", (1.20, 1.00, 0.16), (xc2, base_y, 1.95), col, mat_ashlar, bevel_width=0.025)

    # 3. Chimney Corbeled Crown with Dual Flared Terracotta Pots
    xc3 = base_x + 6.5
    create_box("Mod_Chimney_Crown_Cap", (1.18, 1.05, 0.22), (xc3, base_y, 0.11), col, mat_ashlar, bevel_width=0.03)
    # Dual Terracotta Pots
    for i, pot_y in enumerate([-0.25, 0.25]):
        create_box(f"Mod_Chimney_Pot_{i}", (0.34, 0.34, 0.65), (xc3, base_y + pot_y, 0.54), col, mat_clay, bevel_width=0.015)
        create_box(f"Mod_Chimney_PotRim_{i}", (0.40, 0.40, 0.08), (xc3, base_y + pot_y, 0.85), col, mat_clay, bevel_width=0.01)

# ==============================================================================
# MASTER GENERATION FUNCTION
# ==============================================================================
def build_all_modular_architecture():
    print("==================================================")
    print("BUILDING MODULAR MEDIEVAL ARCHITECTURE KIT")
    print("==================================================")

    # Ensure collections hierarchy
    root_col = get_or_create_collection("02_ARCHITECTURE_MODULAR")
    sub_cols = [
        "01_Foundations",
        "02_Walls_Stone",
        "03_Walls_Timber",
        "04_Gables_Roofs",
        "05_Doors_Windows",
        "06_Arches_Stairs",
        "07_Chimneys"
    ]
    for sc in sub_cols:
        full_name = f"02_ARCHITECTURE_MODULAR/{sc}"
        get_or_create_collection(full_name, root_col)
        clear_collection(full_name)

    # Row 1: Foundations (Y = 12.0)
    print("[1/7] Building Stone Foundations...")
    build_foundations(base_x=-4.0, base_y=12.0)

    # Row 2: Ground Floor Stone Walls (Y = 8.0)
    print("[2/7] Building Ground Floor Stone Walls...")
    build_stone_walls(base_x=-7.0, base_y=8.0)

    # Row 3: Timber & Plaster Upper Walls (Y = 4.0)
    print("[3/7] Building Timber & Plaster Upper Walls & Jetty...")
    build_timber_walls(base_x=-7.0, base_y=4.0)

    # Row 4: Gables & Roof Panels (Y = -0.5)
    print("[4/7] Building Gables, Bargeboards, Roof Panels & Dormer...")
    build_gables_and_roofs(base_x=-10.0, base_y=-0.5)

    # Row 5: Doors, Windows & Shutters (Y = -5.0)
    print("[5/7] Building Door Frames, Windows & Shutters...")
    build_doors_and_windows(base_x=-4.0, base_y=-5.0)

    # Row 6: Arches & Stairs (Y = -8.5)
    print("[6/7] Building Stone & Gothic Arches, Stone & Timber Stairs...")
    build_arches_and_stairs(base_x=-6.5, base_y=-8.5)

    # Row 7: Chimneys (Y = -12.5)
    print("[7/7] Building Modular Stackable Chimney Components...")
    build_chimneys(base_x=-3.0, base_y=-12.5)

    print("==================================================")
    print("MODULAR ARCHITECTURE KIT SUCCESSFULLY CREATED!")
    print("==================================================")

if __name__ == '__main__':
    build_all_modular_architecture()
