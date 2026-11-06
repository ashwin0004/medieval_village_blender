"""
render_marketplace_showcases.py
===============================
Renders high-resolution 1080p showcase views of the Central Medieval Marketplace:
  1. Market_Square_Overview (Elevated wide overview of the full vibrant market square, stalls, wagon, and well)
  2. Market_Well_Hero (Hero eye-level view of the detailed stone well, windlass, rope, bucket, and basin)
  3. Market_Stalls_Produce_Avenue (Ground-level view of produce crates, apples, cabbages, bread, cheese, sacks)
  4. Market_Night_Atmosphere (Atmospheric nighttime render with glowing lanterns and cobblestone reflections)
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
RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\marketplace"
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
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 1500.0
    cam_obj.location = Vector(loc)

    direction = Vector(target) - Vector(loc)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    return cam_obj

def setup_marketplace_cameras():
    col = get_or_create_col("00_MANAGEMENT")
    cams = {}

    # Market center is at (0.0, -19.5)
    # 1. Elevated Overview: High angle showing full square, 4 stalls, wagon, carts, well, and tavern
    cams["Cam_Market_Overview"] = make_tracked_cam(
        "Cam_Market_Overview",
        loc=(4.2, -33.5, 9.5),
        target=(0.0, -19.5, 1.2),
        lens=25.0,
        col=col
    )

    # 2. Hero Well Close-Up: Perfectly framed view of the stone well from ground apron to roof ridge
    cams["Cam_Market_Well"] = make_tracked_cam(
        "Cam_Market_Well",
        loc=(-3.5, -24.8, 2.2),
        target=(0.0, -19.5, 1.9),
        lens=35.0,
        col=col
    )

    # 3. Produce Avenue & Stalls Ground View: Looking at Greengrocer & Baker stalls with produce crates & bread
    cams["Cam_Market_Avenue"] = make_tracked_cam(
        "Cam_Market_Avenue",
        loc=(-1.8, -26.2, 1.8),
        target=(-4.6, -17.5, 1.3),
        lens=32.0,
        col=col
    )

    # 4. Night Atmosphere View: Across the square showing lanterns illuminating cobblestones and stalls
    cams["Cam_Market_Night"] = make_tracked_cam(
        "Cam_Market_Night",
        loc=(3.2, -30.0, 4.2),
        target=(0.0, -19.5, 1.5),
        lens=28.0,
        col=col
    )

    return cams

def render_marketplace_showcases():
    print("==================================================")
    print("   RENDERING CENTRAL MARKETPLACE SHOWCASES")
    print("==================================================")
    cams = setup_marketplace_cameras()
    scene = bpy.context.scene

    for cname in ["03_VILLAGE_STRUCTURES", "Market_Dressing"]:
        c = bpy.data.collections.get(cname)
        if c:
            for vl in scene.view_layers:
                lc = vl.layer_collection.children.get(cname)
                if lc:
                    lc.exclude = False

    render_schedule = [
        ("Cam_Market_Overview", lighting_manager.set_daytime_lighting, "Market_Square_Overview"),
        ("Cam_Market_Well", lighting_manager.set_daytime_lighting, "Market_Well_Hero"),
        ("Cam_Market_Avenue", lighting_manager.set_sunset_lighting, "Market_Stalls_Produce_Avenue"),
        ("Cam_Market_Night", lighting_manager.set_nighttime_lighting, "Market_Night_Atmosphere"),
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
    print("ALL 4 MARKETPLACE SHOWCASE RENDERS COMPLETE!")
    for name, path, sz in results:
        print(f" - {name}: {sz} KB -> {path}")
    print("==================================================")

if __name__ == "__main__":
    render_marketplace_showcases()
