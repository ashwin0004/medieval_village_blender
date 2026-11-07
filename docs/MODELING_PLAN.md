# Modeling Plan: Photorealistic AAA Medieval Fantasy Transformation

## Objective
Elevate the existing Medieval Village blockout into a cinematic AAA game environment while strictly preserving existing village architecture, road topology, watchtower location, and layout.

## Reference Analysis (Based on Supplied Art Direction)
1. **Alpine River Glade & Canyon Valley**:
   - Mountain valley with rocky riverbank, foaming water, and stone arch bridge connecting village quarters.
   - Distinct elevation steps from waterfront up through terraced streets.
2. **Timber-Framed & Stone Masonry Architecture**:
   - Heavy timber-frame upper storeys over weathered ashlar stone bases.
   - Overhanging eaves, slate and clay roof tiles with natural color variation and moss.
3. **Realistic Foliage & Nature**:
   - Dense mixed European woodland: ancient broadleaf oaks, towering Scots pines, and textured understory bushes.
   - Natural ground clutter: mossy boulders, fallen branches, dirt paths, and weeds along stone borders.

## Execution Stages
1. **Stage 1: Realistic Tree & Rock Validation (Current)**
   - Import 1 broadleaf oak (`tree_small_02`), 1 conifer pine (`pine_tree_01`), and 1 river boulder (`boulder_01`).
   - Validate shaders, texture paths, and alpha blending in Blender Cycles.
   - Position test specimens at the riverbank/forest edge without deleting existing placeholder trees.
   - Render `renders/Test_Realistic_Trees_Preview.png` for user review.

2. **Stage 2: Forest & Nature Replacement**
   - Replace 72 stylized cone/sphere placeholders with linked duplicate instances (memory-safe).
   - Add rotation and subtle scale variation to prevent repetitive silhouette.
   - Plant river boulders along water borders and rock steps.

3. **Stage 3: Water, Bridge & Watermill**
   - Refine continuous riverbed depth, submerged river rocks, and Cycles water shader (IOR 1.333, depth absorption).
   - Authenticate medieval stone arch bridge with keystones and weathered parapets.
   - Add watermill building with rotating wooden water wheel at the weir cascade.

4. **Stage 4: Road & Market Polish**
   - Enhance cobblestones with crowned road profile, mud patches, and drainage runnels.
   - Fill marketplace with detailed props: barrels, woven baskets, flour sacks, pottery jugs, and carts.

5. **Stage 5: Master Cinematic Lighting & 12 Portfolio Renders**
   - Daylight (bright crisp morning sun).
   - Sunset (warm golden hour alpine glow).
   - Nighttime (atmospheric moonlight with glowing warm tavern lanterns and windows).
