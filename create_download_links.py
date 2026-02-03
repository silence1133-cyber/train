# -*- coding: utf-8 -*-
"""
station_prpr_mapping_ok.json 기준으로 이미지 다운로드 링크 HTML 생성.
브라우저에서 이 HTML을 열고, '한 번에 링크 열기' 또는 각 링크를 클릭해 저장하면 됨.
"""

import json
import os
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = 'https://hc.kric.go.kr/hc/ext/images/visual/handicapped/cnv'
MAPPING_FILE = 'station_prpr_mapping_ok.json'
OUT_HTML = 'download_image_links.html'

with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

rows = []
for key, info in mapping.items():
    rail = info['railOprIsttCd']
    ln = info['lnCd']
    prpr = info['prprStinCd']
    name = info['stinNm']
    url = f"{BASE_URL}/{rail}/{rail}_{ln}_{prpr}.png"
    safe_name = name.replace('/', '_').replace('\\', '_')
    filename = f"{safe_name}_{rail}_{ln}.png"
    rows.append(f'  <a data-link="station" href="{url}" download="{filename}" target="_blank">{name} ({rail}_{ln})</a>')

html = '''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>역 이미지 다운로드 링크</title>
  <style>
    body { font-family: "Malgun Gothic"; padding: 20px; }
    a { display: block; padding: 6px 0; color: #667eea; }
    a:hover { text-decoration: underline; }
    button {
      margin: 15px 0;
      padding: 10px 18px;
      border: none;
      border-radius: 8px;
      background: #667eea;
      color: #fff;
      cursor: pointer;
      font-size: 15px;
    }
    button:disabled {
      background: #b3b7ff;
      cursor: not-allowed;
    }
  </style>
</head>
<body>
  <h1>역 편의시설 이미지 다운로드 (85개)</h1>
  <p>각 링크를 클릭하면 해당 역 이미지가 다운로드됩니다. (또는 우클릭 → 다른 이름으로 링크 저장)</p>
  <p><button id="openAllBtn">한 번에 링크 열기 (팝업 허용 필요)</button></p>
  <script>
    const btn = document.getElementById('openAllBtn');
    btn.addEventListener('click', () => {
      const links = Array.from(document.querySelectorAll('a[data-link="station"]'));
      if (!links.length) return;
      btn.disabled = true;
      let index = 0;
      const timer = setInterval(() => {
        if (index >= links.length) {
          clearInterval(timer);
          btn.disabled = false;
          return;
        }
        const link = links[index];
        const win = window.open(link.href, '_blank');
        if (!win) {
          alert('팝업이 차단되었습니다. 브라우저에서 팝업 허용 후 다시 시도하세요.');
          clearInterval(timer);
          btn.disabled = false;
          return;
        }
        setTimeout(() => {
          try {
            if (win && !win.closed) {
              win.close();
            }
          } catch (e) {
            console.warn('탭 자동 종료 실패:', e);
          }
        }, 2500);
        index += 1;
      }, 600);
    });
  </script>
''' + '\n'.join(rows) + '''
</body>
</html>
'''

with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"[OK] {OUT_HTML} 생성됨 (총 {len(rows)}개 링크)")
print(f"     브라우저에서 {OUT_HTML} 을 연 뒤 링크를 클릭해 이미지를 저장하세요.")
