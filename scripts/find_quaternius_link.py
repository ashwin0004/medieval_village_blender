import subprocess
import re

cmd = ['curl.exe', '-s', '-L', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'https://quaternius.com/packs/farmanimal.html']
html = subprocess.run(cmd, capture_output=True, text=True).stdout
print(f"HTML length: {len(html)}")
links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html)
for l in links:
    if any(k in l.lower() for k in ['zip', 'drive', 'mega', 'itch', 'gumroad', 'patreon', 'download', 'farm']):
        print('Found link:', l)

