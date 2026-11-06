"""
Medieval Fantasy Village - Detailed Cottage Master Build & Render Script
Automates the complete workflow:
1. Scene setup & GPU configuration
2. PBR Materials initialization (Wood, Stone, Plaster, Slate, Clay, Iron, Glass, Lantern)
3. Full detailed cottage procedural modeling
4. Multi-camera setup (Front, Back, Left, Right, Top Orthographic + Door & Roof Close-ups + 3/4)
5. Save to assets/buildings/main_cottage.blend and backups
6. Render all required views to renders/cottage/
"""

import bpy
import sys
import os
import time

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import scene_setup
import materials_library
import cottage_detailed
import camera_setup_detailed

def render_all_cottage_views(output_dir=r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\cottage", samples=96):
    os.makedirs(output_dir, exist_ok=True)
    scene = bpy.context.scene

    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
        cprefs = bpy.context.preferences.addons['cycles'].preferences
        cprefs.compute_device_type = 'OPTIX'
        cprefs.get_devices()
        for d in cprefs.devices:
            if "RTX" in d.name:
                d.use = True
            else:
                d.use = False
    except Exception as e:
        print("Note on GPU setup:", e)

    scene.cycles.samples = samples
    scene.cycles.preview_samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    required_views = [
        "Cam_Ortho_Front",
        "Cam_Ortho_Back",
        "Cam_Ortho_Left",
        "Cam_Ortho_Right",
        "Cam_Ortho_Top",
        "Cam_Detail_Door",
        "Cam_Detail_Roof",
        "Cam_ThreeQuarter",
    ]

    rendered_files = []
    print(f"\n--- Starting Cycles GPU Rendering for {len(required_views)} Camera Views ---")

    for cam_name in required_views:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Warning: Camera '{cam_name}' not found, skipping.")
            continue

        scene.camera = cam_obj
        filepath = os.path.join(output_dir, f"{cam_name}.png")
        scene.render.filepath = filepath

        t0 = time.time()
        print(f"Rendering '{cam_name}' -> {filepath}...")
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        print(f"Finished '{cam_name}' in {dt:.2f}s")
        rendered_files.append(filepath)

    if "Cam_ThreeQuarter" in bpy.data.objects:
        scene.camera = bpy.data.objects["Cam_ThreeQuarter"]

    return rendered_files

def run_build(do_render=True):
    print("================================================================")
    print("STARTING COMPLETE DETAILED MEDIEVAL COTTAGE PRODUCTION PIPELINE")
    print("================================================================")

    # 1. Scene setup
    print("\n[Step 1/5] Configuring Scene Settings, Units, AgX Color & OptiX GPU...")
    scene_setup.run_scene_setup()

    # 2. Materials
    print("\n[Step 2/5] Initializing Comprehensive PBR Material Palette...")
    materials_library.build_all_materials()

    # 3. Cottage detailed build
    print("\n[Step 3/5] Procedurally Constructing Detailed Cottage Mesh Geometry...")
    cottage_detailed.build_complete_detailed_cottage()

    # 4. Cameras
    print("\n[Step 4/5] Setting Up Orthographic, Detail & Perspective Cameras...")
    camera_setup_detailed.setup_all_required_cameras()

    # 5. Save blend files
    print("\n[Step 5/5] Saving Blender Project Files...")
    target_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\buildings\main_cottage.blend"
    village_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\Medieval_Village.blend"
    backup_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\backups\main_cottage_detailed_v01.blend"

    os.makedirs(os.path.dirname(target_blend), exist_ok=True)
    os.makedirs(os.path.dirname(backup_blend), exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=target_blend)
    print(f"Saved primary asset file: {target_blend}")

    bpy.ops.wm.save_as_mainfile(filepath=village_blend, copy=True)
    print(f"Saved village project copy: {village_blend}")

    bpy.ops.wm.save_as_mainfile(filepath=backup_blend, copy=True)
    print(f"Saved backup version: {backup_blend}")

    rendered = []
    if do_render:
        rendered = render_all_cottage_views(samples=96)

    print("\n================================================================")
    print("COMPLETE DETAILED MEDIEVAL COTTAGE FINISHED SUCCESSFULLY!")
    print("================================================================")
    return rendered

if __name__ == '__main__':
    run_build(do_render=True)

