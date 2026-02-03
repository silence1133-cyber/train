# -*- coding: utf-8 -*-
"""
역 이미지 다운로드 스크립트 (매핑 파일 사용)
1. 먼저 browser_console_script.js를 브라우저에서 실행해서 station_prpr_mapping.json 생성
2. 이 스크립트를 실행하면 해당 매핑을 사용해서 이미지 다운로드
"""

import requests
import json
import os
import sys

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 설정
BASE_URL = 'https://hc.kric.go.kr'
IMAGE_BASE = '/hc/ext/images/visual/handicapped/cnv'
IMAGES_DIR = 'station_images'

# 이미지 저장 폴더 생성
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)
    print(f"[생성] '{IMAGES_DIR}' 폴더를 생성했습니다.\n")

# stations.json 파일 로드
print("[로드] stations.json 파일 읽는 중...")
with open('stations.json', 'r', encoding='utf-8') as f:
    stations_data = json.load(f)
print(f"[OK] {len(stations_data)}개 역 정보 로드\n")

# station_prpr_mapping.json 파일 로드
mapping_file = 'station_prpr_mapping.json'
if os.path.exists(mapping_file):
    print(f"[로드] {mapping_file} 파일 읽는 중...")
    with open(mapping_file, 'r', encoding='utf-8') as f:
        prpr_mapping = json.load(f)
    print(f"[OK] {len(prpr_mapping)}개 매핑 정보 로드\n")
else:
    print(f"[경고] {mapping_file} 파일이 없습니다!")
    print(f"[안내] 먼저 browser_console_script.js를 브라우저에서 실행하세요.\n")
    prpr_mapping = {}

# 세션 생성
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://hc.kric.go.kr/hc/index.jsp'
})

def download_image(image_url, save_path):
    """이미지를 다운로드합니다."""
    try:
        response = session.get(image_url, timeout=10)
        
        if response.status_code != 200:
            return False
            
        # 파일 크기 확인 (너무 작으면 에러 이미지일 가능성)
        if len(response.content) < 500:
            return False
            
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return True
        
    except Exception:
        return False

# 결과 저장
results = {
    'total_checked': 0,
    'images_downloaded': 0,
    'failed': []
}

print("[시작] 이미지 다운로드 중...\n")

# 각 역에 대해 처리
for station_name, station_info_list in stations_data.items():
    for station_info in station_info_list:
        results['total_checked'] += 1
        
        rail_code = station_info['railOprIsttCd']
        line_code = station_info['lnCd']
        station_code = station_info['stinCd']
        line_name = station_info.get('lnNm', line_code)
        
        # prprStinCd 찾기
        mapping_key = f"{rail_code}_{line_code}_{station_name}"
        
        if mapping_key in prpr_mapping:
            prpr_stin_cd = prpr_mapping[mapping_key]['prprStinCd']
        else:
            # 매핑이 없으면 원본 코드로 시도
            prpr_stin_cd = station_code
        
        # 이미지 URL 생성
        image_url = f"{BASE_URL}{IMAGE_BASE}/{rail_code}/{rail_code}_{line_code}_{prpr_stin_cd}.png"
        
        # 파일명 생성
        safe_station_name = station_name.replace('/', '_').replace('\\', '_')
        safe_line_name = line_name.replace('/', '_').replace('\\', '_')
        filename = f"{safe_station_name}_{safe_line_name}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # 이미지 다운로드 시도
        if download_image(image_url, filepath):
            results['images_downloaded'] += 1
            
            # 진행 상황 출력 (50개마다)
            if results['images_downloaded'] % 50 == 0:
                print(f"[진행] {results['images_downloaded']}개 이미지 다운로드 완료")
            
            # 처음 10개는 상세 정보 출력
            if results['images_downloaded'] <= 10:
                print(f"[+] {station_name} ({line_name}) -> {filename}")

# 최종 결과
print("\n" + "="*60)
print("[결과] 이미지 다운로드 완료")
print("="*60)
print(f"조회한 역: {results['total_checked']}개")
print(f"다운로드한 이미지: {results['images_downloaded']}개")
print(f"성공률: {results['images_downloaded']/results['total_checked']*100:.1f}%")
print("="*60)

# 결과 저장
result_file = 'image_download_results.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\n[완료] 상세 결과가 '{result_file}'에 저장되었습니다.")
print(f"[완료] 이미지는 '{IMAGES_DIR}' 폴더에 저장되었습니다.")
