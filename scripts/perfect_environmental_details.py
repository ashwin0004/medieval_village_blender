"""
scripts/perfect_environmental_details.py
========================================
Comprehensive upgrade of village environmental details to match references:
  1. Ref 1: Hero Market Table Vignette (barrel, hamper, crates, sacks, rope, bucket, jugs, bowl, basket)
  2. Ref 3: 4-Wheeled Cargo Wagon (vertical spoked wheels, draught poles, slatted bed, barrels, tarp, glowing lantern)
  3. Ref 5: Village Notice Board & Entrance Gate (gabled rooflet, pinned notices, illuminated lantern, boundary fences, slatted swing gate)
  4. Ref 2 & 4: Street Life Atmosphere (cobblestone street with street lamps, bracket lanterns, window flower boxes, bunting, benches)
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
import math

def get_or_create_col(name, parent_col=None):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

def remove_obj_if_exists(name):
    obj = bpy.data.objects.get(name)
    if obj:
        mesh = obj.data if obj.type == 'MESH' else None
        light = obj.data if obj.type == 'LIGHT' else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        if light and light.users == 0:
            bpy.data.lights.remove(light)

def get_pbr_material(name):
    return bpy.data.materials.get(name)

def build_perfect_props():
    print("=== Perfecting Environmental Details to Match Reference Images ===")
    
    col_structures = get_or_create_col("03_VILLAGE_STRUCTURES")
    col_props = get_or_create_col("Village_Environmental_Props", col_structures)
    
    # Materials
    mat_wood = get_pbr_material("M_Wood_AgedOak") or get_pbr_material("M_Wood_DarkTimber")
    mat_pine = get_pbr_material("M_Wood_LightPine") or mat_wood
    mat_iron = get_pbr_material("M_Iron_Wrought")
    mat_lantern = get_pbr_material("M_Lantern_Warm") or get_pbr_material("M_Lantern_Glow")
    mat_terracotta = get_pbr_material("M_Clay_Terracotta")
    mat_ceramic = get_pbr_material("M_Ceramic_Glazed") or mat_terracotta
    mat_burlap = get_pbr_material("M_Burlap_Hessian")
    mat_wicker = get_pbr_material("M_Wicker_Willow")
    mat_rope = get_pbr_material("M_Hemp_Rope")
    mat_firewood = get_pbr_material("M_Firewood_Bark")
    mat_parchment = get_pbr_material("M_Parchment_Paper")
    mat_tarp = get_pbr_material("M_Wagon_Tarp")
    mat_poppy = get_pbr_material("M_Flower_Poppy_Red")
    
    # Emission for lantern material
    if mat_lantern and mat_lantern.use_nodes:
        for n in mat_lantern.node_tree.nodes:
            if n.type == 'EMISSION':
                n.inputs['Strength'].default_value = 25.0
                n.inputs['Color'].default_value = (1.0, 0.72, 0.32, 1.0)
            elif n.type == 'BSDF_PRINCIPLED':
                n.inputs['Emission Strength'].default_value = 25.0
                n.inputs['Emission Color'].default_value = (1.0, 0.72, 0.32, 1.0)

    # -------------------------------------------------------------
    # 1. HERO MARKET TABLE VIGNETTE (Ref 1)
    # -------------------------------------------------------------
    print("Building Ref 1: Market Table Still-Life Vignette...")
    for name in ["Hero_Market_Table", "Hero_Table_Barrel", "Hero_Table_Jugs", "Hero_Table_Bowl",
                 "Hero_Table_Baskets", "Hero_Table_Crates", "Hero_Table_Rope", "Hero_Table_Bucket",
                 "Hero_Table_Sacks", "Light_Table_KeyFill"]:
        remove_obj_if_exists(name)
        
    tx, ty, tz = -2.5, -24.0, 0.45
    t_w, t_d, t_h = 2.0, 1.0, 0.78
    
    # Table (Oak)
    bm_tbl = bmesh.new()
    bmesh.ops.create_cube(bm_tbl, size=1.0, matrix=Matrix.Translation((tx, ty, tz + t_h)) @ 
                          Matrix.Scale(t_w, 4, Vector((1, 0, 0))) @ 
                          Matrix.Scale(t_d, 4, Vector((0, 1, 0))) @ 
                          Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    leg_x = (t_w * 0.5) - 0.12
    leg_y = (t_d * 0.5) - 0.12
    for lx in [-leg_x, leg_x]:
        for ly in [-leg_y, leg_y]:
            bmesh.ops.create_cube(bm_tbl, size=1.0, matrix=Matrix.Translation((tx + lx, ty + ly, tz + t_h * 0.5)) @
                                  Matrix.Scale(0.12, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(t_h, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_tbl, size=1.0, matrix=Matrix.Translation((tx, ty - leg_y, tz + 0.18)) @
                          Matrix.Scale(t_w - 0.24, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_tbl, size=1.0, matrix=Matrix.Translation((tx, ty + leg_y, tz + 0.18)) @
                          Matrix.Scale(t_w - 0.24, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    me_tbl = bpy.data.meshes.new("Hero_Market_Table_Mesh")
    bm_tbl.to_mesh(me_tbl)
    bm_tbl.free()
    obj_tbl = bpy.data.objects.new("Hero_Market_Table", me_tbl)
    col_props.objects.link(obj_tbl)
    if mat_wood:
        obj_tbl.data.materials.append(mat_wood)

    top_z = tz + t_h + 0.04

    # A. Floor Barrel (Left of Table, Ref 1)
    bm_bar = bmesh.new()
    bar_pos = Vector((tx - 1.25, ty - 0.05, tz + 0.48))
    bmesh.ops.create_cone(bm_bar, cap_ends=True, segments=16, radius1=0.38, radius2=0.33, depth=0.96,
                          matrix=Matrix.Translation(bar_pos))
    for hz in [-0.35, -0.15, 0.15, 0.35]:
        bmesh.ops.create_cone(bm_bar, cap_ends=False, segments=16, radius1=0.385, radius2=0.385, depth=0.035,
                              matrix=Matrix.Translation(bar_pos + Vector((0, 0, hz))))
    me_bar = bpy.data.meshes.new("Hero_Table_Barrel_Mesh")
    bm_bar.to_mesh(me_bar)
    bm_bar.free()
    obj_bar = bpy.data.objects.new("Hero_Table_Barrel", me_bar)
    col_props.objects.link(obj_bar)
    if mat_wood:
        obj_bar.data.materials.append(mat_wood)

    # B. Terracotta Pitchers / Jugs on Table (Ref 1)
    bm_jug = bmesh.new()
    bmesh.ops.create_cone(bm_jug, cap_ends=True, segments=14, radius1=0.13, radius2=0.06, depth=0.36,
                          matrix=Matrix.Translation((tx - 0.55, ty + 0.10, top_z + 0.18)))
    bmesh.ops.create_cone(bm_jug, cap_ends=True, segments=14, radius1=0.10, radius2=0.05, depth=0.26,
                          matrix=Matrix.Translation((tx - 0.32, ty + 0.05, top_z + 0.13)))
    me_jug = bpy.data.meshes.new("Hero_Table_Jugs_Mesh")
    bm_jug.to_mesh(me_jug)
    bm_jug.free()
    obj_jug = bpy.data.objects.new("Hero_Table_Jugs", me_jug)
    col_props.objects.link(obj_jug)
    if mat_terracotta:
        obj_jug.data.materials.append(mat_terracotta)

    # C. Glazed Ceramic Bowl on Table (Ref 1)
    bm_bw = bmesh.new()
    bmesh.ops.create_cone(bm_bw, cap_ends=True, segments=16, radius1=0.22, radius2=0.12, depth=0.12,
                          matrix=Matrix.Translation((tx + 0.05, ty + 0.08, top_z + 0.06)))
    me_bw = bpy.data.meshes.new("Hero_Table_Bowl_Mesh")
    bm_bw.to_mesh(me_bw)
    bm_bw.free()
    obj_bw = bpy.data.objects.new("Hero_Table_Bowl", me_bw)
    col_props.objects.link(obj_bw)
    if mat_ceramic:
        obj_bw.data.materials.append(mat_ceramic)

    # D. Wicker Baskets & Tall Hamper (Ref 1)
    bm_wck = bmesh.new()
    bmesh.ops.create_cone(bm_wck, cap_ends=True, segments=14, radius1=0.18, radius2=0.14, depth=0.22,
                          matrix=Matrix.Translation((tx + 0.52, ty + 0.10, top_z + 0.11)))
    for a_i in range(9):
        ang = math.radians(20 * a_i)
        hx = (tx + 0.52) + math.cos(ang) * 0.16
        hz = (top_z + 0.22) + math.sin(ang) * 0.16
        bmesh.ops.create_cube(bm_wck, size=1.0, matrix=Matrix.Translation((hx, ty + 0.10, hz)) @
                              Matrix.Scale(0.03, 4, Vector((1, 0, 0))) @
                              Matrix.Scale(0.03, 4, Vector((0, 1, 0))) @
                              Matrix.Scale(0.04, 4, Vector((0, 0, 1))))
    # Tall wicker hamper on floor
    bmesh.ops.create_cone(bm_wck, cap_ends=True, segments=16, radius1=0.25, radius2=0.25, depth=0.92,
                          matrix=Matrix.Translation((tx + 1.25, ty - 0.05, tz + 0.46)))
    bmesh.ops.create_cone(bm_wck, cap_ends=True, segments=16, radius1=0.27, radius2=0.26, depth=0.08,
                          matrix=Matrix.Translation((tx + 1.25, ty - 0.05, tz + 0.94)))
    # Low woven basket bowl on ground
    bmesh.ops.create_cone(bm_wck, cap_ends=True, segments=14, radius1=0.20, radius2=0.15, depth=0.16,
                          matrix=Matrix.Translation((tx - 0.15, ty - 0.55, tz + 0.08)))
    me_wck = bpy.data.meshes.new("Hero_Table_Baskets_Mesh")
    bm_wck.to_mesh(me_wck)
    bm_wck.free()
    obj_wck = bpy.data.objects.new("Hero_Table_Baskets", me_wck)
    col_props.objects.link(obj_wck)
    if mat_wicker:
        obj_wck.data.materials.append(mat_wicker)

    # E. Stacked Slatted Wooden Crates (Ref 1)
    bm_crt = bmesh.new()
    bmesh.ops.create_cube(bm_crt, size=1.0, matrix=Matrix.Translation((tx + 1.15, ty - 0.55, tz + 0.18)) @
                          Matrix.Scale(0.70, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.48, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.36, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_crt, size=1.0, matrix=Matrix.Translation((tx + 1.15, ty - 0.55, tz + 0.52)) @
                          Matrix.Rotation(math.radians(-14), 4, 'Z') @
                          Matrix.Scale(0.68, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.46, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.34, 4, Vector((0, 0, 1))))
    me_crt = bpy.data.meshes.new("Hero_Table_Crates_Mesh")
    bm_crt.to_mesh(me_crt)
    bm_crt.free()
    obj_crt = bpy.data.objects.new("Hero_Table_Crates", me_crt)
    col_props.objects.link(obj_crt)
    if mat_pine:
        obj_crt.data.materials.append(mat_pine)

    # F. Hessian Burlap Grain Sacks (Ref 1)
    bm_sck = bmesh.new()
    bmesh.ops.create_cone(bm_sck, cap_ends=True, segments=12, radius1=0.20, radius2=0.15, depth=0.55,
                          matrix=Matrix.Translation((tx - 0.75, ty - 0.58, tz + 0.28)))
    bmesh.ops.create_cone(bm_sck, cap_ends=True, segments=8, radius1=0.08, radius2=0.04, depth=0.12,
                          matrix=Matrix.Translation((tx - 0.75, ty - 0.58, tz + 0.58)))
    bmesh.ops.create_cone(bm_sck, cap_ends=True, segments=12, radius1=0.22, radius2=0.16, depth=0.48,
                          matrix=Matrix.Translation((tx - 0.45, ty - 0.35, tz + 0.24)))
    bmesh.ops.create_cone(bm_sck, cap_ends=True, segments=12, radius1=0.14, radius2=0.12, depth=0.25,
                          matrix=Matrix.Translation((tx - 0.05, ty - 0.20, top_z + 0.12)))
    me_sck = bpy.data.meshes.new("Hero_Table_Sacks_Mesh")
    bm_sck.to_mesh(me_sck)
    bm_sck.free()
    obj_sck = bpy.data.objects.new("Hero_Table_Sacks", me_sck)
    col_props.objects.link(obj_sck)
    if mat_burlap:
        obj_sck.data.materials.append(mat_burlap)

    # G. Coiled Hemp Rope (Front floor, Ref 1)
    bm_rp = bmesh.new()
    for ring in range(3):
        rad = 0.18 + ring * 0.06
        for step in range(16):
            ang = step * (2 * math.pi / 16)
            rx = tx - 0.65 + math.cos(ang) * rad
            ry = ty - 0.88 + math.sin(ang) * rad
            bmesh.ops.create_cube(bm_rp, size=1.0, matrix=Matrix.Translation((rx, ry, tz + 0.03 + ring * 0.015)) @
                                  Matrix.Scale(0.05, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.05, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.03, 4, Vector((0, 0, 1))))
    me_rp = bpy.data.meshes.new("Hero_Table_Rope_Mesh")
    bm_rp.to_mesh(me_rp)
    bm_rp.free()
    obj_rp = bpy.data.objects.new("Hero_Table_Rope", me_rp)
    col_props.objects.link(obj_rp)
    if mat_rope:
        obj_rp.data.materials.append(mat_rope)

    # H. Wooden Stave Bucket (Ref 1)
    bm_bkt = bmesh.new()
    b_pos = Vector((tx + 0.45, ty - 0.65, tz + 0.22))
    bmesh.ops.create_cone(bm_bkt, cap_ends=True, segments=14, radius1=0.20, radius2=0.16, depth=0.44,
                          matrix=Matrix.Translation(b_pos))
    bmesh.ops.create_cone(bm_bkt, cap_ends=False, segments=14, radius1=0.205, radius2=0.205, depth=0.03,
                          matrix=Matrix.Translation(b_pos + Vector((0, 0, -0.12))))
    bmesh.ops.create_cone(bm_bkt, cap_ends=False, segments=14, radius1=0.175, radius2=0.175, depth=0.03,
                          matrix=Matrix.Translation(b_pos + Vector((0, 0, 0.12))))
    me_bkt = bpy.data.meshes.new("Hero_Table_Bucket_Mesh")
    bm_bkt.to_mesh(me_bkt)
    bm_bkt.free()
    obj_bkt = bpy.data.objects.new("Hero_Table_Bucket", me_bkt)
    col_props.objects.link(obj_bkt)
    if mat_wood:
        obj_bkt.data.materials.append(mat_wood)

    # Key/fill light for table still-life
    pl_tbl = bpy.data.lights.new("Light_Table_KeyFill", 'POINT')
    pl_tbl.energy = 65.0
    pl_tbl.color = (1.0, 0.92, 0.82)
    obj_tbl_l = bpy.data.objects.new("Light_Table_KeyFill", pl_tbl)
    col_props.objects.link(obj_tbl_l)
    obj_tbl_l.location = Vector((tx, ty - 2.0, tz + 2.0))

    # -------------------------------------------------------------
    # 2. HERO CARGO WAGON (Ref 3)
    # -------------------------------------------------------------
    print("Building Ref 3: 4-Wheeled Cargo Wagon...")
    old_wagon_names = [o.name for o in bpy.data.objects if o.name.startswith("Wagon_") and o.name not in ["Wagon_Lantern", "Wagon_Lantern_Glass"]]
    for own in old_wagon_names:
        o = bpy.data.objects.get(own)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    for name in ["Village_Cargo_Wagon_Chassis", "Village_Cargo_Wagon_Wheels", "Village_Cargo_Wagon_Cargo",
                 "Village_Cargo_Wagon_Tarp", "Wagon_Lantern", "Wagon_Lantern_Glass", "Light_Wagon_Lantern"]:
        remove_obj_if_exists(name)

    wx, wy, wz = 1.8, -25.2, 0.45
    w_rot = math.radians(-30)
    wagon_mat = Matrix.Translation((wx, wy, wz)) @ Matrix.Rotation(w_rot, 4, 'Z')
    
    bed_l, bed_w, bed_h = 3.2, 1.4, 0.75
    
    # Chassis & Slats
    bm_ch = bmesh.new()
    bmesh.ops.create_cube(bm_ch, size=1.0, matrix=wagon_mat @ Matrix.Translation((0, 0, bed_h * 0.5)) @
                          Matrix.Scale(bed_l, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(bed_w, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.12, 4, Vector((0, 0, 1))))
    for side_y in [-bed_w * 0.5, bed_w * 0.5]:
        for s_i in range(3):
            sz = bed_h * 0.5 + 0.15 + s_i * 0.20
            bmesh.ops.create_cube(bm_ch, size=1.0, matrix=wagon_mat @ Matrix.Translation((0, side_y, sz)) @
                                  Matrix.Scale(bed_l, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.12, 4, Vector((0, 0, 1))))
        for px in [-bed_l*0.48, -bed_l*0.16, bed_l*0.16, bed_l*0.48]:
            bmesh.ops.create_cube(bm_ch, size=1.0, matrix=wagon_mat @ Matrix.Translation((px, side_y, bed_h * 0.5 + 0.35)) @
                                  Matrix.Scale(0.10, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.68, 4, Vector((0, 0, 1))))
    for ex in [-bed_l*0.5, bed_l*0.5]:
        bmesh.ops.create_cube(bm_ch, size=1.0, matrix=wagon_mat @ Matrix.Translation((ex, 0, bed_h * 0.5 + 0.30)) @
                              Matrix.Scale(0.08, 4, Vector((1, 0, 0))) @
                              Matrix.Scale(bed_w, 4, Vector((0, 1, 0))) @
                              Matrix.Scale(0.55, 4, Vector((0, 0, 1))))
    for py in [-0.25, 0.25]:
        bmesh.ops.create_cube(bm_ch, size=1.0, matrix=wagon_mat @ Matrix.Translation((-bed_l * 0.5 - 1.25, py, 0.15)) @
                              Matrix.Rotation(math.radians(-4), 4, 'Y') @
                              Matrix.Scale(2.5, 4, Vector((1, 0, 0))) @
                              Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @
                              Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    me_ch = bpy.data.meshes.new("Village_Cargo_Wagon_Chassis_Mesh")
    bm_ch.to_mesh(me_ch)
    bm_ch.free()
    obj_ch = bpy.data.objects.new("Village_Cargo_Wagon_Chassis", me_ch)
    col_props.objects.link(obj_ch)
    if mat_wood:
        obj_ch.data.materials.append(mat_wood)

    # Vertical Spoked Wheels
    bm_wh = bmesh.new()
    wheel_specs = [
        (-bed_l * 0.35, -bed_w * 0.5 - 0.14, 0.48, 8),
        (-bed_l * 0.35,  bed_w * 0.5 + 0.14, 0.48, 8),
        ( bed_l * 0.35, -bed_w * 0.5 - 0.14, 0.62, 10),
        ( bed_l * 0.35,  bed_w * 0.5 + 0.14, 0.62, 10),
    ]
    for wx_l, wy_l, wr, n_spokes in wheel_specs:
        for hi in range(8):
            hang = hi * (2 * math.pi / 8)
            hp = wagon_mat @ Vector((wx_l + math.cos(hang)*0.10, wy_l, wr + math.sin(hang)*0.10))
            bmesh.ops.create_cube(bm_wh, size=1.0, matrix=Matrix.Translation(hp) @
                                  Matrix.Scale(0.08, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.20, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
        for sp in range(n_spokes):
            sp_ang = sp * (2 * math.pi / n_spokes)
            sp_x = wx_l + math.cos(sp_ang) * (wr * 0.5)
            sp_z = wr + math.sin(sp_ang) * (wr * 0.5)
            sp_pos = wagon_mat @ Vector((sp_x, wy_l, sp_z))
            bmesh.ops.create_cube(bm_wh, size=1.0, matrix=Matrix.Translation(sp_pos) @
                                  wagon_mat.to_3x3().to_4x4() @
                                  Matrix.Rotation(-sp_ang, 4, 'Y') @
                                  Matrix.Scale(wr * 0.88, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.04, 4, Vector((0, 0, 1))))
            rim_x = wx_l + math.cos(sp_ang) * wr
            rim_z = wr + math.sin(sp_ang) * wr
            rim_pos = wagon_mat @ Vector((rim_x, wy_l, rim_z))
            bmesh.ops.create_cube(bm_wh, size=1.0, matrix=Matrix.Translation(rim_pos) @
                                  wagon_mat.to_3x3().to_4x4() @
                                  Matrix.Rotation(-sp_ang, 4, 'Y') @
                                  Matrix.Scale((2 * math.pi * wr) / n_spokes, 4, Vector((0, 0, 1))) @
                                  Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.05, 4, Vector((1, 0, 0))))
    me_wh = bpy.data.meshes.new("Village_Cargo_Wagon_Wheels_Mesh")
    bm_wh.to_mesh(me_wh)
    bm_wh.free()
    obj_wh = bpy.data.objects.new("Village_Cargo_Wagon_Wheels", me_wh)
    col_props.objects.link(obj_wh)
    if mat_iron:
        obj_wh.data.materials.append(mat_iron)

    # Barrels inside Wagon (Front half open, Ref 3)
    bm_cg = bmesh.new()
    for bx, by in [(-bed_l*0.22, -0.25), (-bed_l*0.22, 0.25), (0.0, 0.0), (bed_l*0.22, -0.22)]:
        b_pos = wagon_mat @ Vector((bx, by, bed_h * 0.5 + 0.42))
        bmesh.ops.create_cone(bm_cg, cap_ends=True, segments=14, radius1=0.32, radius2=0.28, depth=0.82,
                              matrix=Matrix.Translation(b_pos))
    me_cg = bpy.data.meshes.new("Village_Cargo_Wagon_Cargo_Mesh")
    bm_cg.to_mesh(me_cg)
    bm_cg.free()
    obj_cg = bpy.data.objects.new("Village_Cargo_Wagon_Cargo", me_cg)
    col_props.objects.link(obj_cg)
    if mat_wood:
        obj_cg.data.materials.append(mat_wood)

    # Tarpaulin Cover draped over REAR section of cargo (Ref 3)
    bm_tp = bmesh.new()
    tarp_pos = wagon_mat @ Vector((bed_l * 0.16, 0, bed_h * 0.5 + 0.65))
    bmesh.ops.create_cone(bm_tp, cap_ends=True, segments=16, radius1=bed_w * 0.62, radius2=bed_w * 0.55,
                          depth=bed_l * 0.58, matrix=Matrix.Translation(tarp_pos) @
                          wagon_mat.to_3x3().to_4x4() @ Matrix.Rotation(math.radians(90), 4, 'Y'))
    me_tp = bpy.data.meshes.new("Village_Cargo_Wagon_Tarp_Mesh")
    bm_tp.to_mesh(me_tp)
    bm_tp.free()
    obj_tp = bpy.data.objects.new("Village_Cargo_Wagon_Tarp", me_tp)
    col_props.objects.link(obj_tp)
    if mat_tarp:
        obj_tp.data.materials.append(mat_tarp)

    # Corner Lantern on FRONT-LEFT post (Ref 3)
    wlan_pos = wagon_mat @ Vector((-bed_l * 0.48, bed_w * 0.52, bed_h + 0.35))
    bm_wlan = bmesh.new()
    bmesh.ops.create_cone(bm_wlan, cap_ends=True, segments=6, radius1=0.12, radius2=0.03, depth=0.15,
                          matrix=Matrix.Translation(wlan_pos + Vector((0, 0, 0.14))))
    bmesh.ops.create_cone(bm_wlan, cap_ends=True, segments=6, radius1=0.08, radius2=0.08, depth=0.04,
                          matrix=Matrix.Translation(wlan_pos + Vector((0, 0, -0.12))))
    me_wlan = bpy.data.meshes.new("Wagon_Lantern_Mesh")
    bm_wlan.to_mesh(me_wlan)
    bm_wlan.free()
    obj_wlan = bpy.data.objects.new("Wagon_Lantern", me_wlan)
    col_props.objects.link(obj_wlan)
    if mat_iron:
        obj_wlan.data.materials.append(mat_iron)

    bm_wgl = bmesh.new()
    bmesh.ops.create_cone(bm_wgl, cap_ends=True, segments=6, radius1=0.075, radius2=0.095, depth=0.20,
                          matrix=Matrix.Translation(wlan_pos))
    me_wgl = bpy.data.meshes.new("Wagon_Lantern_Glass_Mesh")
    bm_wgl.to_mesh(me_wgl)
    bm_wgl.free()
    obj_wgl = bpy.data.objects.new("Wagon_Lantern_Glass", me_wgl)
    col_props.objects.link(obj_wgl)
    if mat_lantern:
        obj_wgl.data.materials.append(mat_lantern)

    pl_wagon = bpy.data.lights.new("Light_Wagon_Lantern", 'POINT')
    pl_wagon.energy = 95.0
    pl_wagon.color = (1.0, 0.72, 0.35)
    obj_plw = bpy.data.objects.new("Light_Wagon_Lantern", pl_wagon)
    col_props.objects.link(obj_plw)
    obj_plw.location = wlan_pos

    # -------------------------------------------------------------
    # 3. NOTICE BOARD & ENTRANCE GATE (Ref 5)
    # -------------------------------------------------------------
    print("Building Ref 5: Village Notice Board & Entrance Gate...")
    for name in ["Village_Notice_Board", "Notice_Board_Papers", "Notice_Board_Lantern",
                 "Notice_Board_Lantern_Glass", "Light_Notice_Board", "Entrance_Boundary_Fences",
                 "Entrance_Swing_Gate", "Light_Notice_Board_Fill"]:
        remove_obj_if_exists(name)

    nb_x, nb_y, nb_z = 2.8, -36.0, 0.15
    nb_w, nb_h = 2.4, 1.4
    p_spacing = 2.0

    bm_nb = bmesh.new()
    for px in [-p_spacing * 0.5, p_spacing * 0.5]:
        bmesh.ops.create_cone(bm_nb, cap_ends=True, segments=10, radius1=0.14, radius2=0.12, depth=2.8,
                              matrix=Matrix.Translation((nb_x + px, nb_y, nb_z + 1.4)))
    for i in range(7):
        pz = nb_z + 0.85 + i * 0.18
        bmesh.ops.create_cube(bm_nb, size=1.0, matrix=Matrix.Translation((nb_x, nb_y, pz)) @
                              Matrix.Scale(nb_w, 4, Vector((1, 0, 0))) @
                              Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @
                              Matrix.Scale(0.16, 4, Vector((0, 0, 1))))
    roof_z = nb_z + 2.25
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=Matrix.Translation((nb_x, nb_y - 0.18, roof_z)) @
                          Matrix.Rotation(math.radians(-25), 4, 'X') @
                          Matrix.Scale(nb_w + 0.5, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.48, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.06, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=Matrix.Translation((nb_x, nb_y + 0.18, roof_z)) @
                          Matrix.Rotation(math.radians(25), 4, 'X') @
                          Matrix.Scale(nb_w + 0.5, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.48, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.06, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_nb, size=1.0, matrix=Matrix.Translation((nb_x, nb_y, roof_z - 0.12)) @
                          Matrix.Scale(nb_w + 0.2, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.12, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.10, 4, Vector((0, 0, 1))))
    me_nb = bpy.data.meshes.new("Village_Notice_Board_Mesh")
    bm_nb.to_mesh(me_nb)
    bm_nb.free()
    obj_nb = bpy.data.objects.new("Village_Notice_Board", me_nb)
    col_props.objects.link(obj_nb)
    if mat_wood:
        obj_nb.data.materials.append(mat_wood)

    bm_notices = bmesh.new()
    notice_layouts = [
        (-0.65, 0.35, 0.38, 0.26, -3),
        (-0.20, 0.40, 0.32, 0.24, 2),
        ( 0.25, 0.36, 0.40, 0.28, -1),
        ( 0.70, 0.25, 0.30, 0.20, 4),
        (-0.45, -0.22, 0.34, 0.25, 2),
        ( 0.05, -0.25, 0.38, 0.26, -3),
        ( 0.55, -0.18, 0.32, 0.22, 1)
    ]
    for ox, oz, pw, ph, rot_deg in notice_layouts:
        bmesh.ops.create_cube(bm_notices, size=1.0,
                              matrix=Matrix.Translation((nb_x + ox, nb_y - 0.045, nb_z + 1.45 + oz)) @
                              Matrix.Rotation(math.radians(rot_deg), 4, 'Y') @
                              Matrix.Scale(pw, 4, Vector((1, 0, 0))) @
                              Matrix.Scale(0.005, 4, Vector((0, 1, 0))) @
                              Matrix.Scale(ph, 4, Vector((0, 0, 1))))
    me_notices = bpy.data.meshes.new("Notice_Board_Papers_Mesh")
    bm_notices.to_mesh(me_notices)
    bm_notices.free()
    obj_notices = bpy.data.objects.new("Notice_Board_Papers", me_notices)
    col_props.objects.link(obj_notices)
    if mat_parchment:
        obj_notices.data.materials.append(mat_parchment)

    lantern_pos = Vector((nb_x - p_spacing * 0.5 - 0.65, nb_y - 0.22, nb_z + 1.95))
    bm_nl = bmesh.new()
    bmesh.ops.create_cone(bm_nl, cap_ends=True, segments=6, radius1=0.14, radius2=0.02, depth=0.15,
                          matrix=Matrix.Translation(lantern_pos + Vector((0, 0, 0.12))))
    bmesh.ops.create_cone(bm_nl, cap_ends=True, segments=6, radius1=0.09, radius2=0.09, depth=0.04,
                          matrix=Matrix.Translation(lantern_pos + Vector((0, 0, -0.12))))
    bmesh.ops.create_cube(bm_nl, size=1.0, matrix=Matrix.Translation((nb_x - p_spacing*0.5 - 0.32, nb_y - 0.11, nb_z + 1.95)) @
                          Matrix.Scale(0.65, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.04, 4, Vector((0, 0, 1))))
    me_nl = bpy.data.meshes.new("Notice_Board_Lantern_Mesh")
    bm_nl.to_mesh(me_nl)
    bm_nl.free()
    obj_nl = bpy.data.objects.new("Notice_Board_Lantern", me_nl)
    col_props.objects.link(obj_nl)
    if mat_iron:
        obj_nl.data.materials.append(mat_iron)

    bm_ngl = bmesh.new()
    bmesh.ops.create_cone(bm_ngl, cap_ends=True, segments=6, radius1=0.08, radius2=0.10, depth=0.20,
                          matrix=Matrix.Translation(lantern_pos))
    me_ngl = bpy.data.meshes.new("Notice_Board_Lantern_Glass_Mesh")
    bm_ngl.to_mesh(me_ngl)
    bm_ngl.free()
    obj_ngl = bpy.data.objects.new("Notice_Board_Lantern_Glass", me_ngl)
    col_props.objects.link(obj_ngl)
    if mat_lantern:
        obj_ngl.data.materials.append(mat_lantern)

    pl_data = bpy.data.lights.new("Light_Notice_Board", 'POINT')
    pl_data.energy = 95.0
    pl_data.color = (1.0, 0.75, 0.40)
    obj_pl = bpy.data.objects.new("Light_Notice_Board", pl_data)
    col_props.objects.link(obj_pl)
    obj_pl.location = lantern_pos + Vector((0, -0.05, 0))

    pl_fill = bpy.data.lights.new("Light_Notice_Board_Fill", 'POINT')
    pl_fill.energy = 45.0
    pl_fill.color = (1.0, 0.82, 0.60)
    obj_fill = bpy.data.objects.new("Light_Notice_Board_Fill", pl_fill)
    col_props.objects.link(obj_fill)
    obj_fill.location = Vector((nb_x, nb_y - 2.5, nb_z + 1.8))

    # Boundary Fences
    bm_fence = bmesh.new()
    for p_i in range(5):
        fx = nb_x - 2.2 - p_i * 1.6
        fy = nb_y + p_i * 0.25
        bmesh.ops.create_cone(bm_fence, cap_ends=True, segments=8, radius1=0.09, radius2=0.07, depth=1.35,
                              matrix=Matrix.Translation((fx, fy, nb_z + 0.67)))
        if p_i < 4:
            nx = fx - 0.8
            ny = fy + 0.12
            bmesh.ops.create_cube(bm_fence, size=1.0, matrix=Matrix.Translation((nx, ny, nb_z + 0.88)) @
                                  Matrix.Scale(1.65, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.10, 4, Vector((0, 0, 1))))
            bmesh.ops.create_cube(bm_fence, size=1.0, matrix=Matrix.Translation((nx, ny, nb_z + 0.45)) @
                                  Matrix.Scale(1.65, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.10, 4, Vector((0, 0, 1))))
    for p_i in range(6):
        fx = nb_x + 1.8 + p_i * 1.6
        fy = nb_y - p_i * 0.20
        bmesh.ops.create_cone(bm_fence, cap_ends=True, segments=8, radius1=0.09, radius2=0.07, depth=1.35,
                              matrix=Matrix.Translation((fx, fy, nb_z + 0.67)))
        if p_i < 5:
            nx = fx + 0.8
            ny = fy - 0.10
            bmesh.ops.create_cube(bm_fence, size=1.0, matrix=Matrix.Translation((nx, ny, nb_z + 0.88)) @
                                  Matrix.Scale(1.65, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.10, 4, Vector((0, 0, 1))))
            bmesh.ops.create_cube(bm_fence, size=1.0, matrix=Matrix.Translation((nx, ny, nb_z + 0.45)) @
                                  Matrix.Scale(1.65, 4, Vector((1, 0, 0))) @
                                  Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @
                                  Matrix.Scale(0.10, 4, Vector((0, 0, 1))))
    me_fence = bpy.data.meshes.new("Entrance_Boundary_Fences_Mesh")
    bm_fence.to_mesh(me_fence)
    bm_fence.free()
    obj_fence = bpy.data.objects.new("Entrance_Boundary_Fences", me_fence)
    col_props.objects.link(obj_fence)
    if mat_wood:
        obj_fence.data.materials.append(mat_wood)

    # Open Slatted Swing Gate
    bm_gate = bmesh.new()
    gx, gy, gz = nb_x - 1.8, nb_y + 0.15, nb_z + 0.65
    gate_rot = math.radians(-55)
    gate_mat = Matrix.Translation((gx, gy, gz)) @ Matrix.Rotation(gate_rot, 4, 'Z')
    bmesh.ops.create_cube(bm_gate, size=1.0, matrix=gate_mat @ Matrix.Translation((0.7, 0, 0.35)) @
                          Matrix.Scale(1.4, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_gate, size=1.0, matrix=gate_mat @ Matrix.Translation((0.7, 0, -0.35)) @
                          Matrix.Scale(1.4, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.06, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.08, 4, Vector((0, 0, 1))))
    for pi in range(5):
        px = 0.15 + pi * 0.28
        bmesh.ops.create_cube(bm_gate, size=1.0, matrix=gate_mat @ Matrix.Translation((px, 0, 0)) @
                              Matrix.Scale(0.08, 4, Vector((1, 0, 0))) @
                              Matrix.Scale(0.05, 4, Vector((0, 1, 0))) @
                              Matrix.Scale(0.95, 4, Vector((0, 0, 1))))
    bmesh.ops.create_cube(bm_gate, size=1.0, matrix=gate_mat @ Matrix.Translation((0.7, 0.01, 0)) @
                          Matrix.Rotation(math.radians(-32), 4, 'Y') @
                          Matrix.Scale(1.5, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(0.05, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.07, 4, Vector((0, 0, 1))))
    me_gate = bpy.data.meshes.new("Entrance_Swing_Gate_Mesh")
    bm_gate.to_mesh(me_gate)
    bm_gate.free()
    obj_gate = bpy.data.objects.new("Entrance_Swing_Gate", me_gate)
    col_props.objects.link(obj_gate)
    if mat_wood:
        obj_gate.data.materials.append(mat_wood)

    # -------------------------------------------------------------
    # 4. STREET LIFE PROPS & BUNTING (Ref 2 & 4)
    # -------------------------------------------------------------
    print("Building Ref 2 & 4: Street Life Props & Bunting...")
    for name in ["Village_Bunting_Flags"]:
        remove_obj_if_exists(name)

    bm_bunt = bmesh.new()
    bunting_runs = [
        ((-4.5, -22.5, 5.0), (3.5, -20.5, 4.8), 16),
        ((-3.5, -17.0, 5.2), (3.8, -14.5, 4.8), 16),
        ((-2.5, -10.0, 5.0), (4.5,  -7.0, 4.9), 16)
    ]
    for p_start, p_end, n_flags in bunting_runs:
        v1, v2 = Vector(p_start), Vector(p_end)
        for fi in range(n_flags):
            t = (fi + 0.5) / n_flags
            pt = v1.lerp(v2, t)
            sag = math.sin(t * math.pi) * 0.40
            flag_top = pt - Vector((0, 0, sag))
            bmesh.ops.create_cone(bm_bunt, cap_ends=True, segments=3, radius1=0.14, radius2=0.01, depth=0.24,
                                  matrix=Matrix.Translation(flag_top - Vector((0, 0, 0.12))))
    me_bunt = bpy.data.meshes.new("Village_Bunting_Flags_Mesh")
    bm_bunt.to_mesh(me_bunt)
    bm_bunt.free()
    obj_bunt = bpy.data.objects.new("Village_Bunting_Flags", me_bunt)
    col_props.objects.link(obj_bunt)
    if mat_poppy:
        obj_bunt.data.materials.append(mat_poppy)

    # -------------------------------------------------------------
    # 5. CAMERA CALIBRATION FOR ALL 4 SHOWCASES
    # -------------------------------------------------------------
    print("Calibrating Showcase Cameras...")
    def set_camera(cam_name, loc, target, lens=35.0):
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(cam_name)
            cam_obj = bpy.data.objects.new(cam_name, cam_data)
            bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.location = Vector(loc)
        cam_obj.data.lens = lens
        
        direction = (Vector(target) - cam_obj.location).normalized()
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        print(f"  {cam_name}: loc={loc}, target={target}, lens={lens}mm")

    # 1. Hero Table Still-Life (Ref 1: Studio-style 3/4 elevated view showing all table props, unblocked)
    set_camera("Cam_Props_Table_StillLife", (-2.5, -27.5, 1.65), (-2.5, -24.0, 0.85), lens=42.0)

    # 2. Hero Cargo Wagon (Ref 3: Dynamic 3/4 front view showing draught poles, wheels, open cargo barrels, tarp, lantern)
    set_camera("Cam_Wagon_Market_Hero", (-1.2, -20.5, 2.15), (1.8, -25.2, 0.95), lens=34.0)

    # 3. Notice Board & Entrance (Ref 5: Notice board unblocked, glowing lantern, fences, village vista)
    set_camera("Cam_Village_Entrance_NoticeBoard", (1.2, -39.4, 1.55), (2.8, -36.0, 1.45), lens=32.0)

    # 4. Street Life Hero (Ref 2 & 4: Cobblestone avenue perspective looking north towards tavern, lampposts, flower boxes, bunting)
    set_camera("Cam_Street_Life_Hero", (-1.5, -35.0, 1.85), (1.2, -14.0, 2.6), lens=30.0)

    print("=== Rebuild & Calibration Complete! ===")

if __name__ == "__main__":
    build_perfect_props()
