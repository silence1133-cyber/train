# -*- coding: utf-8 -*-
"""
KRIC 웹사이트에서 수유실 이미지를 크롤링하는 스크립트
https://hc.kric.go.kr/hc/index.jsp
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin
import sys

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 설정
BASE_URL = 'https://hc.kric.go.kr'
IMAGES_DIR = 'nursing_room_images'

# 이미지 저장 폴더 생성
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)
    print(f"[생성] '{IMAGES_DIR}' 폴더를 생성했습니다.")

# stations.json 파일 로드
print("[로드] 역 정보를 불러오는 중...")
with open('stations.json', 'r', encoding='utf-8') as f:
    stations_data = json.load(f)

print(f"[완료] 총 {len(stations_data)}개의 역 정보를 로드했습니다.\n")

# 세션 생성 (쿠키 유지)
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

def get_station_facility_page(station_name, rail_code, line_code, station_code):
    """특정 역의 편의시설 페이지를 가져옵니다."""
    
    # 가능한 URL 패턴들을 시도
    url_patterns = [
        f"{BASE_URL}/hc/stationInfo.do?railOprIsttCd={rail_code}&lnCd={line_code}&stinCd={station_code}",
        f"{BASE_URL}/hc/station.do?railOprIsttCd={rail_code}&lnCd={line_code}&stinCd={station_code}",
        f"{BASE_URL}/hc/convFacility.do?railOprIsttCd={rail_code}&lnCd={line_code}&stinCd={station_code}",
        f"{BASE_URL}/hc/stationCnvFacl.do?railOprIsttCd={rail_code}&lnCd={line_code}&stinCd={station_code}",
    ]
    
    print(f"[검색] {station_name} 페이지 조회 중...")
    
    for url in url_patterns:
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200 and len(response.text) > 1000:
                print(f"   [OK] URL 발견: {url}")
                return response.text, url
        except Exception as e:
            print(f"   [WARN] {url} 실패: {str(e)[:50]}")
            continue
    
    return None, None

def extract_images_from_html(html_content, base_url):
    """HTML에서 이미지 URL을 추출합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    image_urls = []
    
    # 모든 이미지 태그 찾기
    images = soup.find_all('img')
    
    for img in images:
        src = img.get('src') or img.get('data-src')
        if src:
            full_url = urljoin(base_url, src)
            # 작은 아이콘이나 로고 제외 (파일 크기 기준)
            if not any(x in full_url.lower() for x in ['icon', 'logo', 'btn', 'arrow']):
                image_urls.append({
                    'url': full_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
    
    return image_urls

def download_image(image_url, save_path):
    """이미지를 다운로드합니다."""
    try:
        response = session.get(image_url, timeout=10)
        response.raise_for_status()
        
        # 파일 크기가 너무 작으면 스킵 (아이콘일 가능성)
        if len(response.content) < 1024:  # 1KB 미만
            return False
            
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"   [ERROR] 이미지 다운로드 실패: {str(e)[:50]}")
        return False

# 메인 실행
results = {
    'total_checked': 0,
    'pages_found': 0,
    'images_found': 0,
    'images_downloaded': 0,
    'stations': []
}

# 테스트: 몇 개의 역만 먼저 시도
test_limit = 3
test_stations = list(stations_data.items())[:test_limit]

print(f"\n[테스트] 처음 {test_limit}개 역만 조회합니다.\n")

for station_name, station_info_list in test_stations:
    # 각 역의 첫 번째 호선만 조회
    station_info = station_info_list[0]
    results['total_checked'] += 1
    
    rail_code = station_info['railOprIsttCd']
    line_code = station_info['lnCd']
    station_code = station_info['stinCd']
    line_name = station_info.get('lnNm', line_code)
    
    print(f"\n[역] {station_name} ({line_name})")
    
    # 웹 페이지 가져오기
    html_content, page_url = get_station_facility_page(
        station_name, rail_code, line_code, station_code
    )
    
    if not html_content:
        print(f"   [FAIL] 페이지를 찾을 수 없습니다.")
        continue
    
    results['pages_found'] += 1
    
    # 이미지 추출
    images = extract_images_from_html(html_content, BASE_URL)
    
    if images:
        print(f"   [발견] {len(images)}개의 이미지")
        results['images_found'] += len(images)
        
        station_result = {
            'station_name': station_name,
            'line_name': line_name,
            'page_url': page_url,
            'images': []
        }
        
        # 이미지 다운로드
        for idx, img_info in enumerate(images):
            img_url = img_info['url']
            
            # 파일명 생성
            safe_station_name = station_name.replace('/', '_').replace('\\', '_')
            safe_line_name = line_name.replace('/', '_').replace('\\', '_')
            
            ext = os.path.splitext(img_url)[1][:5] or '.jpg'  # 확장자 길이 제한
            filename = f"{safe_station_name}_{safe_line_name}_{idx+1}{ext}"
            filepath = os.path.join(IMAGES_DIR, filename)
            
            print(f"   [다운] {filename}...", end=' ')
            
            if download_image(img_url, filepath):
                print("[OK]")
                results['images_downloaded'] += 1
                station_result['images'].append({
                    'filename': filename,
                    'url': img_url,
                    'alt': img_info['alt']
                })
            else:
                print("[SKIP]")
        
        results['stations'].append(station_result)
    else:
        print(f"   [없음] 이미지를 찾을 수 없습니다.")
    
    # 첫 번째 역의 HTML 저장
    if results['total_checked'] == 1:
        html_file = 'sample_page.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"   [저장] HTML을 '{html_file}'에 저장했습니다.")
    
    # 요청 간 딜레이
    time.sleep(1)

# 결과 저장
print("\n" + "="*60)
print("[결과] 크롤링 완료")
print("="*60)
print(f"조회한 역: {results['total_checked']}개")
print(f"페이지 발견: {results['pages_found']}개")
print(f"발견한 이미지: {results['images_found']}개")
print(f"다운로드한 이미지: {results['images_downloaded']}개")
print("="*60)

# 결과를 JSON으로 저장
result_file = 'crawling_results.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\n[완료] 결과가 '{result_file}'에 저장되었습니다.")
print(f"[완료] 이미지는 '{IMAGES_DIR}' 폴더에 저장되었습니다.")
print(f"[힌트] 'sample_page.html'을 열어서 웹사이트 구조를 확인하세요.")
