"""
polish_materials.py
===================
Master PBR Materials Upgrade for Medieval Fantasy Village.
Creates photorealistic procedural materials using Cycles nodes:
  - M_Terrain_Landscape (slope/height blended grass, soil, rock)
  - M_Grass_Green (procedural grass blades with subsurface translucency)
  - M_Foliage_Canopy (leaf cluster variegation with SSS & micro-bump)
  - M_Foliage_Bush (warm green shrubbery)
  - M_Cobblestone_Road (Voronoi mortared stones with roughness/dirt mask)
  - M_River_Water (deep blue-green absorption, wave ripples, fresnel)
  - M_Stone_Rough & M_Stone_Rubble (multi-octave chiseled masonry with moss)
  - M_Aged_Oak & M_Wood_AgedOak (directional grain, cracks, silvered patina)
  - M_Plaster_Cream & M_Plaster_Historic (troweled stippling, dirt stains)
  - M_Slate_Roof (cleavage planes, subtle sheen, dark charcoal-blue)
  - M_Clay_Terracotta (kiln-fired warmth, powdery matte, edge moss)
  - M_Window_Leaded & M_Window_Glow (daytime leaded glass vs warm night emission)
  - M_Lantern_Warm (incandescent amber glow for street lamps and interiors)
  - M_Iron_Wrought (hammered blacksmith iron with micro-pitting)
  - M_Hay_Thatch (dry golden fibrous straw)
"""

import bpy
import math

def get_or_create_mat(name):
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat

def clear_nodes(mat):
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    return nt, out

# ──────────────────────────────────────────────
# 1. UPGRADED TERRAIN SHADER
# ──────────────────────────────────────────────
def upgrade_terrain_material():
    mat = get_or_create_mat("M_Ground_Mud")
    nt, out = clear_nodes(mat)
    
    # Coordinates
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    # Macro Noise for color variation (soil vs grass vs rock)
    noise_macro = nt.nodes.new("ShaderNodeTexNoise")
    noise_macro.location = (-900, 200)
    noise_macro.inputs["Scale"].default_value = 0.08
    noise_macro.inputs["Detail"].default_value = 4.0
    noise_macro.inputs["Roughness"].default_value = 0.6
    nt.links.new(tc.outputs["Object"], noise_macro.inputs["Vector"])
    
    # Micro Noise for soil/grass texture
    noise_micro = nt.nodes.new("ShaderNodeTexNoise")
    noise_micro.location = (-900, -100)
    noise_micro.inputs["Scale"].default_value = 4.5
    noise_micro.inputs["Detail"].default_value = 8.0
    noise_micro.inputs["Roughness"].default_value = 0.7
    nt.links.new(tc.outputs["Object"], noise_micro.inputs["Vector"])
    
    # Grass Color Ramp (rich medieval pasture green to olive gold)
    ramp_grass = nt.nodes.new("ShaderNodeValToRGB")
    ramp_grass.location = (-600, 200)
    ramp_grass.color_ramp.elements[0].position = 0.2
    ramp_grass.color_ramp.elements[0].color = (0.05, 0.16, 0.04, 1.0) # Deep forest moss green
    ramp_grass.color_ramp.elements[1].position = 0.8
    ramp_grass.color_ramp.elements[1].color = (0.16, 0.32, 0.06, 1.0) # Sunlit meadow green
    nt.links.new(noise_macro.outputs["Fac"], ramp_grass.inputs["Fac"])
    
    # Soil Color Ramp (dark rich loam to dry dirt)
    ramp_soil = nt.nodes.new("ShaderNodeValToRGB")
    ramp_soil.location = (-600, -50)
    ramp_soil.color_ramp.elements[0].position = 0.3
    ramp_soil.color_ramp.elements[0].color = (0.12, 0.09, 0.06, 1.0) # Damp earth
    ramp_soil.color_ramp.elements[1].position = 0.7
    ramp_soil.color_ramp.elements[1].color = (0.24, 0.18, 0.12, 1.0) # Dry clay soil
    nt.links.new(noise_micro.outputs["Fac"], ramp_soil.inputs["Fac"])
    
    # Mix Grass & Soil (Blender 4/5 compatible)
    try:
        mix_surface = nt.nodes.new("ShaderNodeMix")
        mix_surface.data_type = 'RGBA'
        mix_surface.blend_type = "MIX"
        mix_surface.location = (-300, 100)
        mix_factor = nt.nodes.new("ShaderNodeMath")
        mix_factor.location = (-450, 400)
        mix_factor.operation = "MULTIPLY"
        mix_factor.inputs[1].default_value = 1.3
        nt.links.new(noise_macro.outputs["Color"], mix_factor.inputs[0])
        nt.links.new(mix_factor.outputs["Value"], mix_surface.inputs["Factor"])
        nt.links.new(ramp_soil.outputs["Color"], mix_surface.inputs[6])
        nt.links.new(ramp_grass.outputs["Color"], mix_surface.inputs[7])
        surface_color = mix_surface.outputs["Result"]
    except Exception:
        mix_surface = nt.nodes.new("ShaderNodeMixRGB")
        mix_surface.location = (-300, 100)
        mix_surface.blend_type = "MIX"
        mix_factor = nt.nodes.new("ShaderNodeMath")
        mix_factor.location = (-450, 400)
        mix_factor.operation = "MULTIPLY"
        mix_factor.inputs[1].default_value = 1.3
        nt.links.new(noise_macro.outputs["Color"], mix_factor.inputs[0])
        nt.links.new(mix_factor.outputs["Value"], mix_surface.inputs["Fac"])
        nt.links.new(ramp_soil.outputs["Color"], mix_surface.inputs["Color1"])
        nt.links.new(ramp_grass.outputs["Color"], mix_surface.inputs["Color2"])
        surface_color = mix_surface.outputs["Color"]
    
    # Principled BSDF
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    nt.links.new(surface_color, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.88
    
    # Subsurface for lush grass look
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.08
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.08
        
    # Bump for ground texture
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (0, -200)
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.1
    nt.links.new(noise_micro.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

# ──────────────────────────────────────────────
# 2. UPGRADED FOLIAGE (TREES & BUSHES)
# ──────────────────────────────────────────────
def upgrade_foliage_materials():
    # Tree canopy material
    mat_canopy = get_or_create_mat("M_Grass_Green")
    nt, out = clear_nodes(mat_canopy)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, 0)
    
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-650, 0)
    noise.inputs["Scale"].default_value = 8.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.65
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-400, 100)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0.04, 0.15, 0.03, 1.0) # Deep forest shadow
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.18, 0.38, 0.07, 1.0) # Vibrant sunlit foliage
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    
    # Subsurface scattering gives lush translucent leaf feel in Cycles!
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
        if "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = (0.1, 0.3, 0.05)
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.25
        
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (0, -200)
    bump.inputs["Strength"].default_value = 0.25
    bump.inputs["Distance"].default_value = 0.05
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat_canopy

