
from fastapi import APIRouter, Query
from typing import Dict, List
import re
from collections import Counter

router = APIRouter()

def simple_keyword_extract(texts: List[str], topk:int=10) -> List[str]:
    tokens = []
    for t in texts:
        tokens += re.findall(r"[A-Za-z가-힣0-9]{2,}", t.lower())
    cnt = Counter(tokens)
    return [w for w,_ in cnt.most_common(topk)]

@router.get("/summary")
def summary():
    # TODO: 실제 NLP/감성/토픽/예측 연결
    dummy_texts = [
        "브랜드A 가성비 좋아요", "브랜드A 품질 최고", "브랜드B 디자인 예쁨", "브랜드A 내구성 좋음",
        "브랜드B 배송 빨라요", "브랜드C 가성비 무난", "브랜드B 재구매 의사 있음"
    ]
    keywords = simple_keyword_extract(dummy_texts, topk=8)
    sentiment = {"positive": 0.71, "neutral": 0.22, "negative": 0.07}
    topics = [{"topic": "가성비/품질", "score": 0.62}, {"topic": "배송/서비스", "score": 0.38}]
    return {"keywords": keywords, "sentiment": sentiment, "topics": topics}
