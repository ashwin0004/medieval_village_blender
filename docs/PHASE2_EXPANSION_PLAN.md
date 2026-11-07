# Phase 2 World Expansion Plan: Photorealistic Medieval Fantasy Environment

## 1. Project Philosophy & Spatial Preservation
- **Original Village Layout Intact**: The existing core village, timber-frame cottages, stone church, Romanesque watchtower, cobblestone roads, and stone bridge will remain completely preserved in place.
- **Radial Expansion**: New themed districts expand outward into natural geographic zones (riverbanks, southeastern valley, western woodland, and northern mountain peaks).
- **Asset Sourcing**: Prioritize CC0 models and scanned textures (Poly Haven, ambientCG, Blender demo assets) optimized for 16 GB RAM using linked duplicate instancing and LOD geometry.

---

## 2. Spatial Map & Coordinate Placement

```
                        [NORTH: High Mountain Ridge]
              (X: -20 to +10, Y: +75 to +110, Z: +35 to +55)
                  ★★★ DISTANT CASTLE RUINS ★★★
             Broken stone towers, collapsed curtain walls,
                     mossy battlements & crags

                                ▲
                                │  (Atmospheric mountain pass)
  [WEST: Woodland & Plateau]    │        [EAST: River Glade & Farmland]
                                │
  ★★★ RIVERSIDE FISHING GLADE ★★★  ═════╗  ★★★ WATERMILL DISTRICT ★★★
  (X: -18 to -8, Y: +20 to +28)        ║  (X: +14 to +22, Y: +20 to +28)
  - Wooden fishing pier & dock         ║  - Stone & timber mill building
  - Moored rowboat, fishing nets       ║  - Large rotating wooden water wheel
  - River reeds, stone water steps     ║  - Sluice gate, flour sacks, grain cart
                                       ║
               [STONE ARCH BRIDGE] ════╬════ (River flow east to west)
               (X: +3 to +9, Y: +18 to +25)
                                       ║
  ★★★ WATCHTOWER & CHURCH ★★★          ║  ★★★ MAIN MARKETPLACE SQUARE ★★★
  (X: -18 to -5, Y: -25 to +15)        ║  (X: -5 to +10, Y: -35 to -15)
  - Preserved Romanesque masonry       ║  - Merchant stalls, cloth canopies
  - Medieval living characters         ║  - Produce baskets, bread, barrels
                                       ║  - Town well, hanging iron signs
                                       ║
  ★★★ FOREST SETTLEMENT ★★★            ║  ★★★ MEDIEVAL FARMING DISTRICT ★★★
  (X: -50 to -35, Y: -35 to -10)       ║  (X: +16 to +42, Y: -45 to -15)
  - Woodcutter cabin & log piles       ║  - Agricultural barn & stables
  - Chopping block, axe, handcart      ║  - Apple orchard & vegetable garden
  - Roadside stone shrine, ferns       ║  - Cabbage, pumpkins, carrot rows
  - Wild mushrooms, fallen logs        ║  - Split-rail fences, haystacks, animals
                                       ║    (Horses, sheep, cows, chickens)
```

---

## 3. Detailed District Specifications

### A. Watermill District (`X: +14 to +22, Y: +20 to +28`)
- **Location**: East of the Stone Bridge along the weir cascade where the river elevation drops.
- **Key Elements**:
  - Mill Building ($8\text{m} \times 6\text{m}$): Ashlar stone ground level with timber-framed upper story, pitched tile roof, and wooden delivery door.
  - Water Wheel ($\varnothing 4.2\text{m}$): Aged oak spokes and paddle buckets, half-submerged in the river current with foam/splash particles.
  - Mill Race & Sluice: Wooden timbers directing water into the wheel channel.
  - Props: Sacks of ground flour, grain barrels, handcart, wooden dock platform.

