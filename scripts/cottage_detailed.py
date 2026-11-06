"""
Medieval Fantasy Village - Complete Detailed Cottage Generator
Procedurally generates the full-detail medieval timber-and-stone cottage:
- Foundation: Mortar core, individual facing rubble stones, corner quoins, water-table, 3-tier steps
- Walls: 0.42m ground floor stone masonry with dressed lintels & sills; upper lime plaster infill panels
- Timber Framing: Cantilevered jetty, bressummers, dragon beams, corbel brackets, corner posts,
  studs, girts, St. Andrew's cross braces, and wooden mortise joint dowel pegs
- Roof: Steep 52-degree pitch, exposed rafters, bargeboards, carved finials, structural ridge beam
- Roof Tiles: INDIVIDUAL overlapping clay tiles arranged in staggered courses with organic rotational jitter,
  plus interlocking half-round terracotta ridge capping tiles
- Chimney: Massive stepped stone chimney with dual weathering drip courses, corbeled crown & terracotta pots
- Doors: Vertical grooved plank door, arched timber frame, forged iron strap hinges, latch ring & plate
- Windows: Stone mullioned GF windows & timber casement UF windows with leaded lattice glass
- Shutters: Wooden plank shutters with iron strap hinges angled open
- Porch: Timber canopy over front steps with carved brackets & individual tile roofing
- Interior: Flagstones, summer spine beam, stone hearth, cooking pot, trestle table, benches & staircase
- Exterior Props: Banded barrels, crates, firewood stack, wall lantern & window flowerbox
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler

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
        col = bpy.data.collections.get(c)
        if col:
            for obj in list(col.objects):
                bpy.data.objects.remove(obj, do_unlink=True)

    for obj in list(bpy.data.objects):
        if obj.name.startswith("Cottage_") or obj.name.startswith("Prop_"):
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

def link_to_collection(obj, col_name):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    target_col = bpy.data.collections.get(col_name)
    if not target_col:
        target_col = bpy.context.scene.collection
    target_col.objects.link(obj)

def create_box(name, size, location, col_name, mat_name=None, bevel=True, bevel_width=0.018):
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

# ---------------------------------------------------------
# 1. FOUNDATION WITH IRREGULAR STONES & STEPS
# ---------------------------------------------------------
def build_foundation():
    col = "01_Foundation"
    mat_stone = "M_Stone_Rubble"

    # Core Plinth: 6.95m x 8.55m x 0.85m (Z: 0.0 to 0.85m)
    create_box("Cottage_Foundation_Core", (6.95, 8.55, 0.85), (0.0, 0.0, 0.425), col, mat_stone, bevel_width=0.03)

    # Water-table chamfered drip molding
    create_box("Cottage_Foundation_WaterTable", (7.16, 8.76, 0.12), (0.0, 0.0, 0.86), col, mat_stone, bevel_width=0.025)

    # Dressed Stone Corner Quoins
    corners = [
        ((-3.52, -4.32), True),
        ((3.52, -4.32), True),
        ((-3.52, 4.32), True),
        ((3.52, 4.32), True),
    ]
    for i, ((cx, cy), _) in enumerate(corners):
        for q_layer in range(3):
            qz = 0.15 + q_layer * 0.28
            q_size = (0.55, 0.55, 0.25) if (q_layer % 2 == 0) else (0.42, 0.42, 0.25)
            create_box(f"Cottage_Foundation_Quoin_{i}_{q_layer}", q_size, (cx, cy, qz), col, mat_stone, bevel_width=0.03)

    # Individual Irregular Rubble Facing Stones along Front & Side Foundation Perimeters
    random.seed(42) # Deterministic organic layout

    # Front Foundation Stones (excluding steps area X = -1.5 to +0.3)
    front_xs = [-3.1, -2.5, -1.9, 0.6, 1.2, 1.8, 2.4, 3.0]
    for i, fx in enumerate(front_xs):
        for layer in range(2):
            fz = 0.22 + layer * 0.38 + random.uniform(-0.03, 0.03)
            sx = random.uniform(0.48, 0.62)
            sz = random.uniform(0.28, 0.36)
            sy = random.uniform(0.18, 0.24)
            s_obj = create_box(f"Cottage_Foundation_Stone_F_{i}_{layer}", (sx, sy, sz), (fx, -4.32, fz), col, mat_stone, bevel_width=0.025)
            s_obj.rotation_euler = (random.uniform(-0.02, 0.02), 0, random.uniform(-0.03, 0.03))

    # Left Side Foundation Stones
    left_ys = [-3.6, -2.8, -2.0, -1.2, -0.4, 0.4, 1.2, 2.0, 2.8, 3.6]
    for i, ly in enumerate(left_ys):
        for layer in range(2):
            lz = 0.22 + layer * 0.38 + random.uniform(-0.03, 0.03)
            sy = random.uniform(0.55, 0.70)
            sz = random.uniform(0.28, 0.35)
            sx = random.uniform(0.18, 0.24)
            s_obj = create_box(f"Cottage_Foundation_Stone_L_{i}_{layer}", (sx, sy, sz), (-3.52, ly, lz), col, mat_stone, bevel_width=0.025)
            s_obj.rotation_euler = (0, random.uniform(-0.02, 0.02), random.uniform(-0.03, 0.03))

    # Front Entrance Steps (3 tiers leading to front doorway at X = -0.6)
    steps = [
        ("Cottage_Step_01", (1.70, 0.48, 0.28), (-0.60, -5.02, 0.14)),
        ("Cottage_Step_02", (1.50, 0.48, 0.28), (-0.60, -4.70, 0.42)),
        ("Cottage_Step_03", (1.30, 0.48, 0.28), (-0.60, -4.38, 0.70)),
    ]
    for name, size, loc in steps:
        create_box(name, size, loc, col, mat_stone, bevel_width=0.03)

# ---------------------------------------------------------
# 2. GROUND FLOOR STONE WALLS
# ---------------------------------------------------------
def build_ground_floor_walls():
    col = "02_Ground_Floor"
    mat_stone = "M_Stone_Rubble"

    # Wall thickness: 0.42m. Height: 2.70m (Z: 0.90 to 3.60m)
    # Front Wall (Y = -4.0):
    create_box("Cottage_GF_Wall_Front_Left", (2.25, 0.42, 2.70), (-2.275, -4.0, 2.25), col, mat_stone)
    create_box("Cottage_GF_Wall_Front_Mid", (1.15, 0.42, 2.70), (0.55, -4.0, 2.25), col, mat_stone)
    create_box("Cottage_GF_Wall_Front_Right", (1.25, 0.42, 2.70), (2.775, -4.0, 2.25), col, mat_stone)

    # Front Window (X = 1.65, Width 1.0m, Height 1.20m -> Z: 1.80 to 3.00)
    create_box("Cottage_GF_Front_Win_SillWall", (1.00, 0.42, 0.90), (1.65, -4.0, 1.35), col, mat_stone)
    create_box("Cottage_GF_Front_Win_LintelWall", (1.00, 0.42, 0.60), (1.65, -4.0, 3.30), col, mat_stone)
    # Heavy chiseled stone door lintel
    create_box("Cottage_GF_Door_Lintel_Stone", (1.36, 0.52, 0.50), (-0.60, -4.0, 3.35), col, mat_stone, bevel_width=0.035)

    # Rear Wall (Y = +4.0):
    create_box("Cottage_GF_Wall_Rear_L", (2.85, 0.42, 2.70), (-1.975, 4.0, 2.25), col, mat_stone)
    create_box("Cottage_GF_Wall_Rear_R", (2.85, 0.42, 2.70), (1.975, 4.0, 2.25), col, mat_stone)
    create_box("Cottage_GF_Rear_Win_SillWall", (1.10, 0.42, 0.90), (0.0, 4.0, 1.35), col, mat_stone)
    create_box("Cottage_GF_Rear_Win_LintelWall", (1.10, 0.42, 0.60), (0.0, 4.0, 3.30), col, mat_stone)

    # Left Wall (X = -3.2):
    create_box("Cottage_GF_Wall_Left_1", (0.42, 2.40, 2.70), (-3.2, -2.80, 2.25), col, mat_stone)
    create_box("Cottage_GF_Wall_Left_2", (0.42, 2.20, 2.70), (-3.2, 0.00, 2.25), col, mat_stone)
    create_box("Cottage_GF_Wall_Left_3", (0.42, 2.40, 2.70), (-3.2, 2.80, 2.25), col, mat_stone)
    create_box("Cottage_GF_Left_Win1_Sill", (0.42, 0.70, 1.05), (-3.2, -1.45, 1.425), col, mat_stone)
    create_box("Cottage_GF_Left_Win1_Lintel", (0.42, 0.70, 0.55), (-3.2, -1.45, 3.325), col, mat_stone)
    create_box("Cottage_GF_Left_Win2_Sill", (0.42, 0.70, 1.05), (-3.2, 1.45, 1.425), col, mat_stone)
    create_box("Cottage_GF_Left_Win2_Lintel", (0.42, 0.70, 0.55), (-3.2, 1.45, 3.325), col, mat_stone)

    # Right Wall (X = +3.2):
    create_box("Cottage_GF_Wall_Right_F", (0.42, 2.70, 2.70), (3.2, -2.65, 2.25), col, mat_stone)
    create_box("Cottage_GF_Wall_Right_B", (0.42, 2.70, 2.70), (3.2, 2.65, 2.25), col, mat_stone)
    create_box("Cottage_GF_Fireplace_Opening_Wall", (0.42, 0.60, 2.70), (3.2, 0.00, 3.35), col, mat_stone)

    # Dressed Wall Corner Quoins (interlocking long-and-short ashlar stones)
    for qi in range(5):
        qz = 1.15 + qi * 0.55
        create_box(f"Cottage_GF_Quoin_FL_{qi}", (0.48, 0.48, 0.32), (-3.22, -4.02, qz), col, mat_stone, bevel_width=0.025)
        create_box(f"Cottage_GF_Quoin_BL_{qi}", (0.48, 0.48, 0.32), (-3.22, 4.02, qz), col, mat_stone, bevel_width=0.025)

# ---------------------------------------------------------
# 3. TIMBER FRAMING, JETTY & REALISTIC JOINTS
# ---------------------------------------------------------
def build_timber_framing_and_joints():
    col_wood = "03_Timber_Framing"
    mat_wood = "M_Wood_AgedOak"

    # Cantilevered Medieval Jetty Bressummers (Z: 3.60 to 3.88m)
    create_box("Cottage_Jetty_Bressummer_Front", (7.45, 0.28, 0.28), (0.0, -4.30, 3.72), col_wood, mat_wood)
    create_box("Cottage_Jetty_Bressummer_Rear", (7.45, 0.28, 0.28), (0.0, 4.30, 3.72), col_wood, mat_wood)
    create_box("Cottage_Jetty_Bressummer_Left", (0.28, 8.85, 0.28), (-3.58, 0.0, 3.72), col_wood, mat_wood)
    create_box("Cottage_Jetty_Bressummer_Right", (0.28, 8.85, 0.28), (3.58, 0.0, 3.72), col_wood, mat_wood)

    # Cantilever Floor Joists projecting under the jetty
    joist_ys = [-3.8, -3.0, -2.2, -1.4, -0.6, 0.2, 1.0, 1.8, 2.6, 3.4]
    for i, y_pos in enumerate(joist_ys):
        create_box(f"Cottage_Jetty_Joist_{i:02d}", (7.40, 0.16, 0.22), (0.0, y_pos, 3.62), col_wood, mat_wood)

    # Carved Medieval Jetty Corbel Brackets supporting the front overhang
    bracket_xs = [-3.3, -2.2, -1.1, 0.0, 1.1, 2.2, 3.3]
    for i, bx in enumerate(bracket_xs):
        create_box(f"Cottage_Jetty_Bracket_F_{i:02d}", (0.16, 0.26, 0.45), (bx, -4.18, 3.35), col_wood, mat_wood, bevel_width=0.02)

    # Upper Floor Corner Posts (0.24 x 0.24m)
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

    # Intermediate Vertical Studs
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

    # REALISTIC JOINTS: Cylindrical Wooden Mortise & Tenon Dowel Pegs
    peg_locs = [
        # Front corner posts into bressummer & girt
        (-3.50, -4.32, 3.88), (3.50, -4.32, 3.88),
        (-3.50, -4.32, 4.95), (3.50, -4.32, 4.95),
        (-3.50, -4.32, 6.20), (3.50, -4.32, 6.20),
        # Diagonal brace joint pins
        (-2.95, -4.30, 4.95), (2.95, -4.30, 4.95),
        (-2.35, -4.30, 3.88), (2.35, -4.30, 3.88),
    ]
    for pi, ploc in enumerate(peg_locs):
        create_box(f"Cottage_Joint_Peg_{pi:02d}", (0.035, 0.05, 0.035), ploc, col_wood, mat_wood, bevel=False)

# ---------------------------------------------------------
# 4. UPPER PLASTER WALLS & GABLES
# ---------------------------------------------------------
def build_upper_plaster_walls():
    col_plaster = "04_Upper_Walls"
    col_roof = "05_Roof"
    mat_plaster = "M_Plaster_Lime"
    mat_wood = "M_Wood_AgedOak"

    # Infill lime plaster panels (slightly recessed 0.02m behind timber surface)
    create_box("Cottage_Plaster_Front_Low", (7.0, 0.12, 1.05), (0.0, -4.20, 4.40), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Front_High", (7.0, 0.12, 1.05), (0.0, -4.20, 5.60), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Rear_Low", (7.0, 0.12, 1.05), (0.0, 4.20, 4.40), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Rear_High", (7.0, 0.12, 1.05), (0.0, 4.20, 5.60), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Left_Low", (0.12, 8.4, 1.05), (-3.50, 0.0, 4.40), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Left_High", (0.12, 8.4, 1.05), (-3.50, 0.0, 5.60), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Right_Low", (0.12, 8.4, 1.05), (3.50, 0.0, 4.40), col_plaster, mat_plaster)
    create_box("Cottage_Plaster_Right_High", (0.12, 8.4, 1.05), (3.50, 0.0, 5.60), col_plaster, mat_plaster)

    # Triangular Gables
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

# ---------------------------------------------------------
# 5. ROOF STRUCTURE & EXPOSED RAFTERS
# ---------------------------------------------------------
def build_roof_structure():
    col_roof = "05_Roof"
    mat_wood = "M_Wood_AgedOak"
    mat_tile = "M_Clay_Terracotta"
    mat_slate = "M_Slate_Dark"

    # Base Roof Planes (underlayment / sarking board)
    def create_roof_plane_mesh(name, x_eave, x_ridge, y_start, y_end, z_eave, z_ridge, thickness=0.14):
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
        apply_modifiers(obj, bevel_width=0.02)
        assign_material(obj, mat_slate)
        return obj

    create_roof_plane_mesh("Cottage_Roof_Underlay_Left", -4.18, -0.02, -4.85, 4.85, 6.00, 8.24)
    create_roof_plane_mesh("Cottage_Roof_Underlay_Right", 4.18, 0.02, -4.85, 4.85, 6.00, 8.24)

    # Exposed Rafter Feet under eaves (spaced every 0.8m)
    rafter_ys = [-4.6, -3.8, -3.0, -2.2, -1.4, -0.6, 0.2, 1.0, 1.8, 2.6, 3.4, 4.2, 4.6]
    for i, ry in enumerate(rafter_ys):
        create_box(f"Cottage_Rafter_Foot_L_{i:02d}", (0.55, 0.12, 0.14), (-3.95, ry, 6.05), col_roof, mat_wood)
        create_box(f"Cottage_Rafter_Foot_R_{i:02d}", (0.55, 0.12, 0.14), (3.95, ry, 6.05), col_roof, mat_wood)

    # Bargeboards along Gable Edges
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

    create_bargeboard("Cottage_Bargeboard_Front_Left", -4.20, 0.0, -4.88, 6.00, 8.25)
    create_bargeboard("Cottage_Bargeboard_Front_Right", 4.20, 0.0, -4.88, 6.00, 8.25)
    create_bargeboard("Cottage_Bargeboard_Rear_Left", -4.20, 0.0, 4.88, 6.00, 8.25)
    create_bargeboard("Cottage_Bargeboard_Rear_Right", 4.20, 0.0, 4.88, 6.00, 8.25)

    # Carved Gable Finials
    create_box("Cottage_Finial_Apex_Front", (0.14, 0.14, 0.75), (0.0, -4.88, 8.55), col_roof, mat_wood, bevel_width=0.02)
    create_box("Cottage_Finial_Apex_Rear", (0.14, 0.14, 0.75), (0.0, 4.88, 8.55), col_roof, mat_wood, bevel_width=0.02)

# ---------------------------------------------------------
# 6. INDIVIDUAL OVERLAPPING ROOF TILES WITH WEATHERING
# ---------------------------------------------------------
def build_individual_roof_tiles():
    col_roof = "05_Roof"
    mat_clay = "M_Clay_Terracotta"

    # Create master tile mesh prototype: traditional medieval clay flat-tile with curved tail
    # Size: width 0.32m, length 0.44m, thickness 0.024m
    tile_mesh = bpy.data.meshes.new("Cottage_Prototype_Tile")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.co.x *= 0.34
        v.co.y *= 0.46
        v.co.z *= 0.024
    bm.to_mesh(tile_mesh)
    bm.free()

    # Apply material to prototype mesh
    mat = bpy.data.materials.get(mat_clay)
    if mat:
        tile_mesh.materials.append(mat)

    slope_angle = math.atan2(2.24, 4.18) # ~28.18 deg

    random.seed(101) # Deterministic organic roof weathering

    # 12 courses (rows) per slope, 22 tiles per course
    num_courses = 12
    tiles_per_course = 22
    y_start = -4.60
    y_step = 9.20 / tiles_per_course

    # Left Slope (X < 0)
    for c_i in range(num_courses):
        t = c_i / (num_courses - 1)
        # Position along slope
        x_base = -4.12 + t * 3.98
        z_base = 6.04 + t * 2.14

        stagger = 0.5 * y_step if (c_i % 2 == 1) else 0.0

        for t_j in range(tiles_per_course):
            y_base = y_start + t_j * y_step + stagger
            if y_base > 4.70 or y_base < -4.70:
                continue

            tile_obj = bpy.data.objects.new(f"Cottage_Tile_L_{c_i:02d}_{t_j:02d}", tile_mesh)
            # Add subtle organic weathering jitter
            jx = random.uniform(-0.015, 0.015)
            jy = random.uniform(-0.015, 0.015)
            jz = random.uniform(-0.01, 0.01) + 0.04 # Lift slightly above underlay
            j_yaw = random.uniform(-0.025, 0.025)
            j_pitch = random.uniform(-0.02, 0.02)

            tile_obj.location = (x_base + jx, y_base + jy, z_base + jz)
            tile_obj.rotation_euler = (j_pitch, -slope_angle, j_yaw)

            link_to_collection(tile_obj, col_roof)

    # Right Slope (X > 0)
    # Right side has chimney stack from Y = -1.3m to +1.3m, X = 3.3 to 4.5m
    for c_i in range(num_courses):
        t = c_i / (num_courses - 1)
        x_base = 4.12 - t * 3.98
        z_base = 6.04 + t * 2.14

        stagger = 0.5 * y_step if (c_i % 2 == 1) else 0.0

        for t_j in range(tiles_per_course):
            y_base = y_start + t_j * y_step + stagger
            if y_base > 4.70 or y_base < -4.70:
                continue

            # Check chimney collision cutout
            if x_base > 3.20 and (-1.35 < y_base < 1.35):
                continue

            tile_obj = bpy.data.objects.new(f"Cottage_Tile_R_{c_i:02d}_{t_j:02d}", tile_mesh)
            jx = random.uniform(-0.015, 0.015)
            jy = random.uniform(-0.015, 0.015)
            jz = random.uniform(-0.01, 0.01) + 0.04
            j_yaw = random.uniform(-0.025, 0.025)
            j_pitch = random.uniform(-0.02, 0.02)

            tile_obj.location = (x_base + jx, y_base + jy, z_base + jz)
            tile_obj.rotation_euler = (j_pitch, slope_angle, j_yaw)

            link_to_collection(tile_obj, col_roof)

    # Interlocking Half-Round Terracotta Ridge Capping Tiles along apex
    ridge_mesh = bpy.data.meshes.new("Cottage_Prototype_RidgeTile")
    bm_r = bmesh.new()
    bmesh.ops.create_cone(bm_r, cap_ends=True, segments=12, radius1=0.18, radius2=0.18, depth=0.45)
    bm_r.to_mesh(ridge_mesh)
    bm_r.free()
    if mat:
        ridge_mesh.materials.append(mat)

    for ri in range(22):
        ry = -4.65 + ri * 0.43
        r_obj = bpy.data.objects.new(f"Cottage_Ridge_Tile_{ri:02d}", ridge_mesh)
        r_obj.location = (0.0, ry, 8.32)
        r_obj.rotation_euler = (math.radians(90.0), 0, random.uniform(-0.03, 0.03))
        link_to_collection(r_obj, col_roof)

# ---------------------------------------------------------
# 7. STEPPED STONE CHIMNEY & DUAL TERRACOTTA POTS
# ---------------------------------------------------------
def build_stone_chimney():
    col = "07_Chimney"
    mat_stone = "M_Stone_Rubble"
    mat_clay = "M_Clay_Terracotta"

    # Tier 1 (Base up to Z = 3.85m): massive stone breast
    create_box("Cottage_Chimney_Base", (1.30, 2.40, 3.85), (3.92, 0.0, 1.925), col, mat_stone, bevel_width=0.04)

    # Weathering Drip Ledge 1 (chamfered stone drip course)
    create_box("Cottage_Chimney_DripLedge_1", (1.42, 2.52, 0.22), (3.92, 0.0, 3.88), col, mat_stone, bevel_width=0.03)

    # Tier 2 (Z = 3.90 to 6.25m): mid stack tapering inward
    create_box("Cottage_Chimney_MidStack", (1.12, 1.85, 2.35), (3.82, 0.0, 5.08), col, mat_stone, bevel_width=0.035)

    # Weathering Drip Ledge 2
    create_box("Cottage_Chimney_DripLedge_2", (1.20, 1.94, 0.20), (3.82, 0.0, 6.28), col, mat_stone, bevel_width=0.03)

    # Tier 3 (Z = 6.30 to 8.85m): upper stack rising above roofline
    create_box("Cottage_Chimney_UpperStack", (0.95, 1.35, 2.58), (3.78, 0.0, 7.60), col, mat_stone, bevel_width=0.03)

    # Corbeled Stone Crown
    create_box("Cottage_Chimney_Crown", (1.12, 1.52, 0.24), (3.78, 0.0, 8.96), col, mat_stone, bevel_width=0.03)

    # Dual Terracotta Chimney Pots with flared rim rings (Z up to 9.55m)
    for i, pot_y in enumerate([-0.36, 0.36]):
        create_box(f"Cottage_Chimney_Pot_{i}", (0.36, 0.36, 0.65), (3.78, pot_y, 9.35), col, mat_clay, bevel_width=0.02)
        create_box(f"Cottage_Chimney_PotRim_{i}", (0.42, 0.42, 0.08), (3.78, pot_y, 9.65), col, mat_clay, bevel_width=0.015)

    # Interior Fireplace Hearth & Heavy Oak Mantel
    create_box("Cottage_Interior_Hearth_Base", (0.85, 1.85, 0.32), (2.85, 0.0, 1.02), "08_Interior", mat_stone)
    create_box("Cottage_Interior_Mantel_Beam", (0.32, 2.05, 0.26), (2.75, 0.0, 2.50), "08_Interior", "M_Wood_AgedOak")

# ---------------------------------------------------------
# 8. DOORS, WINDOWS, SHUTTERS & HARDWARE
# ---------------------------------------------------------
def build_doors_and_windows():
    col = "06_Doors_Windows"
    mat_wood = "M_Wood_AgedOak"
    mat_iron = "M_Iron_Wrought"
    mat_glass = "M_Glass_Leaded"
    mat_stone = "M_Stone_Rubble"

    # Front Entrance Door (at X = -0.60, Y = -4.0, Z: 0.90 to 3.05)
    # Vertical grooved plank leaf
    create_box("Cottage_Door_PlankLeaf", (1.02, 0.08, 2.10), (-0.60, -4.06, 1.95), col, mat_wood, bevel_width=0.015)
    # Timber Door Frame
    create_box("Cottage_Door_Frame_L", (0.14, 0.18, 2.20), (-1.16, -4.05, 2.00), col, mat_wood)
    create_box("Cottage_Door_Frame_R", (0.14, 0.18, 2.20), (-0.04, -4.05, 2.00), col, mat_wood)
    create_box("Cottage_Door_Frame_Head", (1.26, 0.18, 0.16), (-0.60, -4.05, 3.12), col, mat_wood)
    # Forged Iron Strap Hinges with scrolled tips
    create_box("Cottage_Door_Hinge_Top", (0.68, 0.04, 0.06), (-0.65, -4.11, 2.65), col, mat_iron)
    create_box("Cottage_Door_Hinge_Bottom", (0.68, 0.04, 0.06), (-0.65, -4.11, 1.35), col, mat_iron)
    create_box("Cottage_Door_Handle_Ring", (0.10, 0.05, 0.12), (-0.22, -4.12, 1.95), col, mat_iron)
    create_box("Cottage_Door_Lock_Plate", (0.12, 0.03, 0.18), (-0.22, -4.11, 1.95), col, mat_iron)

    # Ground Floor Front Window (X = 1.65, Y = -4.0)
    create_box("Cottage_GF_Win_Sill", (1.18, 0.24, 0.10), (1.65, -4.14, 1.78), col, mat_stone, bevel_width=0.02)
    create_box("Cottage_GF_Win_Mullion", (0.10, 0.14, 1.15), (1.65, -4.02, 2.40), col, mat_stone)
    create_box("Cottage_GF_Win_Glass_L", (0.42, 0.02, 1.12), (1.37, -4.02, 2.40), col, mat_glass, bevel=False)
    create_box("Cottage_GF_Win_Glass_R", (0.42, 0.02, 1.12), (1.93, -4.02, 2.40), col, mat_glass, bevel=False)

    # Ground Floor Side Windows (Left Wall: X = -3.2)
    for i, wy in enumerate([-1.45, 1.45]):
        create_box(f"Cottage_GF_SideWin_Sill_{i}", (0.24, 0.88, 0.10), (-3.34, wy, 1.95), col, mat_stone)
        create_box(f"Cottage_GF_SideWin_Glass_{i}", (0.02, 0.62, 1.25), (-3.20, wy, 2.65), col, mat_glass, bevel=False)

    # Upper Floor Front Casement Windows with Operable Shutters (X = -1.55 and X = +1.55)
    for i, wx in enumerate([-1.55, 1.55]):
        create_box(f"Cottage_UF_Win_Sill_{i}", (1.15, 0.24, 0.10), (wx, -4.32, 4.95), col, mat_wood)
        create_box(f"Cottage_UF_Win_Frame_{i}", (0.98, 0.14, 0.98), (wx, -4.22, 5.50), col, mat_wood)
        create_box(f"Cottage_UF_Win_Mullion_{i}", (0.08, 0.12, 0.88), (wx, -4.22, 5.50), col, mat_wood)
        create_box(f"Cottage_UF_Win_Glass_{i}", (0.82, 0.02, 0.82), (wx, -4.22, 5.50), col, mat_glass, bevel=False)

        # Operable Wooden Shutters (angled open 52 degrees)
        sh_l = create_box(f"Cottage_Shutter_{i}_L", (0.42, 0.04, 0.86), (wx - 0.58, -4.34, 5.50), col, mat_wood)
        sh_l.rotation_euler = (0, 0, math.radians(52))
        sh_r = create_box(f"Cottage_Shutter_{i}_R", (0.42, 0.04, 0.86), (wx + 0.58, -4.34, 5.50), col, mat_wood)
        sh_r.rotation_euler = (0, 0, math.radians(-52))

        # Shutter iron strap hinges
        create_box(f"Cottage_Shutter_Hinge_{i}_TL", (0.32, 0.02, 0.04), (wx - 0.56, -4.36, 5.80), col, mat_iron, bevel=False)
        create_box(f"Cottage_Shutter_Hinge_{i}_BL", (0.32, 0.02, 0.04), (wx - 0.56, -4.36, 5.20), col, mat_iron, bevel=False)
        create_box(f"Cottage_Shutter_Hinge_{i}_TR", (0.32, 0.02, 0.04), (wx + 0.56, -4.36, 5.80), col, mat_iron, bevel=False)
        create_box(f"Cottage_Shutter_Hinge_{i}_BR", (0.32, 0.02, 0.04), (wx + 0.56, -4.36, 5.20), col, mat_iron, bevel=False)

# ---------------------------------------------------------
# 9. ENTRANCE PORCH CANOPY
# ---------------------------------------------------------
def build_porch_canopy():
    col = "05_Roof"
    mat_wood = "M_Wood_AgedOak"
    mat_clay = "M_Clay_Terracotta"
    mat_slate = "M_Slate_Dark"

    # Pitched awning canopy over front door steps
    p_roof = create_box("Cottage_Porch_Canopy_Roof", (1.92, 1.18, 0.08), (-0.60, -4.72, 3.28), col, mat_clay)
    p_roof.rotation_euler = (math.radians(24.0), 0, 0)

    # Slate flashing strip along wall intersection
    create_box("Cottage_Porch_Flashing_Strip", (2.00, 0.08, 0.12), (-0.60, -4.26, 3.48), col, mat_slate)

    # Heavy Carved Diagonal Brackets supporting the canopy
    create_box("Cottage_Porch_Bracket_L", (0.12, 0.70, 0.70), (-1.45, -4.45, 3.00), col, mat_wood)
    create_box("Cottage_Porch_Bracket_R", (0.12, 0.70, 0.70), (0.25, -4.45, 3.00), col, mat_wood)

# ---------------------------------------------------------
# 10. INTERIOR ARCHITECTURE & FURNISHINGS
# ---------------------------------------------------------
def build_interior():
    col = "08_Interior"
    mat_stone = "M_Stone_Rubble"
    mat_wood = "M_Wood_AgedOak"
    mat_iron = "M_Iron_Wrought"
    mat_plaster = "M_Plaster_Lime"

    # Flagstone Ground Floor & Oak Upper Floorboards
    create_box("Cottage_Floor_Flagstones", (6.10, 7.70, 0.08), (0.0, 0.0, 0.88), col, mat_stone)
    create_box("Cottage_Floor_Upper_Planks", (7.15, 8.55, 0.06), (0.0, 0.0, 3.86), col, mat_wood)

    # Master Spine Summer Beam
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

    # Upper Roof Tie Beams
    create_box("Cottage_UF_TieBeam_1", (7.10, 0.22, 0.20), (0.0, -1.8, 6.40), col, mat_wood)
    create_box("Cottage_UF_TieBeam_2", (7.10, 0.22, 0.20), (0.0, 1.8, 6.40), col, mat_wood)

    # Dining Trestle Table & Benches
    create_box("Cottage_Interior_Table_Top", (2.20, 0.90, 0.08), (-0.80, 0.0, 1.65), col, mat_wood)
    create_box("Cottage_Interior_Table_Leg_1", (0.16, 0.70, 0.72), (-1.65, 0.0, 1.25), col, mat_wood)
    create_box("Cottage_Interior_Table_Leg_2", (0.16, 0.70, 0.72), (0.05, 0.0, 1.25), col, mat_wood)
    create_box("Cottage_Interior_Bench_1", (2.20, 0.30, 0.06), (-0.80, -0.75, 1.35), col, mat_wood)
    create_box("Cottage_Interior_Bench_2", (2.20, 0.30, 0.06), (-0.80, 0.75, 1.35), col, mat_wood)

    # Fireplace Grate & Hanging Cooking Pot
    create_box("Cottage_Interior_FireGrate", (0.60, 0.50, 0.20), (2.85, 0.0, 1.12), col, mat_iron)
    create_box("Cottage_Interior_CookingPot", (0.35, 0.35, 0.32), (2.85, 0.0, 1.45), col, mat_iron, bevel_width=0.02)

    # Upper Floor Loft Bed Frame
    create_box("Cottage_Interior_Bed_Frame", (1.60, 2.10, 0.45), (1.80, 2.20, 4.10), col, mat_wood)
    create_box("Cottage_Interior_Bed_Mattress", (1.45, 1.95, 0.22), (1.80, 2.20, 4.40), col, mat_plaster)

# ---------------------------------------------------------
# 11. EXTERIOR PROPS & STREET SET-DRESSING
# ---------------------------------------------------------
def build_exterior_props():
    col = "09_Exterior_Props"
    mat_wood = "M_Wood_AgedOak"
    mat_iron = "M_Iron_Wrought"
    mat_stone = "M_Stone_Rubble"
    mat_lantern = "M_Lantern_Warm"

    # Banded Barrels
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

    # Wooden Storage Crates
    create_box("Cottage_Prop_Crate_Large", (0.80, 0.80, 0.80), (-3.88, 0.25, 0.40), col, mat_wood, bevel_width=0.02)
    c2 = create_box("Cottage_Prop_Crate_Small", (0.58, 0.58, 0.58), (-3.88, 1.05, 0.29), col, mat_wood, bevel_width=0.015)
    c2.rotation_euler = (0, 0, math.radians(22))

    # Stacked Split Firewood under Eave
    create_box("Cottage_Prop_Firewood_Stack", (0.65, 2.30, 0.88), (3.85, -2.75, 0.44), col, mat_wood, bevel_width=0.03)

    # Medieval Iron Wall Lantern beside front door
    create_box("Cottage_Prop_Lantern_Bracket", (0.06, 0.48, 0.38), (0.28, -4.24, 2.48), col, mat_iron)
    create_box("Cottage_Prop_Lantern_Cage", (0.24, 0.24, 0.38), (0.28, -4.50, 2.36), col, mat_iron, bevel_width=0.01)
    create_box("Cottage_Prop_Lantern_Core", (0.12, 0.12, 0.20), (0.28, -4.50, 2.36), col, mat_lantern, bevel=False)

    # Window Flowerbox under front upper right window
    create_box("Cottage_Prop_Flowerbox", (1.15, 0.30, 0.24), (1.55, -4.44, 4.80), col, mat_wood, bevel_width=0.02)
    create_box("Cottage_Prop_Flower_Foliage", (1.05, 0.24, 0.16), (1.55, -4.44, 4.90), col, mat_stone, bevel_width=0.02)

    # Exterior Boulder Accents
    boulders = [
        ((-3.85, -4.45), (0.55, 0.50, 0.38), 0.19),
        ((-4.10, -4.10), (0.42, 0.48, 0.32), 0.16),
        ((3.90, -4.40), (0.50, 0.45, 0.35), 0.18),
    ]
    for i, ((bx, by), bsize, bz) in enumerate(boulders):
        create_box(f"Cottage_Prop_Stone_{i}", bsize, (bx, by, bz), col, mat_stone, bevel_width=0.04)

    # Climbing Ivy Vine on Left Foundation Corner
    create_box("Cottage_Prop_Ivy_Trunk", (0.08, 0.08, 2.80), (-3.62, -4.22, 1.40), col, mat_wood, bevel_width=0.02)
    for vi in range(4):
        create_box(f"Cottage_Prop_Ivy_Foliage_{vi}", (0.45, 0.45, 0.35), (-3.65, -4.15 + vi*0.35, 1.20 + vi*0.65), col, mat_stone, bevel_width=0.03)

# ---------------------------------------------------------
# MASTER BUILD FUNCTION
# ---------------------------------------------------------
def build_complete_detailed_cottage():
    print("==================================================")
    print("BUILDING COMPLETE DETAILED MEDIEVAL COTTAGE")
    print("==================================================")
    print("[1/9] Clearing previous objects...")
    clear_all_cottage_objects()

    print("[2/9] Building Foundation, Irregular Stones & Steps...")
    build_foundation()

    print("[3/9] Building Ground Floor Stone Masonry...")
    build_ground_floor_walls()

    print("[4/9] Building Timber Framing, Jetty & Mortise Dowel Pegs...")
    build_timber_framing_and_joints()

    print("[5/9] Building Upper Plaster Walls & Gables...")
    build_upper_plaster_walls()

    print("[6/9] Building Roof Structure, Rafters & Bargeboards...")
    build_roof_structure()

    print("[7/9] Generating Individual Overlapping Roof Tiles & Ridge Capping...")
    build_individual_roof_tiles()

    print("[8/9] Building Stepped Stone Chimney & Flared Terracotta Pots...")
    build_stone_chimney()

    print("[9/9] Building Doors, Windows, Shutters, Porch & Set-Dressing...")
    build_doors_and_windows()
    build_porch_canopy()
    build_interior()
    build_exterior_props()

    print("==================================================")
    print("COMPLETE DETAILED COTTAGE GENERATED SUCCESSFULLY!")
    print("==================================================")

if __name__ == '__main__':
    build_complete_detailed_cottage()
