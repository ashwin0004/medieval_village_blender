"""
Medieval Fantasy Village - Build Props Collection & Render Showcase
Automates:
1. PBR Materials initialization (burlap, wicker, rope, glazed ceramics, rusted iron, firewood bark)
2. Comprehensive props modeling (containers, kitchen, tools, furniture, street lighting, carts, firewood)
3. Props exhibition studio, lighting and cameras
4. Blend file saving to assets/props/village_props.blend and master
5. Full HD Cycles GPU rendering of the prop collection showcase
"""

import bpy
import sys
import os
import time

scripts_dir = r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import materials_library
import props_collection
import props_cameras

def hide_other_collections():
    for cname in ["Main_Cottage", "01_BUILDINGS", "02_ARCHITECTURE_MODULAR"]:
        col = bpy.data.collections.get(cname)
        if col:
            col.hide_viewport = True
            col.hide_render = True

def unhide_all_collections():
    for cname in ["Main_Cottage", "01_BUILDINGS", "02_ARCHITECTURE_MODULAR", "04_PROPS_FURNITURE"]:
        col = bpy.data.collections.get(cname)
        if col:
            col.hide_viewport = False
            col.hide_render = False

def render_props_showcase(output_dir=r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\props", samples=96):
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

    views = [
        "Cam_Props_Overview",
        "Cam_Props_Front",
        "Cam_Props_CloseUp_Containers",
        "Cam_Props_CloseUp_Cart",
    ]

    rendered_files = []
    print(f"\n--- Starting Cycles GPU Rendering for {len(views)} Props Showcase Views ---")

    for cam_name in views:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Warning: Camera '{cam_name}' not found, skipping.")
            continue

        scene.camera = cam_obj
        filepath = os.path.join(output_dir, f"{cam_name}.png")
        scene.render.filepath = filepath

        t0 = time.time()
        print(f"Rendering props view '{cam_name}' -> {filepath}...")
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        print(f"Finished '{cam_name}' in {dt:.2f}s")
        rendered_files.append(filepath)

    if "Cam_Props_Overview" in bpy.data.objects:
        scene.camera = bpy.data.objects["Cam_Props_Overview"]

    return rendered_files

def run_build(do_render=True):
    print("================================================================")
    print("BUILDING MEDIEVAL VILLAGE PROP COLLECTION & SHOWCASE")
    print("================================================================")

    # 1. Materials
    print("\n[Step 1/5] Initializing Specialized Prop Materials...")
    materials_library.build_all_materials()

    # 2. Props Collection
    print("\n[Step 2/5] Constructing Full Medieval Village Prop Library...")
    props_collection.build_all_village_props()

    # 3. Studio Setup
    print("\n[Step 3/5] Setting up Props Studio Exhibition Floor, Lighting & Cameras...")
    props_cameras.setup_props_studio()
    props_cameras.setup_props_cameras()
    hide_other_collections()

    # 4. Save Blend Files
    print("\n[Step 4/5] Saving Prop Library Blend Files...")
    props_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\props\village_props.blend"
    village_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\Medieval_Village.blend"
    backup_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\backups\village_props_v01.blend"

    os.makedirs(os.path.dirname(props_blend), exist_ok=True)
    os.makedirs(os.path.dirname(backup_blend), exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=props_blend)
    print(f"Saved props library: {props_blend}")

    bpy.ops.wm.save_as_mainfile(filepath=village_blend, copy=True)
    print(f"Updated village master blend: {village_blend}")

    bpy.ops.wm.save_as_mainfile(filepath=backup_blend, copy=True)
    print(f"Saved backup version: {backup_blend}")

    # 5. Render Showcase Views
    rendered = []
    if do_render:
        print("\n[Step 5/5] Rendering High-Definition Prop Collection Showcase...")
        rendered = render_props_showcase(samples=96)

    # Restore visibility
    unhide_all_collections()
    bpy.ops.wm.save_as_mainfile(filepath=village_blend)

    print("\n================================================================")
    print("MEDIEVAL VILLAGE PROPS COMPLETE & SHOWCASE RENDERED!")
    print("================================================================")
    return rendered

if __name__ == '__main__':
    run_build(do_render=True)

