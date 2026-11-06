"""
build_environmental_details.py
==============================
Builds comprehensive small environmental details and prop collections
for the medieval fantasy village based directly on user reference images (Ref 1-5):
  - Ref 1: Wooden barrels, crates, sacks, baskets, pottery jugs, buckets, coiled ropes, market table.
  - Ref 2: Window flower boxes with blooming poppies & trailing ivy, potted ferns, street lanterns, festival bunting.
  - Ref 3: 4-wheeled wooden cargo wagon with spoked wheels, barrels, tarpaulin cover, draught poles, and lantern.
  - Ref 4: Wall-mounted wrought iron bracket lanterns, hanging swinging shop trade signs, atmospheric night glow.
  - Ref 5: Village entrance notice board with pinned proclamations, wooden post-and-rail fences, swing gate, firewood stacks, and chopping block with axe.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
import random
import os
import sys

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import lighting_manager

print("==================================================")
print("   BUILDING SMALL ENVIRONMENTAL PROPS & DETAILS   ")
print("==================================================")

# ── 1. Helpers: Collection & Ground Raycast ────
def get_col(name, parent="03_VILLAGE_STRUCTURES"):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    parent_col = bpy.data.collections.get(parent) or bpy.context.scene.collection
    parent_col.children.link(col)
    return col

col_props = get_col("Village_Environmental_Props", parent="03_VILLAGE_STRUCTURES")
col_mgmt = bpy.data.collections.get("00_MANAGEMENT") or get_col("00_MANAGEMENT")

def get_ground_z(x, y, fallback=0.2):
    terrain = bpy.data.objects.get("Terrain_Village")
    if not terrain:
        return fallback
    ray_origin = Vector((x, y, 60.0))
    ray_dir = Vector((0.0, 0.0, -1.0))
    mw_inv = terrain.matrix_world.inverted()
    orig_local = mw_inv @ ray_origin
    dir_local = mw_inv.to_3x3() @ ray_dir
    success, loc, normal, face_idx = terrain.ray_cast(orig_local, dir_local)
    return (terrain.matrix_world @ loc).z if success else fallback

# ── 2. Materials Setup ─────────────────────────
mat_wood = bpy.data.materials.get("M_Wood_Aged_Oak")
mat_dark_wood = bpy.data.materials.get("M_Wood_Dark_Timber") or mat_wood
mat_iron = bpy.data.materials.get("M_Iron_Wrought")
mat_lantern = bpy.data.materials.get("M_Lantern_Warm")
mat_terracotta = bpy.data.materials.get("M_Clay_Terracotta") or bpy.data.materials.get("M_Ceramic_Glazed")
mat_burlap = bpy.data.materials.get("M_Burlap_Material")
mat_wicker = bpy.data.materials.get("M_Wicker_Material")
mat_rope = bpy.data.materials.get("M_Rope")
mat_firewood = bpy.data.materials.get("M_Firewood_Bark")
mat_parchment = bpy.data.materials.get("M_Parchment_Paper")
mat_tarp = bpy.data.materials.get("M_Wagon_Tarp")
mat_flower_red = bpy.data.materials.get("M_Flower_Poppy_Red")
mat_flower_yellow = bpy.data.materials.get("M_Flower_Yellow")
mat_leaf = bpy.data.materials.get("M_Bush_Leaves_Fresh") or bpy.data.materials.get("M_Oak_Foliage_Green")

# ── 3. MODULE 1: Fences, Gates & Notice Board (Ref 5) ──
def build_fences_and_notice_board():
    print("Building entrance fences, swing gate and village notice board...")
    
    # Clean previous notice board & entrance fence objects
    for o in list(bpy.data.objects):
        if any(o.name.startswith(p) for p in ["Village_Notice_Board", "Entrance_Fence_", "Church_Fence_"]):
            bpy.data.objects.remove(o, do_unlink=True)
            
    # A. Village Notice Board / Bulletin Signboard (Ref 5)
    # Location: (2.8, -36.0), east shoulder of south entrance road
    nb_x, nb_y = 2.8, -36.0
    nb_z = get_ground_z(nb_x, nb_y)
    
    bm_nb = bmesh.new()
    
    # Twin vertical rustic timber posts (H=2.6m, diam=0.16m, spacing 1.8m)
    p_spacing = 1.8
    for px_offset in [-p_spacing*0.5, p_spacing*0.5]:
        p_mat = Matrix.Translation((nb_x + px_offset, nb_y, nb_z + 1.3))
        bmesh.ops.create_cone(bm_nb, cap_ends=True, segments=8, radius1=0.08, radius2=0.07, depth=2.7, matrix=p_mat)
        
    # Horizontal board backing (2.1m x 1.1m x 0.05m) at Z = nb_z + 1.45m
    b_mat = Matrix.Translation((nb_x, nb_y + 0.02, nb_z + 1.45)) @ Matrix.Scale(2.1, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.05, 4, Vector((0, 1, 0))) @ Matrix.Scale(1.1, 4, Vector((0, 0, 1)))
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=b_mat)
    
    # Gabled rooflet overhang (Ref 5)
    # Ridge at Z = nb_z + 2.50m, eaves overhang
    r_mat_l = Matrix.Translation((nb_x, nb_y - 0.18, nb_z + 2.30)) @ Matrix.Rotation(math.radians(35), 4, 'X') @ Matrix.Scale(2.4, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.48, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1)))
    r_mat_r = Matrix.Translation((nb_x, nb_y + 0.18, nb_z + 2.30)) @ Matrix.Rotation(math.radians(-35), 4, 'X') @ Matrix.Scale(2.4, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.48, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1)))
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=r_mat_l)
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=r_mat_r)
    
    # Cantilevered wooden lantern arm extending from left post
    arm_mat = Matrix.Translation((nb_x - p_spacing*0.5 - 0.45, nb_y - 0.25, nb_z + 2.25)) @ Matrix.Scale(0.9, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 0, 1)))
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=arm_mat)
    
    me_nb = bpy.data.meshes.new("Village_Notice_Board_Mesh")
    bm_nb.to_mesh(me_nb)
    bm_nb.free()
    obj_nb = bpy.data.objects.new("Village_Notice_Board", me_nb)
    col_props.objects.link(obj_nb)
    if mat_wood:
        obj_nb.data.materials.append(mat_wood)
        
    # Pinned Parchment Notices (Ref 5)
    bm_notices = bmesh.new()
    notices_data = [
        (-0.60, 0.25, 0.32, 0.42, 3),
        (-0.15, 0.20, 0.28, 0.36, -5),
        (0.25, 0.15, 0.35, 0.45, 2),
        (0.65, -0.15, 0.26, 0.34, -4),
        (-0.45, -0.22, 0.30, 0.38, 6),
        (0.10, -0.25, 0.32, 0.40, -2)
    ]
    for ox, oz, nw, nh, rot_deg in notices_data:
        pos = Vector((nb_x + ox, nb_y - 0.015, nb_z + 1.45 + oz))
        n_mat = Matrix.Translation(pos) @ Matrix.Rotation(math.radians(rot_deg), 4, 'Y') @ Matrix.Scale(nw, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.005, 4, Vector((0, 1, 0))) @ Matrix.Scale(nh, 4, Vector((0, 0, 1)))
        bmesh.ops.create_cube(bm_notices, size=1.0, matrix=n_mat)
        
    me_notices = bpy.data.meshes.new("Notice_Board_Papers_Mesh")
    bm_notices.to_mesh(me_notices)
    bm_notices.free()
    obj_notices = bpy.data.objects.new("Notice_Board_Papers", me_notices)
    col_props.objects.link(obj_notices)
    if mat_parchment:
        obj_notices.data.materials.append(mat_parchment)
        
    # Notice Board Hanging Lantern & Light
    lantern_pos = Vector((nb_x - p_spacing*0.5 - 0.70, nb_y - 0.25, nb_z + 1.95))
    bm_l = bmesh.new()
    bmesh.ops.create_cone(bm_l, cap_ends=True, segments=6, radius1=0.14, radius2=0.02, depth=0.15, matrix=Matrix.Translation(lantern_pos + Vector((0, 0, 0.12))))
    bmesh.ops.create_cone(bm_l, cap_ends=True, segments=6, radius1=0.09, radius2=0.11, depth=0.22, matrix=Matrix.Translation(lantern_pos))
    me_l = bpy.data.meshes.new("Notice_Board_Lantern_Mesh")
    bm_l.to_mesh(me_l)
    bm_l.free()
    obj_nl = bpy.data.objects.new("Notice_Board_Lantern", me_l)
    col_props.objects.link(obj_nl)
    if mat_iron:
        obj_nl.data.materials.append(mat_iron)
        
    pl_data = bpy.data.lights.new("Light_Notice_Board", 'POINT')
    pl_data.energy = 40.0
    pl_data.color = (1.0, 0.75, 0.40)
    obj_pl = bpy.data.objects.new("Light_Notice_Board", pl_data)
    col_props.objects.link(obj_pl)
    obj_pl.location = lantern_pos
    
    # B. Post-and-Rail Boundary Fences flanking South Entrance (Ref 5)
    # Running along Y = -37.0 on East and West sides
    bm_fence = bmesh.new()
    
    # East fence: X = 4.2 to 14.0 (length = 9.8m, 5 posts)
    # West fence: X = -3.8 to -14.0 (length = 10.2m, 5 posts)
    fence_runs = [
        [(4.2, -37.0), (6.6, -37.2), (9.0, -37.1), (11.5, -36.9), (14.0, -36.8)],
        [(-3.8, -37.0), (-6.2, -37.2), (-8.8, -37.1), (-11.4, -36.9), (-14.0, -36.8)]
    ]
    for run in fence_runs:
        post_coords = []
        for fx, fy in run:
            fz = get_ground_z(fx, fy)
            p_mat = Matrix.Translation((fx, fy, fz + 0.65))
            bmesh.ops.create_cone(bm_fence, cap_ends=True, segments=6, radius1=0.07, radius2=0.06, depth=1.35, matrix=p_mat)
            post_coords.append(Vector((fx, fy, fz)))
            
        # 2 Horizontal rails between consecutive posts
        for p_i in range(len(post_coords) - 1):
            p_a = post_coords[p_i]
            p_b = post_coords[p_i + 1]
            seg_vec = p_b - p_a
            seg_len = seg_vec.length
            mid = (p_a + p_b) * 0.5
            rot_z = math.atan2(seg_vec.y, seg_vec.x)
            
            # Lower rail (Z + 0.38) & Upper rail (Z + 0.85)
            for r_z in [0.38, 0.85]:
                r_mat = Matrix.Translation(mid + Vector((0, 0, r_z))) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Scale(seg_len, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.09, 4, Vector((0, 0, 1)))
                bmesh.ops.create_cube(bm_fence, size=1.0, matrix=r_mat)

    # Wooden Swing Gate on East side (at X=3.5, Y=-37.0)
    gate_mat = Matrix.Translation((3.5, -37.0, get_ground_z(3.5, -37.0) + 0.65)) @ Matrix.Rotation(math.radians(25), 4, 'Z')
    # Gate frame (1.2m x 0.08m x 1.0m)
    bmesh.ops.create_cube(bm_fence, size=1.0, matrix=gate_mat @ Matrix.Scale(1.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.95, 4, Vector((0, 0, 1))))
    
    me_fence = bpy.data.meshes.new("Entrance_Boundary_Fences_Mesh")
    bm_fence.to_mesh(me_fence)
    bm_fence.free()
    obj_fence = bpy.data.objects.new("Entrance_Boundary_Fences", me_fence)
    col_props.objects.link(obj_fence)
    if mat_wood:
        obj_fence.data.materials.append(mat_wood)

    print("Notice board and entrance fences completed.")

# ── 4. MODULE 2: Loaded 4-Wheeled Cargo Wagon (Ref 3) ───
def build_loaded_cargo_wagon():
    print("Constructing 4-wheeled loaded medieval cargo wagon...")
    
    old_wagon = bpy.data.objects.get("Village_Cargo_Wagon")
    if old_wagon:
        bpy.data.objects.remove(old_wagon, do_unlink=True)
    for o in list(bpy.data.objects):
        if o.name.startswith("Village_Cargo_Wagon_"):
            bpy.data.objects.remove(o, do_unlink=True)

    # Location: Parked in Market/Tavern avenue at (5.6, -17.8)
    wx, wy = 5.6, -17.8
    wz = get_ground_z(wx, wy) + 0.52
    
    wagon_mat = Matrix.Translation((wx, wy, wz)) @ Matrix.Rotation(math.radians(-15), 4, 'Z')
    
    # ── A. Wagon Timber Bed & Stakes ──────────────
    bm_chassis = bmesh.new()
    
    bed_l = 3.4
    bed_w = 1.6
    bed_h = 0.65
    
    # Main bed floor planks
    bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Scale(bed_l, 4, Vector((1, 0, 0))) @ Matrix.Scale(bed_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    
    # Longitudinal chassis stringers (under floor)
    for sy in [-bed_w*0.35, bed_w*0.35]:
        bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((0, sy, -0.12)) @ Matrix.Scale(bed_l * 1.05, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.14, 4, Vector((0, 0, 1))))
        
    # Vertical side stake posts (4 on each side)
    for si in range(4):
        sx = -bed_l*0.42 + si * (bed_l * 0.84 / 3.0)
        for sy in [-bed_w*0.5, bed_w*0.5]:
            bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((sx, sy, bed_h*0.5)) @ Matrix.Scale(0.08, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @ Matrix.Scale(bed_h, 4, Vector((0, 0, 1))))
            
    # Horizontal slatted sideboards (3 tiers per side)
    for ti in range(3):
        sz = 0.12 + ti * 0.22
        for sy in [-bed_w*0.5, bed_w*0.5]:
            bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((0, sy, sz)) @ Matrix.Scale(bed_l, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.16, 4, Vector((0, 0, 1))))
            
    # Tailgate and frontboard
    bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((-bed_l*0.5, 0, bed_h*0.45)) @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(bed_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(bed_h*0.8, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((bed_l*0.5, 0, bed_h*0.45)) @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(bed_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(bed_h*0.8, 4, Vector((0, 0, 1))))
    
    # Draught hitching poles extending forward (Ref 3)
    for py in [-0.25, 0.25]:
        bmesh.ops.create_cone(bm_chassis, cap_ends=True, segments=6, radius1=0.05, radius2=0.035, depth=2.4, matrix=wagon_mat @ Matrix.Translation((bed_l*0.5 + 1.1, py, -0.15)) @ Matrix.Rotation(math.radians(90), 4, 'Y'))

    me_chassis = bpy.data.meshes.new("Village_Cargo_Wagon_Chassis_Mesh")
    bm_chassis.to_mesh(me_chassis)
    bm_chassis.free()
    obj_chassis = bpy.data.objects.new("Village_Cargo_Wagon_Chassis", me_chassis)
    col_props.objects.link(obj_chassis)
    if mat_wood:
        obj_chassis.data.materials.append(mat_wood)

    # ── B. 4 Spoked Wooden Wheels with Iron Rims (Ref 3) ──
    # Rear wheels: R=0.55m, Front wheels: R=0.42m
    wheel_positions = [
        ("Rear_L", -bed_l*0.32, -bed_w*0.58, 0.0, 0.55),
        ("Rear_R", -bed_l*0.32, bed_w*0.58, 0.0, 0.55),
        ("Front_L", bed_l*0.30, -bed_w*0.56, -0.08, 0.44),
        ("Front_R", bed_l*0.30, bed_w*0.56, -0.08, 0.44),
    ]
    bm_wheels = bmesh.new()
    for w_name, ox, oy, oz, rad in wheel_positions:
        w_center = wagon_mat @ Vector((ox, oy, oz))
        # Hub
        w_trans = wagon_mat @ Matrix.Translation((ox, oy, oz)) @ Matrix.Rotation(math.radians(90), 4, 'X')
        bmesh.ops.create_cone(bm_wheels, cap_ends=True, segments=12, radius1=0.12, radius2=0.12, depth=0.22, matrix=w_trans)
        
        # Outer Iron Tire Rim (tube/torus approximation)
        n_rim = 16
        rim_pts = []
        for k in range(n_rim):
            ang = k * (2 * math.pi / n_rim)
            vx = math.cos(ang) * rad
            vz = math.sin(ang) * rad
            rim_pts.append((vx, vz))
            
        for k in range(n_rim):
            k_next = (k + 1) % n_rim
            rx0, rz0 = rim_pts[k]
            rx1, rz1 = rim_pts[k_next]
            # Rim segment
            bmesh.ops.create_cube(bm_wheels, size=1.0, matrix=w_trans @ Matrix.Translation(((rx0+rx1)*0.5, 0, (rz0+rz1)*0.5)) @ Matrix.Rotation(-k * (2*math.pi/n_rim), 4, 'Y') @ Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(2*rad*math.sin(math.pi/n_rim)*1.05, 4, Vector((0, 0, 1))))
            
        # 8 Spokes
        for s_idx in range(8):
            s_ang = s_idx * (math.pi / 4.0)
            s_mat = w_trans @ Matrix.Rotation(s_ang, 4, 'Y') @ Matrix.Translation((0, 0, rad*0.48)) @ Matrix.Scale(0.04, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(rad*0.85, 4, Vector((0, 0, 1)))
            bmesh.ops.create_cube(bm_wheels, size=1.0, matrix=s_mat)

    me_wheels = bpy.data.meshes.new("Village_Cargo_Wagon_Wheels_Mesh")
    bm_wheels.to_mesh(me_wheels)
    bm_wheels.free()
    obj_wheels = bpy.data.objects.new("Village_Cargo_Wagon_Wheels", me_wheels)
    col_props.objects.link(obj_wheels)
    if mat_iron:
        obj_wheels.data.materials.append(mat_iron)

    # ── C. Loaded Barrels & Canvas Tarpaulin Cover (Ref 3) ──
    bm_cargo = bmesh.new()
    
    # 4 Oak Ale Barrels loaded in wagon bed
    barrel_locs = [
        (-0.85, -0.32, 0.48), (-0.85, 0.32, 0.48),
        (0.20, -0.30, 0.48), (0.20, 0.30, 0.48)
    ]
    for bx, by, bz in barrel_locs:
        b_mat = wagon_mat @ Matrix.Translation((bx, by, bz))
        bmesh.ops.create_cone(bm_cargo, cap_ends=True, segments=12, radius1=0.32, radius2=0.28, depth=0.88, matrix=b_mat)
        
    # Canvas Tarpaulin draped over barrels (Ref 3)
    # Billowing undulating cloth blanket
    tarp_w = 1.55
    tarp_l = 2.4
    t_steps_x = 10
    t_steps_y = 8
    
    tarp_grid = []
    for ti in range(t_steps_x + 1):
        tx = -1.2 + (ti / t_steps_x) * tarp_l
        row = []
        for tj in range(t_steps_y + 1):
            ty = -tarp_w*0.5 + (tj / t_steps_y) * tarp_w
            # Height follows barrels curve
            h_sag = math.cos(tj / t_steps_y * math.pi - math.pi*0.5) * 0.28
            tz = 0.88 + h_sag + math.sin(ti * 0.8) * 0.05
            # Edge drape downward
            if tj == 0 or tj == t_steps_y:
                tz -= 0.38
            if ti == 0 or ti == t_steps_x:
                tz -= 0.32
            pt = wagon_mat @ Vector((tx, ty, tz))
            v = bm_cargo.verts.new(pt)
            row.append(v)
        tarp_grid.append(row)
        
    for ti in range(t_steps_x):
        for tj in range(t_steps_y):
            v0 = tarp_grid[ti][tj]
            v1 = tarp_grid[ti][tj+1]
            v2 = tarp_grid[ti+1][tj+1]
            v3 = tarp_grid[ti+1][tj]
            bm_cargo.faces.new([v0, v1, v2, v3])

    me_cargo = bpy.data.meshes.new("Village_Cargo_Wagon_Cargo_Mesh")
    bm_cargo.to_mesh(me_cargo)
    bm_cargo.free()
    me_cargo.shade_smooth()
    obj_cargo = bpy.data.objects.new("Village_Cargo_Wagon_Cargo", me_cargo)
    col_props.objects.link(obj_cargo)
    if mat_tarp:
        obj_cargo.data.materials.append(mat_tarp)
        
    # D. Oil Lantern mounted on front corner post (Ref 3)
    lantern_loc = wagon_mat @ Vector((bed_l*0.48, bed_w*0.52, bed_h + 0.35))
    bm_wlan = bmesh.new()
    bmesh.ops.create_cone(bm_wlan, cap_ends=True, segments=6, radius1=0.10, radius2=0.08, depth=0.22, matrix=Matrix.Translation(lantern_loc))
    me_wlan = bpy.data.meshes.new("Wagon_Lantern_Mesh")
    bm_wlan.to_mesh(me_wlan)
    bm_wlan.free()
    obj_wlan = bpy.data.objects.new("Wagon_Lantern", me_wlan)
    col_props.objects.link(obj_wlan)
    if mat_iron:
        obj_wlan.data.materials.append(mat_iron)
        
    pl_wagon = bpy.data.lights.new("Light_Wagon_Lantern", 'POINT')
    pl_wagon.energy = 35.0
    pl_wagon.color = (1.0, 0.72, 0.35)
    obj_plw = bpy.data.objects.new("Light_Wagon_Lantern", pl_wagon)
    col_props.objects.link(obj_plw)
    obj_plw.location = lantern_loc

    print("Loaded 4-wheeled cargo wagon created successfully.")

# ── 5. MODULE 3: Hero Market Still-Life Table Vignette (Ref 1) ─
def build_market_table_vignette():
    print("Building hero market table still-life vignette (Ref 1)...")
    
    for o in list(bpy.data.objects):
        if o.name.startswith("Hero_Market_Table_"):
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Location: Under market awning at (-1.8, -20.5)
    tx, ty = -1.8, -20.5
    tz = get_ground_z(tx, ty)
    
    # 1. Heavy Wooden Market Work Table
    bm_tab = bmesh.new()
    tbl_mat = Matrix.Translation((tx, ty, tz + 0.42))
    # Tabletop planks (2.2m x 1.1m x 0.08m)
    bmesh.ops.create_cube(bm_tab, size=1.0, matrix=tbl_mat @ Matrix.Scale(2.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(1.1, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    # 4 Heavy square legs
    for lx in [-0.95, 0.95]:
        for ly in [-0.45, 0.45]:
            bmesh.ops.create_cube(bm_tab, size=1.0, matrix=tbl_mat @ Matrix.Translation((lx, ly, -0.42*0.5)) @ Matrix.Scale(0.12, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.42, 4, Vector((0, 0, 1))))
            
    me_tab = bpy.data.meshes.new("Hero_Market_Table_Wood_Mesh")
    bm_tab.to_mesh(me_tab)
    bm_tab.free()
    obj_tab = bpy.data.objects.new("Hero_Market_Table_Wood", me_tab)
    col_props.objects.link(obj_tab)
    if mat_wood:
        obj_tab.data.materials.append(mat_wood)

    # 2. Tabletop Goods: Barrels, Wicker Baskets, Ceramic Jugs, Buckets & Ropes (Ref 1)
    bm_goods = bmesh.new()
    top_z = tz + 0.46
    
    # A. Standing Oak Barrel (back-left)
    bmesh.ops.create_cone(bm_goods, cap_ends=True, segments=12, radius1=0.28, radius2=0.24, depth=0.72, matrix=Matrix.Translation((tx - 0.75, ty - 0.15, top_z + 0.36)))
    # B. Terracotta Clay Jugs (Ref 1)
    bmesh.ops.create_cone(bm_goods, cap_ends=True, segments=8, radius1=0.14, radius2=0.06, depth=0.34, matrix=Matrix.Translation((tx - 0.35, ty + 0.20, top_z + 0.17)))
    bmesh.ops.create_cone(bm_goods, cap_ends=True, segments=8, radius1=0.10, radius2=0.05, depth=0.24, matrix=Matrix.Translation((tx - 0.15, ty + 0.28, top_z + 0.12)))
    # C. Wicker Baskets (round handled + tall hamper)
    bmesh.ops.create_cone(bm_goods, cap_ends=True, segments=10, radius1=0.18, radius2=0.16, depth=0.22, matrix=Matrix.Translation((tx + 0.35, ty + 0.15, top_z + 0.11)))
    # Tall cylindrical wicker hamper (standing on ground beside table)
    bmesh.ops.create_cone(bm_goods, cap_ends=True, segments=10, radius1=0.22, radius2=0.22, depth=0.85, matrix=Matrix.Translation((tx + 1.25, ty - 0.10, tz + 0.42)))
    # D. Wooden Stave Bucket with rope handle
    bmesh.ops.create_cone(bm_goods, cap_ends=True, segments=8, radius1=0.15, radius2=0.13, depth=0.30, matrix=Matrix.Translation((tx + 0.70, ty - 0.20, top_z + 0.15)))
    # E. Slatted Wooden Produce Crates (stacked on ground)
    bmesh.ops.create_cube(bm_goods, size=1.0, matrix=Matrix.Translation((tx + 1.10, ty + 0.45, tz + 0.16)) @ Matrix.Scale(0.65, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.45, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.32, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_goods, size=1.0, matrix=Matrix.Translation((tx + 1.10, ty + 0.45, tz + 0.48)) @ Matrix.Rotation(math.radians(12), 4, 'Z') @ Matrix.Scale(0.65, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.45, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.32, 4, Vector((0, 0, 1))))
    # F. Coiled Hemp Rope (spiral coil on ground, Ref 1)
    for r_i in range(16):
        r_ang = r_i * 0.4
        r_dist = 0.12 + (r_i % 4) * 0.05
        rx = tx - 0.85 + math.cos(r_ang) * r_dist
        ry = ty + 0.45 + math.sin(r_ang) * r_dist
        bmesh.ops.create_cone(bm_goods, cap_ends=True, segments=4, radius1=0.025, radius2=0.025, depth=0.08, matrix=Matrix.Translation((rx, ry, tz + 0.03)))

    me_goods = bpy.data.meshes.new("Hero_Market_Table_Goods_Mesh")
    bm_goods.to_mesh(me_goods)
    bm_goods.free()
    obj_goods = bpy.data.objects.new("Hero_Market_Table_Goods", me_goods)
    col_props.objects.link(obj_goods)
    if mat_wicker:
        obj_goods.data.materials.append(mat_wicker)

    print("Hero market table vignette complete.")

# ── 6. MODULE 4: Firewood Stacks & Chopping Blocks (Ref 5) ─
def build_firewood_stacks():
    print("Building firewood stacks and chopping block with axe...")
    
    for o in list(bpy.data.objects):
        if o.name.startswith("Village_Firewood_"):
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Stack 1: Beside Tithe Barn (20.5, 17.5)
    # Stack 2: Beside Cottage 2 (-4.8, 4.2)
    stacks = [
        ("Barn_Stack", 20.5, 17.5, 2.6, 0.75, 1.35, 12),
        ("Cottage_Stack", -4.8, 4.2, 2.2, 0.65, 1.20, -75)
    ]
    
    bm_wood = bmesh.new()
    for name, sx, sy, s_len, s_wid, s_h, rot_deg in stacks:
        sz = get_ground_z(sx, sy)
        st_mat = Matrix.Translation((sx, sy, sz)) @ Matrix.Rotation(math.radians(rot_deg), 4, 'Z')
        
        # End vertical stake posts holding wood
        for ex in [-s_len*0.5, s_len*0.5]:
            for ey in [-s_wid*0.5, s_wid*0.5]:
                bmesh.ops.create_cone(bm_wood, cap_ends=True, segments=6, radius1=0.06, radius2=0.05, depth=s_h * 1.15, matrix=st_mat @ Matrix.Translation((ex, ey, s_h*0.55)))
                
        # Split Cordwood Logs (stacked rows)
        n_layers = 7
        logs_per_layer = int(s_len / 0.22)
        log_r = 0.09
        for li in range(n_layers):
            lz = (li + 0.5) * (log_r * 1.7)
            y_jitter = (li % 2) * 0.04
            for lk in range(logs_per_layer):
                lx = -s_len*0.45 + lk * 0.22 + (li % 2)*0.08
                # Cylinder log oriented along Y (length s_wid)
                l_mat = st_mat @ Matrix.Translation((lx, y_jitter, lz)) @ Matrix.Rotation(math.radians(90), 4, 'X')
                bmesh.ops.create_cone(bm_wood, cap_ends=True, segments=6, radius1=log_r, radius2=log_r*0.95, depth=s_wid*0.95, matrix=l_mat)

    # Chopping Block with Embedded Iron Axe (Ref 5)
    cb_x, cb_y = 19.2, 16.5
    cb_z = get_ground_z(cb_x, cb_y)
    cb_mat = Matrix.Translation((cb_x, cb_y, cb_z + 0.35))
    # Tree stump block (H=0.7m, diam=0.6m)
    bmesh.ops.create_cone(bm_wood, cap_ends=True, segments=8, radius1=0.32, radius2=0.28, depth=0.70, matrix=cb_mat)
    
    # Axe Handle (Hickory wood)
    axe_pos = Matrix.Translation((cb_x, cb_y, cb_z + 0.70)) @ Matrix.Rotation(math.radians(25), 4, 'X')
    bmesh.ops.create_cone(bm_wood, cap_ends=True, segments=6, radius1=0.025, radius2=0.02, depth=0.85, matrix=axe_pos @ Matrix.Translation((0, 0, 0.40)))
    # Iron Axe Head
    bmesh.ops.create_cube(bm_wood, size=1.0, matrix=axe_pos @ Matrix.Scale(0.04, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.22, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 0, 1))))

    me_wood = bpy.data.meshes.new("Village_Firewood_Mesh")
    bm_wood.to_mesh(me_wood)
    bm_wood.free()
    obj_wood = bpy.data.objects.new("Village_Firewood_Stacks", me_wood)
    col_props.objects.link(obj_wood)
    if mat_firewood:
        obj_wood.data.materials.append(mat_firewood)

    print("Firewood stacks and chopping block created.")

# ── 7. MODULE 5: Window Flower Boxes, Potted Ferns & Planters (Ref 1 & 2) ──
def build_flower_boxes_and_pots():
    print("Building window flower boxes and terracotta potted plants...")
    
    for o in list(bpy.data.objects):
        if o.name.startswith("Village_Flower_"):
            bpy.data.objects.remove(o, do_unlink=True)

    # 1. Window Flower Planter Boxes (Ref 2 & 4)
    # Mounted beneath cottage and tavern windows
    flower_box_locs = [
        # Main Cottage front windows (X=0, Y=0 area)
        (0.8, -4.6, 2.15, 1.4, 0),
        (-2.2, -4.6, 2.15, 1.4, 0),
        # Tavern front and balcony (X=4.4, Y=-16.8)
        (3.0, -13.5, 2.35, 1.6, 0),
        (5.5, -13.5, 2.35, 1.6, 0),
        (4.2, -13.6, 4.45, 2.2, 0), # upper balcony
        # Cottage 2 (X=-4, Y=4)
        (-3.2, 2.5, 2.25, 1.2, 90),
        # Cottage 3 (X=11.5, Y=13.2)
        (10.5, 12.2, 2.20, 1.4, -30),
    ]
    
    bm_boxes = bmesh.new()
    bm_flowers = bmesh.new()
    
    for bx, by, bz, b_len, b_rot in flower_box_locs:
        rot_mat = Matrix.Rotation(math.radians(b_rot), 4, 'Z')
        box_mat = Matrix.Translation((bx, by, bz)) @ rot_mat
        
        # Wooden planter trough (b_len x 0.28m x 0.22m)
        bmesh.ops.create_cube(bm_boxes, size=1.0, matrix=box_mat @ Matrix.Scale(b_len, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.28, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.22, 4, Vector((0, 0, 1))))
        
        # Dense blossoms & hanging ivy foliage inside box
        n_blossoms = int(b_len / 0.18)
        for fi in range(n_blossoms):
            fx = -b_len*0.45 + fi * 0.18
            f_pos = box_mat @ Vector((fx, 0, 0.12))
            
            # Blossom cluster (red/yellow)
            bmesh.ops.create_cone(bm_flowers, cap_ends=True, segments=5, radius1=0.06, radius2=0.01, depth=0.08, matrix=Matrix.Translation(f_pos))
            # Hanging ivy vine cascading down (Ref 2)
            hang_len = 0.25 + (fi % 3) * 0.15
            for k in range(3):
                h_pos = box_mat @ Vector((fx + (k % 2)*0.03, -0.15, 0.05 - k * (hang_len / 3.0)))
                bmesh.ops.create_cone(bm_flowers, cap_ends=True, segments=4, radius1=0.04, radius2=0.01, depth=0.06, matrix=Matrix.Translation(h_pos))

    me_boxes = bpy.data.meshes.new("Village_Flower_Boxes_Mesh")
    bm_boxes.to_mesh(me_boxes)
    bm_boxes.free()
    obj_boxes = bpy.data.objects.new("Village_Flower_Boxes", me_boxes)
    col_props.objects.link(obj_boxes)
    if mat_wood:
        obj_boxes.data.materials.append(mat_wood)

    me_flowers = bpy.data.meshes.new("Village_Flower_Blossoms_Mesh")
    bm_flowers.to_mesh(me_flowers)
    bm_flowers.free()
    obj_flowers = bpy.data.objects.new("Village_Flower_Blossoms", me_flowers)
    col_props.objects.link(obj_flowers)
    if mat_flower_red:
        obj_flowers.data.materials.append(mat_flower_red)

    # 2. Free-Standing Terracotta Flower Pots with Ferns (Ref 1 & 2)
    pot_locs = [
        # Main Cottage entrance
        (1.8, -4.8), (-1.2, -4.8), (0.2, -5.2),
        # Tavern porch & steps
        (2.8, -14.2), (6.2, -14.2), (4.5, -15.5),
        # Market plaza corners
        (-3.5, -24.5), (3.5, -24.5),
        # Blacksmith porch
        (11.8, -8.5), (14.2, -8.5),
        # Waterfront steps
        (9.8, 18.2), (12.2, 18.2)
    ]
    
    bm_pots = bmesh.new()
    for px, py in pot_locs:
        pz = get_ground_z(px, py)
        pot_mat = Matrix.Translation((px, py, pz + 0.22))
        
        # Terracotta pot body (flared lip)
        bmesh.ops.create_cone(bm_pots, cap_ends=True, segments=8, radius1=0.20, radius2=0.14, depth=0.44, matrix=pot_mat)
        
        # Fern fronds spreading outward (Ref 2)
        for fri in range(6):
            fr_ang = fri * (math.pi / 3.0)
            fr_mat = pot_mat @ Matrix.Translation((0, 0, 0.22)) @ Matrix.Rotation(fr_ang, 4, 'Z') @ Matrix.Rotation(math.radians(35), 4, 'X')
            bmesh.ops.create_cone(bm_pots, cap_ends=True, segments=4, radius1=0.08, radius2=0.01, depth=0.35, matrix=fr_mat @ Matrix.Translation((0, 0, 0.18)))

    me_pots = bpy.data.meshes.new("Village_Flower_Pots_Mesh")
    bm_pots.to_mesh(me_pots)
    bm_pots.free()
    obj_pots = bpy.data.objects.new("Village_Flower_Pots", me_pots)
    col_props.objects.link(obj_pots)
    if mat_terracotta:
        obj_pots.data.materials.append(mat_terracotta)

    print("Flower boxes and potted ferns complete.")

# ── 8. MODULE 6: Hanging Trade Signs & Street Bracket Lanterns (Ref 4) ──
def build_signs_and_bracket_lanterns():
    print("Building hanging trade signs and street bracket lanterns...")
    
    for o in list(bpy.data.objects):
        if o.name.startswith("Village_Sign_") or o.name.startswith("Village_Bracket_Lantern_"):
            bpy.data.objects.remove(o, do_unlink=True)
            
    # 1. Hanging Swinging Trade Signs (Ref 4)
    # A. Tavern Sign ("The Prancing Boar"): mounted on Tavern timber corner at (2.4, -14.8, 3.8)
    # B. Blacksmith Anvil Sign: mounted at (12.2, -8.5, 3.2)
    signs = [
        ("Tavern_Sign", 2.4, -14.8, 3.8, 0.9, 0.65, "SHIELD"),
        ("Smith_Sign", 12.2, -8.5, 3.2, 0.75, 0.55, "ANVIL")
    ]
    
    bm_signs = bmesh.new()
    for name, sx, sy, sz, sw, sh, s_type in signs:
        # Wrought iron scrollwork bracket extending from wall
        b_mat = Matrix.Translation((sx, sy, sz))
        # Horizontal iron arm (L=1.1m)
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=b_mat @ Matrix.Translation((0.55, 0, 0)) @ Matrix.Scale(1.1, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.05, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.05, 4, Vector((0, 0, 1))))
        # Diagonal scrolled support strut
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=b_mat @ Matrix.Translation((0.45, 0, -0.35)) @ Matrix.Rotation(math.radians(-40), 4, 'Y') @ Matrix.Scale(0.9, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))))
        
        # Hanging chains (2 links)
        for cx_off in [0.35, 0.85]:
            bmesh.ops.create_cone(bm_signs, cap_ends=True, segments=4, radius1=0.015, radius2=0.015, depth=0.20, matrix=b_mat @ Matrix.Translation((cx_off, 0, -0.12)))
            
        # Hanging Sign Board
        sign_board_mat = b_mat @ Matrix.Translation((0.60, 0, -0.55))
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=sign_board_mat @ Matrix.Scale(sw, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(sh, 4, Vector((0, 0, 1))))
        
        # Decorative rim molding
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=sign_board_mat @ Matrix.Scale(sw*1.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @ Matrix.Scale(sh*1.06, 4, Vector((0, 0, 1))))

    me_signs = bpy.data.meshes.new("Village_Trade_Signs_Mesh")
    bm_signs.to_mesh(me_signs)
    bm_signs.free()
    obj_signs = bpy.data.objects.new("Village_Trade_Signs", me_signs)
    col_props.objects.link(obj_signs)
    if mat_wood:
        obj_signs.data.materials.append(mat_wood)

    # 2. Wall-Mounted Wrought Iron Bracket Lanterns (Ref 4)
    # Mounted on cottage corners and under overhanging timber jetties
    lantern_mounts = [
        ("Tavern_Corner", 2.2, -14.2, 2.9, -1, 0),
        ("Main_Cottage_Porch", 0.6, -4.8, 2.7, 0, -1),
        ("Blacksmith_Corner", 12.6, -9.2, 2.7, 1, 0),
        ("Cottage_2_Corner", -3.6, 2.8, 2.8, -1, 0),
        ("Cottage_3_Street", 10.2, 11.8, 2.7, 1, 0),
        ("Bridge_Approach", 3.8, 16.5, 2.5, -1, 0)
    ]
    
    bm_blan = bmesh.new()
    for name, lx, ly, lz, dx, dy in lantern_mounts:
        mount_mat = Matrix.Translation((lx, ly, lz))
        rot_ang = math.atan2(dy, dx)
        # Scrolled iron bracket extending from wall
        bmesh.ops.create_cube(bm_blan, size=1.0, matrix=mount_mat @ Matrix.Rotation(rot_ang, 4, 'Z') @ Matrix.Translation((0.25, 0, 0)) @ Matrix.Scale(0.50, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))))
        
        # Hexagonal lantern cage (Ref 4)
        l_pos = Vector((lx + dx * 0.45, ly + dy * 0.45, lz - 0.15))
        bmesh.ops.create_cone(bm_blan, cap_ends=True, segments=6, radius1=0.14, radius2=0.03, depth=0.14, matrix=Matrix.Translation(l_pos + Vector((0, 0, 0.16))))
        bmesh.ops.create_cone(bm_blan, cap_ends=True, segments=6, radius1=0.09, radius2=0.12, depth=0.24, matrix=Matrix.Translation(l_pos))
        
        # Point light inside lantern
        pl_data = bpy.data.lights.new(f"Light_Bracket_{name}", 'POINT')
        pl_data.energy = 42.0
        pl_data.color = (1.0, 0.74, 0.38)
        pl_data.shadow_soft_size = 0.15
        obj_pl = bpy.data.objects.new(f"Light_Bracket_{name}", pl_data)
        col_props.objects.link(obj_pl)
        obj_pl.location = l_pos

    me_blan = bpy.data.meshes.new("Village_Bracket_Lanterns_Mesh")
    bm_blan.to_mesh(me_blan)
    bm_blan.free()
    obj_blan = bpy.data.objects.new("Village_Bracket_Lanterns", me_blan)
    col_props.objects.link(obj_blan)
    if mat_iron:
        obj_blan.data.materials.append(mat_iron)

    print("Hanging trade signs and bracket lanterns completed.")

# ── 9. MODULE 7: Colorful Festival Bunting Flags (Ref 2) ──
def build_festival_bunting():
    print("Building festival bunting flag garlands across main street (Ref 2)...")
    
    for o in list(bpy.data.objects):
        if o.name.startswith("Village_Bunting_"):
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Catenary rope lines across the street:
    # Line 1: Tavern upper gable to across the street
    # Line 2: Main cottage to opposite workshop
    lines = [
        (Vector((2.8, -13.5, 4.6)), Vector((-2.2, -14.2, 4.4))),
        (Vector((3.2, -4.5, 4.8)), Vector((8.5, -5.2, 4.6)))
    ]
    
    bm_bunt = bmesh.new()
    for p0, p1 in lines:
        seg_vec = p1 - p0
        seg_len = seg_vec.length
        n_flags = int(seg_len / 0.45)
        
        for fi in range(n_flags):
            t0 = fi / n_flags
            t1 = (fi + 0.8) / n_flags
            
            # Catenary sag in center
            sag0 = math.sin(t0 * math.pi) * 0.45
            sag1 = math.sin(t1 * math.pi) * 0.45
            
            pt_a = p0 + seg_vec * t0 - Vector((0, 0, sag0))
            pt_b = p0 + seg_vec * t1 - Vector((0, 0, sag1))
            pt_tip = (pt_a + pt_b) * 0.5 - Vector((0, 0, 0.32)) # downward triangle point
            
            va = bm_bunt.verts.new(pt_a)
            vb = bm_bunt.verts.new(pt_b)
            vt = bm_bunt.verts.new(pt_tip)
            bm_bunt.faces.new([va, vb, vt])

    me_bunt = bpy.data.meshes.new("Village_Bunting_Flags_Mesh")
    bm_bunt.to_mesh(me_bunt)
    bm_bunt.free()
    obj_bunt = bpy.data.objects.new("Village_Bunting_Flags", me_bunt)
    col_props.objects.link(obj_bunt)
    if mat_flower_red:
        obj_bunt.data.materials.append(mat_flower_red)

    print("Festival bunting garlands complete.")

# ── 10. MODULE 8: Cinematic Showcase Cameras ───
def setup_environmental_cameras():
    print("Setting up showcase cameras for small environmental details...")
    
    def make_cam(name, loc, target, lens=35.0):
        if name in bpy.data.objects:
            cam_obj = bpy.data.objects[name]
        else:
            cdata = bpy.data.cameras.new(name)
            cam_obj = bpy.data.objects.new(name, cdata)
            col_mgmt.objects.link(cam_obj)
        cam_obj.location = Vector(loc)
        cam_obj.data.lens = lens
        cam_obj.data.clip_start = 0.2
        cam_obj.data.clip_end = 2500.0
        dir_v = Vector(target) - Vector(loc)
        cam_obj.rotation_euler = dir_v.to_track_quat('-Z', 'Y').to_euler()
        return cam_obj

    cams = {}
    
    # 1. Cam_Street_Life_Hero (Ref 2 & 4): Looking down the main street at flower boxes, lanterns, bunting, cottages
    cams["Cam_Street_Life_Hero"] = make_cam(
        "Cam_Street_Life_Hero",
        loc=(2.5, -11.5, 1.65),
        target=(3.8, -16.5, 2.20),
        lens=28.0
    )
    
    # 2. Cam_Wagon_Market_Hero (Ref 3): Hero close-up of 4-wheeled loaded cargo wagon in market square
    cams["Cam_Wagon_Market_Hero"] = make_cam(
        "Cam_Wagon_Market_Hero",
        loc=(8.8, -15.5, 1.45),
        target=(5.6, -17.8, 0.85),
        lens=36.0
    )
    
    # 3. Cam_Props_Table_StillLife (Ref 1): Still-life showcase of market work table, barrels, crates, baskets, jugs, ropes
    cams["Cam_Props_Table_StillLife"] = make_cam(
        "Cam_Props_Table_StillLife",
        loc=(-1.8, -18.8, 1.25),
        target=(-1.8, -20.5, 0.65),
        lens=42.0
    )
    
    # 4. Cam_Village_Entrance_NoticeBoard (Ref 5): South entrance showing notice board, fences, gate, firewood stack, lantern
    cams["Cam_Village_Entrance_NoticeBoard"] = make_cam(
        "Cam_Village_Entrance_NoticeBoard",
        loc=(0.5, -39.5, 1.60),
        target=(2.8, -36.0, 1.40),
        lens=32.0
    )

    print("All 4 environmental showcase cameras configured.")
    return cams

def run_build_environmental_details():
    # ── Master Execution ───────────────────────────
    build_fences_and_notice_board()
    build_loaded_cargo_wagon()
    build_market_table_vignette()
    build_firewood_stacks()
    build_flower_boxes_and_pots()
    build_signs_and_bracket_lanterns()
    build_festival_bunting()
    cams = setup_environmental_cameras()

    print("==================================================")
    print("ENVIRONMENTAL DETAILS & PROPS COMPLETE!")
    print("==================================================")
    return cams

if __name__ == "__main__":
    run_build_environmental_details()

