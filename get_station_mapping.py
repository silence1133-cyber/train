# -*- coding: utf-8 -*-
"""
KRIC 웹사이트에서 역 코드 매핑 정보를 가져오는 스크립트
API: https://hc.kric.go.kr/hc/visual/handicapped/selectLegendClickInfo.do
"""

import requests
import json
import sys
import time

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 설정
BASE_URL = 'https://hc.kric.go.kr'
LEGEND_API = '/hc/visual/handicapped/selectLegendClickInfo.do'

# 세션 생성
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://hc.kric.go.kr/hc/index.jsp'
})

# 지역 코드 (수도권 = 01)
area_code = '01'

# 결과 저장
all_mappings = {}

print("[시작] 역 코드 매핑 정보 수집 중...\n")

# paramLnCd 1~8까지 호출
for line_num in range(1, 9):
    line_cd = str(line_num)
    
    print(f"[API 호출] 지역={area_code}, 노선={line_cd}")
    
    try:
        url = f"{BASE_URL}{LEGEND_API}?paramAreCd={area_code}&paramLnCd={line_cd}"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'resultStinList' in data and data['resultStinList']:
            stations = data['resultStinList']
            print(f"   [OK] {len(stations)}개 역 정보 수신")
            
            # 매핑 저장
            for station in stations:
                rail_opr_istt_cd = station.get('railOprIsttCd')
                ln_cd = station.get('lnCd')
                stin_nm = station.get('stinNm')
                prpr_stin_cd = station.get('prprStinCd')
                
                if all([rail_opr_istt_cd, ln_cd, stin_nm, prpr_stin_cd]):
                    key = f"{rail_opr_istt_cd}_{ln_cd}_{stin_nm}"
                    
                    if key not in all_mappings:
                        all_mappings[key] = {
                            'railOprIsttCd': rail_opr_istt_cd,
                            'lnCd': ln_cd,
                            'stinNm': stin_nm,
                            'prprStinCd': prpr_stin_cd
                        }
            
            # 처음 3개 역 예시 출력
            if len(stations) > 0:
                print(f"   [예시] {stations[0].get('stinNm')} -> prprStinCd: {stations[0].get('prprStinCd')}")
        else:
            print(f"   [EMPTY] 데이터 없음")
            
    except Exception as e:
        print(f"   [ERROR] {str(e)[:80]}")
    
    # API 호출 간 딜레이
    time.sleep(0.5)

# 결과 저장
print("\n" + "="*60)
print(f"[완료] 총 {len(all_mappings)}개의 역 매핑 정보 수집")
print("="*60)

# JSON 파일로 저장
mapping_file = 'station_prpr_mapping.json'
with open(mapping_file, 'w', encoding='utf-8') as f:
    json.dump(all_mappings, f, ensure_ascii=False, indent=4)

print(f"\n[저장] '{mapping_file}' 파일에 저장되었습니다.")

# 몇 개 예시 출력
print("\n[예시] 매핑 정보:")
for i, (key, value) in enumerate(list(all_mappings.items())[:5], 1):
    print(f"{i}. {value['stinNm']} ({value['lnCd']}호선) -> prprStinCd: {value['prprStinCd']}")
