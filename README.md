
# 브랜드 및 제품 데이터 수집 및 마케팅 트렌드 분석 웹앱

엔드투엔드: 데이터 수집 → NLP/ML → 대시보드

## 실행
```bash
docker compose up --build
```
- Backend: http://localhost:8000 (Swagger: /docs)
- Frontend: http://localhost:5173


## RSS 수집 (뉴스 → data/collected.jsonl)
```bash
cd tools
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python rss_ingest.py --lang ko --region KR
```

키워드 수정: `tools/keywords.yaml`

## 보고서 표 자동 생성 (CSV/Markdown)
```bash
cd tools
source .venv/bin/activate
python build_report_tables.py
# 결과: docs/tables/*.csv, *.md
```

> 컨테이너 환경에서는 repo 전체가 포함되지 않을 수 있으므로, 보고서 표 파일은 로컬에서 tools를 실행하세요.


## 대시보드 필터 사용
- 상단 **필터**(브랜드/플랫폼/시작일/종료일)를 설정 후 **적용**을 누르면
  - `/analytics/summary` 및 `/analytics/timeseries`가 해당 조건으로 호출됩니다.
- 백엔드 필터 파라미터:
  - `brand`, `platform`, `start_date`(YYYY-MM-DD), `end_date`(YYYY-MM-DD)

## 보고서용 PNG 생성
- `tools/build_report_tables.py` 실행 시 `docs/tables/png/` 아래에 **일별 언급량**, **플랫폼 분포**, **브랜드 분포**, **상위 키워드** PNG 이미지도 생성됩니다.


## 도구(TOOLS) 설치 오류 대처
- `pandas==2.2.2` 설치 실패 시: 로컬 Python이 3.9 미만일 가능성이 큽니다.
- 해결: `tools/requirements.txt`는 **pandas>=2.0,<2.1** 및 **matplotlib>=3.7,<3.9**로 조정되어 있습니다.
- 가상환경 재생성 예시(WSL/Ubuntu):
```bash
cd tools
deactivate 2>/dev/null || true
rm -rf .venv
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -r requirements.txt
```
