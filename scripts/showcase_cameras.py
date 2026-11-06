"""
Medieval Fantasy Village - Modular Kit Showcase Cameras & Lighting
Sets up dedicated studio showcase lighting and cameras to present the modular kit.
"""

import bpy
import math
from mathutils import Vector

def setup_showcase_studio():
    # Studio Exhibition Platform Plane
    plane_name = "Showcase_Studio_Floor"
    plane_obj = bpy.data.objects.get(plane_name)
    if not plane_obj:
        bpy.ops.mesh.primitive_plane_add(size=70.0, location=(0, 0, -0.01))
        plane_obj = bpy.context.active_object
        plane_obj.name = plane_name

    # Studio Cobblestone / Flagstone floor material
    mat = bpy.data.materials.get("M_Stone_AshlarGrey")
    if mat and len(plane_obj.data.materials) == 0:
        plane_obj.data.materials.append(mat)

    # Move to Management or Architecture collection
    target_col = bpy.data.collections.get("02_ARCHITECTURE_MODULAR")
    if target_col and plane_obj.name not in target_col.objects:
        for c in list(plane_obj.users_collection):
            c.objects.unlink(plane_obj)
        target_col.objects.link(plane_obj)

    # Key Showcase Light
    light_col = bpy.data.collections.get("Lighting")
    key_light = bpy.data.lights.get("Light_Showcase_Sun")
    if not key_light:
        key_light = bpy.data.lights.new("Light_Showcase_Sun", type='SUN')
    key_light.energy = 4.2
    key_light.color = (1.0, 0.96, 0.88)
    key_light.angle = math.radians(2.0)

    key_obj = bpy.data.objects.get("Light_Showcase_Sun")
    if not key_obj:
        key_obj = bpy.data.objects.new("Light_Showcase_Sun", key_light)
        if light_col:
            light_col.objects.link(key_obj)
        else:
            bpy.context.scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(52.0), math.radians(20.0), math.radians(-45.0))

def get_or_create_camera(name, cam_type='PERSP', ortho_scale=24.0, focal_length=45.0):
    cam_data = bpy.data.cameras.get(name)
    if not cam_data:
        cam_data = bpy.data.cameras.new(name)
    cam_data.type = cam_type
    if cam_type == 'ORTHO':
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.lens = focal_length
    cam_data.clip_start = 0.1
    cam_data.clip_end = 500.0

    cam_obj = bpy.data.objects.get(name)
    if not cam_obj:
        cam_obj = bpy.data.objects.new(name, cam_data)
        col = bpy.data.collections.get("Cameras")
        if col:
            col.objects.link(cam_obj)
        else:
            bpy.context.scene.collection.objects.link(cam_obj)

    return cam_obj

def orient_camera(cam_obj, location, target):
    cam_obj.location = Vector(location)
    direction = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

def setup_showcase_cameras():
    cameras = {}

    # Center of modular kit exhibition is roughly (5.0, 0.0, 1.2)
    # 1. Showcase Overview (Cinematic Three-Quarter View)
    c_over = get_or_create_camera("Cam_Showcase_Overview", cam_type='PERSP', focal_length=30.0)
    orient_camera(c_over, (20.0, -28.0, 19.0), (5.0, -0.5, 1.2))
    cameras["Cam_Showcase_Overview"] = c_over

    # 2. Showcase Front Elevation (Wide View)
    c_front = get_or_create_camera("Cam_Showcase_Front", cam_type='PERSP', focal_length=32.0)
    orient_camera(c_front, (5.0, -34.0, 13.0), (5.0, -0.5, 1.2))
    cameras["Cam_Showcase_Front"] = c_front

    # 3. Showcase Close-Up: Walls & Timber Framing
    c_walls = get_or_create_camera("Cam_Showcase_CloseUp_Walls", cam_type='PERSP', focal_length=50.0)
    orient_camera(c_walls, (3.5, -2.5, 4.8), (2.0, 6.0, 1.5))
    cameras["Cam_Showcase_CloseUp_Walls"] = c_walls

    # 4. Showcase Close-Up: Arches, Doors & Stairs
    c_details = get_or_create_camera("Cam_Showcase_CloseUp_Details", cam_type='PERSP', focal_length=50.0)
    orient_camera(c_details, (3.5, -16.5, 4.5), (1.5, -7.0, 1.4))
    cameras["Cam_Showcase_CloseUp_Details"] = c_details

    bpy.context.scene.camera = c_over
    return cameras

if __name__ == '__main__':
    setup_showcase_studio()
    setup_showcase_cameras()
    print("Showcase studio and cameras ready.")