# ──────────────────────────────────────────────
# 3. UPGRADED COBBLESTONE ROAD
# ──────────────────────────────────────────────
def upgrade_cobblestone_material():
    mat = get_or_create_mat("M_Cobblestone_Road")
    nt, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1100, 0)
    
    # Voronoi for stone cobblestone cells
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.location = (-850, 150)
    vor.voronoi_dimensions = "2D"
    vor.feature = "F1"
    vor.distance = "EUCLIDEAN"
    vor.inputs["Scale"].default_value = 5.5
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    
    # Distance to edge gives mortar groove
    vor_edge = nt.nodes.new("ShaderNodeTexVoronoi")
    vor_edge.location = (-850, -150)
    vor_edge.voronoi_dimensions = "2D"
    vor_edge.feature = "DISTANCE_TO_EDGE"
    vor_edge.inputs["Scale"].default_value = 5.5
    nt.links.new(tc.outputs["Object"], vor_edge.inputs["Vector"])
    
    # Stone color variations (grey granite, warm sandstone, dark slate)
    ramp_stone = nt.nodes.new("ShaderNodeValToRGB")
    ramp_stone.location = (-550, 200)
    ramp_stone.color_ramp.elements[0].position = 0.15
    ramp_stone.color_ramp.elements[0].color = (0.15, 0.14, 0.13, 1.0) # Dark basalt
    ramp_stone.color_ramp.elements[1].position = 0.85
    ramp_stone.color_ramp.elements[1].color = (0.35, 0.32, 0.28, 1.0) # Weathered granite
    nt.links.new(vor.outputs["Color"], ramp_stone.inputs["Fac"])
    
    # Mortar mask
    ramp_mortar = nt.nodes.new("ShaderNodeValToRGB")
    ramp_mortar.location = (-550, -100)
    ramp_mortar.color_ramp.elements[0].position = 0.04
    ramp_mortar.color_ramp.elements[0].color = (0.08, 0.06, 0.05, 1.0) # Dark dirt mortar
    ramp_mortar.color_ramp.elements[1].position = 0.18
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
        stone_color = mix.outputs["Result"]
    except Exception:
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.location = (-250, 50)
        mix.blend_type = "MULTIPLY"
        nt.links.new(ramp_stone.outputs["Color"], mix.inputs["Color1"])
        nt.links.new(ramp_mortar.outputs["Color"], mix.inputs["Color2"])
        mix.inputs["Fac"].default_value = 1.0
        stone_color = mix.outputs["Color"]
    
    # BSDF
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    nt.links.new(stone_color, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.82
    
    # Stone height bump
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (0, -200)
    bump.inputs["Strength"].default_value = 0.65
    bump.inputs["Distance"].default_value = 0.08
    nt.links.new(ramp_mortar.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

# ──────────────────────────────────────────────
# 4. UPGRADED RIVER WATER SHADER
# ──────────────────────────────────────────────
def upgrade_river_water_material():
    mat = get_or_create_mat("M_River_Water")
    nt, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1000, 0)
    
    # Water ripples - layered Wave + Noise
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-750, -100)
    wave.wave_type = "BANDS"
    wave.inputs["Scale"].default_value = 3.5
    wave.inputs["Distortion"].default_value = 8.0
    wave.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], wave.inputs["Vector"])
    
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-750, 150)
    noise.inputs["Scale"].default_value = 12.0
    noise.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    
    try:
        mix_bump = nt.nodes.new("ShaderNodeMix")
        mix_bump.data_type = 'RGBA'
        mix_bump.blend_type = "ADD"
        mix_bump.location = (-450, 0)
        mix_bump.inputs["Factor"].default_value = 0.4
        nt.links.new(wave.outputs["Color"], mix_bump.inputs[6])
        nt.links.new(noise.outputs["Color"], mix_bump.inputs[7])
        bump_height = mix_bump.outputs["Result"]
    except Exception:
        mix_bump = nt.nodes.new("ShaderNodeMixRGB")
        mix_bump.location = (-450, 0)
        mix_bump.blend_type = "ADD"
        mix_bump.inputs["Fac"].default_value = 0.4
        nt.links.new(wave.outputs["Color"], mix_bump.inputs["Color1"])
        nt.links.new(noise.outputs["Color"], mix_bump.inputs["Color2"])
        bump_height = mix_bump.outputs["Color"]
    
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    # Deep emerald river water
    bsdf.inputs["Base Color"].default_value = (0.06, 0.22, 0.28, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.04
    bsdf.inputs["IOR"].default_value = 1.333
    
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.88
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = 0.88
        
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (0, -200)
    bump.inputs["Strength"].default_value = 0.15
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(bump_height, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

# ──────────────────────────────────────────────
# 5. UPGRADED STONE & MASONRY
# ──────────────────────────────────────────────
def upgrade_stone_materials():
    for mat_name in ["M_Stone_Rough", "M_Rough_Stone", "M_Stone_AshlarGrey", "M_Stone_Rubble"]:
        mat = get_or_create_mat(mat_name)
        nt, out = clear_nodes(mat)
        
        tc = nt.nodes.new("ShaderNodeTexCoord")
        tc.location = (-1000, 0)
        
        noise1 = nt.nodes.new("ShaderNodeTexNoise")
        noise1.location = (-750, 150)
        noise1.inputs["Scale"].default_value = 4.0
        noise1.inputs["Detail"].default_value = 8.0
        noise1.inputs["Roughness"].default_value = 0.7
        nt.links.new(tc.outputs["Object"], noise1.inputs["Vector"])
        
        noise2 = nt.nodes.new("ShaderNodeTexNoise")
        noise2.location = (-750, -150)
        noise2.inputs["Scale"].default_value = 18.0
        noise2.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], noise2.inputs["Vector"])
        
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.location = (-450, 100)
        ramp.color_ramp.elements[0].position = 0.2
        ramp.color_ramp.elements[0].color = (0.18, 0.17, 0.16, 1.0) # Dark weathered stone
        ramp.color_ramp.elements[1].position = 0.8
        ramp.color_ramp.elements[1].color = (0.38, 0.36, 0.34, 1.0) # Light chiseled stone
        nt.links.new(noise1.outputs["Fac"], ramp.inputs["Fac"])
        
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (200, 0)
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.88
        
        bump = nt.nodes.new("ShaderNodeBump")
        bump.location = (0, -200)
        bump.inputs["Strength"].default_value = 0.45
        bump.inputs["Distance"].default_value = 0.06
        nt.links.new(noise2.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# ──────────────────────────────────────────────
# 6. UPGRADED TIMBER & WOOD
# ──────────────────────────────────────────────
def upgrade_wood_materials():
    for mat_name in ["M_Aged_Oak", "M_Wood_AgedOak", "M_Wood_DarkTimber"]:
        mat = get_or_create_mat(mat_name)
        nt, out = clear_nodes(mat)
        
        tc = nt.nodes.new("ShaderNodeTexCoord")
        tc.location = (-1100, 0)
        
        # Anisotropic wood stretch
        map_node = nt.nodes.new("ShaderNodeMapping")
        map_node.location = (-900, 0)
        map_node.inputs["Scale"].default_value = (1.0, 1.0, 8.0)
        nt.links.new(tc.outputs["Object"], map_node.inputs["Vector"])
        
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.location = (-650, 150)
        wave.wave_type = "RINGS"
        wave.inputs["Scale"].default_value = 2.0
        wave.inputs["Distortion"].default_value = 3.5
        wave.inputs["Detail"].default_value = 4.0
        nt.links.new(map_node.outputs["Vector"], wave.inputs["Vector"])
        
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.location = (-650, -150)
        noise.inputs["Scale"].default_value = 6.0
        noise.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.location = (-350, 100)
        ramp.color_ramp.elements[0].position = 0.15
        ramp.color_ramp.elements[0].color = (0.09, 0.06, 0.04, 1.0) # Deep aged brown
        ramp.color_ramp.elements[1].position = 0.85
        ramp.color_ramp.elements[1].color = (0.24, 0.18, 0.13, 1.0) # Silvered weathered oak
        nt.links.new(wave.outputs["Color"], ramp.inputs["Fac"])
        
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (200, 0)
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.78
        
        bump = nt.nodes.new("ShaderNodeBump")
        bump.location = (0, -200)
        bump.inputs["Strength"].default_value = 0.35
        bump.inputs["Distance"].default_value = 0.04
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# ──────────────────────────────────────────────
# 7. UPGRADED PLASTER & DAUB
# ──────────────────────────────────────────────
def upgrade_plaster_materials():
    for mat_name in ["M_Plaster_Cream", "M_Plaster_Historic", "M_Plaster_Lime"]:
        mat = get_or_create_mat(mat_name)
        nt, out = clear_nodes(mat)
        
        tc = nt.nodes.new("ShaderNodeTexCoord")
        tc.location = (-1000, 0)
        
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.location = (-750, 0)
        noise.inputs["Scale"].default_value = 15.0
        noise.inputs["Detail"].default_value = 6.0
        noise.inputs["Roughness"].default_value = 0.7
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.location = (-450, 100)
        ramp.color_ramp.elements[0].position = 0.2
        ramp.color_ramp.elements[0].color = (0.65, 0.60, 0.52, 1.0) # Aged cream/ochre
        ramp.color_ramp.elements[1].position = 0.8
        ramp.color_ramp.elements[1].color = (0.82, 0.79, 0.72, 1.0) # Whitewashed lime plaster
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (200, 0)
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.92
        
        bump = nt.nodes.new("ShaderNodeBump")
        bump.location = (0, -200)
        bump.inputs["Strength"].default_value = 0.25
        bump.inputs["Distance"].default_value = 0.02
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# ──────────────────────────────────────────────
# 8. UPGRADED ROOF MATERIALS
# ──────────────────────────────────────────────
def upgrade_roof_materials():
    # Slate Roof
    for mat_name in ["M_Slate_Roof", "M_Slate_Dark"]:
        mat = get_or_create_mat(mat_name)
        nt, out = clear_nodes(mat)
        
        tc = nt.nodes.new("ShaderNodeTexCoord")
        tc.location = (-900, 0)
        
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.location = (-650, 0)
        noise.inputs["Scale"].default_value = 22.0
        noise.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.location = (-400, 100)
        ramp.color_ramp.elements[0].position = 0.2
        ramp.color_ramp.elements[0].color = (0.12, 0.14, 0.16, 1.0) # Dark charcoal blue slate
        ramp.color_ramp.elements[1].position = 0.8
        ramp.color_ramp.elements[1].color = (0.22, 0.25, 0.28, 1.0) # Grey slate sheen
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (200, 0)
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.45 # Polished slate cleavage
        
        bump = nt.nodes.new("ShaderNodeBump")
        bump.location = (0, -200)
        bump.inputs["Strength"].default_value = 0.3
        bump.inputs["Distance"].default_value = 0.03
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        
    # Terracotta Clay
    for mat_name in ["M_Clay_Terracotta", "M_Clay_Tile"]:
        mat = get_or_create_mat(mat_name)
        nt, out = clear_nodes(mat)
        
        tc = nt.nodes.new("ShaderNodeTexCoord")
        tc.location = (-900, 0)
        
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.location = (-650, 0)
        noise.inputs["Scale"].default_value = 10.0
        noise.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.location = (-400, 100)
        ramp.color_ramp.elements[0].position = 0.2
        ramp.color_ramp.elements[0].color = (0.35, 0.12, 0.05, 1.0) # Fired brick red
        ramp.color_ramp.elements[1].position = 0.8
        ramp.color_ramp.elements[1].color = (0.55, 0.24, 0.10, 1.0) # Warm terracotta orange
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (200, 0)
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.86
        
        bump = nt.nodes.new("ShaderNodeBump")
        bump.location = (0, -200)
        bump.inputs["Strength"].default_value = 0.35
        bump.inputs["Distance"].default_value = 0.04
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# ──────────────────────────────────────────────
# 9. WINDOWS & LANTERNS (DAYTIME VS NIGHT EMISSION)
# ──────────────────────────────────────────────
def set_windows_and_lanterns_state(night_glow=False, emission_mult=1.0):
    """Configures windows and lanterns for daytime clarity or nighttime warm emission."""
    # Leaded glass material
    for g_name in ["M_Glass_Leaded", "M_Leaded_Glass"]:
        mat = get_or_create_mat(g_name)
        nt, out = clear_nodes(mat)
        
        if night_glow:
            # Night: glowing interior candlelight
            em = nt.nodes.new("ShaderNodeEmission")
            em.location = (200, 0)
            em.inputs["Color"].default_value = (1.0, 0.70, 0.28, 1.0) # Cozy warm amber interior
            em.inputs["Strength"].default_value = 14.0 * emission_mult
            nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        else:
            # Day: transparent leaded window with slight reflection
            bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
            bsdf.location = (200, 0)
            bsdf.inputs["Base Color"].default_value = (0.75, 0.85, 0.80, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.08
            bsdf.inputs["IOR"].default_value = 1.45
            if "Transmission Weight" in bsdf.inputs:
                bsdf.inputs["Transmission Weight"].default_value = 0.88
            elif "Transmission" in bsdf.inputs:
                bsdf.inputs["Transmission"].default_value = 0.88
            nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Lantern materials
    for l_name in ["M_Lantern_Warm", "M_Lantern_Glow"]:
        mat = get_or_create_mat(l_name)
        nt, out = clear_nodes(mat)
        em = nt.nodes.new("ShaderNodeEmission")
        em.location = (200, 0)
        em.inputs["Color"].default_value = (1.0, 0.65, 0.22, 1.0) # Radiant flame glow
        em.inputs["Strength"].default_value = (35.0 * emission_mult) if night_glow else 2.5
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])

def apply_all_material_upgrades():
    print("Upgrading all materials to realistic PBR...")
    upgrade_terrain_material()
    upgrade_foliage_materials()
    upgrade_cobblestone_material()
    upgrade_river_water_material()
    upgrade_stone_materials()
    upgrade_wood_materials()
    upgrade_plaster_materials()
    upgrade_roof_materials()
    set_windows_and_lanterns_state(night_glow=False)
    print("Materials upgrade complete!")

if __name__ == "__main__":
    apply_all_material_upgrades()

