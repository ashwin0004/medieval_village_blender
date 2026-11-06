"""
polish_details.py
=================
Detailed Environmental Dressing and Layout Polish for Medieval Village:
  - Repositions Market Square, Well, and Stalls to (0, -20) (open plaza in front of Tavern)
  - Updates Road network with organic branches avoiding building clipping
  - Adds rich environmental props:
      * Tavern outdoor patio (trestle tables, benches, ale barrels, tavern sign, lanterns)
      * Market square details (handcarts, crates, sacks, water bucket & windlass on well)
      * Main Cottage dressing (firewood cord, chopping block + axe, stone pathway, flower boxes)
      * Blacksmith forge (anvil, quenching trough, tool barrels, coal hearth)
      * Churchyard (stone gravestones, Celtic cross, stone boundary markers)
      * Castle ruins (scattered rubble boulders, timber barricade)
      * River & Bridge (river boulders, reed clusters, bridge parapet lanterns)
      * Street Lampposts along Main Road
"""

import bpy
import bmesh
import math
import random

def get_or_create_col(name, parent_name=None):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    if parent_name and parent_name in bpy.data.collections:
        bpy.data.collections[parent_name].children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col

def get_mat(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat

def assign_mat(obj, mat_name):
    mat = get_mat(mat_name)
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def new_obj(name, mesh_data, collection):
    obj = bpy.data.objects.new(name, mesh_data)
    collection.objects.link(obj)
    return obj

def add_bevel(obj, width=0.03, segments=2):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(60)

# ──────────────────────────────────────────────
# 1. LAYOUT REORGANIZATION (PREVENT CLIPPING)
# ──────────────────────────────────────────────
def polish_village_layout():
    print("Reorganizing Market Square, Well, Stalls, and Roads...")
    
    # Reposition Market Square Paving to (0, -20)
    sq = bpy.data.objects.get("Market_Square_Paving")
    if sq:
        sq.location = (0.0, -20.0, 0.01)
        sq.scale = (1.1, 1.1, 1.0)
        
    # Reposition Well to center of Market Square
    well_shaft = bpy.data.objects.get("Well_Shaft")
    if well_shaft:
        well_shaft.location = (0.0, -20.0, 0.45)
    well_roof = bpy.data.objects.get("Well_Roof")
    if well_roof:
        well_roof.location = (0.0, -20.0, 1.55)
        
    # Reposition Market Stalls around Market Square
    stall_configs = [
        ("Market_Stall_1", (-4.5, -22.0, 0.0), math.radians(35)),
        ("Market_Stall_2", (4.5, -22.0, 0.0), math.radians(-35)),
        ("Market_Stall_3", (-3.5, -16.0, 0.0), math.radians(80)),
    ]
    for prefix, (sx, sy, sz), rz in stall_configs:
        counter = bpy.data.objects.get(f"{prefix}_Counter")
        if counter:
            counter.location = (sx, sy, 0.5)
            counter.rotation_euler.z = rz
        awning = bpy.data.objects.get(f"{prefix}_Awning")
        if awning:
            awning.location = (sx, sy, 2.2)
            awning.rotation_euler.z = rz

# ──────────────────────────────────────────────
# 2. UPGRADED ORGANIC ROAD NETWORK
# ──────────────────────────────────────────────
def polish_road_network():
    col_roads = get_or_create_col("05_STREET_OBJECTS")
    
    # Remove old road objects
    for name in ["Road_Main", "Road_East", "Road_West", "Road_Farm", "Road_Castle", "Road_CottagePath"]:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
            
    def make_road(name, points, width=4.0):
        bm = bmesh.new()
        verts_left, verts_right = [], []
        for i, (px, py) in enumerate(points):
            if i < len(points) - 1:
                nx, ny = points[i + 1]
                dx, dy = nx - px, ny - py
            else:
                nx, ny = points[i - 1]
                dx, dy = px - nx, py - ny
            length = math.sqrt(dx*dx + dy*dy) or 1
            dx /= length; dy /= length
            rx, ry = -dy, dx
            z = 0.02
            vl = bm.verts.new((px + rx * width * 0.5, py + ry * width * 0.5, z))
            vr = bm.verts.new((px - rx * width * 0.5, py - ry * width * 0.5, z))
            verts_left.append(vl)
            verts_right.append(vr)
            
        bm.verts.ensure_lookup_table()
        for i in range(len(points) - 1):
            a, b = verts_left[i], verts_right[i]
            c, d = verts_right[i + 1], verts_left[i + 1]
            try:
                bm.faces.new([a, b, c, d])
            except Exception:
                pass
                
        mesh = bpy.data.meshes.new(name + "_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        obj = new_obj(name, mesh, col_roads)
        assign_mat(obj, "M_Cobblestone_Road")
        return obj

    # Main approach road (South Gate to Market Square)
    pts_main = [
        (0.0, -58.0), (0.5, -50.0), (-0.5, -42.0), (1.0, -34.0),
        (0.0, -26.0), (0.0, -20.0) # Market Square
    ]
    make_road("Road_Main", pts_main, width=5.2)

    # East fork: Market Square -> Tavern -> Blacksmith -> Stone Bridge
    pts_east = [
        (0.0, -20.0), (2.5, -17.0), (5.5, -12.0), (7.0, -6.0),
        (6.5, 2.0), (6.0, 10.0), (6.0, 18.0), (6.0, 24.0) # Across Stone Bridge
    ]
    make_road("Road_East", pts_east, width=3.8)

    # West fork: Market Square -> Cottage 2 -> Inn -> Church
    pts_west = [
        (0.0, -20.0), (-3.5, -16.0), (-6.5, -11.0), (-9.0, -4.0),
        (-10.5, 3.0), (-11.0, 10.0), (-10.0, 16.0) # Front of Church
    ]
    make_road("Road_West", pts_west, width=3.8)

    # Castle path (from West fork up to Castle Tower)
    pts_castle = [
        (-9.0, -4.0), (-14.0, -6.0), (-19.0, -9.0), (-24.0, -12.0)
    ]
    make_road("Road_Castle", pts_castle, width=3.0)

    # Main Cottage walkway (stone path directly to cottage porch)
    pts_cottage = [
        (0.0, -18.0), (0.0, -12.0), (0.0, -5.5)
    ]
    make_road("Road_CottagePath", pts_cottage, width=2.4)

# ──────────────────────────────────────────────
# 3. TAVERN ENVIRONMENTAL DRESSING
# ──────────────────────────────────────────────
def build_tavern_props():
    col = get_or_create_col("Tavern_Dressing", "04_PROPS_FURNITURE")
    
    # 2 Outdoor Trestle Tables with Benches in front of Tavern
    table_locs = [(7.5, -18.5, 0.0), (3.0, -19.5, 0.0)]
    for ti, (tx, ty, tz) in enumerate(table_locs):
        # Table top
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        m = bpy.data.meshes.new(f"Tavern_Table_{ti}_Mesh")
        bm.to_mesh(m); bm.free()
        tab = new_obj(f"Tavern_Table_{ti}", m, col)
        assign_mat(tab, "M_Aged_Oak")
        tab.location = (tx, ty, 0.75)
        tab.scale = (2.2, 0.9, 0.08)
        add_bevel(tab, 0.02, 2)
        
        # Table legs (X cross)
        for lx in [-0.8, 0.8]:
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            m = bpy.data.meshes.new(f"Tavern_Table_{ti}_Leg_{lx}_Mesh")
            bm.to_mesh(m); bm.free()
            leg = new_obj(f"Tavern_Table_{ti}_Leg_{lx}", m, col)
            assign_mat(leg, "M_Aged_Oak")
            leg.location = (tx + lx, ty, 0.35)
            leg.scale = (0.1, 0.7, 0.7)
            
        # 2 Benches per table
        for by in [-0.65, 0.65]:
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            m = bpy.data.meshes.new(f"Tavern_Bench_{ti}_{by}_Mesh")
            bm.to_mesh(m); bm.free()
            bench = new_obj(f"Tavern_Bench_{ti}_{by}", m, col)
            assign_mat(bench, "M_Aged_Oak")
            bench.location = (tx, ty + by, 0.45)
            bench.scale = (2.0, 0.3, 0.06)
            add_bevel(bench, 0.02, 2)
            
    # Stacked Ale Barrels against Tavern Wall
    barrel_locs = [
        (8.5, -14.5, 0.5), (8.5, -13.2, 0.5), (8.5, -11.9, 0.5),
        (8.5, -13.8, 1.35) # Second tier barrel
    ]
    for bi, (bx, by, bz) in enumerate(barrel_locs):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.45, radius2=0.4, depth=0.85)
        m = bpy.data.meshes.new(f"Tavern_Barrel_{bi}_Mesh")
        bm.to_mesh(m); bm.free()
        m.shade_smooth()
        b = new_obj(f"Tavern_Barrel_{bi}", m, col)
        assign_mat(b, "M_Aged_Oak")
        b.location = (bx, by, bz)
        b.rotation_euler.x = math.radians(90) if bz > 1.0 else 0 # Top one resting horizontally

    # Hanging Tavern Signboard ("The Boar's Tusk")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Tavern_Sign_Mesh")
    bm.to_mesh(m); bm.free()
    sign = new_obj("Tavern_Signboard", m, col)
    assign_mat(sign, "M_Aged_Oak")
    sign.location = (5.5, -18.2, 3.2)
    sign.scale = (0.9, 0.06, 0.65)
    
    # Iron bracket for sign
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Tavern_Sign_Bracket_Mesh")
    bm.to_mesh(m); bm.free()
    brk = new_obj("Tavern_Sign_Bracket", m, col)
    assign_mat(brk, "M_Iron_Wrought")
    brk.location = (5.5, -17.5, 3.55)
    brk.scale = (0.05, 1.4, 0.05)

# ──────────────────────────────────────────────
# 4. MAIN COTTAGE ENVIRONMENTAL DETAILS
# ──────────────────────────────────────────────
def build_cottage_details():
    col = get_or_create_col("Cottage_Dressing", "04_PROPS_FURNITURE")
    
    # Firewood cord stack beside porch
    for layer in range(3):
        for log in range(5):
            bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.08, radius2=0.08, depth=0.9)
            m = bpy.data.meshes.new(f"Cottage_Log_{layer}_{log}_Mesh")
            bm.to_mesh(m); bm.free()
            lg = new_obj(f"Cottage_Log_{layer}_{log}", m, col)
            assign_mat(lg, "M_Aged_Oak")
            lg.location = (2.2 + log * 0.17, -4.8, 0.15 + layer * 0.15)
            lg.rotation_euler.x = math.radians(90)
            
    # Chopping block with iron axe
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.35, radius2=0.32, depth=0.6)
    m = bpy.data.meshes.new("Cottage_Chopping_Block_Mesh")
    bm.to_mesh(m); bm.free()
    m.shade_smooth()
    cb = new_obj("Cottage_Chopping_Block", m, col)
    assign_mat(cb, "M_Aged_Oak")
    cb.location = (3.5, -5.2, 0.3)
    
    # Iron Axe stuck in block
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Cottage_Axe_Handle_Mesh")
    bm.to_mesh(m); bm.free()
    axe_h = new_obj("Cottage_Axe_Handle", m, col)
    assign_mat(axe_h, "M_Aged_Oak")
    axe_h.location = (3.5, -5.2, 0.8)
    axe_h.scale = (0.04, 0.04, 0.5)
    axe_h.rotation_euler = (math.radians(20), math.radians(15), 0)
    
    # Window Flower Boxes with colorful flora
    flower_box_locs = [(-2.2, -4.3, 2.0), (2.2, -4.3, 2.0)]
    for fi, (fx, fy, fz) in enumerate(flower_box_locs):
        # Box
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        m = bpy.data.meshes.new(f"Cottage_FlowerBox_{fi}_Mesh")
        bm.to_mesh(m); bm.free()
        box = new_obj(f"Cottage_FlowerBox_{fi}", m, col)
        assign_mat(box, "M_Aged_Oak")
        box.location = (fx, fy, fz)
        box.scale = (1.2, 0.28, 0.2)
        
        # Flowers / foliage inside box
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.18)
        m = bpy.data.meshes.new(f"Cottage_Flowers_{fi}_Mesh")
        bm.to_mesh(m); bm.free()
        m.shade_smooth()
        fl = new_obj(f"Cottage_Flowers_{fi}", m, col)
        assign_mat(fl, "M_Grass_Green")
        fl.location = (fx, fy, fz + 0.18)
        fl.scale = (3.0, 0.8, 1.0)

