# -*- coding: utf-8 -*-
"""
KRIC 웹사이트에서 역 편의시설 이미지를 다운로드하는 스크립트
이미지 URL 패턴: https://hc.kric.go.kr/hc/ext/images/visual/handicapped/cnv/{railOprIsttCd}/{railOprIsttCd}_{lnCd}_{prprStinCd}.png
"""

import requests
import json
import os
import time
import sys

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 설정
BASE_URL = 'https://hc.kric.go.kr'
LEGEND_API = '/hc/visual/handicapped/selectLegendClickInfo.do'
IMAGE_BASE = '/hc/ext/images/visual/handicapped/cnv'
IMAGES_DIR = 'station_images'

# 이미지 저장 폴더 생성
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)
    print(f"[생성] '{IMAGES_DIR}' 폴더를 생성했습니다.")

# stations.json 파일 로드
print("[로드] 역 정보를 불러오는 중...")
with open('stations.json', 'r', encoding='utf-8') as f:
    stations_data = json.load(f)

print(f"[완료] 총 {len(stations_data)}개의 역 정보를 로드했습니다.\n")

# 세션 생성
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://hc.kric.go.kr/hc/index.jsp'
})

# 지역 코드 매핑 (필요시 확장)
AREA_CODE_MAP = {
    'S1': '01',  # 서울교통공사 (수도권)
    'S9': '01',  # 서울9호선
    'KR': '01',  # 한국철도공사 수도권
    'AR': '01',  # 공항철도
    'IC': '01',  # 인천교통공사
    'GX': '01',  # GTX
    # 필요시 다른 지역 코드 추가
}

def get_prpr_stin_cd_mapping(area_cd, line_cd):
    """
    selectLegendClickInfo.do API를 호출하여 역명과 prprStinCd 매핑을 가져옵니다.
    """
    try:
        url = f"{BASE_URL}{LEGEND_API}?paramAreCd={area_cd}&paramLnCd={line_cd}"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'resultStinList' in data:
            mapping = {}
            for station in data['resultStinList']:
                stin_nm = station.get('stinNm')
                prpr_stin_cd = station.get('prprStinCd')
                if stin_nm and prpr_stin_cd:
                    mapping[stin_nm] = prpr_stin_cd
            
            return mapping
        
    except Exception as e:
        print(f"   [ERROR] API 호출 실패: {str(e)[:80]}")
    
    return {}

def download_image(image_url, save_path):
    """이미지를 다운로드합니다."""
    try:
        response = session.get(image_url, timeout=10)
        
        # 404나 다른 에러는 건너뜀
        if response.status_code != 200:
            return False
            
        # 파일 크기가 너무 작으면 스킵
        if len(response.content) < 500:
            return False
            
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return True
        
    except Exception as e:
        return False

# 결과 저장
results = {
    'total_stations': 0,
    'mapping_attempts': 0,
    'mappings_found': 0,
    'images_found': 0,
    'images_downloaded': 0,
    'failed': [],
    'station_images': {}
}

# 노선별로 prprStinCd 매핑 캐시
line_mappings = {}

# 각 역에 대해 처리
station_count = 0
for station_name, station_info_list in stations_data.items():
    for station_info in station_info_list:
        station_count += 1
        results['total_stations'] += 1
        
        rail_code = station_info['railOprIsttCd']
        line_code = station_info['lnCd']
        station_code = station_info['stinCd']
        line_name = station_info.get('lnNm', line_code)
        
        # 진행률 표시 (10개마다)
        if station_count % 10 == 0:
            print(f"[진행] {station_count}/{len(stations_data)} 처리 중...")
        
        # 지역 코드 가져오기
        area_code = AREA_CODE_MAP.get(rail_code, '01')
        
        # 노선별 매핑 캐시 확인
        cache_key = f"{area_code}_{line_code}"
        
        if cache_key not in line_mappings:
            print(f"\n[API] {line_name} 노선의 역 코드 매핑 조회 중...")
            results['mapping_attempts'] += 1
            
            mapping = get_prpr_stin_cd_mapping(area_code, line_code)
            
            if mapping:
                line_mappings[cache_key] = mapping
                results['mappings_found'] += 1
                print(f"   [OK] {len(mapping)}개 역 매핑 완료")
            else:
                line_mappings[cache_key] = {}
                print(f"   [FAIL] 매핑 실패")
            
            time.sleep(0.5)  # API 호출 간 딜레이
        
        # prprStinCd 찾기
        prpr_stin_cd = line_mappings.get(cache_key, {}).get(station_name)
        
        if not prpr_stin_cd:
            # 매핑을 찾지 못한 경우 원본 코드로 시도
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
            results['images_found'] += 1
            
            if station_name not in results['station_images']:
                results['station_images'][station_name] = []
            
            results['station_images'][station_name].append({
                'line_name': line_name,
                'filename': filename,
                'url': image_url,
                'rail_code': rail_code,
                'line_code': line_code,
                'prpr_stin_cd': prpr_stin_cd
            })
            
            # 간헐적으로 성공 메시지 출력
            if results['images_downloaded'] % 50 == 0:
                print(f"   [+] {results['images_downloaded']}개 이미지 다운로드 완료")

# 최종 결과
print("\n" + "="*60)
print("[결과] 다운로드 완료")
print("="*60)
print(f"조회한 역(호선): {results['total_stations']}개")
print(f"API 매핑 시도: {results['mapping_attempts']}개 노선")
print(f"매핑 성공: {results['mappings_found']}개 노선")
print(f"다운로드한 이미지: {results['images_downloaded']}개")
print("="*60)

# 결과를 JSON으로 저장
result_file = 'image_download_results.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\n[완료] 결과가 '{result_file}'에 저장되었습니다.")
print(f"[완료] 이미지는 '{IMAGES_DIR}' 폴더에 저장되었습니다.")

# 성공한 역 몇 개 예시 출력
if results['station_images']:
    print("\n[예시] 이미지를 찾은 역:")
    for station_name, images in list(results['station_images'].items())[:5]:
        print(f"   - {station_name}: {len(images)}개 이미지")
