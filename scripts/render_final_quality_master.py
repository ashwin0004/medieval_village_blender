"""
render_final_quality_master.py
==============================
Master Rendering Script for the Final Quality Medieval Fantasy Village.
Produces comprehensive Full HD 1080p renders across all three required lighting setups:
  1. DAYLIGHT:
     - Final_Daylight_Aerial_Overview (Whole settlement overview)
     - Final_Daylight_Street_Market (Main cobblestone avenue & market stalls)
     - Final_Daylight_River_Bridge (River water reflections, pebbles, rocks & stone bridge)
     - Final_Daylight_Cottage_Architecture (Cottage facade & timber details)

  2. SUNSET:
     - Final_Sunset_Aerial_Vista (Golden-hour aerial perspective)
     - Final_Sunset_River_Reflections (Matches Reference Image 1 with sparkling water & golden rim light)
     - Final_Sunset_MainStreet (Warm sunset casting long shadows across cobblestones)

  3. NIGHTTIME:
     - Final_Nighttime_Aerial_Overview (Constellation of glowing windows & lantern pools)
     - Final_Nighttime_River_Glade (Matches Reference Image 2 with enchanted river & glowing cottage)
     - Final_Nighttime_Tavern_Market (Warm lantern pools illuminating the market square & tavern)
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

def render_view(cam_name, out_filename, samples=72):
    scene = bpy.context.scene
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        print(f"Error: Camera '{cam_name}' not found!")
        return None
        
    scene.camera = cam
    lighting_manager.setup_cycles_engine(samples=samples)
    
    out_path = os.path.join(RENDERS_DIR, f"{out_filename}.png")
    art_path = os.path.join(ARTIFACT_DIR, f"{out_filename}.png")
    
    scene.render.filepath = out_path
    print(f"\nRendering [{out_filename}] via {cam_name} ({samples} samples)...")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_path, art_path)
    
    sz_kb = os.path.getsize(out_path) // 1024
    print(f"-> Successfully saved: {out_filename}.png ({sz_kb} KB)")
    return out_path

def render_all_final_views():
    results = {}
    
    # =========================================================================
    # 1. DAYLIGHT SUITE
    # =========================================================================
    print("\n" + "="*50)
    print("PHASE 1: CONFIGURING DAYLIGHT LIGHTING RIG")
    print("="*50)
    lighting_manager.set_daytime_lighting(samples=64)
    
    results["Daylight_Aerial"] = render_view("Cam_Polish_Aerial", "Final_Daylight_Aerial_Overview", samples=64)
    results["Daylight_Street"] = render_view("Cam_Street_Life_Hero", "Final_Daylight_Street_Market", samples=64)
    results["Daylight_River"] = render_view("Cam_River_Sunset_Reflections", "Final_Daylight_River_Bridge", samples=64)
    results["Daylight_Cottage"] = render_view("Cam_Polish_Cottage", "Final_Daylight_Cottage_Architecture", samples=64)
    
    # =========================================================================
    # 2. SUNSET SUITE
    # =========================================================================
    print("\n" + "="*50)
    print("PHASE 2: CONFIGURING SUNSET LIGHTING RIG")
    print("="*50)
    lighting_manager.set_sunset_lighting(samples=64)
    
    results["Sunset_Aerial"] = render_view("Cam_Final_Aerial_Vista", "Final_Sunset_Aerial_Vista", samples=64)
    results["Sunset_River"] = render_view("Cam_River_Sunset_Reflections", "Final_Sunset_River_Reflections", samples=64)
    results["Sunset_Street"] = render_view("Cam_PBR_Cobblestone_Hero", "Final_Sunset_MainStreet", samples=64)
    
    # =========================================================================
    # 3. NIGHTTIME SUITE
    # =========================================================================
    print("\n" + "="*50)
    print("PHASE 3: CONFIGURING NIGHTTIME LIGHTING RIG")
    print("="*50)
    lighting_manager.set_nighttime_lighting(samples=72)
    
    results["Night_Aerial"] = render_view("Cam_Polish_Night", "Final_Nighttime_Aerial_Overview", samples=72)
    results["Night_River"] = render_view("Cam_River_Sunset_Reflections", "Final_Nighttime_River_Glade", samples=72)
    results["Night_Tavern"] = render_view("Cam_Final_Tavern_Market", "Final_Nighttime_Tavern_Market", samples=72)
    
    print("\n" + "="*50)
    print("ALL 10 FINAL QUALITY RENDERS COMPLETE!")
    print("="*50)
    return results

if __name__ == "__main__":
    render_all_final_views()

