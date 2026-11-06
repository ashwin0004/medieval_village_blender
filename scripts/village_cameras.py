"""
village_cameras.py
==================
World-scale cameras for the medieval village environment.
Creates 6 cinematic camera angles covering:
  - Aerial overview (top-down)
  - 3/4 beauty shot
  - Ground level market square
  - Ground level main road
  - River bridge view
  - Night-ish sunset angle
"""

import bpy
import math


def _make_cam(name, location, rotation_euler, lens=35.0, ortho_scale=None, col=None):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    if ortho_scale is not None:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.type = "PERSP"
    cam_data.clip_end = 1000.0
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = location
    cam_obj.rotation_euler = [math.radians(r) for r in rotation_euler]
    if col:
        col.objects.link(cam_obj)
    else:
        bpy.context.scene.collection.objects.link(cam_obj)
    return cam_obj


def setup_village_cameras():
    # Camera collection
    cam_col_name = "00_MANAGEMENT"
    if cam_col_name in bpy.data.collections:
        cam_col = bpy.data.collections[cam_col_name]
    else:
        cam_col = bpy.data.collections.new(cam_col_name)
        bpy.context.scene.collection.children.link(cam_col)

    # Remove old village cameras if re-running
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Cam_Village_") and obj.type == "CAMERA":
            bpy.data.objects.remove(obj, do_unlink=True)

    cameras = {}

    # 1. Aerial Top-Down Overview
    cameras["Cam_Village_Aerial"] = _make_cam(
        "Cam_Village_Aerial",
        location=(0, -5, 90),
        rotation_euler=(12, 0, 0),
        lens=28,
        col=cam_col
    )

    # 2. Classic 3/4 cinematic beauty shot
    cameras["Cam_Village_Beauty"] = _make_cam(
        "Cam_Village_Beauty",
        location=(55, -55, 48),
        rotation_euler=(52, 0, 45),
        lens=35,
        col=cam_col
    )

    # 3. Ground level — Market square looking toward church
    cameras["Cam_Village_Market"] = _make_cam(
        "Cam_Village_Market",
        location=(8, -8, 1.7),
        rotation_euler=(90, 0, 335),
        lens=28,
        col=cam_col
    )

    # 4. Ground level — Main road looking north toward tavern
    cameras["Cam_Village_Road"] = _make_cam(
        "Cam_Village_Road",
        location=(0, -35, 1.7),
        rotation_euler=(90, 0, 0),
        lens=24,
        col=cam_col
    )

    # 5. Bridge / River view
    cameras["Cam_Village_Bridge"] = _make_cam(
        "Cam_Village_Bridge",
        location=(-10, 18, 4.5),
        rotation_euler=(78, 0, 48),
        lens=35,
        col=cam_col
    )

    # 6. Castle tower dramatic angle
    cameras["Cam_Village_Castle"] = _make_cam(
        "Cam_Village_Castle",
        location=(-8, -30, 8),
        rotation_euler=(72, 0, 340),
        lens=28,
        col=cam_col
    )

    print(f"Created {len(cameras)} village cameras.")
    return cameras