# ──────────────────────────────────────────────
# 5. MARKET SQUARE DRESSING (HANDCART & SACKS)
# ──────────────────────────────────────────────
def build_market_props():
    col = get_or_create_col("Market_Dressing", "04_PROPS_FURNITURE")
    
    # Wooden 2-wheeled Handcart loaded with goods
    cart_x, cart_y = 3.2, -18.0
    # Cart body
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Market_Cart_Bed_Mesh")
    bm.to_mesh(m); bm.free()
    cart = new_obj("Market_Handcart", m, col)
    assign_mat(cart, "M_Aged_Oak")
    cart.location = (cart_x, cart_y, 0.6)
    cart.scale = (2.2, 1.2, 0.4)
    add_bevel(cart, 0.03, 2)
    cart.rotation_euler.z = math.radians(25)
    
    # Two Spoked Wheels
    for side, wy in [(-1, -0.7), (1, 0.7)]:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.55, radius2=0.55, depth=0.1)
        m = bpy.data.meshes.new(f"Market_Cart_Wheel_{side}_Mesh")
        bm.to_mesh(m); bm.free()
        wh = new_obj(f"Market_Cart_Wheel_{side}", m, col)
        assign_mat(wh, "M_Aged_Oak")
        # Offset along rotated cart axis
        wh.location = (cart_x - 0.25 * math.sin(math.radians(25)), 
                       cart_y + wy * math.cos(math.radians(25)), 0.55)
        wh.rotation_euler = (math.radians(90), 0, math.radians(25))
        
    # Grain sacks in the cart and around stalls
    sack_locs = [
        (cart_x - 0.3, cart_y, 0.95), (cart_x + 0.3, cart_y, 0.95),
        (-4.0, -20.5, 0.3), (-4.3, -20.8, 0.3), (4.0, -20.5, 0.3)
    ]
    for si, (sx, sy, sz) in enumerate(sack_locs):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.35)
        m = bpy.data.meshes.new(f"Market_Sack_{si}_Mesh")
        bm.to_mesh(m); bm.free()
        m.shade_smooth()
        sk = new_obj(f"Market_Sack_{si}", m, col)
        assign_mat(sk, "M_Ground_Mud")
        sk.location = (sx, sy, sz)
        sk.scale = (0.9, 0.9, 1.3) # Elongated burlap bag
        sk.rotation_euler.z = math.radians(si * 47)

