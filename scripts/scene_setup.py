"""
Medieval Fantasy Village - Scene Setup
Configures units, color management, Cycles OptiX GPU, collections hierarchy,
world lighting, cameras with auto-tracking, and ground plane.
"""

import bpy
import math
from mathutils import Vector

def setup_units_and_color():
    scene = bpy.context.scene
    # Real-world metric units
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

    # Color management
    scene.display_settings.display_device = 'sRGB'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

def setup_cycles_engine(samples=128):
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

    # Resolution
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

def get_or_create_collection(name, parent=None):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent is None:
            bpy.context.scene.collection.children.link(col)
        else:
            parent.children.link(col)
    return col

def setup_collections_hierarchy():
    cols_structure = {
        "00_MANAGEMENT": ["Cameras", "Lighting"],
        "01_BUILDINGS": [
            "Main_Cottage",
            "Main_Cottage/01_Foundation",
            "Main_Cottage/02_Ground_Floor",
            "Main_Cottage/03_Timber_Framing",
            "Main_Cottage/04_Upper_Walls",
            "Main_Cottage/05_Roof",
            "Main_Cottage/06_Doors_Windows",
            "Main_Cottage/07_Chimney",
            "Main_Cottage/08_Interior",
            "Main_Cottage/09_Exterior_Props",
        ],
        "02_ARCHITECTURE_MODULAR": [],
        "03_VILLAGE_STRUCTURES": [],
        "04_PROPS_FURNITURE": [],
        "05_STREET_OBJECTS": [],
        "06_ENVIRONMENT_NATURE": [],
        "99_TERRAIN_ATMOSPHERE": []
    }

    created = {}
    for main_col, sub_cols in cols_structure.items():
        main = get_or_create_collection(main_col)
        created[main_col] = main
        for sub in sub_cols:
            if "/" in sub:
                parts = sub.split("/")
                parent = created.get(parts[0], main)
                child = get_or_create_collection(parts[1], parent)
                created[sub] = child
            else:
                child = get_or_create_collection(sub, main)
                created[sub] = child

    return created

def setup_world_and_sun():
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Medieval_World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputWorld')
    output.location = (400, 0)

    bg = nodes.new(type='ShaderNodeBackground')
    bg.location = (150, 0)
    bg.inputs['Color'].default_value = (0.50, 0.65, 0.85, 1.0) # Atmospheric medieval sky
    bg.inputs['Strength'].default_value = 0.90
    links.new(bg.outputs['Background'], output.inputs['Surface'])

    # Key Sunlight: warm medieval afternoon lighting
    light_col = bpy.data.collections.get("Lighting")
    sun_data = bpy.data.lights.get("Sun_Medieval_Day")
    if not sun_data:
        sun_data = bpy.data.lights.new(name="Sun_Medieval_Day", type='SUN')
    sun_data.energy = 4.5
    sun_data.color = (1.0, 0.95, 0.86)
    sun_data.angle = math.radians(2.0) # Soft realistic shadows

    sun_obj = bpy.data.objects.get("Sun_Medieval_Day")
    if not sun_obj:
        sun_obj = bpy.data.objects.new("Sun_Medieval_Day", sun_data)
        if light_col:
            light_col.objects.link(sun_obj)
        else:
            bpy.context.scene.collection.objects.link(sun_obj)

    # Sun angled from high front-left to cast rich architectural cast shadows across timber frames
    sun_obj.rotation_euler = (math.radians(50.0), math.radians(25.0), math.radians(-50.0))

    # Fill sun light
    fill_data = bpy.data.lights.get("Sun_Fill_Soft")
    if not fill_data:
        fill_data = bpy.data.lights.new(name="Sun_Fill_Soft", type='SUN')
    fill_data.energy = 0.75
    fill_data.color = (0.62, 0.75, 0.95)
    fill_obj = bpy.data.objects.get("Sun_Fill_Soft")
    if not fill_obj:
        fill_obj = bpy.data.objects.new("Sun_Fill_Soft", fill_data)
        if light_col:
            light_col.objects.link(fill_obj)
        else:
            bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(55.0), math.radians(-15.0), math.radians(130.0))

