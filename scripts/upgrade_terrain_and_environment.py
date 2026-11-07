import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

def upgrade_grass_material():
    print("Upgrading M_Grass_Green to photorealistic European alpine meadow...")
    mat = bpy.data.materials.get("M_Grass_Green")
    if not mat:
        mat = bpy.data.materials.new("M_Grass_Green")
        mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Create Nodes
    out_node = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Specular IOR Level'].default_value = 0.2

    # Coordinates
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (0.12, 0.12, 0.12)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # Macro Noise for Large Tone Variations (Deep green vs Meadow vs Dry Thatch)
    noise_macro = nodes.new('ShaderNodeTexNoise')
    noise_macro.inputs['Scale'].default_value = 0.08
    noise_macro.inputs['Detail'].default_value = 4.0
    noise_macro.inputs['Roughness'].default_value = 0.6
    links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])

    ramp_macro = nodes.new('ShaderNodeValToRGB')
    ramp_macro.color_ramp.elements[0].position = 0.25
    ramp_macro.color_ramp.elements[0].color = (0.05, 0.11, 0.03, 1.0) # Deep dark woodland green
    ramp_macro.color_ramp.elements[1].position = 0.70
    ramp_macro.color_ramp.elements[1].color = (0.13, 0.21, 0.06, 1.0) # Rich alpine meadow green
    el_dry = ramp_macro.color_ramp.elements.new(0.92)
    el_dry.color = (0.24, 0.22, 0.11, 1.0) # Weathered dry grass / thatch
    links.new(noise_macro.outputs['Fac'], ramp_macro.inputs['Fac'])

    # Micro Noise for Soil & Grass Blade Strands
    noise_micro = nodes.new('ShaderNodeTexNoise')
    noise_micro.inputs['Scale'].default_value = 4.5
    noise_micro.inputs['Detail'].default_value = 8.0
    noise_micro.inputs['Roughness'].default_value = 0.7
    links.new(tex_coord.outputs['Object'], noise_micro.inputs['Vector'])

    mix_color = nodes.new('ShaderNodeMix')
    mix_color.data_type = 'RGBA'
    mix_color.blend_type = 'DARKEN'
    mix_color.inputs['Factor'].default_value = 0.45
    links.new(ramp_macro.outputs['Color'], mix_color.inputs[6])
    
    # Soil color
    soil_color = nodes.new('ShaderNodeRGB')
    soil_color.outputs['Color'].default_value = (0.08, 0.055, 0.03, 1.0)
    links.new(soil_color.outputs['Color'], mix_color.inputs[7])

    # Blend with micro texture
    blend_micro = nodes.new('ShaderNodeMix')
    blend_micro.data_type = 'RGBA'
    blend_micro.blend_type = 'MIX'
    links.new(noise_micro.outputs['Fac'], blend_micro.inputs['Factor'])
    links.new(ramp_macro.outputs['Color'], blend_micro.inputs[6])
    links.new(mix_color.outputs[2], blend_micro.inputs[7])

    links.new(blend_micro.outputs[2], bsdf.inputs['Base Color'])

    # Bump mapping for terrain turf texture
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.15
    links.new(noise_micro.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    print("M_Grass_Green upgraded.")

def build_seamless_midground_terrain():
    print("Building seamless midground terrain skirt to eliminate dark outer boundary...")
    col = bpy.data.collections.get("99_TERRAIN_ATMOSPHERE")
    if not col:
        col = bpy.data.collections.get("06_ENVIRONMENT_NATURE")

    # Remove previous skirt if exists
    for o in list(bpy.data.objects):
        if o.name == "Terrain_Midground_Skirt":
            bpy.data.objects.remove(o, do_unlink=True)

    bm = bmesh.new()

    # Create concentric rings expanding from radius 58m out to 220m
    num_segments = 48
    radii = [56.0, 75.0, 105.0, 145.0, 195.0, 240.0]
    heights = [0.0, 3.5, 9.0, 18.0, 32.0, 48.0]

    ring_verts = []
    for r_idx, (r, h_base) in enumerate(zip(radii, heights)):
        current_ring = []
        for i in range(num_segments):
            angle = (2 * math.pi / num_segments) * i
            # Add rolling hill undulation
            h_var = math.sin(angle * 3) * (r * 0.08) + math.cos(angle * 5) * (r * 0.04)
            z = h_base + h_var
            # Dip in river directions (North-West)
            if math.radians(110) <= angle <= math.radians(170):
                z -= 6.0
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            v = bm.verts.new((x, y, z))
            current_ring.append(v)
        ring_verts.append(current_ring)

    # Bridge rings with quad faces
    for r_idx in range(len(radii) - 1):
        r1 = ring_verts[r_idx]
        r2 = ring_verts[r_idx + 1]
        for i in range(num_segments):
            next_i = (i + 1) % num_segments
            bm.faces.new([r1[i], r2[i], r2[next_i], r1[next_i]])

    mesh = bpy.data.meshes.new("Terrain_Midground_Skirt_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Terrain_Midground_Skirt", mesh)
    mat = bpy.data.materials.get("M_Grass_Green")
    if mat:
        obj.data.materials.append(mat)
    col.objects.link(obj)

    # Smooth shading
    for poly in mesh.polygons:
        poly.use_smooth = True

    print("Terrain midground skirt complete!")

def setup_natural_daylight_sky():
    print("Setting up natural European alpine daylight sky...")
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    out_node = nodes.new('ShaderNodeOutputWorld')
    bg_node = nodes.new('ShaderNodeBackground')

    # Color Ramp for Realistic Atmospheric Sky Gradient
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])

    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.gradient_type = 'LINEAR'
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.76, 0.82, 0.88, 1.0) # Soft alpine horizon mist
    ramp.color_ramp.elements[1].position = 0.55
    ramp.color_ramp.elements[1].color = (0.35, 0.58, 0.85, 1.0) # Clear European azure sky
    links.new(gradient.outputs['Fac'], ramp.inputs['Fac'])

    links.new(ramp.outputs['Color'], bg_node.inputs['Color'])
    bg_node.inputs['Strength'].default_value = 1.15
    links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])

    # Ensure Sun is angled naturally for crisp alpine sunlight
    sun = bpy.data.objects.get("Sun_Daylight")
    if sun:
        sun.hide_render = False
        sun.data.energy = 5.5
        sun.data.color = (1.0, 0.96, 0.90) # Warm sun tint
        sun.rotation_euler = Euler((math.radians(52), math.radians(16), math.radians(-38)), 'XYZ')

    print("Natural daylight sky setup complete!")

def run_environment_upgrades():
    upgrade_grass_material()
    build_seamless_midground_terrain()
    setup_natural_daylight_sky()

if __name__ == "__main__":
    run_environment_upgrades()

