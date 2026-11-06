"""
Medieval Fantasy Village - Comprehensive PBR Materials Library with Variations
Creates realistic procedural PBR materials for Blender 4.x / 5.x Cycles:
- Wood:
  - M_Wood_AgedOak: Weathered aged European oak
  - M_Wood_DarkTimber: Dark stained / pitch-preserved heavy timber
  - M_Wood_LightPine: Fresh-sawn golden pine / carpentry timber
- Stone:
  - M_Stone_Rubble: Rough fieldstone / mortar rubble masonry
  - M_Stone_AshlarGrey: Dressed ashlar limestone / granite blocks
  - M_Stone_Sandstone: Warm golden medieval sandstone
- Plaster:
  - M_Plaster_Lime: Historical lime plaster (off-white)
  - M_Plaster_AgedDaub: Weathered straw-and-clay daub (warm earthy)
- Roofing:
  - M_Clay_Terracotta: Porous kiln-fired clay tiles
  - M_Slate_Dark: Delaminated dark grey-blue roofing slate
- Metals & Glazing:
  - M_Iron_Wrought: Forged wrought iron with micro-hammering
  - M_Glass_Leaded: Transmissive leaded lattice glass
  - M_Lantern_Warm: Candlelight/oil flame emission
"""

import bpy

def get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    return mat

