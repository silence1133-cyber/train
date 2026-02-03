# -*- coding: utf-8 -*-
import pandas as pd
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 엑셀 파일 읽기
df = pd.read_excel('운영기관_역사_코드정보_2025.07.04.xlsx')

print("[컬럼 목록]")
for i, col in enumerate(df.columns.tolist(), 1):
    print(f"{i}. {col}")

print(f"\n[행 수]: {len(df)}")

# 처음 3행 출력
print("\n[샘플 데이터]")
print(df.head(3).to_string())
