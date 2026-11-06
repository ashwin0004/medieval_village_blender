"""
build_polish_village.py
=======================
Master Orchestrator for Village Polish Pass:
  1. Applies PBR material upgrades (terrain, foliage, water, stone, wood, plaster, roofs)
  2. Resolves layout conflicts (Market square to (0,-20), organic branching roads)
  3. Builds environmental props (tavern patio, market carts/sacks, cottage garden/firewood,
     blacksmith hearth/anvil, churchyard gravestones/cross, castle rubble, street lamps)
  4. Excludes stage showroom studio elements from the village view layer
  5. Configures 7 cinematic cameras
  6. Renders the 7 requested views under optimal lighting (Daytime, Sunset, Nighttime)
  7. Saves master blend & copies all renders to designated folders
"""

import bpy
import sys
import os
import shutil
import importlib

SCRIPTS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
MASTER_BLEND = r"c:\Users\ashwi\Documents\Medieval_Village_Project\Medieval_Village.blend"
WORLD_BLEND = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\world\village_world.blend"
BACKUP_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\backups"
RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders"
POLISH_RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\polish"
ARTIFACT_DIR = r"C:\Users\ashwi\.gemini\antigravity\brain\a0a9786d-d6d3-4462-aac6-e6fdc3ebcb84\renders"

os.makedirs(POLISH_RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import polish_materials
importlib.reload(polish_materials)

import polish_details
importlib.reload(polish_details)

import polish_cameras
importlib.reload(polish_cameras)

import lighting_manager
importlib.reload(lighting_manager)

def hide_showroom_studios():
    """Excludes Stage 2/3 showroom showcase collections from the village view layer."""
    vl = bpy.context.view_layer
    def set_exclude(lc, name, val):
        if lc.name == name:
            lc.exclude = val
        for ch in lc.children:
            set_exclude(ch, name, val)

    set_exclude(vl.layer_collection, "02_ARCHITECTURE_MODULAR", True)
    set_exclude(vl.layer_collection, "04_PROPS_FURNITURE/01_Containers", True)
    set_exclude(vl.layer_collection, "04_PROPS_FURNITURE/02_Kitchen_Tools", True)
    set_exclude(vl.layer_collection, "04_PROPS_FURNITURE/03_Furniture", True)
    set_exclude(vl.layer_collection, "04_PROPS_FURNITURE/04_Lighting_Street", True)

    for floor_name in ["Props_Studio_Floor", "Showcase_Studio_Floor"]:
        f_obj = bpy.data.objects.get(floor_name)
        if f_obj:
            f_obj.hide_render = True

def execute_polish_pipeline():
    print("==================================================")
    print("   MEDIEVAL VILLAGE POLISH PIPELINE: START")
    print("==================================================")
    
    # 1. Materials Upgrade
    polish_materials.apply_all_material_upgrades()
    
    # 2. Environmental Dressing & Layout Polish
    polish_details.apply_all_detail_polishing()
    
    # 3. Clean View Layer (hide studio showroom floors)
    hide_showroom_studios()
    
    # 4. Setup Cameras
    cameras = polish_cameras.setup_all_polish_cameras()
    
    # 5. Save World Blend before rendering
    bpy.ops.wm.save_as_mainfile(filepath=WORLD_BLEND)
    print(f"Saved state to world blend: {WORLD_BLEND}")

    # 6. Render Schedule with separate Lighting Setups
    # (Camera Name, Lighting Rig Function, Output Base Name)
    render_tasks = [
        ("Cam_Polish_Aerial", lighting_manager.set_daytime_lighting, "Aerial_Overview"),
        ("Cam_Polish_MainStreet", lighting_manager.set_daytime_lighting, "Main_Street"),
        ("Cam_Polish_Cottage", lighting_manager.set_daytime_lighting, "Main_Cottage"),
        ("Cam_Polish_Bridge", lighting_manager.set_daytime_lighting, "River_and_Stone_Bridge"),
        ("Cam_Polish_Tavern", lighting_manager.set_sunset_lighting, "Tavern"),
        ("Cam_Polish_ChurchCastle", lighting_manager.set_sunset_lighting, "Church_and_Castle"),
        ("Cam_Polish_Night", lighting_manager.set_nighttime_lighting, "Nighttime_Village"),
    ]
    
    rendered_files = []
    scene = bpy.context.scene
    
    for cam_name, lighting_func, output_name in render_tasks:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"ERROR: Camera {cam_name} not found, skipping!")
            continue
            
        print(f"\n>>> Preparing render: {output_name} ({cam_name})")
        # Apply specific lighting rig
        lighting_func()
        scene.camera = cam_obj
        
        # Paths
        primary_path = os.path.join(RENDERS_DIR, f"{output_name}.png")
        sub_path = os.path.join(POLISH_RENDERS_DIR, f"{cam_name}.png")
        art_path = os.path.join(ARTIFACT_DIR, f"{output_name}.png")
        
        scene.render.filepath = primary_path
        bpy.ops.render.render(write_still=True)
        
        # Copy to subfolder and artifact directory
        shutil.copy2(primary_path, sub_path)
        shutil.copy2(primary_path, art_path)
        
        sz_kb = os.path.getsize(primary_path) // 1024
        print(f"Rendered {output_name}: {sz_kb} KB -> {primary_path}")
        rendered_files.append((output_name, primary_path, sz_kb))
        
    # 7. Save Master Blend & Backup
    bpy.ops.wm.save_as_mainfile(filepath=MASTER_BLEND)
    print(f"Saved master blend: {MASTER_BLEND}")
    backup_file = os.path.join(BACKUP_DIR, "village_polish_v01.blend")
    shutil.copy2(MASTER_BLEND, backup_file)
    print(f"Backup created: {backup_file}")
    
    print("==================================================")
    print(f"   MEDIEVAL VILLAGE POLISH COMPLETE: {len(rendered_files)} renders generated.")
    print("==================================================")
    return rendered_files

if __name__ == "__main__":
    execute_polish_pipeline()
