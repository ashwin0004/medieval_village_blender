"""
Medieval Fantasy Village - Prop Collection Showcase Cameras & Studio
Configures exhibition studio floor, studio lighting, and multi-angle cameras for the prop collection.
"""

import bpy
import math
from mathutils import Vector

def setup_props_studio():
    # Studio display floor
    plane_name = "Props_Studio_Floor"
    plane_obj = bpy.data.objects.get(plane_name)
    if not plane_obj:
        bpy.ops.mesh.primitive_plane_add(size=35.0, location=(-3.0, -1.0, -0.01))
        plane_obj = bpy.context.active_object
        plane_obj.name = plane_name

    mat = bpy.data.materials.get("M_Stone_AshlarGrey")
    if mat and len(plane_obj.data.materials) == 0:
        plane_obj.data.materials.append(mat)

    # Move to Props collection
    target_col = bpy.data.collections.get("04_PROPS_FURNITURE")
    if target_col and plane_obj.name not in target_col.objects:
        for c in list(plane_obj.users_collection):
            c.objects.unlink(plane_obj)
        target_col.objects.link(plane_obj)

    # Key Studio Light
    light_col = bpy.data.collections.get("Lighting")
    key_light = bpy.data.lights.get("Light_Props_Sun")
    if not key_light:
        key_light = bpy.data.lights.new("Light_Props_Sun", type='SUN')
    key_light.energy = 4.2
    key_light.color = (1.0, 0.95, 0.88)
    key_light.angle = math.radians(2.0)

    key_obj = bpy.data.objects.get("Light_Props_Sun")
    if not key_obj:
        key_obj = bpy.data.objects.new("Light_Props_Sun", key_light)
        if light_col:
            light_col.objects.link(key_obj)
        else:
            bpy.context.scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(50.0), math.radians(22.0), math.radians(-42.0))

def get_or_create_camera(name, cam_type='PERSP', focal_length=45.0):
    cam_data = bpy.data.cameras.get(name)
    if not cam_data:
        cam_data = bpy.data.cameras.new(name)
    cam_data.type = cam_type
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

def setup_props_cameras():
    cameras = {}
    props_center = (-3.0, -1.0, 0.6)

    # 1. Props Overview (Cinematic Three-Quarter Beauty View)
    c_over = get_or_create_camera("Cam_Props_Overview", focal_length=36.0)
    orient_camera(c_over, (7.0, -14.5, 9.5), (-3.0, -1.0, 0.6))
    cameras["Cam_Props_Overview"] = c_over

    # 2. Props Front View (Elevated Wide)
    c_front = get_or_create_camera("Cam_Props_Front", focal_length=38.0)
    orient_camera(c_front, (-3.0, -16.0, 7.5), (-3.0, -0.5, 0.6))
    cameras["Cam_Props_Front"] = c_front

    # 3. Macro Close-Up: Containers (Barrels, Crates, Sacks, Baskets)
    c_cont = get_or_create_camera("Cam_Props_CloseUp_Containers", focal_length=52.0)
    orient_camera(c_cont, (-4.5, -2.5, 3.2), (-4.8, 3.8, 0.5))
    cameras["Cam_Props_CloseUp_Containers"] = c_cont

    # 4. Macro Close-Up: Handcart, Furniture & Firewood
    c_cart = get_or_create_camera("Cam_Props_CloseUp_Cart", focal_length=50.0)
    orient_camera(c_cart, (1.8, -12.5, 3.6), (-2.0, -6.5, 0.7))
    cameras["Cam_Props_CloseUp_Cart"] = c_cart

    bpy.context.scene.camera = c_over
    return cameras

if __name__ == '__main__':
    setup_props_studio()
    setup_props_cameras()
    print("Props cameras and studio ready.")

