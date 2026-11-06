"""
build_pbr_materials_master.py
=============================
Master PBR Materials Upgrade for Medieval Fantasy Village.
Implements physically-based shading across all 11 core medieval materials using
photographic PBR texture maps, multi-scale roughness maps, bump/normal depth,
and subsurface scattering:
  1. Aged Oak Wood (M_Wood_AgedOak, M_Aged_Oak, M_Wood_DarkTimber)
  2. Rough Stone & Mortar (M_Stone_Rough, M_Stone_Rubble, M_Stone_AshlarGrey, M_Stone_Sandstone)
  3. Clay Roof Tiles (M_Clay_Terracotta, M_Tile_Weathered_Moss)
  4. Cobblestone Road (M_Cobblestone_Road)
  5. Slate Roofing (M_Slate_Dark, M_Slate_Roof)
  6. Weathered Lime Plaster (M_Plaster_Lime, M_Plaster_Cream)
  7. Wrought Iron & Rust (M_Iron_Wrought, M_Iron_Rusted)
  8. Leaded Antique Glass (M_Glass_Leaded, M_Leaded_Glass)
  9. Velvet Forest Moss (M_Stone_Waterline_Moss, M_Log_Mossy_Bark)
 10. Meadow Grass (M_Grass_Green)
 11. Compacted Dirt & Mud (M_Ground_Mud, M_Dirt_Path_Mud)

Also constructs a dedicated PBR Material Showcase Palette scene with 11 studio swatches.
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
import os
import math

TEX_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\textures"

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
    out.location = (800, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (500, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return nt, bsdf, out

def load_texture(subpath):
    full_path = os.path.join(TEX_DIR, subpath)
    if os.path.exists(full_path):
        return bpy.data.images.load(full_path, check_existing=True)
    print(f"Warning: Texture file not found: {full_path}")
    return None

# =====================================================================
# 1. AGED OAK WOOD
# =====================================================================
def build_pbr_aged_wood(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (0.35, 0.35, 0.35)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    # Photographic Texture
    tex_img = nt.nodes.new("ShaderNodeTexImage")
    tex_img.location = (-750, 150)
    tex_img.projection = 'BOX'
    tex_img.projection_blend = 0.25
    img = load_texture(r"wood\aged_oak_dark.jpg")
    if img:
        tex_img.image = img
    nt.links.new(mapping.outputs["Vector"], tex_img.inputs["Vector"])
    
    # Secondary vertical grain noise
    noise_grain = nt.nodes.new("ShaderNodeTexNoise")
    noise_grain.location = (-750, -150)
    noise_grain.inputs["Scale"].default_value = 8.0
    noise_grain.inputs["Detail"].default_value = 6.0
    noise_grain.inputs["Roughness"].default_value = 0.7
    nt.links.new(mapping.outputs["Vector"], noise_grain.inputs["Vector"])
    
    # Mix texture with subtle warm heartwood color grading
    mix_col = nt.nodes.new("ShaderNodeMix")
    mix_col.data_type = 'RGBA'
    mix_col.blend_type = 'MULTIPLY'
    mix_col.location = (-450, 150)
    mix_col.inputs["Factor"].default_value = 0.35
    mix_col.inputs[7].default_value = (0.85, 0.72, 0.58, 1.0) # subtle warm oak tint
    nt.links.new(tex_img.outputs["Color"], mix_col.inputs[6])
    nt.links.new(mix_col.outputs["Result"], bsdf.inputs["Base Color"])
    
    # Roughness Map (ColorRamp from texture)
    ramp_rough = nt.nodes.new("ShaderNodeValToRGB")
    ramp_rough.location = (-450, -50)
    ramp_rough.color_ramp.elements[0].position = 0.10
    ramp_rough.color_ramp.elements[0].color = (0.62, 0.62, 0.62, 1.0) # polished raised ridges
    ramp_rough.color_ramp.elements[1].position = 0.85
    ramp_rough.color_ramp.elements[1].color = (0.92, 0.92, 0.92, 1.0) # dry weathered cracks
    nt.links.new(tex_img.outputs["Color"], ramp_rough.inputs["Fac"])
    nt.links.new(ramp_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    # Bump Depth (Deep wood grain grooves & cracks)
    bump_tex = nt.nodes.new("ShaderNodeBump")
    bump_tex.location = (-150, -150)
    bump_tex.inputs["Strength"].default_value = 0.55
    bump_tex.inputs["Distance"].default_value = 0.04
    nt.links.new(tex_img.outputs["Color"], bump_tex.inputs["Height"])
    
    # Micro grain bump
    bump_micro = nt.nodes.new("ShaderNodeBump")
    bump_micro.location = (150, -150)
    bump_micro.inputs["Strength"].default_value = 0.20
    bump_micro.inputs["Distance"].default_value = 0.01
    nt.links.new(noise_grain.outputs["Fac"], bump_micro.inputs["Height"])
    nt.links.new(bump_tex.outputs["Normal"], bump_micro.inputs["Normal"])
    nt.links.new(bump_micro.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Aged Oak: {mat_name}")

# =====================================================================
# 2. ROUGH STONE & MORTAR
# =====================================================================
def build_pbr_rough_stone(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (0.30, 0.30, 0.30)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    # Photographic Texture
    tex_img = nt.nodes.new("ShaderNodeTexImage")
    tex_img.location = (-750, 150)
    tex_img.projection = 'BOX'
    tex_img.projection_blend = 0.25
    img = load_texture(r"stone\rough_stone_wall.jpg")
    if img:
        tex_img.image = img
    nt.links.new(mapping.outputs["Vector"], tex_img.inputs["Vector"])
    
    # Color Ramp for stone tinting / contrast
    ramp_col = nt.nodes.new("ShaderNodeValToRGB")
    ramp_col.location = (-450, 150)
    ramp_col.color_ramp.elements[0].position = 0.05
    ramp_col.color_ramp.elements[0].color = (0.12, 0.11, 0.10, 1.0) # dark mortar
    ramp_col.color_ramp.elements[1].position = 0.90
    ramp_col.color_ramp.elements[1].color = (0.75, 0.72, 0.68, 1.0) # limestone ashlar
    nt.links.new(tex_img.outputs["Color"], ramp_col.inputs["Fac"])
    nt.links.new(tex_img.outputs["Color"], bsdf.inputs["Base Color"])
    
    # Roughness: porous rock vs mortar
    ramp_rough = nt.nodes.new("ShaderNodeValToRGB")
    ramp_rough.location = (-450, -50)
    ramp_rough.color_ramp.elements[0].position = 0.15
    ramp_rough.color_ramp.elements[0].color = (0.72, 0.72, 0.72, 1.0) # flint / smooth faces
    ramp_rough.color_ramp.elements[1].position = 0.80
    ramp_rough.color_ramp.elements[1].color = (0.95, 0.95, 0.95, 1.0) # chalky mortar
    nt.links.new(tex_img.outputs["Color"], ramp_rough.inputs["Fac"])
    nt.links.new(ramp_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    # Deep Mortar & Stone Relief Bump
    bump_stone = nt.nodes.new("ShaderNodeBump")
    bump_stone.location = (-150, -150)
    bump_stone.inputs["Strength"].default_value = 0.75
    bump_stone.inputs["Distance"].default_value = 0.06
    nt.links.new(tex_img.outputs["Color"], bump_stone.inputs["Height"])
    
    # Fine mineral grit micro-bump
    noise_grit = nt.nodes.new("ShaderNodeTexNoise")
    noise_grit.location = (-450, -280)
    noise_grit.inputs["Scale"].default_value = 45.0
    noise_grit.inputs["Detail"].default_value = 4.0
    nt.links.new(mapping.outputs["Vector"], noise_grit.inputs["Vector"])
    
    bump_grit = nt.nodes.new("ShaderNodeBump")
    bump_grit.location = (150, -150)
    bump_grit.inputs["Strength"].default_value = 0.18
    bump_grit.inputs["Distance"].default_value = 0.01
    nt.links.new(noise_grit.outputs["Fac"], bump_grit.inputs["Height"])
    nt.links.new(bump_stone.outputs["Normal"], bump_grit.inputs["Normal"])
    nt.links.new(bump_grit.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Rough Stone: {mat_name}")

# =====================================================================
# 3. CLAY ROOF TILES
# =====================================================================
def build_pbr_clay_tiles(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (0.40, 0.40, 0.40)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    tex_img = nt.nodes.new("ShaderNodeTexImage")
    tex_img.location = (-750, 150)
    tex_img.projection = 'BOX'
    tex_img.projection_blend = 0.20
    img = load_texture(r"roof\clay_roof_tiles.jpg")
    if img:
        tex_img.image = img
    nt.links.new(mapping.outputs["Vector"], tex_img.inputs["Vector"])
    
    # Warm kiln terracotta color grade
    mix_tint = nt.nodes.new("ShaderNodeMix")
    mix_tint.data_type = 'RGBA'
    mix_tint.blend_type = 'MULTIPLY'
    mix_tint.location = (-450, 150)
    mix_tint.inputs["Factor"].default_value = 0.20
    mix_tint.inputs[7].default_value = (1.0, 0.88, 0.78, 1.0)
    nt.links.new(tex_img.outputs["Color"], mix_tint.inputs[6])
    nt.links.new(mix_tint.outputs["Result"], bsdf.inputs["Base Color"])
    
    # Roughness
    ramp_rough = nt.nodes.new("ShaderNodeValToRGB")
    ramp_rough.location = (-450, -50)
    ramp_rough.color_ramp.elements[0].position = 0.15
    ramp_rough.color_ramp.elements[0].color = (0.78, 0.78, 0.78, 1.0)
    ramp_rough.color_ramp.elements[1].position = 0.85
    ramp_rough.color_ramp.elements[1].color = (0.92, 0.92, 0.92, 1.0)
    nt.links.new(tex_img.outputs["Color"], ramp_rough.inputs["Fac"])
    nt.links.new(ramp_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    # Tile Ridge Bump
    bump_tile = nt.nodes.new("ShaderNodeBump")
    bump_tile.location = (-150, -150)
    bump_tile.inputs["Strength"].default_value = 0.80
    bump_tile.inputs["Distance"].default_value = 0.05
    nt.links.new(tex_img.outputs["Color"], bump_tile.inputs["Height"])
    nt.links.new(bump_tile.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Clay Roof Tiles: {mat_name}")

# =====================================================================
# 4. COBBLESTONE ROAD
# =====================================================================
def build_pbr_cobblestone(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (0.28, 0.28, 0.28)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    tex_img = nt.nodes.new("ShaderNodeTexImage")
    tex_img.location = (-750, 150)
    tex_img.projection = 'BOX'
    tex_img.projection_blend = 0.25
    img = load_texture(r"ground\cobblestone_mossy.jpg")
    if img:
        tex_img.image = img
    nt.links.new(mapping.outputs["Vector"], tex_img.inputs["Vector"])
    nt.links.new(tex_img.outputs["Color"], bsdf.inputs["Base Color"])
    
    # Roughness: tops worn smooth (0.55), mortar rough (0.92)
    ramp_rough = nt.nodes.new("ShaderNodeValToRGB")
    ramp_rough.location = (-450, -50)
    ramp_rough.color_ramp.elements[0].position = 0.20
    ramp_rough.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1.0)
    ramp_rough.color_ramp.elements[1].position = 0.80
    ramp_rough.color_ramp.elements[1].color = (0.92, 0.92, 0.92, 1.0)
    nt.links.new(tex_img.outputs["Color"], ramp_rough.inputs["Fac"])
    nt.links.new(ramp_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    # Cobble Relief Bump
    bump_cob = nt.nodes.new("ShaderNodeBump")
    bump_cob.location = (-150, -150)
    bump_cob.inputs["Strength"].default_value = 0.85
    bump_cob.inputs["Distance"].default_value = 0.08
    nt.links.new(tex_img.outputs["Color"], bump_cob.inputs["Height"])
    nt.links.new(bump_cob.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Cobblestone: {mat_name}")

# =====================================================================
# 5. SLATE ROOFING
# =====================================================================
def build_pbr_slate(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (1.5, 1.5, 1.5)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    # Wave texture for layered cleavage planes
    wave_slate = nt.nodes.new("ShaderNodeTexWave")
    wave_slate.location = (-750, 150)
    wave_slate.wave_type = 'BANDS'
    wave_slate.inputs["Scale"].default_value = 6.0
    wave_slate.inputs["Distortion"].default_value = 2.5
    wave_slate.inputs["Detail"].default_value = 4.0
    nt.links.new(mapping.outputs["Vector"], wave_slate.inputs["Vector"])
    
    noise_slate = nt.nodes.new("ShaderNodeTexNoise")
    noise_slate.location = (-750, -150)
    noise_slate.inputs["Scale"].default_value = 18.0
    noise_slate.inputs["Detail"].default_value = 6.0
    nt.links.new(mapping.outputs["Vector"], noise_slate.inputs["Vector"])
    
    # Color Ramp: Charcoal-blue shale
    ramp_col = nt.nodes.new("ShaderNodeValToRGB")
    ramp_col.location = (-450, 150)
    ramp_col.color_ramp.elements[0].position = 0.20
    ramp_col.color_ramp.elements[0].color = (0.04, 0.05, 0.07, 1.0) # deep slate blue-grey
    ramp_col.color_ramp.elements[1].position = 0.85
    ramp_col.color_ramp.elements[1].color = (0.13, 0.15, 0.18, 1.0) # lighter cleavage facet
    nt.links.new(wave_slate.outputs["Color"], ramp_col.inputs["Fac"])
    nt.links.new(ramp_col.outputs["Color"], bsdf.inputs["Base Color"])
    
    # Cleavage sheen roughness (0.42 split sheen to 0.85 edge)
    ramp_rough = nt.nodes.new("ShaderNodeValToRGB")
    ramp_rough.location = (-450, -50)
    ramp_rough.color_ramp.elements[0].position = 0.20
    ramp_rough.color_ramp.elements[0].color = (0.42, 0.42, 0.42, 1.0)
    ramp_rough.color_ramp.elements[1].position = 0.80
    ramp_rough.color_ramp.elements[1].color = (0.85, 0.85, 0.85, 1.0)
    nt.links.new(wave_slate.outputs["Fac"], ramp_rough.inputs["Fac"])
    nt.links.new(ramp_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    # Bump: Stepped flaking
    bump_slate = nt.nodes.new("ShaderNodeBump")
    bump_slate.location = (-150, -150)
    bump_slate.inputs["Strength"].default_value = 0.50
    bump_slate.inputs["Distance"].default_value = 0.03
    nt.links.new(wave_slate.outputs["Color"], bump_slate.inputs["Height"])
    nt.links.new(bump_slate.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Slate Roofing: {mat_name}")

# =====================================================================
# 6. WEATHERED LIME PLASTER
# =====================================================================
def build_pbr_plaster(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    # Trowel wave
    noise_trowel = nt.nodes.new("ShaderNodeTexNoise")
    noise_trowel.location = (-750, 150)
    noise_trowel.inputs["Scale"].default_value = 1.8
    noise_trowel.inputs["Detail"].default_value = 3.0
    nt.links.new(mapping.outputs["Vector"], noise_trowel.inputs["Vector"])
    
    # Stipple micro-grain
    noise_stipple = nt.nodes.new("ShaderNodeTexNoise")
    noise_stipple.location = (-750, -150)
    noise_stipple.inputs["Scale"].default_value = 65.0
    noise_stipple.inputs["Detail"].default_value = 6.0
    nt.links.new(mapping.outputs["Vector"], noise_stipple.inputs["Vector"])
    
    # Historical lime color (soft antique off-white to warm daub)
    ramp_col = nt.nodes.new("ShaderNodeValToRGB")
    ramp_col.location = (-450, 150)
    ramp_col.color_ramp.elements[0].position = 0.15
    ramp_col.color_ramp.elements[0].color = (0.58, 0.54, 0.46, 1.0) # aged weathered shadow
    ramp_col.color_ramp.elements[1].position = 0.85
    ramp_col.color_ramp.elements[1].color = (0.76, 0.73, 0.66, 1.0) # lime wash cream
    nt.links.new(noise_trowel.outputs["Fac"], ramp_col.inputs["Fac"])
    nt.links.new(ramp_col.outputs["Color"], bsdf.inputs["Base Color"])
    
    bsdf.inputs["Roughness"].default_value = 0.88
    
    # Trowel bump + fine stipple
    bump_trowel = nt.nodes.new("ShaderNodeBump")
    bump_trowel.location = (-150, -150)
    bump_trowel.inputs["Strength"].default_value = 0.35
    bump_trowel.inputs["Distance"].default_value = 0.03
    nt.links.new(noise_trowel.outputs["Fac"], bump_trowel.inputs["Height"])
    
    bump_stipple = nt.nodes.new("ShaderNodeBump")
    bump_stipple.location = (150, -150)
    bump_stipple.inputs["Strength"].default_value = 0.15
    bump_stipple.inputs["Distance"].default_value = 0.008
    nt.links.new(noise_stipple.outputs["Fac"], bump_stipple.inputs["Height"])
    nt.links.new(bump_trowel.outputs["Normal"], bump_stipple.inputs["Normal"])
    nt.links.new(bump_stipple.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Weathered Plaster: {mat_name}")

# =====================================================================
# 7. WROUGHT IRON & RUST
# =====================================================================
def build_pbr_iron(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (3.0, 3.0, 3.0)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    # Rust mask noise
    noise_rust = nt.nodes.new("ShaderNodeTexNoise")
    noise_rust.location = (-750, 150)
    noise_rust.inputs["Scale"].default_value = 8.0
    noise_rust.inputs["Detail"].default_value = 8.0
    noise_rust.inputs["Roughness"].default_value = 0.75
    nt.links.new(mapping.outputs["Vector"], noise_rust.inputs["Vector"])
    
    # Color Ramp: Hammered black metal to rust ochre
    ramp_col = nt.nodes.new("ShaderNodeValToRGB")
    ramp_col.location = (-450, 150)
    ramp_col.color_ramp.elements[0].position = 0.45
    ramp_col.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0) # wrought iron
    ramp_col.color_ramp.elements[1].position = 0.70
    ramp_col.color_ramp.elements[1].color = (0.28, 0.09, 0.03, 1.0) # oxidized rust
    nt.links.new(noise_rust.outputs["Fac"], ramp_col.inputs["Fac"])
    nt.links.new(ramp_col.outputs["Color"], bsdf.inputs["Base Color"])
    
    # Metallic: 1.0 on bare iron, 0.0 on rust
    ramp_met = nt.nodes.new("ShaderNodeValToRGB")
    ramp_met.location = (-450, -50)
    ramp_met.color_ramp.elements[0].position = 0.45
    ramp_met.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0) # metallic iron
    ramp_met.color_ramp.elements[1].position = 0.65
    ramp_met.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0) # non-metallic rust
    nt.links.new(noise_rust.outputs["Fac"], ramp_met.inputs["Fac"])
    nt.links.new(ramp_met.outputs["Color"], bsdf.inputs["Metallic"])
    
    # Roughness: 0.45 on metal facets, 0.92 on rust
    ramp_rough = nt.nodes.new("ShaderNodeValToRGB")
    ramp_rough.location = (-450, -220)
    ramp_rough.color_ramp.elements[0].position = 0.45
    ramp_rough.color_ramp.elements[0].color = (0.45, 0.45, 0.45, 1.0)
    ramp_rough.color_ramp.elements[1].position = 0.70
    ramp_rough.color_ramp.elements[1].color = (0.92, 0.92, 0.92, 1.0)
    nt.links.new(noise_rust.outputs["Fac"], ramp_rough.inputs["Fac"])
    nt.links.new(ramp_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    # Hammered & pitted bump
    bump_iron = nt.nodes.new("ShaderNodeBump")
    bump_iron.location = (-150, -150)
    bump_iron.inputs["Strength"].default_value = 0.45
    bump_iron.inputs["Distance"].default_value = 0.02
    nt.links.new(noise_rust.outputs["Fac"], bump_iron.inputs["Height"])
    nt.links.new(bump_iron.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Wrought Iron & Rust: {mat_name}")

# =====================================================================
# 8. MEDIEVAL LEADED GLASS
# =====================================================================
def build_pbr_glass(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (2.0, 2.0, 2.0)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    # Cylinder glass wave distortion
    noise_glass = nt.nodes.new("ShaderNodeTexNoise")
    noise_glass.location = (-750, 150)
    noise_glass.inputs["Scale"].default_value = 4.0
    noise_glass.inputs["Detail"].default_value = 3.0
    nt.links.new(mapping.outputs["Vector"], noise_glass.inputs["Vector"])
    
    # Base Color: Antique greenish/amber tint
    bsdf.inputs["Base Color"].default_value = (0.88, 0.94, 0.89, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.03
    bsdf.inputs["IOR"].default_value = 1.52
    
    # Transmission for realistic Cycles raytraced refraction
    bsdf.inputs["Transmission Weight"].default_value = 0.95
    
    bump_glass = nt.nodes.new("ShaderNodeBump")
    bump_glass.location = (-150, -150)
    bump_glass.inputs["Strength"].default_value = 0.025
    bump_glass.inputs["Distance"].default_value = 0.04
    nt.links.new(noise_glass.outputs["Fac"], bump_glass.inputs["Height"])
    nt.links.new(bump_glass.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Leaded Glass: {mat_name}")

# =====================================================================
# 9. VELVET FOREST MOSS
# =====================================================================
def build_pbr_moss(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (3.5, 3.5, 3.5)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    noise_moss = nt.nodes.new("ShaderNodeTexNoise")
    noise_moss.location = (-750, 150)
    noise_moss.inputs["Scale"].default_value = 12.0
    noise_moss.inputs["Detail"].default_value = 8.0
    noise_moss.inputs["Roughness"].default_value = 0.7
    nt.links.new(mapping.outputs["Vector"], noise_moss.inputs["Vector"])
    
    # Moss Color: Deep forest green to vibrant spring moss
    ramp_col = nt.nodes.new("ShaderNodeValToRGB")
    ramp_col.location = (-450, 150)
    ramp_col.color_ramp.elements[0].position = 0.20
    ramp_col.color_ramp.elements[0].color = (0.08, 0.22, 0.04, 1.0) # damp forest green
    ramp_col.color_ramp.elements[1].position = 0.80
    ramp_col.color_ramp.elements[1].color = (0.24, 0.48, 0.09, 1.0) # bright velvety tip
    nt.links.new(noise_moss.outputs["Fac"], ramp_col.inputs["Fac"])
    nt.links.new(ramp_col.outputs["Color"], bsdf.inputs["Base Color"])
    
    # Subsurface scattering for cellular light bleed
    bsdf.inputs["Subsurface Weight"].default_value = 0.35
    bsdf.inputs["Subsurface Radius"].default_value = (0.15, 0.30, 0.08)
    bsdf.inputs["Roughness"].default_value = 0.92
    
    # Sheen for velvet micro-fuzz
    bsdf.inputs["Sheen Weight"].default_value = 0.85
    bsdf.inputs["Sheen Tint"].default_value = (0.85, 0.95, 0.60, 1.0)
    
    # Cellular tuft bump
    bump_moss = nt.nodes.new("ShaderNodeBump")
    bump_moss.location = (-150, -150)
    bump_moss.inputs["Strength"].default_value = 0.65
    bump_moss.inputs["Distance"].default_value = 0.04
    nt.links.new(noise_moss.outputs["Fac"], bump_moss.inputs["Height"])
    nt.links.new(bump_moss.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Velvet Moss: {mat_name}")

# =====================================================================
# 10. MEADOW GRASS
# =====================================================================
def build_pbr_grass(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (2.0, 2.0, 2.0)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    noise_grass = nt.nodes.new("ShaderNodeTexNoise")
    noise_grass.location = (-750, 150)
    noise_grass.inputs["Scale"].default_value = 8.0
    noise_grass.inputs["Detail"].default_value = 6.0
    nt.links.new(mapping.outputs["Vector"], noise_grass.inputs["Vector"])
    
    ramp_col = nt.nodes.new("ShaderNodeValToRGB")
    ramp_col.location = (-450, 150)
    ramp_col.color_ramp.elements[0].position = 0.20
    ramp_col.color_ramp.elements[0].color = (0.11, 0.28, 0.05, 1.0)
    ramp_col.color_ramp.elements[1].position = 0.85
    ramp_col.color_ramp.elements[1].color = (0.32, 0.52, 0.12, 1.0)
    nt.links.new(noise_grass.outputs["Fac"], ramp_col.inputs["Fac"])
    nt.links.new(ramp_col.outputs["Color"], bsdf.inputs["Base Color"])
    
    bsdf.inputs["Subsurface Weight"].default_value = 0.25
    bsdf.inputs["Subsurface Radius"].default_value = (0.2, 0.4, 0.1)
    bsdf.inputs["Roughness"].default_value = 0.65
    
    bump_grass = nt.nodes.new("ShaderNodeBump")
    bump_grass.location = (-150, -150)
    bump_grass.inputs["Strength"].default_value = 0.35
    bump_grass.inputs["Distance"].default_value = 0.02
    nt.links.new(noise_grass.outputs["Fac"], bump_grass.inputs["Height"])
    nt.links.new(bump_grass.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Meadow Grass: {mat_name}")

# =====================================================================
# 11. COMPACTED DIRT & MUD
# =====================================================================
def build_pbr_dirt(mat_name):
    mat = get_or_create_mat(mat_name)
    nt, bsdf, out = clear_nodes(mat)
    
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs["Scale"].default_value = (1.2, 1.2, 1.2)
    nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
    
    noise_dirt = nt.nodes.new("ShaderNodeTexNoise")
    noise_dirt.location = (-750, 150)
    noise_dirt.inputs["Scale"].default_value = 5.0
    noise_dirt.inputs["Detail"].default_value = 8.0
    noise_dirt.inputs["Roughness"].default_value = 0.75
    nt.links.new(mapping.outputs["Vector"], noise_dirt.inputs["Vector"])
    
    # Soil Color: Rich dark loamy earth
    ramp_col = nt.nodes.new("ShaderNodeValToRGB")
    ramp_col.location = (-450, 150)
    ramp_col.color_ramp.elements[0].position = 0.20
    ramp_col.color_ramp.elements[0].color = (0.09, 0.06, 0.04, 1.0) # damp rut
    ramp_col.color_ramp.elements[1].position = 0.85
    ramp_col.color_ramp.elements[1].color = (0.22, 0.16, 0.11, 1.0) # dry loam silt
    nt.links.new(noise_dirt.outputs["Fac"], ramp_col.inputs["Fac"])
    nt.links.new(ramp_col.outputs["Color"], bsdf.inputs["Base Color"])
    
    # Dynamic moisture roughness
    ramp_rough = nt.nodes.new("ShaderNodeValToRGB")
    ramp_rough.location = (-450, -50)
    ramp_rough.color_ramp.elements[0].position = 0.25
    ramp_rough.color_ramp.elements[0].color = (0.35, 0.35, 0.35, 1.0) # damp soil sheen
    ramp_rough.color_ramp.elements[1].position = 0.75
    ramp_rough.color_ramp.elements[1].color = (0.94, 0.94, 0.94, 1.0) # dry matte earth
    nt.links.new(noise_dirt.outputs["Fac"], ramp_rough.inputs["Fac"])
    nt.links.new(ramp_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    # Earth clod & rut bump
    bump_dirt = nt.nodes.new("ShaderNodeBump")
    bump_dirt.location = (-150, -150)
    bump_dirt.inputs["Strength"].default_value = 0.70
    bump_dirt.inputs["Distance"].default_value = 0.06
    nt.links.new(noise_dirt.outputs["Fac"], bump_dirt.inputs["Height"])
    nt.links.new(bump_dirt.outputs["Normal"], bsdf.inputs["Normal"])
    
    print(f"Built PBR Compacted Dirt & Mud: {mat_name}")

# =====================================================================
# MASTER UPGRADE & SYNC
# =====================================================================
def upgrade_all_pbr_materials():
    print("\n=======================================================")
    print("UPGRADING ALL MEDIEVAL VILLAGE MATERIALS TO PBR")
    print("=======================================================")
    
    # 1. Aged Wood
    for w_name in ["M_Wood_AgedOak", "M_Aged_Oak", "M_Wood_DarkTimber"]:
        build_pbr_aged_wood(w_name)
        
    # 2. Rough Stone
    for s_name in ["M_Stone_Rough", "M_Stone_Rubble", "M_Stone_AshlarGrey", "M_Stone_Sandstone", "M_Stone_Bridge_Ashlar", "M_Stone_Bridge_Voussoir"]:
        build_pbr_rough_stone(s_name)
        
    # 3. Clay Roof Tiles
    for t_name in ["M_Clay_Terracotta", "M_Tile_Weathered_Moss"]:
        build_pbr_clay_tiles(t_name)
        
    # 4. Cobblestone
    build_pbr_cobblestone("M_Cobblestone_Road")
    
    # 5. Slate Roofing
    for sl_name in ["M_Slate_Dark", "M_Slate_Roof"]:
        build_pbr_slate(sl_name)
        
    # 6. Weathered Lime Plaster
    for p_name in ["M_Plaster_Lime", "M_Plaster_Cream"]:
        build_pbr_plaster(p_name)
        
    # 7. Wrought Iron & Rust
    for i_name in ["M_Iron_Wrought", "M_Iron_Rusted"]:
        build_pbr_iron(i_name)
        
    # 8. Leaded Antique Glass
    for g_name in ["M_Glass_Leaded", "M_Leaded_Glass"]:
        build_pbr_glass(g_name)
        
    # 9. Velvet Forest Moss
    for m_name in ["M_Stone_Waterline_Moss", "M_Log_Mossy_Bark"]:
        build_pbr_moss(m_name)
        
    # 10. Meadow Grass
    build_pbr_grass("M_Grass_Green")
    
    # 11. Compacted Dirt & Mud
    for d_name in ["M_Ground_Mud", "M_Dirt_Path_Mud"]:
        build_pbr_dirt(d_name)

    print("All 11 PBR core materials upgraded and synchronized across the scene!")

# =====================================================================
# STUDIO MATERIAL SHOWCASE SWATCH RIG
# =====================================================================
def build_material_swatch_showcase():
    print("\nBuilding Studio Material Palette Swatch Rig...")
    
    col_name = "00_MATERIAL_SHOWCASE_SPHERES"
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
        
    # Dark studio plinth
    plinth_mat = get_or_create_mat("M_Studio_Plinth")
    nt_p, bsdf_p, _ = clear_nodes(plinth_mat)
    bsdf_p.inputs["Base Color"].default_value = (0.04, 0.04, 0.05, 1.0)
    bsdf_p.inputs["Roughness"].default_value = 0.25
    
    # Create Plinth Mesh
    bm_pl = bmesh.new()
    bmesh.ops.create_cube(bm_pl, size=1.0, matrix=Matrix.Translation((0, 200, 0)) @
                          Matrix.Scale(16.0, 4, Vector((1, 0, 0))) @
                          Matrix.Scale(4.5, 4, Vector((0, 1, 0))) @
                          Matrix.Scale(0.35, 4, Vector((0, 0, 1))))
    me_pl = bpy.data.meshes.new("Studio_Plinth_Mesh")
    bm_pl.to_mesh(me_pl)
    bm_pl.free()
    obj_pl = bpy.data.objects.new("Studio_Plinth", me_pl)
    col.objects.link(obj_pl)
    obj_pl.data.materials.append(plinth_mat)
    
    materials_list = [
        ("Aged_Oak", "M_Wood_AgedOak"),
        ("Rough_Stone", "M_Stone_Rough"),
        ("Lime_Plaster", "M_Plaster_Lime"),
        ("Clay_Tiles", "M_Clay_Terracotta"),
        ("Slate_Roof", "M_Slate_Dark"),
        ("Wrought_Iron", "M_Iron_Wrought"),
        ("Leaded_Glass", "M_Glass_Leaded"),
        ("Velvet_Moss", "M_Stone_Waterline_Moss"),
        ("Meadow_Grass", "M_Grass_Green"),
        ("Compacted_Dirt", "M_Ground_Mud"),
        ("Cobblestone", "M_Cobblestone_Road")
    ]
    
    spacing = 1.35
    total_w = (len(materials_list) - 1) * spacing
    start_x = -total_w * 0.5
    
    for idx, (label, mat_name) in enumerate(materials_list):
        sx = start_x + idx * spacing
        sy = 200.0
        sz = 0.70
        
        # Pedestal
        bm_ped = bmesh.new()
        bmesh.ops.create_cone(bm_ped, cap_ends=True, segments=24, radius1=0.38, radius2=0.32, depth=0.60,
                              matrix=Matrix.Translation((sx, sy, 0.30)))
        me_ped = bpy.data.meshes.new(f"Pedestal_{label}_Mesh")
        bm_ped.to_mesh(me_ped)
        bm_ped.free()
        obj_ped = bpy.data.objects.new(f"Pedestal_{label}", me_ped)
        col.objects.link(obj_ped)
        obj_ped.data.materials.append(plinth_mat)
        
        # Swatch Sphere with subdivisions
        bm_sph = bmesh.new()
        bmesh.ops.create_icosphere(bm_sph, subdivisions=4, radius=0.42,
                                   matrix=Matrix.Translation((sx, sy, sz + 0.18)))
        me_sph = bpy.data.meshes.new(f"Sphere_{label}_Mesh")
        bm_sph.to_mesh(me_sph)
        bm_sph.free()
        
        # Smooth shading
        for p in me_sph.polygons:
            p.use_smooth = True
            
        obj_sph = bpy.data.objects.new(f"Sphere_{label}", me_sph)
        col.objects.link(obj_sph)
        
        mat = bpy.data.materials.get(mat_name)
        if mat:
            obj_sph.data.materials.append(mat)
            
    # Camera for Material Showcase
    cam_name = "Cam_PBR_Materials_Showcase"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        col.objects.link(cam_obj)
    cam_obj.location = Vector((0.0, 192.5, 2.2))
    cam_obj.data.lens = 32.0
    dir_vec = (Vector((0.0, 200.0, 0.85)) - cam_obj.location).normalized()
    cam_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    
    # 3-Point Studio Lighting for Materials
    # Key light
    key_light = bpy.data.lights.new("Studio_Key_Light", 'AREA')
    key_light.energy = 450.0
    key_light.size = 6.0
    key_light.color = (1.0, 0.95, 0.90)
    obj_key = bpy.data.objects.new("Studio_Key_Light", key_light)
    col.objects.link(obj_key)
    obj_key.location = Vector((-6.0, 195.0, 5.5))
    k_dir = (Vector((0.0, 200.0, 0.85)) - obj_key.location).normalized()
    obj_key.rotation_euler = k_dir.to_track_quat('-Z', 'Y').to_euler()
    
    # Fill light
    fill_light = bpy.data.lights.new("Studio_Fill_Light", 'AREA')
    fill_light.energy = 180.0
    fill_light.size = 8.0
    fill_light.color = (0.85, 0.92, 1.0)
    obj_fill = bpy.data.objects.new("Studio_Fill_Light", fill_light)
    col.objects.link(obj_fill)
    obj_fill.location = Vector((7.0, 196.0, 4.0))
    f_dir = (Vector((0.0, 200.0, 0.85)) - obj_fill.location).normalized()
    obj_fill.rotation_euler = f_dir.to_track_quat('-Z', 'Y').to_euler()
    
    # Rim / Back light for specular sheen
    rim_light = bpy.data.lights.new("Studio_Rim_Light", 'AREA')
    rim_light.energy = 650.0
    rim_light.size = 14.0
    rim_light.color = (1.0, 0.92, 0.85)
    obj_rim = bpy.data.objects.new("Studio_Rim_Light", rim_light)
    col.objects.link(obj_rim)
    obj_rim.location = Vector((0.0, 204.5, 4.5))
    r_dir = (Vector((0.0, 200.0, 0.85)) - obj_rim.location).normalized()
    obj_rim.rotation_euler = r_dir.to_track_quat('-Z', 'Y').to_euler()

    print("Studio Material Palette Swatch Rig successfully constructed at Y = 200m!")

if __name__ == "__main__":
    upgrade_all_pbr_materials()
    build_material_swatch_showcase()
