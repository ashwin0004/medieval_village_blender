"""
upgrade_watchtower.py
=====================
Transforms the castle tower into an authentic, highly detailed medieval stone watchtower
based on the user's reference images (Ref 1-5):
  - Battered stone base with torus string course moulding (Ref 1, 3)
  - Multi-tier ashlar stone shaft with belt courses and narrow arrow slits (Ref 1, 4)
  - Ground-level stone arch entrance door with iron studs, strap hinges & flanking lanterns (Ref 5)
  - Elevated defensive sally port door at the staircase landing (Ref 4, 5)
  - Exterior wooden staircase with timber stringers, treads, posts, and X-braced railings
    climbing the curved tower wall (Ref 2, 3, 5)
  - Cantilevered wooden observation platform / hoarding (hourd) supported by stone corbels
    and diagonal timber struts (Ref 2, 4, 5)
  - Stone battlements (crenellated parapet with merlons & embrasures) (Ref 1, 5)
  - Conical slate roof structure with exposed rafters and wrought-iron weather vane (Ref 2, 5)
  - Wrought-iron cage lanterns illuminating the entrance, stairs, and observation deck (Ref 5)
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# ──────────────────────────────────────────────
# Helper Functions
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
# Watchtower Builder Class
# ──────────────────────────────────────────────

class WatchtowerBuilder:
    def __init__(self, cx=-26.0, cy=-14.0, cz=0.0):
        self.center = Vector((cx, cy, cz))
        b_col = bpy.data.collections.get("01_BUILDINGS")
        self.col = ensure_collection("Castle", b_col)

    def to_world(self, lx, ly, lz):
        return Vector((self.center.x + lx, self.center.y + ly, self.center.z + lz))

    def make_box(self, name, lx, ly, lz, sx, sy, sz, rx=0, ry=0, rz=0, mat_name="M_Aged_Oak", bevel=0.02):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        m = bpy.data.meshes.new(f"{name}_Mesh")
        bm.to_mesh(m)
        bm.free()
        
        obj = bpy.data.objects.new(name, m)
        self.col.objects.link(obj)
        assign_mat(obj, mat_name)
        obj.location = self.to_world(lx, ly, lz)
        obj.scale = (sx, sy, sz)
        obj.rotation_euler = (rx, ry, rz)
        if bevel > 0:
            add_bevel(obj, width=bevel, segments=2)
        return obj

    def make_cylinder(self, name, lx, ly, lz, r1, r2, depth, segments=16, rx=0, ry=0, rz=0, mat_name="M_Stone_Rough"):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r1, radius2=r2, depth=depth)
        m = bpy.data.meshes.new(f"{name}_Mesh")
        bm.to_mesh(m)
        bm.free()
        m.shade_smooth()
        
        obj = bpy.data.objects.new(name, m)
        self.col.objects.link(obj)
        assign_mat(obj, mat_name)
        obj.location = self.to_world(lx, ly, lz)
        obj.rotation_euler = (rx, ry, rz)
        return obj

    # ──────────────────────────────────────────
    # 1. Battered Stone Base & Tower Shaft
    # ──────────────────────────────────────────
    def build_stone_structure(self):
        # 1. Battered Base (Ref 1, 3): slopes from r=4.3m at ground to r=3.8m at z=3.8m
        self.make_cylinder("Watchtower_Battered_Base", 0, 0, 1.9, 4.3, 3.8, 3.8, segments=24, mat_name="M_Stone_Rough")
        
        # 2. Torus String Course Moulding at top of battered base (Ref 1, 3)
        self.make_cylinder("Watchtower_String_Course_1", 0, 0, 3.85, 3.95, 3.95, 0.22, segments=24, mat_name="M_Stone_Rough")
        
        # 3. Main Stone Shaft: from z=3.8m to z=14.8m (height 11.0m, radius 3.75m)
        self.make_cylinder("Watchtower_Main_Shaft", 0, 0, 9.3, 3.75, 3.75, 11.0, segments=24, mat_name="M_Stone_Rough")
        
        # 4. Mid-height Belt Course Moulding at z=9.0m
        self.make_cylinder("Watchtower_Belt_Course_2", 0, 0, 9.0, 3.88, 3.88, 0.18, segments=24, mat_name="M_Stone_Rough")
        
        # 5. Machicolation Corbel Brackets (Tiered stone brackets, Ref 1, 2)
        n_corbels = 16
        for i in range(n_corbels):
            angle = i * (2 * math.pi / n_corbels)
            cx = math.cos(angle) * 3.85
            cy = math.sin(angle) * 3.85
            # 2-tiered stepped corbel stone
            self.make_box(f"Tower_Corbel_Tier1_{i}", cx, cy, 14.3, 0.42, 0.55, 0.5, rz=angle, mat_name="M_Stone_Rough", bevel=0.03)
            self.make_box(f"Tower_Corbel_Tier2_{i}", cx * 1.05, cy * 1.05, 14.7, 0.48, 0.70, 0.4, rz=angle, mat_name="M_Stone_Rough", bevel=0.03)
            
        # 6. Overhanging Parapet Cornice Ring at z=15.0m (radius 4.4m)
        self.make_cylinder("Watchtower_Parapet_Cornice", 0, 0, 15.0, 4.4, 4.4, 0.35, segments=24, mat_name="M_Stone_Rough")

    # ──────────────────────────────────────────
    # 2. Entrance Doors (Ground & Sally Port)
    # ──────────────────────────────────────────
    def build_entrances(self):
        # Ground Entrance: facing South-East (towards village at angle -45 deg / 315 deg)
        ang = math.radians(-45)
        ex = math.cos(ang) * 3.9
        ey = math.sin(ang) * 3.9
        
        # Stone Arched Doorway Frame (Ref 5)
        self.make_box("Ground_Portal_Jamb_L", ex - 0.7 * math.sin(ang), ey + 0.7 * math.cos(ang), 1.25, 0.35, 0.45, 2.4, rz=ang, mat_name="M_Stone_Rough")
        self.make_box("Ground_Portal_Jamb_R", ex + 0.7 * math.sin(ang), ey - 0.7 * math.cos(ang), 1.25, 0.35, 0.45, 2.4, rz=ang, mat_name="M_Stone_Rough")
        self.make_box("Ground_Portal_Arch", ex, ey, 2.55, 1.75, 0.45, 0.45, rz=ang, mat_name="M_Stone_Rough", bevel=0.04)
        
        # Heavy Wooden Plank Door with Iron Studs & Strap Hinges (Ref 5)
        self.make_box("Ground_Door_Leaf", ex, ey + 0.1, 1.15, 1.2, 0.08, 2.2, rz=ang, mat_name="M_Wood_AgedOak")
        for hy in [0.4, 1.7]:
            self.make_box(f"Ground_Door_Hinge_{int(hy*10)}", ex - 0.3 * math.sin(ang), ey - 0.05, hy, 0.6, 0.03, 0.08, rz=ang, mat_name="M_Iron_Wrought")
        self.make_cylinder("Ground_Door_Ring", ex + 0.35 * math.cos(ang), ey + 0.35 * math.sin(ang), 1.1, 0.07, 0.07, 0.02, segments=8, rx=math.radians(90), mat_name="M_Iron_Wrought")
        
        # Stone Entrance Threshold Steps
        self.make_box("Ground_Door_Step_0", ex * 1.08, ey * 1.08, 0.15, 1.8, 0.55, 0.3, rz=ang, mat_name="M_Stone_Rough", bevel=0.03)

        # Elevated Watchman Entrance / Sally Port Door at z=5.2m (Ref 4, 5)
        ang_elev = math.radians(20) # East face on stair landing
        sx = math.cos(ang_elev) * 3.7
        sy = math.sin(ang_elev) * 3.7
        self.make_box("Sally_Port_Frame", sx, sy, 6.2, 1.3, 0.35, 2.2, rz=ang_elev, mat_name="M_Stone_Rough", bevel=0.03)
        self.make_box("Sally_Port_Door", sx, sy + 0.05, 6.15, 1.0, 0.08, 2.0, rz=ang_elev, mat_name="M_Aged_Oak")

    # ──────────────────────────────────────────
    # 3. Narrow Arrow Slits & Lookout Windows
    # ──────────────────────────────────────────
    def build_openings(self):
        # Stone Arrow Loops with cross-slits (Ref 1, 4)
        slit_configs = [
            (math.radians(70), 5.5), (math.radians(160), 5.5), (math.radians(250), 5.5),
            (math.radians(110), 9.8), (math.radians(200), 9.8), (math.radians(290), 9.8),
            (math.radians(340), 12.5), (math.radians(80), 12.5), (math.radians(220), 12.5)
        ]
        for idx, (ang, sz) in enumerate(slit_configs):
            ox = math.cos(ang) * 3.74
            oy = math.sin(ang) * 3.74
            # Vertical narrow slit with stone reveal
            self.make_box(f"Arrow_Loop_V_{idx}", ox, oy, sz, 0.14, 0.32, 1.35, rz=ang, mat_name="M_Aged_Oak")
            # Horizontal cross-slit (oillets)
            self.make_box(f"Arrow_Loop_H_{idx}", ox, oy, sz + 0.15, 0.45, 0.30, 0.12, rz=ang, mat_name="M_Aged_Oak")

        # Upper Arched Lookout Windows with Stone Surrounds (Ref 1, 5)
        for w_ang in [math.radians(-40), math.radians(140)]:
            wx = math.cos(w_ang) * 3.72
            wy = math.sin(w_ang) * 3.72
            self.make_box(f"Lookout_Win_Frame_{int(w_ang*10)}", wx, wy, 13.2, 0.95, 0.35, 1.45, rz=w_ang, mat_name="M_Stone_Rough", bevel=0.03)
            self.make_box(f"Lookout_Win_Opening_{int(w_ang*10)}", wx, wy, 13.2, 0.65, 0.18, 1.15, rz=w_ang, mat_name="M_Aged_Oak")
            # Iron security grille
            self.make_box(f"Lookout_Win_Grille_{int(w_ang*10)}", wx, wy, 13.2, 0.04, 0.12, 1.1, rz=w_ang, mat_name="M_Iron_Wrought")

    # ──────────────────────────────────────────
    # 4. Exterior Wooden Staircase & Landings (Ref 2, 3, 5)
    # ──────────────────────────────────────────
    def build_exterior_stairs(self):
        # The wooden staircase wraps along the tower's South-East face:
        # Flight 1: from ground (ang = -75 deg, z=0.3m) up to Landing 1 (ang = -10 deg, z=3.8m)
        # Flight 2: from Landing 1 up to Sally Port Landing 2 (ang = +25 deg, z=5.2m)
        # Landing 3: upper stair ascending towards the wooden observation deck
        
        stair_mat = "M_Aged_Oak"
        rail_mat = "M_Aged_Oak"
        
        # Total steps from ground to landing 1: ~18 steps
        n_steps_1 = 18
        start_ang = math.radians(-85)
        end_ang = math.radians(-10)
        
        for s in range(n_steps_1):
            t = s / n_steps_1
            ang = start_ang + t * (end_ang - start_ang)
            rad = 4.15 + t * 0.25 # Slightly further out from wall
            step_z = 0.25 + t * 3.6
            
            sx = math.cos(ang) * rad
            sy = math.sin(ang) * rad
            
            # Step tread (solid oak beam)
            step_tan = ang + math.radians(90)
            self.make_box(f"Stair_Tread_{s}", sx, sy, step_z, 1.15, 0.32, 0.09, rz=step_tan, mat_name=stair_mat)
            
            # Outer timber handrail baluster every 3 steps
            if s % 3 == 0:
                px = math.cos(ang) * (rad + 0.5)
                py = math.sin(ang) * (rad + 0.5)
                self.make_box(f"Stair_Newel_{s}", px, py, step_z + 0.5, 0.10, 0.10, 1.05, rz=step_tan, mat_name=rail_mat)

        # Outer timber handrail railing
        for s in range(n_steps_1 - 1):
            t1 = s / n_steps_1
            t2 = (s + 1) / n_steps_1
            ang1 = start_ang + t1 * (end_ang - start_ang)
            ang2 = start_ang + t2 * (end_ang - start_ang)
            r = 4.65
            z1 = 0.25 + t1 * 3.6 + 0.95
            z2 = 0.25 + t2 * 3.6 + 0.95
            
            mx = (math.cos(ang1) + math.cos(ang2)) * 0.5 * r
            my = (math.sin(ang1) + math.sin(ang2)) * 0.5 * r
            mz = (z1 + z2) * 0.5
            d_len = math.sqrt((math.cos(ang2)*r - math.cos(ang1)*r)**2 + (math.sin(ang2)*r - math.sin(ang1)*r)**2 + (z2 - z1)**2)
            seg_ang = math.atan2(math.sin(ang2) - math.sin(ang1), math.cos(ang2) - math.cos(ang1))
            self.make_box(f"Stair_Rail_{s}", mx, my, mz, 0.08, d_len, 0.08, rz=seg_ang, mat_name=rail_mat)

        # Landing 1 at z=3.85m (ang = -10 deg)
        l1_ang = math.radians(-10)
        l1_x = math.cos(l1_ang) * 4.35
        l1_y = math.sin(l1_ang) * 4.35
        self.make_box("Stair_Landing_1", l1_x, l1_y, 3.85, 1.6, 1.6, 0.14, rz=l1_ang, mat_name=stair_mat)
        
        # Heavy timber diagonal knee-brace supporting Landing 1 from stone wall (Ref 5)
        self.make_box("Landing_1_Brace_L", l1_x * 0.95, l1_y * 0.95, 2.6, 0.16, 1.4, 0.16, rx=math.radians(-40), rz=l1_ang, mat_name=stair_mat)

        # Flight 2: from Landing 1 up to Sally Port Landing 2 (z=5.2m, ang = +20 deg)
        n_steps_2 = 8
        for s in range(n_steps_2):
            t = s / n_steps_2
            ang = math.radians(-10) + t * math.radians(30)
            rad = 4.35
            step_z = 3.95 + t * 1.3
            sx = math.cos(ang) * rad
            sy = math.sin(ang) * rad
            self.make_box(f"Stair_F2_Tread_{s}", sx, sy, step_z, 1.15, 0.32, 0.09, rz=ang + math.radians(90), mat_name=stair_mat)

        # Landing 2 at Sally Port (z=5.25m, ang = +20 deg)
        l2_ang = math.radians(20)
        l2_x = math.cos(l2_ang) * 4.3
        l2_y = math.sin(l2_ang) * 4.3
        self.make_box("Sally_Port_Platform", l2_x, l2_y, 5.25, 1.6, 1.8, 0.14, rz=l2_ang, mat_name=stair_mat)
        self.make_box("Sally_Port_Handrail", l2_x * 1.12, l2_y * 1.12, 6.2, 1.6, 0.10, 0.08, rz=l2_ang + math.radians(90), mat_name=rail_mat)
        # Diagonal X-bracing on Landing 2 balustrade (Ref 5)
        self.make_box("Sally_Balustrade_X1", l2_x * 1.12, l2_y * 1.12, 5.75, 1.5, 0.05, 0.08, rx=math.radians(35), rz=l2_ang + math.radians(90), mat_name=rail_mat)
        self.make_box("Sally_Balustrade_X2", l2_x * 1.12, l2_y * 1.12, 5.75, 1.5, 0.05, 0.08, rx=math.radians(-35), rz=l2_ang + math.radians(90), mat_name=rail_mat)

    # ──────────────────────────────────────────
    # 5. Wooden Observation Platform & Hoarding (Ref 2, 4, 5)
    # ──────────────────────────────────────────
    def build_observation_platform(self):
        # 1. Cantilevered Timber Floor Beams radiating outward at z=14.9m
        n_beams = 16
        for bi in range(n_beams):
            angle = bi * (2 * math.pi / n_beams)
            bx = math.cos(angle) * 3.8
            by = math.sin(angle) * 3.8
            # Heavy timber beam projecting outward to radius 4.8m
            self.make_box(f"Hoard_Beam_{bi}", bx * 1.12, by * 1.12, 14.95, 0.22, 1.4, 0.22, rz=angle + math.radians(90), mat_name="M_Aged_Oak")
            # Diagonal timber strut underneath supporting from tower shaft
            self.make_box(f"Hoard_Strut_{bi}", bx * 1.05, by * 1.05, 14.15, 0.16, 1.2, 0.16, rx=math.radians(38), rz=angle + math.radians(90), mat_name="M_Aged_Oak")
            
        # 2. Wooden Floor Deck Ring
        self.make_cylinder("Hoard_Floor_Deck", 0, 0, 15.08, 4.85, 4.85, 0.12, segments=24, mat_name="M_Aged_Oak")
        
        # 3. Defensive Timber Hoarding Screen & Balustrades (Ref 4, 5)
        # Vertical oak posts around the perimeter
        for pi in range(n_beams):
            angle = pi * (2 * math.pi / n_beams)
            px = math.cos(angle) * 4.75
            py = math.sin(angle) * 4.75
            # Heavy vertical timber post
            self.make_box(f"Hoard_Post_{pi}", px, py, 16.35, 0.18, 0.18, 2.4, rz=angle, mat_name="M_Aged_Oak")

        # Timber Boarding Panels with Defensive Arrow Slits (Ref 4)
        for pi in range(n_beams):
            a1 = pi * (2 * math.pi / n_beams)
            a2 = (pi + 1) * (2 * math.pi / n_beams)
            mid_a = (a1 + a2) * 0.5
            mx = math.cos(mid_a) * 4.75
            my = math.sin(mid_a) * 4.75
            panel_w = 2 * math.sin(math.pi / n_beams) * 4.75
            # Timber wall panel (lower half solid, upper has arrow slit)
            self.make_box(f"Hoard_Panel_Bot_{pi}", mx, my, 15.8, panel_w * 0.98, 0.08, 1.3, rz=mid_a + math.radians(90), mat_name="M_Wood_AgedOak")
            self.make_box(f"Hoard_Panel_Top_{pi}", mx, my, 17.1, panel_w * 0.98, 0.08, 0.6, rz=mid_a + math.radians(90), mat_name="M_Wood_AgedOak")
            # Cruciform arrow loop cutout in the panel
            self.make_box(f"Hoard_Arrow_Slit_{pi}", mx, my, 16.55, 0.12, 0.12, 0.5, rz=mid_a + math.radians(90), mat_name="M_Aged_Oak")

        # Continuous Timber Top Railing Plate
        self.make_cylinder("Hoard_Top_Plate", 0, 0, 17.5, 4.85, 4.85, 0.18, segments=24, mat_name="M_Aged_Oak")

    # ──────────────────────────────────────────
    # 6. Conical Roof Structure & Weather Vane (Ref 2, 5)
    # ──────────────────────────────────────────
    def build_roof_structure(self):
        # 1. Exposed Rafter Ring underneath the roof eaves (Ref 4)
        n_rafters = 24
        for ri in range(n_rafters):
            ang = ri * (2 * math.pi / n_rafters)
            rx = math.cos(ang) * 4.6
            ry = math.sin(ang) * 4.6
            self.make_box(f"Roof_Rafter_Tail_{ri}", rx, ry, 17.6, 0.14, 0.75, 0.16, rz=ang + math.radians(90), mat_name="M_Aged_Oak")

        # 2. Conical Slate Roof (radius 5.1m at eaves tapering to apex at z=22.8m, height 5.2m)
        self.make_cylinder("Watchtower_Conical_Roof", 0, 0, 20.2, 5.15, 0.18, 5.2, segments=24, mat_name="M_Slate_Roof")

        # 3. Weather Vane Finial on Roof Apex (Ref 2, 5)
        # Copper/lead finial sleeve
        self.make_cylinder("Finial_Cap_Sleeve", 0, 0, 22.9, 0.28, 0.10, 0.6, segments=12, mat_name="M_Iron_Wrought")
        # Central wrought-iron rod
        self.make_box("Weather_Vane_Rod", 0, 0, 23.8, 0.06, 0.06, 1.4, mat_name="M_Iron_Wrought")
        # Compass directional cross (N-S, E-W)
        self.make_box("Weather_Vane_NS", 0, 0, 23.9, 0.04, 0.85, 0.04, mat_name="M_Iron_Wrought")
        self.make_box("Weather_Vane_EW", 0, 0, 23.9, 0.85, 0.04, 0.04, mat_name="M_Iron_Wrought")
        # Rotating metal banner pennant (Ref 5)
        self.make_box("Weather_Vane_Banner", 0.35, 0, 24.3, 0.65, 0.02, 0.35, mat_name="M_Iron_Wrought")

    # ──────────────────────────────────────────
    # 7. Wrought-Iron Cage Lanterns (Ref 5)
    # ──────────────────────────────────────────
    def build_lanterns(self):
        lantern_locs = [
            # Ground entrance flanking lanterns
            ("Lantern_Ground_L", Vector((-2.1, -17.5, 2.6)), math.radians(-45)),
            ("Lantern_Ground_R", Vector((-4.0, -15.8, 2.6)), math.radians(-45)),
            # Staircase landing 1 lantern
            ("Lantern_Stair_Landing1", Vector((-21.8, -14.6, 4.6)), math.radians(-10)),
            # Sally port landing 2 lantern
            ("Lantern_Sally_Port", Vector((-22.1, -12.4, 6.4)), math.radians(20)),
            # Upper observation platform lantern
            ("Lantern_Observation_Deck", Vector((-22.5, -17.2, 16.2)), math.radians(-45))
        ]
        
        for name, w_pos, rot_ang in lantern_locs:
            lx = w_pos.x - self.center.x
            ly = w_pos.y - self.center.y
            lz = w_pos.z - self.center.z
            
            # Wrought iron wall bracket
            self.make_box(f"{name}_Bracket", lx, ly, lz + 0.15, 0.05, 0.45, 0.05, rz=rot_ang, mat_name="M_Iron_Wrought")
            # Cage Lantern Body
            self.make_cylinder(f"{name}_Cage", lx, ly, lz - 0.12, 0.16, 0.12, 0.38, segments=6, rz=rot_ang, mat_name="M_Iron_Wrought")
            # Glowing Candle / Flame Core
            self.make_cylinder(f"{name}_Flame", lx, ly, lz - 0.12, 0.08, 0.08, 0.18, segments=8, mat_name="M_Lantern_Warm")


# ──────────────────────────────────────────────
# Master Upgrade Function
# ──────────────────────────────────────────────

def clean_old_tower_objects():
    """Removes the primitive tower objects while preserving ramparts/walls."""
    c_col = bpy.data.collections.get("Castle")
    if not c_col:
        b_col = bpy.data.collections.get("01_BUILDINGS")
        if b_col:
            c_col = b_col.children.get("Castle")
    if not c_col:
        return
        
    for o in list(c_col.objects):
        # Remove old tower parts (preserve Rampart walls and merlons)
        if o.name.startswith("Castle_Watchtower") or o.name.startswith("Castle_Tower") or \
           o.name.startswith("Castle_Machicolation") or o.name.startswith("Castle_Arrow_Slit") or \
           o.name.startswith("Castle_Parapet"):
            bpy.data.objects.remove(o, do_unlink=True)
            
    print("Cleaned primitive tower objects.")

def upgrade_watchtower_complete():
    print("==================================================")
    print("   MEDIEVAL STONE WATCHTOWER UPGRADE: START")
    print("==================================================")
    clean_old_tower_objects()
    
    # Build complete medieval watchtower at (-26.0, -14.0, 0.0)
    builder = WatchtowerBuilder(cx=-26.0, cy=-14.0, cz=0.0)
    
    print("1. Building battered stone base and multi-tier shaft...")
    builder.build_stone_structure()
    
    print("2. Building ground entrance and elevated sally port...")
    builder.build_entrances()
    
    print("3. Building stone arrow loops and lookout windows...")
    builder.build_openings()
    
    print("4. Building exterior wooden staircase and landings...")
    builder.build_exterior_stairs()
    
    print("5. Building wooden observation platform & hoarding...")
    builder.build_observation_platform()
    
    print("6. Building conical slate roof & weather vane...")
    builder.build_roof_structure()
    
    print("7. Installing wrought-iron lanterns...")
    builder.build_lanterns()
    
    print("==================================================")
    print("   MEDIEVAL STONE WATCHTOWER UPGRADE: COMPLETE")
    print("==================================================")
    return True

if __name__ == "__main__":
    upgrade_watchtower_complete()

