"""
Medieval Fantasy Village - Detailed Camera Setup
Creates:
- Front, Back, Left, Right, and Top Orthographic Cameras
- Close-up Perspective Detail Cameras for Roof and Door
- Cinematic Three-Quarter Beauty Camera
"""

import bpy
import math
from mathutils import Vector

def get_or_create_camera(name, cam_type='PERSP', ortho_scale=12.5, focal_length=50.0):
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

def setup_all_required_cameras():
    cameras = {}
    cottage_center = (0.0, 0.0, 4.6)

    # 1. Front Orthographic Camera
    c_front = get_or_create_camera("Cam_Ortho_Front", cam_type='ORTHO', ortho_scale=12.5)
    orient_camera(c_front, (0.0, -25.0, 4.6), (0.0, 0.0, 4.6))
    cameras["Cam_Ortho_Front"] = c_front

    # 2. Back Orthographic Camera
    c_back = get_or_create_camera("Cam_Ortho_Back", cam_type='ORTHO', ortho_scale=12.5)
    orient_camera(c_back, (0.0, 25.0, 4.6), (0.0, 0.0, 4.6))
    cameras["Cam_Ortho_Back"] = c_back

    # 3. Left Orthographic Camera (Windows & Barrels)
    c_left = get_or_create_camera("Cam_Ortho_Left", cam_type='ORTHO', ortho_scale=13.5)
    orient_camera(c_left, (-25.0, 0.0, 4.6), (0.0, 0.0, 4.6))
    cameras["Cam_Ortho_Left"] = c_left

    # 4. Right Orthographic Camera (Chimney Stack Side)
    c_right = get_or_create_camera("Cam_Ortho_Right", cam_type='ORTHO', ortho_scale=13.5)
    orient_camera(c_right, (25.0, 0.0, 4.6), (0.0, 0.0, 4.6))
    cameras["Cam_Ortho_Right"] = c_right

    # 5. Top Orthographic Camera (Roof & Site Plan)
    c_top = get_or_create_camera("Cam_Ortho_Top", cam_type='ORTHO', ortho_scale=13.0)
    c_top.location = Vector((0.0, 0.0001, 30.0))
    c_top.rotation_euler = (0.0, 0.0, 0.0)
    cameras["Cam_Ortho_Top"] = c_top

    # 6. Close-Up Detail Camera: Door & Porch
    c_door = get_or_create_camera("Cam_Detail_Door", cam_type='PERSP', focal_length=50.0)
    orient_camera(c_door, (1.2, -6.6, 2.2), (-0.60, -4.05, 2.05))
    cameras["Cam_Detail_Door"] = c_door

    # 7. Close-Up Detail Camera: Roof Tiles, Eaves & Bargeboard
    c_roof = get_or_create_camera("Cam_Detail_Roof", cam_type='PERSP', focal_length=65.0)
    orient_camera(c_roof, (-5.5, -8.2, 7.8), (-2.8, -3.8, 6.7))
    cameras["Cam_Detail_Roof"] = c_roof

    # 8. Cinematic Three-Quarter Beauty Camera
    c_3q = get_or_create_camera("Cam_ThreeQuarter", cam_type='PERSP', focal_length=45.0)
    orient_camera(c_3q, (12.0, -14.5, 7.8), (0.0, -0.5, 4.0))
    cameras["Cam_ThreeQuarter"] = c_3q

    bpy.context.scene.camera = c_3q
    return cameras

if __name__ == '__main__':
    setup_all_required_cameras()
    print("All required orthographic, detail, and perspective cameras set up successfully.")

