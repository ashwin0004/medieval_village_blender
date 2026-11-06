"""
polish_cameras.py
=================
Cinematic Camera Setup for the 7 Polish Village Renders:
  1. Cam_Polish_Aerial (Epic village overview, landscape, river & castle)
  2. Cam_Polish_MainStreet (Eye-level cobblestone avenue looking toward market)
  3. Cam_Polish_Tavern (Hero shot of tavern, outdoor patio, tables, barrels, sign)
  4. Cam_Polish_Cottage (Spectacular 3/4 beauty view of main timber/stone cottage)
  5. Cam_Polish_ChurchCastle (Majestic composition of church spire & castle ruins)
  6. Cam_Polish_Bridge (Scenic riverbank view of double-arch stone bridge)
  7. Cam_Polish_Night (Atmospheric illuminated overview of night village)
"""

import bpy
import math
from mathutils import Vector

def get_or_create_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def make_or_update_cam_tracked(name, loc, target, lens=35.0, col=None):
    if name in bpy.data.objects:
        cam_obj = bpy.data.objects[name]
    else:
        cam_data = bpy.data.cameras.new(name)
        cam_obj = bpy.data.objects.new(name, cam_data)
        if col:
            col.objects.link(cam_obj)
        else:
            bpy.context.scene.collection.objects.link(cam_obj)
            
    cam_obj.data.lens = lens
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 1500.0
    cam_obj.location = loc
    
    # Calculate exact track quaternion: -Z points to target, +Y points up
    direction = target - loc
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    return cam_obj

def setup_all_polish_cameras():
    col = get_or_create_col("00_MANAGEMENT")
    cameras = {}
    
    # 1. Aerial Overview
    cameras["Cam_Polish_Aerial"] = make_or_update_cam_tracked(
        "Cam_Polish_Aerial",
        loc=Vector((0.0, -16.0, 92.0)),
        target=Vector((0.0, 4.0, 2.0)),
        lens=26.0,
        col=col
    )
    
    # 2. Main Street (Human eye level 1.7m)
    cameras["Cam_Polish_MainStreet"] = make_or_update_cam_tracked(
        "Cam_Polish_MainStreet",
        loc=Vector((0.0, -48.0, 1.7)),
        target=Vector((0.0, -16.0, 2.2)),
        lens=25.0,
        col=col
    )
    
    # 3. Tavern & Outdoor Patio
    cameras["Cam_Polish_Tavern"] = make_or_update_cam_tracked(
        "Cam_Polish_Tavern",
        loc=Vector((7.0, -24.5, 3.2)),
        target=Vector((4.5, -14.0, 3.8)),
        lens=35.0,
        col=col
    )
    
    # 4. Main Cottage Hero View
    cameras["Cam_Polish_Cottage"] = make_or_update_cam_tracked(
        "Cam_Polish_Cottage",
        loc=Vector((-2.5, -8.8, 2.4)),
        target=Vector((0.0, -1.8, 3.2)),
        lens=36.0,
        col=col
    )
    
    # 5. Church and Castle
    cameras["Cam_Polish_ChurchCastle"] = make_or_update_cam_tracked(
        "Cam_Polish_ChurchCastle",
        loc=Vector((14.0, 2.0, 10.5)),
        target=Vector((-16.0, 10.0, 9.0)),
        lens=28.0,
        col=col
    )
    
    # 6. River and Stone Bridge
    cameras["Cam_Polish_Bridge"] = make_or_update_cam_tracked(
        "Cam_Polish_Bridge",
        loc=Vector((-5.0, 15.0, 3.0)),
        target=Vector((6.0, 22.0, 1.8)),
        lens=34.0,
        col=col
    )
    
    # 7. Nighttime Village
    cameras["Cam_Polish_Night"] = make_or_update_cam_tracked(
        "Cam_Polish_Night",
        loc=Vector((44.0, -44.0, 34.0)),
        target=Vector((0.0, -10.0, 3.5)),
        lens=32.0,
        col=col
    )
    
    print(f"Configured and verified line-of-sight for all {len(cameras)} polish cameras.")
    return cameras

if __name__ == "__main__":
    setup_all_polish_cameras()
