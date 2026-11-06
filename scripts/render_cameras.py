"""
Medieval Fantasy Village - Multi-Angle Render Pipeline
Renders all designated production camera views in Cycles with GPU OptiX denoiser.
"""

import bpy
import os

def render_all_views(output_dir=r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\blockout", resolution_scale=100):
    os.makedirs(output_dir, exist_ok=True)
    scene = bpy.context.scene

    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
    except Exception:
        pass

    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15
    scene.render.resolution_percentage = resolution_scale

    cam_names = [
        "Cam_ThreeQuarter",
        "Cam_Front",
        "Cam_Side_Right",
        "Cam_Side_Left",
        "Cam_Top",
        "Cam_Entrance_EyeLevel",
    ]

    rendered_files = []

    for cam_name in cam_names:
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            print(f"Warning: Camera '{cam_name}' not found, skipping.")
            continue

        scene.camera = cam_obj
        filepath = os.path.join(output_dir, f"{cam_name}.png")
        scene.render.filepath = filepath
        print(f"Rendering view '{cam_name}' to: {filepath}...")
        bpy.ops.render.render(write_still=True)
        rendered_files.append(filepath)
        print(f"Finished rendering: {filepath}")

    # Reset active camera to ThreeQuarter
    if "Cam_ThreeQuarter" in bpy.data.objects:
        scene.camera = bpy.data.objects["Cam_ThreeQuarter"]

    return rendered_files

if __name__ == '__main__':
    render_all_views()

