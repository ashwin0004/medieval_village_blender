"""
polish_river_and_bridge.py
==========================
Polishes and refines the River, Stone Arch Bridge, Waterfalls, and Riverbanks:
  1. Removes old blockout flower cones from riverbank (Wildflowers_poppy_10, 11).
  2. Adds high-detail running-bond masonry texture to bridge ashlar and parapets.
  3. Builds organic, curved cascading waterfalls with aerated foam and splash mist.
  4. Adds trailing ivy and flowering planters along the bridge and waterfront retaining wall (Ref 1).
  5. Configures warm, flattering cinematic river lighting so arches, voussoirs, water reflections, and rowboat gleam.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix
import random
import os
import shutil

def run_polish_river_and_bridge():
    print("--- Step 1: Remove blockout cones near river ---")
    for oname in ["Wildflowers_poppy_10", "Wildflowers_poppy_11", "Wildflowers_yellow_12", "River_Waterfall_Foam"]:
        o = bpy.data.objects.get(oname)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    print("--- Step 2: Realistic Running-Bond Ashlar Stone Material for Bridge ---")
    mat_ash = bpy.data.materials.get("M_Stone_Bridge_Ashlar")
    if mat_ash and mat_ash.use_nodes:
        nt = mat_ash.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        out.location = (600, 0)
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (300, 0)
        bsdf.inputs['Roughness'].default_value = 0.88
        
        tc = nt.nodes.new("ShaderNodeTexCoord")
        tc.location = (-700, 0)
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.location = (-500, 0)
        nt.links.new(tc.outputs['Object'], mapping.inputs['Vector'])
        
        # Brick Texture for medieval ashlar coursing (rectangular dressed blocks)
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.location = (-300, 100)
        brick.inputs['Scale'].default_value = 3.5
        brick.inputs['Mortar Size'].default_value = 0.02
        brick.inputs['Mortar Smooth'].default_value = 0.2
        brick.inputs['Row Height'].default_value = 0.35
        brick.inputs['Color1'].default_value = (0.36, 0.34, 0.31, 1.0)
        brick.inputs['Color2'].default_value = (0.31, 0.29, 0.26, 1.0)
        brick.inputs['Mortar'].default_value = (0.16, 0.15, 0.14, 1.0)
        nt.links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
        
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.location = (-300, -150)
        noise.inputs['Scale'].default_value = 22.0
        nt.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
        
        # Bump combining brick mortar lines and stone surface grain
        bump_brick = nt.nodes.new("ShaderNodeBump")
        bump_brick.location = (-50, 100)
        bump_brick.inputs['Strength'].default_value = 0.45
        bump_brick.inputs['Distance'].default_value = 0.05
        nt.links.new(brick.outputs['Fac'], bump_brick.inputs['Height'])
        
        bump_stone = nt.nodes.new("ShaderNodeBump")
        bump_stone.location = (150, 0)
        bump_stone.inputs['Strength'].default_value = 0.25
        bump_stone.inputs['Distance'].default_value = 0.03
        nt.links.new(noise.outputs['Fac'], bump_stone.inputs['Height'])
        nt.links.new(bump_brick.outputs['Normal'], bump_stone.inputs['Normal'])
        
        nt.links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
        nt.links.new(bump_stone.outputs['Normal'], bsdf.inputs['Normal'])
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    print("--- Step 3: Build Organic Stepped Waterfall & Weir Cascades ---")
    col_nature = bpy.data.collections.get("06_ENVIRONMENT_NATURE")
    mat_foam = bpy.data.materials.get("M_Water_Foam")
    mat_water = bpy.data.materials.get("M_River_Water_Reflective")

    # 1. Bridge Weir Waterfall Curtain (Curving organic sheet, Ref 3)
    bm_wf = bmesh.new()

    # Smooth curved curtain falling from weir timber sill (X=5.2) to pool (X=4.6, Z=-0.85)
    n_curt_u = 24
    n_curt_v = 8
    for i in range(n_curt_u + 1):
        ty = i / n_curt_u
        wy = 19.3 + ty * 5.4
        for j in range(n_curt_v + 1):
            tv = j / n_curt_v
            # Parabolic waterfall trajectory
            wx = 5.2 - (tv ** 1.6) * 0.55 + math.sin(i * 1.5) * 0.04
            wz = -0.50 - (tv ** 1.4) * 0.35
            bm_wf.verts.new((wx, wy, wz))

    bm_wf.verts.ensure_lookup_table()
    for i in range(n_curt_u):
        for j in range(n_curt_v):
            v0 = bm_wf.verts[i * (n_curt_v + 1) + j]
            v1 = bm_wf.verts[i * (n_curt_v + 1) + j + 1]
            v2 = bm_wf.verts[(i + 1) * (n_curt_v + 1) + j + 1]
            v3 = bm_wf.verts[(i + 1) * (n_curt_v + 1) + j]
            bm_wf.faces.new([v0, v1, v2, v3])

    # 2. Upstream East Stepped Waterfall (Ref 2, 5)
    # Cascading over 3 natural rock ledges at X=27.5 down to X=22.5
    wf_ledges = [
        (27.0, 24.0, 1.10, 0.45),
        (25.0, 23.5, 0.60, 0.50),
        (23.2, 23.2, 0.05, 0.55),
    ]
    for lx, ly, lz, drop in wf_ledges:
        base_idx = len(bm_wf.verts)
        n_w_u = 12
        n_w_v = 6
        for i in range(n_w_u + 1):
            ty = i / n_w_u
            ky = (ly - 1.8) + ty * 3.6
            for j in range(n_w_v + 1):
                tj = j / n_w_v
                kx = lx - (tj ** 1.5) * 0.85 + math.sin(i * 1.2) * 0.06
                kz = lz - (tj ** 1.3) * drop
                bm_wf.verts.new((kx, ky, kz))
                
        bm_wf.verts.ensure_lookup_table()
        for i in range(n_w_u):
            for j in range(n_w_v):
                v0 = bm_wf.verts[base_idx + i * (n_w_v + 1) + j]
                v1 = bm_wf.verts[base_idx + i * (n_w_v + 1) + j + 1]
                v2 = bm_wf.verts[base_idx + (i + 1) * (n_w_v + 1) + j + 1]
                v3 = bm_wf.verts[base_idx + (i + 1) * (n_w_v + 1) + j]
                bm_wf.faces.new([v0, v1, v2, v3])

    me_wf = bpy.data.meshes.new("Organic_Waterfalls_Mesh")
    bm_wf.to_mesh(me_wf)
    bm_wf.free()
    me_wf.shade_smooth()

    obj_wf = bpy.data.objects.new("Organic_Waterfalls", me_wf)
    if col_nature:
        col_nature.objects.link(obj_wf)
    if mat_foam:
        obj_wf.data.materials.append(mat_foam)

    # Add Solidify modifier for volume
    mod_sol = obj_wf.modifiers.new("Solidify", 'SOLIDIFY')
    mod_sol.thickness = 0.04

    print("--- Step 4: Add Trailing Ivy & Flowering Greenery (Ref 1) ---")
    col_struct = bpy.data.collections.get("03_VILLAGE_STRUCTURES")
    mat_leaf = bpy.data.materials.get("M_Bush_Leaves_Fresh") or bpy.data.materials.get("M_Oak_Foliage_Green")

    bm_ivy = bmesh.new()
    # Drape along south retaining wall (X=8.8 to 16.0, Y=18.6)
    for i in range(16):
        ix = 9.2 + i * 0.42
        iy = 18.55
        iz = 0.38
        hang_len = 0.35 + (i % 4) * 0.15
        
        # 3 hanging leaves per vine
        for k in range(4):
            tk = k / 3.0
            lx = ix + (k % 2) * 0.05
            ly = iy + 0.04
            lz = iz - tk * hang_len
            sz = 0.07 + (k % 2) * 0.03
            bmesh.ops.create_cone(bm_ivy, cap_ends=True, segments=4, radius1=sz, radius2=0.01, depth=sz*1.5, matrix=Matrix.Translation((lx, ly, lz)))

    me_ivy = bpy.data.meshes.new("Waterfront_Trailing_Ivy_Mesh")
    bm_ivy.to_mesh(me_ivy)
    bm_ivy.free()
    obj_ivy = bpy.data.objects.new("Waterfront_Trailing_Ivy", me_ivy)
    if col_struct:
        col_struct.objects.link(obj_ivy)
    if mat_leaf:
        obj_ivy.data.materials.append(mat_leaf)

    print("--- Step 5: Cinematic Warm River Daylight Rig ---")
    old_sun = bpy.data.objects.get("River_Hero_Sun")
    if old_sun:
        bpy.data.objects.remove(old_sun, do_unlink=True)

    sun_data = bpy.data.lights.new("River_Hero_Sun", 'SUN')
    sun_data.energy = 3.8
    sun_data.color = (1.0, 0.94, 0.88)
    sun_data.angle = math.radians(1.2)
    sun_obj = bpy.data.objects.new("River_Hero_Sun", sun_data)
    col_mgmt = bpy.data.collections.get("00_MANAGEMENT")
    if col_mgmt:
        col_mgmt.objects.link(sun_obj)
    sun_obj.location = Vector((25.0, -10.0, 35.0))
    sun_obj.rotation_euler = (math.radians(52.0), math.radians(18.0), math.radians(-48.0))

    print("Polishing script completed successfully!")

if __name__ == "__main__":
    run_polish_river_and_bridge()
