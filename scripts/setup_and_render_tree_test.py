import bpy
import math
from mathutils import Vector, Euler

def setup_tree_test_scene():
    print("Setting up comprehensive realistic tree test scene...")

    col_name = "06_ENVIRONMENT_TEST_REALISTIC"
    test_col = bpy.data.collections.get(col_name)
    if not test_col:
        test_col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(test_col)

    # Clean existing test objects in this collection
    for obj in list(test_col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    oak_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\oak\tree_small_02\tree_small_02_1k.blend"
    fir_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\fir\fir_tree_01\fir_tree_01_1k.blend"
    boulder_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\rocks\boulder_01\boulder_01_1k.blend"

    # 1. Oak tree (LOD1)
    with bpy.data.libraries.load(oak_blend, link=False) as (df, dt):
        dt.objects = ['tree_small_02_LOD1']
    oak_obj = bpy.data.objects.get('tree_small_02_LOD1')
    if oak_obj:
        if oak_obj.name not in test_col.objects:
            test_col.objects.link(oak_obj)
        oak_obj.name = "Test_Realistic_Oak_01"
        oak_obj.location = Vector((9.8, 23.8, 0.2))
        oak_obj.rotation_euler = Euler((0, 0, math.radians(45)), 'XYZ')
        oak_obj.scale = Vector((1.1, 1.1, 1.1))

    # 2. Fir tree (LOD1)
    with bpy.data.libraries.load(fir_blend, link=False) as (df, dt):
        dt.objects = ['fir_tree_01_a_LOD1']
    fir_obj = bpy.data.objects.get('fir_tree_01_a_LOD1')
    if fir_obj:
        if fir_obj.name not in test_col.objects:
            test_col.objects.link(fir_obj)
        fir_obj.name = "Test_Realistic_Fir_01"
        fir_obj.location = Vector((13.2, 25.5, 0.4))
        fir_obj.rotation_euler = Euler((0, 0, math.radians(70)), 'XYZ')
        fir_obj.scale = Vector((0.75, 0.75, 0.75))

    # 3. Boulder (LOD0) in foreground near water
    with bpy.data.libraries.load(boulder_blend, link=False) as (df, dt):
        dt.objects = ['boulder_01_LOD0']
    boulder_obj = bpy.data.objects.get('boulder_01_LOD0')
    if boulder_obj:
        if boulder_obj.name not in test_col.objects:
            test_col.objects.link(boulder_obj)
        boulder_obj.name = "Test_Realistic_Boulder_01"
        boulder_obj.location = Vector((7.6, 20.2, 0.3))
        boulder_obj.rotation_euler = Euler((math.radians(12), math.radians(-15), math.radians(40)), 'XYZ')
        boulder_obj.scale = Vector((1.35, 1.35, 1.35))

    # 4. Hide obstructing stylized foreground bush
    bush = bpy.data.objects.get("Bush_Foliage_09")
    if bush:
        bush.hide_render = True

    # 5. Set up Camera
    cam_name = "Cam_Test_Realistic_Trees"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
    
    cam_obj.data.lens = 32
    cam_obj.data.dof.use_dof = True
    cam_obj.data.dof.focus_object = oak_obj
    cam_obj.data.dof.aperture_fstop = 5.6

    cam_obj.location = Vector((4.8, 15.2, 2.3))
    
    target = Vector((10.5, 23.5, 3.2))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    bpy.context.scene.camera = cam_obj

    # 6. Lighting: Ensure daylight sun is active
    sun = bpy.data.objects.get("Sun_Daylight")
    if sun:
        sun.hide_render = False
        sun.data.energy = 5.0
        sun.rotation_euler = Euler((math.radians(48), math.radians(18), math.radians(-38)), 'XYZ')

    # 7. Render Settings: Cycles
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.filepath = r"c:\Users\ashwi\Documents\Medieval_Village_Project\renders\Test_Realistic_Trees_Preview.png"

    print("Comprehensive realistic tree test scene ready.")

if __name__ == "__main__":
    setup_tree_test_scene()
