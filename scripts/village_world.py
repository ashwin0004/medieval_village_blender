"""
village_world.py
================
Medieval Fantasy Village World Assembly
Builds the complete village environment:
  - Sculpted terrain with river valley
  - Winding cobblestone roads
  - Buildings assembled from modular kit & copies of cottage
  - Vegetation (trees, bushes, rocks, grass)
  - River surface and banks
  - Market square with well and stalls
  - Forest area
  - Castle tower
  - Church tower stub
  - Organic, irregular settlement layout
"""

import bpy
import bmesh
import math
import random
import importlib
import sys
import os

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def ensure_collection(name, parent=None):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent is None:
            bpy.context.scene.collection.children.link(col)
        else:
            parent.children.link(col)
    return col


def link_to(col, obj):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)


def get_mat(name):
    """Return existing material by name, or create a plain fallback."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
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
# 1. TERRAIN
# ──────────────────────────────────────────────

def build_terrain(col_terrain):
    """Create a 120×120m subdivided terrain with gentle hills and river valley."""
    # Remove old flat terrain if present
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Terrain_Village"):
            bpy.data.objects.remove(obj, do_unlink=True)

    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=80, y_segments=80, size=60.0)

    # Gentle height displacement
    rng = random.Random(42)
    for v in bm.verts:
        x, y = v.co.x, v.co.y
        # Rolling hills
        h = (math.sin(x * 0.08) * math.cos(y * 0.06) * 1.8
             + math.sin(x * 0.15 + 1.2) * 0.6
             + math.cos(y * 0.12 + 0.7) * 0.8)
        # River valley depression (runs roughly NW–SE diagonally across center)
        river_dist = abs((x * 0.6 + y * 0.8) - 5.0)
        river_carve = max(0.0, 1.0 - river_dist / 8.0) * 2.5
        # Market center — keep flatter
        center_flat = max(0.0, 1.0 - math.sqrt(x*x + y*y) / 18.0) * h * 0.7
        v.co.z = h - river_carve - center_flat * 0.5 + rng.uniform(-0.05, 0.05)

    mesh = bpy.data.meshes.new("Terrain_Village_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.shade_smooth()

    terrain = new_obj("Terrain_Village", mesh, col_terrain)
    assign_mat(terrain, "M_Ground_Mud")

    # Smooth modifier
    smooth = terrain.modifiers.new("Smooth", "SMOOTH")
    smooth.factor = 0.8
    smooth.iterations = 3

    return terrain


# ──────────────────────────────────────────────
# 2. RIVER
# ──────────────────────────────────────────────

def build_river(col_terrain):
    """Flat river surface plane following the valley depression."""
    bm = bmesh.new()
    # River runs diagonally: from (-45, 20) to (30, -45)
    # Build as a wide strip subdivided lengthwise
    verts = []
    steps = 30
    width = 6.0
    for i in range(steps + 1):
        t = i / steps
        cx = -45 + t * 75   # x goes -45 → 30
        cy = 20 - t * 65    # y goes 20 → -45
        # Perpendicular direction (normalised)
        dx, dy = 0.6, 0.8   # along river dir
        px, py = -dy, dx    # perpendicular
        bm.verts.new((cx + px * width * 0.5, cy + py * width * 0.5, -0.25))
        bm.verts.new((cx - px * width * 0.5, cy - py * width * 0.5, -0.25))

    bm.verts.ensure_lookup_table()
    for i in range(steps):
        a, b = i * 2, i * 2 + 1
        c, d = a + 2, b + 2
        bm.faces.new([bm.verts[a], bm.verts[b], bm.verts[d], bm.verts[c]])

    mesh = bpy.data.meshes.new("River_Surface_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    river = new_obj("River_Surface", mesh, col_terrain)

    # Water material
    mat = bpy.data.materials.new("M_River_Water")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    gls = nt.nodes.new("ShaderNodeBsdfGlossy")
    gls.inputs["Color"].default_value = (0.05, 0.25, 0.45, 1.0)
    gls.inputs["Roughness"].default_value = 0.05
    mix.inputs["Fac"].default_value = 0.85
    nt.links.new(trans.outputs[0], mix.inputs[1])
    nt.links.new(gls.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    mat.blend_method = "BLEND"
    river.data.materials.append(mat)

    return river


# ──────────────────────────────────────────────
# 3. ROADS
# ──────────────────────────────────────────────

def make_road_strip(name, points, width, col, mat_name):
    """Create a road as a series of quad strips following waypoints."""
    bm = bmesh.new()
    verts_left = []
    verts_right = []

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
        z = 0.02  # slightly above terrain
        vl = bm.verts.new((px + rx * width * 0.5, py + ry * width * 0.5, z))
        vr = bm.verts.new((px - rx * width * 0.5, py - ry * width * 0.5, z))
        verts_left.append(vl)
        verts_right.append(vr)

    bm.verts.ensure_lookup_table()
    for i in range(len(points) - 1):
        a = verts_left[i]
        b = verts_right[i]
        c = verts_right[i + 1]
        d = verts_left[i + 1]
        try:
            bm.faces.new([a, b, c, d])
        except Exception:
            pass

    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = new_obj(name, mesh, col)
    assign_mat(obj, mat_name)
    return obj


def build_roads(col_roads):
    """Build winding cobblestone roads."""
    roads = []

    # Main road: south entrance → market square → north
    main_pts = [
        (0, -58), (1, -50), (-1, -42), (2, -34),
        (0, -25), (-2, -18), (0, -10), (0, 0),   # market center
        (1, 8),  (-2, 16), (0, 24), (2, 34), (0, 45)
    ]
    r1 = make_road_strip("Road_Main", main_pts, 5.0, col_roads, "M_Cobblestone_Road")
    roads.append(r1)

    # East fork: market → blacksmith / tavern
    east_pts = [(0, 0), (6, -3), (12, -6), (18, -8), (24, -9)]
    r2 = make_road_strip("Road_East", east_pts, 3.5, col_roads, "M_Cobblestone_Road")
    roads.append(r2)

    # West fork: market → church / residential
    west_pts = [(0, 0), (-6, 3), (-12, 8), (-18, 12), (-24, 15)]
    r3 = make_road_strip("Road_West", west_pts, 3.5, col_roads, "M_Cobblestone_Road")
    roads.append(r3)

    # Farm lane
    farm_pts = [(18, -8), (22, 2), (24, 12), (22, 20)]
    r4 = make_road_strip("Road_Farm", farm_pts, 3.0, col_roads, "M_Cobblestone_Road")
    roads.append(r4)

    # Castle approach (narrow)
    castle_pts = [(-24, 15), (-26, 8), (-27, 0), (-26, -8), (-24, -15)]
    r5 = make_road_strip("Road_Castle", castle_pts, 3.0, col_roads, "M_Cobblestone_Road")
    roads.append(r5)

    return roads


# ──────────────────────────────────────────────
# 4. MARKET SQUARE
# ──────────────────────────────────────────────

def build_market_square(col_village):
    """Cobblestone market square around village center."""
    bm = bmesh.new()
    # 18×18m square paving
    bmesh.ops.create_grid(bm, x_segments=12, y_segments=12, size=9.0)
    mesh = bpy.data.meshes.new("Market_Square_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    sq = new_obj("Market_Square_Paving", mesh, col_village)
    assign_mat(sq, "M_Cobblestone_Road")
    sq.location = (0, 0, 0.01)
    return sq


def build_well(col_village):
    """Stone well at market center."""
    bm = bmesh.new()
    # Cylinder shaft
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=16, radius1=0.55, radius2=0.55, depth=0.9)
    mesh = bpy.data.meshes.new("Well_Shaft_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    shaft = new_obj("Well_Shaft", mesh, col_village)
    assign_mat(shaft, "M_Stone_Rough")
    shaft.location = (2.5, 2.5, 0.45)

    # Roof cap (two triangular prisms)
    bm2 = bmesh.new()
    # Simple pitched roof over well: box + scale
    bmesh.ops.create_cube(bm2, size=1.4)
    mesh2 = bpy.data.meshes.new("Well_Roof_Mesh")
    bm2.to_mesh(mesh2)
    bm2.free()
    roof = new_obj("Well_Roof", mesh2, col_village)
    assign_mat(roof, "M_Slate_Roof")
    roof.location = (2.5, 2.5, 1.5)
    roof.scale = (0.7, 0.5, 0.4)

    return [shaft, roof]


# ──────────────────────────────────────────────
# 5. BUILDINGS — assembled from box primitives
#    (quick modular assembly at village scale)
# ──────────────────────────────────────────────

def make_box_building(name, col,
                      x, y, z_base,
                      w, d, h,
                      roof_h, rot_z=0,
                      wall_mat="M_Stone_Rough",
                      roof_mat="M_Slate_Roof"):
    """
    Create a simple box building with a pitched roof.
    Used for quick village layout assembly — each is a
    named landmark that gets replaced by detailed assets later.
    """
    bm = bmesh.new()
    # Walls box
    bmesh.ops.create_cube(bm, size=1.0)
    mesh = bpy.data.meshes.new(name + "_Walls_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    walls = new_obj(name + "_Walls", mesh, col)
    assign_mat(walls, wall_mat)
    walls.location = (x, y, z_base + h * 0.5)
    walls.scale = (w, d, h)
    add_bevel(walls, 0.04, 2)
    walls.rotation_euler.z = rot_z

    # Pitched roof (elongated pyramid)
    bm2 = bmesh.new()
    verts = [
        (-w*0.5, -d*0.5, 0),
        ( w*0.5, -d*0.5, 0),
        ( w*0.5,  d*0.5, 0),
        (-w*0.5,  d*0.5, 0),
        (0, -d*0.5, roof_h),
        (0,  d*0.5, roof_h),
    ]
    faces = [
        [0, 1, 5, 4],
        [1, 2, 5],
        [2, 3, 4, 5],
        [3, 0, 4],
        [0, 3, 2, 1],
    ]
    for v in verts:
        bm2.verts.new(v)
    bm2.verts.ensure_lookup_table()
    for f in faces:
        try:
            bm2.faces.new([bm2.verts[i] for i in f])
        except Exception:
            pass
    mesh2 = bpy.data.meshes.new(name + "_Roof_Mesh")
    bm2.to_mesh(mesh2)
    bm2.free()
    roof = new_obj(name + "_Roof", mesh2, col)
    assign_mat(roof, roof_mat)
    roof.location = (x, y, z_base + h)
    roof.rotation_euler.z = rot_z

    mesh2.shade_smooth()
    return [walls, roof]


def make_chimney(name, col, x, y, z_base, height=2.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=4, radius1=0.3, radius2=0.25, depth=height)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = new_obj(name, mesh, col)
    assign_mat(obj, "M_Stone_Rough")
    obj.location = (x, y, z_base + height * 0.5)
    obj.rotation_euler.z = math.radians(45)
    return obj


def make_tower(name, col, x, y, height=12.0, radius=3.0):
    """Round tower (castle / church bell tower)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=12, radius1=radius, radius2=radius, depth=height)
    mesh = bpy.data.meshes.new(name + "_Shaft_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    shaft = new_obj(name + "_Shaft", mesh, col)
    assign_mat(shaft, "M_Stone_Rough")
    shaft.location = (x, y, height * 0.5)

    # Crenellations (small cubes on top)
    for i in range(8):
            angle = i * math.pi / 4
            cx = x + math.cos(angle) * (radius - 0.3)
            cy = y + math.sin(angle) * (radius - 0.3)
            bm2 = bmesh.new()
            bmesh.ops.create_cube(bm2, size=0.7)
            mesh2 = bpy.data.meshes.new(name + f"_Cren_{i}_Mesh")
            bm2.to_mesh(mesh2)
            bm2.free()
            cren = new_obj(name + f"_Cren_{i}", mesh2, col)
            assign_mat(cren, "M_Stone_Rough")
            cren.location = (cx, cy, height + 0.35)
            cren.scale = (0.5, 0.5, 0.9)

    # Conical roof
    bm3 = bmesh.new()
    bmesh.ops.create_cone(bm3, cap_ends=True, cap_tris=False,
                          segments=12, radius1=radius + 0.3, radius2=0.1, depth=height * 0.35)
    mesh3 = bpy.data.meshes.new(name + "_Cap_Mesh")
    bm3.to_mesh(mesh3)
    bm3.free()
    cap = new_obj(name + "_Cap", mesh3, col)
    assign_mat(cap, "M_Slate_Roof")
    cap.location = (x, y, height + height * 0.175)

    return [shaft, cap]


def make_arch_bridge(name, col, x, y, rot_z=0):
    """Simple 2-arch stone bridge over the river."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    mesh = bpy.data.meshes.new(name + "_Deck_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    deck = new_obj(name + "_Deck", mesh, col)
    assign_mat(deck, "M_Stone_Rough")
    deck.location = (x, y, 0.1)
    deck.scale = (10.0, 7.5, 0.35)
    deck.rotation_euler.z = rot_z

    # Two arch piers
    for side in [-1, 1]:
        bm2 = bmesh.new()
        bmesh.ops.create_cone(bm2, cap_ends=True, cap_tris=False,
                              segments=8, radius1=0.9, radius2=0.9, depth=2.0)
        mesh2 = bpy.data.meshes.new(name + f"_Pier_{side}_Mesh")
        bm2.to_mesh(mesh2)
        bm2.free()
        pier = new_obj(name + f"_Pier_{side}", mesh2, col)
        assign_mat(pier, "M_Stone_Rough")
        ox = math.cos(rot_z) * side * 2.5 - math.sin(rot_z) * 0
        oy = math.sin(rot_z) * side * 2.5 + math.cos(rot_z) * 0
        pier.location = (x + ox, y + oy, -0.8)

    # Stone railings
    for side in [-1, 1]:
        bm3 = bmesh.new()
        bmesh.ops.create_cube(bm3, size=1.0)
        mesh3 = bpy.data.meshes.new(name + f"_Rail_{side}_Mesh")
        bm3.to_mesh(mesh3)
        bm3.free()
        rail = new_obj(name + f"_Rail_{side}", mesh3, col)
        assign_mat(rail, "M_Stone_Rough")
        rox = -math.sin(rot_z) * side * 3.2
        roy = math.cos(rot_z) * side * 3.2
        rail.location = (x + rox, y + roy, 0.55)
        rail.scale = (10.0 if abs(math.cos(rot_z)) > 0.5 else 0.3,
                      0.3 if abs(math.cos(rot_z)) > 0.5 else 7.5,
                      0.6)
        rail.rotation_euler.z = rot_z

    return [deck]


def build_village_buildings(col_buildings, col_structures):
    """Place all village landmark buildings."""
    buildings = []

    # ── Tavern (center-south of market)
    buildings += make_box_building("Tavern", col_buildings,
                                   4, -14, 0, 10, 8, 5.5, 3.5, 0.0,
                                   "M_Plaster_Cream", "M_Clay_Terracotta")
    buildings.append(make_chimney("Tavern_Chimney", col_buildings, 4, -14, 5.5, 2.2))
    # Second story addition
    buildings += make_box_building("Tavern_Upper", col_buildings,
                                   4, -14, 5.5, 7, 5, 3.0, 2.0, 0.0,
                                   "M_Plaster_Cream", "M_Clay_Terracotta")

    # ── Blacksmith (east)
    buildings += make_box_building("Blacksmith", col_buildings,
                                   14, -7, 0, 8, 7, 4.0, 2.5, math.radians(15),
                                   "M_Stone_Rough", "M_Slate_Roof")
    # Open lean-to shed
    buildings += make_box_building("Blacksmith_Shed", col_buildings,
                                   19, -7, 0, 5, 5, 3.0, 1.8, math.radians(15),
                                   "M_Aged_Oak", "M_Slate_Roof")
    buildings.append(make_chimney("Blacksmith_Chimney", col_buildings, 14, -7, 4.0, 3.5))

    # ── Church (north-west)
    buildings += make_box_building("Church", col_buildings,
                                   -10, 18, 0, 11, 16, 6.0, 5.0, 0.0,
                                   "M_Stone_Rough", "M_Slate_Roof")
    # Bell tower
    buildings += make_tower("Church_Bell_Tower", col_buildings, -10, 12, 14.0, 2.5)

    # ── Inn (east of market)
    buildings += make_box_building("Inn", col_buildings,
                                   -15, 8, 0, 9, 7, 5.0, 3.0, math.radians(-10),
                                   "M_Plaster_Cream", "M_Aged_Oak")
    buildings.append(make_chimney("Inn_Chimney", col_buildings, -15, 8, 5.0, 2.0))

    # ── Cottage 2 (residential)
    buildings += make_box_building("Cottage_2", col_buildings,
                                   -8, -8, 0, 6.8, 8.4, 4.5, 3.0, math.radians(20),
                                   "M_Stone_Rough", "M_Slate_Roof")
    buildings.append(make_chimney("Cottage_2_Chimney", col_buildings, -8, -8, 4.5, 1.8))

    # ── Cottage 3
    buildings += make_box_building("Cottage_3", col_buildings,
                                   10, 10, 0, 6.0, 7.0, 4.0, 2.8, math.radians(-25),
                                   "M_Plaster_Cream", "M_Slate_Roof")
    buildings.append(make_chimney("Cottage_3_Chimney", col_buildings, 10, 10, 4.0, 1.8))

    # ── Barn (farm area)
    buildings += make_box_building("Barn", col_buildings,
                                   24, 16, 0, 12, 9, 5.5, 4.0, math.radians(5),
                                   "M_Aged_Oak", "M_Clay_Terracotta")

    # ── Castle Tower (south-west)
    buildings += make_tower("Castle_Tower", col_buildings, -26, -14, 16.0, 4.0)
    # Castle wall stub
    buildings += make_box_building("Castle_Wall_N", col_buildings,
                                   -20, -14, 0, 14, 1.5, 5.0, 0.1, 0.0,
                                   "M_Stone_Rough", "M_Stone_Rough")
    buildings += make_box_building("Castle_Wall_W", col_buildings,
                                   -26, -8, 0, 1.5, 12, 5.0, 0.1, 0.0,
                                   "M_Stone_Rough", "M_Stone_Rough")

    # ── Stone Bridge (over river at X≈6, Y≈22)
    buildings += make_arch_bridge("Stone_Bridge", col_structures, 6, 22, math.radians(30))

    # ── Gate posts (village entrance south)
    for side, sx in [("L", -3.5), ("R", 3.5)]:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=8, radius1=0.6, radius2=0.5, depth=5.0)
        mesh = bpy.data.meshes.new(f"Gate_Post_{side}_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        post = new_obj(f"Gate_Post_{side}", mesh, col_structures)
        assign_mat(post, "M_Stone_Rough")
        post.location = (sx, -56, 2.5)

    return buildings


# ──────────────────────────────────────────────
# 6. MARKET STALLS
# ──────────────────────────────────────────────

def build_market_stalls(col_village):
    stalls = []
    positions = [(-5, -5, math.radians(30)), (5, -5, math.radians(-20)), (-5, 5, math.radians(15))]
    for i, (sx, sy, rz) in enumerate(positions):
        # Counter table
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        mesh = bpy.data.meshes.new(f"Stall_{i+1}_Counter_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        counter = new_obj(f"Market_Stall_{i+1}_Counter", mesh, col_village)
        assign_mat(counter, "M_Aged_Oak")
        counter.location = (sx, sy, 0.5)
        counter.scale = (2.5, 1.0, 0.8)
        counter.rotation_euler.z = rz

        # Awning
        bm2 = bmesh.new()
        bmesh.ops.create_cube(bm2, size=1.0)
        mesh2 = bpy.data.meshes.new(f"Stall_{i+1}_Awning_Mesh")
        bm2.to_mesh(mesh2)
        bm2.free()
        awning = new_obj(f"Market_Stall_{i+1}_Awning", mesh2, col_village)
        assign_mat(awning, "M_Clay_Terracotta")
        awning.location = (sx, sy, 2.2)
        awning.scale = (3.0, 1.5, 0.08)
        awning.rotation_euler.z = rz

        stalls += [counter, awning]
    return stalls


# ──────────────────────────────────────────────
# 7. VEGETATION — Trees, bushes, rocks, grass
# ──────────────────────────────────────────────

def make_tree(name, col, x, y, height=5.0, canopy_r=2.2, seed=0):
    """Oak-style tree: trunk cylinder + multi-level canopy icospheres."""
    rng = random.Random(seed)

    trunk_h = height * 0.55
    trunk_r = max(0.15, height * 0.04)

    # Trunk
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=8, radius1=trunk_r, radius2=trunk_r * 0.7, depth=trunk_h)
    mesh = bpy.data.meshes.new(name + "_Trunk_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    trunk = new_obj(name + "_Trunk", mesh, col)
    assign_mat(trunk, "M_Aged_Oak")
    trunk.location = (x, y, trunk_h * 0.5)

    # Canopy — 3 overlapping icospheres
    canopy_objs = []
    layers = [(0, 0, trunk_h + canopy_r * 0.5, canopy_r),
              (rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), trunk_h + canopy_r * 0.25, canopy_r * 0.75),
              (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), trunk_h + canopy_r * 0.7, canopy_r * 0.6)]
    for li, (ox, oy, oz, cr) in enumerate(layers):
        bm2 = bmesh.new()
        bmesh.ops.create_icosphere(bm2, subdivisions=2, radius=cr)
        mesh2 = bpy.data.meshes.new(name + f"_Canopy_{li}_Mesh")
        bm2.to_mesh(mesh2)
        bm2.free()
        mesh2.shade_smooth()
        canopy = new_obj(name + f"_Canopy_{li}", mesh2, col)
        assign_mat(canopy, "M_Grass_Green")
        canopy.location = (x + ox, y + oy, oz)
        # Slight random rotation and scale variation
        canopy.scale = (rng.uniform(0.9, 1.1), rng.uniform(0.9, 1.1), rng.uniform(0.8, 1.0))
        canopy_objs.append(canopy)

    return [trunk] + canopy_objs


def build_forest(col_nature):
    """Scatter trees in forest zone (west/north-west area)."""
    trees = []
    rng = random.Random(99)
    forest_positions = [
        (-32, 5), (-38, 10), (-35, 18), (-30, 22), (-40, 25),
        (-36, -2), (-42, 5), (-28, 28), (-33, 32), (-38, -8),
        (-44, 14), (-30, 14), (-45, 20), (-34, -14), (-40, -5),
        (28, 20), (34, 18), (38, 24), (32, 30), (36, 10),
        (-20, 35), (-15, 38), (-25, 42), (10, 40), (18, 42),
    ]
    for i, (fx, fy) in enumerate(forest_positions):
        h = rng.uniform(4.5, 8.0)
        cr = rng.uniform(1.8, 3.2)
        fx += rng.uniform(-1.5, 1.5)
        fy += rng.uniform(-1.5, 1.5)
        trees += make_tree(f"Tree_{i+1:02d}", col_nature, fx, fy, h, cr, seed=i*7)
    return trees


def build_bushes(col_nature):
    """Scattered bushes along roads and building edges."""
    bushes = []
    rng = random.Random(55)
    bush_spots = [
        (6, -5), (-6, -3), (8, 8), (-8, 5), (12, -10),
        (-12, 12), (3, -20), (-3, -22), (18, -12), (-18, 6),
        (2, 18), (-4, 16), (8, -15), (-9, -4), (5, 25),
        (15, 5), (-15, -5), (20, -4), (-20, 18), (12, 22),
    ]
    for i, (bx, by) in enumerate(bush_spots):
        bx += rng.uniform(-0.8, 0.8)
        by += rng.uniform(-0.8, 0.8)
        r = rng.uniform(0.5, 1.1)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        mesh = bpy.data.meshes.new(f"Bush_{i+1:02d}_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        mesh.shade_smooth()
        bush = new_obj(f"Bush_{i+1:02d}", mesh, col_nature)
        assign_mat(bush, "M_Grass_Green")
        bush.location = (bx, by, r * 0.5)
        bush.scale = (rng.uniform(0.8, 1.2), rng.uniform(0.8, 1.2), rng.uniform(0.6, 0.9))
        bushes.append(bush)
    return bushes


def build_rocks(col_nature):
    """Scatter boulders and rocks naturally."""
    rocks = []
    rng = random.Random(77)
    rock_spots = [
        (-15, -12), (-18, -18), (-22, -20), (10, -18), (14, -20),
        (-10, -5), (16, 6), (-6, 22), (8, -22), (-28, -5),
        (-30, -12), (22, -14), (-5, -30), (5, -35), (-3, -42),
        (20, 8), (26, -5), (-25, 5), (-32, 18), (14, 28),
        (2, -28), (-8, -22), (18, -18), (-24, -8), (6, 30),
    ]
    for i, (rx, ry) in enumerate(rock_spots):
        rx += rng.uniform(-1.0, 1.0)
        ry += rng.uniform(-1.0, 1.0)
        r = rng.uniform(0.3, 1.4)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        mesh = bpy.data.meshes.new(f"Rock_{i+1:02d}_Mesh")
        # Warp verts for organic look
        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            v.co.x += rng.uniform(-r*0.3, r*0.3)
            v.co.y += rng.uniform(-r*0.3, r*0.3)
            v.co.z = max(-r*0.4, v.co.z + rng.uniform(-r*0.2, r*0.1))
        bm.to_mesh(mesh)
        bm.free()
        rock = new_obj(f"Rock_{i+1:02d}", mesh, col_nature)
        assign_mat(rock, "M_Stone_Rough")
        rock.location = (rx, ry, 0.0)
        rock.scale = (rng.uniform(0.7, 1.3), rng.uniform(0.7, 1.3), rng.uniform(0.4, 0.9))
        rock.rotation_euler.z = rng.uniform(0, math.pi * 2)
        rocks.append(rock)
    return rocks


def build_grass_patches(col_nature):
    """Flat grass patches in natural areas."""
    patches = []
    rng = random.Random(33)
    spots = [
        ((-20, -5), 6), ((-15, 22), 8), ((18, 12), 7),
        ((0, -30), 5), ((-30, 2), 10), ((25, 25), 8),
        ((-5, 30), 9), ((12, -25), 6), ((-10, -30), 7),
    ]
    for i, ((gx, gy), size) in enumerate(spots):
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=size*0.5)
        for v in bm.verts:
            v.co.z += rng.uniform(-0.05, 0.05)
        mesh = bpy.data.meshes.new(f"Grass_Patch_{i+1:02d}_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        patch = new_obj(f"Grass_Patch_{i+1:02d}", mesh, col_nature)
        assign_mat(patch, "M_Grass_Green")
        patch.location = (gx + rng.uniform(-2, 2), gy + rng.uniform(-2, 2), 0.01)
        patch.rotation_euler.z = rng.uniform(0, math.pi * 2)
        patches.append(patch)
    return patches


# ──────────────────────────────────────────────
# 8. FARM AREA
# ──────────────────────────────────────────────

def build_farm(col_farm):
    """Farm fences, haystack and animal pen."""
    items = []
    rng = random.Random(11)

    # Field fence posts + rails
    fence_pts = [(18, 5), (30, 5), (30, 28), (18, 28), (18, 5)]
    for i in range(len(fence_pts) - 1):
        x1, y1 = fence_pts[i]
        x2, y2 = fence_pts[i + 1]
        dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        posts = int(dist / 2.5)
        for p in range(posts + 1):
            t = p / max(posts, 1)
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=0.15)
            mesh = bpy.data.meshes.new(f"FencePost_{i}_{p}_Mesh")
            bm.to_mesh(mesh)
            bm.free()
            post = new_obj(f"FencePost_{i}_{p}", mesh, col_farm)
            assign_mat(post, "M_Aged_Oak")
            post.location = (px, py, 0.7)
            post.scale = (1, 1, 9)
            items.append(post)

    # Haystack
    for hs in range(3):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                              segments=12, radius1=1.4, radius2=0.2, depth=1.8)
        mesh = bpy.data.meshes.new(f"Haystack_{hs}_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        mesh.shade_smooth()
        hay = new_obj(f"Haystack_{hs}", mesh, col_farm)
        assign_mat(hay, "M_Ground_Mud")
        hay.location = (22 + hs*2.5, 22, 0.9)
        items.append(hay)

    return items


# ──────────────────────────────────────────────
# MAIN ENTRY
# ──────────────────────────────────────────────

def build_village_environment():
    print("=== Village World Assembly: START ===")
    rng = random.Random(42)

    # Ensure asset directory
    os.makedirs("c:/Users/ashwi/Documents/Medieval_Village_Project/assets/world", exist_ok=True)

    # ── Collections
    col_terrain = ensure_collection("99_TERRAIN_ATMOSPHERE")
    col_village = ensure_collection("03_VILLAGE_STRUCTURES")
    col_buildings = ensure_collection("01_BUILDINGS")
    col_roads = ensure_collection("05_STREET_OBJECTS")
    col_nature = ensure_collection("06_ENVIRONMENT_NATURE")
    col_farm = ensure_collection("07_FARM", col_nature)

    print("Building terrain...")
    build_terrain(col_terrain)
    print("Building river...")
    build_river(col_terrain)
    print("Building roads...")
    build_roads(col_roads)
    print("Building market square...")
    build_market_square(col_village)
    build_well(col_village)
    build_market_stalls(col_village)
    print("Building village buildings...")
    build_village_buildings(col_buildings, col_village)
    print("Building forest trees...")
    build_forest(col_nature)
    print("Building bushes...")
    build_bushes(col_nature)
    print("Building rocks...")
    build_rocks(col_nature)
    print("Building grass patches...")
    build_grass_patches(col_nature)
    print("Building farm...")
    build_farm(col_farm)

    print("=== Village World Assembly: COMPLETE ===")
    return True

