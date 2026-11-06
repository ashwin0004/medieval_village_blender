"""
render_building_showcases.py
============================
Sets up dedicated cinematic cameras for each newly upgraded building:
  - Tavern (2-story overhanging jetty, balcony, individual scalloped tiles)
  - Cottage 2 (Weaver's cottage - Ref 2: fieldstone base, logs, crossed apex finials)
  - Cottage 3 (Baker's house - Ref 1: arched stone door, half-timber upper, dormer)
  - Church (Gothic portal, stone buttresses, lancet windows, 16m bell tower)
  - Blacksmith (Open lean-to shed, forge chimney, heavy timber framing)
  - Barn (Sweeping roof, massive double wagon doors, hayloft hoist beam)
  - Castle (Machicolated watchtower, arrow slits, ruined rampart walls)
  - Aerial Overview (High angle capturing all upgraded architecture)
  - Main Street (Eye-level avenue past the new buildings)
  - Nighttime Village (Atmospheric night illumination)
Renders high-res 1080p images into renders/upgraded_buildings/ and copies to artifacts.
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
RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\upgraded_buildings"
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

def setup_building_cameras():
    col = get_or_create_col("00_MANAGEMENT")
    cams = {}
    
    # 1. Tavern Showcase (Overhang jetty, upper balcony, individual tiles)
    cams["Cam_Showcase_Tavern"] = make_tracked_cam(
        "Cam_Showcase_Tavern",
        loc=(8.5, -24.5, 3.8),
        target=(4.0, -14.0, 4.2),
        lens=34.0,
        col=col
    )
    
    # 2. Cottage 2 (Weaver - Ref Image 2: fieldstone base, logs, crossed apex bargeboards)
    # Cottage 2 at (-8.0, -8.0), rot=20 deg
    cams["Cam_Showcase_Cottage2"] = make_tracked_cam(
        "Cam_Showcase_Cottage2",
        loc=(-3.5, -15.5, 2.6),
        target=(-8.0, -8.0, 3.2),
        lens=36.0,
        col=col
    )
    
    # 3. Cottage 3 (Baker - Ref Image 1: stone arch entrance, half-timber, dormer)
    # Cottage 3 at (10.0, 10.0), rot=-25 deg
    cams["Cam_Showcase_Cottage3"] = make_tracked_cam(
        "Cam_Showcase_Cottage3",
        loc=(5.2, 4.2, 2.8),
        target=(10.0, 10.0, 3.4),
        lens=36.0,
        col=col
    )
    
    # 4. Church & Bell Tower (Gothic portal, buttresses, belfry, spire)
    cams["Cam_Showcase_Church"] = make_tracked_cam(
        "Cam_Showcase_Church",
        loc=(-4.0, 6.0, 4.5),
        target=(-10.0, 16.0, 8.5),
        lens=28.0,
        col=col
    )
    
    # 5. Blacksmith & Lean-to Workshop
    cams["Cam_Showcase_Blacksmith"] = make_tracked_cam(
        "Cam_Showcase_Blacksmith",
        loc=(9.0, -15.0, 3.0),
        target=(15.5, -7.0, 2.8),
        lens=35.0,
        col=col
    )
    
    # 6. Tithe Barn (Sweeping roof, double wagon doors, hayloft hoist beam)
    cams["Cam_Showcase_Barn"] = make_tracked_cam(
        "Cam_Showcase_Barn",
        loc=(18.0, 8.5, 3.2),
        target=(24.0, 16.0, 4.5),
        lens=32.0,
        col=col
    )
    
    # 7. Castle Watchtower & Ramparts
    cams["Cam_Showcase_Castle"] = make_tracked_cam(
        "Cam_Showcase_Castle",
        loc=(-16.0, -26.0, 7.5),
        target=(-26.0, -14.0, 10.0),
        lens=28.0,
        col=col
    )
    
    # 8. Aerial Overview (Capturing all upgraded buildings in village context)
    cams["Cam_Showcase_Aerial"] = make_tracked_cam(
        "Cam_Showcase_Aerial",
        loc=(0.0, -16.0, 92.0),
        target=(0.0, 4.0, 2.0),
        lens=26.0,
        col=col
    )

    # 9. Main Street Avenue
    cams["Cam_Showcase_Street"] = make_tracked_cam(
        "Cam_Showcase_Street",
        loc=(0.0, -48.0, 1.7),
        target=(0.0, -16.0, 2.2),
        lens=25.0,
        col=col
    )

    # 10. Nighttime Village Overview
    cams["Cam_Showcase_Night"] = make_tracked_cam(
        "Cam_Showcase_Night",
        loc=(44.0, -44.0, 34.0),
        target=(0.0, -10.0, 3.5),
        lens=32.0,
        col=col
    )
    
    return cams

def render_all_showcases():
    print("==================================================")
    print("   RENDERING UPGRADED BUILDING SHOWCASES")
    print("==================================================")
    cams = setup_building_cameras()
    scene = bpy.context.scene
    
    render_schedule = [
        ("Cam_Showcase_Tavern", lighting_manager.set_sunset_lighting, "Upgraded_Tavern"),
        ("Cam_Showcase_Cottage2", lighting_manager.set_daytime_lighting, "Upgraded_Cottage2_Weaver"),
        ("Cam_Showcase_Cottage3", lighting_manager.set_daytime_lighting, "Upgraded_Cottage3_Baker"),
        ("Cam_Showcase_Church", lighting_manager.set_sunset_lighting, "Upgraded_Church_Chapel"),
        ("Cam_Showcase_Blacksmith", lighting_manager.set_daytime_lighting, "Upgraded_Blacksmith"),
        ("Cam_Showcase_Barn", lighting_manager.set_daytime_lighting, "Upgraded_Tithe_Barn"),
        ("Cam_Showcase_Castle", lighting_manager.set_sunset_lighting, "Upgraded_Castle_Watchtower"),
        ("Cam_Showcase_Aerial", lighting_manager.set_daytime_lighting, "Upgraded_Village_Aerial"),
        ("Cam_Showcase_Street", lighting_manager.set_daytime_lighting, "Upgraded_Main_Street"),
        ("Cam_Showcase_Night", lighting_manager.set_nighttime_lighting, "Upgraded_Village_Night"),
    ]
    
    results = []
    for cam_name, light_func, out_name in render_schedule:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Skipping {cam_name} (not found)")
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
        
    # Save master blend file
    bpy.ops.wm.save_as_mainfile(filepath=MASTER_BLEND)
    print(f"Saved master blend: {MASTER_BLEND}")
    return results

if __name__ == "__main__":
    render_all_showcases()

