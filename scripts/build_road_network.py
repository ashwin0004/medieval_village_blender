"""
build_road_network.py
=====================
Creates a complete, highly realistic village road network conforming directly
to the sculpted terrain, based on historical medieval references (Ref 1-5):
  - Main Cobblestone Road with crowned profile, curb stones, and river-cobble paving
  - Branching Dirt & Beaten Earth Paths connecting every building naturally:
      * Castle Watchtower Ascent Path
      * Church & Graveyard Path
      * Tithe Barn & Farm Lane (with cart ruts)
      * Main Cottage Flagstone Walkway
      * Blacksmith Forge Spur
      * Riverbank Fisherman's Trail
  - Individual irregular stones & curbs along road edges and building thresholds
  - Stone steps bridging terrain elevation changes (Castle, Church, Cottage, River)
  - Mud patches with wet puddles and wagon ruts
  - Grass & moss tufts growing in the crevices between stones and along path margins
  - Small roadside rocks & wheel-guard curb boulders (chasse-roues)
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

# ──────────────────────────────────────────────
# Material Helpers
# ──────────────────────────────────────────────

def get_mat(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat

def assign_mat(obj, mat_name):
    mat = get_mat(mat_name)
    if not obj.data.materials:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

def add_bevel(obj, width=0.03, segments=2):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(60)

def ensure_collection(name, parent_col=None):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

# ──────────────────────────────────────────────
# PBR Materials for Roads & Paths
# ──────────────────────────────────────────────

def setup_road_materials():
    print("Setting up enhanced PBR road materials...")
    
    # 1. Enhanced Cobblestone Material (Ref Image 3: rounded river cobbles with moss)
    mat_cobble = get_mat("M_Cobblestone_Road")
    nt = mat_cobble.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1100, 0)
    
    # Voronoi for stone cobblestone cells
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.location = (-850, 150)
    vor.voronoi_dimensions = "2D"
    vor.feature = "F1"
    vor.distance = "EUCLIDEAN"
    vor.inputs["Scale"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    
    # Distance to edge gives mortar groove
    vor_edge = nt.nodes.new("ShaderNodeTexVoronoi")
    vor_edge.location = (-850, -150)
    vor_edge.voronoi_dimensions = "2D"
    vor_edge.feature = "DISTANCE_TO_EDGE"
    vor_edge.inputs["Scale"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], vor_edge.inputs["Vector"])
    
    # Stone color variations (grey granite, warm sandstone, dark slate)
    ramp_stone = nt.nodes.new("ShaderNodeValToRGB")
    ramp_stone.location = (-550, 200)
    ramp_stone.color_ramp.elements[0].position = 0.15
    ramp_stone.color_ramp.elements[0].color = (0.22, 0.19, 0.15, 1.0) # Dark basalt
    ramp_stone.color_ramp.elements[1].position = 0.85
    ramp_stone.color_ramp.elements[1].color = (0.45, 0.38, 0.28, 1.0) # Warm sunlit granite (Ref 3)
    nt.links.new(vor.outputs["Color"], ramp_stone.inputs["Fac"])
    
    # Mortar / crevice mask
    ramp_mortar = nt.nodes.new("ShaderNodeValToRGB")
    ramp_mortar.location = (-550, -100)
    ramp_mortar.color_ramp.elements[0].position = 0.04
    ramp_mortar.color_ramp.elements[0].color = (0.08, 0.06, 0.04, 1.0) # Dark dirt mortar
    ramp_mortar.color_ramp.elements[1].position = 0.22
    ramp_mortar.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0) # Stone top
    nt.links.new(vor_edge.outputs["Distance"], ramp_mortar.inputs["Fac"])
    
    # Mix Stone and Mortar (Blender 4/5 compatible)
    try:
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = 'RGBA'
        mix.blend_type = "MULTIPLY"
        mix.location = (-250, 50)
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(ramp_stone.outputs["Color"], mix.inputs[6])
        nt.links.new(ramp_mortar.outputs["Color"], mix.inputs[7])
        nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    except Exception:
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.location = (-250, 50)
        mix.blend_type = "MULTIPLY"
        nt.links.new(ramp_stone.outputs["Color"], mix.inputs["Color1"])
        nt.links.new(ramp_mortar.outputs["Color"], mix.inputs["Color2"])
        mix.inputs["Fac"].default_value = 1.0
        nt.links.new(mix.outputs[0], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.72 # Worn stone tops
    
    # Stone height bump (Ref 3: prominent rounded cobbles)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (0, -200)
    bump.inputs["Strength"].default_value = 0.75
    bump.inputs["Distance"].default_value = 0.08
    nt.links.new(ramp_mortar.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    
    # 2. Dirt & Mud Path Material (Ref Image 4)
    mat_dirt = get_mat("M_Dirt_Path_Mud")
    nt2 = mat_dirt.node_tree
    nt2.nodes.clear()
    out2 = nt2.nodes.new("ShaderNodeOutputMaterial")
    out2.location = (600, 0)
    bsdf2 = nt2.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf2.location = (200, 0)
    
    tc2 = nt2.nodes.new("ShaderNodeTexCoord")
    tc2.location = (-900, 0)
    noise_dirt = nt2.nodes.new("ShaderNodeTexNoise")
    noise_dirt.location = (-650, 0)
    noise_dirt.inputs["Scale"].default_value = 8.0
    noise_dirt.inputs["Detail"].default_value = 6.0
    nt2.links.new(tc2.outputs["Object"], noise_dirt.inputs["Vector"])
    
    ramp_dirt = nt2.nodes.new("ShaderNodeValToRGB")
    ramp_dirt.location = (-400, 100)
    ramp_dirt.color_ramp.elements[0].position = 0.2
    ramp_dirt.color_ramp.elements[0].color = (0.12, 0.09, 0.06, 1.0) # Damp trodden mud
    ramp_dirt.color_ramp.elements[1].position = 0.8
    ramp_dirt.color_ramp.elements[1].color = (0.28, 0.22, 0.16, 1.0) # Dry earth & gravel
    nt2.links.new(noise_dirt.outputs["Fac"], ramp_dirt.inputs["Fac"])
    
    nt2.links.new(ramp_dirt.outputs["Color"], bsdf2.inputs["Base Color"])
    bsdf2.inputs["Roughness"].default_value = 0.85
    
    bump2 = nt2.nodes.new("ShaderNodeBump")
    bump2.location = (0, -200)
    bump2.inputs["Strength"].default_value = 0.4
    bump2.inputs["Distance"].default_value = 0.05
    nt2.links.new(noise_dirt.outputs["Fac"], bump2.inputs["Height"])
    nt2.links.new(bump2.outputs["Normal"], bsdf2.inputs["Normal"])
    
    nt2.links.new(bsdf2.outputs["BSDF"], out2.inputs["Surface"])
    
    # 3. Wet Mud & Puddle Material (Ref 4)
    mat_mud = get_mat("M_Mud_Puddle")
    nt3 = mat_mud.node_tree
    nt3.nodes.clear()
    out3 = nt3.nodes.new("ShaderNodeOutputMaterial")
    out3.location = (600, 0)
    bsdf3 = nt3.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf3.location = (200, 0)
    
    bsdf3.inputs["Base Color"].default_value = (0.09, 0.07, 0.05, 1.0) # Deep wet silt
    bsdf3.inputs["Roughness"].default_value = 0.15 # Highly reflective wet puddle sheen
    bsdf3.inputs["IOR"].default_value = 1.333
    nt3.links.new(bsdf3.outputs["BSDF"], out3.inputs["Surface"])

# ──────────────────────────────────────────────
# Terrain Height Projector
# ──────────────────────────────────────────────

class TerrainProjector:
    def __init__(self):
        self.terrain = bpy.data.objects.get("Terrain_Village")
        self.down = Vector((0.0, 0.0, -1.0))

    def get_z(self, x, y, default_z=0.0):
        if not self.terrain:
            return default_z
        res, loc, norm, idx = self.terrain.ray_cast(Vector((x, y, 40.0)), self.down)
        return loc.z if res else default_z

# ──────────────────────────────────────────────
# Master Road Network Generator
# ──────────────────────────────────────────────

def clean_old_roads():
    s_col = bpy.data.collections.get("05_STREET_OBJECTS")
    if not s_col:
        return
    for o in list(s_col.objects):
        if o.name.startswith("Road_") or o.name.startswith("Path_") or o.name.startswith("Market_Square_Paving"):
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Clean child collections if re-running
    for ch_name in ["Road_Curbs", "Road_Steps", "Road_Mud_Puddles", "Road_Grass_Tufts", "Roadside_Rocks"]:
        ch = bpy.data.collections.get(ch_name)
        if ch:
            for o in list(ch.objects):
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(ch)
            
    print("Cleaned existing road ribbons and elements.")

def build_road_strip(name, points, width, col, mat_name, proj, is_dirt=False):
    """Creates a quad-strip road surface with vertices conforming to terrain elevation."""
    bm = bmesh.new()
    verts_left = []
    verts_center = []
    verts_right = []
    
    # Subdivide long spans between waypoints for smooth terrain conforming
    refined_pts = []
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        n_subs = max(1, int(dist / 2.0))
        for s in range(n_subs):
            t = s / n_subs
            refined_pts.append((p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])))
    refined_pts.append(points[-1])
    
    for i, (px, py) in enumerate(refined_pts):
        if i < len(refined_pts) - 1:
            nx, ny = refined_pts[i + 1]
            dx, dy = nx - px, ny - py
        else:
            nx, ny = refined_pts[i - 1]
            dx, dy = px - nx, py - ny
        length = math.sqrt(dx*dx + dy*dy) or 1
        dx /= length; dy /= length
        rx, ry = -dy, dx # Perpendicular vector
        
        # Terrain height at left, center, right
        lx = px + rx * width * 0.5
        ly = py + ry * width * 0.5
        rx_pos = px - rx * width * 0.5
        ry_pos = py - ry * width * 0.5
        
        lz = proj.get_z(lx, ly) + 0.04
        cz = proj.get_z(px, py) + (0.07 if not is_dirt else 0.04) # Crowned profile on cobblestone
        rz = proj.get_z(rx_pos, ry_pos) + 0.04
        
        vl = bm.verts.new((lx, ly, lz))
        vc = bm.verts.new((px, py, cz))
        vr = bm.verts.new((rx_pos, ry_pos, rz))
        
        verts_left.append(vl)
        verts_center.append(vc)
        verts_right.append(vr)
        
    bm.verts.ensure_lookup_table()
    for i in range(len(refined_pts) - 1):
        # 2 quads per segment (left-center, center-right) for crowned road profile
        l1, c1, r1 = verts_left[i], verts_center[i], verts_right[i]
        l2, c2, r2 = verts_left[i + 1], verts_center[i + 1], verts_right[i + 1]
        try:
            bm.faces.new([l1, c1, c2, l2])
            bm.faces.new([c1, r1, r2, c2])
        except Exception:
            pass
            
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.shade_smooth()
    
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    assign_mat(obj, mat_name)
    return obj, refined_pts

def build_all_roads_and_paths():
    print("==================================================")
    print("   BUILDING REALISTIC VILLAGE ROAD NETWORK")
    print("==================================================")
    
    setup_road_materials()
    clean_old_roads()
    
    s_col = ensure_collection("05_STREET_OBJECTS")
    col_curbs = ensure_collection("Road_Curbs", s_col)
    col_steps = ensure_collection("Road_Steps", s_col)
    col_mud = ensure_collection("Road_Mud_Puddles", s_col)
    col_grass = ensure_collection("Road_Grass_Tufts", s_col)
    col_rocks = ensure_collection("Roadside_Rocks", s_col)
    
    proj = TerrainProjector()
    
    # ──────────────────────────────────────────
    # 1. Main Cobblestone Road Network
    # ──────────────────────────────────────────
    print("1. Constructing Main Cobblestone Avenue...")
    # South Gate -> Market Square -> Central Avenue -> Stone Bridge
    pts_main = [
        (0.0, -58.0), (0.5, -50.0), (-0.5, -42.0), (0.5, -34.0),
        (0.0, -26.0), (0.0, -20.0), # Market Square
        (1.5, -16.0), (3.0, -12.0), (4.5, -6.0), (5.0, 0.0), # Central Avenue
        (5.5, 6.0), (5.8, 12.0), (6.0, 18.0), (6.0, 24.0)   # Across Stone Bridge
    ]
    main_road_obj, main_pts = build_road_strip("Road_Main_Cobblestone", pts_main, width=5.4, col=s_col, mat_name="M_Cobblestone_Road", proj=proj)
    
    # Market Square Full Cobblestone Plaza Paving (16m x 14m)
    bm_market = bmesh.new()
    bmesh.ops.create_grid(bm_market, x_segments=16, y_segments=14, size=8.0)
    for v in bm_market.verts:
        # Scale to 16m wide (X) and 14m deep (Y) around (0, -20)
        vx = v.co.x * 2.0
        vy = -20.0 + v.co.y * 1.75
        vz = proj.get_z(vx, vy) + 0.05
        v.co = Vector((vx, vy, vz))
    m_market = bpy.data.meshes.new("Road_Market_Plaza_Mesh")
    bm_market.to_mesh(m_market)
    bm_market.free()
    m_market.shade_smooth()
    market_obj = bpy.data.objects.new("Road_Market_Plaza", m_market)
    s_col.objects.link(market_obj)
    assign_mat(market_obj, "M_Cobblestone_Road")

    # ──────────────────────────────────────────
    # 2. Branching Dirt & Beaten Earth Paths
    # ──────────────────────────────────────────
    print("2. Constructing Branching Dirt & Beaten Earth Paths...")
    
    # Path A: Castle Watchtower Ascent Path (Climbing from Market Square up to -26, -14)
    pts_castle = [
        (0.0, -20.0), (-4.5, -18.5), (-9.0, -17.5), (-14.0, -16.8),
        (-18.5, -16.0), (-21.5, -15.5), (-24.5, -14.8) # Tower entrance
    ]
    build_road_strip("Path_Castle_Ascent", pts_castle, width=3.2, col=s_col, mat_name="M_Dirt_Path_Mud", proj=proj, is_dirt=True)

    # Path B: Church & Graveyard Path (Winding West past Cottage 2 & Inn to Church Portal)
    pts_church = [
        (0.0, -20.0), (-3.5, -16.5), (-6.5, -12.0), (-9.5, -6.0),
        (-12.5, 0.0), (-14.5, 5.0), (-12.5, 10.0), (-10.0, 11.5) # Church Portal
    ]
    build_road_strip("Path_Church_Chapel", pts_church, width=3.4, col=s_col, mat_name="M_Dirt_Path_Mud", proj=proj, is_dirt=True)

    # Path C: Tithe Barn & Farm Lane (Branching East to Barn wagon doors)
    pts_barn = [
        (4.5, -6.0), (8.5, -2.0), (13.0, 3.0), (17.5, 8.0),
        (21.0, 11.5), (24.0, 13.5) # Barn wagon doors
    ]
    build_road_strip("Path_Barn_Farm_Lane", pts_barn, width=3.6, col=s_col, mat_name="M_Dirt_Path_Mud", proj=proj, is_dirt=True)

    # Path D: Main Cottage Front Walkway
    pts_cottage = [
        (1.5, -16.0), (1.0, -11.0), (0.5, -7.0), (0.0, -4.8) # Cottage steps
    ]
    build_road_strip("Path_Main_Cottage_Walkway", pts_cottage, width=2.6, col=s_col, mat_name="M_Cobblestone_Road", proj=proj)

    # Path E: Blacksmith Forge Spur
    pts_smith = [
        (4.5, -6.0), (8.0, -7.0), (11.5, -7.5), (13.5, -7.5) # Smithy anvil
    ]
    build_road_strip("Path_Blacksmith_Spur", pts_smith, width=2.8, col=s_col, mat_name="M_Dirt_Path_Mud", proj=proj, is_dirt=True)

    # Path F: Riverbank Trail
    pts_river = [
        (6.0, 18.0), (8.5, 16.0), (11.0, 12.0), (14.0, 7.0), (16.5, 1.0)
    ]
    build_road_strip("Path_Riverbank_Trail", pts_river, width=2.2, col=s_col, mat_name="M_Dirt_Path_Mud", proj=proj, is_dirt=True)

    # ──────────────────────────────────────────
    # 3. Individual Irregular Stones & Curb Edgings (Ref 1, 3)
    # ──────────────────────────────────────────
    print("3. Placing Individual Irregular Stones & Curb Edgings...")
    # Generate raised stone curb blocks along the main cobblestone road borders
    n_curbs = len(main_pts)
    for i in range(0, n_curbs - 1, 2):
        px, py = main_pts[i]
        nx, ny = main_pts[i + 1]
        dx, dy = nx - px, ny - py
        length = math.sqrt(dx*dx + dy*dy) or 1
        dx /= length; dy /= length
        rx, ry = -dy, dx
        
        # Place curbs on both Left & Right margins
        for side, sign in [("L", 1), ("R", -1)]:
            cx = px + sign * rx * 2.85
            cy = py + sign * ry * 2.85
            cz = proj.get_z(cx, cy) + 0.10
            
            bm_curb = bmesh.new()
            bmesh.ops.create_cube(bm_curb, size=1.0)
            m_curb = bpy.data.meshes.new(f"Curb_{side}_{i}_Mesh")
            bm_curb.to_mesh(m_curb)
            bm_curb.free()
            
            curb = bpy.data.objects.new(f"Curb_{side}_{i}", m_curb)
            col_curbs.objects.link(curb)
            assign_mat(curb, "M_Stone_Rough")
            curb.location = Vector((cx, cy, cz))
            curb.scale = (random.uniform(0.35, 0.45), random.uniform(1.4, 1.8), random.uniform(0.18, 0.24))
            curb.rotation_euler = (0, 0, math.atan2(dy, dx) + random.uniform(-0.08, 0.08))
            add_bevel(curb, 0.03, 2)

    # Building Entrance Flagstone Thresholds
    threshold_locs = [
        ("Thresh_Tavern", 4.0, -17.5, 2.4, 1.2),
        ("Thresh_Cottage", 0.0, -4.4, 2.2, 1.0),
        ("Thresh_Blacksmith", 13.0, -8.8, 2.0, 1.0),
        ("Thresh_Church", -10.0, 10.5, 2.5, 1.4),
        ("Thresh_Inn", -15.0, 4.5, 2.2, 1.1),
        ("Thresh_Cottage2", -8.0, -10.5, 2.0, 1.0),
        ("Thresh_Cottage3", 10.0, 6.5, 2.0, 1.0),
        ("Thresh_Barn", 24.0, 12.0, 3.6, 1.4),
        ("Thresh_Castle", -23.5, -15.5, 2.2, 1.2)
    ]
    for name, tx, ty, tw, td in threshold_locs:
        tz = proj.get_z(tx, ty) + 0.08
        bm_th = bmesh.new()
        bmesh.ops.create_cube(bm_th, size=1.0)
        m_th = bpy.data.meshes.new(f"{name}_Mesh")
        bm_th.to_mesh(m_th)
        bm_th.free()
        th = bpy.data.objects.new(name, m_th)
        col_curbs.objects.link(th)
        assign_mat(th, "M_Stone_Rough")
        th.location = Vector((tx, ty, tz))
        th.scale = (tw, td, 0.16)
        add_bevel(th, 0.04, 2)

    # ──────────────────────────────────────────
    # 4. Stone Steps Bridging Slope Transitions
    # ──────────────────────────────────────────
    print("4. Building Stone Steps on Sloping Paths...")
    # Flight A: Castle Watchtower Ascent Steps (bridging slope to watchtower)
    castle_steps = [
        (-17.5, -16.2), (-18.8, -16.0), (-20.0, -15.8), (-21.2, -15.5)
    ]
    for si, (sx, sy) in enumerate(castle_steps):
        sz = proj.get_z(sx, sy) + 0.12
        bm_s = bmesh.new()
        bmesh.ops.create_cube(bm_s, size=1.0)
        m_s = bpy.data.meshes.new(f"Step_Castle_{si}_Mesh")
        bm_s.to_mesh(m_s)
        bm_s.free()
        st = bpy.data.objects.new(f"Step_Castle_{si}", m_s)
        col_steps.objects.link(st)
        assign_mat(st, "M_Stone_Rough")
        st.location = Vector((sx, sy, sz))
        st.scale = (1.4, 0.6, 0.22)
        st.rotation_euler = (0, 0, math.radians(15))
        add_bevel(st, 0.04, 2)

    # Flight B: Church Terrace Descent Steps
    church_steps = [
        (-13.5, 6.5), (-12.5, 8.0), (-11.5, 9.5)
    ]
    for si, (sx, sy) in enumerate(church_steps):
        sz = proj.get_z(sx, sy) + 0.12
        bm_s = bmesh.new()
        bmesh.ops.create_cube(bm_s, size=1.0)
        m_s = bpy.data.meshes.new(f"Step_Church_{si}_Mesh")
        bm_s.to_mesh(m_s)
        bm_s.free()
        st = bpy.data.objects.new(f"Step_Church_{si}", m_s)
        col_steps.objects.link(st)
        assign_mat(st, "M_Stone_Rough")
        st.location = Vector((sx, sy, sz))
        st.scale = (1.8, 0.65, 0.24)
        st.rotation_euler = (0, 0, math.radians(-35))
        add_bevel(st, 0.04, 2)

    # ──────────────────────────────────────────
    # 5. Mud Patches with Wet Puddles & Wheel Ruts (Ref 4)
    # ──────────────────────────────────────────
    print("5. Laying Mud Patches & Wet Puddles...")
    mud_spots = [
        # (X, Y, Scale X, Scale Y, Rotation)
        (22.0, 11.5, 5.0, 4.0, math.radians(10)),   # Tithe Barn wagon turning area
        (1.5, -23.5, 4.5, 3.8, math.radians(-15)),  # Market square cart delivery
        (10.5, -7.0, 3.5, 3.2, math.radians(25)),   # Blacksmith scrap yard
        (5.5, -17.5, 4.0, 3.0, math.radians(5)),    # Tavern cellar entrance
        (-14.5, 2.0, 3.8, 3.0, math.radians(-10))   # Inn carriage pull-in
    ]
    for mi, (mx, my, msx, msy, mrot) in enumerate(mud_spots):
        mz = proj.get_z(mx, my) + 0.06
        bm_mud = bmesh.new()
        bmesh.ops.create_grid(bm_mud, x_segments=6, y_segments=6, size=1.0)
        # Deform vertices for natural puddle bowl
        for v in bm_mud.verts:
            r = math.sqrt(v.co.x**2 + v.co.y**2)
            v.co.z = -0.05 * max(0.0, 1.0 - r)
        m_mud = bpy.data.meshes.new(f"Mud_Puddle_{mi}_Mesh")
        bm_mud.to_mesh(m_mud)
        bm_mud.free()
        m_mud.shade_smooth()
        mud = bpy.data.objects.new(f"Mud_Puddle_{mi}", m_mud)
        col_mud.objects.link(mud)
        assign_mat(mud, "M_Mud_Puddle")
        mud.location = Vector((mx, my, mz))
        mud.scale = (msx, msy, 1.0)
        mud.rotation_euler = (0, 0, mrot)

    # ──────────────────────────────────────────
    # 6. Grass Growing Between Stones & Crevices (Ref 3, 5)
    # ──────────────────────────────────────────
    print("6. Scattering Grass Tufts in Crevices & Road Margins...")
    # Scatter 3D grass tufts along path borders and between cobbles
    rng = random.Random(88)
    for gi in range(75):
        # Pick random point along main road or paths
        t_pt = rng.choice(main_pts)
        gx = t_pt[0] + rng.uniform(-3.2, 3.2)
        gy = t_pt[1] + rng.uniform(-3.2, 3.2)
        gz = proj.get_z(gx, gy) + 0.05
        
        # 3-blade grass cluster
        bm_g = bmesh.new()
        for bi in range(4):
            bang = bi * (math.pi / 2) + rng.uniform(-0.3, 0.3)
            bx = math.sin(bang) * 0.15
            by = math.cos(bang) * 0.15
            bmesh.ops.create_cone(bm_g, cap_ends=True, segments=4, radius1=0.03, radius2=0.005, depth=rng.uniform(0.18, 0.38))
            bmesh.ops.translate(bm_g, vec=(bx, by, 0.15), verts=bm_g.verts[-6:])
        m_g = bpy.data.meshes.new(f"Grass_Tuft_{gi}_Mesh")
        bm_g.to_mesh(m_g)
        bm_g.free()
        m_g.shade_smooth()
        tuft = bpy.data.objects.new(f"Grass_Tuft_{gi}", m_g)
        col_grass.objects.link(tuft)
        assign_mat(tuft, "M_Grass_Green")
        tuft.location = Vector((gx, gy, gz))
        tuft.rotation_euler = (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), rng.uniform(0, math.pi * 2))

    # ──────────────────────────────────────────
    # 7. Small Roadside Rocks & Wheel-Guard Boulders
    # ──────────────────────────────────────────
    print("7. Scattering Roadside Rocks & Curb Wheel-Guards...")
    # Boulders placed at sharp road corners to protect building corners (Ref 1)
    chasse_roues = [
        ("Guard_Rock_Tavern_Corner", 7.2, -18.5, 0.55),
        ("Guard_Rock_Cottage_Corner", -3.2, -4.5, 0.45),
        ("Guard_Rock_Smith_Corner", 8.8, -9.5, 0.50),
        ("Guard_Rock_Inn_Corner", -12.5, 4.0, 0.48),
        ("Guard_Rock_Bridge_L", 4.2, 17.5, 0.65),
        ("Guard_Rock_Bridge_R", 7.8, 17.5, 0.65),
        ("Guard_Rock_Market_S", -3.8, -25.5, 0.45),
        ("Guard_Rock_Market_E", 3.8, -25.5, 0.45)
    ]
    for name, rx, ry, r_sz in chasse_roues:
        rz = proj.get_z(rx, ry) + r_sz * 0.4
        bm_r = bmesh.new()
        bmesh.ops.create_icosphere(bm_r, subdivisions=2, radius=r_sz)
        # Deform vertices for natural faceted boulder
        for v in bm_r.verts:
            v.co += Vector((rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06)))
        m_r = bpy.data.meshes.new(f"{name}_Mesh")
        bm_r.to_mesh(m_r)
        bm_r.free()
        m_r.shade_smooth()
        rock = bpy.data.objects.new(name, m_r)
        col_rocks.objects.link(rock)
        assign_mat(rock, "M_Stone_Rough")
        rock.location = Vector((rx, ry, rz))
        rock.rotation_euler = (rng.uniform(0, math.pi), rng.uniform(0, math.pi), rng.uniform(0, math.pi))

    # Scatter 35 smaller fieldstones and pebbles along the road verges
    for ri in range(35):
        t_pt = rng.choice(main_pts)
        px = t_pt[0] + rng.uniform(-3.5, 3.5)
        py = t_pt[1] + rng.uniform(-3.5, 3.5)
        pz = proj.get_z(px, py) + 0.08
        rad = rng.uniform(0.12, 0.28)
        
        bm_p = bmesh.new()
        bmesh.ops.create_icosphere(bm_p, subdivisions=1, radius=rad)
        m_p = bpy.data.meshes.new(f"Pebble_{ri}_Mesh")
        bm_p.to_mesh(m_p)
        bm_p.free()
        m_p.shade_smooth()
        peb = bpy.data.objects.new(f"Pebble_{ri}", m_p)
        col_rocks.objects.link(peb)
        assign_mat(peb, "M_Stone_Rough")
        peb.location = Vector((px, py, pz))
        peb.scale = (rng.uniform(0.8, 1.3), rng.uniform(0.8, 1.3), rng.uniform(0.5, 0.9))

    print("==================================================")
    print("   ROAD NETWORK GENERATION COMPLETE!")
    print("==================================================")
    return True

if __name__ == "__main__":
    build_all_roads_and_paths()

