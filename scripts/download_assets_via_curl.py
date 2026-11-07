import os
import sys
import json
import subprocess

def run_curl_json(url):
    cmd = ["curl.exe", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", url]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error curling {url}: {res.stderr}")
        return None
    try:
        return json.loads(res.stdout)
    except Exception as e:
        print(f"JSON decode error: {e}")
        return None

def download_file(url, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        print(f"Already exists: {target_path} ({os.path.getsize(target_path)} bytes)")
        return True
    print(f"Downloading {url} -> {target_path} ...")
    cmd = ["curl.exe", "-L", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "-o", target_path, url]
    res = subprocess.run(cmd)
    if res.returncode == 0 and os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        print(f"Success ({os.path.getsize(target_path)} bytes)")
        return True
    else:
        print(f"Failed to download {url}")
        return False

def download_polyhaven_asset(asset_id, output_dir, resolution="1k"):
    meta_url = f"https://api.polyhaven.com/files/{asset_id}"
    data = run_curl_json(meta_url)
    if not data:
        print(f"No metadata found for {asset_id}")
        return False

    blend_entry = data.get("blend", {}).get(resolution, {})
    if not blend_entry:
        for res in ["2k", "1k", "4k"]:
            if res in data.get("blend", {}):
                resolution = res
                blend_entry = data["blend"][res]
                break

    if not blend_entry:
        print(f"No blend file found for {asset_id}")
        return False

    blend_file = blend_entry.get("blend", {})
    blend_url = blend_file.get("url")
    if blend_url:
        blend_filename = os.path.basename(blend_url)
        download_file(blend_url, os.path.join(output_dir, blend_filename))

    includes = blend_file.get("include", {})
    for rel_path, inc_meta in includes.items():
        inc_url = inc_meta.get("url")
        if inc_url:
            local_target = os.path.join(output_dir, rel_path)
            download_file(inc_url, local_target)

    print(f"Completed download of {asset_id} to {output_dir}")
    return True

if __name__ == "__main__":
    assets_to_download = [
        ("boulder_01", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\rocks\boulder_01"),
        ("tree_small_02", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\oak\tree_small_02"),
        ("pine_tree_01", r"c:\Users\ashwi\Documents\Medieval_Village_Project\assets\trees\pine\pine_tree_01")
    ]
    for asset_id, out_dir in assets_to_download:
        print(f"\n================ Processing {asset_id} ================")
        download_polyhaven_asset(asset_id, out_dir, "1k")
