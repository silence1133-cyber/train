# -*- coding: utf-8 -*-
"""
station_images 폴더의 PNG 파일명을 station_prpr_mapping.json 키 이름으로 변경.
새 이름: "{키} (기존파일명).png"
예: S1_4_0477.png -> S1_4_이촌 (S1_4_0477).png
"""

import json
import os
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

MAPPING_FILE = 'station_prpr_mapping.json'
IMAGES_DIR = 'station_images'

with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# (railOprIsttCd, lnCd, prprStinCd) -> key
file_to_key = {}
for key, info in mapping.items():
    rail = info['railOprIsttCd']
    ln = info['lnCd']
    prpr = info['prprStinCd']
    fname = f"{rail}_{ln}_{prpr}.png"
    file_to_key[fname] = key

renamed = 0
skipped = 0
for filename in os.listdir(IMAGES_DIR):
    if not filename.lower().endswith('.png'):
        continue
    if filename in file_to_key:
        key = file_to_key[filename]
        new_name = f"{key} ({filename})"
        old_path = os.path.join(IMAGES_DIR, filename)
        new_path = os.path.join(IMAGES_DIR, new_name)
        if old_path != new_path:
            os.rename(old_path, new_path)
            renamed += 1
            print(f"[OK] {filename} -> {new_name}")
    else:
        skipped += 1
        print(f"[SKIP] {filename} (매핑 없음)")

print("\n" + "="*50)
print(f"변경: {renamed}개, 매핑 없음: {skipped}개")