### B. Riverside Fishing Glade (`X: -18 to -8, Y: +20 to +28`)
- **Location**: West of the Stone Bridge where the river widens into a calm deep pool.
- **Key Elements**:
  - Wooden Dock: Weathered oak pilings and plank decking reaching into the water.
  - Fishing Boat: Authentic small wooden skiff moored to a wooden cleat.
  - Equipment: Suspended fish drying racks, hemp nets with cork floats, coiled ropes, tackle crates.
  - Nature: Lush river reeds, cattails, water lilies, and smooth submerged river pebbles.

### C. Medieval Farming District (`X: +16 to +42, Y: -45 to -15`)
- **Location**: Expansive sunny valley southeast of the residential road.
- **Key Elements**:
  - Barn & Stables ($12\text{m} \times 8\text{m}$): Weathered timber barn with hayloft, lean-to horse shed, and water troughs.
  - Orchard: Rows of apple trees with fruit, fallen apples, and wooden gathering ladders.
  - Crops: Mounded soil beds with green cabbages, leafy carrot tops, and orange pumpkins.
  - Pastures & Fences: Wooden post-and-rail fences enclosing grassy paddocks.
  - Livestock: Realistic horses in paddock, sheep grazing, free-roaming hens and roosters.
  - Agricultural Props: Haystacks with pitchforks, wooden wheelbarrows, scarecrow with burlap tunic.

### D. Forest Settlement & Woodcutter Glade (`X: -50 to -35, Y: -35 to -10`)
- **Location**: Dense pine and oak woodland southwest of the Watchtower.
- **Key Elements**:
  - Woodcutter Cabin: Rustic rough-hewn log cabin with stone chimney and wood shingle roof.
  - Firewood Yard: Neatly stacked cords of split firewood, cut rounds, and birch logs.
  - Work Area: Massive tree stump chopping block with embedded iron axe, crosscut saws, wood shavings.
  - Woodland Shrine: Ancient lichen-covered stone cairn with carved Celtic rune and candle niche.
  - Natural Clutter: Fallen mossy log bridges, shelf fungi, forest mushrooms, and fern beds.

### E. Distant Castle Ruins (`X: -20 to +10, Y: +75 to +110, Z: +35 to +55`)
- **Location**: High northern mountain ridge framing the horizon.
- **Key Elements**:
  - Ruined Keep: Cylindrical stone keep with collapsed parapet and gaping arched windows.
  - Curtain Wall: Broken crenellations, fallen stone rubble slopes, and ruined gothic portal arch.
  - Overgrowth: Mountain pines clinging to cliffs, creeping ivy, and atmospheric mountain mist.

### F. Marketplace & Living Villagers (`X: -5 to +10, Y: -35 to -15`)
- **Market Enhancements**: Striped linen awnings (terracotta, cream, olive), fruit baskets (apples, pears), round bread loaves, clay amphoras, and cheese wheels.
- **3D Characters**:
  - Blacksmith hammering at the forge anvil.
  - Market merchants behind wooden counters.
  - Villagers conversing near the town well.
  - Farmer wheeling a wooden barrow.
  - Fisherman sitting on the river dock.

---

## 4. Execution Phases

| Phase | Milestone | Deliverable |
|---|---|---|
| **Phase A** | Scene Audit & Safety Backup | ✅ Completed: Backup saved (`Medieval_Village_pre_phase2_expansion_...blend`) |
| **Phase B** | External Asset Sourcing & Testing | Poly Haven & ambientCG CC0 models (animals, boats, props, farming) |
| **Phase C** | Watermill & Riverside District | Modeled watermill, water wheel, fishing pier, boat, and water shader |
| **Phase D** | Farming District & Livestock | Barn, stables, crops, fences, orchard, and animals (horses, sheep, chickens) |
| **Phase E** | Forest Settlement | Woodcutter cabin, lumber piles, chopping block, shrine, mushrooms |
| **Phase F** | Distant Castle Ruins | Ruined towers, broken walls, and atmospheric perspective |
| **Phase G** | Marketplace & Villagers | Detailed produce, well props, and medieval characters |
| **Phase H** | Storytelling & Micro Details | Chimney smoke, flower boxes, balconies, lanterns, puddles |
| **Phase I** | Cinematic Cameras & 3 Lightings | Daylight, Sunset, Nighttime renders (10 cinematic compositions) |

