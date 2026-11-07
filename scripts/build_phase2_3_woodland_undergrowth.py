import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler

def create_or_get_col(name, parent_name=None):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        if parent_name and bpy.data.collections.get(parent_name):
            bpy.data.collections[parent_name].children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col

def get_terrain_z(x, y, default_z=0.0):
    deps = bpy.context.evaluated_depsgraph_get()
    ray_origin = Vector((x, y, 40.0))
    ray_dir = Vector((0, 0, -1))
    hit, loc, _, _, obj, _ = bpy.context.scene.ray_cast(deps, ray_origin, ray_dir, distance=60.0)
    if hit and obj and ("Terrain" in obj.name or "Ground" in obj.name or "Mountain" in obj.name or "River" in obj.name):
        return loc.z
    return default_z

def load_prototypes():
    lib_col = create_or_get_col("00_NATURE_PROTOTYPE_LIBRARY")
    lib_col.hide_viewport = True
    lib_col.hide_render = True

    prototypes = {}

    def fetch(filepath, obj_name, key):
        if key in prototypes and prototypes[key] is not None:
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
            return obj
        return None

    oak_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\oak\tree_small_02\tree_small_02_1k.blend"
    fir_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\fir\fir_tree_01\fir_tree_01_1k.blend"
    pine_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\pine\pine_tree_01\pine_tree_01_1k.blend"
    sapling_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\trees\fir_sapling\fir_sapling_1k.blend"
    fern_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\ferns\fern_02\fern_02_1k.blend"
    shrub1_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\bushes\shrub_01\shrub_01_1k.blend"
    shrub2_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\bushes\shrub_02\shrub_02_1k.blend"
    rock1_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\rocks\rock_moss_set_01\rock_moss_set_01_1k.blend"
    rock2_path = r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\rocks\rock_moss_set_02\rock_moss_set_02_1k.blend"

    fetch(oak_path, 'tree_small_02_LOD1', 'oak')
    fetch(fir_path, 'fir_tree_01_a_LOD1', 'fir_a')
    fetch(fir_path, 'fir_tree_01_b_LOD1', 'fir_b')
    fetch(pine_path, 'pine_tree_01_a_LOD1', 'pine_a')
    fetch(pine_path, 'pine_tree_01_b_LOD1', 'pine_b')

    # Saplings
    fetch(sapling_path, 'fir_sapling_a', 'sapling_a')
    fetch(sapling_path, 'fir_sapling_b', 'sapling_b')
    fetch(sapling_path, 'fir_sapling_c', 'sapling_c')

    # Ferns
    fetch(fern_path, 'fern_02_a', 'fern_a')
    fetch(fern_path, 'fern_02_b', 'fern_b')
    fetch(fern_path, 'fern_02_c', 'fern_c')
    fetch(fern_path, 'fern_02_d', 'fern_d')

    # Shrubs
    fetch(shrub1_path, 'shrub_01_a_LOD1', 'shrub_a')
    fetch(shrub1_path, 'shrub_01_c_LOD1', 'shrub_c')
    fetch(shrub2_path, 'shrub_02_a_LOD1', 'shrub_d')

    # Rocks
    for i in range(1, 7):
        fetch(rock1_path, f'rock_moss_set_01_rock{i:02d}', f'moss_rock_{i}')
    for i in range(7, 14):
        fetch(rock2_path, f'rock_moss_set_02_rock{i:02d}', f'moss_rock_{i}')

    print(f"Loaded {len(prototypes)} nature prototypes into library.")
    return prototypes

