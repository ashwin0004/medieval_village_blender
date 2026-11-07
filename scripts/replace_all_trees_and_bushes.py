import bpy
import math
import random
import os
from mathutils import Vector, Euler

def replace_trees_and_bushes():
    print("==================================================")
    print("STARTING FULL REPLACEMENT OF TREES AND BUSHES")
    print("==================================================")

    # 1. Paths to asset blend files
    oak_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\oak\tree_small_02\tree_small_02_1k.blend"
    fir_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\fir\fir_tree_01\fir_tree_01_1k.blend"
    pine_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\pine\pine_tree_01\pine_tree_01_1k.blend"
    shrub1_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\bushes\shrub_01\shrub_01_1k.blend"
    shrub2_blend = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\bushes\shrub_02\shrub_02_1k.blend"

    # 2. Collections
    nature_col = bpy.data.collections.get("06_ENVIRONMENT_NATURE")
    if not nature_col:
        nature_col = bpy.data.collections.new("06_ENVIRONMENT_NATURE")
        bpy.context.scene.collection.children.link(nature_col)

    backup_col = bpy.data.collections.get("06_ENVIRONMENT_NATURE_LEGACY_BACKUP")
    if not backup_col:
        backup_col = bpy.data.collections.new("06_ENVIRONMENT_NATURE_LEGACY_BACKUP")
        bpy.context.scene.collection.children.link(backup_col)
    backup_col.hide_viewport = True
    backup_col.hide_render = True

    lib_col = bpy.data.collections.get("00_NATURE_PROTOTYPE_LIBRARY")
    if not lib_col:
        lib_col = bpy.data.collections.new("00_NATURE_PROTOTYPE_LIBRARY")
        bpy.context.scene.collection.children.link(lib_col)
    lib_col.hide_viewport = True
    lib_col.hide_render = True

    # 3. Load Prototypes into Library
    prototypes = {}

    def load_proto(filepath, obj_name, key):
        if key in prototypes:
            return prototypes[key]
        with bpy.data.libraries.load(filepath, link=False) as (df, dt):
            if obj_name in df.objects:
                dt.objects = [obj_name]
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if obj.name not in lib_col.objects:
                lib_col.objects.link(obj)
            obj.hide_viewport = True
            obj.hide_render = True
            prototypes[key] = obj
            print(f"Loaded prototype [{key}]: {obj_name} ({len(obj.data.vertices)} verts)")
            return obj
        print(f"FAILED to load prototype {obj_name} from {filepath}")
        return None

    # Oak
    load_proto(oak_blend, 'tree_small_02_LOD1', 'oak')

    # Fir variants
    load_proto(fir_blend, 'fir_tree_01_a_LOD1', 'fir_a')
    load_proto(fir_blend, 'fir_tree_01_b_LOD1', 'fir_b')
    load_proto(fir_blend, 'fir_tree_01_c_LOD1', 'fir_c')

    # Pine variants
    load_proto(pine_blend, 'pine_tree_01_a_LOD1', 'pine_a')
    load_proto(pine_blend, 'pine_tree_01_b_LOD1', 'pine_b')
    load_proto(pine_blend, 'pine_tree_01_c_LOD1', 'pine_c')

    # Bush variants
    load_proto(shrub1_blend, 'shrub_01_a_LOD1', 'shrub1_a')
    load_proto(shrub1_blend, 'shrub_01_c_LOD1', 'shrub1_c')
    load_proto(shrub1_blend, 'shrub_01_f_LOD1', 'shrub1_f')
    load_proto(shrub2_blend, 'shrub_02_a_LOD1', 'shrub2_a')
    load_proto(shrub2_blend, 'shrub_02_b_LOD1', 'shrub2_b')
    load_proto(shrub2_blend, 'shrub_02_c_LOD1', 'shrub2_c')

    conifer_keys = ['fir_a', 'fir_b', 'fir_c', 'pine_a', 'pine_b', 'pine_c']
    shrub_keys = ['shrub1_a', 'shrub1_c', 'shrub1_f', 'shrub2_a', 'shrub2_b', 'shrub2_c']

    # 4. Find all existing legacy trees and bushes
    legacy_pines = [o for o in list(bpy.data.objects) if o.name.startswith("Pine_Tree_") and not o.name.startswith("Pine_Tree_Realistic_")]
    legacy_oaks = [o for o in list(bpy.data.objects) if o.name.startswith("Oak_Tree_") and not o.name.startswith("Oak_Tree_Realistic_")]
    legacy_bushes = [o for o in list(bpy.data.objects) if o.name.startswith("Bush_Foliage_") and not o.name.startswith("Bush_Realistic_")]

    print(f"Found {len(legacy_pines)} legacy pines, {len(legacy_oaks)} legacy oaks, {len(legacy_bushes)} legacy bushes.")

    # Seed for deterministic, beautifully balanced organic variation
    random.seed(42)

    # Clean previous realistic replacements if any exist
    for o in list(nature_col.objects):
        if o.name.startswith("Realistic_"):
            bpy.data.objects.remove(o, do_unlink=True)

    # 5. Replace Oaks
    oak_proto = prototypes.get('oak')
    for idx, old_oak in enumerate(legacy_oaks):
        loc = old_oak.location.copy()
        # Move old to backup
        for c in list(old_oak.users_collection):
            c.objects.unlink(old_oak)
        backup_col.objects.link(old_oak)
        old_oak.hide_viewport = True
        old_oak.hide_render = True

        if oak_proto:
            new_name = f"Realistic_Oak_{idx:02d}"
            new_obj = bpy.data.objects.new(new_name, oak_proto.data)
            nature_col.objects.link(new_obj)
            
            # Ground placement & subtle random rotation / scale
            yaw = random.uniform(0, 2 * math.pi)
            scale_fac = random.uniform(0.95, 1.25)
            new_obj.location = Vector((loc.x, loc.y, loc.z))
            new_obj.rotation_euler = Euler((0, 0, yaw), 'XYZ')
            new_obj.scale = Vector((scale_fac, scale_fac, scale_fac))

    # 6. Replace Pines (Mix of Scots Pine & Alpine Fir)
    for idx, old_pine in enumerate(legacy_pines):
        loc = old_pine.location.copy()
        for c in list(old_pine.users_collection):
            c.objects.unlink(old_pine)
        backup_col.objects.link(old_pine)
        old_pine.hide_viewport = True
        old_pine.hide_render = True

        proto_key = random.choice(conifer_keys)
        proto = prototypes.get(proto_key)
        if proto:
            new_name = f"Realistic_Conifer_{idx:02d}"
            new_obj = bpy.data.objects.new(new_name, proto.data)
            nature_col.objects.link(new_obj)

            yaw = random.uniform(0, 2 * math.pi)
            if 'fir' in proto_key:
                scale_fac = random.uniform(0.65, 1.05)
            else:
                scale_fac = random.uniform(0.50, 0.75)

            new_obj.location = Vector((loc.x, loc.y, loc.z))
            new_obj.rotation_euler = Euler((0, 0, yaw), 'XYZ')
            new_obj.scale = Vector((scale_fac, scale_fac, scale_fac))

    # 7. Replace Bushes
    for idx, old_bush in enumerate(legacy_bushes):
        loc = old_bush.location.copy()
        for c in list(old_bush.users_collection):
            c.objects.unlink(old_bush)
        backup_col.objects.link(old_bush)
        old_bush.hide_viewport = True
        old_bush.hide_render = True

        shrub_key = random.choice(shrub_keys)
        shrub_proto = prototypes.get(shrub_key)
        if shrub_proto:
            new_name = f"Realistic_Bush_{idx:02d}"
            new_obj = bpy.data.objects.new(new_name, shrub_proto.data)
            nature_col.objects.link(new_obj)

            yaw = random.uniform(0, 2 * math.pi)
            scale_fac = random.uniform(0.9, 1.4)
            new_obj.location = Vector((loc.x, loc.y, loc.z))
            new_obj.rotation_euler = Euler((0, 0, yaw), 'XYZ')
            new_obj.scale = Vector((scale_fac, scale_fac, scale_fac))

    # Clean up test collection
    test_col = bpy.data.collections.get("06_ENVIRONMENT_TEST_REALISTIC")
    if test_col:
        for o in list(test_col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(test_col)

    print("==================================================")
    print("FULL REPLACEMENT COMPLETE!")
    print(f"Created: {len(legacy_oaks)} realistic oaks, {len(legacy_pines)} realistic conifers, {len(legacy_bushes)} realistic bushes.")
    print("==================================================")

if __name__ == "__main__":
    replace_trees_and_bushes()

