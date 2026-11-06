"""
render_watchtower_showcases.py
==============================
Renders high-resolution 1080p showcase views of the upgraded Medieval Stone Watchtower:
  1. Watchtower_Full_Beauty (Dramatic ground-up perspective: battered base, stone shaft,
     exterior wooden staircase, observation hoarding, and conical roof)
  2. Watchtower_Stairs_CloseUp (Detailed view of the exterior wooden stairs, landings,
     sally port entrance, and wrought-iron lanterns)
  3. Watchtower_Observation_Deck (Close-up of the cantilevered timber hoarding,
     defensive arrow loops, slate roof, and weather vane)
  4. Watchtower_Night_Illumination (Atmospheric night render with warm glowing lanterns)
Saves renders to renders/watchtower/ and copies to artifacts.
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
RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\watchtower"
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

def setup_watchtower_cameras():
    col = get_or_create_col("00_MANAGEMENT")
    cams = {}
    
    # Tower center is at (-26.0, -14.0, 0.0)
    # 1. Full Beauty Shot: Ground-up 3/4 view from South-East (along castle approach path)
    cams["Cam_Watchtower_Full"] = make_tracked_cam(
        "Cam_Watchtower_Full",
        loc=(-15.0, -26.0, 4.5),
        target=(-25.5, -14.0, 10.5),
        lens=30.0,
        col=col
    )
    
    # 2. Stairs & Sally Port Close-Up
    cams["Cam_Watchtower_Stairs"] = make_tracked_cam(
        "Cam_Watchtower_Stairs",
        loc=(-18.5, -20.5, 3.8),
        target=(-23.5, -15.5, 4.5),
        lens=42.0,
        col=col
    )
    
    # 3. Observation Platform & Hoarding Close-Up (Elevated angle looking up at hoarding)
    cams["Cam_Watchtower_Hoarding"] = make_tracked_cam(
        "Cam_Watchtower_Hoarding",
        loc=(-17.0, -22.0, 11.5),
        target=(-25.5, -14.0, 17.0),
        lens=45.0,
        col=col
    )
    
    # 4. Nighttime Watchtower Shot
    cams["Cam_Watchtower_Night"] = make_tracked_cam(
        "Cam_Watchtower_Night",
        loc=(-15.5, -25.5, 5.0),
        target=(-25.5, -14.0, 10.0),
        lens=32.0,
        col=col
    )
    
    return cams

def render_watchtower_showcases():
    print("==================================================")
    print("   RENDERING WATCHTOWER SHOWCASE VIEWS")
    print("==================================================")
    cams = setup_watchtower_cameras()
    scene = bpy.context.scene
    
    # Add dynamic point light for watchtower lanterns in night mode
    col_light = get_or_create_col("00_MANAGEMENT")
    
    render_schedule = [
        ("Cam_Watchtower_Full", lighting_manager.set_sunset_lighting, "Watchtower_Full_Beauty"),
        ("Cam_Watchtower_Stairs", lighting_manager.set_daytime_lighting, "Watchtower_Stairs_CloseUp"),
        ("Cam_Watchtower_Hoarding", lighting_manager.set_sunset_lighting, "Watchtower_Observation_Hoarding"),
        ("Cam_Watchtower_Night", lighting_manager.set_nighttime_lighting, "Watchtower_Night_Illumination"),
    ]
    
    results = []
    for cam_name, light_func, out_name in render_schedule:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Skipping {cam_name}")
            continue
            
        print(f"\n>>> Rendering {out_name} via {cam_name}...")
        light_func(samples=96)
        
        # If night, add point light near watchtower stairs and hoarding
        if "Night" in out_name:
            lamp_p = bpy.data.lights.new("Village_Dyn_Watchtower_Lamp", "POINT")
            lamp_p.energy = 95.0
            lamp_p.color = (1.0, 0.60, 0.20)
            lamp_p.shadow_soft_size = 0.25
            l_obj = bpy.data.objects.new("Village_Dyn_Watchtower_Lamp", lamp_p)
            col_light.objects.link(l_obj)
            l_obj.location = Vector((-21.8, -14.6, 4.8))
            
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
    render_watchtower_showcases()