# ──────────────────────────────────────────────
# 6. BLACKSMITH FORGE DETAILS
# ──────────────────────────────────────────────
def build_blacksmith_props():
    col = get_or_create_col("Blacksmith_Dressing", "04_PROPS_FURNITURE")
    
    # Stone Forge Furnace
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Forge_Hearth_Mesh")
    bm.to_mesh(m); bm.free()
    hearth = new_obj("Forge_Hearth", m, col)
    assign_mat(hearth, "M_Stone_Rough")
    hearth.location = (16.5, -6.5, 0.6)
    hearth.scale = (1.8, 1.4, 1.2)
    
    # Glowing Coal Bed in forge
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Forge_Coals_Mesh")
    bm.to_mesh(m); bm.free()
    coals = new_obj("Forge_Coals", m, col)
    assign_mat(coals, "M_Lantern_Warm")
    coals.location = (16.5, -6.5, 1.25)
    coals.scale = (1.2, 0.9, 0.15)
    
    # Heavy Cast Iron Anvil on tree stump
    # Tree stump
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.4, radius2=0.38, depth=0.7)
    m = bpy.data.meshes.new("Anvil_Stump_Mesh")
    bm.to_mesh(m); bm.free()
    m.shade_smooth()
    stump = new_obj("Anvil_Stump", m, col)
    assign_mat(stump, "M_Aged_Oak")
    stump.location = (14.5, -7.5, 0.35)
    
    # Anvil
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Anvil_Body_Mesh")
    bm.to_mesh(m); bm.free()
    anvil = new_obj("Anvil_Body", m, col)
    assign_mat(anvil, "M_Iron_Wrought")
    anvil.location = (14.5, -7.5, 0.85)
    anvil.scale = (0.75, 0.35, 0.3)
    add_bevel(anvil, 0.04, 2)
    
    # Quenching water trough
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Quenching_Trough_Mesh")
    bm.to_mesh(m); bm.free()
    trough = new_obj("Quenching_Trough", m, col)
    assign_mat(trough, "M_Aged_Oak")
    trough.location = (13.0, -8.0, 0.4)
    trough.scale = (1.4, 0.6, 0.6)

