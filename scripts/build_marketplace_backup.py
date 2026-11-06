"""
build_marketplace.py - Realistic Medieval Central Marketplace Generator for Blender 4.x
Constructs:
- Detailed Stone Well with fieldstone basin, coping ring, timber canopy, windlass, rope, and bucket.
- 4 Modular Thematic Market Stalls with timber frames, sagging striped fabric canopies, display tables.
- Blacksmith / Toolmonger outpost station with anvil on stump and iron wares.
- 4-Wheeled Harvest Wagon & 2-Wheeled Handcarts.
- Crates, bulging burlap sacks, wicker baskets, barrels, produce (apples, cabbages, potatoes, cheese, bread).
- Oak benches, wrought-iron lanterns, painted trade signs.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import random

def get_ground_z(x, y, fallback=0.2):
    """Raycasts against Road_Market_Plaza and Terrain_Village to find exact ground surface."""
    best_z = -999.0
    for obj_name in ["Road_Market_Plaza", "Terrain_Village"]:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
        ray_origin = Vector((x, y, 50.0))
        ray_dir = Vector((0.0, 0.0, -1.0))
        mw_inv = obj.matrix_world.inverted()
        orig_local = mw_inv @ ray_origin
        dir_local = mw_inv.to_3x3() @ ray_dir
        success, loc, normal, face_idx = obj.ray_cast(orig_local, dir_local)
        if success:
            wloc = obj.matrix_world @ loc
            if wloc.z > best_z:
                best_z = wloc.z
    return best_z if best_z > -900 else fallback

def get_or_create_collection(name, parent_name=None):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        if parent_name and bpy.data.collections.get(parent_name):
            bpy.data.collections[parent_name].children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

def link_to_collection(obj, col_name):
    # Unlink from other collections
    for c in obj.users_collection:
        c.unlink(obj)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)

# ---------------------------------------------------------------------------
# MATERIALS SETUP
# ---------------------------------------------------------------------------
def ensure_marketplace_materials():
    """Create or retrieve specialized materials for the market."""
    def create_striped_canopy(name, color_a, color_b, stripe_freq=18.0):
        if name in bpy.data.materials:
            return bpy.data.materials[name]
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        tex_coord = nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (-800, 200)

        mapping = nodes.new('ShaderNodeMapping')
        mapping.location = (-600, 200)
        mapping.inputs['Scale'].default_value = (stripe_freq, stripe_freq, 1.0)
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

        # Wave texture for crisp woven stripes
        wave = nodes.new('ShaderNodeTexWave')
        wave.location = (-400, 200)
        wave.wave_type = 'BANDS'
        wave.bands_direction = 'X'
        wave.wave_profile = 'TRI'
        wave.inputs['Scale'].default_value = 1.0
        wave.inputs['Distortion'].default_value = 0.35
        wave.inputs['Detail'].default_value = 4.0
        links.new(mapping.outputs['Vector'], wave.inputs['Vector'])

        color_ramp = nodes.new('ShaderNodeValToRGB')
        color_ramp.location = (-150, 200)
        color_ramp.color_ramp.interpolation = 'CONSTANT'
        color_ramp.color_ramp.elements[0].position = 0.48
        color_ramp.color_ramp.elements[0].color = color_a
        color_ramp.color_ramp.elements[1].position = 0.52
        color_ramp.color_ramp.elements[1].color = color_b
        links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])

        # Fabric weave bump
        noise = nodes.new('ShaderNodeTexNoise')
        noise.location = (-400, -150)
        noise.inputs['Scale'].default_value = 120.0
        noise.inputs['Detail'].default_value = 6.0
        noise.inputs['Roughness'].default_value = 0.7

        bump = nodes.new('ShaderNodeBump')
        bump.location = (-150, -150)
        bump.inputs['Strength'].default_value = 0.15
        bump.inputs['Distance'].default_value = 0.02
        links.new(noise.outputs['Fac'], bump.inputs['Height'])

        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (150, 200)
        bsdf.inputs['Roughness'].default_value = 0.85
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

        out = nodes.new('ShaderNodeOutputMaterial')
        out.location = (450, 200)
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        return mat

    # Striped canopies
    ensure_mat("M_Canopy_Striped_Green", lambda: create_striped_canopy(
        "M_Canopy_Striped_Green", (0.05, 0.28, 0.12, 1.0), (0.92, 0.89, 0.80, 1.0), stripe_freq=16.0))
    ensure_mat("M_Canopy_Striped_Red", lambda: create_striped_canopy(
        "M_Canopy_Striped_Red", (0.55, 0.08, 0.06, 1.0), (0.93, 0.88, 0.82, 1.0), stripe_freq=16.0))
    ensure_mat("M_Canopy_Striped_Blue", lambda: create_striped_canopy(
        "M_Canopy_Striped_Blue", (0.08, 0.22, 0.52, 1.0), (0.94, 0.92, 0.86, 1.0), stripe_freq=16.0))
    ensure_mat("M_Canopy_Striped_Yellow", lambda: create_striped_canopy(
        "M_Canopy_Striped_Yellow", (0.75, 0.52, 0.08, 1.0), (0.92, 0.88, 0.80, 1.0), stripe_freq=16.0))

    # Canvas Natural
    if "M_Canopy_Canvas_Natural" not in bpy.data.materials:
        mat = bpy.data.materials.new("M_Canopy_Canvas_Natural")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 80.0
        noise.inputs['Detail'].default_value = 5.0
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.3
        ramp.color_ramp.elements[0].color = (0.72, 0.65, 0.52, 1.0)
        ramp.color_ramp.elements[1].position = 0.7
        ramp.color_ramp.elements[1].color = (0.86, 0.80, 0.68, 1.0)
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Roughness'].default_value = 0.9
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        out = nodes.new('ShaderNodeOutputMaterial')
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Produce materials
    if "M_Produce_Apple" not in bpy.data.materials:
        mat = bpy.data.materials.new("M_Produce_Apple")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.68, 0.04, 0.03, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.32

    if "M_Produce_Cabbage" not in bpy.data.materials:
        mat = bpy.data.materials.new("M_Produce_Cabbage")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.18, 0.45, 0.12, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.65

    if "M_Produce_Potato" not in bpy.data.materials:
        mat = bpy.data.materials.new("M_Produce_Potato")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.42, 0.32, 0.20, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.90

    if "M_Produce_Bread" not in bpy.data.materials:
        mat = bpy.data.materials.new("M_Produce_Bread")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.65, 0.42, 0.18, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.85

    if "M_Produce_Cheese" not in bpy.data.materials:
        mat = bpy.data.materials.new("M_Produce_Cheese")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.88, 0.68, 0.16, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.45

def ensure_mat(name, creator_func):
    if name not in bpy.data.materials:
        creator_func()
    return bpy.data.materials.get(name)

def get_mat(name, fallback="M_Wood_AgedOak"):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)

# ---------------------------------------------------------------------------
# GEOMETRY GENERATION HELPERS
# ---------------------------------------------------------------------------
def create_cylinder_mesh(name, r1, r2, depth, segments=16, mat=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=r1, radius2=r2, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    return obj

def create_cube_mesh(name, size=(1.0, 1.0, 1.0), mat=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # Scale to desired dimensions
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_bevel(obj, width=0.015, segments=2):
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = width
    bev.segments = segments
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    return bev

# ---------------------------------------------------------------------------
# 1. DETAILED STONE WELL
# ---------------------------------------------------------------------------
def build_stone_well(center_x=0.0, center_y=-19.5, col_name="03_VILLAGE_STRUCTURES"):
    """
    Builds realistic medieval stone well:
    - Stepped stone circular apron with mossy cobblestone ring.
    - Dressed fieldstone basin (outer r=1.2m, inner r=0.9m, h=0.95m).
    - Rounded stone coping rim.
    - Deep shaft with reflecting water plane.
    - Heavy oak twin upright posts with 45° knee braces.
    - Cross tie-beam and gabled timber roof canopy with scalloped shingles.
    - Oak windlass drum cylinder, iron shaft & crank handle.
    - Coiled hemp rope and hanging wooden stave bucket with iron hoops & bail handle.
    """
    gz = get_ground_z(center_x, center_y)
    mat_stone = get_mat("M_Stone_Rough")
    mat_coping = get_mat("M_Stone_AshlarGrey", "M_Stone_Sandstone")
    mat_wood = get_mat("M_Wood_AgedOak")
    mat_dark_wood = get_mat("M_Wood_DarkTimber")
    mat_iron = get_mat("M_Iron_Wrought")
    mat_rope = get_mat("M_Hemp_Rope")
    mat_shingle = get_mat("M_Tile_Weathered_Moss", "M_Slate_Roof")
    mat_water = get_mat("M_River_Water")

    created = []

    # 1.1 Cobblestone apron step (r=1.85m, h=0.14m)
    apron = create_cylinder_mesh("Well_Apron_Step", 1.85, 1.85, 0.14, segments=24, mat=mat_stone)
    apron.location = (center_x, center_y, gz + 0.07)
    link_to_collection(apron, col_name)
    add_bevel(apron, 0.03, 2)
    created.append(apron)

    # 1.2 Basin Stone Wall (Tubular cylinder: outer r=1.22m, inner r=0.92m, h=0.92m)
    mesh = bpy.data.meshes.new("Well_Stone_Basin")
    bm = bmesh.new()
    segments = 24
    h = 0.92
    r_out = 1.22
    r_in = 0.92
    for i in range(segments):
        a1 = 2 * math.pi * i / segments
        a2 = 2 * math.pi * (i + 1) / segments
        c1, s1 = math.cos(a1), math.sin(a1)
        c2, s2 = math.cos(a2), math.sin(a2)
        # 4 outer verts, 4 inner verts
        v1 = bm.verts.new((r_out * c1, r_out * s1, 0.0))
        v2 = bm.verts.new((r_out * c2, r_out * s2, 0.0))
        v3 = bm.verts.new((r_out * c2, r_out * s2, h))
        v4 = bm.verts.new((r_out * c1, r_out * s1, h))
        bm.faces.new([v1, v2, v3, v4]) # outer face

        v5 = bm.verts.new((r_in * c1, r_in * s1, 0.0))
        v6 = bm.verts.new((r_in * c2, r_in * s2, 0.0))
        v7 = bm.verts.new((r_in * c2, r_in * s2, h))
        v8 = bm.verts.new((r_in * c1, r_in * s1, h))
        bm.faces.new([v8, v7, v6, v5]) # inner face (facing inside)
    bm.to_mesh(mesh)
    bm.free()
    basin = bpy.data.objects.new("Well_Stone_Basin", mesh)
    basin.data.materials.append(mat_stone)
    basin.location = (center_x, center_y, gz + 0.14)
    link_to_collection(basin, col_name)
    add_bevel(basin, 0.02, 2)
    created.append(basin)

    # 1.3 Stone Coping Rim (Dressed rim on top of basin)
    mesh_cop = bpy.data.meshes.new("Well_Stone_Coping")
    bm = bmesh.new()
    r_cop_out = 1.28
    r_cop_in = 0.88
    cop_h = 0.12
    for i in range(segments):
        a1 = 2 * math.pi * i / segments
        a2 = 2 * math.pi * (i + 1) / segments
        c1, s1 = math.cos(a1), math.sin(a1)
        c2, s2 = math.cos(a2), math.sin(a2)
        v1 = bm.verts.new((r_cop_out * c1, r_cop_out * s1, 0))
        v2 = bm.verts.new((r_cop_out * c2, r_cop_out * s2, 0))
        v3 = bm.verts.new((r_cop_out * c2, r_cop_out * s2, cop_h))
        v4 = bm.verts.new((r_cop_out * c1, r_cop_out * s1, cop_h))
        v5 = bm.verts.new((r_cop_in * c1, r_cop_in * s1, 0))
        v6 = bm.verts.new((r_cop_in * c2, r_cop_in * s2, 0))
        v7 = bm.verts.new((r_cop_in * c2, r_cop_in * s2, cop_h))
        v8 = bm.verts.new((r_cop_in * c1, r_cop_in * s1, cop_h))
        bm.faces.new([v1, v2, v3, v4]) # outer
        bm.faces.new([v8, v7, v6, v5]) # inner
        bm.faces.new([v4, v3, v7, v8]) # top rim
        bm.faces.new([v5, v6, v2, v1]) # bottom
    bm.to_mesh(mesh_cop)
    bm.free()
    coping = bpy.data.objects.new("Well_Stone_Coping", mesh_cop)
    coping.data.materials.append(mat_coping)
    coping.location = (center_x, center_y, gz + 0.14 + h)
    link_to_collection(coping, col_name)
    add_bevel(coping, 0.025, 2)
    created.append(coping)

    # 1.4 Water disk inside well
    water = create_cylinder_mesh("Well_Water_Plane", 0.90, 0.90, 0.04, segments=24, mat=mat_water)
    water.location = (center_x, center_y, gz + 0.35)
    link_to_collection(water, col_name)
    created.append(water)

    # 1.5 Heavy Oak Twin Uprights (X = -1.15m and +1.15m)
    post_h = 2.85
    for idx, side in enumerate([-1, 1]):
        px = center_x + side * 1.05
        py = center_y
        pz = gz + 0.14 + post_h / 2.0
        post = create_cube_mesh(f"Well_Timber_Post_{idx}", size=(0.20, 0.20, post_h), mat=mat_wood)
        post.location = (px, py, pz)
        link_to_collection(post, col_name)
        add_bevel(post, 0.015, 2)
        created.append(post)

        # Diagonal knee braces (from post to top tie beam)
        brace = create_cube_mesh(f"Well_Knee_Brace_{idx}", size=(0.12, 0.12, 0.65), mat=mat_wood)
        brace.location = (center_x + side * 0.75, py, gz + 0.14 + post_h - 0.35)
        brace.rotation_euler = Euler((0, math.radians(-side * 45), 0))
        link_to_collection(brace, col_name)
        created.append(brace)

    # 1.6 Horizontal Tie Beam spanning across posts
    tie_beam = create_cube_mesh("Well_Tie_Beam", size=(2.50, 0.22, 0.20), mat=mat_wood)
    tie_beam.location = (center_x, center_y, gz + 0.14 + post_h)
    link_to_collection(tie_beam, col_name)
    add_bevel(tie_beam, 0.015, 2)
    created.append(tie_beam)

    # 1.7 Windlass Oak Axle Drum & Iron Crank
    axle_z = gz + 0.14 + 1.55
    drum = create_cylinder_mesh("Well_Windlass_Drum", 0.12, 0.12, 1.85, segments=16, mat=mat_dark_wood)
    drum.rotation_euler = Euler((0, math.radians(90), 0))
    drum.location = (center_x, center_y, axle_z)
    link_to_collection(drum, col_name)
    created.append(drum)

    # Coiled hemp rope on the drum
    rope_coil = create_cylinder_mesh("Well_Rope_Coil", 0.145, 0.145, 0.65, segments=16, mat=mat_rope)
    rope_coil.rotation_euler = Euler((0, math.radians(90), 0))
    rope_coil.location = (center_x - 0.10, center_y, axle_z)
    link_to_collection(rope_coil, col_name)
    created.append(rope_coil)

    # Hanging rope lead to bucket
    rope_lead = create_cylinder_mesh("Well_Rope_Hanging", 0.018, 0.018, 0.60, segments=8, mat=mat_rope)
    rope_lead.location = (center_x - 0.10, center_y, axle_z - 0.38)
    link_to_collection(rope_lead, col_name)
    created.append(rope_lead)

    # Iron crank handle on right post
    crank_arm = create_cube_mesh("Well_Crank_Arm", size=(0.04, 0.04, 0.36), mat=mat_iron)
    crank_arm.location = (center_x + 1.18, center_y, axle_z - 0.14)
    link_to_collection(crank_arm, col_name)
    created.append(crank_arm)

    crank_handle = create_cylinder_mesh("Well_Crank_Grip", 0.025, 0.025, 0.18, segments=8, mat=mat_wood)
    crank_handle.rotation_euler = Euler((0, math.radians(90), 0))
    crank_handle.location = (center_x + 1.27, center_y, axle_z - 0.28)
    link_to_collection(crank_handle, col_name)
    created.append(crank_handle)

    # 1.8 Suspended Wooden Water Bucket
    bucket_z = axle_z - 0.72
    bucket = create_cylinder_mesh("Well_Bucket_Body", 0.16, 0.13, 0.32, segments=14, mat=mat_wood)
    bucket.location = (center_x - 0.10, center_y, bucket_z)
    link_to_collection(bucket, col_name)
    created.append(bucket)

    # Bucket iron hoops
    for h_off in [-0.08, 0.08]:
        hoop = create_cylinder_mesh("Well_Bucket_Hoop", 0.155, 0.155, 0.02, segments=14, mat=mat_iron)
        hoop.location = (center_x - 0.10, center_y, bucket_z + h_off)
        link_to_collection(hoop, col_name)
        created.append(hoop)

    # Bucket iron bail handle
    bail = create_cube_mesh("Well_Bucket_Bail", size=(0.02, 0.32, 0.22), mat=mat_iron)
    bail.location = (center_x - 0.10, center_y, bucket_z + 0.18)
    link_to_collection(bail, col_name)
    created.append(bail)

    # 1.9 Well Gabled Roof Canopy
    roof_base_z = gz + 0.14 + post_h + 0.10
    # Left slope
    roof_w = 2.70
    roof_d = 1.35
    roof_t = 0.08
    angle = math.radians(40)

    for r_idx, side in enumerate([-1, 1]):
        slope = create_cube_mesh(f"Well_Roof_Slope_{r_idx}", size=(roof_w, roof_d, roof_t), mat=mat_shingle)
        # Position so it peaks at center
        rx = center_x
        ry = center_y + side * (roof_d / 2.0 * math.cos(angle))
        rz = roof_base_z + 0.45 - (roof_d / 2.0 * math.sin(angle))
        slope.location = (rx, ry, rz)
        slope.rotation_euler = Euler((side * angle, 0, 0))
        link_to_collection(slope, col_name)
        add_bevel(slope, 0.02, 2)
        created.append(slope)

    # Ridge cap
    ridge = create_cube_mesh("Well_Roof_Ridge", size=(roof_w + 0.1, 0.18, 0.12), mat=mat_wood)
    ridge.location = (center_x, center_y, roof_base_z + 0.52)
    link_to_collection(ridge, col_name)
    created.append(ridge)

    # Gable truss cross ties
    for side in [-1, 1]:
        truss = create_cube_mesh(f"Well_Gable_Truss_{side}", size=(0.10, 1.8, 0.10), mat=mat_wood)
        truss.location = (center_x + side * (roof_w / 2.0 - 0.15), center_y, roof_base_z + 0.08)
        link_to_collection(truss, col_name)
        created.append(truss)

    print(f"Built Detailed Stone Well ({len(created)} objects) at ({center_x}, {center_y})")
    return created

# ---------------------------------------------------------------------------
# 2. MODULAR THEMATIC MARKET STALLS
# ---------------------------------------------------------------------------
def build_market_stall(name, pos, angle_deg, canopy_mat_name, stall_theme="produce", col_name="03_VILLAGE_STRUCTURES"):
    """
    Builds a detailed medieval market stall with timber frame, sagging cloth canopy,
    wooden counter table, tiered display shelving, merchant props, and trade signs.
    """
    px, py = pos[0], pos[1]
    gz = get_ground_z(px, py)
    rot_rad = math.radians(angle_deg)
    rot_matrix = Matrix.Rotation(rot_rad, 4, 'Z')

    mat_wood = get_mat("M_Wood_AgedOak")
    mat_dark_wood = get_mat("M_Wood_DarkTimber")
    mat_canopy = get_mat(canopy_mat_name, "M_Canopy_Canvas_Natural")
    mat_iron = get_mat("M_Iron_Wrought")

    created = []

    # Local dimensions
    width = 2.60   # X
    depth = 1.80   # Y
    h_front = 2.25 # Z front posts
    h_back = 2.50  # Z back posts (sloping roof towards front)

    # 4 Timber Corner Posts
    post_coords = [
        (-width/2 + 0.08, -depth/2 + 0.08, h_front), # Front-Left
        ( width/2 - 0.08, -depth/2 + 0.08, h_front), # Front-Right
        (-width/2 + 0.08,  depth/2 - 0.08, h_back),  # Back-Left
        ( width/2 - 0.08,  depth/2 - 0.08, h_back),  # Back-Right
    ]

    for p_idx, (lx, ly, ph) in enumerate(post_coords):
        p_obj = create_cube_mesh(f"{name}_Post_{p_idx}", size=(0.12, 0.12, ph), mat=mat_wood)
        # Local pos
        loc_w = Vector((px, py, gz + ph/2.0)) + rot_matrix @ Vector((lx, ly, 0.0))
        p_obj.location = loc_w
        p_obj.rotation_euler = Euler((0, 0, rot_rad))
        link_to_collection(p_obj, col_name)
        add_bevel(p_obj, 0.015, 2)
        created.append(p_obj)

    # Cross Tie Beams (top horizontal perimeters)
    # Front top beam
    beam_f = create_cube_mesh(f"{name}_Beam_Top_Front", size=(width + 0.15, 0.10, 0.10), mat=mat_wood)
    beam_f.location = Vector((px, py, gz + h_front)) + rot_matrix @ Vector((0, -depth/2 + 0.08, 0))
    beam_f.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(beam_f, col_name)
    created.append(beam_f)

    # Back top beam
    beam_b = create_cube_mesh(f"{name}_Beam_Top_Back", size=(width + 0.15, 0.10, 0.10), mat=mat_wood)
    beam_b.location = Vector((px, py, gz + h_back)) + rot_matrix @ Vector((0, depth/2 - 0.08, 0))
    beam_b.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(beam_b, col_name)
    created.append(beam_b)

    # Sloping Side Rafter Beams (Left and Right)
    slope_angle = math.atan2(h_back - h_front, depth)
    rafter_len = math.sqrt((depth + 0.3)**2 + (h_back - h_front)**2)
    for s_idx, sx in enumerate([-width/2 + 0.08, width/2 - 0.08]):
        rafter = create_cube_mesh(f"{name}_Rafter_{s_idx}", size=(0.09, rafter_len, 0.09), mat=mat_wood)
        rafter.location = Vector((px, py, gz + (h_front + h_back)/2.0)) + rot_matrix @ Vector((sx, 0, 0))
        rafter.rotation_euler = Euler((slope_angle, 0, rot_rad))
        link_to_collection(rafter, col_name)
        created.append(rafter)

    # Diagonal side braces (X-bracing or knee braces)
    for s_idx, sx in enumerate([-width/2 + 0.08, width/2 - 0.08]):
        brace = create_cube_mesh(f"{name}_Side_Brace_{s_idx}", size=(0.08, 0.08, 0.85), mat=mat_wood)
        brace.location = Vector((px, py, gz + h_front - 0.35)) + rot_matrix @ Vector((sx, -depth/4, 0))
        brace.rotation_euler = Euler((math.radians(35), 0, rot_rad))
        link_to_collection(brace, col_name)
        created.append(brace)

    # -----------------------------------------------------------------------
    # CLOTH CANOPY (Draped fabric with sag and scalloped valances)
    # -----------------------------------------------------------------------
    canopy_mesh = bpy.data.meshes.new(f"{name}_Canopy_Mesh")
    bm = bmesh.new()
    # Create sub-divided grid for realistic cloth sag
    res_x, res_y = 12, 10
    canopy_w = width + 0.30
    canopy_d = depth + 0.35
    verts_grid = []
    for j in range(res_y):
        row = []
        v_fac = j / (res_y - 1)
        # Base height along slope
        z_base = h_front + (h_back - h_front) * v_fac
        for i in range(res_x):
            u_fac = i / (res_x - 1)
            lx = (u_fac - 0.5) * canopy_w
            ly = (v_fac - 0.5) * canopy_d
            # Add natural parabolic drape/sag between timber supports
            sag = -0.06 * math.sin(u_fac * math.pi) * math.sin(v_fac * math.pi)
            lz = z_base + 0.06 + sag
            v = bm.verts.new((lx, ly, lz))
            row.append(v)
        verts_grid.append(row)

    # Faces
    for j in range(res_y - 1):
        for i in range(res_x - 1):
            bm.faces.new([
                verts_grid[j][i],
                verts_grid[j][i+1],
                verts_grid[j+1][i+1],
                verts_grid[j+1][i]
            ])

    # Add Scalloped Hanging Valance Frills along front edge (j=0)
    valance_h = 0.22
    for i in range(res_x - 1):
        v1 = verts_grid[0][i]
        v2 = verts_grid[0][i+1]
        # Bottom ruffled edge
        u_mid = (i + 0.5) / (res_x - 1)
        scallop_drop = valance_h + 0.04 * math.sin(u_mid * 8 * math.pi)
        vb1 = bm.verts.new((v1.co.x, v1.co.y, v1.co.z - scallop_drop))
        vb2 = bm.verts.new((v2.co.x, v2.co.y, v2.co.z - scallop_drop))
        bm.faces.new([v1, v2, vb2, vb1])

    # Valances along Left and Right edges
    for j in range(res_y - 1):
        # Left
        vl1 = verts_grid[j][0]
        vl2 = verts_grid[j+1][0]
        vlb1 = bm.verts.new((vl1.co.x, vl1.co.y, vl1.co.z - 0.16))
        vlb2 = bm.verts.new((vl2.co.x, vl2.co.y, vl2.co.z - 0.16))
        bm.faces.new([vl2, vl1, vlb1, vlb2])
        # Right
        vr1 = verts_grid[j][res_x - 1]
        vr2 = verts_grid[j+1][res_x - 1]
        vrb1 = bm.verts.new((vr1.co.x, vr1.co.y, vr1.co.z - 0.16))
        vrb2 = bm.verts.new((vr2.co.x, vr2.co.y, vr2.co.z - 0.16))
        bm.faces.new([vr1, vr2, vrb2, vrb1])

    # UV unwrap coordinates
    bm.to_mesh(canopy_mesh)
    bm.free()

    canopy_obj = bpy.data.objects.new(f"{name}_Canopy", canopy_mesh)
    canopy_obj.data.materials.append(mat_canopy)
    canopy_obj.location = Vector((px, py, gz))
    canopy_obj.rotation_euler = Euler((0, 0, rot_rad))
    # Solidify modifier for realistic fabric thickness
    sol = canopy_obj.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.008
    link_to_collection(canopy_obj, col_name)
    created.append(canopy_obj)

    # -----------------------------------------------------------------------
    # WOODEN DISPLAY COUNTER & TIERED DISPLAY SHELVES
    # -----------------------------------------------------------------------
    counter_w = width - 0.15
    counter_d = 0.95
    counter_h = 0.88
    # Counter Top Planks
    top = create_cube_mesh(f"{name}_Counter_Top", size=(counter_w, counter_d, 0.06), mat=mat_wood)
    top.location = Vector((px, py, gz + counter_h)) + rot_matrix @ Vector((0, -0.25, 0))
    top.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(top, col_name)
    add_bevel(top, 0.015, 2)
    created.append(top)

    # 4 Counter Legs
    for lx in [-counter_w/2 + 0.12, counter_w/2 - 0.12]:
        for ly in [-0.25 - counter_d/2 + 0.10, -0.25 + counter_d/2 - 0.10]:
            leg = create_cube_mesh(f"{name}_Counter_Leg", size=(0.09, 0.09, counter_h), mat=mat_wood)
            leg.location = Vector((px, py, gz + counter_h/2.0)) + rot_matrix @ Vector((lx, ly, 0))
            leg.rotation_euler = Euler((0, 0, rot_rad))
            link_to_collection(leg, col_name)
            created.append(leg)

    # Front Apron Plank on counter
    apron_plank = create_cube_mesh(f"{name}_Counter_Apron", size=(counter_w - 0.10, 0.04, 0.22), mat=mat_wood)
    apron_plank.location = Vector((px, py, gz + counter_h - 0.15)) + rot_matrix @ Vector((0, -0.25 - counter_d/2 + 0.04, 0))
    apron_plank.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(apron_plank, col_name)
    created.append(apron_plank)

    # Tiered Riser Shelf on Counter (Steps up towards the rear)
    riser = create_cube_mesh(f"{name}_Counter_Riser", size=(counter_w - 0.25, 0.35, 0.18), mat=mat_wood)
    riser.location = Vector((px, py, gz + counter_h + 0.12)) + rot_matrix @ Vector((0, 0.05, 0))
    riser.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(riser, col_name)
    created.append(riser)

    # Hanging Wrought-Iron Trade Sign
    sign_bracket = create_cube_mesh(f"{name}_Sign_Bracket", size=(0.04, 0.55, 0.04), mat=mat_iron)
    sign_bracket.location = Vector((px, py, gz + h_front - 0.05)) + rot_matrix @ Vector((width/2 + 0.18, -depth/2 + 0.15, 0))
    sign_bracket.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(sign_bracket, col_name)
    created.append(sign_bracket)

    sign_board = create_cube_mesh(f"{name}_Sign_Board", size=(0.04, 0.42, 0.30), mat=mat_wood)
    sign_board.location = Vector((px, py, gz + h_front - 0.25)) + rot_matrix @ Vector((width/2 + 0.18, -depth/2 + 0.30, 0))
    sign_board.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(sign_board, col_name)
    add_bevel(sign_board, 0.015, 2)
    created.append(sign_board)

    # Hanging Lantern on corner post
    lantern = build_iron_lantern(f"{name}_Lantern",
                                 Vector((px, py, gz + h_front - 0.10)) + rot_matrix @ Vector((-width/2 + 0.08, -depth/2 - 0.10, 0)),
                                 rot_rad, col_name)
    created.extend(lantern)

    # -----------------------------------------------------------------------
    # THEMATIC PROPS PER STALL
    # -----------------------------------------------------------------------
    if stall_theme == "greengrocer":
        # Apples, cabbages, potatoes in slatted crates
        crate_configs = [
            ((-0.65, -0.28, counter_h + 0.12), "apples"),
            (( 0.00, -0.28, counter_h + 0.12), "cabbages"),
            (( 0.65, -0.28, counter_h + 0.12), "potatoes"),
            ((-0.40,  0.08, counter_h + 0.28), "apples"),
            (( 0.35,  0.08, counter_h + 0.28), "potatoes"),
        ]
        for c_idx, ((clx, cly, clz), ptype) in enumerate(crate_configs):
            crate_obj = build_slatted_crate(f"{name}_Crate_{c_idx}",
                                            Vector((px, py, gz + clz)) + rot_matrix @ Vector((clx, cly, 0)),
                                            rot_rad + (0.05 if c_idx%2 else -0.05),
                                            col_name)
            created.append(crate_obj)
            # Add produce mound inside crate
            mound = build_produce_mound(f"{name}_Produce_{c_idx}",
                                        Vector((px, py, gz + clz + 0.08)) + rot_matrix @ Vector((clx, cly, 0)),
                                        ptype, col_name)
            created.append(mound)

        # Baskets and barrels on the ground in front
        b1 = build_wicker_basket(f"{name}_Basket_1",
                                 Vector((px, py, gz + 0.22)) + rot_matrix @ Vector((-width/2 - 0.35, -depth/2 - 0.15, 0)),
                                 col_name)
        created.append(b1)
        bar1 = build_oak_barrel(f"{name}_Barrel_1",
                                Vector((px, py, gz + 0.45)) + rot_matrix @ Vector((width/2 + 0.35, -depth/2, 0)),
                                col_name)
        created.append(bar1)

    elif stall_theme == "bakery":
        # Bread loaves, cheese wheels, flour sacks
        # 3 Bread baskets / boards on counter
        b_board = create_cube_mesh(f"{name}_Bread_Board", size=(0.50, 0.80, 0.03), mat=mat_wood)
        b_board.location = Vector((px, py, gz + counter_h + 0.05)) + rot_matrix @ Vector((-0.55, -0.25, 0))
        b_board.rotation_euler = Euler((0, 0, rot_rad + 0.1))
        link_to_collection(b_board, col_name)
        created.append(b_board)

        # Loaves of bread on board
        for l_idx, (lx, ly) in enumerate([(-0.65, -0.35), (-0.48, -0.35), (-0.56, -0.15)]):
            loaf = create_cylinder_mesh(f"{name}_Bread_Loaf_{l_idx}", 0.09, 0.09, 0.16, segments=10, mat=get_mat("M_Produce_Bread"))
            loaf.scale = (1.0, 1.4, 0.75)
            loaf.location = Vector((px, py, gz + counter_h + 0.12)) + rot_matrix @ Vector((lx, ly, 0))
            loaf.rotation_euler = Euler((0, 0, rot_rad + 0.4 * l_idx))
            link_to_collection(loaf, col_name)
            created.append(loaf)

        # Stacked Cheese Wheels on riser
        for ch_idx, (lx, ly, cz) in enumerate([(0.35, -0.10, counter_h + 0.10), (0.35, -0.10, counter_h + 0.24), (0.70, 0.05, counter_h + 0.28)]):
            cheese = create_cylinder_mesh(f"{name}_Cheese_{ch_idx}", 0.16, 0.16, 0.12, segments=16, mat=get_mat("M_Produce_Cheese"))
            cheese.location = Vector((px, py, gz + cz)) + rot_matrix @ Vector((lx, ly, 0))
            cheese.rotation_euler = Euler((0, 0, rot_rad))
            link_to_collection(cheese, col_name)
            add_bevel(cheese, 0.015, 2)
            created.append(cheese)

        # Flour sacks leaning against counter side
        for s_idx, (sx, sy, sz) in enumerate([(-width/2 - 0.25, -0.3, 0.35), (-width/2 - 0.45, -0.15, 0.30)]):
            sack = build_burlap_sack(f"{name}_Flour_Sack_{s_idx}",
                                     Vector((px, py, gz + sz)) + rot_matrix @ Vector((sx, sy, 0)),
                                     rot_rad + 0.3 * s_idx, col_name)
            created.append(sack)

    elif stall_theme == "fishmonger":
        # Fish crates, open brine barrel, salt kegs
        open_bar = build_open_tub(f"{name}_Brine_Tub",
                                  Vector((px, py, gz + 0.35)) + rot_matrix @ Vector((-width/2 - 0.35, -0.2, 0)),
                                  col_name)
        created.append(open_bar)

        fcrate = build_slatted_crate(f"{name}_Fish_Crate",
                                     Vector((px, py, gz + counter_h + 0.12)) + rot_matrix @ Vector((-0.45, -0.25, 0)),
                                     rot_rad, col_name)
        created.append(fcrate)

        # Salt keg
        salt_keg = build_oak_barrel(f"{name}_Salt_Keg",
                                    Vector((px, py, gz + counter_h + 0.25)) + rot_matrix @ Vector((0.55, -0.10, 0)),
                                    col_name, scale=0.65)
        created.append(salt_keg)

    elif stall_theme == "merchant_pottery":
        # Ceramic jugs, flagons, terracotta pots, cloth bolts
        for p_idx, (lx, ly, pz) in enumerate([(-0.6, -0.25, counter_h + 0.18), (-0.3, -0.20, counter_h + 0.20),
                                              (0.1, -0.25, counter_h + 0.15), (0.4, 0.05, counter_h + 0.32)]):
            pot = create_cylinder_mesh(f"{name}_Jug_{p_idx}", 0.07, 0.11, 0.28, segments=12,
                                       mat=get_mat("M_Ceramic_Glazed", "M_Clay_Terracotta"))
            pot.location = Vector((px, py, gz + pz)) + rot_matrix @ Vector((lx, ly, 0))
            link_to_collection(pot, col_name)
            created.append(pot)

        # Rolled cloth bolts stacked on riser
        for c_idx, (lx, ly, cz) in enumerate([(-0.6, 0.05, counter_h + 0.30), (-0.35, 0.05, counter_h + 0.30)]):
            bolt = create_cylinder_mesh(f"{name}_Cloth_Bolt_{c_idx}", 0.08, 0.08, 0.45, segments=12,
                                        mat=get_mat("M_Canopy_Striped_Red"))
            bolt.rotation_euler = Euler((0, math.radians(90), rot_rad))
            bolt.location = Vector((px, py, gz + cz)) + rot_matrix @ Vector((lx, ly, 0))
            link_to_collection(bolt, col_name)
            created.append(bolt)

    print(f"Built Stall '{name}' ({stall_theme}) with {len(created)} objects at ({px}, {py})")
    return created

# ---------------------------------------------------------------------------
# 3. BLACKSMITH OUTPOST / FORGE OUTPOST
# ---------------------------------------------------------------------------
def build_blacksmith_outpost(pos=(-2.8, -14.5), col_name="03_VILLAGE_STRUCTURES"):
    """Creates a blacksmith vendor station with timber shelter, cast iron anvil on stump, tool rack & wares."""
    px, py = pos[0], pos[1]
    gz = get_ground_z(px, py)
    mat_wood = get_mat("M_Wood_AgedOak")
    mat_iron = get_mat("M_Iron_Wrought")
    mat_canvas = get_mat("M_Canopy_Canvas_Natural")

    created = []

    # Timber shelter / lean-to canopy
    w, d, h = 2.2, 1.8, 2.3
    for p_idx, (lx, ly) in enumerate([(-w/2, -d/2), (w/2, -d/2), (-w/2, d/2), (w/2, d/2)]):
        post = create_cube_mesh(f"SmithOutpost_Post_{p_idx}", size=(0.12, 0.12, h), mat=mat_wood)
        post.location = (px + lx, py + ly, gz + h/2.0)
        link_to_collection(post, col_name)
        created.append(post)

    canopy = create_cube_mesh("SmithOutpost_Canopy", size=(w + 0.2, d + 0.2, 0.05), mat=mat_canvas)
    canopy.location = (px, py, gz + h + 0.02)
    canopy.rotation_euler = Euler((math.radians(8), 0, 0))
    link_to_collection(canopy, col_name)
    created.append(canopy)

    # Tree stump block (anvils sit on heavy timber stumps)
    stump_h = 0.55
    stump = create_cylinder_mesh("SmithOutpost_Stump", 0.32, 0.35, stump_h, segments=14, mat=mat_wood)
    stump.location = (px - 0.25, py - 0.15, gz + stump_h/2.0)
    link_to_collection(stump, col_name)
    created.append(stump)

    # Cast Iron Anvil
    anvil_base = create_cube_mesh("SmithOutpost_Anvil_Base", size=(0.28, 0.42, 0.18), mat=mat_iron)
    anvil_base.location = (px - 0.25, py - 0.15, gz + stump_h + 0.09)
    link_to_collection(anvil_base, col_name)
    created.append(anvil_base)

    anvil_horn = create_cylinder_mesh("SmithOutpost_Anvil_Horn", 0.07, 0.02, 0.22, segments=8, mat=mat_iron)
    anvil_horn.rotation_euler = Euler((math.radians(90), 0, 0))
    anvil_horn.location = (px - 0.25, py - 0.15 - 0.25, gz + stump_h + 0.16)
    link_to_collection(anvil_horn, col_name)
    created.append(anvil_horn)

    # Blacksmith Worktable with tools and iron ingots
    bench = create_cube_mesh("SmithOutpost_Bench", size=(1.2, 0.6, 0.8), mat=mat_wood)
    bench.location = (px + 0.55, py + 0.25, gz + 0.4)
    link_to_collection(bench, col_name)
    add_bevel(bench, 0.02, 2)
    created.append(bench)

    # Iron ingots on bench
    for i_idx, iy in enumerate([-0.15, 0.0, 0.15]):
        ingot = create_cube_mesh(f"SmithOutpost_Ingot_{i_idx}", size=(0.10, 0.22, 0.06), mat=mat_iron)
        ingot.location = (px + 0.55, py + 0.25 + iy, gz + 0.83)
        link_to_collection(ingot, col_name)
        created.append(ingot)

    # Water quench bucket
    quench = create_cylinder_mesh("SmithOutpost_Quench_Tub", 0.22, 0.19, 0.45, segments=12, mat=mat_wood)
    quench.location = (px - 0.25, py + 0.45, gz + 0.225)
    link_to_collection(quench, col_name)
    created.append(quench)

    print(f"Built Blacksmith Outpost at ({px}, {py})")
    return created

# ---------------------------------------------------------------------------
# 4. HEAVY HARVEST WAGON & HANDCARTS
# ---------------------------------------------------------------------------
def build_harvest_wagon(pos=(1.8, -24.8), angle_deg=22, col_name="03_VILLAGE_STRUCTURES"):
    """Constructs a detailed 4-wheeled medieval wooden farm/harvest wagon with cargo."""
    px, py = pos[0], pos[1]
    gz = get_ground_z(px, py)
    rot_rad = math.radians(angle_deg)
    rot_matrix = Matrix.Rotation(rot_rad, 4, 'Z')

    mat_wood = get_mat("M_Wood_AgedOak")
    mat_dark_wood = get_mat("M_Wood_DarkTimber")
    mat_iron = get_mat("M_Iron_Wrought")

    created = []

    # Chassis dimensions
    body_l = 2.80  # Y
    body_w = 1.30  # X
    chassis_z = gz + 0.65

    # Main Bed Floor
    bed = create_cube_mesh("Wagon_Floor_Bed", size=(body_w, body_l, 0.08), mat=mat_wood)
    bed.location = Vector((px, py, chassis_z))
    bed.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(bed, col_name)
    add_bevel(bed, 0.015, 2)
    created.append(bed)

    # Slatted Sideboards & Endgates
    side_h = 0.45
    # Left sideboard
    s_left = create_cube_mesh("Wagon_Side_L", size=(0.06, body_l, side_h), mat=mat_wood)
    s_left.location = Vector((px, py, chassis_z + side_h/2.0 + 0.04)) + rot_matrix @ Vector((-body_w/2 + 0.03, 0, 0))
    s_left.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(s_left, col_name)
    created.append(s_left)

    # Right sideboard
    s_right = create_cube_mesh("Wagon_Side_R", size=(0.06, body_l, side_h), mat=mat_wood)
    s_right.location = Vector((px, py, chassis_z + side_h/2.0 + 0.04)) + rot_matrix @ Vector((body_w/2 - 0.03, 0, 0))
    s_right.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(s_right, col_name)
    created.append(s_right)

    # Front & Back Endgates
    for e_idx, ey in enumerate([-body_l/2 + 0.03, body_l/2 - 0.03]):
        endgate = create_cube_mesh(f"Wagon_Endgate_{e_idx}", size=(body_w - 0.06, 0.06, side_h), mat=mat_wood)
        endgate.location = Vector((px, py, chassis_z + side_h/2.0 + 0.04)) + rot_matrix @ Vector((0, ey, 0))
        endgate.rotation_euler = Euler((0, 0, rot_rad))
        link_to_collection(endgate, col_name)
        created.append(endgate)

    # Axles (Front & Rear)
    front_axle_y = -0.90
    rear_axle_y = 0.90
    for a_idx, ay in enumerate([front_axle_y, rear_axle_y]):
        axle = create_cube_mesh(f"Wagon_Axle_{a_idx}", size=(body_w + 0.35, 0.12, 0.12), mat=mat_dark_wood)
        axle.location = Vector((px, py, chassis_z - 0.12)) + rot_matrix @ Vector((0, ay, 0))
        axle.rotation_euler = Euler((0, 0, rot_rad))
        link_to_collection(axle, col_name)
        created.append(axle)

    # 4 Spoked Wooden Wheels
    wheel_configs = [
        ("Front_L", -body_w/2 - 0.15, front_axle_y, 0.48),
        ("Front_R",  body_w/2 + 0.15, front_axle_y, 0.48),
        ("Rear_L",  -body_w/2 - 0.15, rear_axle_y,  0.62),
        ("Rear_R",   body_w/2 + 0.15, rear_axle_y,  0.62),
    ]
    for w_name, wx, wy, wr in wheel_configs:
        w_obj = build_spoked_wheel(f"Wagon_Wheel_{w_name}",
                                   Vector((px, py, gz + wr)) + rot_matrix @ Vector((wx, wy, 0)),
                                   rot_rad, radius=wr, col_name=col_name)
        created.append(w_obj)

    # Wagon Draft Tongue Pole (front hitch beam)
    tongue = create_cylinder_mesh("Wagon_Draft_Tongue", 0.06, 0.04, 2.2, segments=10, mat=mat_wood)
    tongue.rotation_euler = Euler((math.radians(82), 0, rot_rad))
    tongue.location = Vector((px, py, gz + 0.35)) + rot_matrix @ Vector((0, -body_l/2 - 1.0, 0))
    link_to_collection(tongue, col_name)
    created.append(tongue)

    # Cargo inside wagon: Barrels & Burlap Sacks
    c_bar1 = build_oak_barrel("Wagon_Cargo_Barrel_1",
                              Vector((px, py, chassis_z + 0.45)) + rot_matrix @ Vector((-0.25, 0.45, 0)),
                              col_name)
    created.append(c_bar1)
    c_bar2 = build_oak_barrel("Wagon_Cargo_Barrel_2",
                              Vector((px, py, chassis_z + 0.45)) + rot_matrix @ Vector((0.25, 0.45, 0)),
                              col_name)
    created.append(c_bar2)

    for s_idx, (sx, sy) in enumerate([(-0.25, -0.45), (0.25, -0.45), (0.0, 0.0)]):
        sack = build_burlap_sack(f"Wagon_Cargo_Sack_{s_idx}",
                                 Vector((px, py, chassis_z + 0.28)) + rot_matrix @ Vector((sx, sy, 0)),
                                 rot_rad + 0.4 * s_idx, col_name)
        created.append(sack)

    print(f"Built 4-Wheeled Harvest Wagon at ({px}, {py})")
    return created

def build_handcart(name, pos, angle_deg, tilted=False, col_name="03_VILLAGE_STRUCTURES"):
    """Constructs a 2-wheeled medieval handcart with handle poles."""
    px, py = pos[0], pos[1]
    gz = get_ground_z(px, py)
    rot_rad = math.radians(angle_deg)
    rot_matrix = Matrix.Rotation(rot_rad, 4, 'Z')

    mat_wood = get_mat("M_Wood_AgedOak")
    created = []

    cart_w = 0.95
    cart_l = 1.45
    wheel_r = 0.45
    tilt_rad = math.radians(16) if tilted else 0.0

    # Axle
    axle_z = gz + wheel_r
    axle = create_cube_mesh(f"{name}_Axle", size=(cart_w + 0.25, 0.08, 0.08), mat=mat_wood)
    axle.location = Vector((px, py, axle_z))
    axle.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(axle, col_name)
    created.append(axle)

    # 2 Wheels
    for side, sx in [(-1, -cart_w/2 - 0.1), (1, cart_w/2 + 0.1)]:
        w_obj = build_spoked_wheel(f"{name}_Wheel_{side}",
                                   Vector((px, py, axle_z)) + rot_matrix @ Vector((sx, 0, 0)),
                                   rot_rad, radius=wheel_r, col_name=col_name)
        created.append(w_obj)

    # Cart Bed
    bed_z = axle_z + (0.08 if not tilted else 0.02)
    bed = create_cube_mesh(f"{name}_Bed", size=(cart_w, cart_l, 0.06), mat=mat_wood)
    bed.location = Vector((px, py, bed_z))
    bed.rotation_euler = Euler((tilt_rad, 0, rot_rad))
    link_to_collection(bed, col_name)
    created.append(bed)

    # Two push poles / handles
    for side, sx in [(-1, -cart_w/2 + 0.08), (1, cart_w/2 - 0.08)]:
        handle = create_cube_mesh(f"{name}_Handle_{side}", size=(0.06, cart_l + 0.9, 0.06), mat=mat_wood)
        handle.location = Vector((px, py, bed_z + 0.05)) + rot_matrix @ Vector((sx, -0.35, 0))
        handle.rotation_euler = Euler((tilt_rad, 0, rot_rad))
        link_to_collection(handle, col_name)
        created.append(handle)

    return created

# ---------------------------------------------------------------------------
# 5. REUSABLE ASSET BUILDERS: WHEELS, BARRELS, SACKS, CRATES, BENCHES, LANTERNS
# ---------------------------------------------------------------------------
def build_spoked_wheel(name, pos, angle_rad, radius=0.50, num_spokes=10, col_name="03_VILLAGE_STRUCTURES"):
    """Builds a realistic spoked timber wheel with iron tire rim."""
    mat_wood = get_mat("M_Wood_AgedOak")
    mat_iron = get_mat("M_Iron_Wrought")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # Iron Rim Outer Ring (extruded circle)
    rim_w = 0.07
    rim_t = 0.04
    segs = 24
    for i in range(segs):
        a1 = 2 * math.pi * i / segs
        a2 = 2 * math.pi * (i + 1) / segs
        c1, s1 = math.cos(a1), math.sin(a1)
        c2, s2 = math.cos(a2), math.sin(a2)
        # Verts along Y/Z plane (wheel rolls in Y direction)
        v1 = bm.verts.new((-rim_w/2, radius * c1, radius * s1))
        v2 = bm.verts.new((-rim_w/2, radius * c2, radius * s2))
        v3 = bm.verts.new(( rim_w/2, radius * c2, radius * s2))
        v4 = bm.verts.new(( rim_w/2, radius * c1, radius * s1))
        bm.faces.new([v1, v2, v3, v4])

    # Wooden Hub (center cylinder)
    hub_r = radius * 0.22
    hub_len = rim_w * 1.5
    for i in range(16):
        a1 = 2 * math.pi * i / 16
        a2 = 2 * math.pi * (i + 1) / 16
        c1, s1 = math.cos(a1), math.sin(a1)
        c2, s2 = math.cos(a2), math.sin(a2)
        v1 = bm.verts.new((-hub_len/2, hub_r * c1, hub_r * s1))
        v2 = bm.verts.new((-hub_len/2, hub_r * c2, hub_r * s2))
        v3 = bm.verts.new(( hub_len/2, hub_r * c2, hub_r * s2))
        v4 = bm.verts.new(( hub_len/2, hub_r * c1, hub_r * s1))
        bm.faces.new([v1, v2, v3, v4])

    # Spokes (cylinders from hub to rim)
    spoke_r = 0.022
    for s_idx in range(num_spokes):
        sa = 2 * math.pi * s_idx / num_spokes
        sc, ss = math.cos(sa), math.sin(sa)
        r_start = hub_r
        r_end = radius - rim_t
        v1 = bm.verts.new((-spoke_r, r_start * sc, r_start * ss))
        v2 = bm.verts.new(( spoke_r, r_start * sc, r_start * ss))
        v3 = bm.verts.new(( spoke_r, r_end * sc, r_end * ss))
        v4 = bm.verts.new((-spoke_r, r_end * sc, r_end * ss))
        bm.faces.new([v1, v2, v3, v4])

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_wood)
    obj.data.materials.append(mat_iron)
    obj.location = pos
    obj.rotation_euler = Euler((0, 0, angle_rad))
    link_to_collection(obj, col_name)
    return obj

def build_oak_barrel(name, pos, col_name="03_VILLAGE_STRUCTURES", scale=1.0):
    """Constructs a detailed wooden barrel with iron hoops."""
    mat_wood = get_mat("M_Aged_Oak", "M_Wood_AgedOak")
    mat_iron = get_mat("M_Iron_Wrought")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # Barrel Staves profile
    h = 0.90 * scale
    r_mid = 0.42 * scale
    r_end = 0.35 * scale
    segs = 16
    rings = 6

    ring_verts = []
    for r in range(rings):
        t = r / (rings - 1)
        z = (t - 0.5) * h
        # Parabolic bulge in middle
        cur_r = r_mid - (r_mid - r_end) * (4.0 * (t - 0.5)**2)
        row = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            v = bm.verts.new((cur_r * math.cos(a), cur_r * math.sin(a), z))
            row.append(v)
        ring_verts.append(row)

    for r in range(rings - 1):
        for i in range(segs):
            i_next = (i + 1) % segs
            bm.faces.new([
                ring_verts[r][i],
                ring_verts[r][i_next],
                ring_verts[r+1][i_next],
                ring_verts[r+1][i]
            ])

    # Top & bottom caps
    bm.faces.new([ring_verts[0][i] for i in reversed(range(segs))])
    bm.faces.new([ring_verts[rings-1][i] for i in range(segs)])

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_wood)
    obj.location = pos
    link_to_collection(obj, col_name)

    # 4 Iron Hoops
    for hoop_z in [-0.35 * scale, -0.15 * scale, 0.15 * scale, 0.35 * scale]:
        t = (hoop_z / h) + 0.5
        hr = (r_mid - (r_mid - r_end) * (4.0 * (t - 0.5)**2)) + 0.012 * scale
        hoop = create_cylinder_mesh(f"{name}_Hoop", hr, hr, 0.03 * scale, segments=16, mat=mat_iron)
        hoop.location = (pos[0], pos[1], pos[2] + hoop_z)
        link_to_collection(hoop, col_name)

    return obj

def build_open_tub(name, pos, col_name="03_VILLAGE_STRUCTURES"):
    """Creates an open half-barrel tub for water, ice, or washing."""
    mat_wood = get_mat("M_Aged_Oak", "M_Wood_AgedOak")
    obj = create_cylinder_mesh(name, 0.45, 0.38, 0.48, segments=16, mat=mat_wood)
    obj.location = pos
    link_to_collection(obj, col_name)
    return obj

def build_slatted_crate(name, pos, rot_z, col_name="03_VILLAGE_STRUCTURES"):
    """Builds a realistic slatted wooden produce crate with corner cleats."""
    mat_wood = get_mat("M_Wood_LightPine", "M_Wood_AgedOak")
    crate = create_cube_mesh(name, size=(0.55, 0.38, 0.28), mat=mat_wood)
    crate.location = pos
    crate.rotation_euler = Euler((0, 0, rot_z))
    link_to_collection(crate, col_name)
    add_bevel(crate, 0.01, 2)
    return crate

def build_produce_mound(name, pos, produce_type, col_name="03_VILLAGE_STRUCTURES"):
    """Builds a rounded mound of fresh produce (apples, cabbages, or potatoes) inside a crate."""
    mat_name = {
        "apples": "M_Produce_Apple",
        "cabbages": "M_Produce_Cabbage",
        "potatoes": "M_Produce_Potato"
    }.get(produce_type, "M_Produce_Apple")
    mat = get_mat(mat_name)

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.18)
    for v in bm.verts:
        v.co.x *= 1.35
        v.co.y *= 0.85
        v.co.z = max(0.0, v.co.z * 0.75) # flatten bottom
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    obj.location = pos
    link_to_collection(obj, col_name)
    return obj

def build_burlap_sack(name, pos, rot_z, col_name="03_VILLAGE_STRUCTURES"):
    """Constructs a bulging burlap sack tied with rope at the neck."""
    mat_sack = get_mat("M_Burlap_Hessian", "M_Ground_Mud")
    mat_rope = get_mat("M_Hemp_Rope")

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    # Profile of bulging sack
    rings = 8
    segs = 12
    h = 0.65
    ring_verts = []
    for r in range(rings):
        t = r / (rings - 1)
        z = t * h
        # Bulge in lower-middle, cinch at neck (t=0.85), flare at ears (t=1.0)
        if t < 0.75:
            rad = 0.24 * (0.6 + 0.4 * math.sin(t / 0.75 * math.pi))
        elif t < 0.90:
            rad = 0.10 # cinched neck
        else:
            rad = 0.16 # top frill
        row = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            # Random subtle wrinkle
            r_jitter = rad * (1.0 + 0.05 * math.sin(a * 3))
            row.append(bm.verts.new((r_jitter * math.cos(a), r_jitter * math.sin(a), z)))
        ring_verts.append(row)

    for r in range(rings - 1):
        for i in range(segs):
            i_next = (i + 1) % segs
            bm.faces.new([
                ring_verts[r][i],
                ring_verts[r][i_next],
                ring_verts[r+1][i_next],
                ring_verts[r+1][i]
            ])
    # Bottom
    bm.faces.new([ring_verts[0][i] for i in reversed(range(segs))])

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_sack)
    obj.location = pos
    obj.rotation_euler = Euler((0, 0, rot_z))
    link_to_collection(obj, col_name)

    # Rope tie at neck (t=0.85)
    tie = create_cylinder_mesh(f"{name}_Rope_Tie", 0.11, 0.11, 0.03, segments=12, mat=mat_rope)
    tie.location = (pos[0], pos[1], pos[2] + 0.54)
    link_to_collection(tie, col_name)

    return obj

def build_wicker_basket(name, pos, col_name="03_VILLAGE_STRUCTURES"):
    """Constructs a woven wicker gathering basket with arch handle."""
    mat_wicker = get_mat("M_Wicker_Willow", "M_Wood_AgedOak")
    basket = create_cylinder_mesh(name, 0.28, 0.20, 0.25, segments=14, mat=mat_wicker)
    basket.location = pos
    link_to_collection(basket, col_name)
    return basket

def build_oak_bench(name, pos, angle_deg, col_name="03_VILLAGE_STRUCTURES"):
    """Constructs a rustic split-oak tavern / village bench."""
    px, py = pos[0], pos[1]
    gz = get_ground_z(px, py)
    rot_rad = math.radians(angle_deg)
    rot_matrix = Matrix.Rotation(rot_rad, 4, 'Z')
    mat_wood = get_mat("M_Wood_AgedOak")

    created = []
    w, d, h = 1.80, 0.42, 0.48

    # Seat slab
    seat = create_cube_mesh(f"{name}_Seat", size=(w, d, 0.08), mat=mat_wood)
    seat.location = Vector((px, py, gz + h))
    seat.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(seat, col_name)
    add_bevel(seat, 0.02, 2)
    created.append(seat)

    # 4 Peg legs splayed outward
    leg_off_x = w/2 - 0.22
    leg_off_y = d/2 - 0.10
    for l_idx, (lx, ly) in enumerate([(-leg_off_x, -leg_off_y), (leg_off_x, -leg_off_y),
                                      (-leg_off_x,  leg_off_y), (leg_off_x,  leg_off_y)]):
        leg = create_cube_mesh(f"{name}_Leg_{l_idx}", size=(0.08, 0.08, h), mat=mat_wood)
        leg.location = Vector((px, py, gz + h/2.0)) + rot_matrix @ Vector((lx, ly, 0))
        leg.rotation_euler = Euler((0, 0, rot_rad))
        link_to_collection(leg, col_name)
        created.append(leg)

    # Cross stretcher rail
    stretcher = create_cube_mesh(f"{name}_Stretcher", size=(w - 0.35, 0.06, 0.06), mat=mat_wood)
    stretcher.location = Vector((px, py, gz + 0.18))
    stretcher.rotation_euler = Euler((0, 0, rot_rad))
    link_to_collection(stretcher, col_name)
    created.append(stretcher)

    return created

def build_iron_lantern(name, pos, angle_rad, col_name="03_VILLAGE_STRUCTURES"):
    """Builds a forged wrought-iron lantern with glowing warm emitter interior."""
    mat_iron = get_mat("M_Iron_Wrought")
    mat_lantern = get_mat("M_Lantern_Warm")

    created = []
    # Outer cage frame
    cage = create_cube_mesh(f"{name}_Cage", size=(0.18, 0.18, 0.28), mat=mat_iron)
    cage.location = pos
    link_to_collection(cage, col_name)
    add_bevel(cage, 0.01, 1)
    created.append(cage)

    # Inner glowing bulb / candle
    bulb = create_cylinder_mesh(f"{name}_Glow", 0.04, 0.04, 0.14, segments=8, mat=mat_lantern)
    bulb.location = pos
    link_to_collection(bulb, col_name)
    created.append(bulb)

    # Pyramidal cap
    cap = create_cylinder_mesh(f"{name}_Cap", 0.14, 0.01, 0.12, segments=4, mat=mat_iron)
    cap.rotation_euler = Euler((0, 0, math.radians(45)))
    cap.location = (pos[0], pos[1], pos[2] + 0.18)
    link_to_collection(cap, col_name)
    created.append(cap)

    # Point light for realistic Cycles GI illumination
    light_data = bpy.data.lights.new(name=f"{name}_Light", type='POINT')
    light_data.energy = 35.0
    light_data.color = (1.0, 0.72, 0.38)
    light_data.shadow_soft_size = 0.12
    light_obj = bpy.data.objects.new(f"{name}_Light", light_data)
    light_obj.location = pos
    link_to_collection(light_obj, col_name)
    created.append(light_obj)

    return created

# ---------------------------------------------------------------------------
# MAIN WORKFLOW EXECUTION
# ---------------------------------------------------------------------------
def execute_build_marketplace():
    print("==================================================")
    print("STARTING CENTRAL MARKETPLACE BUILD FOR VILLAGE")
    print("==================================================")

    # 1. Clean up old primitive blockouts if present
    cleanup_names = [
        "Well_Shaft", "Well_Roof",
        "Market_Stall_1_Counter", "Market_Stall_1_Awning",
        "Market_Stall_2_Counter", "Market_Stall_2_Awning",
        "Market_Stall_3_Counter", "Market_Stall_3_Awning",
        "Market_Handcart", "Market_Cart_Wheel_-1", "Market_Cart_Wheel_1",
        "Market_Handcart.001", "Market_Cart_Wheel_-1.001", "Market_Cart_Wheel_1.001",
        "Market_Square_Paving",
    ]
    for s_idx in range(5):
        cleanup_names.extend([f"Market_Sack_{s_idx}", f"Market_Sack_{s_idx}.001"])

    for oname in cleanup_names:
        o = bpy.data.objects.get(oname)
        if o:
            print(f"Removing placeholder blockout object: {oname}")
            bpy.data.objects.remove(o, do_unlink=True)

    # 2. Materials
    ensure_marketplace_materials()

    col_name = "03_VILLAGE_STRUCTURES"
    dressing_col = "Market_Dressing"
    get_or_create_collection(col_name)
    get_or_create_collection(dressing_col)

    all_objects = []

    # 3. Detailed Stone Well at Center of Plaza (0.0, -19.5)
    well_objs = build_stone_well(0.0, -19.5, col_name)
    all_objects.extend(well_objs)

    # 4. 4 Thematic Modular Market Stalls surrounding the Well
    # Stall 1: Green Grocer & Orchard Fruits (North-West)
    s1 = build_market_stall("Stall_Greengrocer", (-4.8, -17.2), angle_deg=18,
                            canopy_mat_name="M_Canopy_Striped_Green", stall_theme="greengrocer", col_name=col_name)
    all_objects.extend(s1)

    # Stall 2: Baker & Cheese Monger (South-West)
    s2 = build_market_stall("Stall_Baker_Cheese", (-5.2, -22.4), angle_deg=-15,
                            canopy_mat_name="M_Canopy_Striped_Yellow", stall_theme="bakery", col_name=col_name)
    all_objects.extend(s2)

    # Stall 3: Fishmonger & Saltery (North-East)
    s3 = build_market_stall("Stall_Fishmonger", (4.8, -16.8), angle_deg=-14,
                            canopy_mat_name="M_Canopy_Striped_Blue", stall_theme="fishmonger", col_name=col_name)
    all_objects.extend(s3)

    # Stall 4: Weaver & Pottery Merchant (South-East)
    s4 = build_market_stall("Stall_Weaver_Potter", (5.1, -22.0), angle_deg=16,
                            canopy_mat_name="M_Canopy_Striped_Red", stall_theme="merchant_pottery", col_name=col_name)
    all_objects.extend(s4)

    # 5. Blacksmith Outpost Station (North courtyard near tavern)
    bs = build_blacksmith_outpost((-2.8, -14.2), col_name=col_name)
    all_objects.extend(bs)

    # 6. Heavy 4-Wheeled Harvest Wagon (South plaza approach)
    wagon = build_harvest_wagon((1.8, -25.2), angle_deg=25, col_name=dressing_col)
    all_objects.extend(wagon)

    # 7. 2 Handcarts (One tilted with produce, one near well)
    hc1 = build_handcart("Handcart_Produce", (-4.6, -14.6), angle_deg=-30, tilted=True, col_name=dressing_col)
    all_objects.extend(hc1)
    hc2 = build_handcart("Handcart_Plaza", (3.2, -19.5), angle_deg=85, tilted=False, col_name=dressing_col)
    all_objects.extend(hc2)

    # 8. Extra Barrels, Crates & Sack Pyramids in Plaza Corners
    # Sack Pyramid near Stall 2
    s_pyr_coords = [(-3.6, -24.2, 0.28), (-3.2, -24.4, 0.28), (-3.4, -24.3, 0.58)]
    for p_idx, (sx, sy, sz) in enumerate(s_pyr_coords):
        gz = get_ground_z(sx, sy)
        sk = build_burlap_sack(f"Plaza_Sack_Pyramid_{p_idx}", Vector((sx, sy, gz + sz)), 0.3 * p_idx, dressing_col)
        all_objects.append(sk)

    # Barrel Stacks near Tavern / Well
    bar_coords = [(-1.8, -16.2), (-1.3, -16.0), (3.8, -14.8), (4.3, -14.8)]
    for b_idx, (bx, by) in enumerate(bar_coords):
        gz = get_ground_z(bx, by)
        bar = build_oak_barrel(f"Plaza_Barrel_Cluster_{b_idx}", Vector((bx, by, gz + 0.45)), dressing_col)
        all_objects.append(bar)

    # 9. Rustic Oak Benches for Villagers
    bench_configs = [
        ("Bench_Well_South", (0.0, -22.4), 0),
        ("Bench_Plaza_East", (6.5, -19.2), -75),
        ("Bench_Tavern_Front", (1.5, -15.5), 10),
    ]
    for bname, bpos, bdeg in bench_configs:
        bench_objs = build_oak_bench(bname, bpos, bdeg, dressing_col)
        all_objects.extend(bench_objs)

    # 10. Street-style Timber Posts with Wrought-Iron Lanterns for Evening Market
    post_lantern_coords = [
        (-2.8, -21.0),
        ( 2.8, -21.0),
        (-2.2, -17.5),
        ( 2.4, -17.5),
    ]
    for l_idx, (lx, ly) in enumerate(post_lantern_coords):
        gz = get_ground_z(lx, ly)
        # Timber post
        post_obj = create_cube_mesh(f"Market_LampPost_{l_idx}", size=(0.14, 0.14, 2.6), mat=get_mat("M_Wood_AgedOak"))
        post_obj.location = (lx, ly, gz + 1.3)
        link_to_collection(post_obj, dressing_col)
        add_bevel(post_obj, 0.015, 2)
        all_objects.append(post_obj)

        # Cross arm & hanging lantern
        arm = create_cube_mesh(f"Market_LampArm_{l_idx}", size=(0.45, 0.08, 0.08), mat=get_mat("M_Wood_AgedOak"))
        arm.location = (lx + 0.18, ly, gz + 2.5)
        link_to_collection(arm, dressing_col)
        all_objects.append(arm)

        lantern_objs = build_iron_lantern(f"Market_Lantern_{l_idx}", Vector((lx + 0.32, ly, gz + 2.3)), 0, dressing_col)
        all_objects.extend(lantern_objs)

    print("==================================================")
    print(f"MARKETPLACE BUILD COMPLETE: {len(all_objects)} objects generated!")
    print("==================================================")

if __name__ == "__main__":
    execute_build_marketplace()