def create_camera(name, location, target_pos, focal_length=50.0, col=None):
    cam_data = bpy.data.cameras.get(name)
    if not cam_data:
        cam_data = bpy.data.cameras.new(name)
    cam_data.lens = focal_length
    cam_data.clip_start = 0.1
    cam_data.clip_end = 1000.0

    cam_obj = bpy.data.objects.get(name)
    if not cam_obj:
        cam_obj = bpy.data.objects.new(name, cam_data)
        if col:
            col.objects.link(cam_obj)
        else:
            bpy.context.scene.collection.objects.link(cam_obj)

    cam_obj.location = Vector(location)

    # Point directly at target_pos
    direction = Vector(target_pos) - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    return cam_obj

def setup_all_cameras():
    cam_col = bpy.data.collections.get("Cameras")
    cameras = {}

    cottage_center = Vector((0.0, 0.0, 4.2))

    # 1. Three-Quarter Cinematic Overview
    cameras["Cam_ThreeQuarter"] = create_camera(
        name="Cam_ThreeQuarter",
        location=(12.0, -14.5, 7.8),
        target_pos=(0.0, -0.5, 4.0),
        focal_length=45.0,
        col=cam_col
    )

    # 2. Front Elevation View
    cameras["Cam_Front"] = create_camera(
        name="Cam_Front",
        location=(0.0, -16.5, 4.4),
        target_pos=(0.0, -1.0, 4.2),
        focal_length=55.0,
        col=cam_col
    )

    # 3. Right Side Elevation View (Chimney Stack side)
    cameras["Cam_Side_Right"] = create_camera(
        name="Cam_Side_Right",
        location=(17.0, 0.0, 4.8),
        target_pos=(0.0, 0.0, 4.5),
        focal_length=55.0,
        col=cam_col
    )

    # 4. Left Side Elevation View (Barrels & Windows)
    cameras["Cam_Side_Left"] = create_camera(
        name="Cam_Side_Left",
        location=(-17.0, 0.0, 4.8),
        target_pos=(0.0, 0.0, 4.5),
        focal_length=55.0,
        col=cam_col
    )

    # 5. Top View (Roof Plan)
    cameras["Cam_Top"] = create_camera(
        name="Cam_Top",
        location=(0.0, 0.01, 20.0),
        target_pos=(0.0, 0.0, 0.0),
        focal_length=48.0,
        col=cam_col
    )

    # 6. Eye-Level Entrance View (Human Scale: 1.7m Z, looking at front door & porch canopy)
    cameras["Cam_Entrance_EyeLevel"] = create_camera(
        name="Cam_Entrance_EyeLevel",
        location=(2.2, -8.2, 1.7),
        target_pos=(-0.6, -4.0, 2.3),
        focal_length=35.0,
        col=cam_col
    )

    # Set active camera to ThreeQuarter
    bpy.context.scene.camera = cameras["Cam_ThreeQuarter"]
    return cameras

def setup_ground_plane():
    terrain_col = bpy.data.collections.get("99_TERRAIN_ATMOSPHERE")
    plane_name = "Terrain_Village_Base"
    plane_obj = bpy.data.objects.get(plane_name)
    if not plane_obj:
        bpy.ops.mesh.primitive_plane_add(size=70.0, location=(0, 0, 0))
        plane_obj = bpy.context.active_object
        plane_obj.name = plane_name
        for col in list(plane_obj.users_collection):
            col.objects.unlink(plane_obj)
        if terrain_col:
            terrain_col.objects.link(plane_obj)

    mat = bpy.data.materials.get("M_Ground_Mud")
    if not mat:
        mat = bpy.data.materials.new("M_Ground_Mud")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.12, 0.10, 0.08, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.95
    if mat and len(plane_obj.data.materials) == 0:
        plane_obj.data.materials.append(mat)

def run_scene_setup():
    # Remove any default objects
    for name in ["Cube", "Light", "Camera"]:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    setup_units_and_color()
    setup_cycles_engine(samples=128)
    setup_collections_hierarchy()
    setup_world_and_sun()
    setup_all_cameras()
    setup_ground_plane()
    print("Scene setup completed successfully.")

if __name__ == '__main__':
    run_scene_setup()
