import bpy
import time

def render_showcases():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100

    # Ensure Daylight is active
    sun = bpy.data.objects.get("Sun_Daylight")
    if sun:
        sun.hide_render = False

    cams = [
        ("Cam_Final_River_Hero", r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\Realistic_Foliage_River_Hero.png"),
        ("Cam_Final_Aerial_Vista", r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\Realistic_Foliage_Aerial_Vista.png")
    ]

    for cam_name, filepath in cams:
        cam_obj = bpy.data.objects.get(cam_name)
        if cam_obj:
            scene.camera = cam_obj
            scene.render.filepath = filepath
            print(f"\nRendering {cam_name} to {filepath} ...")
            t0 = time.time()
            bpy.ops.render.render(write_still=True)
            print(f"Rendered {cam_name} in {time.time() - t0:.2f} seconds.")

if __name__ == "__main__":
    render_showcases()

