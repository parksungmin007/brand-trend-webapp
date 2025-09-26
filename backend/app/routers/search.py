
from fastapi import APIRouter, Query
from typing import List, Dict
import os, json

router = APIRouter()

DATA_PATHS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "sample.jsonl")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample.jsonl")),
]

def _load_records():
    for p in DATA_PATHS:
        if os.path.exists(p):
            recs = []
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        recs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return recs
    return [
        {"platform":"instagram","brand":"A","text":"브랜드A 가성비 최고","url":"http://example.com/1"},
        {"platform":"news","brand":"B","text":"브랜드B 신제품 출시","url":"http://example.com/2"},
        {"platform":"blog","brand":"C","text":"브랜드C 디자인 호평","url":"http://example.com/3"},
    ]

@router.get("/search")
def search(q: str) -> List[Dict]:
    ql = q.lower()
    db = _load_records()
    return [row for row in db if ql in str(row.get("text","")).lower() or ql in str(row.get("brand","")).lower()]
