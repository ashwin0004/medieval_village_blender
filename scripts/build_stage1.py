"""
Medieval Fantasy Village - Build Stage 1 Orchestrator
Executes complete scene setup, material initialization, cottage blockout modeling,
project saving, backup generation, and multi-angle camera rendering.
"""

import bpy
import sys
import os

# Ensure scripts dir is in sys.path
scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import scene_setup
import materials_library
import cottage_blockout
import render_cameras

def run_stage_1(do_render=True):
    print("==================================================")
    print("STARTING STAGE 1: MEDIEVAL COTTAGE BLOCKOUT BUILD")
    print("==================================================")

    # 1. Clean and configure scene
    print("\n[Step 1/5] Configuring Scene Settings, Units, and Lighting...")
    scene_setup.run_scene_setup()

    # 2. Build Materials Library
    print("\n[Step 2/5] Initializing PBR Materials Library...")
    materials_library.build_all_materials()

    # 3. Build Cottage Blockout
    print("\n[Step 3/5] Constructing Cottage Architectural Components...")
    cottage_blockout.build_complete_cottage()

    # 4. Save Blend File & Backup
    print("\n[Step 4/5] Saving Blender Project and Backup...")
    project_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\Medieval_Village.blend"
    backup_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\backups\Medieval_Village_Stage01_Blockout.blend"

    os.makedirs(os.path.dirname(backup_blend), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=project_blend)
    print(f"Project saved to: {project_blend}")

    bpy.ops.wm.save_as_mainfile(filepath=backup_blend, copy=True)
    print(f"Backup copy saved to: {backup_blend}")

    # 5. Render Previews
    rendered = []
    if do_render:
        print("\n[Step 5/5] Rendering Multi-Angle Camera Previews...")
        rendered = render_cameras.render_all_views(resolution_scale=100)
        print(f"Rendered {len(rendered)} camera views.")

    print("\n==================================================")
    print("STAGE 1 COMPLETED SUCCESSFULLY!")
    print("==================================================")
    return rendered

if __name__ == '__main__':
    run_stage_1(do_render=True)