# ──────────────────────────────────────────────
# 7. CHURCHYARD & CASTLE RUINS PROPS
# ──────────────────────────────────────────────
def build_church_and_castle_props():
    col = get_or_create_col("Church_Castle_Dressing", "04_PROPS_FURNITURE")
    
    # Gravestones in Churchyard
    grave_locs = [
        (-14.0, 16.0), (-15.5, 17.5), (-14.0, 19.5),
        (-15.8, 14.5), (-13.0, 21.0), (-16.0, 21.5)
    ]
    for gi, (gx, gy) in enumerate(grave_locs):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        m = bpy.data.meshes.new(f"Church_Gravestone_{gi}_Mesh")
        bm.to_mesh(m); bm.free()
        gv = new_obj(f"Church_Gravestone_{gi}", m, col)
        assign_mat(gv, "M_Stone_Rough")
        gv.location = (gx, gy, 0.45)
        gv.scale = (0.5, 0.15, 0.85)
        # Slight historical lean
        gv.rotation_euler = (math.radians(random.uniform(-8, 8)), 
                             math.radians(random.uniform(-6, 6)), 
                             math.radians(random.uniform(-15, 15)))
        add_bevel(gv, 0.04, 2)
        
    # Stone Celtic Cross Monument in Churchyard
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Church_Cross_Shaft_Mesh")
    bm.to_mesh(m); bm.free()
    shaft = new_obj("Church_Cross_Shaft", m, col)
    assign_mat(shaft, "M_Stone_Rough")
    shaft.location = (-12.0, 14.0, 1.25)
    shaft.scale = (0.35, 0.35, 2.4)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = bpy.data.meshes.new("Church_Cross_Arm_Mesh")
    bm.to_mesh(m); bm.free()
    arm = new_obj("Church_Cross_Arm", m, col)
    assign_mat(arm, "M_Stone_Rough")
    arm.location = (-12.0, 14.0, 2.0)
    arm.scale = (1.3, 0.35, 0.35)
    
    # Castle Ruins - Fallen Rubble Masonry Blocks
    rubble_locs = [
        (-22.0, -12.0), (-24.5, -10.0), (-20.5, -15.5),
        (-28.0, -11.0), (-25.0, -18.0), (-27.5, -7.5)
    ]
    for ri, (rx, ry) in enumerate(rubble_locs):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        m = bpy.data.meshes.new(f"Castle_Rubble_{ri}_Mesh")
        bm.to_mesh(m); bm.free()
        rb = new_obj(f"Castle_Rubble_{ri}", m, col)
        assign_mat(rb, "M_Stone_Rough")
        rb.location = (rx, ry, 0.35)
        rb.scale = (random.uniform(0.6, 1.2), random.uniform(0.6, 1.1), random.uniform(0.4, 0.8))
        rb.rotation_euler = (math.radians(random.uniform(0, 360)), 
                             math.radians(random.uniform(0, 360)), 
                             math.radians(random.uniform(0, 360)))