def build_dense_woodland_and_undergrowth():
    print("==================================================")
    print("BUILDING DENSE WOODLAND, UNDERGROWTH & MOSSY ROCKS")
    print("==================================================")

    prototypes = load_prototypes()

    nature_col = create_or_get_col("06_ENVIRONMENT_NATURE")
    forest_col = create_or_get_col("06_ENVIRONMENT_FOREST_EXPANSION", "06_ENVIRONMENT_NATURE")

    # Clean existing expansion objects
    for o in list(forest_col.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    random.seed(101)

    conifer_keys = ['fir_a', 'fir_b', 'pine_a', 'pine_b']
    sapling_keys = ['sapling_a', 'sapling_b', 'sapling_c']
    fern_keys = ['fern_a', 'fern_b', 'fern_c', 'fern_d']
    shrub_keys = ['shrub_a', 'shrub_c', 'shrub_d']
    rock_keys = [f'moss_rock_{i}' for i in range(1, 14)]

    # 1. Outer Northern Mountain Slopes Forest (Dense backdrop)
    print("Planting Northern Mountain Forest...")
    north_tree_count = 35
    for i in range(north_tree_count):
        x = random.uniform(-45.0, 35.0)
        y = random.uniform(32.0, 58.0)
        # Avoid river channel
        if 18.0 <= y <= 26.0 and -25.0 <= x <= 15.0:
            continue
        z = get_terrain_z(x, y, 1.5)
        
        pkey = random.choice(conifer_keys)
        proto = prototypes.get(pkey)
        if proto:
            obj = bpy.data.objects.new(f"Forest_North_Conifer_{i:02d}", proto.data)
            forest_col.objects.link(obj)
            scale_fac = random.uniform(0.7, 1.25)
            obj.location = Vector((x, y, z))
            obj.rotation_euler = Euler((0, 0, random.uniform(0, 2 * math.pi)), 'XYZ')
            obj.scale = Vector((scale_fac, scale_fac, scale_fac))

            # Add 1-2 young saplings around mature trees
            if random.random() < 0.65:
                skey = random.choice(sapling_keys)
                sproto = prototypes.get(skey)
                if sproto:
                    sx = x + random.uniform(-2.5, 2.5)
                    sy = y + random.uniform(-2.5, 2.5)
                    sz = get_terrain_z(sx, sy, z)
                    sobj = bpy.data.objects.new(f"Forest_North_Sapling_{i:02d}", sproto.data)
                    forest_col.objects.link(sobj)
                    sscale = random.uniform(0.8, 1.4)
                    sobj.location = Vector((sx, sy, sz))
                    sobj.rotation_euler = Euler((0, 0, random.uniform(0, 2 * math.pi)), 'XYZ')
                    sobj.scale = Vector((sscale, sscale, sscale))

    # 2. Western Ridge & Watchtower Backdrop Forest
    print("Planting Western Forest Ridge...")
    west_tree_count = 25
    for i in range(west_tree_count):
        x = random.uniform(-58.0, -32.0)
        y = random.uniform(-35.0, 15.0)
        # Keep clearings around watchtower
        if (-22.0 <= x <= -14.0) and (-28.0 <= y <= -18.0):
            continue
        z = get_terrain_z(x, y, 0.5)

        # Mix of oaks and conifers
        pkey = 'oak' if random.random() < 0.35 else random.choice(conifer_keys)
        proto = prototypes.get(pkey)
        if proto:
            obj = bpy.data.objects.new(f"Forest_West_{i:02d}", proto.data)
            forest_col.objects.link(obj)
            scale_fac = random.uniform(0.8, 1.2)
            obj.location = Vector((x, y, z))
            obj.rotation_euler = Euler((0, 0, random.uniform(0, 2 * math.pi)), 'XYZ')
            obj.scale = Vector((scale_fac, scale_fac, scale_fac))

    # 3. Eastern Meadows & Slopes
    print("Planting Eastern Valley Trees...")
    east_tree_count = 20
    for i in range(east_tree_count):
        x = random.uniform(25.0, 50.0)
        y = random.uniform(-40.0, 10.0)
        # Keep farming area clearing
        if (20.0 <= x <= 32.0) and (-35.0 <= y <= -20.0):
            continue
        z = get_terrain_z(x, y, 0.2)
        pkey = 'oak' if random.random() < 0.45 else random.choice(conifer_keys)
        proto = prototypes.get(pkey)
        if proto:
            obj = bpy.data.objects.new(f"Forest_East_{i:02d}", proto.data)
            forest_col.objects.link(obj)
            scale_fac = random.uniform(0.75, 1.15)
            obj.location = Vector((x, y, z))
            obj.rotation_euler = Euler((0, 0, random.uniform(0, 2 * math.pi)), 'XYZ')
            obj.scale = Vector((scale_fac, scale_fac, scale_fac))

    # 4. Mossy Rock Clusters along Riverbanks & Glades
    print("Placing Mossy Rocks...")
    rock_spots = [
        # Riverbanks
        (12.0, 26.5), (8.5, 27.2), (1.5, 24.5), (-5.5, 27.0), (-16.5, 27.5),
        (-22.5, 26.5), (-28.0, 24.0), (14.0, 21.5), (10.5, 21.0), (3.0, 17.5),
        # Watchtower base & cliff
        (-19.5, -24.5), (-14.0, -28.0), (-22.0, -18.0),
        # Forest glade
        (-35.0, -10.0), (-42.0, -15.0), (32.0, -8.0)
    ]
    for idx, (rx, ry) in enumerate(rock_spots):
        rz = get_terrain_z(rx, ry, -0.2)
        rkey = random.choice(rock_keys)
        rproto = prototypes.get(rkey)
        if rproto:
            robj = bpy.data.objects.new(f"Mossy_Rock_Cluster_{idx:02d}", rproto.data)
            forest_col.objects.link(robj)
            rscale = random.uniform(1.2, 2.2)
            robj.location = Vector((rx, ry, rz))
            robj.rotation_euler = Euler((
                random.uniform(-0.2, 0.2),
                random.uniform(-0.2, 0.2),
                random.uniform(0, 2 * math.pi)
            ), 'XYZ')
            robj.scale = Vector((rscale, rscale, rscale))

    # 5. Woodland Ferns & Understory Shrubs
    print("Placing Ferns and Understory...")
    fern_count = 35
    for i in range(fern_count):
        # Cluster near rocks, trees, and river margins
        base_spot = random.choice(rock_spots)
        fx = base_spot[0] + random.uniform(-3.0, 3.0)
        fy = base_spot[1] + random.uniform(-3.0, 3.0)
        fz = get_terrain_z(fx, fy, 0.0)

        fkey = random.choice(fern_keys)
        fproto = prototypes.get(fkey)
        if fproto:
            fobj = bpy.data.objects.new(f"Woodland_Fern_{i:02d}", fproto.data)
            forest_col.objects.link(fobj)
            fscale = random.uniform(0.8, 1.5)
            fobj.location = Vector((fx, fy, fz))
            fobj.rotation_euler = Euler((0, 0, random.uniform(0, 2 * math.pi)), 'XYZ')
            fobj.scale = Vector((fscale, fscale, fscale))

    print("Dense woodland, undergrowth & mossy rocks build complete!")

if __name__ == "__main__":
    build_dense_woodland_and_undergrowth()

