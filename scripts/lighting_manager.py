"""
lighting_manager.py
===================
Cinematic Lighting Setups for Medieval Fantasy Village:
  1. DAYTIME:
     - Crisp, warm sun (38 deg elevation, azimuth 160 deg)
     - Clean Hosek-Wilkie sky with soft fill
     - Realistic sharp-to-soft medieval architectural shadows
  2. SUNSET:
     - Dramatic low golden-hour sun (10 deg elevation, azimuth 255 deg)
     - Rich warm amber/crimson rim highlights across rooftops
     - Deep twilight atmosphere
     - Early lantern glow starting to flicker
  3. NIGHTTIME:
     - Deep midnight blue indigo sky
     - Soft cool silver-blue moonlight (55 deg elevation, azimuth 65 deg)
     - Warm incandescent point lights inside lanterns and tavern/cottage windows
     - High emission lantern flames and leaded window glow
"""

import bpy
import math
import os
import sys

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if _SCRIPTS_DIR not in sys.path:
    sys.path.append(_SCRIPTS_DIR)

def clean_lighting_rig():
    """Removes previous dynamic lamps and lingering sun lamps to prevent buildup."""
    for o in list(bpy.data.objects):
        if o.name.startswith("Village_Dyn_"):
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.type == 'LIGHT' and o.data.type == 'SUN':
            # Remove any sun lights to ensure a clean lighting baseline
            bpy.data.objects.remove(o, do_unlink=True)
        elif o.name in ["Sun_Daylight", "Sun_Medieval_Day", "Sun_Fill_Soft", "Light_Props_Sun", "Light_Showcase_Sun", "River_Hero_Sun"]:
            bpy.data.objects.remove(o, do_unlink=True)

