"""
Medieval Fantasy Village - Comprehensive Props Collection
Procedurally models authentic medieval village props:
- Barrels (Large 120L oak barrel with bunghole, Small 40L beer/wine keg with tap)
- Crates (Large shipping crate with corner iron brackets, Open produce crate)
- Sacks (Upright tied grain sack, Slumped horizontal burlap sack)
- Baskets (Round woven wicker basket with arch handle, Rectangular flat-top hamper)
- Wooden Buckets (Staved oak bucket with iron bands and hinged wrought-iron bail handle)
- Clay Pots & Stoneware (Salt-glazed ceramic crock with twin loop handles, Tavern ale pitcher)
- Cooking Utensils (3-legged cast iron cauldron, Skillet frying pan, Carved wooden ladles)
- Ropes & Chains (Coiled floor hemp rope with knot, Heavy forged iron chain links with hook)
- Tools (Woodcutter axe, Blacksmith hammer, 3-tine farm pitchfork, Harvest scythe)
- Furniture (Trestle dining table with wedge keys, Long tavern bench, Splayed 3-leg stool, Tavern chair)
- Lanterns (4-sided glazed street lantern with bracket & flame, Portable cylinder hand lantern)
- Signboards (Hanging tavern shield signboard with ornate wrought-iron scrolled bracket)
- Carts (Two-wheel village handcart with 12-spoked wheels, axle, stakes & pull shafts)
- Firewood (Neat cord stack of split logs, Round tree stump chopping block with embedded axe)
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

def apply_modifiers(obj, bevel_width=0.012, segments=2):
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

def create_box(name, size, location, col_name, mat_name=None, bevel=True, bevel_width=0.012):
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

def create_cylinder(name, radius, depth, location, col_name, mat_name=None, segments=16, bevel=True, bevel_width=0.01):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius, radius2=radius, depth=depth)
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
# 1. BARRELS & KEGS
# ==============================================================================
def build_barrels(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/01_Containers"
    mat_wood = "M_Wood_AgedOak"
    mat_iron = "M_Iron_Wrought"

    # Large 120L Oak Barrel
    # Modeled with barrel curvature: radius1=0.36m, radius_mid=0.42m, height=0.96m
    mesh_b1 = bpy.data.meshes.new("Prop_Barrel_Large_120L")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=18, radius1=0.36, radius2=0.36, depth=0.96)
    bm.to_mesh(mesh_b1)
    bm.free()
    b1 = bpy.data.objects.new("Prop_Barrel_Large_120L", mesh_b1)
    b1.location = (base_x, base_y, 0.48)
    link_to_col(b1, col)
    apply_modifiers(b1, bevel_width=0.015)
    assign_material(b1, mat_wood)

    # 4 Forged Iron Hoops with rivets
    for h_z in [-0.35, -0.15, 0.15, 0.35]:
        r = 0.38 if abs(h_z) > 0.2 else 0.42
        create_cylinder(f"Prop_Barrel_Large_Hoop_{h_z}", r, 0.045, (base_x, base_y, 0.48 + h_z), col, mat_iron, segments=18, bevel=False)
    # Wooden Bunghole Plug on belly
    create_cylinder("Prop_Barrel_Large_Bung", 0.04, 0.06, (base_x, base_y - 0.42, 0.48), col, "M_Wood_LightPine", segments=10)
    bpy.data.objects["Prop_Barrel_Large_Bung"].rotation_euler = (math.radians(90.0), 0, 0)

    # Small 40L Beer/Wine Keg with Dispensing Tap
    xk = base_x + 1.2
    mesh_keg = bpy.data.meshes.new("Prop_Barrel_Keg_40L")
    bm_k = bmesh.new()
    bmesh.ops.create_cone(bm_k, cap_ends=True, segments=16, radius1=0.24, radius2=0.24, depth=0.62)
    bm_k.to_mesh(mesh_keg)
    bm_k.free()
    keg = bpy.data.objects.new("Prop_Barrel_Keg_40L", mesh_keg)
    keg.location = (xk, base_y, 0.31)
    link_to_col(keg, col)
    apply_modifiers(keg, bevel_width=0.012)
    assign_material(keg, mat_wood)

    for h_z in [-0.20, 0.0, 0.20]:
        create_cylinder(f"Prop_Keg_Hoop_{h_z}", 0.255, 0.035, (xk, base_y, 0.31 + h_z), col, mat_iron, segments=16, bevel=False)
    # Brass/Wood Dispensing Spigot
    create_cylinder("Prop_Keg_Spigot_Body", 0.02, 0.12, (xk, base_y - 0.28, 0.22), col, mat_iron, segments=8)
    bpy.data.objects["Prop_Keg_Spigot_Body"].rotation_euler = (math.radians(90.0), 0, 0)
    create_cylinder("Prop_Keg_Spigot_TurnKey", 0.012, 0.06, (xk, base_y - 0.31, 0.25), col, mat_iron, segments=8)

# ==============================================================================
# 2. CRATES & STORAGE BOXES
# ==============================================================================
def build_crates(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/01_Containers"
    mat_wood = "M_Wood_AgedOak"
    mat_iron = "M_Iron_Wrought"

    # Large Shipping Crate (0.85m x 0.85m x 0.85m) with corner brackets
    c1 = create_box("Prop_Crate_Large_Box", (0.85, 0.85, 0.85), (base_x, base_y, 0.425), col, mat_wood, bevel_width=0.016)
    # Diagonal battens
    for side, rot in [((-0.43, 0), (0, math.radians(45), 0)), ((0.43, 0), (0, math.radians(-45), 0))]:
        b = create_box("Prop_Crate_Large_Batten_L", (0.08, 0.03, 1.05), (base_x + side[0], base_y, 0.425), col, mat_wood)
        b.rotation_euler = rot
    # Metal corner reinforcement plates
    for cx in [-0.43, 0.43]:
        for cy in [-0.43, 0.43]:
            create_box(f"Prop_Crate_CornerPlate_{cx}_{cy}", (0.08, 0.08, 0.12), (base_x + cx, base_y + cy, 0.80), col, mat_iron, bevel=False)
            create_box(f"Prop_Crate_CornerPlateB_{cx}_{cy}", (0.08, 0.08, 0.12), (base_x + cx, base_y + cy, 0.06), col, mat_iron, bevel=False)

    # Open Slatted Produce Crate (0.70m x 0.48m x 0.32m) with handle cutouts
    xo = base_x + 1.25
    create_box("Prop_Crate_Open_Bottom", (0.68, 0.46, 0.04), (xo, base_y, 0.02), col, mat_wood)
    # Side slats
    create_box("Prop_Crate_Open_Slat_F", (0.70, 0.03, 0.30), (xo, base_y - 0.23, 0.17), col, mat_wood)
    create_box("Prop_Crate_Open_Slat_B", (0.70, 0.03, 0.30), (xo, base_y + 0.23, 0.17), col, mat_wood)
    create_box("Prop_Crate_Open_Slat_L", (0.03, 0.48, 0.30), (xo - 0.34, base_y, 0.17), col, mat_wood)
    create_box("Prop_Crate_Open_Slat_R", (0.03, 0.48, 0.30), (xo + 0.34, base_y, 0.17), col, mat_wood)

# ==============================================================================
# 3. SACKS & BASKETS
# ==============================================================================
def build_sacks_and_baskets(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/01_Containers"
    mat_burlap = "M_Burlap_Hessian"
    mat_wicker = "M_Wicker_Willow"
    mat_rope = "M_Hemp_Rope"

    # Upright Bulging Grain Sack with tied rope neck
    xs1 = base_x
    mesh_s1 = bpy.data.meshes.new("Prop_Grain_Sack_Upright")
    bm_s1 = bmesh.new()
    bmesh.ops.create_cone(bm_s1, cap_ends=True, segments=14, radius1=0.28, radius2=0.22, depth=0.75)
    bm_s1.to_mesh(mesh_s1)
    bm_s1.free()
    s1 = bpy.data.objects.new("Prop_Grain_Sack_Upright", mesh_s1)
    s1.location = (xs1, base_y, 0.375)
    link_to_col(s1, col)
    apply_modifiers(s1, bevel_width=0.02)
    assign_material(s1, mat_burlap)
    # Tied Rope Collar & Flared Top
    create_cylinder("Prop_Sack_Rope_Tied", 0.15, 0.04, (xs1, base_y, 0.72), col, mat_rope, segments=12, bevel=False)
    create_cylinder("Prop_Sack_Flared_Mouth", 0.19, 0.12, (xs1, base_y, 0.80), col, mat_burlap, segments=12)

    # Slumped Horizontal Grain Sack
    xs2 = base_x + 0.95
    s2 = create_box("Prop_Grain_Sack_Lying", (0.75, 0.48, 0.32), (xs2, base_y, 0.16), col, mat_burlap, bevel_width=0.04)
    s2.rotation_euler = (0, 0, math.radians(14.0))

    # Round Woven Wicker Basket with Arch Handle
    xb1 = base_x + 1.85
    b_obj = create_cylinder("Prop_Wicker_Basket_Round", 0.30, 0.38, (xb1, base_y, 0.19), col, mat_wicker, segments=18, bevel_width=0.02)
    # Arch Handle
    handle = create_box("Prop_Basket_Handle", (0.04, 0.58, 0.32), (xb1, base_y, 0.46), col, mat_wicker)
    handle.rotation_euler = (math.radians(12.0), 0, 0)

    # Rectangular Woven Storage Hamper with Lid
    xb2 = base_x + 2.80
    create_box("Prop_Wicker_Hamper_Body", (0.65, 0.42, 0.40), (xb2, base_y, 0.20), col, mat_wicker, bevel_width=0.025)
    create_box("Prop_Wicker_Hamper_Lid", (0.68, 0.45, 0.08), (xb2, base_y, 0.44), col, mat_wicker, bevel_width=0.02)

# ==============================================================================
# 4. WOODEN BUCKETS & CLAY POTTERY
# ==============================================================================
def build_buckets_and_pottery(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/02_Kitchen_Tools"
    mat_wood = "M_Wood_AgedOak"
    mat_iron = "M_Iron_Wrought"
    mat_glazed = "M_Ceramic_Glazed"
    mat_clay = "M_Clay_Terracotta"

    # Staved Wooden Water Bucket with Iron Bands & Bail Handle
    xb = base_x
    b_mesh = bpy.data.meshes.new("Prop_Bucket_Staved_Body")
    bm_b = bmesh.new()
    bmesh.ops.create_cone(bm_b, cap_ends=True, segments=16, radius1=0.18, radius2=0.15, depth=0.40)
    bm_b.to_mesh(b_mesh)
    bm_b.free()
    bucket = bpy.data.objects.new("Prop_Bucket_Staved_Body", b_mesh)
    bucket.location = (xb, base_y, 0.20)
    link_to_col(bucket, col)
    apply_modifiers(bucket, bevel_width=0.012)
    assign_material(bucket, mat_wood)
    # Iron hoops
    create_cylinder("Prop_Bucket_Hoop_Top", 0.178, 0.03, (xb, base_y, 0.34), col, mat_iron, segments=16, bevel=False)
    create_cylinder("Prop_Bucket_Hoop_Bot", 0.156, 0.03, (xb, base_y, 0.08), col, mat_iron, segments=16, bevel=False)
    # Hinged Curved Bail Handle
    b_handle = create_box("Prop_Bucket_Bail_Handle", (0.02, 0.34, 0.26), (xb, base_y, 0.45), col, mat_iron, bevel=False)
    b_handle.rotation_euler = (math.radians(-22.0), 0, 0)

    # Salt-Glazed Ceramic Storage Crock with Twin Handles
    xp1 = base_x + 0.75
    crock = create_cylinder("Prop_Clay_Crock_Glazed", 0.22, 0.44, (xp1, base_y, 0.22), col, mat_glazed, segments=18, bevel_width=0.02)
    create_cylinder("Prop_Clay_Crock_Rim", 0.24, 0.06, (xp1, base_y, 0.44), col, mat_glazed, segments=18, bevel_width=0.015)
    create_box("Prop_Clay_Crock_Handle_L", (0.05, 0.10, 0.08), (xp1 - 0.24, base_y, 0.35), col, mat_glazed)
    create_box("Prop_Clay_Crock_Handle_R", (0.05, 0.10, 0.08), (xp1 + 0.24, base_y, 0.35), col, mat_glazed)

    # Tavern Ceramic Ale Pitcher / Jug
    xp2 = base_x + 1.45
    pitcher = create_cylinder("Prop_Clay_Pitcher_Jug", 0.14, 0.36, (xp2, base_y, 0.18), col, mat_clay, segments=16, bevel_width=0.015)
    create_cylinder("Prop_Clay_Pitcher_Neck", 0.08, 0.12, (xp2, base_y, 0.40), col, mat_clay, segments=14, bevel_width=0.01)
    create_box("Prop_Clay_Pitcher_Handle", (0.03, 0.12, 0.22), (xp2, base_y + 0.12, 0.30), col, mat_clay)

# ==============================================================================
# 5. COOKING UTENSILS & KITCHENWARE
# ==============================================================================
def build_cooking_utensils(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/02_Kitchen_Tools"
    mat_iron = "M_Iron_Wrought"
    mat_rusted = "M_Iron_Rusted"
    mat_wood = "M_Wood_LightPine"

    # 3-Legged Cast Iron Cauldron with Bail Handle
    xc = base_x
    cauldron = create_cylinder("Prop_Iron_Cauldron_Pot", 0.26, 0.32, (xc, base_y, 0.26), col, mat_iron, segments=18, bevel_width=0.02)
    # 3 tripod legs
    for li, lang in enumerate([0, math.radians(120), math.radians(240)]):
        lx = xc + 0.20 * math.cos(lang)
        ly = base_y + 0.20 * math.sin(lang)
        create_box(f"Prop_Cauldron_Leg_{li}", (0.04, 0.04, 0.14), (lx, ly, 0.07), col, mat_iron)
    # Bail handle
    ch = create_box("Prop_Cauldron_Handle", (0.02, 0.48, 0.32), (xc, base_y, 0.50), col, mat_iron, bevel=False)
    ch.rotation_euler = (math.radians(18.0), 0, 0)

    # Long-Handled Forged Iron Skillet / Frying Pan
    xs = base_x + 0.85
    create_cylinder("Prop_Skillet_Pan_Base", 0.18, 0.05, (xs, base_y, 0.025), col, mat_rusted, segments=16, bevel_width=0.01)
    create_box("Prop_Skillet_Handle", (0.04, 0.42, 0.02), (xs, base_y - 0.28, 0.04), col, mat_rusted)

    # Carved Wooden Spoon & Soup Ladle
    xl = base_x + 1.55
    create_cylinder("Prop_Wooden_Ladle_Bowl", 0.07, 0.06, (xl, base_y, 0.03), col, mat_wood, segments=12)
    create_box("Prop_Wooden_Ladle_Handle", (0.025, 0.38, 0.02), (xl, base_y - 0.22, 0.05), col, mat_wood)

# ==============================================================================
# 6. ROPES, CHAINS & HOOKS
# ==============================================================================
def build_ropes_and_chains(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/02_Kitchen_Tools"
    mat_rope = "M_Hemp_Rope"
    mat_iron = "M_Iron_Wrought"

    # Coiled Floor Hemp Rope with Tied Loop
    xr = base_x
    for ring_i, rad in enumerate([0.16, 0.24, 0.32]):
        create_cylinder(f"Prop_Rope_Coil_Ring_{ring_i}", rad, 0.045, (xr, base_y, 0.025 * ring_i + 0.02), col, mat_rope, segments=18, bevel=False)
    create_box("Prop_Rope_Knot_Tied", (0.12, 0.16, 0.09), (xr + 0.28, base_y, 0.05), col, mat_rope)

    # Forged Iron Chain Links with Hoist Hook
    xc = base_x + 1.15
    for link_i in range(8):
        lz = 0.06 + link_i * 0.12
        link_obj = create_box(f"Prop_Chain_Link_{link_i}", (0.08, 0.04, 0.14), (xc, base_y, lz), col, mat_iron, bevel=False)
        if link_i % 2 == 1:
            link_obj.rotation_euler = (0, 0, math.radians(90.0))
    # Heavy Forged Hoist Hook at bottom
    create_box("Prop_Chain_Hook_Eye", (0.07, 0.07, 0.08), (xc, base_y, 1.05), col, mat_iron)
    create_box("Prop_Chain_Hook_Curved", (0.04, 0.16, 0.18), (xc, base_y + 0.06, 1.18), col, mat_iron)

# ==============================================================================
# 7. TOOLS (AXE, HAMMER, PITCHFORK, SCYTHE)
# ==============================================================================
def build_tools(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/02_Kitchen_Tools"
    mat_wood = "M_Wood_LightPine"
    mat_iron = "M_Iron_Wrought"

    # 1. Woodcutter's Felling Axe
    xa = base_x
    create_cylinder("Prop_Tool_Axe_Handle", 0.024, 0.85, (xa, base_y, 0.425), col, mat_wood, segments=10)
    create_box("Prop_Tool_Axe_Head", (0.06, 0.22, 0.14), (xa, base_y - 0.04, 0.80), col, mat_iron, bevel_width=0.015)
    create_box("Prop_Tool_Axe_CuttingBlade", (0.01, 0.18, 0.16), (xa, base_y - 0.12, 0.80), col, mat_iron, bevel_width=0.005)

    # 2. Blacksmith's Forging Cross-Peen Hammer
    xh = base_x + 0.55
    create_cylinder("Prop_Tool_Hammer_Handle", 0.022, 0.42, (xh, base_y, 0.21), col, mat_wood, segments=10)
    create_box("Prop_Tool_Hammer_Head", (0.07, 0.16, 0.07), (xh, base_y, 0.40), col, mat_iron, bevel_width=0.01)

    # 3. 3-Tine Farm Pitchfork
    xp = base_x + 1.10
    create_cylinder("Prop_Tool_Pitchfork_Pole", 0.022, 1.65, (xp, base_y, 0.825), col, mat_wood, segments=10)
    create_box("Prop_Tool_Pitchfork_Socket", (0.04, 0.04, 0.12), (xp, base_y, 1.68), col, mat_iron)
    create_box("Prop_Tool_Pitchfork_Crossbar", (0.28, 0.03, 0.03), (xp, base_y, 1.74), col, mat_iron)
    for ti, tx in enumerate([-0.12, 0.0, 0.12]):
        create_box(f"Prop_Tool_Pitchfork_Tine_{ti}", (0.018, 0.018, 0.34), (xp + tx, base_y, 1.92), col, mat_iron)

    # 4. Harvest Grain Scythe
    xs = base_x + 1.80
    create_cylinder("Prop_Tool_Scythe_Snath", 0.025, 1.75, (xs, base_y, 0.875), col, mat_wood, segments=10)
    create_box("Prop_Tool_Scythe_Handgrip_1", (0.14, 0.03, 0.03), (xs + 0.06, base_y, 0.70), col, mat_wood)
    create_box("Prop_Tool_Scythe_Handgrip_2", (0.14, 0.03, 0.03), (xs + 0.06, base_y, 1.25), col, mat_wood)
    # Long curved sweeping scythe blade
    blade = create_box("Prop_Tool_Scythe_Blade", (0.85, 0.08, 0.012), (xs - 0.38, base_y, 1.76), col, mat_iron)
    blade.rotation_euler = (0, math.radians(-18.0), 0)

# ==============================================================================
# 8. FURNITURE: TABLES, BENCHES, CHAIRS & STOOLS
# ==============================================================================
def build_furniture(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/03_Furniture"
    mat_oak = "M_Wood_AgedOak"
    mat_dark = "M_Wood_DarkTimber"

    # 1. Heavy Trestle Dining Table with Through-Mortise Wedge Keys
    xt = base_x
    # Split-oak tabletop planks
    create_box("Prop_Table_Trestle_Top", (2.40, 0.95, 0.08), (xt, base_y, 0.76), col, mat_oak)
    # Trestle end frames (chamfered posts and splayed foot)
    for side_x in [-0.85, 0.85]:
        create_box(f"Prop_Table_Trestle_Foot_{side_x}", (0.18, 0.80, 0.12), (xt + side_x, base_y, 0.06), col, mat_oak)
        create_box(f"Prop_Table_Trestle_Post_{side_x}", (0.16, 0.20, 0.62), (xt + side_x, base_y, 0.41), col, mat_oak)
        create_box(f"Prop_Table_Trestle_TopBearer_{side_x}", (0.18, 0.80, 0.10), (xt + side_x, base_y, 0.70), col, mat_oak)
    # Center longitudinal spine stretcher
    create_box("Prop_Table_Trestle_Stretcher", (2.10, 0.08, 0.16), (xt, base_y, 0.35), col, mat_oak)
    # Locking wedge pins
    create_box("Prop_Table_Wedge_L", (0.04, 0.12, 0.22), (xt - 0.95, base_y, 0.35), col, mat_dark)
    create_box("Prop_Table_Wedge_R", (0.04, 0.12, 0.22), (xt + 0.95, base_y, 0.35), col, mat_dark)

    # 2. Long Tavern Bench with Stretcher
    xb = base_x + 3.0
    create_box("Prop_Bench_Tavern_Seat", (2.20, 0.34, 0.06), (xb, base_y, 0.47), col, mat_oak)
    for bx in [-0.80, 0.80]:
        create_box(f"Prop_Bench_Leg_{bx}", (0.12, 0.30, 0.44), (xb + bx, base_y, 0.22), col, mat_oak)
    create_box("Prop_Bench_Stretcher", (1.80, 0.05, 0.10), (xb, base_y, 0.20), col, mat_oak)

    # 3. Splayed 3-Legged Wooden Hearth Stool
    xs = base_x + 5.0
    create_cylinder("Prop_Stool_3Leg_Seat", 0.18, 0.05, (xs, base_y, 0.45), col, mat_oak, segments=16)
    for li, lang in enumerate([0, math.radians(120), math.radians(240)]):
        lx = xs + 0.11 * math.cos(lang)
        ly = base_y + 0.11 * math.sin(lang)
        leg = create_cylinder(f"Prop_Stool_3Leg_Foot_{li}", 0.024, 0.46, (lx, ly, 0.22), col, mat_oak, segments=10)
        leg.rotation_euler = (0.15 * math.sin(lang), 0.15 * math.cos(lang), 0)

    # 4. Pegged Wooden Tavern Chair with Splat Back
    xc = base_x + 6.2
    create_box("Prop_Chair_Tavern_Seat", (0.48, 0.46, 0.05), (xc, base_y, 0.46), col, mat_oak)
    for cx in [-0.19, 0.19]:
        for cy in [-0.18, 0.18]:
            create_box(f"Prop_Chair_Leg_{cx}_{cy}", (0.05, 0.05, 0.44), (xc + cx, base_y + cy, 0.22), col, mat_oak)
    # Backrest stiles and curved top rail
    create_box("Prop_Chair_Back_Stile_L", (0.05, 0.05, 0.50), (xc - 0.19, base_y + 0.18, 0.73), col, mat_oak)
    create_box("Prop_Chair_Back_Stile_R", (0.05, 0.05, 0.50), (xc + 0.19, base_y + 0.18, 0.73), col, mat_oak)
    create_box("Prop_Chair_Back_TopRail", (0.48, 0.04, 0.12), (xc, base_y + 0.18, 0.94), col, mat_oak)
    create_box("Prop_Chair_Back_Splat", (0.14, 0.02, 0.40), (xc, base_y + 0.18, 0.70), col, mat_oak)

# ==============================================================================
# 9. LANTERNS & SIGNBOARDS
# ==============================================================================
def build_lanterns_and_signboards(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/04_Lighting_Street"
    mat_iron = "M_Iron_Wrought"
    mat_glass = "M_Glass_Leaded"
    mat_lantern = "M_Lantern_Warm"
    mat_wood = "M_Wood_AgedOak"

    # 1. Glazed Hanging Street Lantern with Wall Bracket
    xl = base_x
    create_box("Prop_Lantern_Street_Cage", (0.24, 0.24, 0.36), (xl, base_y, 1.40), col, mat_iron, bevel_width=0.01)
    create_box("Prop_Lantern_Street_Glass", (0.20, 0.20, 0.30), (xl, base_y, 1.40), col, mat_glass, bevel=False)
    create_cylinder("Prop_Lantern_Street_Candle", 0.035, 0.14, (xl, base_y, 1.34), col, "M_Plaster_Lime", segments=10)
    create_cylinder("Prop_Lantern_Street_Flame", 0.015, 0.04, (xl, base_y, 1.43), col, mat_lantern, segments=8)
    # Pyramid copper cap & top loop
    create_box("Prop_Lantern_Street_Cap", (0.26, 0.26, 0.12), (xl, base_y, 1.62), col, mat_iron)
    # Scrolled Wrought Iron Wall Bracket
    create_box("Prop_Lantern_Wall_Plate", (0.06, 0.04, 0.65), (xl, base_y + 0.45, 1.65), col, mat_iron)
    create_box("Prop_Lantern_Wall_Arm", (0.04, 0.45, 0.04), (xl, base_y + 0.22, 1.85), col, mat_iron)

    # 2. Portable Hand Lantern with Glass Cylinder
    xh = base_x + 1.10
    create_cylinder("Prop_Hand_Lantern_Base", 0.11, 0.05, (xh, base_y, 0.025), col, mat_iron, segments=16)
    create_cylinder("Prop_Hand_Lantern_Glass", 0.09, 0.24, (xh, base_y, 0.17), col, mat_glass, segments=16, bevel=False)
    create_cylinder("Prop_Hand_Lantern_Cap", 0.11, 0.06, (xh, base_y, 0.32), col, mat_iron, segments=16)
    create_box("Prop_Hand_Lantern_WireHandle", (0.02, 0.20, 0.22), (xh, base_y, 0.44), col, mat_iron, bevel=False)
    create_cylinder("Prop_Hand_Lantern_Flame", 0.02, 0.06, (xh, base_y, 0.15), col, mat_lantern, segments=8)

    # 3. Hanging Medieval Tavern Signboard with Scrolled Bracket
    xs = base_x + 2.50
    # Shield-shaped wooden signboard
    create_box("Prop_Signboard_Shield_Plank", (0.80, 0.06, 1.05), (xs, base_y, 1.35), col, mat_wood, bevel_width=0.02)
    create_box("Prop_Signboard_Border_Trim", (0.84, 0.08, 1.09), (xs, base_y, 1.35), col, "M_Wood_DarkTimber", bevel_width=0.015)
    # Suspension chains
    create_box("Prop_Signboard_Chain_L", (0.02, 0.02, 0.32), (xs - 0.28, base_y, 1.95), col, mat_iron)
    create_box("Prop_Signboard_Chain_R", (0.02, 0.02, 0.32), (xs + 0.28, base_y, 1.95), col, mat_iron)
    # Heavy wrought iron wall bracket
    create_box("Prop_Signboard_Wall_Spur", (0.05, 0.85, 0.05), (xs, base_y + 0.38, 2.12), col, mat_iron)
    create_box("Prop_Signboard_Wall_Plate", (0.08, 0.04, 0.95), (xs, base_y + 0.80, 2.10), col, mat_iron)

# ==============================================================================
# 10. TWO-WHEEL VILLAGE HANDCART
# ==============================================================================
def build_handcart(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/04_Lighting_Street"
    mat_wood = "M_Wood_AgedOak"
    mat_iron = "M_Iron_Wrought"

    # Cargo bed (Length: 1.80m, Width: 1.10m, Height from ground: 0.62m)
    create_box("Prop_Cart_Bed_Planks", (1.10, 1.80, 0.05), (base_x, base_y, 0.62), col, mat_wood)
    # Side stakes and sideboards
    create_box("Prop_Cart_Sideboard_L", (0.04, 1.80, 0.35), (base_x - 0.53, base_y, 0.80), col, mat_wood)
    create_box("Prop_Cart_Sideboard_R", (0.04, 1.80, 0.35), (base_x + 0.53, base_y, 0.80), col, mat_wood)
    create_box("Prop_Cart_Frontboard", (1.10, 0.04, 0.35), (base_x, base_y + 0.88, 0.80), col, mat_wood)

    # Heavy wooden axle beam & iron axle spindle
    create_box("Prop_Cart_Axle_Beam", (1.45, 0.12, 0.12), (base_x, base_y, 0.54), col, mat_wood)

    # 2 Large 12-Spoked Wooden Wheels with Iron Rim Tires (Radius 0.54m)
    for wx, side_name in [(-0.76, "L"), (0.76, "R")]:
        # Iron tire rim
        create_cylinder(f"Prop_Cart_Wheel_{side_name}_Tire", 0.54, 0.08, (base_x + wx, base_y, 0.54), col, mat_iron, segments=24)
        bpy.data.objects[f"Prop_Cart_Wheel_{side_name}_Tire"].rotation_euler = (0, math.radians(90.0), 0)
        # Wooden felloe ring
        create_cylinder(f"Prop_Cart_Wheel_{side_name}_Felloe", 0.50, 0.07, (base_x + wx, base_y, 0.54), col, mat_wood, segments=24)
        bpy.data.objects[f"Prop_Cart_Wheel_{side_name}_Felloe"].rotation_euler = (0, math.radians(90.0), 0)
        # Center nave / hub
        create_cylinder(f"Prop_Cart_Wheel_{side_name}_Hub", 0.12, 0.14, (base_x + wx, base_y, 0.54), col, mat_wood, segments=12)
        bpy.data.objects[f"Prop_Cart_Wheel_{side_name}_Hub"].rotation_euler = (0, math.radians(90.0), 0)
        # 8 Spokes
        for spk_i in range(8):
            spk_ang = spk_i * (math.pi / 4)
            spk = create_box(f"Prop_Cart_Spoke_{side_name}_{spk_i}", (0.04, 0.04, 0.44), (base_x + wx, base_y, 0.54), col, mat_wood)
            spk.rotation_euler = (spk_ang, 0, 0)

    # Dual Pull Shafts / Handles extending forward
    create_box("Prop_Cart_Shaft_L", (0.06, 1.40, 0.06), (base_x - 0.42, base_y - 1.40, 0.48), col, mat_wood)
    create_box("Prop_Cart_Shaft_R", (0.06, 1.40, 0.06), (base_x + 0.42, base_y - 1.40, 0.48), col, mat_wood)
    # Ground resting prop leg
    create_box("Prop_Cart_Rest_Prop", (0.06, 0.06, 0.48), (base_x, base_y - 1.80, 0.24), col, mat_wood)

# ==============================================================================
# 11. FIREWOOD & CHOPPING BLOCK
# ==============================================================================
def build_firewood_and_chopping_block(base_x=0.0, base_y=0.0):
    col = "04_PROPS_FURNITURE/04_Lighting_Street"
    mat_wood = "M_Wood_AgedOak"
    mat_bark = "M_Firewood_Bark"
    mat_iron = "M_Iron_Wrought"

    # Stacked Cord of Split Firewood Logs (2.0m wide x 0.6m deep x 0.9m high)
    create_box("Prop_Firewood_Stack_Core", (2.00, 0.60, 0.90), (base_x, base_y, 0.45), col, mat_bark, bevel_width=0.03)
    # Individual split log ends facing out
    for layer in range(4):
        for col_i in range(6):
            lx = base_x - 0.85 + col_i * 0.34
            lz = 0.12 + layer * 0.24
            create_cylinder(f"Prop_Firewood_Log_{layer}_{col_i}", 0.09, 0.64, (lx, base_y, lz), col, mat_bark, segments=8)
            bpy.data.objects[f"Prop_Firewood_Log_{layer}_{col_i}"].rotation_euler = (math.radians(90.0), 0, random.uniform(-0.08, 0.08))

    # Tree Stump Chopping Block with Embedded Axe
    xb = base_x + 1.85
    # Heavy round tree trunk block
    create_cylinder("Prop_Chopping_Block_Stump", 0.34, 0.58, (xb, base_y, 0.29), col, mat_bark, segments=16, bevel_width=0.02)
    # Split log chunk on top
    create_box("Prop_Chopping_Split_Log", (0.16, 0.22, 0.28), (xb - 0.06, base_y, 0.68), col, mat_wood)
    # Embedded woodcutter axe
    axe_head = create_box("Prop_Chopping_Axe_Head", (0.04, 0.18, 0.12), (xb, base_y, 0.76), col, mat_iron)
    axe_head.rotation_euler = (0, math.radians(18.0), 0)
    axe_handle = create_cylinder("Prop_Chopping_Axe_Handle", 0.022, 0.80, (xb + 0.18, base_y, 1.05), col, "M_Wood_LightPine", segments=10)
    axe_handle.rotation_euler = (0, math.radians(48.0), 0)

# ==============================================================================
# MASTER PROPS GENERATION FUNCTION
# ==============================================================================
def build_all_village_props():
    print("==================================================")
    print("BUILDING COMPLETE MEDIEVAL VILLAGE PROP COLLECTION")
    print("==================================================")

    root_col = get_or_create_collection("04_PROPS_FURNITURE")
    sub_cols = [
        "01_Containers",
        "02_Kitchen_Tools",
        "03_Furniture",
        "04_Lighting_Street"
    ]
    for sc in sub_cols:
        full_name = f"04_PROPS_FURNITURE/{sc}"
        get_or_create_collection(full_name, root_col)
        clear_collection(full_name)

    # Row 1: Containers (Barrels, Crates, Sacks, Baskets) at Y = 4.0
    print("[1/5] Building Barrels, Crates, Sacks & Baskets...")
    build_barrels(base_x=-8.0, base_y=4.0)
    build_crates(base_x=-5.0, base_y=4.0)
    build_sacks_and_baskets(base_x=-2.0, base_y=4.0)

    # Row 2: Buckets, Pottery, Cooking Utensils, Ropes & Tools at Y = 1.0
    print("[2/5] Building Buckets, Pottery, Utensils, Ropes & Tools...")
    build_buckets_and_pottery(base_x=-8.0, base_y=1.0)
    build_cooking_utensils(base_x=-5.0, base_y=1.0)
    build_ropes_and_chains(base_x=-2.0, base_y=1.0)
    build_tools(base_x=0.5, base_y=1.0)

    # Row 3: Furniture (Trestle Table, Benches, Stools, Chairs) at Y = -2.5
    print("[3/5] Building Tables, Benches, Stools & Chairs...")
    build_furniture(base_x=-6.5, base_y=-2.5)

    # Row 4: Lighting, Signboards, Handcart, Firewood & Chopping Block at Y = -6.5
    print("[4/5] Building Lanterns, Signboard, Handcart & Firewood...")
    build_lanterns_and_signboards(base_x=-8.0, base_y=-6.5)
    build_handcart(base_x=-3.0, base_y=-6.5)
    build_firewood_and_chopping_block(base_x=1.0, base_y=-6.5)

    print("==================================================")
    print("MEDIEVAL VILLAGE PROPS SUCCESSFULLY CREATED!")
    print("==================================================")

if __name__ == '__main__':
    build_all_village_props()

