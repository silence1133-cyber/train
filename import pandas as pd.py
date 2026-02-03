import pandas as pd
import json

# 1. 엑셀 파일 불러오기 (파일 경로는 본인 환경에 맞게 수정)
# 엑셀의 컬럼명이 '운영기관코드', '노선코드', '역코드', '역명' 이라고 가정합니다.
# 실제 엑셀 헤더를 확인하고 수정해주세요!
# .xls 파일을 .xlsx로 변환해서 저장한 후 아래 경로를 수정하세요
df = pd.read_excel("운영기관_역사_코드정보_2025.07.04.xlsx")

# 2. 데이터를 검색하기 좋은 구조로 변환
# 구조: { "강남": [{ "railOprIsttCd": "S1", "lnCd": "2", "stinCd": "222" }, ...], ... }
# 동일한 역명이지만 다른 호선인 경우를 위해 배열로 저장
station_db = {}

for index, row in df.iterrows():
    station_name = str(row['STIN_NM']).strip()  # 역명
    
    station_info = {
        "railOprIsttCd": str(row['RAIL_OPR_ISTT_CD']), # 운영기관코드
        "lnCd": str(row['LN_CD']),           # 노선코드
        "stinCd": str(row['STIN_CD']),       # 역코드
        "lnNm": str(row['LN_NM']) if 'LN_NM' in row else ""  # 노선명 (있는 경우)
    }
    
    # 역명이 이미 존재하면 배열에 추가, 없으면 새로운 배열 생성
    if station_name in station_db:
        station_db[station_name].append(station_info)
    else:
        station_db[station_name] = [station_info]

# 3. JSON 파일로 저장
with open("stations.json", "w", encoding="utf-8") as f:
    json.dump(station_db, f, ensure_ascii=False, indent=4)

print("stations.json 생성 완료!")