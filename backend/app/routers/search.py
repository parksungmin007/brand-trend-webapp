
from fastapi import APIRouter, Query
from typing import List, Dict

router = APIRouter()

MOCK_DB = [
    {"platform":"instagram","brand":"A","text":"브랜드A 가성비 최고","url":"http://example.com/1"},
    {"platform":"news","brand":"B","text":"브랜드B 신제품 출시","url":"http://example.com/2"},
    {"platform":"blog","brand":"C","text":"브랜드C 디자인 호평","url":"http://example.com/3"},
]

@router.get("/search")
def search(q: str = Query(..., description="검색 키워드")) -> List[Dict]:
    ql = q.lower()
    return [row for row in MOCK_DB if ql in row["text"].lower() or ql in row["brand"].lower()]
