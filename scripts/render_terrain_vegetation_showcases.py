"""
render_terrain_vegetation_showcases.py
======================================
Renders high-resolution 1080p showcase views of the Upgraded Terrain & Vegetation:
  1. Terrain_Alpine_Valley_Aerial (Panoramic valley overview with distant snow-capped mountains, rolling hills, and forests - Ref 1 & 2)
  2. Terrain_River_Valley_Vista (River canyon view with boulders, water reflections, stone bridge, and towering peaks - Ref 1 & 3)
  3. Nature_Vegetation_Wildflowers_Macro (Close-up of red poppies, yellow buttercups, mossy boulders, and grass - Ref 5)
  4. Terrain_Rolling_Hills_Sunset (Sunset across rolling hills, Scots pines, Great Village Oak, and horizon - Ref 2 & 4)
"""

import bpy
import os
import shutil
import math
from mathutils import Vector
import sys

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import lighting_manager

MASTER_BLEND = r"c:\Users\ashwi\Documents\Medieval_Village_Project\Medieval_Village.blend"
RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\nature"
ARTIFACT_DIR = r"C:\Users\ashwi\.gemini\antigravity\brain\a0a9786d-d6d3-4462-aac6-e6fdc3ebcb84\renders"

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

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
    cam_obj.data.clip_start = 0.2
    cam_obj.data.clip_end = 2500.0
    cam_obj.location = Vector(loc)

    direction = Vector(target) - Vector(loc)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    return cam_obj

def setup_nature_cameras():
    col = get_or_create_col("00_MANAGEMENT")
    cams = {}

    # 1. Alpine Valley Aerial Overview (Ref 1, 2)
    cams["Cam_Alpine_Valley_Aerial"] = make_tracked_cam(
        "Cam_Alpine_Valley_Aerial",
        loc=(-30.0, -58.0, 26.0),
        target=(0.0, 5.0, 5.0),
        lens=25.0,
        col=col
    )

    # 2. River Valley Vista (Ref 1, 3)
    cams["Cam_River_Valley_Vista"] = make_tracked_cam(
        "Cam_River_Valley_Vista",
        loc=(-6.0, 12.0, 2.8),
        target=(6.0, 24.0, 3.5),
        lens=32.0,
        col=col
    )

    # 3. Nature & Wildflowers Macro Close-Up (Ref 5)
    cams["Cam_Wildflowers_Macro"] = make_tracked_cam(
        "Cam_Wildflowers_Macro",
        loc=(10.2, -4.6, 0.85),
        target=(11.8, -2.8, 0.55),
        lens=48.0,
        col=col
    )

    # 4. Rolling Hills Sunset (Ref 2, 4)
    cams["Cam_Rolling_Hills_Sunset"] = make_tracked_cam(
        "Cam_Rolling_Hills_Sunset",
        loc=(24.0, -48.0, 16.0),
        target=(-5.0, -10.0, 2.5),
        lens=28.0,
        col=col
    )

    return cams

def render_nature_showcases():
    print("==================================================")
    print("   RENDERING TERRAIN & VEGETATION SHOWCASES")
    print("==================================================")
    cams = setup_nature_cameras()
    scene = bpy.context.scene

    for cname in ["06_ENVIRONMENT_NATURE", "99_TERRAIN_ATMOSPHERE", "03_VILLAGE_STRUCTURES", "Market_Dressing"]:
        c = bpy.data.collections.get(cname)
        if c:
            for vl in scene.view_layers:
                lc = vl.layer_collection.children.get(cname)
                if lc:
                    lc.exclude = False

    render_schedule = [
        ("Cam_Alpine_Valley_Aerial", lighting_manager.set_daytime_lighting, "Terrain_Alpine_Valley_Aerial"),
        ("Cam_River_Valley_Vista", lighting_manager.set_daytime_lighting, "Terrain_River_Valley_Vista"),
        ("Cam_Wildflowers_Macro", lighting_manager.set_daytime_lighting, "Nature_Vegetation_Wildflowers_Macro"),
        ("Cam_Rolling_Hills_Sunset", lighting_manager.set_sunset_lighting, "Terrain_Rolling_Hills_Sunset"),
    ]

    results = []
    for cam_name, light_func, out_name in render_schedule:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Skipping {cam_name}")
            continue

        print(f"\n>>> Setting up {out_name} via {cam_name}...")
        light_func(samples=96)

        scene.camera = cam_obj
        out_path = os.path.join(RENDERS_DIR, f"{out_name}.png")
        art_path = os.path.join(ARTIFACT_DIR, f"{out_name}.png")

        scene.render.filepath = out_path
        print(f"Starting render to {out_path}...")
        bpy.ops.render.render(write_still=True)

        shutil.copy2(out_path, art_path)
        sz_kb = os.path.getsize(out_path) // 1024
        print(f"Rendered {out_name}: {sz_kb} KB")
        results.append((out_name, out_path, sz_kb))

    print("==================================================")
    print("ALL 4 TERRAIN & VEGETATION SHOWCASE RENDERS COMPLETE!")
    for name, path, sz in results:
        print(f" - {name}: {sz} KB -> {path}")
    print("==================================================")

if __name__ == "__main__":
    render_nature_showcases()
