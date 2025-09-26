
# 브랜드 및 제품 데이터 수집 및 마케팅 트렌드 분석 웹앱

> 인스타그램/유튜브/블로그/뉴스 등 다중 플랫폼 데이터 수집 → NLP/ML 분석 → 대시보드 시각화까지 제공하는 엔드투엔드 웹앱입니다.

## 모듈 구조
```
backend/        # FastAPI 기반 API 서버 (수집/분석/조회 API)
crawler/        # Scrapy + Playwright(옵션) 크롤러 스켈레톤
analytics/      # NLP/ML 파이프라인 (감성/토픽/시계열 예측)
frontend/       # React(경량 템플릿) 대시보드
data/           # 예시 데이터 및 스키마
docs/           # 보고서/참고문헌 템플릿
docker-compose.yml
```

## 빠른 시작
### 1) Docker(권장)
```bash
docker compose up --build
```
- Backend: http://localhost:8000 (Swagger: `/docs`)
- Frontend: http://localhost:5173

### 2) 수동 실행
```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend
cd ../frontend
npm install
npm run dev
```

## 주요 API (초기 버전)
- `GET /health` : 상태 확인
- `POST /ingest` : 원시 텍스트/메타데이터 수집
- `GET /analytics/summary` : 키워드/감성/토픽 간단 요약 (더미)
- `GET /search?q=...` : 간단 키워드 검색 (더미)

## 라이선스
MIT
