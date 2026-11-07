import bpy
import math
import time
from mathutils import Vector, Euler

def setup_and_render_phase_c():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100

    # Ensure Daylight Sun is active
    sun = bpy.data.objects.get("Sun_Daylight")
    if sun:
        sun.hide_render = False
        sun.data.energy = 5.2

    # 1. Camera 1: Watermill Hero
    c1_name = "Cam_Watermill_Hero"
    cam1 = bpy.data.objects.get(c1_name)
    if not cam1:
        cd1 = bpy.data.cameras.new(c1_name)
        cam1 = bpy.data.objects.new(c1_name, cd1)
        scene.collection.objects.link(cam1)

    cam1.data.lens = 38
    cam1.location = Vector((9.8, 17.2, 1.8))
    target1 = Vector((16.8, 24.2, 1.5))
    dir1 = target1 - cam1.location
    cam1.rotation_euler = dir1.to_track_quat('-Z', 'Y').to_euler()

    # 2. Camera 2: Riverside Fishing Hero
    c2_name = "Cam_Riverside_Fishing_Hero"
    cam2 = bpy.data.objects.get(c2_name)
    if not cam2:
        cd2 = bpy.data.cameras.new(c2_name)
        cam2 = bpy.data.objects.new(c2_name, cd2)
        scene.collection.objects.link(cam2)

    cam2.data.lens = 32
    cam2.location = Vector((-6.8, 20.2, 0.9))
    target2 = Vector((-12.2, 23.0, 0.5))
    dir2 = target2 - cam2.location
    cam2.rotation_euler = dir2.to_track_quat('-Z', 'Y').to_euler()

    # Render Watermill
    scene.camera = cam1
    scene.render.filepath = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\Watermill_District_Hero.png"
    print("\nRendering Cam_Watermill_Hero...")
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"Rendered in {time.time() - t0:.2f}s")

    # Render Fishing Glade
    scene.camera = cam2
    scene.render.filepath = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\Riverside_Fishing_Hero.png"
    print("\nRendering Cam_Riverside_Fishing_Hero...")
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"Rendered in {time.time() - t0:.2f}s")

if __name__ == "__main__":
    setup_and_render_phase_c()

