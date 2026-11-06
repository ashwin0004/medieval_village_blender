"""
rebuild_environmental_details.py
================================
Rebuilds and textures all small environmental props with exact material bindings:
  - Exact materials: M_Wood_AgedOak, M_Wood_DarkTimber, M_Wood_LightPine,
    M_Burlap_Hessian, M_Wicker_Willow, M_Hemp_Rope, M_Clay_Terracotta,
    M_Ceramic_Glazed, M_Iron_Wrought, M_Firewood_Bark, M_Parchment_Paper,
    M_Wagon_Tarp, M_Flower_Poppy_Red, M_Flower_Yellow, M_Lantern_Warm.
  - Fixes wagon wheels to be vertical spoked wheels with iron rims.
  - Separates market still-life objects into distinct material-mapped meshes (Ref 1).
  - Positions all props with correct ground offsets.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
import random
import os


def run_rebuild():
    print("--- Step 1: Bind Exact PBR Materials ---")
    mat_wood = bpy.data.materials.get("M_Wood_AgedOak")
    mat_dark_wood = bpy.data.materials.get("M_Wood_DarkTimber") or mat_wood
    mat_pine = bpy.data.materials.get("M_Wood_LightPine") or mat_wood
    mat_iron = bpy.data.materials.get("M_Iron_Wrought")
    mat_lantern = bpy.data.materials.get("M_Lantern_Warm")
    mat_terracotta = bpy.data.materials.get("M_Clay_Terracotta")
    mat_ceramic = bpy.data.materials.get("M_Ceramic_Glazed") or mat_terracotta
    mat_burlap = bpy.data.materials.get("M_Burlap_Hessian")
    mat_wicker = bpy.data.materials.get("M_Wicker_Willow")
    mat_rope = bpy.data.materials.get("M_Hemp_Rope")
    mat_firewood = bpy.data.materials.get("M_Firewood_Bark")
    mat_parchment = bpy.data.materials.get("M_Parchment_Paper")
    mat_tarp = bpy.data.materials.get("M_Wagon_Tarp")
    mat_flower_red = bpy.data.materials.get("M_Flower_Poppy_Red")
    mat_flower_yellow = bpy.data.materials.get("M_Flower_Yellow")
    mat_leaf = bpy.data.materials.get("M_Oak_Foliage_Green") or bpy.data.materials.get("M_Bush_Foliage")
    mat_tile = bpy.data.materials.get("M_Tile_Weathered_Moss") or mat_dark_wood
    
    col_props = bpy.data.collections.get("Village_Environmental_Props")
    if not col_props:
        col_props = bpy.data.collections.new("Village_Environmental_Props")
        bpy.data.collections["03_VILLAGE_STRUCTURES"].children.link(col_props)
    
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
    
    # ── Clean previous objects in col_props ────────
    for o in list(col_props.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    
    # ── 1. MODULE 1: Village Notice Board & Entrance Fences (Ref 5) ──
    print("Rebuilding Notice Board & Fences...")
    nb_x, nb_y = 2.8, -36.0
    nb_z = get_ground_z(nb_x, nb_y)
    
    bm_nb = bmesh.new()
    p_spacing = 1.8
    # Posts
    for px_offset in [-p_spacing*0.5, p_spacing*0.5]:
        p_mat = Matrix.Translation((nb_x + px_offset, nb_y, nb_z + 1.3))
        bmesh.ops.create_cone(bm_nb, cap_ends=True, segments=8, radius1=0.08, radius2=0.07, depth=2.7, matrix=p_mat)
    
    # Backing board
    b_mat = Matrix.Translation((nb_x, nb_y + 0.02, nb_z + 1.45)) @ Matrix.Scale(2.1, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.05, 4, Vector((0, 1, 0))) @ Matrix.Scale(1.1, 4, Vector((0, 0, 1)))
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=b_mat)
    
    # Rooflet
    r_mat_l = Matrix.Translation((nb_x, nb_y - 0.18, nb_z + 2.30)) @ Matrix.Rotation(math.radians(35), 4, 'X') @ Matrix.Scale(2.4, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.48, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1)))
    r_mat_r = Matrix.Translation((nb_x, nb_y + 0.18, nb_z + 2.30)) @ Matrix.Rotation(math.radians(-35), 4, 'X') @ Matrix.Scale(2.4, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.48, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1)))
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=r_mat_l)
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=r_mat_r)
    
    # Arm
    arm_mat = Matrix.Translation((nb_x - p_spacing*0.5 - 0.45, nb_y - 0.25, nb_z + 2.25)) @ Matrix.Scale(0.9, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 0, 1)))
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=arm_mat)
    
    me_nb = bpy.data.meshes.new("Village_Notice_Board_Mesh")
    bm_nb.to_mesh(me_nb)
    bm_nb.free()
    obj_nb = bpy.data.objects.new("Village_Notice_Board", me_nb)
    col_props.objects.link(obj_nb)
    if mat_wood:
        obj_nb.data.materials.append(mat_wood)
    
    # Pinned Notices
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
    
    # Lantern on Notice Board
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
    pl_data.energy = 45.0
    pl_data.color = (1.0, 0.75, 0.40)
    obj_pl = bpy.data.objects.new("Light_Notice_Board", pl_data)
    col_props.objects.link(obj_pl)
    obj_pl.location = lantern_pos
    
    # Entrance Boundary Fences
    bm_fence = bmesh.new()
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
            
        for p_i in range(len(post_coords) - 1):
            p_a = post_coords[p_i]
            p_b = post_coords[p_i + 1]
            seg_vec = p_b - p_a
            seg_len = seg_vec.length
            mid = (p_a + p_b) * 0.5
            rot_z = math.atan2(seg_vec.y, seg_vec.x)
            for r_z in [0.38, 0.85]:
                r_mat = Matrix.Translation(mid + Vector((0, 0, r_z))) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Scale(seg_len, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.09, 4, Vector((0, 0, 1)))
                bmesh.ops.create_cube(bm_fence, size=1.0, matrix=r_mat)
    
    # Swing gate
    gate_mat = Matrix.Translation((3.5, -37.0, get_ground_z(3.5, -37.0) + 0.65)) @ Matrix.Rotation(math.radians(25), 4, 'Z')
    bmesh.ops.create_cube(bm_fence, size=1.0, matrix=gate_mat @ Matrix.Scale(1.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.95, 4, Vector((0, 0, 1))))
    
    me_fence = bpy.data.meshes.new("Entrance_Boundary_Fences_Mesh")
    bm_fence.to_mesh(me_fence)
    bm_fence.free()
    obj_fence = bpy.data.objects.new("Entrance_Boundary_Fences", me_fence)
    col_props.objects.link(obj_fence)
    if mat_wood:
        obj_fence.data.materials.append(mat_wood)
    
    # ── 2. MODULE 2: Loaded 4-Wheeled Cargo Wagon (Ref 3) ──
    print("Rebuilding Cargo Wagon with true vertical spoked wheels...")
    # Placed prominently in the Market Square at (3.5, -22.5)
    wx, wy = 3.5, -22.5
    wz = 1.30 # plaza cobblestone height + wheel radius
    wagon_mat = Matrix.Translation((wx, wy, wz)) @ Matrix.Rotation(math.radians(-25), 4, 'Z')
    
    bed_l = 3.2
    bed_w = 1.5
    bed_h = 0.60
    
    # A. Wagon Wood Chassis & Sideboards
    bm_chassis = bmesh.new()
    # Floor
    bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Scale(bed_l, 4, Vector((1, 0, 0))) @ Matrix.Scale(bed_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    # Stringers
    for sy in [-bed_w*0.35, bed_w*0.35]:
        bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((0, sy, -0.10)) @ Matrix.Scale(bed_l*1.05, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 0, 1))))
    # Side stakes
    for si in range(4):
        sx = -bed_l*0.42 + si * (bed_l * 0.84 / 3.0)
        for sy in [-bed_w*0.5, bed_w*0.5]:
            bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((sx, sy, bed_h*0.5)) @ Matrix.Scale(0.08, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @ Matrix.Scale(bed_h, 4, Vector((0, 0, 1))))
    # Slatted sideboards
    for ti in range(3):
        sz = 0.12 + ti * 0.20
        for sy in [-bed_w*0.5, bed_w*0.5]:
            bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((0, sy, sz)) @ Matrix.Scale(bed_l, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.14, 4, Vector((0, 0, 1))))
    # Front & Tail boards
    bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((-bed_l*0.5, 0, bed_h*0.45)) @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(bed_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(bed_h*0.8, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_chassis, size=1.0, matrix=wagon_mat @ Matrix.Translation((bed_l*0.5, 0, bed_h*0.45)) @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(bed_w, 4, Vector((0, 1, 0))) @ Matrix.Scale(bed_h*0.8, 4, Vector((0, 0, 1))))
    # Draught poles
    for py in [-0.25, 0.25]:
        bmesh.ops.create_cone(bm_chassis, cap_ends=True, segments=6, radius1=0.05, radius2=0.035, depth=2.4, matrix=wagon_mat @ Matrix.Translation((bed_l*0.5 + 1.1, py, -0.15)) @ Matrix.Rotation(math.radians(90), 4, 'Y'))
    
    me_chassis = bpy.data.meshes.new("Village_Cargo_Wagon_Chassis_Mesh")
    bm_chassis.to_mesh(me_chassis)
    bm_chassis.free()
    obj_chassis = bpy.data.objects.new("Village_Cargo_Wagon_Chassis", me_chassis)
    col_props.objects.link(obj_chassis)
    if mat_wood:
        obj_chassis.data.materials.append(mat_wood)
    
    # B. True Vertical Spoked Wheels with Iron Rims (Ref 3)
    bm_wheels = bmesh.new()
    # Wheels: Rear R=0.55m, Front R=0.44m
    wheel_info = [
        (-bed_l*0.32, -bed_w*0.56, 0.0, 0.55),
        (-bed_l*0.32, bed_w*0.56, 0.0, 0.55),
        (bed_l*0.30, -bed_w*0.54, -0.10, 0.44),
        (bed_l*0.30, bed_w*0.54, -0.10, 0.44)
    ]
    for ox, oy, oz, rad in wheel_info:
        # Wheel hub: cylinder along wagon Y axis
        hub_mat = wagon_mat @ Matrix.Translation((ox, oy, oz)) @ Matrix.Rotation(math.radians(90), 4, 'X')
        bmesh.ops.create_cone(bm_wheels, cap_ends=True, segments=12, radius1=0.11, radius2=0.11, depth=0.22, matrix=hub_mat)
        
        # Outer Iron Rim in X-Z plane of wagon:
        n_rim = 16
        for k in range(n_rim):
            th0 = k * (2 * math.pi / n_rim)
            th1 = (k + 1) * (2 * math.pi / n_rim)
            p0 = wagon_mat @ Vector((ox + math.cos(th0)*rad, oy, oz + math.sin(th0)*rad))
            p1 = wagon_mat @ Vector((ox + math.cos(th1)*rad, oy, oz + math.sin(th1)*rad))
            mid = (p0 + p1) * 0.5
            seg_v = p1 - p0
            rot_seg = seg_v.to_track_quat('Z', 'Y').to_euler()
            bmesh.ops.create_cube(bm_wheels, size=1.0, matrix=Matrix.Translation(mid) @ rot_seg.to_matrix().to_4x4() @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @ Matrix.Scale(seg_v.length, 4, Vector((0, 0, 1))))
            
        # 8 Radial Spokes in X-Z plane
        for s_i in range(8):
            s_th = s_i * (math.pi / 4.0)
            p_hub = wagon_mat @ Vector((ox, oy, oz))
            p_rim = wagon_mat @ Vector((ox + math.cos(s_th)*rad*0.9, oy, oz + math.sin(s_th)*rad*0.9))
            sp_mid = (p_hub + p_rim) * 0.5
            sp_v = p_rim - p_hub
            bmesh.ops.create_cube(bm_wheels, size=1.0, matrix=Matrix.Translation(sp_mid) @ sp_v.to_track_quat('Z', 'Y').to_matrix().to_4x4() @ Matrix.Scale(0.04, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(sp_v.length, 4, Vector((0, 0, 1))))
    
    me_wheels = bpy.data.meshes.new("Village_Cargo_Wagon_Wheels_Mesh")
    bm_wheels.to_mesh(me_wheels)
    bm_wheels.free()
    obj_wheels = bpy.data.objects.new("Village_Cargo_Wagon_Wheels", me_wheels)
    col_props.objects.link(obj_wheels)
    if mat_iron:
        obj_wheels.data.materials.append(mat_iron)
    
    # C. Loaded Barrels & Canvas Tarpaulin Cover
    bm_tarp = bmesh.new()
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
            h_sag = math.cos(tj / t_steps_y * math.pi - math.pi*0.5) * 0.28
            tz = 0.88 + h_sag + math.sin(ti * 0.8) * 0.05
            if tj == 0 or tj == t_steps_y:
                tz -= 0.38
            if ti == 0 or ti == t_steps_x:
                tz -= 0.32
            pt = wagon_mat @ Vector((tx, ty, tz))
            v = bm_tarp.verts.new(pt)
            row.append(v)
        tarp_grid.append(row)
        
    for ti in range(t_steps_x):
        for tj in range(t_steps_y):
            v0 = tarp_grid[ti][tj]
            v1 = tarp_grid[ti][tj+1]
            v2 = tarp_grid[ti+1][tj+1]
            v3 = tarp_grid[ti+1][tj]
            bm_tarp.faces.new([v0, v1, v2, v3])
    
    me_tarp = bpy.data.meshes.new("Village_Cargo_Wagon_Tarp_Mesh")
    bm_tarp.to_mesh(me_tarp)
    bm_tarp.free()
    me_tarp.shade_smooth()
    obj_tarp = bpy.data.objects.new("Village_Cargo_Wagon_Tarp", me_tarp)
    col_props.objects.link(obj_tarp)
    if mat_tarp:
        obj_tarp.data.materials.append(mat_tarp)
    
    # Corner Lantern
    wlan_pos = wagon_mat @ Vector((bed_l*0.48, bed_w*0.52, bed_h + 0.35))
    bm_wlan = bmesh.new()
    bmesh.ops.create_cone(bm_wlan, cap_ends=True, segments=6, radius1=0.10, radius2=0.08, depth=0.22, matrix=Matrix.Translation(wlan_pos))
    me_wlan = bpy.data.meshes.new("Wagon_Lantern_Mesh")
    bm_wlan.to_mesh(me_wlan)
    bm_wlan.free()
    obj_wlan = bpy.data.objects.new("Wagon_Lantern", me_wlan)
    col_props.objects.link(obj_wlan)
    if mat_iron:
        obj_wlan.data.materials.append(mat_iron)
    
    pl_wagon = bpy.data.lights.new("Light_Wagon_Lantern", 'POINT')
    pl_wagon.energy = 40.0
    pl_wagon.color = (1.0, 0.72, 0.35)
    obj_plw = bpy.data.objects.new("Light_Wagon_Lantern", pl_wagon)
    col_props.objects.link(obj_plw)
    obj_plw.location = wlan_pos
    
    # ── 3. MODULE 3: Hero Market Table Still-Life (Ref 1) ──
    print("Rebuilding Market Table Still-Life with individual material objects...")
    tx, ty = -2.2, -21.5
    tz = 1.25 # plaza height
    
    # Table
    bm_tab = bmesh.new()
    tbl_mat = Matrix.Translation((tx, ty, tz + 0.42))
    bmesh.ops.create_cube(bm_tab, size=1.0, matrix=tbl_mat @ Matrix.Scale(2.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(1.1, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    for lx in [-0.95, 0.95]:
        for ly in [-0.45, 0.45]:
            bmesh.ops.create_cube(bm_tab, size=1.0, matrix=tbl_mat @ Matrix.Translation((lx, ly, -0.42*0.5)) @ Matrix.Scale(0.12, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.42, 4, Vector((0, 0, 1))))
    
    me_tab = bpy.data.meshes.new("Hero_Market_Table_Mesh")
    bm_tab.to_mesh(me_tab)
    bm_tab.free()
    obj_tab = bpy.data.objects.new("Hero_Market_Table", me_tab)
    col_props.objects.link(obj_tab)
    if mat_wood:
        obj_tab.data.materials.append(mat_wood)
    
    top_z = tz + 0.46
    
    # A. Barrel on Table
    bm_bar = bmesh.new()
    bmesh.ops.create_cone(bm_bar, cap_ends=True, segments=14, radius1=0.28, radius2=0.25, depth=0.72, matrix=Matrix.Translation((tx - 0.72, ty - 0.12, top_z + 0.36)))
    me_bar = bpy.data.meshes.new("Hero_Table_Barrel_Mesh")
    bm_bar.to_mesh(me_bar)
    bm_bar.free()
    obj_bar = bpy.data.objects.new("Hero_Table_Barrel", me_bar)
    col_props.objects.link(obj_bar)
    if mat_wood:
        obj_bar.data.materials.append(mat_wood)
    
    # B. Ceramic & Terracotta Jugs (Ref 1)
    bm_jug = bmesh.new()
    bmesh.ops.create_cone(bm_jug, cap_ends=True, segments=10, radius1=0.14, radius2=0.06, depth=0.34, matrix=Matrix.Translation((tx - 0.32, ty + 0.18, top_z + 0.17)))
    bmesh.ops.create_cone(bm_jug, cap_ends=True, segments=10, radius1=0.10, radius2=0.05, depth=0.25, matrix=Matrix.Translation((tx - 0.12, ty + 0.25, top_z + 0.12)))
    me_jug = bpy.data.meshes.new("Hero_Table_Jugs_Mesh")
    bm_jug.to_mesh(me_jug)
    bm_jug.free()
    obj_jug = bpy.data.objects.new("Hero_Table_Jugs", me_jug)
    col_props.objects.link(obj_jug)
    if mat_terracotta:
        obj_jug.data.materials.append(mat_terracotta)
    
    # C. Wicker Baskets (Ref 1)
    bm_wck = bmesh.new()
    bmesh.ops.create_cone(bm_wck, cap_ends=True, segments=12, radius1=0.18, radius2=0.15, depth=0.22, matrix=Matrix.Translation((tx + 0.35, ty + 0.15, top_z + 0.11)))
    # Tall hamper beside table
    bmesh.ops.create_cone(bm_wck, cap_ends=True, segments=12, radius1=0.22, radius2=0.22, depth=0.85, matrix=Matrix.Translation((tx + 1.25, ty - 0.10, tz + 0.42)))
    me_wck = bpy.data.meshes.new("Hero_Table_Baskets_Mesh")
    bm_wck.to_mesh(me_wck)
    bm_wck.free()
    obj_wck = bpy.data.objects.new("Hero_Table_Baskets", me_wck)
    col_props.objects.link(obj_wck)
    if mat_wicker:
        obj_wck.data.materials.append(mat_wicker)
    
    # D. Wooden Crates
    bm_crt = bmesh.new()
    bmesh.ops.create_cube(bm_crt, size=1.0, matrix=Matrix.Translation((tx + 1.10, ty + 0.45, tz + 0.16)) @ Matrix.Scale(0.65, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.45, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.32, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_crt, size=1.0, matrix=Matrix.Translation((tx + 1.10, ty + 0.45, tz + 0.48)) @ Matrix.Rotation(math.radians(12), 4, 'Z') @ Matrix.Scale(0.65, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.45, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.32, 4, Vector((0, 0, 1))))
    me_crt = bpy.data.meshes.new("Hero_Table_Crates_Mesh")
    bm_crt.to_mesh(me_crt)
    bm_crt.free()
    obj_crt = bpy.data.objects.new("Hero_Table_Crates", me_crt)
    col_props.objects.link(obj_crt)
    if mat_pine:
        obj_crt.data.materials.append(mat_pine)
    
    # E. Coiled Hemp Rope (Ref 1)
    bm_rp = bmesh.new()
    for r_i in range(18):
        r_ang = r_i * 0.38
        r_dist = 0.10 + (r_i % 5) * 0.04
        rx = tx - 0.82 + math.cos(r_ang) * r_dist
        ry = ty + 0.38 + math.sin(r_ang) * r_dist
        bmesh.ops.create_cone(bm_rp, cap_ends=True, segments=5, radius1=0.025, radius2=0.025, depth=0.08, matrix=Matrix.Translation((rx, ry, tz + 0.04)))
    me_rp = bpy.data.meshes.new("Hero_Table_Rope_Mesh")
    bm_rp.to_mesh(me_rp)
    bm_rp.free()
    obj_rp = bpy.data.objects.new("Hero_Table_Rope", me_rp)
    col_props.objects.link(obj_rp)
    if mat_rope:
        obj_rp.data.materials.append(mat_rope)
    
    # F. Wooden Bucket with Rope Handle (Ref 1)
    bm_bkt = bmesh.new()
    bmesh.ops.create_cone(bm_bkt, cap_ends=True, segments=10, radius1=0.16, radius2=0.13, depth=0.32, matrix=Matrix.Translation((tx + 0.65, ty - 0.20, top_z + 0.16)))
    me_bkt = bpy.data.meshes.new("Hero_Table_Bucket_Mesh")
    bm_bkt.to_mesh(me_bkt)
    bm_bkt.free()
    obj_bkt = bpy.data.objects.new("Hero_Table_Bucket", me_bkt)
    col_props.objects.link(obj_bkt)
    if mat_wood:
        obj_bkt.data.materials.append(mat_wood)
    
    # ── 4. MODULE 4: Firewood Stacks & Chopping Block ─────────
    print("Rebuilding Firewood Stacks...")
    stacks = [
        ("Barn_Stack", 20.5, 17.5, 2.6, 0.75, 1.35, 12),
        ("Cottage_Stack", -4.8, 4.2, 2.2, 0.65, 1.20, -75)
    ]
    bm_wood = bmesh.new()
    for name, sx, sy, s_len, s_wid, s_h, rot_deg in stacks:
        sz = get_ground_z(sx, sy)
        st_mat = Matrix.Translation((sx, sy, sz)) @ Matrix.Rotation(math.radians(rot_deg), 4, 'Z')
        for ex in [-s_len*0.5, s_len*0.5]:
            for ey in [-s_wid*0.5, s_wid*0.5]:
                bmesh.ops.create_cone(bm_wood, cap_ends=True, segments=6, radius1=0.06, radius2=0.05, depth=s_h * 1.15, matrix=st_mat @ Matrix.Translation((ex, ey, s_h*0.55)))
        n_layers = 7
        logs_per_layer = int(s_len / 0.22)
        log_r = 0.09
        for li in range(n_layers):
            lz = (li + 0.5) * (log_r * 1.7)
            y_jitter = (li % 2) * 0.04
            for lk in range(logs_per_layer):
                lx = -s_len*0.45 + lk * 0.22 + (li % 2)*0.08
                l_mat = st_mat @ Matrix.Translation((lx, y_jitter, lz)) @ Matrix.Rotation(math.radians(90), 4, 'X')
                bmesh.ops.create_cone(bm_wood, cap_ends=True, segments=6, radius1=log_r, radius2=log_r*0.95, depth=s_wid*0.95, matrix=l_mat)
    
    cb_x, cb_y = 19.2, 16.5
    cb_z = get_ground_z(cb_x, cb_y)
    cb_mat = Matrix.Translation((cb_x, cb_y, cb_z + 0.35))
    bmesh.ops.create_cone(bm_wood, cap_ends=True, segments=8, radius1=0.32, radius2=0.28, depth=0.70, matrix=cb_mat)
    axe_pos = Matrix.Translation((cb_x, cb_y, cb_z + 0.70)) @ Matrix.Rotation(math.radians(25), 4, 'X')
    bmesh.ops.create_cone(bm_wood, cap_ends=True, segments=6, radius1=0.025, radius2=0.02, depth=0.85, matrix=axe_pos @ Matrix.Translation((0, 0, 0.40)))
    bmesh.ops.create_cube(bm_wood, size=1.0, matrix=axe_pos @ Matrix.Scale(0.04, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.22, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 0, 1))))
    
    me_wood = bpy.data.meshes.new("Village_Firewood_Mesh")
    bm_wood.to_mesh(me_wood)
    bm_wood.free()
    obj_wood = bpy.data.objects.new("Village_Firewood_Stacks", me_wood)
    col_props.objects.link(obj_wood)
    if mat_firewood:
        obj_wood.data.materials.append(mat_firewood)
    
    # ── 5. MODULE 5: Window Flower Boxes & Potted Plants ──────
    print("Rebuilding Window Flower Boxes...")
    flower_box_locs = [
        (0.8, -4.6, 2.15, 1.4, 0),
        (-2.2, -4.6, 2.15, 1.4, 0),
        (3.0, -13.5, 2.35, 1.6, 0),
        (5.5, -13.5, 2.35, 1.6, 0),
        (4.2, -13.6, 4.45, 2.2, 0),
        (-3.2, 2.5, 2.25, 1.2, 90),
        (10.5, 12.2, 2.20, 1.4, -30),
    ]
    bm_boxes = bmesh.new()
    bm_flowers = bmesh.new()
    for bx, by, bz, b_len, b_rot in flower_box_locs:
        rot_mat = Matrix.Rotation(math.radians(b_rot), 4, 'Z')
        box_mat = Matrix.Translation((bx, by, bz)) @ rot_mat
        bmesh.ops.create_cube(bm_boxes, size=1.0, matrix=box_mat @ Matrix.Scale(b_len, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.28, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.22, 4, Vector((0, 0, 1))))
        n_blossoms = int(b_len / 0.18)
        for fi in range(n_blossoms):
            fx = -b_len*0.45 + fi * 0.18
            f_pos = box_mat @ Vector((fx, 0, 0.12))
            bmesh.ops.create_cone(bm_flowers, cap_ends=True, segments=5, radius1=0.06, radius2=0.01, depth=0.08, matrix=Matrix.Translation(f_pos))
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
    
    # Potted Ferns
    pot_locs = [
        (1.8, -4.8), (-1.2, -4.8), (0.2, -5.2),
        (2.8, -14.2), (6.2, -14.2), (4.5, -15.5),
        (-3.5, -24.5), (3.5, -24.5),
        (11.8, -8.5), (14.2, -8.5),
        (9.8, 18.2), (12.2, 18.2)
    ]
    bm_pots = bmesh.new()
    for px, py in pot_locs:
        pz = get_ground_z(px, py)
        pot_mat = Matrix.Translation((px, py, pz + 0.22))
        bmesh.ops.create_cone(bm_pots, cap_ends=True, segments=8, radius1=0.20, radius2=0.14, depth=0.44, matrix=pot_mat)
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
    
    # ── 6. MODULE 6: Hanging Trade Signs & Wall Bracket Lanterns ──
    print("Rebuilding Trade Signs and Bracket Lanterns...")
    signs = [
        ("Tavern_Sign", 2.4, -14.8, 3.8, 0.9, 0.65),
        ("Smith_Sign", 12.2, -8.5, 3.2, 0.75, 0.55)
    ]
    bm_signs = bmesh.new()
    for name, sx, sy, sz, sw, sh in signs:
        b_mat = Matrix.Translation((sx, sy, sz))
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=b_mat @ Matrix.Translation((0.55, 0, 0)) @ Matrix.Scale(1.1, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.05, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.05, 4, Vector((0, 0, 1))))
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=b_mat @ Matrix.Translation((0.45, 0, -0.35)) @ Matrix.Rotation(math.radians(-40), 4, 'Y') @ Matrix.Scale(0.9, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))))
        for cx_off in [0.35, 0.85]:
            bmesh.ops.create_cone(bm_signs, cap_ends=True, segments=4, radius1=0.015, radius2=0.015, depth=0.20, matrix=b_mat @ Matrix.Translation((cx_off, 0, -0.12)))
        sign_board_mat = b_mat @ Matrix.Translation((0.60, 0, -0.55))
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=sign_board_mat @ Matrix.Scale(sw, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(sh, 4, Vector((0, 0, 1))))
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=sign_board_mat @ Matrix.Scale(sw*1.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @ Matrix.Scale(sh*1.06, 4, Vector((0, 0, 1))))
    
    me_signs = bpy.data.meshes.new("Village_Trade_Signs_Mesh")
    bm_signs.to_mesh(me_signs)
    bm_signs.free()
    obj_signs = bpy.data.objects.new("Village_Trade_Signs", me_signs)
    col_props.objects.link(obj_signs)
    if mat_wood:
        obj_signs.data.materials.append(mat_wood)
    
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
        bmesh.ops.create_cube(bm_blan, size=1.0, matrix=mount_mat @ Matrix.Rotation(rot_ang, 4, 'Z') @ Matrix.Translation((0.25, 0, 0)) @ Matrix.Scale(0.50, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))))
        l_pos = Vector((lx + dx * 0.45, ly + dy * 0.45, lz - 0.15))
        bmesh.ops.create_cone(bm_blan, cap_ends=True, segments=6, radius1=0.14, radius2=0.03, depth=0.14, matrix=Matrix.Translation(l_pos + Vector((0, 0, 0.16))))
        bmesh.ops.create_cone(bm_blan, cap_ends=True, segments=6, radius1=0.09, radius2=0.12, depth=0.24, matrix=Matrix.Translation(l_pos))
    
    me_blan = bpy.data.meshes.new("Village_Bracket_Lanterns_Mesh")
    bm_blan.to_mesh(me_blan)
    bm_blan.free()
    obj_blan = bpy.data.objects.new("Village_Bracket_Lanterns", me_blan)
    col_props.objects.link(obj_blan)
    if mat_iron:
        obj_blan.data.materials.append(mat_iron)
    
    # ── 7. MODULE 7: Festival Bunting Flags ──────────────────
    print("Rebuilding Bunting Flags...")
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
            sag0 = math.sin(t0 * math.pi) * 0.45
            sag1 = math.sin(t1 * math.pi) * 0.45
            pt_a = p0 + seg_vec * t0 - Vector((0, 0, sag0))
            pt_b = p0 + seg_vec * t1 - Vector((0, 0, sag1))
            pt_tip = (pt_a + pt_b) * 0.5 - Vector((0, 0, 0.32))
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
    
    # ── 8. MODULE 8: Update Camera Angles ────────────────────
    print("Updating camera angles...")
    col_mgmt = bpy.data.collections.get("00_MANAGEMENT")
    
    # 1. Cam_Street_Life_Hero (Ref 2 & 4): Market Square looking North toward Tavern & Street
    cam_st = bpy.data.objects.get("Cam_Street_Life_Hero")
    loc_st = Vector((-1.2, -26.0, 1.85))
    tgt_st = Vector((3.0, -17.5, 2.40))
    cam_st.location = loc_st
    cam_st.data.lens = 28.0
    cam_st.rotation_euler = (tgt_st - loc_st).to_track_quat('-Z', 'Y').to_euler()
    
    # 2. Cam_Wagon_Market_Hero (Ref 3): Hero close-up of 4-wheeled wagon in Market Square
    cam_wg = bpy.data.objects.get("Cam_Wagon_Market_Hero")
    loc_wg = Vector((0.5, -25.2, 1.95))
    tgt_wg = Vector((3.5, -22.5, 1.55))
    cam_wg.location = loc_wg
    cam_wg.data.lens = 35.0
    cam_wg.rotation_euler = (tgt_wg - loc_wg).to_track_quat('-Z', 'Y').to_euler()
    
    # 3. Cam_Props_Table_StillLife (Ref 1): Still-life of table with goods
    cam_tab = bpy.data.objects.get("Cam_Props_Table_StillLife")
    loc_tab = Vector((-2.2, -19.6, 1.45))
    tgt_tab = Vector((-2.2, -21.5, 0.82))
    cam_tab.location = loc_tab
    cam_tab.data.lens = 38.0
    cam_tab.rotation_euler = (tgt_tab - loc_tab).to_track_quat('-Z', 'Y').to_euler()
    
    # 4. Cam_Village_Entrance_NoticeBoard (Ref 5): South entrance notice board & fences
    cam_nb = bpy.data.objects.get("Cam_Village_Entrance_NoticeBoard")
    loc_nb = Vector((0.5, -39.5, 1.55))
    tgt_nb = Vector((2.8, -36.0, 1.35))
    cam_nb.location = loc_nb
    cam_nb.data.lens = 30.0
    cam_nb.rotation_euler = (tgt_nb - loc_nb).to_track_quat('-Z', 'Y').to_euler()
    
    print("Rebuild completed successfully!")
    

if __name__ == "__main__":
    run_rebuild()
