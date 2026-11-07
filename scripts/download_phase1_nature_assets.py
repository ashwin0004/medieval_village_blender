import sys
import os
sys.path.append(r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts")
from download_assets_via_curl import download_polyhaven_asset

assets = [
    ("fir_sapling", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\trees\fir_sapling"),
    ("rock_moss_set_01", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\rocks\rock_moss_set_01"),
    ("rock_moss_set_02", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\rocks\rock_moss_set_02"),
    ("fern_02", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\ferns\fern_02")
]

if __name__ == "__main__":
    for asset_id, out_dir in assets:
        print(f"\n================ Processing {asset_id} ================")
        download_polyhaven_asset(asset_id, out_dir, "1k")

