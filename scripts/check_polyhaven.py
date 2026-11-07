import urllib.request
import json
import os

assets = ['boulder_01', 'tree_small_02', 'pine_tree_01', 'fir_tree_01']
for asset in assets:
    try:
        url = f'https://api.polyhaven.com/files/{asset}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f'=== {asset} ===')
            if 'blend' in data:
                print('blend formats:', list(data['blend'].keys()))
                for res in ['1k', '2k']:
                    if res in data['blend']:
                        b_obj = data['blend'][res].get('blend', {})
                        size_kb = b_obj.get('size', 0) // 1024
                        print(f"  blend {res}: {b_obj.get('url')} ({size_kb} KB)")
                        includes = data['blend'][res].get('include', {})
                        print(f"  includes ({len(includes)} items): {list(includes.keys())[:5]}")
            if 'gltf' in data:
                print('gltf formats:', list(data['gltf'].keys()))
                for res in ['1k', '2k']:
                    if res in data['gltf']:
                        g_obj = data['gltf'][res].get('gltf', {})
                        size_kb = g_obj.get('size', 0) // 1024
                        print(f"  gltf {res}: {g_obj.get('url')} ({size_kb} KB)")
    except Exception as e:
        print(f'Error for {asset}: {e}')

