"""
render_comprehensive_final_suite.py
===================================
Master Final Rendering Suite for Medieval Fantasy Village.
Produces Full HD 1080p renders across all 3 lighting configurations
(Daylight, Sunset, Nighttime) and 3 camera perspectives
(Aerial, Street-Level, and Close-Up Hero Views).
"""

import bpy
import os
import shutil
import sys
import datetime

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import lighting_manager

RENDERS_DIR = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders"
ARTIFACT_DIR = r"C:\Users\ashwi\.gemini\antigravity\brain\a0a9786d-d6d3-4462-aac6-e6fdc3ebcb84\renders"

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def render_camera_view(cam_name, out_name, samples=64):
    scene = bpy.context.scene
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        print(f"Warning: Camera {cam_name} not found! Skipping {out_name}.")
        return None
    scene.camera = cam
    scene.cycles.samples = samples
    
    out_path = os.path.join(RENDERS_DIR, f"{out_name}.png")
    art_path = os.path.join(ARTIFACT_DIR, f"{out_name}.png")
    scene.render.filepath = out_path
    
    print(f"Rendering [{out_name}] via '{cam_name}' ({samples} samples)...")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_path, art_path)
    sz_kb = os.path.getsize(out_path) // 1024
    print(f"-> Successfully saved: {out_name}.png ({sz_kb} KB)")
    return out_path

def run_master_suite():
    results = {}
    
    # =========================================================================
    # 1. DAYLIGHT CONFIGURATION
    # =========================================================================
    print("\n" + "="*50)
    print("SETTING UP CINEMATIC DAYLIGHT LIGHTING RIG")
    print("="*50)
    lighting_manager.set_daytime_lighting(samples=64)
    
    results["Daylight_Aerial"] = render_camera_view("Cam_Final_Aerial_Vista", "Final_Daylight_Aerial_Overview", samples=64)
    results["Daylight_Street"] = render_camera_view("Cam_Street_Life_Hero", "Final_Daylight_Street_Market", samples=64)
    results["Daylight_Props"] = render_camera_view("Cam_Props_Table_StillLife", "Final_Daylight_Props_Vignette", samples=64)
    results["Daylight_River"] = render_camera_view("Cam_River_Sunset_Reflections", "Final_Daylight_River_Bridge", samples=64)

    # =========================================================================
    # 2. SUNSET CONFIGURATION (Golden Hour)
    # =========================================================================
    print("\n" + "="*50)
    print("SETTING UP CINEMATIC SUNSET LIGHTING RIG")
    print("="*50)
    lighting_manager.set_sunset_lighting(samples=64)
    
    results["Sunset_Aerial"] = render_camera_view("Cam_Final_Aerial_Vista", "Final_Sunset_Aerial_Vista", samples=64)
    results["Sunset_Street"] = render_camera_view("Cam_Street_Life_Hero", "Final_Sunset_MainStreet", samples=64)
    results["Sunset_River"] = render_camera_view("Cam_River_Sunset_Reflections", "Final_Sunset_River_Reflections", samples=64)
    results["Sunset_Wagon"] = render_camera_view("Cam_Wagon_Market_Hero", "Final_Sunset_Cargo_Wagon", samples=64)

    # =========================================================================
    # 3. NIGHTTIME CONFIGURATION (Moonlight & Lantern Pools)
    # =========================================================================
    print("\n" + "="*50)
    print("SETTING UP CINEMATIC NIGHTTIME LIGHTING RIG")
    print("="*50)
    lighting_manager.set_nighttime_lighting(samples=72)
    
    results["Night_Aerial"] = render_camera_view("Cam_Polish_Night", "Final_Nighttime_Aerial_Overview", samples=72)
    results["Night_Street"] = render_camera_view("Cam_Street_Life_Hero", "Final_Nighttime_Tavern_Market", samples=72)
    results["Night_River"] = render_camera_view("Cam_Final_Night_Glade_Hero", "Final_Nighttime_River_Glade", samples=72)
    
    print("\n" + "="*50)
    print("MASTER FINAL RENDERING SUITE COMPLETE!")
    print("="*50)
    return results

if __name__ == "__main__":
    run_master_suite()