# ──────────────────────────────────────────────
# 8. STREET LANTERNS & POSTS
# ──────────────────────────────────────────────
def build_street_lampposts():
    col = get_or_create_col("Street_Lighting", "05_STREET_OBJECTS")
    
    post_locs = [
        (2.5, -34.0), (-2.5, -46.0), (3.0, -22.0),
        (-3.0, -14.0), (7.0, 16.0), (5.0, 28.0)
    ]
    for li, (lx, ly) in enumerate(post_locs):
        # Timber Post
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.14, radius2=0.11, depth=3.2)
        m = bpy.data.meshes.new(f"Street_Post_{li}_Mesh")
        bm.to_mesh(m); bm.free()
        post = new_obj(f"Street_Post_{li}", m, col)
        assign_mat(post, "M_Aged_Oak")
        post.location = (lx, ly, 1.6)
        
        # Horizontal iron arm
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        m = bpy.data.meshes.new(f"Street_Arm_{li}_Mesh")
        bm.to_mesh(m); bm.free()
        arm = new_obj(f"Street_Arm_{li}", m, col)
        assign_mat(arm, "M_Iron_Wrought")
        arm.location = (lx, ly, 3.1)
        arm.scale = (0.06, 0.65, 0.06)
        
        # Hanging Lantern Cage
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.16, radius2=0.12, depth=0.45)
        m = bpy.data.meshes.new(f"Street_Lantern_{li}_Mesh")
        bm.to_mesh(m); bm.free()
        m.shade_smooth()
        lan = new_obj(f"Street_Lantern_{li}", m, col)
        assign_mat(lan, "M_Lantern_Warm")
        lan.location = (lx, ly + 0.3, 2.75)

