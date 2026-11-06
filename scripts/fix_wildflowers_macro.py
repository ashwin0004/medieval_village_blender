import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import random
import os
import shutil
import sys

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)
import lighting_manager

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

def run_fix_wildflowers():
    print("--- Step 1: Adjust Mountain Alpine Material ---")
    mat_mtn = bpy.data.materials.get("M_Mountain_Alpine")
    if mat_mtn and mat_mtn.use_nodes:
        for node in mat_mtn.node_tree.nodes:
            if node.type == 'VALTORGB' and node.location.y > 0: # alt ramp
                node.color_ramp.elements[0].position = 0.78 # Snow only above ~66m
                node.color_ramp.elements[1].position = 0.92
                print("Updated mountain snow altitude thresholds.")

    print("--- Step 2: Clean old hero flower objects ---")
    col = bpy.data.collections.get("06_ENVIRONMENT_NATURE")
    if not col:
        col = bpy.data.collections.new("06_ENVIRONMENT_NATURE")
        bpy.context.scene.collection.children.link(col)

    for oname in ["Hero_Poppies", "Hero_Buttercups", "Hero_Poppy_Blossoms", "Hero_Poppy_Stems", "Hero_Poppy_Centers", "Hero_Yellow_Blossoms", "Hero_Yellow_Stems"]:
        o = bpy.data.objects.get(oname)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    cx, cy = 5.8, -41.2
    gz = get_ground_z(cx, cy)

    mat_stem = bpy.data.materials.get("M_Flower_Stem")
    mat_poppy = bpy.data.materials.get("M_Flower_Poppy_Red")
    mat_yellow = bpy.data.materials.get("M_Flower_Yellow")
    mat_center = bpy.data.materials.get("M_Flower_Center")

    # Positions in FRONT and around the hero boulder
    flower_positions = [
        (cx - 0.25, cy - 0.55),
        (cx - 0.05, cy - 0.65),
        (cx + 0.15, cy - 0.50),
        (cx + 0.35, cy - 0.60),
        (cx - 0.40, cy - 0.40),
        (cx + 0.45, cy - 0.45),
        (cx - 0.15, cy - 0.75),
        (cx + 0.20, cy - 0.70),
        (cx + 0.00, cy - 0.58),
        (cx - 0.30, cy - 0.68),
        (cx + 0.30, cy - 0.52),
        (cx - 0.10, cy - 0.48),
    ]

    print("--- Step 3: Create Poppy Stems, Centers & Blossoms ---")
    me_stems = bpy.data.meshes.new("Hero_Poppy_Stems_Mesh")
    me_blossoms = bpy.data.meshes.new("Hero_Poppy_Blossoms_Mesh")
    me_centers = bpy.data.meshes.new("Hero_Poppy_Centers_Mesh")

    bm_s = bmesh.new()
    bm_b = bmesh.new()
    bm_c = bmesh.new()

    random.seed(42)

    for i, (fx, fy) in enumerate(flower_positions[:8]):
        fz = get_ground_z(fx, fy, fallback=gz)
        stem_h = random.uniform(0.24, 0.36)
        n_seg = 6
        v_prev = None
        
        # Curved stem
        curve_dir = random.uniform(0, 2*math.pi)
        curve_amt = random.uniform(0.03, 0.07)
        
        for s in range(n_seg + 1):
            t = s / n_seg
            sx = fx + math.cos(curve_dir) * (t ** 1.5) * curve_amt
            sy = fy + math.sin(curve_dir) * (t ** 1.5) * curve_amt
            sz = fz + t * stem_h
            r_stem = 0.0035 * (1.0 - t * 0.3)
            
            # Create a 4-sided cross section ring
            ring_verts = []
            for a in range(4):
                ang = a * (math.pi / 2.0)
                rx = sx + math.cos(ang) * r_stem
                ry = sy + math.sin(ang) * r_stem
                ring_verts.append(bm_s.verts.new((rx, ry, sz)))
                
            if v_prev:
                for k in range(4):
                    bm_s.faces.new([v_prev[k], v_prev[(k+1)%4], ring_verts[(k+1)%4], ring_verts[k]])
            v_prev = ring_verts
            
        head_x, head_y, head_z = sx, sy, sz
        
        # Center dome (capsule/ovary)
        bmesh.ops.create_uvsphere(bm_c, u_segments=8, v_segments=6, radius=0.012, matrix=Matrix.Translation((head_x, head_y, head_z + 0.005)))
        
        # 4 wide scalloped petals (cup shape)
        n_petals = 4
        base_rot = random.uniform(0, math.pi)
        cup_flare = random.uniform(0.045, 0.065)
        petal_w = random.uniform(0.035, 0.050)
        
        for p in range(n_petals):
            p_ang = base_rot + p * (math.pi / 2.0)
            c_dir = Vector((math.cos(p_ang), math.sin(p_ang), 0.0))
            side_dir = Vector((-math.sin(p_ang), math.cos(p_ang), 0.0))
            
            p_base = Vector((head_x, head_y, head_z))
            p_mid = p_base + c_dir * (cup_flare * 0.5) + Vector((0, 0, 0.025))
            p_tip = p_base + c_dir * cup_flare + Vector((0, 0, 0.045))
            
            # Quad fan for each petal
            v_b = bm_b.verts.new(p_base)
            v_ml = bm_b.verts.new(p_mid - side_dir * (petal_w * 0.4))
            v_mr = bm_b.verts.new(p_mid + side_dir * (petal_w * 0.4))
            v_t = bm_b.verts.new(p_tip)
            
            bm_b.faces.new([v_b, v_ml, v_t, v_mr])

    bm_s.to_mesh(me_stems)
    bm_s.free()
    bm_b.to_mesh(me_blossoms)
    bm_b.free()
    bm_c.to_mesh(me_centers)
    bm_c.free()

    obj_stems = bpy.data.objects.new("Hero_Poppy_Stems", me_stems)
    obj_blossoms = bpy.data.objects.new("Hero_Poppy_Blossoms", me_blossoms)
    obj_centers = bpy.data.objects.new("Hero_Poppy_Centers", me_centers)

    col.objects.link(obj_stems)
    col.objects.link(obj_blossoms)
    col.objects.link(obj_centers)

    if mat_stem:
        obj_stems.data.materials.append(mat_stem)
    if mat_poppy:
        obj_blossoms.data.materials.append(mat_poppy)
    if mat_center:
        obj_centers.data.materials.append(mat_center)

    mod_sol = obj_blossoms.modifiers.new("Solidify", 'SOLIDIFY')
    mod_sol.thickness = 0.0015

    print("--- Step 4: Create Yellow Buttercup Blossoms & Stems ---")
    me_ystems = bpy.data.meshes.new("Hero_Yellow_Stems_Mesh")
    me_yblossoms = bpy.data.meshes.new("Hero_Yellow_Blossoms_Mesh")

    bm_ys = bmesh.new()
    bm_yp = bmesh.new()

    for i, (fx, fy) in enumerate(flower_positions[6:]):
        fz = get_ground_z(fx, fy, fallback=gz)
        stem_h = random.uniform(0.18, 0.28)
        
        # Stem
        v0 = bm_ys.verts.new((fx, fy, fz))
        v1 = bm_ys.verts.new((fx + random.uniform(-0.02, 0.02), fy + random.uniform(-0.02, 0.02), fz + stem_h * 0.5))
        v2 = bm_ys.verts.new((fx + random.uniform(-0.04, 0.04), fy + random.uniform(-0.04, 0.04), fz + stem_h))
        
        # Thin tube for buttercup stem
        hx, hy, hz = v2.co.x, v2.co.y, v2.co.z
        
        # 5 star petals
        n_ypetals = 5
        b_rot = random.uniform(0, 2*math.pi)
        yflare = random.uniform(0.025, 0.038)
        
        for yp in range(n_ypetals):
            ya = b_rot + yp * (2 * math.pi / n_ypetals)
            ydir = Vector((math.cos(ya), math.sin(ya), 0.0))
            yside = Vector((-math.sin(ya), math.cos(ya), 0.0))
            
            pb = Vector((hx, hy, hz))
            pm = pb + ydir * (yflare * 0.5) + Vector((0, 0, 0.012))
            pt = pb + ydir * yflare + Vector((0, 0, 0.022))
            
            vpb = bm_yp.verts.new(pb)
            vpml = bm_yp.verts.new(pm - yside * (yflare * 0.25))
            vpmr = bm_yp.verts.new(pm + yside * (yflare * 0.25))
            vpt = bm_yp.verts.new(pt)
            
            bm_yp.faces.new([vpb, vpml, vpt, vpmr])

    bm_ys.to_mesh(me_ystems)
    bm_ys.free()
    bm_yp.to_mesh(me_yblossoms)
    bm_yp.free()

    obj_ystems = bpy.data.objects.new("Hero_Yellow_Stems", me_ystems)
    obj_yblossoms = bpy.data.objects.new("Hero_Yellow_Blossoms", me_yblossoms)

    col.objects.link(obj_ystems)
    col.objects.link(obj_yblossoms)

    if mat_stem:
        obj_ystems.data.materials.append(mat_stem)
    if mat_yellow:
        obj_yblossoms.data.materials.append(mat_yellow)

    mod_sol_y = obj_yblossoms.modifiers.new("Solidify", 'SOLIDIFY')
    mod_sol_y.thickness = 0.0015

    print("Wildflower mesh rebuild completed successfully!")

if __name__ == "__main__":
    run_fix_wildflowers()
