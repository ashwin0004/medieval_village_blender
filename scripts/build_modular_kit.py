"""
Medieval Fantasy Village - Build Modular Architecture Kit & Render Showcase
Automates:
1. PBR Material variations initialization
2. Full modular architecture kit generation (foundations, walls, timber framing, gables, roofs, doors, windows, arches, stairs, chimneys)
3. Showcase exhibition floor, studio lighting, and cameras
4. Blend file saving to assets/architecture/modular_kit.blend
5. Full HD Cycles GPU rendering of asset showcase views
"""

import bpy
import sys
import os
import time

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import materials_library
import modular_kit
import showcase_cameras

def hide_cottage_for_showcase():
    cottage_col = bpy.data.collections.get("Main_Cottage")
    if cottage_col:
        cottage_col.hide_viewport = True
        cottage_col.hide_render = True
    base_cottage_col = bpy.data.collections.get("01_BUILDINGS")
    if base_cottage_col:
        base_cottage_col.hide_viewport = True
        base_cottage_col.hide_render = True

def unhide_cottage():
    cottage_col = bpy.data.collections.get("Main_Cottage")
    if cottage_col:
        cottage_col.hide_viewport = False
        cottage_col.hide_render = False
    base_cottage_col = bpy.data.collections.get("01_BUILDINGS")
    if base_cottage_col:
        base_cottage_col.hide_viewport = False
        base_cottage_col.hide_render = False

def render_showcase(output_dir=r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\modular_kit", samples=96):
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

    showcase_views = [
        "Cam_Showcase_Overview",
        "Cam_Showcase_Front",
        "Cam_Showcase_CloseUp_Walls",
        "Cam_Showcase_CloseUp_Details",
    ]

    rendered_files = []
    print(f"\n--- Starting Cycles GPU Rendering for {len(showcase_views)} Showcase Views ---")

    for cam_name in showcase_views:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Warning: Camera '{cam_name}' not found, skipping.")
            continue

        scene.camera = cam_obj
        filepath = os.path.join(output_dir, f"{cam_name}.png")
        scene.render.filepath = filepath

        t0 = time.time()
        print(f"Rendering showcase view '{cam_name}' -> {filepath}...")
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        print(f"Finished '{cam_name}' in {dt:.2f}s")
        rendered_files.append(filepath)

    if "Cam_Showcase_Overview" in bpy.data.objects:
        scene.camera = bpy.data.objects["Cam_Showcase_Overview"]

    return rendered_files

def run_build(do_render=True):
    print("================================================================")
    print("BUILDING MODULAR MEDIEVAL ARCHITECTURE KIT & SHOWCASE")
    print("================================================================")

    # 1. Materials
    print("\n[Step 1/5] Initializing PBR Materials with Variations...")
    materials_library.build_all_materials()

    # 2. Modular Architecture Kit
    print("\n[Step 2/5] Constructing Modular Architectural Components...")
    modular_kit.build_all_modular_architecture()

    # 3. Studio Showcase Setup
    print("\n[Step 3/5] Setting up Studio Exhibition Floor, Lighting & Cameras...")
    showcase_cameras.setup_showcase_studio()
    showcase_cameras.setup_showcase_cameras()
    hide_cottage_for_showcase()

    # 4. Save Blend Files
    print("\n[Step 4/5] Saving Architecture Blend Files...")
    kit_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\architecture\modular_kit.blend"
    village_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\Medieval_Village.blend"
    backup_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\backups\modular_kit_v01.blend"

    os.makedirs(os.path.dirname(kit_blend), exist_ok=True)
    os.makedirs(os.path.dirname(backup_blend), exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=kit_blend)
    print(f"Saved modular kit library: {kit_blend}")

    bpy.ops.wm.save_as_mainfile(filepath=village_blend, copy=True)
    print(f"Updated village master blend: {village_blend}")

    bpy.ops.wm.save_as_mainfile(filepath=backup_blend, copy=True)
    print(f"Saved backup version: {backup_blend}")

    # 5. Render Showcase Views
    rendered = []
    if do_render:
        print("\n[Step 5/5] Rendering High-Definition Asset Showcase...")
        rendered = render_showcase(samples=96)

    print("\n================================================================")
    print("MODULAR ARCHITECTURE KIT COMPLETE & SHOWCASE RENDERED!")
    print("================================================================")
    return rendered

if __name__ == '__main__':
    run_build(do_render=True)

