import bpy
import math
import time
from mathutils import Vector, Euler

def render_fishing_hero():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True

    c2_name = "Cam_Riverside_Fishing_Hero"
    cam2 = bpy.data.objects.get(c2_name)
    if not cam2:
        cd2 = bpy.data.cameras.new(c2_name)
        cam2 = bpy.data.objects.new(c2_name, cd2)
        scene.collection.objects.link(cam2)

    cam2.data.lens = 35
    cam2.location = Vector((-25.0, 26.5, -0.3))
    target2 = Vector((-20.5, 23.5, -1.2))
    dir2 = target2 - cam2.location
    cam2.rotation_euler = dir2.to_track_quat('-Z', 'Y').to_euler()

    scene.camera = cam2
    scene.render.filepath = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\Riverside_Fishing_Hero.png"
    print("\nRendering refined Cam_Riverside_Fishing_Hero...")
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"Rendered in {time.time() - t0:.2f}s")

if __name__ == "__main__":
    render_fishing_hero()
