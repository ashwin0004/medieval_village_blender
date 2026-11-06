import bpy

def get_or_create_mat(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat

def create_river_water_reflective():
    mat = get_or_create_mat("M_River_Water_Reflective")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    # Deep translucent mountain river water (emerald cyan-blue)
    bsdf.inputs['Base Color'].default_value = (0.04, 0.16, 0.20, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['IOR'].default_value = 1.333
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.94
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.94
    
    # Layered Procedural Wave & Flow Bump
    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-600, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-400, 0)
    mapping.inputs['Scale'].default_value = (2.0, 1.0, 1.0)
    nt.links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-200, 100)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 1.8
    wave.inputs['Distortion'].default_value = 3.5
    wave.inputs['Detail'].default_value = 4.0
    nt.links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-200, -150)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 5.0
    noise.inputs['Roughness'].default_value = 0.4
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
    bump.inputs['Strength'].default_value = 0.18
    bump.inputs['Distance'].default_value = 0.08
    nt.links.new(mix_out, bump.inputs['Height'])
    
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # Cycles & Eevee transparency settings
    try:
        mat.blend_method = 'BLEND'
    except Exception:
        pass
    print("Created M_River_Water_Reflective")
    return mat

def create_riverbed_gravel():
    mat = get_or_create_mat("M_Riverbed_Gravel")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs['Roughness'].default_value = 0.45
    
    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-600, 0)
    
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.location = (-400, 100)
    vor.inputs['Scale'].default_value = 24.0
    vor.feature = 'F1'
    nt.links.new(tex_coord.outputs['Object'], vor.inputs['Vector'])
    
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-400, -150)
    noise.inputs['Scale'].default_value = 35.0
    nt.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-150, 100)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.05, 0.04, 0.03, 1.0) # dark wet silt
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.22, 0.19, 0.15, 1.0) # river stone
    nt.links.new(vor.outputs['Distance'], ramp.inputs['Fac'])
    
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (100, -100)
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.04
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("Created M_Riverbed_Gravel")
    return mat

def create_water_foam():
    mat = get_or_create_mat("M_Water_Foam")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    # Bright aerated white water
    bsdf.inputs['Base Color'].default_value = (0.92, 0.96, 0.98, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.35
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.35
    
    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-500, 0)
    
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-300, 0)
    noise.inputs['Scale'].default_value = 32.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.7
    nt.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (100, -100)
    bump.inputs['Strength'].default_value = 0.65
    bump.inputs['Distance'].default_value = 0.08
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    print("Created M_Water_Foam")
    return mat

def create_stone_bridge_materials():
    # 1. Ashlar Stone
    mat_ash = get_or_create_mat("M_Stone_Bridge_Ashlar")
    mat_ash.use_nodes = True
    nt = mat_ash.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Base Color'].default_value = (0.28, 0.27, 0.25, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs['Scale'].default_value = 18.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.35
    nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    # 2. Voussoir (Arch stones)
    mat_v = get_or_create_mat("M_Stone_Bridge_Voussoir")
    mat_v.use_nodes = True
    nt = mat_v.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Base Color'].default_value = (0.33, 0.31, 0.28, 1.0) # slightly lighter dressed stone
    bsdf.inputs['Roughness'].default_value = 0.82
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs['Scale'].default_value = 24.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.4
    nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # 3. Waterline Moss on stone
    mat_moss = get_or_create_mat("M_Stone_Waterline_Moss")
    mat_moss.use_nodes = True
    nt = mat_moss.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Base Color'].default_value = (0.12, 0.18, 0.08, 1.0) # mossy green-dark stone
    bsdf.inputs['Roughness'].default_value = 0.95
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs['Scale'].default_value = 16.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.5
    nt.links.new(tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    print("Created Bridge Stone Materials")

if __name__ == '__main__':
    create_river_water_reflective()
    create_riverbed_gravel()
    create_water_foam()
    create_stone_bridge_materials()

