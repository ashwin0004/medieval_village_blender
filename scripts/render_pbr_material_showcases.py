"""
render_pbr_material_showcases.py
================================
Renders high-detail 1080p showcase views demonstrating the 11 realistic PBR materials:
  1. PBR_Material_Palette_Showcase: Macro studio showcase of all 11 PBR materials side-by-side
  2. PBR_Cottage_Architecture_Hero: Cottage facade featuring aged oak, stone foundation, plaster, clay tiles, leaded glass
  3. PBR_Watchtower_Stone_Hero: Watchtower masonry featuring rough stone, ashlar quoins, timber hoarding, slate roof
  4. PBR_Cobblestone_Street_Hero: Main street featuring cobblestone road with moss, mud, carts, and iron lanterns
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

def render_pbr_view(cam_name, out_filename, light_fn=None, samples=72):
    scene = bpy.context.scene
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        print(f"Error: Camera {cam_name} not found!")
        return None
        
    print(f"\n==========================================")
    print(f"Configuring {out_filename} via {cam_name}...")
    
    lighting_manager.setup_cycles_engine(samples=samples)
    if light_fn:
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

def render_material_palette():
    # Studio lighting is built into the showcase rig
    return render_pbr_view("Cam_PBR_Materials_Showcase", "PBR_Material_Palette_Showcase", light_fn=None, samples=64)

def render_cottage_hero():
    # Use existing cottage camera or position dedicated close-up
    cam = bpy.data.objects.get("Cam_Polish_Cottage") or bpy.data.objects.get("Cam_Showcase_Front")
    return render_pbr_view(cam.name, "PBR_Cottage_Architecture_Hero", light_fn=lighting_manager.set_daytime_lighting, samples=64)

def render_watchtower_hero():
    cam = bpy.data.objects.get("Cam_Watchtower_Full")
    return render_pbr_view(cam.name, "PBR_Watchtower_Stone_Hero", light_fn=lighting_manager.set_daytime_lighting, samples=64)

def render_cobblestone_hero():
    cam = bpy.data.objects.get("Cam_Roads_Cobble_Macro") or bpy.data.objects.get("Cam_Roads_Main_Avenue")
    return render_pbr_view(cam.name, "PBR_Cobblestone_Street_Hero", light_fn=lighting_manager.set_sunset_lighting, samples=64)

if __name__ == "__main__":
    render_material_palette()
    render_cottage_hero()
    render_watchtower_hero()
    render_cobblestone_hero()

