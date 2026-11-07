import os
import sys
sys.path.append(r"c:\Users\ashwi\Documents\Medieval_Village_Project\scripts")
from download_assets_via_curl import download_polyhaven_asset

if __name__ == "__main__":
    bushes = [
        ("shrub_01", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\bushes\shrub_01"),
        ("shrub_02", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\vegetation\bushes\shrub_02")
    ]
    for asset_id, out_dir in bushes:
        print(f"\nDownloading bush asset: {asset_id} to {out_dir}")
        download_polyhaven_asset(asset_id, out_dir, "1k")

