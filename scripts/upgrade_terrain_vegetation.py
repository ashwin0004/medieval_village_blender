"""
upgrade_terrain_vegetation.py - Realistic Terrain & Vegetation System for Medieval Fantasy Village
Constructs:
- Panoramic Distant Alpine Mountain Range (jagged rock cliffs, vertical rock strata, snow-capped peaks).
- Rolling hills and natural landscape elevation around the village perimeter.
- Assigns rich meadow grass material (M_Grass_Green) to Terrain_Village.
- Realistic Oak trees (gnarled trunks with root flares, spreading scaffold boughs, smooth organic leaf clusters).
- Realistic Alpine Pine trees (tapered trunks with bark fluting, multi-tiered drooping conifer boughs).
- Multi-stemmed leafy bushes hugging foundations, roadsides, and riverbanks.
- Wildflowers: Red wild poppies with translucent petals, dark center seed capsules, and yellow buttercups.
- Multi-blade 3D grass clumps on meadows and slopes.
- Mossy angular field boulders with crevices and mossy tops.
- Decaying fallen logs with branch stubs and moss.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import random

def get_ground_z(x, y, fallback=0.2):
    """Raycasts against Terrain_Village to find exact ground surface."""
    terrain = bpy.data.objects.get("Terrain_Village")
    if not terrain:
        return fallback
    ray_origin = Vector((x, y, 60.0))
    ray_dir = Vector((0.0, 0.0, -1.0))
    mw_inv = terrain.matrix_world.inverted()
    orig_local = mw_inv @ ray_origin
    dir_local = mw_inv.to_3x3() @ ray_dir
    success, loc, normal, face_idx = terrain.ray_cast(orig_local, dir_local)
    if success:
        wloc = terrain.matrix_world @ loc
        return wloc.z
    return fallback

def get_or_create_col(name, parent_name=None):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        if parent_name and bpy.data.collections.get(parent_name):
            bpy.data.collections[parent_name].children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

def link_to_collection(obj, col_name):
    for c in list(obj.users_collection):
        c.unlink(obj)
    col = get_or_create_col(col_name)
    col.objects.link(obj)

# ---------------------------------------------------------------------------
# 1. SHADERS AND MATERIALS
# ---------------------------------------------------------------------------
def ensure_nature_materials():
    """Builds procedural PBR materials for trees, foliage, flowers, rocks, and mountains."""
    # 1. Pine Needles (Rich conifer spruce green with sunlight translucency and soft rough shading)
    mat_pine = bpy.data.materials.get("M_Pine_Needles_Dark") or bpy.data.materials.new("M_Pine_Needles_Dark")
    mat_pine.use_nodes = True
    bsdf = mat_pine.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.035, 0.145, 0.050, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.78
        bsdf.inputs['Specular IOR Level'].default_value = 0.25
        if 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = 0.15
            bsdf.inputs['Subsurface Radius'].default_value = (0.2, 0.8, 0.1)

    # 2. Oak Foliage (Vibrant layered deciduous green with warm highlights and soft volume)
    mat_oak = bpy.data.materials.get("M_Oak_Foliage_Green") or bpy.data.materials.new("M_Oak_Foliage_Green")
    mat_oak.use_nodes = True
    bsdf = mat_oak.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.11, 0.35, 0.07, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.75
        bsdf.inputs['Specular IOR Level'].default_value = 0.3
        if 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = 0.22
            bsdf.inputs['Subsurface Radius'].default_value = (0.3, 0.9, 0.2)

    # 3. Pine Bark (Rugged furrowed dark conifer trunk)
    mat_bark = bpy.data.materials.get("M_Bark_Conifer") or bpy.data.materials.new("M_Bark_Conifer")
    mat_bark.use_nodes = True
    bsdf = mat_bark.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.14, 0.10, 0.08, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.92

    # 4. Bush Foliage
    mat_bush = bpy.data.materials.get("M_Bush_Foliage") or bpy.data.materials.new("M_Bush_Foliage")
    mat_bush.use_nodes = True
    bsdf = mat_bush.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.13, 0.38, 0.08, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.70

    # 5. Wild Poppy Petals (Vivid crimson red with subsurface glow)
    mat_poppy = bpy.data.materials.get("M_Flower_Poppy_Red") or bpy.data.materials.new("M_Flower_Poppy_Red")
    mat_poppy.use_nodes = True
    bsdf = mat_poppy.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.85, 0.03, 0.02, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.32
        if 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = 0.35

    # 6. Wildflower Yellow (Dandelion / Buttercup)
    mat_yel = bpy.data.materials.get("M_Flower_Yellow") or bpy.data.materials.new("M_Flower_Yellow")
    mat_yel.use_nodes = True
    bsdf = mat_yel.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.78, 0.05, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.38
        if 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = 0.25

    # 7. Flower Center (Dark seed capsule)
    mat_cen = bpy.data.materials.get("M_Flower_Center") or bpy.data.materials.new("M_Flower_Center")
    mat_cen.use_nodes = True
    bsdf = mat_cen.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.04, 0.02, 0.03, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.85

    # 8. Flower Stem & Leaves (Deep emerald)
    mat_stem = bpy.data.materials.get("M_Flower_Stem") or bpy.data.materials.new("M_Flower_Stem")
    mat_stem.use_nodes = True
    bsdf = mat_stem.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.08, 0.32, 0.06, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.60

    # 9. Decaying Log Bark with Moss
    mat_log = bpy.data.materials.get("M_Log_Mossy_Bark") or bpy.data.materials.new("M_Log_Mossy_Bark")
    mat_log.use_nodes = True
    bsdf = mat_log.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.22, 0.18, 0.12, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.88

    # 10. Distant Alpine Mountain Shader (Dark rugged rock cliffs, vertical strata, snow only on high peaks)
    mat_mtn = bpy.data.materials.get("M_Mountain_Alpine") or bpy.data.materials.new("M_Mountain_Alpine")
    mat_mtn.use_nodes = True
    nodes = mat_mtn.node_tree.nodes
    links = mat_mtn.node_tree.links
    nodes.clear()

    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-900, 200)

    sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
    sep_xyz.location = (-700, 100)
    links.new(tex_coord.outputs['Object'], sep_xyz.inputs['Vector'])

    geom = nodes.new('ShaderNodeNewGeometry')
    geom.location = (-900, -200)
    sep_norm = nodes.new('ShaderNodeSeparateXYZ')
    sep_norm.location = (-700, -200)
    links.new(geom.outputs['Normal'], sep_norm.inputs['Vector'])

    # Snow mask: only above 52 meters (Z > 52m) AND on moderate slope (Normal Z > 0.48)
    alt_ramp = nodes.new('ShaderNodeValToRGB')
    alt_ramp.location = (-450, 150)
    alt_ramp.color_ramp.elements[0].position = 0.62 # starts at ~52m
    alt_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    alt_ramp.color_ramp.elements[1].position = 0.85 # fully snow at ~72m
    alt_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

    alt_math = nodes.new('ShaderNodeMath')
    alt_math.location = (-580, 150)
    alt_math.operation = 'DIVIDE'
    alt_math.inputs[1].default_value = 85.0
    links.new(sep_xyz.outputs['Z'], alt_math.inputs[0])
    links.new(alt_math.outputs['Value'], alt_ramp.inputs['Fac'])

    slope_ramp = nodes.new('ShaderNodeValToRGB')
    slope_ramp.location = (-450, -150)
    slope_ramp.color_ramp.elements[0].position = 0.45
    slope_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    slope_ramp.color_ramp.elements[1].position = 0.65
    slope_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    links.new(sep_norm.outputs['Z'], slope_ramp.inputs['Fac'])

    snow_mult = nodes.new('ShaderNodeMath')
    snow_mult.location = (-250, 50)
    snow_mult.operation = 'MULTIPLY'
    links.new(alt_ramp.outputs['Color'], snow_mult.inputs[0])
    links.new(slope_ramp.outputs['Color'], snow_mult.inputs[1])

    # Vertical rock strata noise
    mapping_strata = nodes.new('ShaderNodeMapping')
    mapping_strata.location = (-700, -400)
    mapping_strata.inputs['Scale'].default_value = (0.05, 0.05, 0.4) # stretched vertically
    links.new(tex_coord.outputs['Object'], mapping_strata.inputs['Vector'])

    noise_rock = nodes.new('ShaderNodeTexNoise')
    noise_rock.location = (-500, -400)
    noise_rock.inputs['Scale'].default_value = 8.0
    noise_rock.inputs['Detail'].default_value = 5.0
    links.new(mapping_strata.outputs['Vector'], noise_rock.inputs['Vector'])

    rock_ramp = nodes.new('ShaderNodeValToRGB')
    rock_ramp.location = (-280, -400)
    rock_ramp.color_ramp.elements[0].position = 0.3
    rock_ramp.color_ramp.elements[0].color = (0.14, 0.13, 0.12, 1.0) # dark granite
    rock_ramp.color_ramp.elements[1].position = 0.7
    rock_ramp.color_ramp.elements[1].color = (0.28, 0.25, 0.22, 1.0) # weathered rock
    links.new(noise_rock.outputs['Fac'], rock_ramp.inputs['Fac'])

    col_mix = nodes.new('ShaderNodeMix')
    col_mix.location = (0, 100)
    col_mix.data_type = 'RGBA'
    links.new(rock_ramp.outputs['Color'], col_mix.inputs['A'])
    col_mix.inputs['B'].default_value = (0.95, 0.97, 0.99, 1.0) # Snow
    links.new(snow_mult.outputs['Value'], col_mix.inputs['Factor'])

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (250, 100)
    bsdf.inputs['Roughness'].default_value = 0.82
    links.new(col_mix.outputs['Result'], bsdf.inputs['Base Color'])

    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (500, 100)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

def get_mat(name, fallback="M_Wood_AgedOak"):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)

# ---------------------------------------------------------------------------
# 2. DISTANT ALPINE MOUNTAINS BACKDROP
# ---------------------------------------------------------------------------
def build_distant_mountain_range(col_name="99_TERRAIN_ATMOSPHERE"):
    """
    Constructs a vast panoramic alpine mountain range with jagged peaks, rock cliffs, and snowy crests.
    Matches Reference Images 1, 2, and 3.
    """
    obj_name = "Mountain_Range_Backdrop"
    old = bpy.data.objects.get(obj_name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    mesh = bpy.data.meshes.new(obj_name)
    bm = bmesh.new()

    rings = 12
    sectors = 72
    r_in = 68.0
    r_out = 240.0

    verts_grid = []
    random.seed(202)

    for r in range(rings):
        t = r / (rings - 1)
        rad = r_in + t * (r_out - r_in)
        row = []
        for s in range(sectors):
            ang = 2 * math.pi * s / sectors
            # Sharp alpine peaks using absolute power harmonics
            f1 = (math.sin(s * 2.1) ** 2) * 22.0 + math.cos(s * 4.3) * 12.0
            f2 = math.sin(s * 7.5) * 8.0 + math.cos(s * 13.2) * 4.5
            f3 = math.sin(s * 25.0) * 2.0

            peak_factor = (f1 + f2 + f3)
            # Base height rises with radius to create dramatic valley amphitheater
            h = (t ** 1.8) * (52.0 + peak_factor)

            # River valley canyon notch to the North-East
            if 1.25 < ang < 1.85:
                h *= 0.35 + 0.15 * math.cos((ang - 1.55) * 8.0)

            # Castle rock spires to the West-South-West
            if 3.0 < ang < 3.8:
                h = max(h, (t ** 1.4) * 78.0)

            vx = rad * math.cos(ang)
            vy = rad * math.sin(ang)
            vz = max(0.5, h)
            row.append(bm.verts.new((vx, vy, vz)))
        verts_grid.append(row)

    for r in range(rings - 1):
        for s in range(sectors):
            s_next = (s + 1) % sectors
            bm.faces.new([
                verts_grid[r][s],
                verts_grid[r][s_next],
                verts_grid[r+1][s_next],
                verts_grid[r+1][s]
            ])

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(obj_name, mesh)
    mat_mtn = get_mat("M_Mountain_Alpine")
    obj.data.materials.append(mat_mtn)
    link_to_collection(obj, col_name)

    for poly in mesh.polygons:
        poly.use_smooth = True

    sub = obj.modifiers.new("Subdivision", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    print(f"Built Distant Mountain Range: {len(mesh.vertices)} verts, {len(mesh.polygons)} faces")
    return obj

# ---------------------------------------------------------------------------
# 3. ROLLING HILLS & MEADOW GRASS ON TERRAIN
# ---------------------------------------------------------------------------
def enhance_terrain_mesh():
    """
    Applies M_Grass_Green to Terrain_Village and sculpts rolling hills and meadow mounds
    outside the village core, preserving roads and building foundations.
    """
    terrain = bpy.data.objects.get("Terrain_Village")
    if not terrain:
        print("Terrain_Village not found!")
        return

    # Assign M_Grass_Green as primary material
    mat_grass = get_mat("M_Grass_Green")
    if terrain.data.materials:
        terrain.data.materials[0] = mat_grass
    else:
        terrain.data.materials.append(mat_grass)

    me = terrain.data
    core_cx, core_cy = 0.0, -10.0
    core_rad = 34.0
    blend_zone = 20.0

    for v in me.vertices:
        dx = v.co.x - core_cx
        dy = v.co.y - core_cy
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < core_rad:
            continue

        blend = min(1.0, max(0.0, (dist - core_rad) / blend_zone))
        hill_wave = (
            math.sin(v.co.x * 0.08) * math.cos(v.co.y * 0.07) * 2.8 +
            math.sin(v.co.x * 0.15 + 1.2) * math.cos(v.co.y * 0.14) * 1.5 +
            math.sin(v.co.x * 0.04) * 3.5
        )
        v.co.z += hill_wave * (blend ** 1.5)

    me.update()
    print("Enhanced Terrain_Village with rolling hills and M_Grass_Green.")

# ---------------------------------------------------------------------------
# 4. REALISTIC TREE BUILDERS (OAKS & PINES)
# ---------------------------------------------------------------------------
def build_pine_tree(name, pos, scale=1.0, col_name="06_ENVIRONMENT_NATURE"):
    """
    Builds a realistic Scots / Alpine Pine with smooth drooping conifer boughs and bark.
    """
    gz = get_ground_z(pos[0], pos[1])
    h = (11.0 + random.uniform(-1.5, 2.5)) * scale
    r_bot = (0.34 + random.uniform(-0.04, 0.06)) * scale
    r_top = 0.05 * scale

    mat_trunk = get_mat("M_Bark_Conifer", "M_Wood_DarkTimber")
    mat_needles = get_mat("M_Pine_Needles_Dark", "M_Grass_Green")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    lean_x = random.uniform(-0.03, 0.03)
    lean_y = random.uniform(-0.03, 0.03)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=r_bot, radius2=r_top, depth=h,
                          matrix=Matrix.Translation((lean_x, lean_y, h / 2.0)))

    # Lower dead branch stubs
    for stub_z in [1.5 * scale, 2.2 * scale, 2.8 * scale]:
        sang = random.uniform(0, 2 * math.pi)
        sx, sy = math.cos(sang), math.sin(sang)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=0.06*scale, radius2=0.01, depth=0.6*scale,
                              matrix=Matrix.Translation((sx * 0.35 * scale, sy * 0.35 * scale, stub_z)))

    for f in bm.faces:
        f.material_index = 0

    # 8 tiers of conifer needle boughs
    tiers = 8
    for t in range(tiers):
        t_fac = t / (tiers - 1)
        tier_z = (3.2 + t_fac * (h - 3.8))
        tier_r = (1.0 - 0.72 * t_fac) * (3.0 * scale)
        tier_h = (1.6 * (1.0 - 0.45 * t_fac)) * scale

        f_start = len(bm.faces)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=12,
                              radius1=tier_r, radius2=0.06 * scale, depth=tier_h,
                              matrix=Matrix.Translation((lean_x * t_fac, lean_y * t_fac, tier_z + tier_h / 2.0)))
        for f in bm.faces[f_start:]:
            f.material_index = 1

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_trunk)
    obj.data.materials.append(mat_needles)
    obj.location = (pos[0], pos[1], gz)
    obj.rotation_euler = Euler((0, 0, random.uniform(0, 2 * math.pi)))

    for poly in mesh.polygons:
        poly.use_smooth = True

    link_to_collection(obj, col_name)
    return obj

def build_oak_tree(name, pos, scale=1.0, col_name="06_ENVIRONMENT_NATURE"):
    """
    Builds a majestic spreading Medieval Oak with smooth organic leaf clusters.
    """
    gz = get_ground_z(pos[0], pos[1])
    mat_trunk = get_mat("M_Aged_Oak", "M_Wood_AgedOak")
    mat_foliage = get_mat("M_Oak_Foliage_Green", "M_Grass_Green")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    trunk_h = (3.8 + random.uniform(-0.3, 0.4)) * scale
    r_base = (0.65 + random.uniform(-0.05, 0.08)) * scale
    r_crotch = 0.38 * scale

    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=r_base, radius2=r_crotch, depth=trunk_h,
                          matrix=Matrix.Translation((0, 0, trunk_h / 2.0)))

    # Root flares
    for i in range(4):
        rang = i * (math.pi / 2) + 0.2
        rx, ry = math.cos(rang) * r_base * 0.9, math.sin(rang) * r_base * 0.9
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.28*scale, radius2=0.08*scale, depth=1.2*scale,
                              matrix=Matrix.Translation((rx, ry, 0.4*scale)) @ Euler((0.4 * ry, -0.4 * rx, rang)).to_matrix().to_4x4())

    # 4 major scaffold boughs
    bough_angles = [0.2, 1.7, 3.3, 4.8]
    for b_idx, ang in enumerate(bough_angles):
        b_len = (3.5 + random.uniform(-0.3, 0.5)) * scale
        dx = math.cos(ang) * 1.5 * scale
        dy = math.sin(ang) * 1.5 * scale
        dz = trunk_h + 1.2 * scale
        b_rot = Euler((math.radians(38) * math.sin(ang), math.radians(38) * math.cos(ang), ang))
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.26*scale, radius2=0.09*scale, depth=b_len,
                              matrix=Matrix.Translation((dx, dy, dz)) @ b_rot.to_matrix().to_4x4())

    for f in bm.faces:
        f.material_index = 0

    # 14 Volumetric leaf-mass clumps
    clump_coords = [
        ( 3.2,  0.5, trunk_h + 2.2, 2.2),
        (-3.0,  0.8, trunk_h + 2.4, 2.3),
        ( 0.4,  3.2, trunk_h + 2.1, 2.2),
        (-0.5, -3.2, trunk_h + 2.5, 2.4),
        ( 2.2,  2.2, trunk_h + 2.6, 2.1),
        (-2.2,  2.2, trunk_h + 2.3, 2.0),
        ( 2.2, -2.2, trunk_h + 2.4, 2.1),
        (-2.2, -2.2, trunk_h + 2.5, 2.2),
        ( 1.5,  0.0, trunk_h + 3.8, 2.4),
        (-1.5,  0.0, trunk_h + 3.6, 2.3),
        ( 0.0,  1.5, trunk_h + 3.9, 2.4),
        ( 0.0, -1.5, trunk_h + 3.7, 2.3),
        ( 0.0,  0.0, trunk_h + 4.8, 2.8),
        ( 0.2,  0.2, trunk_h + 5.5, 2.0),
    ]

    for cx, cy, cz, cr in clump_coords:
        f_start = len(bm.faces)
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=cr * scale,
                                  matrix=Matrix.Translation((cx * scale, cy * scale, cz * scale)))
        for f in bm.faces[f_start:]:
            f.material_index = 1

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_trunk)
    obj.data.materials.append(mat_foliage)
    obj.location = (pos[0], pos[1], gz)
    obj.rotation_euler = Euler((0, 0, random.uniform(0, 2 * math.pi)))

    for poly in mesh.polygons:
        poly.use_smooth = True

    link_to_collection(obj, col_name)
    return obj

# ---------------------------------------------------------------------------
# 5. BUSHES, WILDFLOWERS, ROCKS, LOGS, GRASS
# ---------------------------------------------------------------------------
def build_bush(name, pos, scale=1.0, col_name="06_ENVIRONMENT_NATURE"):
    """Builds a multi-lobed leafy understory shrub with smooth shading."""
    gz = get_ground_z(pos[0], pos[1])
    mat = get_mat("M_Bush_Foliage", "M_Oak_Foliage_Green")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    for i in range(5):
        ang = i * (2 * math.pi / 5)
        bx = math.cos(ang) * 0.45 * scale
        by = math.sin(ang) * 0.45 * scale
        bz = 0.55 * scale
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.65 * scale,
                                  matrix=Matrix.Translation((bx, by, bz)))
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.75 * scale,
                              matrix=Matrix.Translation((0, 0, 0.85 * scale)))

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    obj.location = (pos[0], pos[1], gz)
    for poly in mesh.polygons:
        poly.use_smooth = True
    link_to_collection(obj, col_name)
    return obj

def build_wildflower_patch(name, pos, flower_type="poppy", count=10, col_name="06_ENVIRONMENT_NATURE"):
    """
    Builds a patch of wild poppies (red) or buttercups (yellow) with green stems,
    broad petals, and dark stamen center capsules. Matches Reference Image 5.
    """
    gz = get_ground_z(pos[0], pos[1])
    mat_stem = get_mat("M_Flower_Stem")
    mat_petal = get_mat("M_Flower_Poppy_Red") if flower_type == "poppy" else get_mat("M_Flower_Yellow")
    mat_center = get_mat("M_Flower_Center")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    for i in range(count):
        off_x = random.uniform(-0.5, 0.5)
        off_y = random.uniform(-0.5, 0.5)
        stem_h = random.uniform(0.38, 0.58)

        # 1. Stem (emerald green)
        f_start = len(bm.faces)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=0.015, radius2=0.010, depth=stem_h,
                              matrix=Matrix.Translation((off_x, off_y, stem_h / 2.0)))
        for f in bm.faces[f_start:]:
            f.material_index = 0

        # 2. Blossom Petals (wide cup petals)
        f_start = len(bm.faces)
        p_rad = 0.13 if flower_type == "poppy" else 0.10
        bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=p_rad, radius2=0.03, depth=0.05,
                              matrix=Matrix.Translation((off_x, off_y, stem_h + 0.025)))
        for f in bm.faces[f_start:]:
            f.material_index = 1

        # 3. Flower Center Capsule (dark stamen)
        f_start = len(bm.faces)
        bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=0.025,
                                  matrix=Matrix.Translation((off_x, off_y, stem_h + 0.02)))
        for f in bm.faces[f_start:]:
            f.material_index = 2

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_stem)
    obj.data.materials.append(mat_petal)
    obj.data.materials.append(mat_center)
    obj.location = (pos[0], pos[1], gz)
    for poly in mesh.polygons:
        poly.use_smooth = True
    link_to_collection(obj, col_name)
    return obj

def build_grass_clump(name, pos, scale=1.0, col_name="06_ENVIRONMENT_NATURE"):
    """Builds a multi-blade arched grass tuft with smooth normal shading."""
    gz = get_ground_z(pos[0], pos[1])
    mat = get_mat("M_Grass_Green")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    num_blades = 14
    for b in range(num_blades):
        ang = b * (2 * math.pi / num_blades) + random.uniform(-0.2, 0.2)
        b_len = (0.45 + random.uniform(-0.1, 0.18)) * scale
        w = 0.03 * scale

        c, s = math.cos(ang), math.sin(ang)
        v1 = bm.verts.new((-w * s, w * c, 0))
        v2 = bm.verts.new(( w * s, -w * c, 0))
        v3 = bm.verts.new((c * b_len * 0.7, s * b_len * 0.7, b_len * 0.6))
        v4 = bm.verts.new((c * b_len, s * b_len, b_len * 0.85))

        bm.faces.new([v1, v2, v3])
        bm.faces.new([v2, v4, v3])

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    obj.location = (pos[0], pos[1], gz)
    for poly in mesh.polygons:
        poly.use_smooth = True
    link_to_collection(obj, col_name)
    return obj

def build_mossy_boulder(name, pos, scale=1.0, col_name="06_ENVIRONMENT_NATURE"):
    """
    Builds an angular fractured field boulder with bevelled faceted faces and moss.
    Matches Reference Image 5.
    """
    gz = get_ground_z(pos[0], pos[1])
    mat_stone = get_mat("M_Stone_Rubble", "M_Stone_Rough")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0 * scale)
    for v in bm.verts:
        v.co.x *= (1.2 + random.uniform(-0.15, 0.15))
        v.co.y *= (0.85 + random.uniform(-0.15, 0.15))
        v.co.z *= (0.75 + random.uniform(-0.1, 0.1))
        if v.co.z < 0:
            v.co.z *= 0.4

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_stone)
    obj.location = (pos[0], pos[1], gz + 0.3 * scale)
    obj.rotation_euler = Euler((random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), random.uniform(0, 2*math.pi)))

    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.04 * scale
    bev.segments = 2

    link_to_collection(obj, col_name)
    return obj

def build_fallen_log(name, pos, angle_deg=35, length=4.5, col_name="06_ENVIRONMENT_NATURE"):
    """Builds a decaying mossy fallen tree trunk with broken branches."""
    gz = get_ground_z(pos[0], pos[1])
    mat = get_mat("M_Log_Mossy_Bark", "M_Wood_DarkTimber")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    r = 0.32
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=r, radius2=r * 0.7, depth=length,
                          matrix=Matrix.Translation((0, 0, length / 2.0)))

    bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=0.08, radius2=0.02, depth=0.7,
                          matrix=Matrix.Translation((0.25, 0.1, length * 0.4)) @ Euler((0.8, 0, 0)).to_matrix().to_4x4())

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    rot_rad = math.radians(angle_deg)
    obj.location = (pos[0], pos[1], gz + r * 0.7)
    obj.rotation_euler = Euler((math.radians(90), 0, rot_rad))
    link_to_collection(obj, col_name)
    return obj

# ---------------------------------------------------------------------------
# 6. MASTER EXECUTION WORKFLOW
# ---------------------------------------------------------------------------
def execute_upgrade_terrain_vegetation():
    print("==================================================")
    print("STARTING UPGRADE OF TERRAIN & VEGETATION")
    print("==================================================")

    env_col = get_or_create_col("06_ENVIRONMENT_NATURE")
    atm_col = get_or_create_col("99_TERRAIN_ATMOSPHERE")

    # Clear previous vegetation objects in 06_ENVIRONMENT_NATURE
    print("Cleaning up previous vegetation objects...")
    for o in list(env_col.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    # 1. Materials
    ensure_nature_materials()

    # 2. Distant Alpine Mountain Range Backdrop
    build_distant_mountain_range("99_TERRAIN_ATMOSPHERE")

    # 3. Rolling hills & Meadow Grass
    enhance_terrain_mesh()

    # 4. Realistic Alpine Pine Trees
    pine_coordinates = [
        # West & Castle Ridge (framing watchtower)
        (-38.0, 12.0, 1.2), (-35.0, 18.0, 1.1), (-29.0, 22.0, 1.0), (-42.0, 24.0, 1.3),
        (-34.0, -2.0, 1.0), (-42.0, 4.0, 1.2), (-36.0, -9.0, 1.1), (-45.0, -12.0, 1.4),
        (-40.0, -18.0, 1.2), (-32.0, -22.0, 1.0), (-38.0, -28.0, 1.3), (-44.0, -32.0, 1.2),
        (-26.0, 28.0, 1.0), (-32.0, 34.0, 1.2), (-38.0, 38.0, 1.3), (-44.0, 42.0, 1.4),
        # North River & Bridge Forest
        (-18.0, 32.0, 1.1), (-12.0, 36.0, 1.2), (-5.0, 38.0, 1.0), (2.0, 42.0, 1.3),
        (8.0, 36.0, 1.1), (15.0, 38.0, 1.2), (22.0, 34.0, 1.0), (28.0, 38.0, 1.3),
        # East Church Hill & Outskirts
        (25.0, 18.0, 1.1), (32.0, 14.0, 1.2), (38.0, 8.0, 1.3), (42.0, 18.0, 1.4),
        (28.0, 2.0, 1.0), (35.0, -5.0, 1.2), (40.0, -12.0, 1.3), (44.0, -20.0, 1.2),
        (32.0, -26.0, 1.1), (38.0, -32.0, 1.3), (25.0, -38.0, 1.0), (32.0, -44.0, 1.2),
        # South Valley Gate frames
        (-16.0, -52.0, 1.1), (-22.0, -56.0, 1.3), (16.0, -52.0, 1.1), (22.0, -56.0, 1.3),
    ]
    for idx, (px, py, pscale) in enumerate(pine_coordinates):
        build_pine_tree(f"Pine_Tree_{idx:02d}", (px, py), scale=pscale, col_name="06_ENVIRONMENT_NATURE")

    # 5. Realistic Spreading Medieval Oak Trees
    oak_coordinates = [
        (13.0, -4.0, 1.2),   # Great Village Oak
        (-18.5, -36.0, 1.0), # Cottage 2 Oak
        (18.0, -38.0, 1.05), # Cottage 3 Oak
        (-8.0, -38.0, 0.95),
        (12.0, 15.0, 1.1),   # Churchyard Oak
        (-8.0, 12.0, 1.0),   # Barn Oak
        (-22.0, 6.0, 1.05),  # Blacksmith Oak
        (-2.0, 22.0, 1.1),   # Riverbank Oak
        (18.0, 25.0, 1.15),  # East Riverbend Oak
        (-5.0, -48.0, 1.1),
        (6.0, -48.0, 1.0),
        (28.0, -18.0, 1.1),
        (-28.0, -38.0, 1.0),
    ]
    for idx, (ox, oy, oscale) in enumerate(oak_coordinates):
        build_oak_tree(f"Oak_Tree_{idx:02d}", (ox, oy), scale=oscale, col_name="06_ENVIRONMENT_NATURE")

    # 6. Bushes & Understory Shrubs (placed on soil/grass along walls)
    bush_coords = [
        (3.5, -12.0, 0.9), (6.5, -12.5, 1.1), (-14.0, -25.0, 0.8), (14.0, -29.0, 0.9),
        (-12.0, 15.0, 1.0), (16.0, 8.0, 1.1), (-24.0, -12.0, 1.2), (18.0, -6.0, 0.9),
        (4.5, 18.5, 1.2), (7.5, 18.0, 1.1), (3.0, 25.0, 1.0), (9.0, 25.5, 1.2),
        (-8.0, 20.0, 1.1), (14.0, 21.0, 1.0), (-14.0, 21.0, 1.2),
        (-4.0, -32.0, 0.8), (4.0, -34.0, 0.9), (-4.5, -42.0, 1.0), (4.5, -44.0, 0.85),
    ]
    for b_idx, (bx, by, bsc) in enumerate(bush_coords):
        build_bush(f"Bush_Foliage_{b_idx:02d}", (bx, by), scale=bsc, col_name="06_ENVIRONMENT_NATURE")

    # 7. Wildflower Patches (Lush meadows around Great Oak and riverbanks, matching Ref 5)
    flower_coords = [
        # Meadow around Great Oak (Hero vignette)
        (11.5, -3.2, "poppy"), (12.2, -2.6, "poppy"), (11.0, -2.5, "poppy"),
        (11.8, -3.8, "yellow"), (12.6, -3.2, "yellow"), (10.8, -3.5, "yellow"),
        # Cottage gardens
        (-15.0, -24.0, "poppy"), (15.0, -27.0, "poppy"),
        (-16.0, -26.0, "yellow"), (16.0, -29.0, "yellow"),
        # Riverbanks & Bridge
        (2.0, 18.5, "poppy"), (10.0, 18.5, "poppy"), (-4.0, 18.0, "yellow"),
        # Church hill
        (10.0, 14.0, "poppy"), (14.0, 16.0, "yellow"),
        # South meadows
        (-6.0, -45.0, "poppy"), (7.0, -45.0, "yellow"),
    ]
    for f_idx, (fx, fy, ftype) in enumerate(flower_coords):
        build_wildflower_patch(f"Wildflowers_{ftype}_{f_idx:02d}", (fx, fy), flower_type=ftype, count=10, col_name="06_ENVIRONMENT_NATURE")

    # 8. Grass Clumps
    grass_coords = [
        (11.2, -3.0), (12.0, -3.5), (10.6, -2.8), (12.4, -2.2),
        (-14.5, -24.5), (14.5, -27.5), (-5.5, -44.0), (6.5, -44.0),
        (3.0, 18.0), (9.0, 18.0), (-3.0, 18.0), (11.0, 15.0),
        (13.0, 14.0), (-7.0, 11.0), (-21.0, 5.0), (19.0, -37.0),
    ]
    for g_idx, (gx, gy) in enumerate(grass_coords):
        build_grass_clump(f"Grass_Clump_{g_idx:02d}", (gx, gy), scale=1.0, col_name="06_ENVIRONMENT_NATURE")

    # 9. Mossy Field Boulders (including hero vignette at 11.6, -2.8)
    rock_coords = [
        # Hero Meadow Boulder Cluster (Ref 5)
        (11.8, -2.7, 1.2), (12.5, -2.2, 0.9), (11.0, -3.2, 0.7),
        # River boulders
        (2.5, 21.5, 1.1), (5.5, 21.0, 1.3), (8.5, 22.0, 1.0), (-2.0, 21.5, 1.2),
        # Hillside and pasture boulders
        (-22.0, -24.0, 1.5), (24.0, -26.0, 1.4), (-18.0, 28.0, 1.6), (18.0, 30.0, 1.5),
        (-30.0, 8.0, 1.8), (30.0, 8.0, 1.7), (-28.0, -8.0, 1.6), (28.0, -8.0, 1.5),
    ]
    for r_idx, (rx, ry, rsc) in enumerate(rock_coords):
        build_mossy_boulder(f"Mossy_Boulder_{r_idx:02d}", (rx, ry), scale=rsc, col_name="06_ENVIRONMENT_NATURE")

    # 10. Decaying Fallen Logs with Moss
    log_coords = [
        (11.5, -1.8, 25, 3.8), # Hero log in meadow
        (-26.0, 15.0, 40, 4.8),
        (24.0, 22.0, -25, 4.2),
        (-14.0, 32.0, 65, 5.0),
        (16.0, 34.0, -45, 4.5),
        (-22.0, -42.0, 15, 4.6),
    ]
    for l_idx, (lx, ly, lang, llen) in enumerate(log_coords):
        build_fallen_log(f"Fallen_Log_{l_idx:02d}", (lx, ly), angle_deg=lang, length=llen, col_name="06_ENVIRONMENT_NATURE")

    print("==================================================")
    print("TERRAIN & VEGETATION UPGRADE COMPLETE!")
    print(f"Generated {len(pine_coordinates)} Pines, {len(oak_coordinates)} Oaks,")
    print(f"{len(bush_coords)} Bushes, {len(flower_coords)} Flower Patches,")
    print(f"{len(rock_coords)} Boulders, {len(log_coords)} Fallen Logs,")
    print("plus Distant Mountain Range and Rolling Hills.")
    print("==================================================")

if __name__ == "__main__":
    execute_upgrade_terrain_vegetation()
