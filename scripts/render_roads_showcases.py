"""
render_roads_showcases.py
=========================
Renders high-resolution 1080p showcase views of the realistic Village Road Network:
  1. Roads_Main_Avenue (Crowned cobblestone road, curbs, roadside rocks, street lamps)
  2. Roads_Cobble_Macro (Macro low-angle view of rounded river cobbles & crevice grass - Ref 3)
  3. Roads_Market_Square (Overview of cobblestone market plaza, stalls, puddles, wagons - Ref 2, 4)
  4. Roads_Castle_Ascent_Steps (Dirt path & stone steps climbing to the stone watchtower)
  5. Roads_Aerial_Network (High aerial view showing all road connections across the village)
Saves renders to renders/roads/ and copies to artifacts.
"""

import bpy
import os
import shutil
import math
import sys
from mathutils import Vector

SCRIPTS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

MASTER_BLEND = r"c:\Users\ashwi\Documents\Medieval_Village_Project\Medieval_Village.blend"
RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\roads"
ARTIFACT_DIR = r"C:\Users\ashwi\.gemini\antigravity\brain\a0a9786d-d6d3-4462-aac6-e6fdc3ebcb84\renders"

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

import lighting_manager

def get_or_create_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def make_tracked_cam(name, loc, target, lens=35.0, col=None):
    if name in bpy.data.objects:
        cam_obj = bpy.data.objects[name]
    else:
        cam_data = bpy.data.cameras.new(name)
        cam_obj = bpy.data.objects.new(name, cam_data)
        if col:
            col.objects.link(cam_obj)
        else:
            bpy.context.scene.collection.objects.link(cam_obj)
            
    cam_obj.data.lens = lens
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 1500.0
    cam_obj.location = Vector(loc)
    
    direction = Vector(target) - Vector(loc)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    return cam_obj

def setup_roads_cameras():
    col = get_or_create_col("00_MANAGEMENT")
    cams = {}
    
    # 1. Main Street Avenue (Looking north from South Gate up the cobblestone road)
    cams["Cam_Roads_Main_Avenue"] = make_tracked_cam(
        "Cam_Roads_Main_Avenue",
        loc=(0.0, -48.0, 1.8),
        target=(0.0, -18.0, 2.2),
        lens=28.0,
        col=col
    )
    
    # 2. Cobblestone Macro Close-up (Low-angle matching Ref Image 3)
    cams["Cam_Roads_Cobble_Macro"] = make_tracked_cam(
        "Cam_Roads_Cobble_Macro",
        loc=(1.2, -26.5, 0.45),
        target=(1.2, -22.0, 0.65),
        lens=50.0,
        col=col
    )
    
    # 3. Market Square Paving & Puddles (Looking over the plaza - Ref 2, 4)
    cams["Cam_Roads_Market_Square"] = make_tracked_cam(
        "Cam_Roads_Market_Square",
        loc=(-8.5, -28.0, 4.8),
        target=(1.0, -18.0, 1.5),
        lens=32.0,
        col=col
    )
    
    # 4. Castle Watchtower Ascent & Stone Steps (Dirt path climbing with stone steps)
    cams["Cam_Roads_Castle_Steps"] = make_tracked_cam(
        "Cam_Roads_Castle_Steps",
        loc=(-12.0, -22.5, 2.8),
        target=(-22.0, -16.0, 2.5),
        lens=36.0,
        col=col
    )
    
    # 5. Aerial View of Entire Road Network
    cams["Cam_Roads_Aerial"] = make_tracked_cam(
        "Cam_Roads_Aerial",
        loc=(0.0, -16.0, 95.0),
        target=(0.0, 4.0, 1.0),
        lens=26.0,
        col=col
    )
    
    return cams

def render_roads_showcases():
    print("==================================================")
    print("   RENDERING ROADS & PATHS SHOWCASE VIEWS")
    print("==================================================")
    cams = setup_roads_cameras()
    scene = bpy.context.scene
    
    render_schedule = [
        ("Cam_Roads_Main_Avenue", lighting_manager.set_daytime_lighting, "Roads_Main_Cobblestone_Avenue"),
        ("Cam_Roads_Cobble_Macro", lighting_manager.set_sunset_lighting, "Roads_Cobblestone_Macro_Ref3"),
        ("Cam_Roads_Market_Square", lighting_manager.set_daytime_lighting, "Roads_Market_Plaza_Paving"),
        ("Cam_Roads_Castle_Steps", lighting_manager.set_sunset_lighting, "Roads_Castle_Ascent_Steps"),
        ("Cam_Roads_Aerial", lighting_manager.set_daytime_lighting, "Roads_Village_Network_Aerial"),
    ]
    
    results = []
    for cam_name, light_func, out_name in render_schedule:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Skipping {cam_name}")
            continue
            
        print(f"\n>>> Rendering {out_name} via {cam_name}...")
        light_func(samples=96)
        scene.camera = cam_obj
        
        out_path = os.path.join(RENDERS_DIR, f"{out_name}.png")
        art_path = os.path.join(ARTIFACT_DIR, f"{out_name}.png")
        
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        
        shutil.copy2(out_path, art_path)
        sz_kb = os.path.getsize(out_path) // 1024
        print(f"Rendered {out_name}: {sz_kb} KB")
        results.append((out_name, out_path, sz_kb))
        
    bpy.ops.wm.save_as_mainfile(filepath=MASTER_BLEND)
    print(f"Saved master blend: {MASTER_BLEND}")
    return results

if __name__ == "__main__":
    render_roads_showcases()