def create_wood_aged_oak():
    mat = get_or_create_material("M_Wood_AgedOak")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-800, 100)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 100)
    mapping.inputs['Scale'].default_value[2] = 10.0
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-380, 100)
    noise.inputs['Scale'].default_value = 14.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.65
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-120, 100)
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = (0.07, 0.045, 0.025, 1.0)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.22, 0.15, 0.09, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.76

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.28
    bump.inputs['Distance'].default_value = 0.025
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_wood_dark_timber():
    mat = get_or_create_material("M_Wood_DarkTimber")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-350, 100)
    noise.inputs['Scale'].default_value = 18.0
    noise.inputs['Detail'].default_value = 7.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-120, 100)
    # Very dark charred / creosote preserved timber
    ramp.color_ramp.elements[0].position = 0.10
    ramp.color_ramp.elements[0].color = (0.025, 0.02, 0.018, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.10, 0.075, 0.055, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.82

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.32
    bump.inputs['Distance'].default_value = 0.02
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_wood_light_pine():
    mat = get_or_create_material("M_Wood_LightPine")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-350, 100)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 5.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-120, 100)
    # Blonde pine / sawn fir
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.42, 0.28, 0.15, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.68, 0.52, 0.32, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.68

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.18
    bump.inputs['Distance'].default_value = 0.015
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_stone_rubble():
    mat = get_or_create_material("M_Stone_Rubble")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 7.5
    noise.inputs['Detail'].default_value = 9.0
    noise.inputs['Roughness'].default_value = 0.70

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.15, 0.14, 0.13, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.38, 0.35, 0.30, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.88

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.38
    bump.inputs['Distance'].default_value = 0.04
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_stone_ashlar_grey():
    mat = get_or_create_material("M_Stone_AshlarGrey")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 10.0
    noise.inputs['Detail'].default_value = 8.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    # Refined dressed grey limestone / castle ashlar
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0.28, 0.29, 0.31, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.52, 0.54, 0.56, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.78

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.24
    bump.inputs['Distance'].default_value = 0.02
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_stone_sandstone():
    mat = get_or_create_material("M_Stone_Sandstone")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 9.0
    noise.inputs['Detail'].default_value = 7.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    # Warm golden medieval sandstone
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.42, 0.32, 0.20, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.64, 0.52, 0.36, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.84

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.30
    bump.inputs['Distance'].default_value = 0.03
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_plaster_lime():
    mat = get_or_create_material("M_Plaster_Lime")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 16.0
    noise.inputs['Detail'].default_value = 6.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0.76, 0.73, 0.66, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.86, 0.83, 0.77, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.86

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.16
    bump.inputs['Distance'].default_value = 0.015
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_plaster_aged_daub():
    mat = get_or_create_material("M_Plaster_AgedDaub")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 7.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    # Earthy straw-and-clay daub
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.55, 0.48, 0.38, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.72, 0.66, 0.54, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.92

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.28
    bump.inputs['Distance'].default_value = 0.025
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_slate_dark():
    mat = get_or_create_material("M_Slate_Dark")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 22.0
    noise.inputs['Detail'].default_value = 8.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.08, 0.09, 0.11, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.18, 0.20, 0.23, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.62

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.22
    bump.inputs['Distance'].default_value = 0.02
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_clay_terracotta():
    mat = get_or_create_material("M_Clay_Terracotta")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 16.0
    noise.inputs['Detail'].default_value = 8.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.26, 0.10, 0.06, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.45, 0.19, 0.11, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.82

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.24
    bump.inputs['Distance'].default_value = 0.025
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_iron_wrought():
    mat = get_or_create_material("M_Iron_Wrought")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.94
    bsdf.inputs['Roughness'].default_value = 0.44

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-300, -150)
    noise.inputs['Scale'].default_value = 35.0

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.18
    bump.inputs['Distance'].default_value = 0.012
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_glass_leaded():
    mat = get_or_create_material("M_Glass_Leaded")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (0.86, 0.93, 0.90, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.06
    bsdf.inputs['IOR'].default_value = 1.48
    bsdf.inputs['Transmission Weight'].default_value = 0.94

    return mat

def create_lantern_warm():
    mat = get_or_create_material("M_Lantern_Warm")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (300, 0)
    emission.inputs['Color'].default_value = (1.0, 0.68, 0.28, 1.0)
    emission.inputs['Strength'].default_value = 18.0
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

    return mat

def create_burlap_material():
    mat = get_or_create_material("M_Burlap_Hessian")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 35.0
    noise.inputs['Detail'].default_value = 7.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.35, 0.28, 0.18, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.55, 0.46, 0.32, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.95

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.42
    bump.inputs['Distance'].default_value = 0.015
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_wicker_material():
    mat = get_or_create_material("M_Wicker_Willow")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 28.0
    noise.inputs['Detail'].default_value = 6.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0.38, 0.28, 0.16, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.62, 0.48, 0.28, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.84

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.018
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_rope_material():
    mat = get_or_create_material("M_Hemp_Rope")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 45.0
    noise.inputs['Detail'].default_value = 8.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.42, 0.34, 0.22, 1.0)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.68, 0.58, 0.40, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.90

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.012
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_ceramic_glazed():
    mat = get_or_create_material("M_Ceramic_Glazed")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 14.0
    noise.inputs['Detail'].default_value = 6.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    # Salt-glazed stoneware tan to dark brown
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (0.24, 0.12, 0.06, 1.0)
    ramp.color_ramp.elements[1].position = 0.70
    ramp.color_ramp.elements[1].color = (0.58, 0.44, 0.28, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.32 # Specular glaze sheen

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.008
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_rusted_iron():
    mat = get_or_create_material("M_Iron_Rusted")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 25.0
    noise.inputs['Detail'].default_value = 8.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    # Gunmetal to reddish-brown rust
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.08, 0.08, 0.09, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.35, 0.12, 0.05, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Metallic'].default_value = 0.65
    bsdf.inputs['Roughness'].default_value = 0.78

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.28
    bump.inputs['Distance'].default_value = 0.015
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_firewood_bark():
    mat = get_or_create_material("M_Firewood_Bark")
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 150)
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 7.0

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 150)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.08, 0.06, 0.04, 1.0) # Dark rough bark
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.38, 0.25, 0.14, 1.0) # Split wood grain
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.88

    bump = nodes.new('ShaderNodeBump')
    bump.location = (80, -150)
    bump.inputs['Strength'].default_value = 0.36
    bump.inputs['Distance'].default_value = 0.03
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def build_all_materials():
    mats = {
        'wood_oak': create_wood_aged_oak(),
        'wood_dark': create_wood_dark_timber(),
        'wood_pine': create_wood_light_pine(),
        'stone_rubble': create_stone_rubble(),
        'stone_ashlar': create_stone_ashlar_grey(),
        'stone_sandstone': create_stone_sandstone(),
        'plaster_lime': create_plaster_lime(),
        'plaster_daub': create_plaster_aged_daub(),
        'slate_dark': create_slate_dark(),
        'clay_terracotta': create_clay_terracotta(),
        'iron_wrought': create_iron_wrought(),
        'iron_rusted': create_rusted_iron(),
        'glass_leaded': create_glass_leaded(),
        'lantern_warm': create_lantern_warm(),
        'burlap': create_burlap_material(),
        'wicker': create_wicker_material(),
        'rope': create_rope_material(),
        'ceramic_glazed': create_ceramic_glazed(),
        'firewood_bark': create_firewood_bark(),
    }
    return mats

create_all_materials = build_all_materials

if __name__ == '__main__':
    build_all_materials()
    print("Full materials library with variations built.")
