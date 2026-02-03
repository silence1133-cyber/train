// 브라우저 콘솔에서 실행할 스크립트
// https://hc.kric.go.kr/hc/index.jsp 페이지에서 F12 누르고 Console 탭에 붙여넣기

async function getAllStationMappings() {
    const baseUrl = 'https://hc.kric.go.kr/hc/visual/handicapped/selectLegendClickInfo.do';
    const allMappings = {};
    
    // paramLnCd 1~8까지 호출
    for (let lineNum = 1; lineNum <= 8; lineNum++) {
        const url = `${baseUrl}?paramAreCd=01&paramLnCd=${lineNum}`;
        
        try {
            console.log(`[API 호출] 노선=${lineNum}`);
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.resultStinList && data.resultStinList.length > 0) {
                console.log(`   [OK] ${data.resultStinList.length}개 역 정보 수신`);
                
                data.resultStinList.forEach(station => {
                    const key = `${station.railOprIsttCd}_${station.lnCd}_${station.stinNm}`;
                    allMappings[key] = {
                        railOprIsttCd: station.railOprIsttCd,
                        lnCd: station.lnCd,
                        stinNm: station.stinNm,
                        prprStinCd: station.prprStinCd
                    };
                });
            }
            
            // 딜레이
            await new Promise(resolve => setTimeout(resolve, 500));
            
        } catch (error) {
            console.error(`   [ERROR] 노선=${lineNum}`, error);
        }
    }
    
    console.log(`\n[완료] 총 ${Object.keys(allMappings).length}개의 역 매핑 정보 수집`);
    
    // 결과를 JSON 형태로 출력
    console.log('\n아래 내용을 복사해서 station_prpr_mapping.json 파일로 저장하세요:');
    console.log(JSON.stringify(allMappings, null, 4));
    
    // 다운로드 링크 생성
    const dataStr = JSON.stringify(allMappings, null, 4);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'station_prpr_mapping.json';
    link.click();
    
    console.log('\n[자동 다운로드] station_prpr_mapping.json 파일이 다운로드되었습니다!');
    
    return allMappings;
}

// 실행
getAllStationMappings();
