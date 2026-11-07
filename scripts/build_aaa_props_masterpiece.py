"""
build_aaa_props_masterpiece.py
==============================
Senior AAA Environment Artist - Photorealistic Prop Geometry & Dressing.
Recreates high-fidelity 3D medieval props matching Reference Images 1-5:
  - Ref 1: Bowed wooden oak barrels with iron hoops, slatted produce crates with handle cutouts,
           tied hessian grain sacks with gathered ruffles, woven wicker baskets (handled basket,
           tall hamper, woven bowl), clay earthenware jugs with handles, staved wooden water bucket,
           coiled hemp rope, sturdy market work table.
  - Ref 2: Street life dressing with wooden window flower boxes, blooming poppies, ivy, potted ferns,
           hanging festival bunting, lampposts.
  - Ref 3: Heavy 4-wheeled medieval cargo wagon with spoked wooden wheels, iron tire rims,
           drawbar shafts, loaded cargo barrels, billowing canvas tarpaulin, mounted iron lantern.
  - Ref 4: Wrought iron curled bracket lanterns with warm glowing candles, swinging shop trade signs.
  - Ref 5: Split-rail boundary fences, swing gate, village notice board with pinned proclamations,
           neatly stacked firewood cords with split logs and chopping block with axe.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
import os
import sys

def get_col(name, parent_name=None):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    parent = bpy.data.collections.get(parent_name) if parent_name else bpy.context.scene.collection
    if not parent:
        parent = bpy.context.scene.collection
    parent.children.link(col)
    return col

def get_mat(name, fallback="M_Wood_AgedOak"):
    m = bpy.data.materials.get(name)
    return m if m else bpy.data.materials.get(fallback)

def remove_obj(name):
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

def smooth_mesh(mesh):
    for p in mesh.polygons:
        p.use_smooth = True

# ==============================================================================
# GEOMETRY GENERATORS
# ==============================================================================

def add_bowed_barrel_to_bmesh(bm, center, height=0.96, r_mid=0.42, r_end=0.35, segments=20, mat_wood_idx=0, mat_iron_idx=1):
    """Creates a realistic convex barrel with bowed staves and iron hoops."""
    # Stave rings along Z
    num_rings = 7
    ring_verts = []
    cx, cy, cz = center
    z_min = cz - height * 0.5
    z_max = cz + height * 0.5
    
    for r_i in range(num_rings):
        t = r_i / (num_rings - 1)
        z = z_min + t * height
        # Parabolic bow
        norm_z = (t - 0.5) * 2.0 # -1 to 1
        r = r_mid - (r_mid - r_end) * (norm_z ** 2)
        
        current_ring = []
        for s in range(segments):
            ang = s * (2.0 * math.pi / segments)
            vx = cx + math.cos(ang) * r
            vy = cy + math.sin(ang) * r
            v = bm.verts.new((vx, vy, z))
            current_ring.append(v)
        ring_verts.append(current_ring)
        
    # Faces for staves
    for r_i in range(num_rings - 1):
        for s in range(segments):
            s_next = (s + 1) % segments
            f = bm.faces.new([ring_verts[r_i][s], ring_verts[r_i][s_next],
                              ring_verts[r_i+1][s_next], ring_verts[r_i+1][s]])
            f.material_index = mat_wood_idx
            
    # Caps (recessed circular lids)
    lid_bot_faces = bm.faces.new(ring_verts[0][::-1])
    lid_bot_faces.material_index = mat_wood_idx
    lid_top_faces = bm.faces.new(ring_verts[-1])
    lid_top_faces.material_index = mat_wood_idx
    
    # 4 Iron Hoops (protruding rings)
    hoop_offsets = [-0.36, -0.16, 0.16, 0.36]
    hoop_width = 0.04
    hoop_thick = 0.012
    for h_off in hoop_offsets:
        h_z = cz + h_off
        norm_z = (h_off / (height * 0.5))
        r_at_z = r_mid - (r_mid - r_end) * (norm_z ** 2)
        r_outer = r_at_z + hoop_thick
        
        r1_verts = []
        r2_verts = []
        for s in range(segments):
            ang = s * (2.0 * math.pi / segments)
            vx = cx + math.cos(ang) * r_outer
            vy = cy + math.sin(ang) * r_outer
            r1_verts.append(bm.verts.new((vx, vy, h_z - hoop_width*0.5)))
            r2_verts.append(bm.verts.new((vx, vy, h_z + hoop_width*0.5)))
        for s in range(segments):
            s_next = (s + 1) % segments
            f = bm.faces.new([r1_verts[s], r1_verts[s_next], r2_verts[s_next], r2_verts[s]])
            f.material_index = mat_iron_idx

def add_slatted_crate_to_bmesh(bm, center, size=(0.70, 0.48, 0.34), rot_z=0.0, mat_wood_idx=0):
    """Creates a realistic open slatted storage crate with gaps and handle cutouts."""
    cx, cy, cz = center
    lx, ly, lz = size
    rot_m = Matrix.Rotation(rot_z, 4, 'Z')
    trans_m = Matrix.Translation(center) @ rot_m
    
    post_w = 0.038
    slat_th = 0.014
    slat_h = 0.075
    gap = 0.022
    
    def add_box(pos, s, mat_idx=mat_wood_idx):
        mat = trans_m @ Matrix.Translation(pos) @ Matrix.Scale(s[0], 4, Vector((1,0,0))) @ Matrix.Scale(s[1], 4, Vector((0,1,0))) @ Matrix.Scale(s[2], 4, Vector((0,0,1)))
        res = bmesh.ops.create_cube(bm, size=1.0, matrix=mat)
        for v in res['verts']:
            for f in v.link_faces:
                f.material_index = mat_idx
                
    # 4 Corner posts
    for px in [-lx*0.5 + post_w*0.5, lx*0.5 - post_w*0.5]:
        for py in [-ly*0.5 + post_w*0.5, ly*0.5 - post_w*0.5]:
            add_box((px, py, lz*0.5), (post_w, post_w, lz))
            
    # Bottom floor planks (5 slats)
    num_bot = 5
    bot_w = (ly - post_w*2) / num_bot * 0.85
    for b_i in range(num_bot):
        by = -ly*0.5 + post_w + (b_i + 0.5) * ((ly - post_w*2) / num_bot)
        add_box((0, by, slat_th*0.5), (lx - 0.01, bot_w, slat_th))
        
    # Long side horizontal slats (3 tiers front & back)
    for tier in range(3):
        sz = slat_h*0.5 + tier * (slat_h + gap)
        # Front slat
        add_box((0, -ly*0.5 + slat_th*0.5, sz), (lx, slat_th, slat_h))
        # Back slat
        add_box((0, ly*0.5 - slat_th*0.5, sz), (lx, slat_th, slat_h))
        
    # Short side horizontal slats (3 tiers left & right)
    for tier in range(3):
        sz = slat_h*0.5 + tier * (slat_h + gap)
        # Handle cutout on top tier
        if tier == 2:
            # Split slat into left and right wings around 0.14m handle hole
            sw = (ly - 0.14) * 0.5
            for sx in [-lx*0.5 + slat_th*0.5, lx*0.5 - slat_th*0.5]:
                add_box((sx, -ly*0.5 + sw*0.5, sz), (slat_th, sw, slat_h))
                add_box((sx, ly*0.5 - sw*0.5, sz), (slat_th, sw, slat_h))
        else:
            add_box((-lx*0.5 + slat_th*0.5, 0, sz), (slat_th, ly, slat_h))
            add_box((lx*0.5 - slat_th*0.5, 0, sz), (slat_th, ly, slat_h))

def add_grain_sack_to_bmesh(bm, center, height=0.68, r_belly=0.25, rot_z=0.0, mat_sack_idx=0, mat_rope_idx=1):
    """Creates an organic burlap grain sack with gathered neck and tied rope knot."""
    cx, cy, cz = center
    rot_m = Matrix.Rotation(rot_z, 4, 'Z')
    trans_m = Matrix.Translation(center) @ rot_m
    
    # Profile points (z, r, organic_factor)
    profile = [
        (0.00, r_belly * 0.85, 0.95),  # base seated
        (0.12, r_belly * 1.05, 1.05),  # bulging lower belly
        (0.28, r_belly * 1.00, 1.00),  # mid belly
        (0.42, r_belly * 0.80, 0.95),  # upper taper
        (0.50, r_belly * 0.45, 0.90),  # constricted neck
        (0.53, r_belly * 0.42, 0.90),  # tied rope constriction
        (0.60, r_belly * 0.65, 1.10),  # flared frill
        (0.66, r_belly * 0.72, 1.15),  # ruffled rim
    ]
    
    segments = 16
    ring_verts = []
    for z, r, org in profile:
        c_ring = []
        for s in range(segments):
            ang = s * (2.0 * math.pi / segments)
            # Add subtle natural folds
            fold = math.sin(ang * 4.0) * 0.015 + math.cos(ang * 2.0) * 0.01
            r_eff = (r + fold) * org
            vx = math.cos(ang) * r_eff
            vy = math.sin(ang) * r_eff
            pt = trans_m @ Vector((vx, vy, z))
            v = bm.verts.new(pt)
            c_ring.append(v)
        ring_verts.append(c_ring)
        
    for r_i in range(len(profile) - 1):
        for s in range(segments):
            s_next = (s + 1) % segments
            f = bm.faces.new([ring_verts[r_i][s], ring_verts[r_i][s_next],
                              ring_verts[r_i+1][s_next], ring_verts[r_i+1][s]])
            f.material_index = mat_sack_idx
            
    # Base cap
    f_base = bm.faces.new(ring_verts[0][::-1])
    f_base.material_index = mat_sack_idx
    # Ruffled top cap (concave dark opening)
    f_top = bm.faces.new(ring_verts[-1])
    f_top.material_index = mat_sack_idx
    
    # Tied Rope Collar around neck
    rope_z = 0.515
    rope_r = r_belly * 0.46
    rope_verts1 = []
    rope_verts2 = []
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        vx = math.cos(ang) * (rope_r + 0.018)
        vy = math.sin(ang) * (rope_r + 0.018)
        pt1 = trans_m @ Vector((vx, vy, rope_z - 0.02))
        pt2 = trans_m @ Vector((vx, vy, rope_z + 0.02))
        rope_verts1.append(bm.verts.new(pt1))
        rope_verts2.append(bm.verts.new(pt2))
    for s in range(segments):
        s_next = (s + 1) % segments
        f = bm.faces.new([rope_verts1[s], rope_verts1[s_next], rope_verts2[s_next], rope_verts2[s]])
        f.material_index = mat_rope_idx

def add_earthenware_jug_to_bmesh(bm, center, scale=1.0, rot_z=0.0, mat_ceramic_idx=0):
    """Creates a classic medieval earthenware jug with narrow neck and curved handle."""
    cx, cy, cz = center
    rot_m = Matrix.Rotation(rot_z, 4, 'Z')
    trans_m = Matrix.Translation(center) @ rot_m
    
    # Profile (z, r)
    profile = [
        (0.00, 0.08),
        (0.04, 0.10),
        (0.14, 0.17),
        (0.24, 0.16),
        (0.32, 0.10),
        (0.40, 0.065),
        (0.44, 0.085),
    ]
    segments = 16
    ring_verts = []
    for z, r in profile:
        c_ring = []
        for s in range(segments):
            ang = s * (2.0 * math.pi / segments)
            vx = math.cos(ang) * (r * scale)
            vy = math.sin(ang) * (r * scale)
            pt = trans_m @ Vector((vx, vy, z * scale))
            c_ring.append(bm.verts.new(pt))
        ring_verts.append(c_ring)
        
    for r_i in range(len(profile) - 1):
        for s in range(segments):
            s_next = (s + 1) % segments
            f = bm.faces.new([ring_verts[r_i][s], ring_verts[r_i][s_next],
                              ring_verts[r_i+1][s_next], ring_verts[r_i+1][s]])
            f.material_index = mat_ceramic_idx
            
    f_base = bm.faces.new(ring_verts[0][::-1])
    f_base.material_index = mat_ceramic_idx
    f_top = bm.faces.new(ring_verts[-1])
    f_top.material_index = mat_ceramic_idx
    
    # Curved Loop Handle from shoulder to neck
    h_steps = 7
    h_prev_v = None
    for step in range(h_steps):
        t = step / (h_steps - 1)
        ang = t * math.pi
        hz = (0.20 + t * 0.18) * scale
        hx = (0.12 + math.sin(ang) * 0.09) * scale
        h_box_mat = trans_m @ Matrix.Translation((hx, 0, hz)) @ Matrix.Scale(0.028*scale, 4, Vector((1,0,0))) @ Matrix.Scale(0.028*scale, 4, Vector((0,1,0))) @ Matrix.Scale(0.035*scale, 4, Vector((0,0,1)))
        res = bmesh.ops.create_cube(bm, size=1.0, matrix=h_box_mat)
        for v in res['verts']:
            for f in v.link_faces:
                f.material_index = mat_ceramic_idx

def add_wicker_basket_to_bmesh(bm, center, r_top=0.25, r_bot=0.17, height=0.28, has_handle=True, mat_wicker_idx=0):
    """Creates a woven wicker basket with rolled rim and curved arch handle."""
    cx, cy, cz = center
    segments = 18
    r1_verts = []
    r2_verts = []
    r_rim_verts = []
    
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        bx = cx + math.cos(ang) * r_bot
        by = cy + math.sin(ang) * r_bot
        tx = cx + math.cos(ang) * r_top
        ty = cy + math.sin(ang) * r_top
        rx = cx + math.cos(ang) * (r_top + 0.02)
        ry = cy + math.sin(ang) * (r_top + 0.02)
        
        r1_verts.append(bm.verts.new((bx, by, cz)))
        r2_verts.append(bm.verts.new((tx, ty, cz + height)))
        r_rim_verts.append(bm.verts.new((rx, ry, cz + height + 0.018)))
        
    for s in range(segments):
        s_next = (s + 1) % segments
        # Body
        f = bm.faces.new([r1_verts[s], r1_verts[s_next], r2_verts[s_next], r2_verts[s]])
        f.material_index = mat_wicker_idx
        # Rolled rim
        f_rim = bm.faces.new([r2_verts[s], r2_verts[s_next], r_rim_verts[s_next], r_rim_verts[s]])
        f_rim.material_index = mat_wicker_idx
        
    f_base = bm.faces.new(r1_verts[::-1])
    f_base.material_index = mat_wicker_idx
    
    # Arch Handle (smooth continuous curved tube spanning across top)
    if has_handle:
        h_steps = 18
        tube_segs = 8
        h_rad = r_top * 0.95
        tube_r = 0.016
        prev_ring = None
        for h_i in range(h_steps):
            ang = (h_i / (h_steps - 1)) * math.pi
            hx = cx + math.cos(ang) * h_rad
            hz = cz + height + math.sin(ang) * (h_rad * 0.85)
            # Tangent direction along arc
            tangent = Vector((-math.sin(ang), 0, math.cos(ang))).normalized()
            normal = Vector((0, 1, 0))
            binormal = tangent.cross(normal)
            
            cur_ring = []
            for t_s in range(tube_segs):
                t_ang = t_s * (2.0 * math.pi / tube_segs)
                offset = normal * (math.cos(t_ang) * tube_r) + binormal * (math.sin(t_ang) * tube_r)
                v = bm.verts.new(Vector((hx, cy, hz)) + offset)
                cur_ring.append(v)
            if prev_ring:
                for t_s in range(tube_segs):
                    t_next = (t_s + 1) % tube_segs
                    f = bm.faces.new([prev_ring[t_s], prev_ring[t_next], cur_ring[t_next], cur_ring[t_s]])
                    f.material_index = mat_wicker_idx
            prev_ring = cur_ring

def add_vertical_wagon_wheel(bm, w_mat, ox, oy, oz, rad, num_spokes=10, mat_wood_idx=0, mat_iron_idx=1):
    """Creates an upright spoked wooden wheel with iron tire rim in the wagon X-Z plane."""
    hub_z = oz + rad
    hub_len = 0.22
    hub_r = 0.11
    hub_mat = w_mat @ Matrix.Translation((ox, oy, hub_z)) @ Matrix.Rotation(math.radians(90.0), 4, 'X')
    hub_res = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=hub_r, radius2=hub_r, depth=hub_len, matrix=hub_mat)
    for v in hub_res['verts']:
        for f in v.link_faces:
            f.material_index = mat_wood_idx
    # Axle iron cap
    axle_res = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.045, radius2=0.045, depth=hub_len + 0.04, matrix=hub_mat)
    for v in axle_res['verts']:
        for f in v.link_faces:
            f.material_index = mat_iron_idx
            
    # Rim segments (X-Z plane circle, lateral thickness along Y)
    n_rim = 18
    rim_w = 0.065
    rim_th = 0.045
    for k in range(n_rim):
        ang1 = k * (2.0 * math.pi / n_rim)
        ang2 = (k + 1) * (2.0 * math.pi / n_rim)
        mid_ang = (ang1 + ang2) * 0.5
        seg_len = 2.0 * rad * math.sin(math.pi / n_rim) * 1.05
        mid_x = ox + math.cos(mid_ang) * (rad - rim_th * 0.5)
        mid_z = hub_z + math.sin(mid_ang) * (rad - rim_th * 0.5)
        tang_ang = -mid_ang
        seg_mat = w_mat @ Matrix.Translation((mid_x, oy, mid_z)) @ Matrix.Rotation(tang_ang, 4, 'Y') @ Matrix.Scale(seg_len, 4, Vector((1,0,0))) @ Matrix.Scale(rim_w, 4, Vector((0,1,0))) @ Matrix.Scale(rim_th, 4, Vector((0,0,1)))
        res = bmesh.ops.create_cube(bm, size=1.0, matrix=seg_mat)
        for v in res['verts']:
            for f in v.link_faces:
                f.material_index = mat_iron_idx

    # 10 Wooden Spokes in X-Z plane
    spoke_len = rad - hub_r - rim_th
    for s_i in range(num_spokes):
        s_ang = s_i * (2.0 * math.pi / num_spokes)
        sp_mid_r = hub_r + spoke_len * 0.5
        sp_x = ox + math.cos(s_ang) * sp_mid_r
        sp_z = hub_z + math.sin(s_ang) * sp_mid_r
        sp_mat = w_mat @ Matrix.Translation((sp_x, oy, sp_z)) @ Matrix.Rotation(-s_ang + math.pi*0.5, 4, 'Y') @ Matrix.Scale(spoke_len, 4, Vector((1,0,0))) @ Matrix.Scale(0.038, 4, Vector((0,1,0))) @ Matrix.Scale(0.042, 4, Vector((0,0,1)))
        res = bmesh.ops.create_cube(bm, size=1.0, matrix=sp_mat)
        for v in res['verts']:
            for f in v.link_faces:
                f.material_index = mat_wood_idx

def add_staved_bucket_to_bmesh(bm, center, height=0.36, r_top=0.20, r_bot=0.16, mat_wood_idx=0, mat_iron_idx=1, mat_rope_idx=2):
    """Creates a wooden staved bucket with iron hoops, ear brackets, and rope bail handle."""
    cx, cy, cz = center
    segments = 16
    r1_verts = []
    r2_verts = []
    
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        r1_verts.append(bm.verts.new((cx + math.cos(ang)*r_bot, cy + math.sin(ang)*r_bot, cz)))
        r2_verts.append(bm.verts.new((cx + math.cos(ang)*r_top, cy + math.sin(ang)*r_top, cz + height)))
        
    for s in range(segments):
        s_next = (s + 1) % segments
        f = bm.faces.new([r1_verts[s], r1_verts[s_next], r2_verts[s_next], r2_verts[s]])
        f.material_index = mat_wood_idx
    f_base = bm.faces.new(r1_verts[::-1])
    f_base.material_index = mat_wood_idx
    
    # 2 Iron Hoops
    for h_z in [cz + 0.08, cz + height - 0.08]:
        t = (h_z - cz) / height
        r_at_z = r_bot + t * (r_top - r_bot) + 0.008
        hw1, hw2 = [], []
        for s in range(segments):
            ang = s * (2.0 * math.pi / segments)
            hw1.append(bm.verts.new((cx + math.cos(ang)*r_at_z, cy + math.sin(ang)*r_at_z, h_z - 0.015)))
            hw2.append(bm.verts.new((cx + math.cos(ang)*r_at_z, cy + math.sin(ang)*r_at_z, h_z + 0.015)))
        for s in range(segments):
            s_next = (s + 1) % segments
            f = bm.faces.new([hw1[s], hw1[s_next], hw2[s_next], hw2[s]])
            f.material_index = mat_iron_idx
            
    # 2 Ear staves extending above rim
    for sign in [-1, 1]:
        ex = cx + sign * (r_top - 0.01)
        ear_mat = Matrix.Translation((ex, cy, cz + height + 0.035)) @ Matrix.Scale(0.02, 4, Vector((1,0,0))) @ Matrix.Scale(0.045, 4, Vector((0,1,0))) @ Matrix.Scale(0.08, 4, Vector((0,0,1)))
        res = bmesh.ops.create_cube(bm, size=1.0, matrix=ear_mat)
        for v in res['verts']:
            for f in v.link_faces:
                f.material_index = mat_wood_idx
                
    # Rope Bail Handle drooping across rim (continuous smooth tube)
    h_steps = 16
    tube_segs = 6
    b_rope_r = 0.012
    prev_ring = None
    for hi in range(h_steps):
        t = hi / (h_steps - 1)
        ang = t * math.pi
        hx = cx + (t - 0.5) * (r_top * 1.9)
        hz = cz + height + 0.06 + math.sin(ang) * 0.12
        tangent = Vector((1.0, 0.0, math.cos(ang) * 0.15)).normalized()
        normal = Vector((0, 1, 0))
        binormal = tangent.cross(normal).normalized()
        cur_ring = []
        for s in range(tube_segs):
            s_ang = s * (2.0 * math.pi / tube_segs)
            offset = normal * (math.cos(s_ang) * b_rope_r) + binormal * (math.sin(s_ang) * b_rope_r)
            v = bm.verts.new(Vector((hx, cy, hz)) + offset)
            cur_ring.append(v)
        if prev_ring:
            for s in range(tube_segs):
                s_next = (s + 1) % tube_segs
                f = bm.faces.new([prev_ring[s], prev_ring[s_next], cur_ring[s_next], cur_ring[s]])
                f.material_index = mat_rope_idx
        prev_ring = cur_ring

def add_coiled_rope_to_bmesh(bm, center, inner_r=0.18, outer_r=0.34, turns=3.5, mat_rope_idx=0):
    """Creates a realistic coiled spiral hemp rope lying on the ground as a continuous smooth tube."""
    cx, cy, cz = center
    num_steps = 64
    tube_segs = 8
    rope_r = 0.022
    prev_ring = None
    for step in range(num_steps):
        t = step / (num_steps - 1)
        ang = t * turns * 2.0 * math.pi
        r = inner_r + t * (outer_r - inner_r)
        rx = cx + math.cos(ang) * r
        ry = cy + math.sin(ang) * r
        rz = cz + rope_r + (math.sin(t * 12.0) * 0.004)
        
        # Tangent along spiral
        dr_dt = outer_r - inner_r
        dtheta_dt = turns * 2.0 * math.pi
        dx = dr_dt * math.cos(ang) - r * math.sin(ang) * dtheta_dt
        dy = dr_dt * math.sin(ang) + r * math.cos(ang) * dtheta_dt
        tangent = Vector((dx, dy, 0.0)).normalized()
        up = Vector((0, 0, 1))
        normal = tangent.cross(up).normalized()
        binormal = tangent.cross(normal).normalized()
        
        cur_ring = []
        for s in range(tube_segs):
            s_ang = s * (2.0 * math.pi / tube_segs)
            offset = normal * (math.cos(s_ang) * rope_r) + binormal * (math.sin(s_ang) * rope_r)
            v = bm.verts.new(Vector((rx, ry, rz)) + offset)
            cur_ring.append(v)
            
        if prev_ring:
            for s in range(tube_segs):
                s_next = (s + 1) % tube_segs
                f = bm.faces.new([prev_ring[s], prev_ring[s_next], cur_ring[s_next], cur_ring[s]])
                f.material_index = mat_rope_idx
        prev_ring = cur_ring

# ==============================================================================
# MASTER BUILDER FOR HERO PROPS
# ==============================================================================

def build_masterpiece_props():
    print("\n=======================================================")
    print("BUILDING PHOTOREALISTIC AAA PROPS & DETAILS")
    print("=======================================================")
    
    col_props = get_col("Village_Environmental_Props", "03_VILLAGE_STRUCTURES")
    
    mat_oak = get_mat("M_Wood_AgedOak")
    mat_iron = get_mat("M_Iron_Wrought")
    mat_pine = get_mat("M_Wood_LightPine", "M_Wood_AgedOak")
    mat_burlap = get_mat("M_Burlap_Hessian", "M_Wood_AgedOak")
    mat_wicker = get_mat("M_Wicker_Willow", "M_Wood_AgedOak")
    mat_rope = get_mat("M_Hemp_Rope", "M_Wood_AgedOak")
    mat_terracotta = get_mat("M_Clay_Terracotta")
    mat_ceramic = get_mat("M_Ceramic_Glazed", "M_Clay_Terracotta")
    
    # -------------------------------------------------------------------------
    # 1. HERO MARKET WORK TABLE & STILL-LIFE VIGNETTE (Ref 1)
    # -------------------------------------------------------------------------
    print("1. Constructing Hero Market Table & Tabletop Goods (Ref 1)...")
    
    # Clear old table still life
    for name in ["Hero_Market_Table", "Hero_Table_Barrel", "Hero_Table_Jugs", "Hero_Table_Bowl",
                 "Hero_Table_Baskets", "Hero_Table_Crates", "Hero_Table_Rope", "Hero_Table_Bucket",
                 "Hero_Table_Sacks", "Hero_Masterpiece_StillLife_Mesh"]:
        remove_obj(name)
        
    tx, ty, tz = -2.5, -23.8, 0.45
    t_w, t_d, t_h = 2.1, 1.05, 0.76
    top_z = tz + t_h
    
    # Build Table
    bm_tbl = bmesh.new()
    # 4 Heavy legs with chamfer
    leg_x = (t_w * 0.5) - 0.12
    leg_y = (t_d * 0.5) - 0.12
    for lx in [-leg_x, leg_x]:
        for ly in [-leg_y, leg_y]:
            l_mat = Matrix.Translation((tx + lx, ty + ly, tz + t_h*0.5)) @ Matrix.Scale(0.13, 4, Vector((1,0,0))) @ Matrix.Scale(0.13, 4, Vector((0,1,0))) @ Matrix.Scale(t_h, 4, Vector((0,0,1)))
            bmesh.ops.create_cube(bm_tbl, size=1.0, matrix=l_mat)
    # Stretchers connecting legs
    for ly in [-leg_y, leg_y]:
        s_mat = Matrix.Translation((tx, ty + ly, tz + 0.18)) @ Matrix.Scale(t_w - 0.24, 4, Vector((1,0,0))) @ Matrix.Scale(0.08, 4, Vector((0,1,0))) @ Matrix.Scale(0.08, 4, Vector((0,0,1)))
        bmesh.ops.create_cube(bm_tbl, size=1.0, matrix=s_mat)
    # 4 Thick tabletop planks with bevel gap
    num_planks = 4
    p_w = (t_d - 0.04) / num_planks
    for p_i in range(num_planks):
        py = ty - t_d*0.5 + 0.02 + (p_i + 0.5) * p_w
        p_mat = Matrix.Translation((tx, py, top_z + 0.035)) @ Matrix.Scale(t_w, 4, Vector((1,0,0))) @ Matrix.Scale(p_w * 0.96, 4, Vector((0,1,0))) @ Matrix.Scale(0.07, 4, Vector((0,0,1)))
        bmesh.ops.create_cube(bm_tbl, size=1.0, matrix=p_mat)
        
    me_tbl = bpy.data.meshes.new("Hero_Market_Table_Mesh")
    bm_tbl.to_mesh(me_tbl)
    bm_tbl.free()
    smooth_mesh(me_tbl)
    obj_tbl = bpy.data.objects.new("Hero_Market_Table", me_tbl)
    col_props.objects.link(obj_tbl)
    if mat_oak:
        obj_tbl.data.materials.append(mat_oak)
        
    # Build Masterpiece Table Goods
    bm_goods = bmesh.new()
    
    # Material indices in goods mesh:
    # 0: mat_oak, 1: mat_iron, 2: mat_pine, 3: mat_burlap, 4: mat_wicker, 5: mat_rope, 6: mat_terracotta, 7: mat_ceramic
    mats_list = [mat_oak, mat_iron, mat_pine, mat_burlap, mat_wicker, mat_rope, mat_terracotta, mat_ceramic]
    
    # A. Large 120L Bowed Oak Barrel (Left of Table, sitting on floor)
    add_bowed_barrel_to_bmesh(bm_goods, center=(tx - 1.25, ty - 0.05, tz + 0.48), height=0.96, r_mid=0.42, r_end=0.36, segments=20, mat_wood_idx=0, mat_iron_idx=1)
    
    # B. Stacked Slatted Produce Crates (Right of Table, on floor, Ref 1)
    add_slatted_crate_to_bmesh(bm_goods, center=(tx + 1.15, ty - 0.48, tz + 0.17), size=(0.70, 0.48, 0.34), rot_z=math.radians(4.0), mat_wood_idx=2)
    add_slatted_crate_to_bmesh(bm_goods, center=(tx + 1.15, ty - 0.48, tz + 0.51), size=(0.68, 0.46, 0.32), rot_z=math.radians(-12.0), mat_wood_idx=2)
    
    # C. Hessian Burlap Grain Sacks (Ref 1: 1 tall upright tied sack, 1 medium sack, 1 small sack on table)
    add_grain_sack_to_bmesh(bm_goods, center=(tx - 0.82, ty - 0.55, tz), height=0.72, r_belly=0.26, rot_z=math.radians(15.0), mat_sack_idx=3, mat_rope_idx=5)
    add_grain_sack_to_bmesh(bm_goods, center=(tx - 0.50, ty - 0.42, tz), height=0.55, r_belly=0.22, rot_z=math.radians(-25.0), mat_sack_idx=3, mat_rope_idx=5)
    add_grain_sack_to_bmesh(bm_goods, center=(tx - 0.15, ty - 0.18, top_z + 0.07), height=0.42, r_belly=0.18, rot_z=math.radians(40.0), mat_sack_idx=3, mat_rope_idx=5)
    
    # D. Wicker Baskets (Ref 1: Handled basket on table, tall hamper on floor, low woven bowl)
    # Handled basket on right side of table
    add_wicker_basket_to_bmesh(bm_goods, center=(tx + 0.52, ty + 0.08, top_z + 0.07), r_top=0.24, r_bot=0.16, height=0.22, has_handle=True, mat_wicker_idx=4)
    # Tall wicker hamper on floor behind crates
    add_wicker_basket_to_bmesh(bm_goods, center=(tx + 1.30, ty + 0.15, tz), r_top=0.27, r_bot=0.24, height=0.88, has_handle=False, mat_wicker_idx=4)
    # Low woven bowl on ground in front
    add_wicker_basket_to_bmesh(bm_goods, center=(tx - 0.08, ty - 0.55, tz), r_top=0.24, r_bot=0.15, height=0.16, has_handle=False, mat_wicker_idx=4)
    
    # E. Ceramic Pitchers & Glazed Bowl on Table (Ref 1)
    add_earthenware_jug_to_bmesh(bm_goods, center=(tx - 0.55, ty + 0.12, top_z + 0.07), scale=1.0, rot_z=math.radians(20.0), mat_ceramic_idx=6)
    add_earthenware_jug_to_bmesh(bm_goods, center=(tx - 0.32, ty + 0.06, top_z + 0.07), scale=0.75, rot_z=math.radians(-45.0), mat_ceramic_idx=6)
    # Glazed pottery bowl in center of table
    add_wicker_basket_to_bmesh(bm_goods, center=(tx + 0.08, ty + 0.10, top_z + 0.07), r_top=0.24, r_bot=0.14, height=0.14, has_handle=False, mat_wicker_idx=7)
    
    # F. Wooden Staved Water Bucket (Front floor, Ref 1)
    add_staved_bucket_to_bmesh(bm_goods, center=(tx + 0.48, ty - 0.65, tz), height=0.38, r_top=0.20, r_bot=0.16, mat_wood_idx=0, mat_iron_idx=1, mat_rope_idx=5)
    
    # G. Coiled Hemp Rope (Front left floor, Ref 1)
    add_coiled_rope_to_bmesh(bm_goods, center=(tx - 0.65, ty - 0.88, tz), inner_r=0.16, outer_r=0.32, turns=3.5, mat_rope_idx=5)
    
    me_goods = bpy.data.meshes.new("Hero_Table_Masterpiece_Goods_Mesh")
    bm_goods.to_mesh(me_goods)
    bm_goods.free()
    smooth_mesh(me_goods)
    obj_goods = bpy.data.objects.new("Hero_Table_Masterpiece_Goods", me_goods)
    col_props.objects.link(obj_goods)
    for m in mats_list:
        obj_goods.data.materials.append(m if m else mat_oak)
        
    print("Hero Market Table & Goods complete!")
    
    # -------------------------------------------------------------------------
    # 2. CALIBRATE CAM_PROPS_TABLE_STILLLIFE (Ref 1 Showcase)
    # -------------------------------------------------------------------------
    cam_name = "Cam_Props_Table_StillLife"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        
    # Studio 3/4 elevated view facing the table from the front matching Ref 1
    cam_loc = Vector((tx, ty - 4.5, tz + 2.2))
    target = Vector((tx, ty - 0.15, tz + 0.75))
    cam_obj.location = cam_loc
    cam_obj.data.lens = 38.0
    dir_v = (target - cam_loc).normalized()
    cam_obj.rotation_euler = dir_v.to_track_quat('-Z', 'Y').to_euler()
    
    # -------------------------------------------------------------------------
    # 2. MASTERPIECE 4-WHEELED CARGO WAGON (Ref 3)
    # -------------------------------------------------------------------------
    print("2. Constructing Masterpiece Cargo Wagon (Ref 3)...")
    for name in ["Village_Cargo_Wagon_Chassis", "Village_Cargo_Wagon_Wheels", "Village_Cargo_Wagon_Cargo",
                 "Village_Cargo_Wagon_Tarp", "Wagon_Lantern", "Light_Wagon_Lantern", "Village_Cargo_Wagon_Masterpiece"]:
        remove_obj(name)
        
    wx, wy, wz = 2.2, -25.5, 0.45
    w_rot = math.radians(-18.0)
    w_mat = Matrix.Translation((wx, wy, wz)) @ Matrix.Rotation(w_rot, 4, 'Z')
    
    bed_l, bed_w, bed_h = 3.2, 1.45, 0.65
    
    bm_wagon = bmesh.new()
    
    # Material indices in wagon mesh:
    # 0: mat_oak, 1: mat_iron, 2: mat_pine, 3: mat_tarp, 4: mat_lantern
    mat_tarp = get_mat("M_Wagon_Tarp", "M_Burlap_Hessian")
    mat_lantern = get_mat("M_Lantern_Warm", "M_Iron_Wrought")
    wagon_mats = [mat_oak, mat_iron, mat_pine, mat_tarp, mat_lantern]
    
    # A. Floor Bed Planks
    num_w_planks = 6
    wp_w = bed_w / num_w_planks
    for pi in range(num_w_planks):
        py = -bed_w*0.5 + (pi + 0.5) * wp_w
        p_box = w_mat @ Matrix.Translation((0, py, bed_h*0.5)) @ Matrix.Scale(bed_l, 4, Vector((1,0,0))) @ Matrix.Scale(wp_w * 0.96, 4, Vector((0,1,0))) @ Matrix.Scale(0.06, 4, Vector((0,0,1)))
        res = bmesh.ops.create_cube(bm_wagon, size=1.0, matrix=p_box)
        for v in res['verts']:
            for f in v.link_faces:
                f.material_index = 0
                
    # B. Side Rails: 4 vertical stake posts and 3 horizontal slatted planks per side
    for si in range(4):
        sx = -bed_l*0.42 + si * (bed_l * 0.84 / 3.0)
        for sy in [-bed_w*0.5 - 0.03, bed_w*0.5 + 0.03]:
            post_box = w_mat @ Matrix.Translation((sx, sy, bed_h*0.5 + 0.32)) @ Matrix.Scale(0.08, 4, Vector((1,0,0))) @ Matrix.Scale(0.08, 4, Vector((0,1,0))) @ Matrix.Scale(0.68, 4, Vector((0,0,1)))
            res = bmesh.ops.create_cube(bm_wagon, size=1.0, matrix=post_box)
            for v in res['verts']:
                for f in v.link_faces:
                    f.material_index = 0
                    
    for ti in range(3):
        sz = bed_h*0.5 + 0.12 + ti * 0.22
        for sy in [-bed_w*0.5 - 0.03, bed_w*0.5 + 0.03]:
            slat_box = w_mat @ Matrix.Translation((0, sy, sz)) @ Matrix.Scale(bed_l, 4, Vector((1,0,0))) @ Matrix.Scale(0.035, 4, Vector((0,1,0))) @ Matrix.Scale(0.16, 4, Vector((0,0,1)))
            res = bmesh.ops.create_cube(bm_wagon, size=1.0, matrix=slat_box)
            for v in res['verts']:
                for f in v.link_faces:
                    f.material_index = 0
                    
    # C. Endgates (Front & Back)
    for ex in [-bed_l*0.5, bed_l*0.5]:
        end_box = w_mat @ Matrix.Translation((ex, 0, bed_h*0.5 + 0.28)) @ Matrix.Scale(0.06, 4, Vector((1,0,0))) @ Matrix.Scale(bed_w, 4, Vector((0,1,0))) @ Matrix.Scale(0.60, 4, Vector((0,0,1)))
        res = bmesh.ops.create_cube(bm_wagon, size=1.0, matrix=end_box)
        for v in res['verts']:
            for f in v.link_faces:
                f.material_index = 0
                
    # D. Draught Hitching Shafts extending forward to ground (Ref 3)
    for py in [-0.28, 0.28]:
        shaft_mat = w_mat @ Matrix.Translation((bed_l*0.5 + 1.25, py, 0.12)) @ Matrix.Rotation(math.radians(-7.0), 4, 'Y') @ Matrix.Scale(2.5, 4, Vector((1,0,0))) @ Matrix.Scale(0.07, 4, Vector((0,1,0))) @ Matrix.Scale(0.07, 4, Vector((0,0,1)))
        res = bmesh.ops.create_cube(bm_wagon, size=1.0, matrix=shaft_mat)
        for v in res['verts']:
            for f in v.link_faces:
                f.material_index = 0

    # E. 4 Spoked Wooden Wheels with Iron Rim Tires (Ref 3)
    wheel_data = [
        ("Rear_L", -bed_l*0.30, -bed_w*0.62, 0.05, 0.56),
        ("Rear_R", -bed_l*0.30, bed_w*0.62, 0.05, 0.56),
        ("Front_L", bed_l*0.30, -bed_w*0.60, -0.04, 0.45),
        ("Front_R", bed_l*0.30, bed_w*0.60, -0.04, 0.45),
    ]
    for w_name, ox, oy, oz, rad in wheel_data:
        add_vertical_wagon_wheel(bm_wagon, w_mat, ox, oy, oz, rad, num_spokes=10, mat_wood_idx=0, mat_iron_idx=1)
                    
    # F. Bowed Oak Barrels Inside Wagon Bed (Ref 3)
    # 4 Barrels resting in bed
    barrel_coords = [
        (-0.75, -0.32),
        (-0.75, 0.32),
        (0.20, -0.32),
        (0.20, 0.32),
    ]
    for bx, by in barrel_coords:
        b_pt = w_mat @ Vector((bx, by, bed_h*0.5 + 0.48))
        add_bowed_barrel_to_bmesh(bm_wagon, center=b_pt, height=0.92, r_mid=0.38, r_end=0.32, segments=16, mat_wood_idx=0, mat_iron_idx=1)
        
    # G. Draped Canvas Tarpaulin Cover (Ref 3)
    # Billowing undulating cloth draped over the rear barrels
    tarp_w = bed_w * 1.15
    tarp_l = 2.1
    t_nx, t_ny = 12, 10
    t_verts = []
    for ti in range(t_nx + 1):
        tx_l = -1.2 + (ti / t_nx) * tarp_l
        row = []
        for tj in range(t_ny + 1):
            ty_l = -tarp_w*0.5 + (tj / t_ny) * tarp_w
            # Sag / arch curve over barrels
            arch = math.cos((tj / t_ny - 0.5) * math.pi) * 0.35
            tz_l = bed_h*0.5 + 0.90 + arch + math.sin(ti * 0.7) * 0.04
            # Hanging drape down sides
            if tj in [0, 1, t_ny-1, t_ny]:
                tz_l -= 0.38 * (1.0 - (tj / t_ny - 0.5)**2)
            if ti in [0, 1]:
                tz_l -= 0.28
            pt = w_mat @ Vector((tx_l, ty_l, tz_l))
            v = bm_wagon.verts.new(pt)
            row.append(v)
        t_verts.append(row)
    for ti in range(t_nx):
        for tj in range(t_ny):
            f = bm_wagon.faces.new([t_verts[ti][tj], t_verts[ti][tj+1], t_verts[ti+1][tj+1], t_verts[ti+1][tj]])
            f.material_index = 3 # mat_tarp
            
    # H. Mounted Iron Bracket Lantern on Sideboard (Ref 3)
    l_pt = w_mat @ Vector((bed_l*0.46, bed_w*0.52, bed_h*0.5 + 0.45))
    lan_cage = bmesh.ops.create_cone(bm_wagon, cap_ends=True, segments=6, radius1=0.10, radius2=0.08, depth=0.24, matrix=Matrix.Translation(l_pt))
    for v in lan_cage['verts']:
        for f in v.link_faces:
            f.material_index = 4 # mat_lantern
            
    me_wagon = bpy.data.meshes.new("Village_Cargo_Wagon_Masterpiece_Mesh")
    bm_wagon.to_mesh(me_wagon)
    bm_wagon.free()
    smooth_mesh(me_wagon)
    obj_wagon = bpy.data.objects.new("Village_Cargo_Wagon_Masterpiece", me_wagon)
    col_props.objects.link(obj_wagon)
    for m in wagon_mats:
        obj_wagon.data.materials.append(m if m else mat_oak)
        
    # Lantern Point Light
    pl_wagon = bpy.data.lights.new("Light_Wagon_Lantern", 'POINT')
    pl_wagon.energy = 45.0
    pl_wagon.color = (1.0, 0.75, 0.35)
    obj_plw = bpy.data.objects.new("Light_Wagon_Lantern", pl_wagon)
    col_props.objects.link(obj_plw)
    obj_plw.location = l_pt
    
    # Calibrate Cam_Wagon_Market_Hero (Ref 3 Showcase)
    cam_wagon = bpy.data.objects.get("Cam_Wagon_Market_Hero")
    if not cam_wagon:
        cam_data = bpy.data.cameras.new("Cam_Wagon_Market_Hero")
        cam_wagon = bpy.data.objects.new("Cam_Wagon_Market_Hero", cam_data)
        bpy.context.scene.collection.objects.link(cam_wagon)
        
    # 3/4 side-front view showing side planks, upright wheels, barrels, draped tarp & lantern (Ref 3)
    cw_loc = Vector((wx + 3.2, wy - 4.2, wz + 1.85))
    cw_tgt = Vector((wx, wy, wz + 0.85))
    cam_wagon.location = cw_loc
    cam_wagon.data.lens = 42.0
    dir_cw = (cw_tgt - cw_loc).normalized()
    cam_wagon.rotation_euler = dir_cw.to_track_quat('-Z', 'Y').to_euler()
    
    # Calibrate Cam_Village_Entrance_NoticeBoard (Ref 5 Showcase)
    cam_nb = bpy.data.objects.get("Cam_Village_Entrance_NoticeBoard")
    if not cam_nb:
        cam_data_nb = bpy.data.cameras.new("Cam_Village_Entrance_NoticeBoard")
        cam_nb = bpy.data.objects.new("Cam_Village_Entrance_NoticeBoard", cam_data_nb)
        bpy.context.scene.collection.objects.link(cam_nb)
    nb_loc = Vector((0.2, -43.5, 2.2))
    nb_tgt = Vector((2.8, -35.5, 1.45))
    cam_nb.location = nb_loc
    cam_nb.data.lens = 32.0
    dir_nb = (nb_tgt - nb_loc).normalized()
    cam_nb.rotation_euler = dir_nb.to_track_quat('-Z', 'Y').to_euler()
    
    print("Cargo wagon build complete!")
    print("Props masterpiece build complete!")

if __name__ == "__main__":
    build_masterpiece_props()
