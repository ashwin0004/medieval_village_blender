"""
build_river_and_bridge.py
=========================
Builds a realistic winding river and high-detail medieval stone arch bridge
based directly on user reference images (Ref 1-5):
  - Ref 1: Winding river with water reflections, stone retaining walls, riverside steps, rowboat, lush riverbank shrubs.
  - Ref 2: Forest cascade / waterfall over mossy boulders into clear shallow pool with submerged smooth pebbles.
  - Ref 3: Stone arch bridge with radial voussoirs, central pier with starlings/cutwaters, and low timber weir waterfall.
  - Ref 4: Riverside street with rustic timber cottages overhanging the water, rocky riverbed with protruding boulders.
  - Ref 5: Epic fantasy river winding through the alpine village valley with waterfalls and distant mountains.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
import random
import os
import shutil
import sys

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import lighting_manager

print("==================================================")
print("   BUILDING MEDIEVAL RIVER & STONE ARCH BRIDGE   ")
print("==================================================")

# ── Helper: Collections ────────────────────────
def get_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

col_nature = get_col("06_ENVIRONMENT_NATURE")
col_struct = get_col("03_VILLAGE_STRUCTURES")
col_mgmt = get_col("00_MANAGEMENT")

# ── 1. Create Dedicated PBR Materials ─────────
def setup_materials():
    print("Setting up enhanced river & bridge materials...")
    
    # 1. M_River_Water_Reflective
    mat_w = bpy.data.materials.get("M_River_Water_Reflective") or bpy.data.materials.new("M_River_Water_Reflective")
    mat_w.use_nodes = True
    nt = mat_w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs['Base Color'].default_value = (0.04, 0.16, 0.20, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['IOR'].default_value = 1.333
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.94
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.94
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-600, 0)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-400, 0)
    mapping.inputs['Scale'].default_value = (2.0, 1.0, 1.0)
    nt.links.new(tc.outputs['Object'], mapping.inputs['Vector'])
    
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-200, 100)
    wave.inputs['Scale'].default_value = 1.8
    wave.inputs['Distortion'].default_value = 3.5
    wave.inputs['Detail'].default_value = 4.0
    nt.links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-200, -150)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 5.0
    nt.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    try:
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = 'RGBA'
        mix.blend_type = 'LINEAR_LIGHT'
        mix.location = (0, 0)
        mix.inputs['Factor'].default_value = 0.25
        nt.links.new(wave.outputs['Color'], mix.inputs[6])
        nt.links.new(noise.outputs['Color'], mix.inputs[7])
        mix_out = mix.outputs['Result']
    except Exception:
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.location = (0, 0)
        mix.blend_type = 'LINEAR_LIGHT'
        mix.inputs['Fac'].default_value = 0.25
        nt.links.new(wave.outputs['Color'], mix.inputs['Color1'])
        nt.links.new(noise.outputs['Color'], mix.inputs['Color2'])
        mix_out = mix.outputs[0]
    
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (150, -100)
    bump.inputs['Strength'].default_value = 0.16
    bump.inputs['Distance'].default_value = 0.08
    nt.links.new(mix_out, bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    try:
        mat_w.blend_method = 'BLEND'
    except Exception:
        pass

    # 2. M_Riverbed_Gravel
    mat_g = bpy.data.materials.get("M_Riverbed_Gravel") or bpy.data.materials.new("M_Riverbed_Gravel")
    mat_g.use_nodes = True
    nt_g = mat_g.node_tree
    nt_g.nodes.clear()
    out_g = nt_g.nodes.new("ShaderNodeOutputMaterial")
    bsdf_g = nt_g.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_g.inputs['Roughness'].default_value = 0.45
    tc_g = nt_g.nodes.new("ShaderNodeTexCoord")
    vor_g = nt_g.nodes.new("ShaderNodeTexVoronoi")
    vor_g.inputs['Scale'].default_value = 24.0
    nt_g.links.new(tc_g.outputs['Object'], vor_g.inputs['Vector'])
    ramp_g = nt_g.nodes.new("ShaderNodeValToRGB")
    ramp_g.color_ramp.elements[0].position = 0.0
    ramp_g.color_ramp.elements[0].color = (0.05, 0.04, 0.03, 1.0)
    ramp_g.color_ramp.elements[1].position = 1.0
    ramp_g.color_ramp.elements[1].color = (0.22, 0.19, 0.15, 1.0)
    nt_g.links.new(vor_g.outputs['Distance'], ramp_g.inputs['Fac'])
    noise_g = nt_g.nodes.new("ShaderNodeTexNoise")
    noise_g.inputs['Scale'].default_value = 35.0
    nt_g.links.new(tc_g.outputs['Object'], noise_g.inputs['Vector'])
    bump_g = nt_g.nodes.new("ShaderNodeBump")
    bump_g.inputs['Strength'].default_value = 0.45
    bump_g.inputs['Distance'].default_value = 0.04
    nt_g.links.new(noise_g.outputs['Fac'], bump_g.inputs['Height'])
    nt_g.links.new(ramp_g.outputs['Color'], bsdf_g.inputs['Base Color'])
    nt_g.links.new(bump_g.outputs['Normal'], bsdf_g.inputs['Normal'])
    nt_g.links.new(bsdf_g.outputs['BSDF'], out_g.inputs['Surface'])

    # 3. M_Water_Foam
    mat_f = bpy.data.materials.get("M_Water_Foam") or bpy.data.materials.new("M_Water_Foam")
    mat_f.use_nodes = True
    nt_f = mat_f.node_tree
    nt_f.nodes.clear()
    out_f = nt_f.nodes.new("ShaderNodeOutputMaterial")
    bsdf_f = nt_f.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_f.inputs['Base Color'].default_value = (0.92, 0.96, 0.98, 1.0)
    bsdf_f.inputs['Roughness'].default_value = 0.75
    if 'Transmission Weight' in bsdf_f.inputs:
        bsdf_f.inputs['Transmission Weight'].default_value = 0.35
    elif 'Transmission' in bsdf_f.inputs:
        bsdf_f.inputs['Transmission'].default_value = 0.35
    tc_f = nt_f.nodes.new("ShaderNodeTexCoord")
    noise_f = nt_f.nodes.new("ShaderNodeTexNoise")
    noise_f.inputs['Scale'].default_value = 32.0
    noise_f.inputs['Detail'].default_value = 8.0
    nt_f.links.new(tc_f.outputs['Object'], noise_f.inputs['Vector'])
    bump_f = nt_f.nodes.new("ShaderNodeBump")
    bump_f.inputs['Strength'].default_value = 0.65
    nt_f.links.new(noise_f.outputs['Fac'], bump_f.inputs['Height'])
    nt_f.links.new(bump_f.outputs['Normal'], bsdf_f.inputs['Normal'])
    nt_f.links.new(bsdf_f.outputs['BSDF'], out_f.inputs['Surface'])

    # 4. M_River_Rock_Wet
    mat_rr = bpy.data.materials.get("M_River_Rock_Wet") or bpy.data.materials.new("M_River_Rock_Wet")
    mat_rr.use_nodes = True
    nt_r = mat_rr.node_tree
    nt_r.nodes.clear()
    out_r = nt_r.nodes.new("ShaderNodeOutputMaterial")
    bsdf_r = nt_r.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_r.inputs['Base Color'].default_value = (0.10, 0.11, 0.10, 1.0)
    bsdf_r.inputs['Roughness'].default_value = 0.18 # wet glossy
    bsdf_r.inputs['Specular IOR Level'].default_value = 0.6 if 'Specular IOR Level' in bsdf_r.inputs else 0.6
    tc_r = nt_r.nodes.new("ShaderNodeTexCoord")
    noise_r = nt_r.nodes.new("ShaderNodeTexNoise")
    noise_r.inputs['Scale'].default_value = 16.0
    nt_r.links.new(tc_r.outputs['Object'], noise_r.inputs['Vector'])
    bump_r = nt_r.nodes.new("ShaderNodeBump")
    bump_r.inputs['Strength'].default_value = 0.45
    nt_r.links.new(noise_r.outputs['Fac'], bump_r.inputs['Height'])
    nt_r.links.new(bump_r.outputs['Normal'], bsdf_r.inputs['Normal'])
    nt_r.links.new(bsdf_r.outputs['BSDF'], out_r.inputs['Surface'])

    # 5. M_Rowboat_Wood
    mat_rb = bpy.data.materials.get("M_Rowboat_Wood") or bpy.data.materials.new("M_Rowboat_Wood")
    mat_rb.use_nodes = True
    nt_rb = mat_rb.node_tree
    nt_rb.nodes.clear()
    out_rb = nt_rb.nodes.new("ShaderNodeOutputMaterial")
    bsdf_rb = nt_rb.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_rb.inputs['Base Color'].default_value = (0.24, 0.16, 0.10, 1.0)
    bsdf_rb.inputs['Roughness'].default_value = 0.75
    tc_rb = nt_rb.nodes.new("ShaderNodeTexCoord")
    wave_rb = nt_rb.nodes.new("ShaderNodeTexWave")
    wave_rb.inputs['Scale'].default_value = 15.0
    nt_rb.links.new(tc_rb.outputs['Object'], wave_rb.inputs['Vector'])
    bump_rb = nt_rb.nodes.new("ShaderNodeBump")
    bump_rb.inputs['Strength'].default_value = 0.35
    nt_rb.links.new(wave_rb.outputs['Color'], bump_rb.inputs['Height'])
    nt_rb.links.new(bump_rb.outputs['Normal'], bsdf_rb.inputs['Normal'])
    nt_rb.links.new(bsdf_rb.outputs['BSDF'], out_rb.inputs['Surface'])

    # 6. M_River_Reeds
    mat_reeds = bpy.data.materials.get("M_River_Reeds") or bpy.data.materials.new("M_River_Reeds")
    mat_reeds.use_nodes = True
    nt_rd = mat_reeds.node_tree
    nt_rd.nodes.clear()
    out_rd = nt_rd.nodes.new("ShaderNodeOutputMaterial")
    bsdf_rd = nt_rd.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_rd.inputs['Base Color'].default_value = (0.12, 0.32, 0.08, 1.0)
    bsdf_rd.inputs['Roughness'].default_value = 0.4
    nt_rd.links.new(bsdf_rd.outputs['BSDF'], out_rd.inputs['Surface'])

    print("River materials ready.")

# ── 2. River Centerline Curve & Terrain Sculpting ───
river_spline = [
    Vector((38.0, 25.0, 3.2)),   # Mountain source
    Vector((28.0, 24.0, 1.2)),   # Upper cascade top
    Vector((22.0, 23.0, -0.55)), # Upper river pool
    Vector((14.0, 22.2, -0.55)), # Barn waterfront
    Vector((6.0, 22.0, -0.55)),  # Under Stone Bridge
    Vector((-2.0, 22.2, -0.55)), # Church pool
    Vector((-10.0, 23.0, -0.7)), # Lower church riverbank
    Vector((-18.0, 23.5, -1.4)), # Western bend
    Vector((-26.0, 21.5, -2.6)), # Ravine rapids
    Vector((-34.0, 19.5, -3.8)), # Gorge cascade
    Vector((-44.0, 18.0, -4.5)), # Valley basin
]

def eval_river_spline(t):
    """Evaluates position and tangent along the river spline for t in [0.0, 1.0]."""
    n_pts = len(river_spline)
    if t <= 0.0:
        p0 = river_spline[0]
        p1 = river_spline[1]
        tan = (p1 - p0).normalized()
        return p0 + tan * (t * 10.0), tan
    if t >= 1.0:
        p0 = river_spline[-2]
        p1 = river_spline[-1]
        tan = (p1 - p0).normalized()
        return p1 + tan * ((t - 1.0) * 10.0), tan
    
    seg_len = 1.0 / (n_pts - 1)
    idx = int(t / seg_len)
    idx = min(idx, n_pts - 2)
    local_t = (t - idx * seg_len) / seg_len
    
    # Cubic Catmull-Rom interpolation
    p0 = river_spline[max(0, idx - 1)]
    p1 = river_spline[idx]
    p2 = river_spline[min(n_pts - 1, idx + 1)]
    p3 = river_spline[min(n_pts - 1, idx + 2)]
    
    pos = 0.5 * (
        (2.0 * p1) +
        (-p0 + p2) * local_t +
        (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * (local_t ** 2) +
        (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * (local_t ** 3)
    )
    tan = 0.5 * (
        (-p0 + p2) +
        2.0 * (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * local_t +
        3.0 * (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * (local_t ** 2)
    ).normalized()
    return pos, tan

def sculpt_riverbed():
    print("Sculpting natural riverbed depression into Terrain_Village...")
    terrain = bpy.data.objects.get("Terrain_Village")
    if not terrain:
        print("Terrain_Village not found!")
        return

    mw = terrain.matrix_world
    mw_inv = mw.inverted()
    mesh = terrain.data
    
    # Ensure M_Riverbed_Gravel is in terrain materials
    mat_gravel = bpy.data.materials.get("M_Riverbed_Gravel")
    gravel_idx = 0
    if mat_gravel:
        if mat_gravel.name not in [m.name for m in mesh.materials if m]:
            mesh.materials.append(mat_gravel)
        gravel_idx = [m.name for m in mesh.materials if m].index(mat_gravel.name)
    
    # Pre-sample spline points
    n_samples = 150
    spline_samples = []
    for i in range(n_samples + 1):
        t = i / n_samples
        pos, tan = eval_river_spline(t)
        spline_samples.append((pos, tan, t))

    carved_count = 0
    for v in mesh.vertices:
        w_co = mw @ v.co
        vx, vy, vz = w_co.x, w_co.y, w_co.z
        
        # Only check near northern valley strip
        if vy < 14.0 or vy > 32.0 or vx < -46.0 or vx > 40.0:
            continue
            
        # Find closest point on spline
        best_dist = 9999.0
        best_pos = None
        for pos, tan, t in spline_samples:
            dx = vx - pos.x
            dy = vy - pos.y
            d = math.sqrt(dx*dx + dy*dy)
            if d < best_dist:
                best_dist = d
                best_pos = pos
        
        # River width parameters
        half_w = 3.8
        if best_pos.x > 18.0:
            half_w = 4.2 # wider upper pool
        elif best_pos.x < -20.0:
            half_w = 4.5 # wider gorge
        
        water_z = best_pos.z
        bed_depth = 1.15
        
        if best_dist < half_w:
            # Channel center
            target_z = water_z - bed_depth * (1.0 - 0.7 * (best_dist / half_w)**2)
            # Under the stone bridge (around X=6), ensure clearance for arches
            if 3.0 <= vx <= 9.0:
                target_z = min(target_z, -1.65)
            if vz > target_z:
                new_w = Vector((vx, vy, target_z))
                v.co = mw_inv @ new_w
                carved_count += 1
        elif best_dist < half_w + 2.5:
            # Bank transition slope
            blend = (best_dist - half_w) / 2.5
            smooth_b = blend * blend * (3.0 - 2.0 * blend)
            target_z = (water_z + 0.15) * (1.0 - smooth_b) + vz * smooth_b
            if vz > target_z:
                new_w = Vector((vx, vy, target_z))
                v.co = mw_inv @ new_w
                carved_count += 1

    mesh.update()
    print(f"Sculpted river channel: updated {carved_count} terrain vertices.")

# ── 3. Build Realistic River Surface Mesh ───────
def build_river_surface():
    print("Building high-detail River_Surface mesh...")
    old_river = bpy.data.objects.get("River_Surface")
    if old_river:
        bpy.data.objects.remove(old_river, do_unlink=True)
    
    col_terr = get_col("99_TERRAIN_ATMOSPHERE")
    bm = bmesh.new()
    
    n_steps = 120
    n_cross = 8
    
    verts_grid = []
    for i in range(n_steps + 1):
        t = i / n_steps
        pos, tan = eval_river_spline(t)
        
        # Normal vector perpendicular to flow
        norm = Vector((-tan.y, tan.x, 0.0)).normalized()
        
        # River width
        half_w = 3.8
        if pos.x > 18.0:
            half_w = 4.2
        elif pos.x < -20.0:
            half_w = 4.8
            
        row = []
        for j in range(n_cross + 1):
            s = j / n_cross
            offset = (s - 0.5) * (half_w * 2.0)
            
            # Subtle water surface dip at edges and center
            vpos = pos + norm * offset
            # Center of village (X between -12 and 22): perfectly level water surface
            if -12.0 <= pos.x <= 22.0:
                vpos.z = -0.55
            elif pos.x > 22.0:
                # Upstream slope/terraces
                vpos.z = pos.z
            else:
                # Downstream ravine slope
                vpos.z = pos.z
                
            bv = bm.verts.new(vpos)
            row.append(bv)
        verts_grid.append(row)
        
    bm.verts.ensure_lookup_table()
    for i in range(n_steps):
        for j in range(n_cross):
            v0 = verts_grid[i][j]
            v1 = verts_grid[i][j+1]
            v2 = verts_grid[i+1][j+1]
            v3 = verts_grid[i+1][j]
            bm.faces.new([v0, v1, v2, v3])
            
    me = bpy.data.meshes.new("River_Surface_Mesh")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    
    river_obj = bpy.data.objects.new("River_Surface", me)
    col_terr.objects.link(river_obj)
    
    mat_w = bpy.data.materials.get("M_River_Water_Reflective")
    if mat_w:
        river_obj.data.materials.append(mat_w)
        
    print(f"River_Surface created: {len(me.vertices)} verts, {len(me.polygons)} polys.")
    return river_obj

# ── 4. Build Waterfalls & Weirs (Ref 2, 3, 5) ────
def build_waterfalls_and_weirs():
    print("Building waterfalls and bridge weir cascades...")
    
    mat_foam = bpy.data.materials.get("M_Water_Foam")
    mat_wood = bpy.data.materials.get("M_Wood_Dark_Timber") or bpy.data.materials.get("M_Wood_Aged_Oak")
    
    # 1. Bridge Weir Waterfall (Ref 3)
    # Low wooden timber weir right between the bridge piers at X = 5.2
    bm_weir = bmesh.new()
    
    # Timber sill beam
    w_beam = 0.22
    h_beam = 0.40
    p0 = Vector((5.2, 19.3, -0.50))
    p1 = Vector((5.2, 24.7, -0.50))
    
    v0 = bm_weir.verts.new(p0 + Vector((-w_beam*0.5, 0, 0)))
    v1 = bm_weir.verts.new(p0 + Vector((w_beam*0.5, 0, 0)))
    v2 = bm_weir.verts.new(p0 + Vector((w_beam*0.5, 0, -h_beam)))
    v3 = bm_weir.verts.new(p0 + Vector((-w_beam*0.5, 0, -h_beam)))
    
    v4 = bm_weir.verts.new(p1 + Vector((-w_beam*0.5, 0, 0)))
    v5 = bm_weir.verts.new(p1 + Vector((w_beam*0.5, 0, 0)))
    v6 = bm_weir.verts.new(p1 + Vector((w_beam*0.5, 0, -h_beam)))
    v7 = bm_weir.verts.new(p1 + Vector((-w_beam*0.5, 0, -h_beam)))
    
    bm_weir.faces.new([v0, v1, v5, v4]) # top
    bm_weir.faces.new([v1, v2, v6, v5]) # front
    bm_weir.faces.new([v2, v3, v7, v6]) # bottom
    bm_weir.faces.new([v3, v0, v4, v7]) # back
    
    me_weir = bpy.data.meshes.new("Bridge_Weir_Timber_Mesh")
    bm_weir.to_mesh(me_weir)
    bm_weir.free()
    obj_weir = bpy.data.objects.new("Bridge_Weir_Timber", me_weir)
    col_struct.objects.link(obj_weir)
    if mat_wood:
        obj_weir.data.materials.append(mat_wood)
        
    # Cascading water sheet + foam curtain over weir
    bm_foam = bmesh.new()
    
    # Vertical curved waterfall drop (drop = 0.35m)
    wf_steps = 16
    for i in range(wf_steps):
        y0 = 19.4 + (i / wf_steps) * 5.2
        y1 = 19.4 + ((i + 1) / wf_steps) * 5.2
        
        # Quad 1: crest curve
        va0 = bm_foam.verts.new((5.25, y0, -0.48))
        va1 = bm_foam.verts.new((5.25, y1, -0.48))
        va2 = bm_foam.verts.new((5.10, y1, -0.62))
        va3 = bm_foam.verts.new((5.10, y0, -0.62))
        bm_foam.faces.new([va0, va1, va2, va3])
        
        # Quad 2: vertical drop curtain
        va4 = bm_foam.verts.new((5.05, y1, -0.85))
        va5 = bm_foam.verts.new((5.05, y0, -0.85))
        bm_foam.faces.new([va3, va2, va4, va5])
        
        # Quad 3: base turbulent boil pool
        va6 = bm_foam.verts.new((4.50, y1, -0.83))
        va7 = bm_foam.verts.new((4.50, y0, -0.83))
        bm_foam.faces.new([va5, va4, va6, va7])
        
    # 2. Upstream East Foothill Waterfall (Ref 2, 5)
    # Cascading drop from X=27 down to X=22 (drop of 1.8m)
    for step_idx in range(3):
        sx = 26.5 - step_idx * 1.8
        sy = 23.5 + (step_idx % 2) * 0.3
        sz = 1.0 - step_idx * 0.55
        
        for k in range(8):
            ky0 = sy - 2.0 + k * 0.5
            ky1 = sy - 2.0 + (k + 1) * 0.5
            vb0 = bm_foam.verts.new((sx + 0.3, ky0, sz))
            vb1 = bm_foam.verts.new((sx + 0.3, ky1, sz))
            vb2 = bm_foam.verts.new((sx - 0.4, ky1, sz - 0.48))
            vb3 = bm_foam.verts.new((sx - 0.4, ky0, sz - 0.48))
            bm_foam.faces.new([vb0, vb1, vb2, vb3])
            
            # Base boil
            vb4 = bm_foam.verts.new((sx - 1.0, ky1, sz - 0.52))
            vb5 = bm_foam.verts.new((sx - 1.0, ky0, sz - 0.52))
            bm_foam.faces.new([vb3, vb2, vb4, vb5])

    me_foam = bpy.data.meshes.new("River_Waterfall_Foam_Mesh")
    bm_foam.to_mesh(me_foam)
    bm_foam.free()
    me_foam.shade_smooth()
    
    obj_foam = bpy.data.objects.new("River_Waterfall_Foam", me_foam)
    col_nature.objects.link(obj_foam)
    if mat_foam:
        obj_foam.data.materials.append(mat_foam)
        
    print("Bridge weir and upstream waterfalls created.")

# ── 5. Build Medieval Stone Arch Bridge (Ref 1 & 3) ───
def build_medieval_stone_bridge():
    print("Constructing high-detail Medieval Stone Arch Bridge...")
    
    # Remove old blockout bridge objects
    for name in ["Stone_Bridge_Deck", "Stone_Bridge_Pier_-1", "Stone_Bridge_Pier_1", "Stone_Bridge_Rail_-1", "Stone_Bridge_Rail_1"]:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Also clean previous upgraded bridge parts if re-running
    for o in list(bpy.data.objects):
        if o.name.startswith("Stone_Bridge_") and o.name not in ["Stone_Bridge_Abutment", "Stone_Bridge_Voussoirs"]:
            bpy.data.objects.remove(o, do_unlink=True)

    mat_ashlar = bpy.data.materials.get("M_Stone_Bridge_Ashlar") or bpy.data.materials.get("M_Stone_Ashlar_Grey")
    mat_voussoir = bpy.data.materials.get("M_Stone_Bridge_Voussoir") or mat_ashlar
    mat_moss = bpy.data.materials.get("M_Stone_Waterline_Moss") or mat_ashlar
    mat_cobble = bpy.data.materials.get("M_Cobblestone_Road")
    mat_iron = bpy.data.materials.get("M_Iron_Wrought")
    mat_lantern = bpy.data.materials.get("M_Lantern_Warm")
    
    # Dimensions:
    # Road runs along X=6.0, crossing from South (Y=17.2) to North (Y=26.8). Length = 9.6m
    # Road width: 5.6m (from X = 3.2 to X = 8.8)
    
    # ── A. Stone Abutments (South & North) ───────
    bm_abut = bmesh.new()
    
    # South Abutment (Y=17.0..18.8, Z=-1.8..0.35)
    bmesh.ops.create_cube(bm_abut, size=1.0, matrix=Matrix.Translation((6.0, 17.9, -0.65)) @ Matrix.Scale(5.8, 4, Vector((1, 0, 0))) @ Matrix.Scale(1.8, 4, Vector((0, 1, 0))) @ Matrix.Scale(2.1, 4, Vector((0, 0, 1))))
    # North Abutment (Y=25.2..27.0, Z=-1.8..0.35)
    bmesh.ops.create_cube(bm_abut, size=1.0, matrix=Matrix.Translation((6.0, 26.1, -0.65)) @ Matrix.Scale(5.8, 4, Vector((1, 0, 0))) @ Matrix.Scale(1.8, 4, Vector((0, 1, 0))) @ Matrix.Scale(2.1, 4, Vector((0, 0, 1))))
    
    me_abut = bpy.data.meshes.new("Stone_Bridge_Abutments_Mesh")
    bm_abut.to_mesh(me_abut)
    bm_abut.free()
    obj_abut = bpy.data.objects.new("Stone_Bridge_Abutments", me_abut)
    col_struct.objects.link(obj_abut)
    if mat_ashlar:
        obj_abut.data.materials.append(mat_ashlar)

    # ── B. Central Pier with Triangular Starlings (Cutwaters) ──
    bm_pier = bmesh.new()
    # Central rectangular body (Y=21.2..22.8, X=3.2..8.8, Z=-1.8..0.45)
    bmesh.ops.create_cube(bm_pier, size=1.0, matrix=Matrix.Translation((6.0, 22.0, -0.65)) @ Matrix.Scale(5.6, 4, Vector((1, 0, 0))) @ Matrix.Scale(1.6, 4, Vector((0, 1, 0))) @ Matrix.Scale(2.2, 4, Vector((0, 0, 1))))
    
    # Upstream Starling (East wedge, pointing into current towards X=10.6)
    # Triangle prism: base at X=8.8, Y=[21.2, 22.8], apex at X=10.6, Y=22.0
    v_base_s = bm_pier.verts.new((8.8, 21.2, -1.75))
    v_base_n = bm_pier.verts.new((8.8, 22.8, -1.75))
    v_apex_b = bm_pier.verts.new((10.6, 22.0, -1.75))
    v_base_st = bm_pier.verts.new((8.8, 21.2, 0.45))
    v_base_nt = bm_pier.verts.new((8.8, 22.8, 0.45))
    v_apex_t = bm_pier.verts.new((10.6, 22.0, 0.45))
    
    bm_pier.faces.new([v_base_s, v_base_n, v_base_nt, v_base_st])
    bm_pier.faces.new([v_base_s, v_apex_b, v_apex_t, v_base_st])
    bm_pier.faces.new([v_base_n, v_base_nt, v_apex_t, v_apex_b])
    bm_pier.faces.new([v_base_st, v_base_nt, v_apex_t]) # top starling cap
    
    # Downstream Starling (West wedge, pointing to X=1.4)
    w_base_s = bm_pier.verts.new((3.2, 21.2, -1.75))
    w_base_n = bm_pier.verts.new((3.2, 22.8, -1.75))
    w_apex_b = bm_pier.verts.new((1.4, 22.0, -1.75))
    w_base_st = bm_pier.verts.new((3.2, 21.2, 0.45))
    w_base_nt = bm_pier.verts.new((3.2, 22.8, 0.45))
    w_apex_t = bm_pier.verts.new((1.4, 22.0, 0.45))
    
    bm_pier.faces.new([w_base_s, w_base_st, w_base_nt, w_base_n])
    bm_pier.faces.new([w_base_s, w_apex_b, w_apex_t, w_base_st])
    bm_pier.faces.new([w_base_n, w_base_nt, w_apex_t, w_apex_b])
    bm_pier.faces.new([w_base_st, w_apex_t, w_base_nt])
    
    me_pier = bpy.data.meshes.new("Stone_Bridge_Pier_Mesh")
    bm_pier.to_mesh(me_pier)
    bm_pier.free()
    obj_pier = bpy.data.objects.new("Stone_Bridge_Pier", me_pier)
    col_struct.objects.link(obj_pier)
    if mat_moss:
        obj_pier.data.materials.append(mat_moss)

    # ── C. Semicircular Barrel Arches (South & North) ─
    bm_arch = bmesh.new()
    
    # Arch 1 (South): Y from 18.8 to 21.2. Center Y=20.0, Span=2.4m, Radius=1.2m
    # Arch 2 (North): Y from 22.8 to 25.2. Center Y=24.0, Span=2.4m, Radius=1.2m
    arch_centers = [20.0, 24.0]
    rad = 1.18
    spring_z = -0.40
    n_rad_seg = 14
    width_x = 5.6
    x_min = 3.2
    
    for c_y in arch_centers:
        arc_verts = []
        for a_idx in range(n_rad_seg + 1):
            theta = math.pi * (a_idx / n_rad_seg) # 0 to pi
            ay = c_y - math.cos(theta) * rad
            az = spring_z + math.sin(theta) * rad
            
            # Intrados row across X
            r_east = bm_arch.verts.new((x_min + width_x, ay, az))
            r_west = bm_arch.verts.new((x_min, ay, az))
            arc_verts.append((r_west, r_east))
            
        for a_idx in range(n_rad_seg):
            w0, e0 = arc_verts[a_idx]
            w1, e1 = arc_verts[a_idx + 1]
            bm_arch.faces.new([w0, e0, e1, w1]) # barrel vault underside
            
    me_arch = bpy.data.meshes.new("Stone_Bridge_Vaults_Mesh")
    bm_arch.to_mesh(me_arch)
    bm_arch.free()
    me_arch.shade_smooth()
    obj_arch = bpy.data.objects.new("Stone_Bridge_Vaults", me_arch)
    col_struct.objects.link(obj_arch)
    if mat_ashlar:
        obj_arch.data.materials.append(mat_ashlar)

    # ── D. Spandrel Walls & Dressed Stone Voussoirs (Ref 3) ───
    bm_voussoir = bmesh.new()
    v_thick = 0.28 # ring thickness outward
    v_depth = 0.22 # stone depth
    
    for c_y in arch_centers:
        for face_x, norm_x in [(x_min, -1), (x_min + width_x, 1)]:
            for a_idx in range(n_rad_seg):
                th0 = math.pi * (a_idx / n_rad_seg)
                th1 = math.pi * ((a_idx + 1) / n_rad_seg)
                
                # Inner ring points
                iy0 = c_y - math.cos(th0) * rad
                iz0 = spring_z + math.sin(th0) * rad
                iy1 = c_y - math.cos(th1) * rad
                iz1 = spring_z + math.sin(th1) * rad
                
                # Outer ring points
                oy0 = c_y - math.cos(th0) * (rad + v_thick)
                oz0 = spring_z + math.sin(th0) * (rad + v_thick)
                oy1 = c_y - math.cos(th1) * (rad + v_thick)
                oz1 = spring_z + math.sin(th1) * (rad + v_thick)
                
                # Chamfer offset for individual stone relief
                chamf = (a_idx % 2) * 0.02
                fx0 = face_x
                fx1 = face_x + norm_x * (v_depth + chamf)
                
                # Front face
                vf0 = bm_voussoir.verts.new((fx1, iy0, iz0))
                vf1 = bm_voussoir.verts.new((fx1, iy1, iz1))
                vf2 = bm_voussoir.verts.new((fx1, oy1, oz1))
                vf3 = bm_voussoir.verts.new((fx1, oy0, oz0))
                bm_voussoir.faces.new([vf0, vf1, vf2, vf3])
                
                # Outer rim face
                vr0 = bm_voussoir.verts.new((fx0, oy0, oz0))
                vr1 = bm_voussoir.verts.new((fx0, oy1, oz1))
                bm_voussoir.faces.new([vf3, vf2, vr1, vr0])

    me_voussoir = bpy.data.meshes.new("Stone_Bridge_Voussoirs_Mesh")
    bm_voussoir.to_mesh(me_voussoir)
    bm_voussoir.free()
    obj_voussoir = bpy.data.objects.new("Stone_Bridge_Voussoirs", me_voussoir)
    col_struct.objects.link(obj_voussoir)
    if mat_voussoir:
        obj_voussoir.data.materials.append(mat_voussoir)

    # ── E. Humpbacked Cobblestone Road Deck ───────
    bm_deck = bmesh.new()
    y_steps = 24
    x_steps = 6
    deck_y_start = 17.2
    deck_y_end = 26.8
    deck_len = deck_y_end - deck_y_start
    
    deck_grid = []
    for yi in range(y_steps + 1):
        ty = yi / y_steps
        dy = deck_y_start + ty * deck_len
        
        # Parabolic humpback arch: peaks at center Y=22.0
        hump_factor = 1.0 - (2.0 * (ty - 0.5)) ** 2
        dz = 0.32 + hump_factor * 0.35 # Z from 0.32m at ends to 0.67m at center
        
        row = []
        for xi in range(x_steps + 1):
            tx = xi / x_steps
            dx = x_min + tx * width_x
            # Crowned road profile (slight camber 4cm higher in center)
            camber = 0.04 * (1.0 - (2.0 * (tx - 0.5))**2)
            v = bm_deck.verts.new((dx, dy, dz + camber))
            row.append(v)
        deck_grid.append(row)
        
    for yi in range(y_steps):
        for xi in range(x_steps):
            v0 = deck_grid[yi][xi]
            v1 = deck_grid[yi][xi+1]
            v2 = deck_grid[yi+1][xi+1]
            v3 = deck_grid[yi+1][xi]
            bm_deck.faces.new([v0, v1, v2, v3])
            
    me_deck = bpy.data.meshes.new("Stone_Bridge_Deck_Mesh")
    bm_deck.to_mesh(me_deck)
    bm_deck.free()
    obj_deck = bpy.data.objects.new("Stone_Bridge_Deck", me_deck)
    col_struct.objects.link(obj_deck)
    if mat_cobble:
        obj_deck.data.materials.append(mat_cobble)

    # ── F. Ashlar Stone Parapets with Pedestrian Refuges ─
    bm_parapet = bmesh.new()
    
    # Parapet thickness 0.32m, height 0.85m above deck
    p_h = 0.82
    p_w = 0.30
    
    # West Parapet (along X = 3.2, with triangular refuge over starling at Y=22.0)
    # East Parapet (along X = 8.8, with triangular refuge at Y=22.0)
    for side, px, out_dir in [("West", x_min, -1), ("East", x_min + width_x, 1)]:
        pts_p = []
        for yi in range(y_steps + 1):
            ty = yi / y_steps
            py = deck_y_start + ty * deck_len
            hump = 0.32 + (1.0 - (2.0 * (ty - 0.5)) ** 2) * 0.35
            
            # Pedestrian refuge projection at center
            refuge_dist = abs(py - 22.0)
            proj = 0.0
            if refuge_dist < 1.4:
                proj = out_dir * (1.4 - refuge_dist) * 0.85
                
            p_base = Vector((px + proj, py, hump))
            p_top = Vector((px + proj, py, hump + p_h))
            pts_p.append((p_base, p_top))
            
        for yi in range(y_steps):
            b0, t0 = pts_p[yi]
            b1, t1 = pts_p[yi + 1]
            
            # Inner wall face
            vi0 = bm_parapet.verts.new(b0)
            vi1 = bm_parapet.verts.new(b1)
            vi2 = bm_parapet.verts.new(t1)
            vi3 = bm_parapet.verts.new(t0)
            bm_parapet.faces.new([vi0, vi1, vi2, vi3])
            
            # Outer wall face (offset by p_w)
            vo0 = bm_parapet.verts.new(b0 + Vector((out_dir * p_w, 0, 0)))
            vo1 = bm_parapet.verts.new(b1 + Vector((out_dir * p_w, 0, 0)))
            vo2 = bm_parapet.verts.new(t1 + Vector((out_dir * p_w, 0, 0)))
            vo3 = bm_parapet.verts.new(t0 + Vector((out_dir * p_w, 0, 0)))
            bm_parapet.faces.new([vo0, vo3, vo2, vo1])
            
            # Beveled Coping Cap
            bm_parapet.faces.new([vi3, vi2, vo2, vo3])

    me_parapet = bpy.data.meshes.new("Stone_Bridge_Parapets_Mesh")
    bm_parapet.to_mesh(me_parapet)
    bm_parapet.free()
    obj_parapet = bpy.data.objects.new("Stone_Bridge_Parapets", me_parapet)
    col_struct.objects.link(obj_parapet)
    if mat_ashlar:
        obj_parapet.data.materials.append(mat_ashlar)

    # ── G. Wrought Iron Parapet Lanterns ──────────
    # Mounted on the refuge pier posts at (2.4, 22.0) and (9.6, 22.0)
    for lx, ly, lz in [(2.45, 22.0, 1.65), (9.55, 22.0, 1.65)]:
        bm_l = bmesh.new()
        # Post bracket
        bmesh.ops.create_cube(bm_l, size=1.0, matrix=Matrix.Translation((lx, ly, lz - 0.15)) @ Matrix.Scale(0.08, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.35, 4, Vector((0, 0, 1))))
        # Lantern roof cap (cone)
        bmesh.ops.create_cone(bm_l, cap_ends=True, segments=6, radius1=0.18, radius2=0.02, depth=0.15, matrix=Matrix.Translation((lx, ly, lz + 0.16)))
        # Glass glowing core (cylinder)
        bmesh.ops.create_cone(bm_l, cap_ends=True, segments=6, radius1=0.10, radius2=0.12, depth=0.22, matrix=Matrix.Translation((lx, ly, lz)))
        
        me_l = bpy.data.meshes.new(f"Stone_Bridge_Lantern_{lx:.0f}_Mesh")
        bm_l.to_mesh(me_l)
        bm_l.free()
        obj_l = bpy.data.objects.new(f"Stone_Bridge_Lantern_{lx:.0f}", me_l)
        col_struct.objects.link(obj_l)
        if mat_iron:
            obj_l.data.materials.append(mat_iron)
            
        # Point light inside lantern
        pl_data = bpy.data.lights.new(f"Light_Bridge_Lantern_{lx:.0f}", 'POINT')
        pl_data.energy = 45.0
        pl_data.color = (1.0, 0.72, 0.38)
        pl_data.shadow_soft_size = 0.15
        obj_pl = bpy.data.objects.new(f"Light_Bridge_Lantern_{lx:.0f}", pl_data)
        col_struct.objects.link(obj_pl)
        obj_pl.location = Vector((lx, ly, lz))

    print("Medieval Stone Arch Bridge construction complete.")

# ── 6. Build Waterfront Stone Wall & Steps (Ref 1) ──
def build_waterfront_and_boat():
    print("Building village waterfront retaining walls, stone steps and moored rowboat...")
    
    mat_ashlar = bpy.data.materials.get("M_Stone_Bridge_Ashlar") or bpy.data.materials.get("M_Stone_Ashlar_Grey")
    mat_moss = bpy.data.materials.get("M_Stone_Waterline_Moss") or mat_ashlar
    mat_wood = bpy.data.materials.get("M_Wood_Aged_Oak")
    mat_rope = bpy.data.materials.get("M_Rope")
    mat_boat = bpy.data.materials.get("M_Rowboat_Wood") or mat_wood
    
    # 1. Stone Retaining Wall along South Bank
    # Stretches from Bridge abutment (X=8.8) to Fisherman's trail (X=16.5) along Y=18.5
    bm_wall = bmesh.new()
    
    w_len = 16.5 - 8.8
    wall_steps = 14
    for i in range(wall_steps):
        wx0 = 8.8 + (i / wall_steps) * w_len
        wx1 = 8.8 + ((i + 1) / wall_steps) * w_len
        
        wy0 = 18.5 + math.sin(i * 0.4) * 0.25
        wy1 = 18.5 + math.sin((i + 1) * 0.4) * 0.25
        
        # Foundation footing
        v0 = bm_wall.verts.new((wx0, wy0, -1.2))
        v1 = bm_wall.verts.new((wx1, wy1, -1.2))
        v2 = bm_wall.verts.new((wx1, wy1 - 0.45, -1.2))
        v3 = bm_wall.verts.new((wx0, wy0 - 0.45, -1.2))
        
        # Crest top
        v4 = bm_wall.verts.new((wx0, wy0 + 0.1, 0.42))
        v5 = bm_wall.verts.new((wx1, wy1 + 0.1, 0.42))
        v6 = bm_wall.verts.new((wx1, wy1 - 0.45, 0.42))
        v7 = bm_wall.verts.new((wx0, wy0 - 0.45, 0.42))
        
        bm_wall.faces.new([v0, v1, v5, v4]) # water-facing wall
        bm_wall.faces.new([v4, v5, v6, v7]) # coping top
        
    me_wall = bpy.data.meshes.new("Waterfront_Retaining_Wall_Mesh")
    bm_wall.to_mesh(me_wall)
    bm_wall.free()
    obj_wall = bpy.data.objects.new("Waterfront_Retaining_Wall", me_wall)
    col_struct.objects.link(obj_wall)
    if mat_ashlar:
        obj_wall.data.materials.append(mat_ashlar)

    # 2. Weathered Stone Steps descending into the river (Ref 1)
    # Located at X=11.2, descending from road (Y=18.2, Z=0.35) into water (Y=19.6, Z=-0.55)
    bm_steps = bmesh.new()
    num_steps = 6
    st_w = 1.6 # step width
    for s_idx in range(num_steps):
        t = s_idx / num_steps
        sy = 18.2 + t * 1.5
        sz = 0.35 - t * 0.90
        
        step_mat = Matrix.Translation((11.2, sy, sz)) @ Matrix.Scale(st_w, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.38, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.18, 4, Vector((0, 0, 1)))
        bmesh.ops.create_cube(bm_steps, size=1.0, matrix=step_mat)
        
    me_steps = bpy.data.meshes.new("Waterfront_Stone_Steps_Mesh")
    bm_steps.to_mesh(me_steps)
    bm_steps.free()
    obj_steps = bpy.data.objects.new("Waterfront_Stone_Steps", me_steps)
    col_struct.objects.link(obj_steps)
    if mat_moss:
        obj_steps.data.materials.append(mat_moss)

    # 3. Wooden Mooring Post & Coiled Rope
    bm_post = bmesh.new()
    # Vertical timber pile
    bmesh.ops.create_cone(bm_post, cap_ends=True, segments=8, radius1=0.12, radius2=0.10, depth=1.3, matrix=Matrix.Translation((10.1, 18.7, -0.1)))
    # Hemp rope coil
    bmesh.ops.create_cone(bm_post, cap_ends=True, segments=8, radius1=0.16, radius2=0.16, depth=0.18, matrix=Matrix.Translation((10.1, 18.7, 0.25)))
    
    me_post = bpy.data.meshes.new("Waterfront_Mooring_Post_Mesh")
    bm_post.to_mesh(me_post)
    bm_post.free()
    obj_post = bpy.data.objects.new("Waterfront_Mooring_Post", me_post)
    col_struct.objects.link(obj_post)
    if mat_wood:
        obj_post.data.materials.append(mat_wood)

    # 4. Rustic Wooden Rowboat Moored near Steps (Ref 1 & 5)
    # Floating at (10.4, 20.2, -0.52), slightly angled
    bm_boat = bmesh.new()
    boat_mat = Matrix.Translation((10.4, 20.3, -0.48)) @ Matrix.Rotation(math.radians(-22), 4, 'Z')
    
    # Boat Hull: tapered bow and stern
    b_len = 2.6
    b_wid = 1.05
    b_h = 0.44
    
    # Build hull cross sections
    b_sections = [
        (-1.3, 0.05, 0.12), # bow tip
        (-0.7, 0.42, 0.0),  # forward
        (0.0, 0.52, -0.05), # midship
        (0.7, 0.46, 0.0),   # aft
        (1.2, 0.35, 0.08),  # transom stern
    ]
    
    hull_verts = []
    for x_sec, half_w, z_offset in b_sections:
        # Keel bottom
        vk = bm_boat.verts.new(boat_mat @ Vector((x_sec, 0.0, z_offset - b_h * 0.5)))
        # Port gunwale
        vp = bm_boat.verts.new(boat_mat @ Vector((x_sec, -half_w, z_offset + b_h * 0.5)))
        # Starboard gunwale
        vs = bm_boat.verts.new(boat_mat @ Vector((x_sec, half_w, z_offset + b_h * 0.5)))
        hull_verts.append((vk, vp, vs))
        
    for i in range(len(b_sections) - 1):
        k0, p0, s0 = hull_verts[i]
        k1, p1, s1 = hull_verts[i + 1]
        bm_boat.faces.new([k0, p0, p1, k1]) # port planking
        bm_boat.faces.new([k0, k1, s1, s0]) # stbd planking
        
    # Stern transom plate
    k_last, p_last, s_last = hull_verts[-1]
    bm_boat.faces.new([k_last, p_last, s_last])
    
    # Wooden thwart (seat bench)
    bmesh.ops.create_cube(bm_boat, size=1.0, matrix=boat_mat @ Matrix.Translation((0.1, 0, 0.05)) @ Matrix.Scale(0.24, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.95, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))))
    
    # Two Wooden Oars inside boat
    bmesh.ops.create_cone(bm_boat, cap_ends=True, segments=6, radius1=0.03, radius2=0.03, depth=1.8, matrix=boat_mat @ Matrix.Translation((-0.1, 0.15, 0.08)) @ Matrix.Rotation(math.radians(12), 4, 'Z'))
    bmesh.ops.create_cone(bm_boat, cap_ends=True, segments=6, radius1=0.03, radius2=0.03, depth=1.8, matrix=boat_mat @ Matrix.Translation((-0.1, -0.15, 0.08)) @ Matrix.Rotation(math.radians(-10), 4, 'Z'))
    
    me_boat = bpy.data.meshes.new("Waterfront_Rowboat_Mesh")
    bm_boat.to_mesh(me_boat)
    bm_boat.free()
    obj_boat = bpy.data.objects.new("Waterfront_Rowboat", me_boat)
    col_struct.objects.link(obj_boat)
    if mat_boat:
        obj_boat.data.materials.append(mat_boat)

    print("Waterfront wall, steps and rowboat complete.")

# ── 7. Place River Rocks, Pebbles & Reeds (Ref 1-4) ──
def place_river_environment():
    print("Placing wet river boulders, submerged pebbles and river reeds...")
    
    mat_rock = bpy.data.materials.get("M_River_Rock_Wet")
    mat_pebble = bpy.data.materials.get("M_Riverbed_Gravel")
    mat_reeds = bpy.data.materials.get("M_River_Reeds")
    
    # 1. Wet River Boulders along banks & waterfall pools
    boulder_locs = [
        # Upstream waterfall pool (East)
        (25.5, 22.0, 0.2, 1.4), (26.2, 24.5, 0.4, 1.6), (24.0, 21.5, -0.2, 1.3),
        (23.2, 24.2, -0.1, 1.5), (21.5, 21.8, -0.4, 1.2), (20.8, 23.8, -0.3, 1.4),
        # Around Bridge Starlings & Abutments
        (8.5, 20.2, -0.45, 1.2), (8.7, 23.8, -0.45, 1.1), (10.8, 22.0, -0.42, 1.3), # Upstream Starling
        (3.5, 20.1, -0.48, 1.2), (3.3, 23.9, -0.48, 1.1), (1.2, 22.0, -0.45, 1.4), # Downstream Starling
        # South Retaining Wall base
        (13.2, 19.8, -0.48, 0.9), (15.5, 19.6, -0.45, 1.1), (7.2, 19.4, -0.46, 0.8),
        # North bank across from village
        (5.2, 25.2, -0.35, 1.3), (8.2, 25.4, -0.38, 1.2), (12.0, 24.8, -0.40, 1.4),
        (16.5, 24.5, -0.35, 1.5), (-1.5, 24.6, -0.42, 1.3), (-5.5, 24.8, -0.45, 1.4),
        # Church & Lower Pools
        (-3.2, 20.8, -0.48, 1.1), (-7.5, 21.2, -0.52, 1.2), (-11.2, 21.8, -0.60, 1.4),
        # Western Gorge rapids
        (-18.5, 22.2, -1.2, 1.6), (-23.5, 21.0, -2.1, 1.8), (-28.2, 20.5, -3.1, 2.0)
    ]
    
    bm_rb = bmesh.new()
    for i, (bx, by, bz, bsz) in enumerate(boulder_locs):
        rot = Matrix.Rotation(i * 1.3, 4, 'Z') @ Matrix.Rotation(i * 0.7, 4, 'X')
        scale = Matrix.Scale(bsz * 0.9, 4, Vector((1, 0, 0))) @ Matrix.Scale(bsz * 0.8, 4, Vector((0, 1, 0))) @ Matrix.Scale(bsz * 0.65, 4, Vector((0, 0, 1)))
        b_mat = Matrix.Translation((bx, by, bz)) @ rot @ scale
        bmesh.ops.create_icosphere(bm_rb, subdivisions=2, radius=0.6, matrix=b_mat)
        
    me_rb = bpy.data.meshes.new("River_Boulders_Wet_Mesh")
    bm_rb.to_mesh(me_rb)
    bm_rb.free()
    me_rb.shade_smooth()
    obj_rb = bpy.data.objects.new("River_Boulders_Wet", me_rb)
    col_nature.objects.link(obj_rb)
    if mat_rock:
        obj_rb.data.materials.append(mat_rock)

    # 2. Submerged Smooth Pebbles in Shallow Water (Ref 2, 4)
    bm_peb = bmesh.new()
    random.seed(101)
    for k in range(65):
        # Cluster in the shallow pool between bridge and steps
        px = 6.5 + random.random() * 8.0
        py = 19.5 + random.random() * 4.0
        pz = -0.68 + random.random() * 0.10 # submerged below water (-0.55m)
        psz = 0.08 + random.random() * 0.14
        
        rot = Matrix.Rotation(random.random() * 6.28, 4, 'Z')
        p_mat = Matrix.Translation((px, py, pz)) @ rot @ Matrix.Scale(psz, 4, Vector((1, 0, 0))) @ Matrix.Scale(psz * 0.8, 4, Vector((0, 1, 0))) @ Matrix.Scale(psz * 0.5, 4, Vector((0, 0, 1)))
        bmesh.ops.create_icosphere(bm_peb, subdivisions=1, radius=1.0, matrix=p_mat)
        
    me_peb = bpy.data.meshes.new("River_Pebbles_Submerged_Mesh")
    bm_peb.to_mesh(me_peb)
    bm_peb.free()
    obj_peb = bpy.data.objects.new("River_Pebbles_Submerged", me_peb)
    col_nature.objects.link(obj_peb)
    if mat_pebble:
        obj_peb.data.materials.append(mat_pebble)

    # 3. River Reeds & Rushes (Ref 1, 2)
    bm_reeds = bmesh.new()
    reed_clusters = [
        (9.5, 19.5), (13.5, 19.2), (15.8, 19.0),
        (5.5, 24.8), (11.0, 24.2), (14.5, 23.8),
        (-2.5, 24.0), (-6.5, 23.8), (-10.5, 23.2),
        (21.0, 24.2), (23.5, 22.2)
    ]
    for cx, cy in reed_clusters:
        for r_i in range(12):
            rx = cx + (random.random() - 0.5) * 0.8
            ry = cy + (random.random() - 0.5) * 0.8
            rz = -0.58
            rh = 0.65 + random.random() * 0.55
            
            p0 = Vector((rx, ry, rz))
            p1 = Vector((rx + (random.random() - 0.5)*0.1, ry + (random.random() - 0.5)*0.1, rz + rh))
            
            # Simple blade ribbon
            w = 0.015
            v0 = bm_reeds.verts.new(p0 + Vector((-w, 0, 0)))
            v1 = bm_reeds.verts.new(p0 + Vector((w, 0, 0)))
            v2 = bm_reeds.verts.new(p1)
            bm_reeds.faces.new([v0, v1, v2])
            
    me_reeds = bpy.data.meshes.new("River_Reeds_Bank_Mesh")
    bm_reeds.to_mesh(me_reeds)
    bm_reeds.free()
    obj_reeds = bpy.data.objects.new("River_Reeds_Bank", me_reeds)
    col_nature.objects.link(obj_reeds)
    if mat_reeds:
        obj_reeds.data.materials.append(mat_reeds)

    print("River rocks, submerged pebbles and reeds placed.")

# ── 8. Setup Showcase Cameras (Ref 1-5) ─────────
def setup_showcase_cameras():
    print("Setting up cinematic river & bridge showcase cameras...")
    
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
    
    # 1. Cam_River_Bridge_Hero (Ref 1): Ground-level view looking West along water to stone bridge
    # Captures arch reflection, voussoirs, rowboat, stone steps, and cottages
    cams["Cam_River_Bridge_Hero"] = make_cam(
        "Cam_River_Bridge_Hero",
        loc=(13.2, 16.8, 0.45),
        target=(6.0, 21.8, 0.20),
        lens=36.0
    )
    
    # 2. Cam_River_Waterfall_Cascade (Ref 2 & 3): Close-up of bridge weir waterfall & foaming rapids
    cams["Cam_River_Waterfall_Cascade"] = make_cam(
        "Cam_River_Waterfall_Cascade",
        loc=(2.2, 19.8, 0.15),
        target=(5.2, 22.0, -0.45),
        lens=42.0
    )
    
    # 3. Cam_River_Village_Vista (Ref 5): High panoramic view of river winding through village
    cams["Cam_River_Village_Vista"] = make_cam(
        "Cam_River_Village_Vista",
        loc=(-16.0, 36.0, 14.0),
        target=(6.0, 20.0, 2.0),
        lens=28.0
    )
    
    # 4. Cam_River_Sunset_Reflections (Ref 1 & 4): Sunset reflections on calm river waters
    cams["Cam_River_Sunset_Reflections"] = make_cam(
        "Cam_River_Sunset_Reflections",
        loc=(15.5, 17.2, 0.75),
        target=(6.0, 21.5, 0.40),
        lens=34.0
    )

    print("All 4 showcase cameras configured.")
    return cams

def run_build_river_and_bridge():
    # ── Master Execution ───────────────────────────
    setup_materials()
    sculpt_riverbed()
    build_river_surface()
    build_waterfalls_and_weirs()
    build_medieval_stone_bridge()
    build_waterfront_and_boat()
    place_river_environment()
    cams = setup_showcase_cameras()

    print("==================================================")
    print("RIVER & MEDIEVAL STONE ARCH BRIDGE BUILD COMPLETE!")
    print("==================================================")
    return cams

if __name__ == "__main__":
    run_build_river_and_bridge()

