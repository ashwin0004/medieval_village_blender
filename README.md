# Medieval Fantasy Village — Blender 3D Environment

A detailed medieval fantasy village environment created in **Blender 5.2.3** using the Blender Python API. The project focuses on realistic European medieval architecture, modular construction, environmental storytelling, PBR materials, terrain, vegetation, roads, a river and stone bridge, village props, and cinematic lighting.

**Repository:** [ashwin0004/medieval_village_blender](https://github.com/ashwin0004/medieval_village_blender)

---

## Project Overview

This project develops a medieval European-inspired village from an initial blockout into a richly detailed environment. The scene combines stone foundations, timber-framed buildings, steep tiled roofs, a market area, a church, a fortified watchtower, a river landscape, a stone bridge, vegetation, and everyday village objects.

The project is built with Blender and Python automation. Reusable scripts are organized by production task, while separate render scripts create focused previews and presentation views.

### Key areas represented in the project

- Medieval timber-and-stone architecture
- Main cottage and modular architectural components
- Village buildings and landmark structures
- Marketplace and street-life props
- Cobblestone roads and pathways
- River environment and stone bridge
- Terrain, trees, vegetation and wildflowers
- PBR material setup and material showcases
- Daylight, sunset and nighttime lighting presentations
- Camera setups and render showcases

> The repository includes a production modeling plan describing a broader 85+ asset library. That document is a design/production specification; it should not be interpreted as proof that every listed asset is already modeled.

---

## Visual Gallery

The repository contains multiple renders and camera showcases. The following images are linked from the `renders/` directory.

### Final environment views

| Daylight — Aerial overview | Sunset — Aerial vista |
|:---:|:---:|
| ![Daylight aerial overview](renders/Final_Daylight_Aerial_Overview.png) | ![Sunset aerial vista](renders/Final_Sunset_Aerial_Vista.png) |

| Nighttime — Aerial overview | River and stone bridge |
|:---:|:---:|
| ![Nighttime aerial overview](renders/Final_Nighttime_Aerial_Overview.png) | ![River and stone bridge](renders/Final_Daylight_River_Bridge.png) |

### Architecture and village life

| Cottage architecture | Street market |
|:---:|:---:|
| ![Cottage architecture](renders/Final_Daylight_Cottage_Architecture.png) | ![Street market](renders/Final_Daylight_Street_Market.png) |

| Church and castle | Main street |
|:---:|:---:|
| ![Church and castle](renders/Church_and_Castle.png) | ![Main street](renders/Main_Street.png) |

### Additional showcases

- [All render images](renders/)
- [Terrain and nature showcases](renders/nature/)
- [Road network showcases](renders/roads/)
- [Marketplace showcases](renders/marketplace/)
- [Watchtower showcases](renders/watchtower/)
- [Modular architecture showcases](renders/modular_kit/)
- [Props showcases](renders/props/)
- [Village world showcases](renders/village_world/)

---

## Technology and Tools

| Tool | Purpose |
|---|---|
| [Blender 5.2.3](https://www.blender.org/) | 3D modeling, materials, scene assembly and rendering |
| Blender Python API (`bpy`) | Procedural modeling and scene automation |
| `bmesh` | Mesh editing and geometry operations |
| `mathutils` | Vector, matrix and transformation operations |
| Cycles | Physically based rendering |
| NVIDIA OptiX | GPU rendering acceleration where supported |
| Git | Version control |
| Git LFS | Versioning large Blender project files and PNG renders |

---

## Repository Structure

The main folders are organized by asset type, scripts, documentation and presentation renders.

```text
medieval_village_blender/
│
├── Medieval_Village.blend
│
├── assets/
│   ├── architecture/
│   │   └── modular_kit.blend
│   ├── buildings/
│   │   └── main_cottage.blend
│   ├── props/
│   │   └── village_props.blend
│   └── world/
│       └── village_world.blend
│
├── backups/
│   └── Previous project versions
│
├── docs/
│   └── MODELING_PLAN.md
│
├── renders/
│   ├── blockout/
│   ├── cottage/
│   ├── marketplace/
│   ├── modular_kit/
│   ├── nature/
│   ├── polish/
│   ├── props/
│   ├── roads/
│   ├── upgraded_buildings/
│   ├── village_world/
│   └── watchtower/
│
├── scripts/
│   ├── build_*.py
│   ├── upgrade_*.py
│   ├── polish_*.py
│   ├── render_*.py
│   ├── scene_setup.py
│   ├── materials_library.py
│   └── camera_setup_detailed.py
│
├── textures/
│   ├── ground/
│   ├── roof/
│   ├── stone/
│   └── wood/
│
├── .gitattributes
└── .gitignore
```

---

## Main Project Components

### 1. Architecture

The architectural direction is based on medieval European vernacular buildings:

- Stone masonry foundations and lower floors
- Timber framing and plaster infill
- Weathered wooden beams and doors
- Steep pitched roofs with clay or slate-style tiles
- Chimneys, windows, shutters and architectural trim
- Modular components for reusable building construction

The detailed cottage and modular kit are important foundation assets for the wider village environment.

### 2. Village buildings and landmarks

The production plan covers a range of village building types, including:

- Main cottage
- Tavern
- Church or chapel
- Castle watchtower
- Blacksmith
- Barn and farm buildings
- Baker's shop
- Workshops and riverside structures

The modeling plan also describes additional building variations and landmark concepts for future expansion.

### 3. Environment and terrain

Environmental work is organized around:

- Rolling terrain and village ground
- Cobblestone streets and road networks
- River mesh and water presentation
- Stone bridge
- Trees, bushes, grass and wildflowers
- Rocks, riverbank elements and natural details
- Environmental props and set dressing

### 4. Marketplace and props

The project includes dedicated scripts and render groups for the marketplace and village props. The intended visual language includes timber stalls, fabric canopies, carts, barrels, crates, baskets, tables, lanterns, signs and other objects that help make the village feel inhabited.

### 5. Materials and lighting

The project includes material-building and polishing scripts, along with material showcase renders. Lighting and camera scripts support presentation under different moods:

- Daylight
- Golden-hour sunset
- Nighttime illumination

The goal is to present the same environment with different lighting and atmosphere.

---

## Python Automation

The `scripts/` directory contains scripts grouped around building, upgrading, polishing, camera setup and rendering.

Some important script names include:

| Script | Intended role |
|---|---|
| `build_stage1.py` | Initial scene/blockout stage |
| `build_detailed_cottage.py` | Detailed cottage construction |
| `build_modular_kit.py` | Modular architecture construction |
| `build_marketplace.py` | Marketplace construction |
| `build_river_and_bridge.py` | River and bridge construction |
| `build_road_network.py` | Road and street network |
| `build_environmental_details.py` | Environmental details |
| `build_pbr_materials_master.py` | PBR material setup |
| `upgrade_buildings.py` | Building upgrades |
| `upgrade_terrain_vegetation.py` | Terrain and vegetation work |
| `upgrade_watchtower.py` | Watchtower upgrade |
| `materials_library.py` | Reusable material definitions |
| `lighting_manager.py` | Lighting management |
| `render_final_quality_master.py` | Final-quality render workflow |
| `render_marketplace_showcases.py` | Marketplace render views |
| `render_river_showcases.py` | River render views |
| `render_watchtower_showcases.py` | Watchtower render views |

These descriptions indicate each script's apparent role from its filename; inspect the script before running it to understand its exact behavior and dependencies.

---

## Getting Started

### Requirements

- Blender **5.2.3** (or a compatible version; scripts may depend on specific Blender APIs)
- Windows, macOS or Linux
- A system capable of handling the scene's geometry and textures
- NVIDIA GPU and OptiX support for the configured GPU-rendering workflow (optional; CPU rendering may be possible after configuring Blender)

### 1. Clone the repository

Install Git and Git LFS, then run:

```bash
git lfs install
git clone https://github.com/ashwin0004/medieval_village_blender.git
cd medieval_village_blender
```

Git LFS is important because large `.blend` and `.png` files are stored as LFS objects. A normal clone with Git LFS installed should retrieve the actual file contents. If you have already cloned without downloading LFS objects, run:

```bash
git lfs pull
```

### 2. Open the Blender project

1. Launch Blender.
2. Select **File → Open**.
3. Browse to `Medieval_Village.blend`.
4. Open the scene and inspect the collections, materials, cameras and objects.

### 3. Run a Python script (optional)

Scripts are intended to be run with Blender's Python environment because they use the `bpy` API.

You can open a script in Blender's Scripting workspace and run it after reviewing its contents. You can also run a script from a terminal:

```bash
blender --background Medieval_Village.blend --python scripts/NAME_OF_SCRIPT.py
```

Replace `NAME_OF_SCRIPT.py` with the script you intend to execute. Some scripts may create or modify scene objects, overwrite files or depend on a particular scene state. **Make a copy of the project before running build, upgrade or polish scripts.** Run scripts in the intended production order, not all at once.

### 4. Render the scene

Open the project in Blender, select an appropriate camera and render engine, configure output resolution and sampling, then use **Render → Render Image**.

The project contains dedicated camera and render scripts that can be inspected for specific showcase workflows.

---

## Modeling Plan and Design Specifications

The detailed production plan is available here:

[**docs/MODELING_PLAN.md**](docs/MODELING_PLAN.md)

It documents:

- Metric architectural scale and proportions
- Building and modular architecture concepts
- Village structures and furniture props
- Street objects and infrastructure
- Environment, flora and landscape assets
- Production milestones
- Hardware and memory optimization targets

The plan describes a broad asset library and roadmap. The actual contents of the current `.blend` files and scripts determine which items are implemented.

---

## Performance and Optimization

The modeling plan targets a Windows PC with 16 GB RAM and an NVIDIA RTX-class GPU. The intended optimization practices include:

- Linked duplicates and collection instances for repeated objects
- Reusable modular architecture
- Lightweight bevel modifier settings
- Efficient scene organization
- Sensible texture resolutions
- GPU rendering with OptiX when supported
- Separate camera and showcase render workflows

Actual render performance depends on scene complexity, texture sizes, GPU memory and Blender settings.

---

## Git and Large Files

This repository uses **Git LFS (Large File Storage)** for large Blender project files and PNG render images. The `.gitattributes` file defines which extensions use LFS.

For normal updates:

```bash
git add .
git commit -m "Describe your project update"
git push
```

Avoid committing generated Python cache files (`__pycache__/`, `*.pyc`) and Blender backup files (`*.blend1`, `*.blend2`). The `.gitignore` file should contain these patterns.

---

## Credits and Asset Licenses

If the project uses third-party models, textures, HDRIs, fonts or other assets, their original creators and license terms should be recorded in an asset credits document.

Before redistributing the project or any third-party asset, verify the asset's license and attribution requirements. Blender files may contain embedded third-party assets, so check them as well.

---

## Future Improvements

Potential areas for further development, based on the production plan:

- Expand the building collection with additional medieval building types
- Add more modular architectural variations
- Expand village structures and interior details
- Improve environmental set dressing and natural variation
- Add more animated or interactive scene elements
- Continue optimizing large scenes and render workflows
- Produce additional cinematic camera sequences

---

## Author

**Ashwin Biju**

- GitHub: [@ashwin0004](https://github.com/ashwin0004)
- Project repository: [medieval_village_blender](https://github.com/ashwin0004/medieval_village_blender)

---

## License

No license file is currently identified in this repository. Unless a license is added, assume the project is shared for viewing and that reuse, modification and redistribution are not automatically granted. Third-party assets may have separate licenses.