def get_or_create_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def setup_cycles_engine(samples=128):
    """Configures Blender Cycles for optimal GPU OptiX rendering and denoising."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.samples = samples
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"
    
    # Denoising
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPTIX"
    except Exception:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
        
    # Color management
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        try:
            scene.view_settings.look = "Medium High Contrast"
        except Exception:
            pass
            
    # Enable OptiX devices
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
    except Exception as e:
        print(f"Cycles device setup note: {e}")

# ──────────────────────────────────────────────
# 1. DAYTIME LIGHTING SETUP
# ──────────────────────────────────────────────
def set_daytime_lighting(samples=128):
    print("Setting up DAYTIME lighting rig...")
    setup_cycles_engine(samples=samples)
    clean_lighting_rig()
    col_light = get_or_create_col("00_MANAGEMENT")
    
    # World Sky
    scene = bpy.context.scene
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    
    out = wnt.nodes.new("ShaderNodeOutputWorld")
    out.location = (600, 0)
    bg = wnt.nodes.new("ShaderNodeBackground")
    bg.location = (300, 0)
    sky = wnt.nodes.new("ShaderNodeTexSky")
    sky.location = (0, 0)
    try:
        sky.sky_type = "HOSEK_WILKIE"
        sky.turbidity = 3.2
    except Exception:
        pass
    bg.inputs["Strength"].default_value = 1.3
    wnt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    wnt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    
    # Key Sun Light
    sun_data = bpy.data.lights.new("Village_Dyn_Sun_Day", "SUN")
    sun_data.energy = 5.2
    sun_data.color = (1.0, 0.96, 0.88)
    sun_data.angle = math.radians(0.6) # Crisp architectural shadows
    sun_obj = bpy.data.objects.new("Village_Dyn_Sun_Day", sun_data)
    col_light.objects.link(sun_obj)
    # Sun from South-East at 38 deg elevation
    sun_obj.rotation_euler = (math.radians(52), 0, math.radians(160))
    
    # Soft fill light (sky bounce)
    fill_data = bpy.data.lights.new("Village_Dyn_Sun_Fill", "SUN")
    fill_data.energy = 0.8
    fill_data.color = (0.7, 0.82, 1.0)
    fill_obj = bpy.data.objects.new("Village_Dyn_Sun_Fill", fill_data)
    col_light.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(15), 0, math.radians(340))
    
    # Window glass in daytime mode (clear, reflective)
    import polish_materials
    polish_materials.set_windows_and_lanterns_state(night_glow=False)
    print("Daytime lighting configured.")

# ──────────────────────────────────────────────
# 2. SUNSET LIGHTING SETUP
# ──────────────────────────────────────────────
def set_sunset_lighting(samples=128):
    print("Setting up SUNSET lighting rig...")
    setup_cycles_engine(samples=samples)
    clean_lighting_rig()
    col_light = get_or_create_col("00_MANAGEMENT")
    
    scene = bpy.context.scene
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    
    out = wnt.nodes.new("ShaderNodeOutputWorld")
    out.location = (600, 0)
    bg = wnt.nodes.new("ShaderNodeBackground")
    bg.location = (300, 0)
    sky = wnt.nodes.new("ShaderNodeTexSky")
    sky.location = (0, 0)
    try:
        sky.sky_type = "HOSEK_WILKIE"
        sky.turbidity = 5.0
    except Exception:
        pass
    bg.inputs["Strength"].default_value = 0.95
    wnt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    wnt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    
    # Low Golden Hour Sun (16 deg elevation, azimuth 230 deg - casts rich golden sidelight down main avenue)
    sun_data = bpy.data.lights.new("Village_Dyn_Sun_Sunset", "SUN")
    sun_data.energy = 6.5
    sun_data.color = (1.0, 0.68, 0.32) # Warm golden sunset amber
    sun_data.angle = math.radians(1.2) # Soft realistic penumbra
    sun_obj = bpy.data.objects.new("Village_Dyn_Sun_Sunset", sun_data)
    col_light.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(74), 0, math.radians(230))
    
    # Opposite dusk ambient fill (deep twilight indigo sky)
    fill_data = bpy.data.lights.new("Village_Dyn_Dusk_Fill", "SUN")
    fill_data.energy = 0.95
    fill_data.color = (0.45, 0.58, 0.85)
    fill_obj = bpy.data.objects.new("Village_Dyn_Dusk_Fill", fill_data)
    col_light.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(35), 0, math.radians(50))
    
    # Early evening lanterns glowing
    import polish_materials
    polish_materials.set_windows_and_lanterns_state(night_glow=True, emission_mult=0.7)
    print("Sunset lighting configured.")

# ──────────────────────────────────────────────
# 3. NIGHTTIME LIGHTING SETUP
# ──────────────────────────────────────────────
def set_nighttime_lighting(samples=160):
    print("Setting up NIGHTTIME lighting rig...")
    setup_cycles_engine(samples=samples)
    clean_lighting_rig()
    col_light = get_or_create_col("00_MANAGEMENT")
    
    scene = bpy.context.scene
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    
    out = wnt.nodes.new("ShaderNodeOutputWorld")
    out.location = (600, 0)
    bg = wnt.nodes.new("ShaderNodeBackground")
    bg.location = (300, 0)
    bg.inputs["Color"].default_value = (0.003, 0.007, 0.022, 1.0) # Deep midnight indigo
    bg.inputs["Strength"].default_value = 0.18 # Moody night ambient
    wnt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    
    # Moonlight (soft cool silver-blue key light)
    moon_data = bpy.data.lights.new("Village_Dyn_Moon", "SUN")
    moon_data.energy = 0.28 # Balanced cool moonlight
    moon_data.color = (0.50, 0.68, 1.0)
    moon_data.angle = math.radians(2.5) # Soft moon shadow penumbra
    moon_obj = bpy.data.objects.new("Village_Dyn_Moon", moon_data)
    col_light.objects.link(moon_obj)
    moon_obj.rotation_euler = (math.radians(35), 0, math.radians(65))
    
    # Enable window and lantern night emission
    import polish_materials
    polish_materials.set_windows_and_lanterns_state(night_glow=True, emission_mult=2.0)
    
    # Add dynamic point lights around village landmarks for rich amber pools of light
    lamp_locations = [
        # Tavern entrance, porch, and interior windows
        ("Light_Tavern_Porch", (5.5, -18.0, 2.5), (1.0, 0.60, 0.18), 120.0, 0.35),
        ("Light_Tavern_Window_1", (1.5, -14.0, 3.2), (1.0, 0.52, 0.12), 140.0, 0.45),
        ("Light_Tavern_Upper_Win", (4.0, -14.0, 7.5), (1.0, 0.55, 0.15), 110.0, 0.45),
        
        # Main Cottage entrance and windows
        ("Light_Cottage_Porch", (0.0, -4.5, 2.2), (1.0, 0.62, 0.20), 90.0, 0.3),
        ("Light_Cottage_Window_L", (-2.2, -4.2, 2.4), (1.0, 0.55, 0.15), 100.0, 0.35),
        ("Light_Cottage_Window_R", (2.2, -4.2, 2.4), (1.0, 0.55, 0.15), 100.0, 0.35),
        
        # Market Square Well and Stalls
        ("Light_Market_Well", (0.0, -20.0, 2.5), (1.0, 0.65, 0.22), 110.0, 0.35),
        ("Light_Market_Stall_1", (-4.5, -22.0, 2.4), (1.0, 0.58, 0.18), 75.0, 0.25),
        ("Light_Market_Stall_2", (4.5, -22.0, 2.4), (1.0, 0.58, 0.18), 75.0, 0.25),
        
        # Main Street Lampposts
        ("Light_Street_Lamp_1", (2.5, -34.0, 2.8), (1.0, 0.62, 0.20), 95.0, 0.3),
        ("Light_Street_Lamp_2", (-2.5, -46.0, 2.8), (1.0, 0.62, 0.20), 95.0, 0.3),
        ("Light_South_Gate", (0.0, -56.0, 3.5), (1.0, 0.55, 0.15), 120.0, 0.4),
        
        # Blacksmith Forge Glow
        ("Light_Blacksmith_Forge", (14.5, -7.0, 1.8), (1.0, 0.28, 0.04), 180.0, 0.55),
        
        # Church Windows & Bell Tower
        ("Light_Church_Nave", (-10.0, 18.0, 4.0), (1.0, 0.68, 0.28), 150.0, 0.6),
        ("Light_Church_Tower", (-10.0, 12.0, 14.5), (1.0, 0.62, 0.22), 90.0, 0.4),
        
        # Stone Bridge Lanterns
        ("Light_Bridge_South", (6.0, 17.5, 2.0), (1.0, 0.62, 0.22), 85.0, 0.3),
        ("Light_Bridge_North", (6.0, 26.5, 2.0), (1.0, 0.62, 0.22), 85.0, 0.3),
        
        # Castle Tower Torch
        ("Light_Castle_Brazier", (-26.0, -14.0, 17.0), (1.0, 0.42, 0.08), 180.0, 0.5),
    ]
    
    for l_name, loc, color, energy, radius in lamp_locations:
        p_data = bpy.data.lights.new(f"Village_Dyn_{l_name}", "POINT")
        p_data.energy = energy
        p_data.color = color
        p_data.shadow_soft_size = radius
        p_obj = bpy.data.objects.new(f"Village_Dyn_{l_name}", p_data)
        col_light.objects.link(p_obj)
        p_obj.location = loc
        
    print(f"Nighttime lighting configured with {len(lamp_locations)} lantern point lights.")
