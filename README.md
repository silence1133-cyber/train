# 지하철 수유실 정보 웹 페이지

지하철 역사별 수유실 현황을 조회할 수 있는 웹 애플리케이션입니다.

## 📋 프로젝트 구성

- `index.html` - 메인 웹 페이지 (수유실 데이터는 **api.info-zip.kr/seoulapi** 프록시 사용)
- `station_prpr_mapping_ok.json` - 역 목록 및 이미지 매핑
- `station_images/` - 역별 편의시설 안내도 이미지

## 🔐 API 키 보안 (프록시 방식)

- 브라우저에서는 **api.info-zip.kr** 서버의 `/seoulapi` 만 호출합니다.
- 서울 열린데이터 API 키는 **서버(api.info-zip.kr)** 에만 두고, 서버가 서울 API를 대신 호출한 뒤 결과만 반환합니다.
- F12 Network에서도 API 키가 노출되지 않습니다.

### api.info-zip.kr 서버의 `/seoulapi` 구현 요약

1. **요청**: `GET https://api.info-zip.kr/seoulapi` (브라우저에서 호출)
2. **서버 동작**: 서버가 내부에 보관한 API 키로 서울 API 호출  
   `http://openapi.seoul.go.kr:8088/{API_KEY}/json/getFcNrsrm/1/1000/`
3. **응답**: 서울 API와 **동일한 JSON 구조** 그대로 반환  
   - `response.header`, `response.body.items.item` (배열), `response.body.totalCount` 등

index.html은 위 형식의 JSON을 그대로 파싱하여 표시합니다.

## 🚀 사용 방법

### 1. 웹 페이지 실행

방법 1: 직접 파일 열기
- `index.html` 파일을 더블클릭하여 브라우저에서 엽니다.

방법 2: 로컬 서버 실행 (권장)
```bash
# Python을 사용하는 경우
cd f:\silent\train-info
python -m http.server 8000

# 브라우저에서 http://localhost:8000 접속
```

### 2. 역 검색 및 정보 조회

1. 검색창에 역 이름을 입력합니다 (예: "강남", "홍대입구")
2. 자동완성 목록에서 원하는 역을 선택하거나 엔터를 누릅니다
3. 수유실 정보가 있으면 상세 정보가 표시됩니다
4. 수유실이 없으면 "수유실 정보가 없습니다" 메시지가 표시됩니다

## 🔧 API 정보

### API 엔드포인트
```
https://openapi.kric.go.kr/openapi/convenientInfo/stationDairyRoom
```

### 요청 파라미터
- `serviceKey`: 발급받은 서비스 키 (필수)
- `format`: 응답 형식 (json)
- `railOprIsttCd`: 운영기관코드 (필수)
- `lnCd`: 노선코드 (필수)
- `stinCd`: 역코드 (필수)

### 출력 변수
- `stinNm`: 역명
- `dryrmFloorNm`: 수유실 층 위치
- `dryrmDrc`: 수유실 방향
- `dryrmRmk`: 수유실 비고
- `atchFleNm`: 첨부파일명
- `atchFleUrl`: 첨부파일 URL

## 📊 데이터 업데이트

새로운 역 정보 엑셀 파일이 있을 경우:

1. 엑셀 파일을 `.xlsx` 형식으로 저장
2. `import pandas as pd.py` 파일의 파일명을 수정
3. 스크립트 실행:
```bash
python "import pandas as pd.py"
```
4. `stations.json` 파일이 업데이트됩니다

## 🎨 주요 기능

- ✅ 역 이름 자동완성
- ✅ 실시간 API 호출
- ✅ 수유실 상세 정보 표시
- ✅ 반응형 디자인 (모바일 대응)
- ✅ 깔끔하고 현대적인 UI

## 🔍 문제 해결

### CORS 오류가 발생하는 경우
- 로컬 서버를 사용해서 실행하세요 (Python HTTP 서버 등)
- 브라우저 확장 프로그램으로 CORS를 해제하세요

### API 호출이 실패하는 경우
1. 서비스 키가 올바르게 설정되었는지 확인
2. 브라우저 개발자 도구(F12)의 Console 탭에서 오류 확인
3. Network 탭에서 API 요청/응답 확인

### 역을 찾을 수 없는 경우
- 정확한 역 이름을 입력했는지 확인
- 자동완성 기능을 활용하세요

## 📝 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.
API는 한국철도공사(KORAIL)에서 제공하는 공공데이터입니다.
