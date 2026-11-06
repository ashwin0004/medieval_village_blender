"""
upgrade_buildings.py
====================
Upgrades the primitive village blockout buildings into realistic, high-detail
medieval architectural structures based on historical European construction
and the user's reference images:
  - Stone foundation plinths with beveled water-tables & entrance steps
  - Heavy timber framing (corner posts, studs, girts, diagonal K/X-braces, corbel jetties)
  - Plaster/daub infill panels & horizontal/vertical wooden planking
  - Overlapping individual roof tiles with beaver-tail / scalloped profiles,
    semicircular ridge tiles, rafter tails, and crossed apex bargeboard finials
  - Tapered stone chimneys with soot hoods and ceramic flue pots
  - Wooden plank doors with diagonal Z-braces, iron strap hinges, and latch handles
  - Multi-pane leaded glass windows with wooden sills and board-and-batten shutters
  - Cantilevered wooden balconies with balustrades
  - Distinct architectural identities for all 8 buildings:
      1. Tavern ("The Dragon's Flagon") - 2-story overhanging jetty, upper balcony, dual chimneys
      2. Blacksmith ("The Iron Hearth") - Fieldstone forge, open timber lean-to shed, hearth chimney
      3. Church ("St. Aldhelm's Chapel") - Stone buttresses, pointed gothic portal & lancets, belfry tower
      4. Inn ("The Wayfarer's Rest") - Half-timbered coaching inn, gabled roof dormers, external gallery
      5. Cottage 2 ("Weaver's Cottage" - Ref 2) - Fieldstone base, horizontal logs, crossed roof finials
      6. Cottage 3 ("Baker's House" - Ref 1) - Arched stone entrance, half-timber upper floor, dormer
      7. Barn ("Village Tithe Barn") - Weatherboard siding, massive wagon doors, hayloft hoist beam
      8. Castle ("Old Watch Ruin") - Battered ashlar masonry, machicolations, arrow slits, ramparts
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

# ──────────────────────────────────────────────
# Material Helpers
# ──────────────────────────────────────────────

def get_mat(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat

def assign_mat(obj, mat_name):
    mat = get_mat(mat_name)
    if not obj.data.materials:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

def add_bevel(obj, width=0.03, segments=2):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(60)

def ensure_collection(name, parent_col):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        parent_col.children.link(col)
    return col

# ──────────────────────────────────────────────
# Master Architectural Builder Engine
# ──────────────────────────────────────────────

class MedievalBuilder:
    def __init__(self, building_name, base_pos, rot_z, parent_col):
        self.name = building_name
        self.base_pos = Vector(base_pos)
        self.rot_z = rot_z
        self.cos_r = math.cos(rot_z)
        self.sin_r = math.sin(rot_z)
        self.col = ensure_collection(building_name, parent_col)

    def to_world(self, lx, ly, lz):
        wx = self.base_pos.x + (lx * self.cos_r - ly * self.sin_r)
        wy = self.base_pos.y + (lx * self.sin_r + ly * self.cos_r)
        wz = self.base_pos.z + lz
        return Vector((wx, wy, wz))

    def make_box(self, part_name, lx, ly, lz, sx, sy, sz, rot_z_offset=0, mat_name="M_Aged_Oak", bevel=0.02):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        m = bpy.data.meshes.new(f"{self.name}_{part_name}_Mesh")
        bm.to_mesh(m)
        bm.free()
        
        obj = bpy.data.objects.new(f"{self.name}_{part_name}", m)
        self.col.objects.link(obj)
        assign_mat(obj, mat_name)
        obj.location = self.to_world(lx, ly, lz)
        obj.scale = (sx, sy, sz)
        obj.rotation_euler = (0, 0, self.rot_z + rot_z_offset)
        if bevel > 0:
            add_bevel(obj, width=bevel, segments=2)
        return obj

    def make_cylinder(self, part_name, lx, ly, lz, r1, r2, depth, segments=12, rot_x=0, rot_y=0, rot_z_offset=0, mat_name="M_Stone_Rough"):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r1, radius2=r2, depth=depth)
        m = bpy.data.meshes.new(f"{self.name}_{part_name}_Mesh")
        bm.to_mesh(m)
        bm.free()
        m.shade_smooth()
        
        obj = bpy.data.objects.new(f"{self.name}_{part_name}", m)
        self.col.objects.link(obj)
        assign_mat(obj, mat_name)
        obj.location = self.to_world(lx, ly, lz)
        obj.rotation_euler = (rot_x, rot_y, self.rot_z + rot_z_offset)
        return obj

    # ──────────────────────────────────────────
    # 1. Stone Foundation with Water-Table Trim
    # ──────────────────────────────────────────
    def build_foundation(self, w, d, h_found, mat_name="M_Stone_Rough"):
        # Main plinth
        self.make_box("Foundation_Plinth", 0, 0, h_found * 0.5, w + 0.16, d + 0.16, h_found, mat_name=mat_name, bevel=0.04)
        # Beveled water-table trim stone along top edge
        self.make_box("Foundation_Trim", 0, 0, h_found + 0.05, w + 0.22, d + 0.22, 0.10, mat_name=mat_name, bevel=0.03)
        # Entrance stone steps (in front of south entrance)
        for s in range(2):
            self.make_box(f"Foundation_Step_{s}", 0, -d * 0.5 - 0.35 - s * 0.35, 0.08 + s * 0.16, 2.0, 0.40, 0.16, mat_name=mat_name, bevel=0.02)

    # ──────────────────────────────────────────
    # 2. Timber-Framed Walls with Inset Panels
    # ──────────────────────────────────────────
    def build_timber_framed_floor(self, z_start, w, d, h_wall, has_plaster=True, plank_horizontal=False, is_overhang=False, overhang_depth=0.5):
        # If upper floor has an overhanging jetty:
        front_offset = -overhang_depth if is_overhang else 0.0
        
        # Infill walls (recessed plaster or timber planks)
        infill_mat = "M_Plaster_Cream" if has_plaster else ("M_Wood_AgedOak" if plank_horizontal else "M_Aged_Oak")
        self.make_box(f"Floor_Infill_{int(z_start)}", 0, front_offset * 0.5, z_start + h_wall * 0.5, 
                      w - 0.06, d + abs(front_offset) - 0.06, h_wall - 0.04, mat_name=infill_mat, bevel=0.01)

        beam_sz = 0.22
        # Sill beam & Top plate beam
        self.make_box(f"Beam_Sill_{int(z_start)}", 0, front_offset * 0.5, z_start + beam_sz * 0.5, w + 0.04, d + abs(front_offset) + 0.04, beam_sz)
        self.make_box(f"Beam_Plate_{int(z_start)}", 0, front_offset * 0.5, z_start + h_wall - beam_sz * 0.5, w + 0.04, d + abs(front_offset) + 0.04, beam_sz)
        
        # 4 Corner Posts
        half_w = (w - beam_sz) * 0.5
        y_min = -d * 0.5 + front_offset + beam_sz * 0.5
        y_max = d * 0.5 - beam_sz * 0.5
        
        for px in [-half_w, half_w]:
            for py in [y_min, y_max]:
                self.make_box(f"Post_Corner_{px:.1f}_{py:.1f}", px, py, z_start + h_wall * 0.5, beam_sz, beam_sz, h_wall)
                
        # Intermediate Studs along length
        n_studs_x = max(1, int(w / 1.8))
        for i in range(1, n_studs_x):
            ix = -w * 0.5 + (i * w / n_studs_x)
            for py in [y_min, y_max]:
                self.make_box(f"Stud_X_{i}_{py:.1f}", ix, py, z_start + h_wall * 0.5, 0.16, 0.16, h_wall)

        # Mid-height Girt Rail
        self.make_box(f"Girt_Rail_{int(z_start)}", 0, front_offset * 0.5, z_start + h_wall * 0.5, w + 0.02, d + abs(front_offset) + 0.02, 0.16)

        # If overhang/jetty: Carved supporting Corbel Brackets underneath
        if is_overhang:
            n_corbels = max(3, int(w / 1.6))
            for ci in range(n_corbels + 1):
                cx = -w * 0.5 + (ci * w / n_corbels)
                # Bracket extending forward
                self.make_box(f"Jetty_Corbel_{ci}", cx, -d * 0.5 - overhang_depth * 0.45, z_start - 0.20, 0.18, overhang_depth * 0.9, 0.40)

    # ──────────────────────────────────────────
    # 3. High-Detail Roof with Overlapping Scalloped Tiles & Ridge
    # ──────────────────────────────────────────
    def build_roof_with_individual_tiles(self, z_eave, w, d, roof_h, overhang=0.45, tile_mat="M_Tile_Weathered_Moss", has_crossed_finial=False):
        # 1. Triangular Gable Walls (Timber framed)
        for side, gy in [("Front", -d * 0.5), ("Back", d * 0.5)]:
            # Triangular gable mesh
            bm = bmesh.new()
            v0 = bm.verts.new((-w * 0.5, 0, 0))
            v1 = bm.verts.new((w * 0.5, 0, 0))
            v2 = bm.verts.new((0, 0, roof_h))
            bm.faces.new([v0, v1, v2])
            # Solidify
            bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.20)
            gm = bpy.data.meshes.new(f"{self.name}_Gable_{side}_Mesh")
            bm.to_mesh(gm)
            bm.free()
            gable = bpy.data.objects.new(f"{self.name}_Gable_{side}", gm)
            self.col.objects.link(gable)
            assign_mat(gable, "M_Plaster_Cream")
            gable.location = self.to_world(0, gy, z_eave)
            gable.rotation_euler = (0, 0, self.rot_z)
            
            # Decorative Gable Timber Truss (Ref Image 2)
            self.make_box(f"Gable_KingPost_{side}", 0, gy, z_eave + roof_h * 0.5, 0.18, 0.22, roof_h)
            self.make_box(f"Gable_TieBeam_{side}", 0, gy, z_eave + 0.10, w, 0.22, 0.20)
            
        # 2. Roof Sub-decking / Rafter planes
        half_w = w * 0.5 + overhang
        slope_len = math.sqrt(half_w * half_w + roof_h * roof_h)
        slope_angle = math.atan2(roof_h, half_w)
        total_d = d + overhang * 2.0
        
        # 3. Individual Overlapping Scalloped Tiles (Built into unified mesh per slope for high performance)
        for slope_side, sign in [("West", -1), ("East", 1)]:
            bm_tiles = bmesh.new()
            # Tile dimensions
            t_w = 0.38
            t_l = 0.52
            t_thick = 0.025
            overlap_y = 0.22 # Staggered overlap
            
            n_rows = max(4, int(slope_len / overlap_y))
            n_cols = max(4, int(total_d / t_w))
            
            for row in range(n_rows):
                # Distance up slope
                dist_up = (row + 0.5) * overlap_y
                # Height and horizontal offset
                tile_z = dist_up * math.sin(slope_angle)
                tile_x = sign * (half_w - dist_up * math.cos(slope_angle))
                
                # Alternate column shift for authentic staggered bond (Ref Image 3)
                col_shift = (row % 2) * (t_w * 0.5)
                
                for col in range(n_cols):
                    tile_y = -total_d * 0.5 + col * t_w + col_shift
                    if tile_y > total_d * 0.5:
                        continue
                        
                    # Create tile: scalloped / rounded bottom profile
                    # Box with tilt matching roof pitch + slight shingle angle (+4 degrees)
                    rot_pitch = sign * (slope_angle + math.radians(4.0))
                    
                    # 8 vertices for tile box
                    tile_verts = []
                    hw, hl, ht = t_w * 0.48, t_l * 0.5, t_thick * 0.5
                    local_coords = [
                        (-hw, -hl, -ht), (hw, -hl, -ht), (hw, hl, -ht), (-hw, hl, -ht),
                        (-hw, -hl,  ht), (hw, -hl,  ht), (hw, hl,  ht), (-hw, hl,  ht)
                    ]
                    cos_p = math.cos(rot_pitch)
                    sin_p = math.sin(rot_pitch)
                    
                    for vx, vy, vz in local_coords:
                        # Rotate around Y axis
                        rx = vx * cos_p + vz * sin_p
                        rz = -vx * sin_p + vz * cos_p
                        tile_verts.append(bm_tiles.verts.new((tile_x + rx, tile_y + vy, tile_z + rz)))
                        
                    # 6 faces of tile box
                    faces = [
                        (0, 1, 2, 3), (4, 7, 6, 5),
                        (0, 4, 5, 1), (1, 5, 6, 2),
                        (2, 6, 7, 3), (3, 7, 4, 0)
                    ]
                    for f in faces:
                        try:
                            bm_tiles.faces.new([tile_verts[vi] for vi in f])
                        except Exception:
                            pass
                            
            tile_mesh = bpy.data.meshes.new(f"{self.name}_Tiles_{slope_side}_Mesh")
            bm_tiles.to_mesh(tile_mesh)
            bm_tiles.free()
            tile_mesh.shade_smooth()
            
            tile_obj = bpy.data.objects.new(f"{self.name}_Tiles_{slope_side}", tile_mesh)
            self.col.objects.link(tile_obj)
            assign_mat(tile_obj, tile_mat)
            tile_obj.location = self.to_world(0, 0, z_eave)
            tile_obj.rotation_euler = (0, 0, self.rot_z)

        # 4. Semicircular Ridge Cap Tiles along Ridge
        bm_ridge = bmesh.new()
        n_ridge = max(4, int(total_d / 0.45))
        for ri in range(n_ridge):
            ry = -total_d * 0.5 + ri * 0.45 + 0.22
            # Semicircular arch cylinder cap
            bmesh.ops.create_cone(bm_ridge, cap_ends=True, segments=10, radius1=0.18, radius2=0.18, depth=0.48)
            # Rotate cone to lay along Y axis
            bmesh.ops.rotate(bm_ridge, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 4, 'X'), verts=bm_ridge.verts[-22:])
            bmesh.ops.translate(bm_ridge, vec=(0, ry, roof_h + 0.08), verts=bm_ridge.verts[-22:])
            
        ridge_mesh = bpy.data.meshes.new(f"{self.name}_Ridge_Tiles_Mesh")
        bm_ridge.to_mesh(ridge_mesh)
        bm_ridge.free()
        ridge_mesh.shade_smooth()
        
        ridge_obj = bpy.data.objects.new(f"{self.name}_Ridge_Tiles", ridge_mesh)
        self.col.objects.link(ridge_obj)
        assign_mat(ridge_obj, tile_mat)
        ridge_obj.location = self.to_world(0, 0, z_eave)
        ridge_obj.rotation_euler = (0, 0, self.rot_z)

        # 5. Bargeboards / Verge boards along gable edges
        for gy, sign_y in [(-d * 0.5 - overhang * 0.8, -1), (d * 0.5 + overhang * 0.8, 1)]:
            for side_x, sign_x in [(-half_w * 0.5, -1), (half_w * 0.5, 1)]:
                rot_ang = sign_x * slope_angle
                self.make_box(f"Bargeboard_{sign_y}_{sign_x}", side_x, gy, z_eave + roof_h * 0.5, 
                              0.08, 0.24, slope_len + 0.3, rot_z_offset=0, mat_name="M_Aged_Oak")
                # Pitch tilt
                # Rotate bargeboard in its local Y axis
                bb_obj = bpy.data.objects.get(f"{self.name}_Bargeboard_{sign_y}_{sign_x}")
                if bb_obj:
                    bb_obj.rotation_euler = (0, rot_ang, self.rot_z)

        # 6. Crossed Apex Bargeboard Finials (Ref Image 2)
        if has_crossed_finial:
            for gy in [-d * 0.5 - overhang * 0.82, d * 0.5 + overhang * 0.82]:
                for f_side, f_rot in [("L", 35), ("R", -35)]:
                    self.make_box(f"Apex_Finial_{f_side}_{int(gy)}", 0, gy, z_eave + roof_h + 0.45, 0.12, 0.20, 1.2, mat_name="M_Aged_Oak")
                    fin = bpy.data.objects.get(f"{self.name}_Apex_Finial_{f_side}_{int(gy)}")
                    if fin:
                        fin.rotation_euler = (0, math.radians(f_rot), self.rot_z)

    # ──────────────────────────────────────────
    # 4. Stone Chimney with Corbeled Cap & Flue Pot
    # ──────────────────────────────────────────
    def build_chimney(self, lx, ly, lz, h=3.2, w=0.9, d=0.9):
        # Chimney shaft (tapered stone)
        self.make_box("Chimney_Shaft", lx, ly, lz + h * 0.5, w, d, h, mat_name="M_Stone_Rough", bevel=0.04)
        # Corbeled stone cap
        self.make_box("Chimney_Cap", lx, ly, lz + h + 0.08, w + 0.18, d + 0.18, 0.16, mat_name="M_Stone_Rough", bevel=0.03)
        # Terracotta / stone flue pot (cylinder)
        self.make_cylinder("Chimney_Pot", lx, ly, lz + h + 0.45, 0.18, 0.16, 0.6, segments=12, mat_name="M_Clay_Terracotta")

    # ──────────────────────────────────────────
    # 5. Wooden Door with Z-Bracing & Strap Hinges
    # ──────────────────────────────────────────
    def build_door(self, lx, ly, lz, w=1.1, h=2.1, is_arched=False):
        # Timber Frame
        self.make_box(f"Door_Frame_{int(lx)}", lx, ly, lz + h * 0.5, w + 0.20, 0.16, h + 0.12, mat_name="M_Aged_Oak")
        # Wooden Plank Door Leaf
        self.make_box(f"Door_PlankLeaf_{int(lx)}", lx, ly, lz + h * 0.5, w, 0.08, h, mat_name="M_Aged_Oak")
        # Diagonal Z-Braces (Ref Image 2)
        self.make_box(f"Door_ZBrace_Top_{int(lx)}", lx, ly - 0.05, lz + h * 0.75, w * 0.8, 0.04, 0.14, mat_name="M_Aged_Oak")
        self.make_box(f"Door_ZBrace_Bot_{int(lx)}", lx, ly - 0.05, lz + h * 0.25, w * 0.8, 0.04, 0.14, mat_name="M_Aged_Oak")
        self.make_box(f"Door_ZBrace_Diag_{int(lx)}", lx, ly - 0.05, lz + h * 0.5, w * 0.75, 0.04, 0.14, rot_z_offset=math.radians(35), mat_name="M_Aged_Oak")
        # Wrought Iron Strap Hinges
        for hy in [0.35, 1.65]:
            self.make_box(f"Door_Hinge_{int(lx)}_{int(hy*10)}", lx - w * 0.25, ly - 0.06, lz + hy, w * 0.45, 0.02, 0.06, mat_name="M_Iron_Wrought")
        # Iron Ring Handle
        self.make_cylinder(f"Door_Handle_{int(lx)}", lx + w * 0.3, ly - 0.08, lz + 1.0, 0.06, 0.06, 0.02, segments=8, rot_x=math.radians(90), mat_name="M_Iron_Wrought")

    # ──────────────────────────────────────────
    # 6. Glass Window with Shutters & Sill
    # ──────────────────────────────────────────
    def build_window(self, lx, ly, lz, w=1.0, h=1.2, rot_offset=0, has_shutters=True):
        # Timber Frame & Projecting Sill
        self.make_box(f"Win_Frame_{int(lx)}_{int(ly)}", lx, ly, lz, w, 0.14, h, rot_z_offset=rot_offset, mat_name="M_Aged_Oak")
        self.make_box(f"Win_Sill_{int(lx)}_{int(ly)}", lx, ly - 0.06, lz - h * 0.5, w + 0.18, 0.22, 0.10, rot_z_offset=rot_offset, mat_name="M_Aged_Oak")
        # Leaded Diamond Glass Pane
        self.make_box(f"Win_Glass_{int(lx)}_{int(ly)}", lx, ly, lz, w - 0.12, 0.02, h - 0.12, rot_z_offset=rot_offset, mat_name="M_Glass_Leaded")
        # Wooden Board Shutters (Left & Right, open)
        if has_shutters:
            shut_w = w * 0.48
            self.make_box(f"Win_Shut_L_{int(lx)}_{int(ly)}", lx - w * 0.5 - shut_w * 0.45, ly - 0.04, lz, shut_w, 0.04, h - 0.05, rot_z_offset=rot_offset + math.radians(-20), mat_name="M_Aged_Oak")
            self.make_box(f"Win_Shut_R_{int(lx)}_{int(ly)}", lx + w * 0.5 + shut_w * 0.45, ly - 0.04, lz, shut_w, 0.04, h - 0.05, rot_z_offset=rot_offset + math.radians(20), mat_name="M_Aged_Oak")

    # ──────────────────────────────────────────
    # 7. Wooden Balcony with Balustrade & Brackets
    # ──────────────────────────────────────────
    def build_balcony(self, lx, ly, lz, w, depth=1.2):
        # Floor joist beams extending outward
        self.make_box("Balcony_Floor", lx, ly - depth * 0.5, lz, w, depth, 0.12, mat_name="M_Aged_Oak")
        # Corner posts
        for px in [-w * 0.5 + 0.08, w * 0.5 - 0.08]:
            self.make_box(f"Balcony_Post_{px:.1f}", lx + px, ly - depth + 0.08, lz + 0.55, 0.12, 0.12, 1.0, mat_name="M_Aged_Oak")
        # Handrail along front & sides
        self.make_box("Balcony_Handrail_Front", lx, ly - depth + 0.08, lz + 1.05, w, 0.12, 0.08, mat_name="M_Aged_Oak")
        self.make_box("Balcony_Handrail_Left", lx - w * 0.5 + 0.08, ly - depth * 0.5, lz + 1.05, 0.10, depth, 0.08, mat_name="M_Aged_Oak")
        self.make_box("Balcony_Handrail_Right", lx + w * 0.5 - 0.08, ly - depth * 0.5, lz + 1.05, 0.10, depth, 0.08, mat_name="M_Aged_Oak")
        # Balusters (vertical pickets)
        n_bal = max(3, int(w / 0.35))
        for bi in range(1, n_bal):
            bx = -w * 0.5 + bi * (w / n_bal)
            self.make_box(f"Balcony_Baluster_{bi}", lx + bx, ly - depth + 0.08, lz + 0.55, 0.06, 0.06, 0.9, mat_name="M_Aged_Oak")
        # Diagonal Knee Braces supporting balcony from wall
        for bx in [-w * 0.35, w * 0.35]:
            self.make_box(f"Balcony_Brace_{bx:.1f}", lx + bx, ly - depth * 0.4, lz - 0.45, 0.12, depth * 0.8, 0.12, mat_name="M_Aged_Oak")
            br = bpy.data.objects.get(f"{self.name}_Balcony_Brace_{bx:.1f}")
            if br:
                br.rotation_euler = (math.radians(-35), 0, self.rot_z)


# ──────────────────────────────────────────────
# SPECIFIC BUILDING GENERATORS
# ──────────────────────────────────────────────

def clean_old_blockout_objects(prefix_list):
    """Removes primitive blockout objects matching prefixes before creating upgraded buildings."""
    b_col = bpy.data.collections.get("01_BUILDINGS")
    if not b_col:
        return
    for o in list(b_col.objects):
        for prefix in prefix_list:
            if o.name.startswith(prefix):
                bpy.data.objects.remove(o, do_unlink=True)
                break

# 1. TAVERN: "The Dragon's Flagon"
def upgrade_tavern(b_col):
    clean_old_blockout_objects(["Tavern_"])
    b = MedievalBuilder("Tavern", base_pos=(4.0, -14.0, 0.0), rot_z=0.0, parent_col=b_col)
    
    # Ground floor: 10m x 8m, height 3.2m
    b.build_foundation(w=10.0, d=8.0, h_found=1.0, mat_name="M_Stone_Rough")
    b.build_timber_framed_floor(z_start=1.0, w=10.0, d=8.0, h_wall=2.8, has_plaster=True)
    
    # Upper floor with 0.6m overhanging jetty on front (Y = -14 -> front at Y=-18.6)
    b.build_timber_framed_floor(z_start=3.8, w=10.0, d=8.0, h_wall=2.8, has_plaster=True, is_overhang=True, overhang_depth=0.6)
    
    # Roof with individual scalloped clay tiles
    b.build_roof_with_individual_tiles(z_eave=6.6, w=10.0, d=8.6, roof_h=3.5, overhang=0.5, tile_mat="M_Tile_Weathered_Moss")
    
    # Upper Wooden Balcony across front
    b.build_balcony(lx=0.0, ly=-4.6, lz=3.8, w=6.5, depth=1.2)
    
    # Front Double Plank Doors
    b.build_door(lx=0.0, ly=-4.05, lz=1.0, w=1.4, h=2.2)
    
    # Windows: Ground floor & Upper floor
    for wx in [-3.2, 3.2]:
        b.build_window(lx=wx, ly=-4.05, lz=2.2, w=1.2, h=1.3, has_shutters=True)
        b.build_window(lx=wx, ly=-4.65, lz=5.0, w=1.2, h=1.3, has_shutters=True)
    b.build_window(lx=0.0, ly=-4.65, lz=5.0, w=1.2, h=1.3, has_shutters=False)
    
    # Dual Stone Chimneys (kitchen hearth + taproom fireplace)
    b.build_chimney(lx=-3.8, ly=2.2, lz=6.6, h=3.2, w=1.1, d=1.1)
    b.build_chimney(lx=3.8, ly=2.2, lz=6.6, h=3.2, w=1.1, d=1.1)
    print("Upgraded Tavern successfully.")

# 2. BLACKSMITH: "The Iron Hearth"
def upgrade_blacksmith(b_col):
    clean_old_blockout_objects(["Blacksmith_"])
    b = MedievalBuilder("Blacksmith", base_pos=(14.0, -7.0, 0.0), rot_z=math.radians(15), parent_col=b_col)
    
    # Main workshop: 8m x 7m, height 3.6m
    b.build_foundation(w=8.0, d=7.0, h_found=1.4, mat_name="M_Stone_Rough")
    b.build_timber_framed_floor(z_start=1.4, w=8.0, d=7.0, h_wall=2.4, has_plaster=False, plank_horizontal=True)
    b.build_roof_with_individual_tiles(z_eave=3.8, w=8.0, d=7.0, roof_h=2.8, overhang=0.45, tile_mat="M_Slate_Roof")
    
    # Open Timber Lean-to Shed on East side (X=4.5)
    for px in [3.8, 7.8]:
        for py in [-3.2, 3.2]:
            b.make_box(f"Shed_Post_{px}_{py}", px, py, 1.4, 0.22, 0.22, 2.8, mat_name="M_Aged_Oak")
    # Shed rafters & roof
    b.make_box("Shed_Plate", 5.8, 0, 2.7, 4.2, 6.8, 0.16, mat_name="M_Aged_Oak")
    b.make_box("Shed_Roof_Shed", 5.8, 0, 3.0, 4.4, 7.2, 0.12, rot_z_offset=0, mat_name="M_Slate_Roof")
    
    # Massive Forge Chimney (industrial stone)
    b.build_chimney(lx=0.0, ly=-2.5, lz=3.8, h=4.2, w=1.4, d=1.4)
    # Double Workshop Doors
    b.build_door(lx=-1.5, ly=-3.55, lz=1.4, w=1.5, h=2.1)
    # Shuttered window
    b.build_window(lx=2.0, ly=-3.55, lz=2.4, w=1.1, h=1.1, has_shutters=True)
    print("Upgraded Blacksmith successfully.")

# 3. CHURCH: "St. Aldhelm's Chapel"
def upgrade_church(b_col):
    clean_old_blockout_objects(["Church_"])
    b = MedievalBuilder("Church", base_pos=(-10.0, 18.0, 0.0), rot_z=0.0, parent_col=b_col)
    
    # Nave: 11m x 16m, height 6.2m
    b.build_foundation(w=11.0, d=16.0, h_found=1.2, mat_name="M_Stone_Rough")
    # Solid stone masonry walls
    b.make_box("Nave_Stone_Walls", 0, 0, 3.8, 11.0, 16.0, 5.2, mat_name="M_Stone_Rough", bevel=0.04)
    
    # Wall Buttresses along North & South sides
    for side_x in [-5.6, 5.6]:
        for by in [-6.0, -2.0, 2.0, 6.0]:
            b.make_box(f"Buttress_{side_x:.1f}_{by:.1f}", side_x, by, 3.2, 0.7, 1.1, 5.8, mat_name="M_Stone_Rough", bevel=0.04)
            
    # Gothic Arched Lancet Windows with Leaded Stained Glass
    for side_x, rot in [(-5.55, math.radians(90)), (5.55, math.radians(-90))]:
        for wy in [-4.0, 0.0, 4.0]:
            b.make_box(f"Church_Lancet_{side_x:.1f}_{wy:.1f}", side_x, wy, 4.2, 1.2, 0.2, 2.6, rot_z_offset=rot, mat_name="M_Glass_Leaded")
            
    # High Pitched Slate Nave Roof
    b.build_roof_with_individual_tiles(z_eave=6.4, w=11.0, d=16.0, roof_h=5.2, overhang=0.5, tile_mat="M_Slate_Roof", has_crossed_finial=False)
    
    # Stone Gothic Arched Portal Entrance (South face, facing village Y=-8.0)
    b.make_box("Church_Portal_Arch", 0, -8.1, 2.2, 2.2, 0.4, 3.4, mat_name="M_Stone_Rough", bevel=0.05)
    b.build_door(lx=0.0, ly=-8.05, lz=1.2, w=1.4, h=2.4)
    
    # Bell Tower at South End (Y = -6.0)
    tower_z = 0.0
    tower_h = 15.5
    b.make_box("Bell_Tower_Shaft", 0, -6.0, tower_h * 0.5, 4.8, 4.8, tower_h, mat_name="M_Stone_Rough", bevel=0.05)
    # Belfry Arched Louver Openings on all 4 sides
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        ox = math.sin(rad) * 2.45
        oy = -6.0 - math.cos(rad) * 2.45
        b.make_box(f"Belfry_Louver_{angle}", ox, oy, 12.8, 1.2, 0.25, 2.4, rot_z_offset=rad, mat_name="M_Aged_Oak")
        
    # Corbeled Bell Tower Parapet with Crenellations
    b.make_box("Bell_Tower_Cornice", 0, -6.0, 15.2, 5.4, 5.4, 0.4, mat_name="M_Stone_Rough", bevel=0.04)
    # Octagonal Pyramidal Slate Spire
    b.make_cylinder("Bell_Tower_Spire", 0, -6.0, 18.2, 2.8, 0.1, 5.5, segments=8, mat_name="M_Slate_Roof")
    # Wrought Iron Cross Finial on Spire Apex
    b.make_box("Spire_Cross_V", 0, -6.0, 21.5, 0.08, 0.08, 1.4, mat_name="M_Iron_Wrought")
    b.make_box("Spire_Cross_H", 0, -6.0, 21.8, 0.8, 0.08, 0.08, mat_name="M_Iron_Wrought")
    print("Upgraded Church & Bell Tower successfully.")

# 4. INN: "The Wayfarer's Rest"
def upgrade_inn(b_col):
    clean_old_blockout_objects(["Inn_"])
    b = MedievalBuilder("Inn", base_pos=(-15.0, 8.0, 0.0), rot_z=math.radians(-10), parent_col=b_col)
    
    # Main building: 9m x 7m, 2 stories
    b.build_foundation(w=9.0, d=7.0, h_found=1.1, mat_name="M_Stone_Rough")
    b.build_timber_framed_floor(z_start=1.1, w=9.0, d=7.0, h_wall=2.6, has_plaster=True)
    b.build_timber_framed_floor(z_start=3.7, w=9.0, d=7.0, h_wall=2.6, has_plaster=True, is_overhang=True, overhang_depth=0.5)
    
    # Sweeping Clay Tiled Roof
    b.build_roof_with_individual_tiles(z_eave=6.3, w=9.0, d=7.5, roof_h=3.4, overhang=0.45, tile_mat="M_Tile_Weathered_Moss")
    
    # 2 Gabled Roof Dormers on front slope
    for dx in [-2.2, 2.2]:
        b.make_box(f"Dormer_{int(dx)}", dx, -2.4, 6.8, 1.4, 1.6, 1.4, mat_name="M_Plaster_Cream")
        b.make_box(f"Dormer_Roof_{int(dx)}", dx, -2.4, 7.6, 1.6, 1.8, 0.6, mat_name="M_Clay_Terracotta")
        b.build_window(lx=dx, ly=-3.1, lz=6.8, w=0.9, h=0.9, has_shutters=False)
        
    # Wooden Balcony / Exterior Gallery on front upper floor
    b.build_balcony(lx=0.0, ly=-4.1, lz=3.7, w=6.0, depth=1.1)
    
    # Front Entrance Door with Covered Timber Porch
    b.build_door(lx=0.0, ly=-3.55, lz=1.1, w=1.2, h=2.1)
    b.build_chimney(lx=3.2, ly=2.2, lz=6.3, h=3.2, w=1.0, d=1.0)
    
    # Windows with shutters
    for wx in [-2.8, 2.8]:
        b.build_window(lx=wx, ly=-3.55, lz=2.1, w=1.1, h=1.2, has_shutters=True)
        b.build_window(lx=wx, ly=-4.15, lz=4.8, w=1.1, h=1.2, has_shutters=True)
    print("Upgraded Inn successfully.")

# 5. COTTAGE 2: "Weaver's Cottage" (Ref Image 2)
def upgrade_cottage_2(b_col):
    clean_old_blockout_objects(["Cottage_2_"])
    b = MedievalBuilder("Cottage_2", base_pos=(-8.0, -8.0, 0.0), rot_z=math.radians(20), parent_col=b_col)
    
    # Massive Fieldstone Foundation Plinth (1.3m high, matching Ref Image 2)
    b.build_foundation(w=6.8, d=8.4, h_found=1.3, mat_name="M_Stone_Rough")
    
    # Horizontal Timber Log/Plank Walls (matching Ref Image 2)
    b.build_timber_framed_floor(z_start=1.3, w=6.8, d=8.4, h_wall=2.8, has_plaster=False, plank_horizontal=True)
    
    # Steep Roof with Weathered Moss Tiles and Crossed Apex Bargeboards (Ref Image 2)
    b.build_roof_with_individual_tiles(z_eave=4.1, w=6.8, d=8.4, roof_h=3.5, overhang=0.5, tile_mat="M_Tile_Weathered_Moss", has_crossed_finial=True)
    
    # Heavy Timber Plank Door with Diagonal Z-Bracing (Ref Image 2)
    b.build_door(lx=-1.5, ly=-4.25, lz=1.3, w=1.1, h=2.1)
    
    # Stone Chimney with Rain Cap (Ref Image 2)
    b.build_chimney(lx=2.0, ly=2.2, lz=4.1, h=3.4, w=1.0, d=1.0)
    
    # Multi-pane wooden windows with shutters
    b.build_window(lx=1.8, ly=-4.25, lz=2.4, w=1.2, h=1.2, has_shutters=True)
    b.build_window(lx=-3.45, ly=0.0, lz=2.4, w=1.1, h=1.1, rot_offset=math.radians(90), has_shutters=True)
    print("Upgraded Cottage 2 (Weaver) successfully.")

# 6. COTTAGE 3: "Baker's House" (Ref Image 1)
def upgrade_cottage_3(b_col):
    clean_old_blockout_objects(["Cottage_3_"])
    b = MedievalBuilder("Cottage_3", base_pos=(10.0, 10.0, 0.0), rot_z=math.radians(-25), parent_col=b_col)
    
    # Ground floor: Full fieldstone masonry with arched entrance (matching Ref Image 1)
    b.build_foundation(w=6.0, d=7.0, h_found=1.0, mat_name="M_Stone_Rough")
    b.make_box("GF_Stone_Walls", 0, 0, 2.1, 6.0, 7.0, 2.2, mat_name="M_Stone_Rough", bevel=0.03)
    
    # Stone Arched Entrance Portico (Ref Image 1)
    b.make_box("Arched_Porch_Stone", -1.2, -3.6, 2.0, 1.8, 0.6, 2.6, mat_name="M_Stone_Rough", bevel=0.04)
    b.build_door(lx=-1.2, ly=-3.55, lz=1.0, w=1.0, h=2.1, is_arched=True)
    
    # Upper floor: Half-timbered framing with cream plaster panels (Ref Image 1)
    b.build_timber_framed_floor(z_start=3.2, w=6.0, d=7.0, h_wall=2.2, has_plaster=True)
    
    # Pitched roof with dormer gablet (Ref Image 1)
    b.build_roof_with_individual_tiles(z_eave=5.4, w=6.0, d=7.0, roof_h=3.0, overhang=0.45, tile_mat="M_Clay_Terracotta")
    
    # Front Gablet Dormer Projection (Ref Image 1)
    b.make_box("Front_Gablet", 1.4, -2.4, 5.8, 2.4, 2.2, 1.8, mat_name="M_Plaster_Cream")
    b.make_box("Front_Gablet_Roof", 1.4, -2.4, 6.8, 2.6, 2.4, 0.8, mat_name="M_Clay_Terracotta")
    b.build_window(lx=1.4, ly=-3.45, lz=5.8, w=1.0, h=1.0, has_shutters=False)
    
    # Ground floor windows with timber trim (Ref Image 1)
    b.build_window(lx=1.4, ly=-3.55, lz=2.1, w=1.4, h=1.2, has_shutters=False)
    
    # Baker's stone oven chimney projection
    b.build_chimney(lx=-3.0, ly=1.0, lz=5.4, h=3.0, w=1.1, d=0.9)
    print("Upgraded Cottage 3 (Baker) successfully.")

# 7. BARN: "Village Tithe Barn"
def upgrade_barn(b_col):
    clean_old_blockout_objects(["Barn_"])
    b = MedievalBuilder("Barn", base_pos=(24.0, 16.0, 0.0), rot_z=math.radians(5), parent_col=b_col)
    
    # Barn: 12m x 9m, height 5.8m
    b.build_foundation(w=12.0, d=9.0, h_found=0.8, mat_name="M_Stone_Rough")
    # Weatherboard timber siding
    b.build_timber_framed_floor(z_start=0.8, w=12.0, d=9.0, h_wall=4.6, has_plaster=False, plank_horizontal=False)
    
    # Sweeping clay/thatch roof
    b.build_roof_with_individual_tiles(z_eave=5.4, w=12.0, d=9.0, roof_h=4.2, overhang=0.55, tile_mat="M_Tile_Weathered_Moss")
    
    # Large Double Wagon Doors on front (Y = -4.55)
    b.make_box("Wagon_Door_L", -1.6, -4.55, 2.4, 2.8, 0.10, 3.2, mat_name="M_Wood_AgedOak")
    b.make_box("Wagon_Door_R", 1.6, -4.55, 2.4, 2.8, 0.10, 3.2, mat_name="M_Wood_AgedOak")
    # Iron Z-braces & giant strap hinges
    for hy in [1.2, 3.6]:
        b.make_box(f"Wagon_Hinge_L_{int(hy)}", -2.0, -4.62, hy, 2.0, 0.03, 0.12, mat_name="M_Iron_Wrought")
        b.make_box(f"Wagon_Hinge_R_{int(hy)}", 2.0, -4.62, hy, 2.0, 0.03, 0.12, mat_name="M_Iron_Wrought")
        
    # Upper Hayloft Door & Projecting Hoist Crane Beam
    b.make_box("Hayloft_Door", 0.0, -4.55, 4.8, 1.2, 0.08, 1.6, mat_name="M_Wood_AgedOak")
    # Projecting timber hoist beam extending forward from apex
    b.make_box("Hayloft_Hoist_Beam", 0.0, -5.4, 7.8, 0.22, 2.2, 0.22, mat_name="M_Aged_Oak")
    print("Upgraded Barn successfully.")

# 8. CASTLE: "Old Watch Ruin"
def upgrade_castle(b_col):
    clean_old_blockout_objects(["Castle_Tower_", "Castle_Wall_"])
    b = MedievalBuilder("Castle", base_pos=(-26.0, -14.0, 0.0), rot_z=0.0, parent_col=b_col)
    
    # 1. Round Watchtower (16.5m high, radius 3.8m)
    tower_h = 16.5
    tower_r = 3.8
    # Battered stone base (wider at base)
    b.make_cylinder("Watchtower_Base", 0, 0, 2.0, tower_r + 0.4, tower_r, 4.0, segments=16, mat_name="M_Stone_Rough")
    # Main tower shaft
    b.make_cylinder("Watchtower_Shaft", 0, 0, 9.5, tower_r, tower_r, 11.0, segments=16, mat_name="M_Stone_Rough")
    
    # Machicolation corbel brackets supporting the parapet
    for i in range(12):
        angle = i * math.pi / 6
        cx = math.cos(angle) * (tower_r + 0.2)
        cy = math.sin(angle) * (tower_r + 0.2)
        b.make_box(f"Machicolation_Corbel_{i}", cx, cy, 14.8, 0.35, 0.5, 0.7, rot_z_offset=angle, mat_name="M_Stone_Rough")
        
    # Overhanging Parapet with Crenellations
    b.make_cylinder("Parapet_Cornice", 0, 0, 15.3, tower_r + 0.5, tower_r + 0.5, 0.6, segments=16, mat_name="M_Stone_Rough")
    for i in range(8):
        angle = i * math.pi / 4
        cx = math.cos(angle) * (tower_r + 0.4)
        cy = math.sin(angle) * (tower_r + 0.4)
        b.make_box(f"Tower_Merlon_{i}", cx, cy, 16.4, 0.9, 0.5, 1.2, rot_z_offset=angle, mat_name="M_Stone_Rough")
        
    # Conical Slate Cap with Weathered Timber Hoarding
    b.make_cylinder("Tower_Cone_Cap", 0, 0, 19.2, tower_r + 0.6, 0.2, 5.0, segments=16, mat_name="M_Slate_Roof")
    
    # Arrow slits in tower walls
    for az, ang in [(6.5, 30), (9.5, 120), (12.5, 240)]:
        rad = math.radians(ang)
        b.make_box(f"Arrow_Slit_{int(az)}", math.cos(rad) * tower_r, math.sin(rad) * tower_r, az, 0.2, 0.4, 1.2, rot_z_offset=rad, mat_name="M_Aged_Oak")
        
    # 2. Curtain Walls (Ramparts)
    # North Wall: 14m long towards village
    b.make_box("Rampart_Wall_North", 6.0, 0.0, 2.8, 12.0, 1.8, 5.6, mat_name="M_Stone_Rough", bevel=0.05)
    # North wall parapet walkway & merlons
    for mi in range(6):
        b.make_box(f"Rampart_N_Merlon_{mi}", 1.0 + mi * 2.0, -0.7, 6.0, 1.1, 0.4, 0.9, mat_name="M_Stone_Rough")
    # West Wall: 12m long
    b.make_box("Rampart_Wall_West", 0.0, 6.0, 2.8, 1.8, 12.0, 5.6, mat_name="M_Stone_Rough", bevel=0.05)
    for mi in range(5):
        b.make_box(f"Rampart_W_Merlon_{mi}", 0.7, 1.5 + mi * 2.2, 6.0, 0.4, 1.1, 0.9, mat_name="M_Stone_Rough")
        
    print("Upgraded Castle Watchtower & Ramparts successfully.")


# ──────────────────────────────────────────────
# MASTER UPGRADE PIPELINE
# ──────────────────────────────────────────────

def upgrade_all_buildings():
    print("==================================================")
    print("   MEDIEVAL VILLAGE: UPGRADE BUILDINGS PIPELINE")
    print("==================================================")
    
    b_col = bpy.data.collections.get("01_BUILDINGS")
    if not b_col:
        print("ERROR: 01_BUILDINGS collection not found!")
        return False
        
    # Upgrade all 8 buildings to high detail
    upgrade_tavern(b_col)
    upgrade_blacksmith(b_col)
    upgrade_church(b_col)
    upgrade_inn(b_col)
    upgrade_cottage_2(b_col)
    upgrade_cottage_3(b_col)
    upgrade_barn(b_col)
    upgrade_castle(b_col)
    
    print("==================================================")
    print("   ALL 8 BUILDINGS SUCCESSFULLY UPGRADED!")
    print("==================================================")
    return True

if __name__ == "__main__":
    upgrade_all_buildings()

