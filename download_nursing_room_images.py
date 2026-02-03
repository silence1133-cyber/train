import requests
import json
import os
import time
from urllib.parse import urlparse

# 설정
SERVICE_KEY = 'YOUR_SERVICE_KEY_HERE'  # 여기에 본인의 서비스 키를 입력하세요
API_BASE_URL = 'https://openapi.kric.go.kr/openapi/convenientInfo/stationDairyRoom'
IMAGES_DIR = 'nursing_room_images'  # 이미지 저장 폴더

# 이미지 저장 폴더 생성
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)
    print(f"📁 '{IMAGES_DIR}' 폴더를 생성했습니다.")

# stations.json 파일 로드
print("📖 역 정보를 불러오는 중...")
with open('stations.json', 'r', encoding='utf-8') as f:
    stations_data = json.load(f)

print(f"✅ 총 {len(stations_data)}개의 역 정보를 로드했습니다.\n")

# 결과 저장용
results = {
    'total_stations': 0,
    'stations_with_nursing_room': 0,
    'images_downloaded': 0,
    'failed': [],
    'nursing_rooms': []
}

# 각 역에 대해 API 호출
for station_name, station_info_list in stations_data.items():
    for station_info in station_info_list:
        results['total_stations'] += 1
        
        # API URL 구성
        url = f"{API_BASE_URL}?serviceKey={SERVICE_KEY}&format=json"
        url += f"&railOprIsttCd={station_info['railOprIsttCd']}"
        url += f"&lnCd={station_info['lnCd']}"
        url += f"&stinCd={station_info['stinCd']}"
        
        line_name = station_info.get('lnNm', station_info['lnCd'])
        print(f"🔍 조회 중: {station_name} ({line_name})... ", end='')
        
        try:
            # API 호출
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 수유실 정보가 있는지 확인
            if data and 'body' in data and isinstance(data['body'], list) and len(data['body']) > 0:
                results['stations_with_nursing_room'] += 1
                print(f"✅ 수유실 발견!")
                
                # 각 수유실 정보 처리
                for idx, room in enumerate(data['body']):
                    room_info = {
                        'station_name': station_name,
                        'line_name': line_name,
                        'railOprIsttCd': station_info['railOprIsttCd'],
                        'lnCd': station_info['lnCd'],
                        'stinCd': station_info['stinCd'],
                        'room_data': room
                    }
                    results['nursing_rooms'].append(room_info)
                    
                    # 이미지 URL이 있으면 다운로드
                    if 'atchFleUrl' in room and room['atchFleUrl']:
                        image_url = room['atchFleUrl']
                        
                        # 파일명 생성 (역명_노선명_인덱스.jpg)
                        safe_station_name = station_name.replace('/', '_').replace('\\', '_')
                        safe_line_name = line_name.replace('/', '_').replace('\\', '_')
                        
                        # 원본 파일 확장자 추출
                        parsed_url = urlparse(image_url)
                        file_ext = os.path.splitext(parsed_url.path)[1] or '.jpg'
                        
                        filename = f"{safe_station_name}_{safe_line_name}_{idx+1}{file_ext}"
                        filepath = os.path.join(IMAGES_DIR, filename)
                        
                        print(f"   📥 이미지 다운로드 중: {filename}... ", end='')
                        
                        try:
                            img_response = requests.get(image_url, timeout=10)
                            img_response.raise_for_status()
                            
                            with open(filepath, 'wb') as img_file:
                                img_file.write(img_response.content)
                            
                            results['images_downloaded'] += 1
                            room_info['image_path'] = filepath
                            print("✅ 완료")
                            
                        except Exception as img_error:
                            print(f"❌ 실패: {img_error}")
                            results['failed'].append({
                                'station': station_name,
                                'line': line_name,
                                'error': str(img_error),
                                'url': image_url
                            })
                    else:
                        print(f"   ℹ️ 이미지 URL이 없습니다.")
            else:
                print("ℹ️ 수유실 없음")
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            results['failed'].append({
                'station': station_name,
                'line': line_name,
                'error': str(e),
                'url': url
            })
        
        # API 호출 간 딜레이 (서버 부하 방지)
        time.sleep(0.5)

# 결과 요약
print("\n" + "="*60)
print("📊 다운로드 결과 요약")
print("="*60)
print(f"총 조회한 역(노선): {results['total_stations']}개")
print(f"수유실이 있는 역: {results['stations_with_nursing_room']}개")
print(f"다운로드한 이미지: {results['images_downloaded']}개")
print(f"실패한 요청: {len(results['failed'])}개")
print("="*60)

# 결과를 JSON 파일로 저장
result_file = 'nursing_room_results.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\n✅ 상세 결과가 '{result_file}' 파일에 저장되었습니다.")
print(f"✅ 이미지는 '{IMAGES_DIR}' 폴더에 저장되었습니다.")

# 실패한 요청이 있으면 표시
if results['failed']:
    print("\n⚠️ 실패한 요청:")
    for fail in results['failed'][:10]:  # 최대 10개만 표시
        print(f"   - {fail['station']} ({fail['line']}): {fail['error']}")
    if len(results['failed']) > 10:
        print(f"   ... 외 {len(results['failed']) - 10}개")
