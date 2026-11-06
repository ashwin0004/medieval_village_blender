"""
build_village_world.py
======================
Orchestrator: loads all modules, builds the village world,
sets up cameras, saves files and renders all village views.
"""

import bpy
import sys
import os
import importlib

SCRIPTS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
ASSETS_DIR  = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\world"
BACKUP_DIR  = r"c:\Users\ashwi\Documents\Medieval_Village_Project\backups"
RENDER_DIR  = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\village_world"
MASTER_BLEND = r"c:\Users\ashwi\Documents\Medieval_Village_Project\Medieval_Village.blend"

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# ── 1. Helper functions ───────────────────────
def ensure_grass_material():
    name = "M_Grass_Green"
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.08, 0.28, 0.06, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
    return mat

def ensure_cobble_material():
    name = "M_Cobblestone_Road"
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.voronoi_dimensions = "2D"
    vor.inputs["Scale"].default_value = 6.0
    
    # Modern Blender 4/5 ShaderNodeMix
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (0.25, 0.22, 0.18, 1.0)
    mix.inputs[7].default_value = (0.18, 0.16, 0.14, 1.0)
    nt.links.new(vor.outputs["Distance"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.88
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def run_build_village_world():
    # ── Load modules ──────────────────────────────
    import materials_library
    importlib.reload(materials_library)
    
    import village_world
    importlib.reload(village_world)
    
    import village_cameras
    importlib.reload(village_cameras)
    
    # ── 1. Ensure PBR materials ───────────────────
    print("Ensuring PBR materials...")
    materials_library.create_all_materials()
    ensure_grass_material()
    ensure_cobble_material()
    
    # ── 3. Build village environment ──────────────
    print("Building village environment...")
    village_world.build_village_environment()
    
    # ── 4. Setup cameras ──────────────────────────
    print("Setting up village cameras...")
    village_cameras.setup_village_cameras()
    
    # ── 5. Configure render settings ─────────────
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 96
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
    except Exception as e:
        print(f"GPU setup note: {e}")
    
    # World / Lighting
    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    bg_node = wnt.nodes.new("ShaderNodeBackground")
    sky_node = wnt.nodes.new("ShaderNodeTexSky")
    sky_node.sky_type = "NISHITA"
    sky_node.sun_elevation = math.radians(35)
    sky_node.sun_rotation = math.radians(200)
    sky_node.air_density = 1.0
    sky_node.dust_density = 0.5
    out_node = wnt.nodes.new("ShaderNodeOutputWorld")
    wnt.links.new(sky_node.outputs["Color"], bg_node.inputs["Color"])
    wnt.links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])
    bg_node.inputs["Strength"].default_value = 1.2
    
    # Sun lamp
    sun_name = "Sun_Daylight"
    if sun_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[sun_name], do_unlink=True)
    sun_data = bpy.data.lights.new(sun_name, "SUN")
    sun_data.energy = 4.0
    sun_data.angle = math.radians(0.5)
    sun_obj = bpy.data.objects.new(sun_name, sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(45), 0, math.radians(200))
    
    # ── 6. Save world blend ───────────────────────
    world_blend = os.path.join(ASSETS_DIR, "village_world.blend")
    bpy.ops.wm.save_as_mainfile(filepath=world_blend)
    print(f"Saved world blend: {world_blend}")
    
    # ── 7. Render all camera views ────────────────
    cam_views = [
        ("Cam_Village_Aerial",  "aerial_overview"),
        ("Cam_Village_Beauty",  "beauty_3quarter"),
        ("Cam_Village_Market",  "market_ground"),
        ("Cam_Village_Road",    "road_ground"),
        ("Cam_Village_Bridge",  "bridge_river"),
        ("Cam_Village_Castle",  "castle_view"),
    ]
    
    for cam_name, view_name in cam_views:
        cam_obj = bpy.data.objects.get(cam_name)
        if cam_obj is None:
            print(f"WARNING: Camera {cam_name} not found, skipping.")
            continue
        scene.camera = cam_obj
        render_path = os.path.join(RENDER_DIR, f"{cam_name}.png")
        scene.render.filepath = render_path
        bpy.ops.render.render(write_still=True)
        print(f"Rendered: {render_path}")
    
    # ── 8. Save master blend ──────────────────────
    bpy.ops.wm.save_as_mainfile(filepath=MASTER_BLEND)
    print(f"Saved master blend: {MASTER_BLEND}")
    
    # ── 9. Backup ─────────────────────────────────
    backup_path = os.path.join(BACKUP_DIR, "village_world_v01.blend")
    shutil.copy2(world_blend, backup_path)
    print(f"Backup: {backup_path}")
    print("=== BUILD VILLAGE WORLD: ALL DONE ===")

if __name__ == "__main__":
    run_build_village_world()

