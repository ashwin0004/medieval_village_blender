"""
render_environmental_showcases.py
=================================
Renders 4 high-resolution 1080p showcase views of the Small Environmental Details & Props:
  1. Props_Street_Life_Hero (Ref 2 & 4: Main street life with flower boxes, bracket lanterns, bunting, cottages)
  2. Props_Wagon_Market_Hero (Ref 3: Loaded 4-wheeled cargo wagon with spoked wheels, barrels, tarpaulin, lantern)
  3. Props_Table_StillLife (Ref 1: Market work table with barrels, crates, sacks, baskets, pottery jugs, bucket, rope)
  4. Props_Village_NoticeBoard_Entrance (Ref 5: South entrance notice board, pinned notices, fences, gate, lantern)
"""

import bpy
import os
import shutil
import sys

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import lighting_manager

RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders"
ARTIFACT_DIR = r"C:\Users\ashwi\.gemini\antigravity\brain\a0a9786d-d6d3-4462-aac6-e6fdc3ebcb84\renders"

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def render_env_view(cam_name, out_filename, light_fn, samples=72):
    scene = bpy.context.scene
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        print(f"Error: Camera {cam_name} not found!")
        return None
        
    print(f"\n==========================================")
    print(f"Configuring {out_filename} via {cam_name}...")
    light_fn(samples=samples)
    
    scene.camera = cam
    out_path = os.path.join(RENDERS_DIR, f"{out_filename}.png")
    art_path = os.path.join(ARTIFACT_DIR, f"{out_filename}.png")
    
    scene.render.filepath = out_path
    print(f"Rendering to {out_path} ({samples} samples)...")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_path, art_path)
    
    sz_kb = os.path.getsize(out_path) // 1024
    print(f"Complete: {out_filename}.png ({sz_kb} KB)")
    return out_path

def render_street_life():
    return render_env_view("Cam_Street_Life_Hero", "Props_Street_Life_Hero", lighting_manager.set_sunset_lighting, samples=64)

def render_wagon():
    return render_env_view("Cam_Wagon_Market_Hero", "Props_Wagon_Market_Hero", lighting_manager.set_daytime_lighting, samples=64)

def render_table():
    return render_env_view("Cam_Props_Table_StillLife", "Props_Table_StillLife", lighting_manager.set_daytime_lighting, samples=64)

def render_notice_board():
    return render_env_view("Cam_Village_Entrance_NoticeBoard", "Props_Village_NoticeBoard_Entrance", lighting_manager.set_sunset_lighting, samples=64)

if __name__ == "__main__":
    render_street_life()
    render_wagon()
    render_table()
    render_notice_board()