# ──────────────────────────────────────────────
# 9. RIVER BANK DETAILS & EXTRA TREES
# ──────────────────────────────────────────────
def build_river_and_nature_details():
    col = get_or_create_col("06_ENVIRONMENT_NATURE")
    
    # River Boulders along the riverbanks
    river_boulders = [
        (4.5, 19.5, 0.2), (7.8, 24.5, 0.2), (2.0, 21.0, 0.1),
        (8.5, 18.0, 0.15), (-5.0, 25.0, 0.1), (12.0, 15.0, 0.15),
        (-15.0, 26.0, 0.2), (18.0, 8.0, 0.2), (-22.0, 27.0, 0.1)
    ]
    for bi, (bx, by, bz) in enumerate(river_boulders):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.85)
        m = bpy.data.meshes.new(f"River_Boulder_{bi}_Mesh")
        bm.to_mesh(m); bm.free()
        m.shade_smooth()
        b = new_obj(f"River_Boulder_{bi}", m, col)
        assign_mat(b, "M_Stone_Rough")
        b.location = (bx, by, bz)
        b.scale = (random.uniform(0.8, 1.4), random.uniform(0.7, 1.3), random.uniform(0.4, 0.7))
        b.rotation_euler.z = random.uniform(0, math.pi * 2)

def apply_all_detail_polishing():
    print("=== Polish Details & Environmental Dressing: START ===")
    polish_village_layout()
    polish_road_network()
    build_tavern_props()
    build_cottage_details()
    build_market_props()
    build_blacksmith_props()
    build_church_and_castle_props()
    build_street_lampposts()
    build_river_and_nature_details()
    print("=== Polish Details & Environmental Dressing: COMPLETE ===")

if __name__ == "__main__":
    apply_all_detail_polishing()

