# -*- coding: utf-8 -*-
"""
station_prpr_mapping_ok.json에 있는 역들의 편의시설 이미지를 일괄 다운로드
URL: https://hc.kric.go.kr/hc/ext/images/visual/handicapped/cnv/{railOprIsttCd}/{railOprIsttCd}_{lnCd}_{prprStinCd}.png
"""

import requests
import json
import os
import sys
import time

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = 'https://hc.kric.go.kr/hc/ext/images/visual/handicapped/cnv'
IMAGES_DIR = 'station_images'
MAPPING_FILE = 'station_prpr_mapping_ok.json'

os.makedirs(IMAGES_DIR, exist_ok=True)

with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://hc.kric.go.kr/hc/index.jsp'
})

total = len(mapping)
downloaded = 0
failed = []

for key, info in mapping.items():
    rail = info['railOprIsttCd']
    ln = info['lnCd']
    prpr = info['prprStinCd']
    name = info['stinNm']

    image_url = f"{BASE_URL}/{rail}/{rail}_{ln}_{prpr}.png"
    safe_name = name.replace('/', '_').replace('\\', '_')
    filename = f"{safe_name}_{rail}_{ln}.png"
    filepath = os.path.join(IMAGES_DIR, filename)

    try:
        r = session.get(image_url, timeout=15)
        if r.status_code == 200 and len(r.content) >= 500:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            downloaded += 1
            if downloaded % 20 == 0 or downloaded <= 5:
                print(f"[OK] {downloaded}/{total} {name} ({rail}_{ln})")
        else:
            failed.append((name, image_url))
    except Exception as e:
        failed.append((name, image_url))

    time.sleep(0.3)

print("\n" + "="*50)
print(f"다운로드 완료: {downloaded}/{total}")
print(f"실패: {len(failed)}개")
print("="*50)
print(f"이미지 저장 위치: {os.path.abspath(IMAGES_DIR)}")

if failed:
    with open('download_failed.txt', 'w', encoding='utf-8') as f:
        for name, url in failed:
            f.write(f"{name}\t{url}\n")
    print(f"실패 목록: download_failed.txt")
