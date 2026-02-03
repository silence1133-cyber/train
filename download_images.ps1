# PowerShell 스크립트: station_prpr_mapping_ok.json 기반 이미지 일괄 다운로드
param(
    [string]$MappingPath = "station_prpr_mapping_ok.json",
    [string]$OutputDir = "F:\silent\train-info\station_images"
)

if (-not (Test-Path $MappingPath)) {
    Write-Error "매핑 파일을 찾을 수 없습니다: $MappingPath"
    exit 1
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$jsonText = Get-Content $MappingPath -Raw -Encoding UTF8
try {
    $json = $jsonText | ConvertFrom-Json
}
catch {
    Write-Error "JSON 파싱 실패: $($_.Exception.Message)"
    exit 1
}
$total = $json.PSObject.Properties.Count

$headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    "Referer"    = "https://hc.kric.go.kr/hc/index.jsp"
}

$baseUrl = "https://hc.kric.go.kr/hc/ext/images/visual/handicapped/cnv"
$i = 0
$success = 0
$fail = @()

foreach ($prop in $json.PSObject.Properties) {
    $info = $prop.Value
    $i++

    $rail = $info.railOprIsttCd
    $ln   = $info.lnCd
    $prpr = $info.prprStinCd
    $name = $info.stinNm

    $fileNameSafe = ($name -replace '[\\/:"*?<>|]', '_') + "_${rail}_${ln}.png"
    $outFile = Join-Path $OutputDir $fileNameSafe
    $url = "$baseUrl/$rail/${rail}_${ln}_${prpr}.png"

    Write-Host ("[{0}/{1}] {2} - 다운로드 시도..." -f $i, $total, $name)

    try {
        Invoke-WebRequest -Uri $url -OutFile $outFile -Headers $headers -TimeoutSec 20 -ErrorAction Stop -UseBasicParsing
        $success++
    }
    catch {
        Write-Warning "실패: $name ($url) - $($_.Exception.Message)"
        $fail += @{ name = $name; url = $url }
    }
}

Write-Host "==========================================="
Write-Host ("완료: 성공 {0}, 실패 {1}" -f $success, $fail.Count)
Write-Host ("저장 위치: {0}" -f $OutputDir)

if ($fail.Count -gt 0) {
    $failPath = Join-Path $OutputDir "download_failed.txt"
    $fail | ForEach-Object { "{0}`t{1}" -f $_.name, $_.url } | Set-Content -Path $failPath -Encoding UTF8
    Write-Host ("실패 목록이 {0} 에 저장되었습니다." -f $failPath)
}
