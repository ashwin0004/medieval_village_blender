"""
render_river_showcases.py
=========================
Renders high-resolution 1080p showcase views of the Winding River and Medieval Stone Arch Bridge:
  1. River_Arch_Bridge_Hero (Ref 1: Hero waterfront view showing arch reflection, voussoirs, rowboat, stone steps)
  2. River_Waterfall_Cascade (Ref 2 & 3: Close-up of bridge weir waterfall, foaming rapids, and river boulders)
  3. River_Village_Vista (Ref 5: Elevated panoramic vista of winding river cutting through village and alpine valley)
  4. River_Sunset_Reflections (Ref 1 & 4: Sunset golden hour reflections on river waters and bridge lanterns)
"""

import bpy
import os
import shutil
import sys
from mathutils import Vector

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import lighting_manager

RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\nature"
ARTIFACT_DIR = r"C:\Users\ashwi\.gemini\antigravity\brain\a0a9786d-d6d3-4462-aac6-e6fdc3ebcb84\renders"

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def render_view(cam_name, out_filename, light_fn, samples=72):
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

# Execute one by one to avoid timeout

