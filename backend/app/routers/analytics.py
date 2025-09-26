
from fastapi import APIRouter
from typing import Dict, List, Optional
import re
from collections import Counter, defaultdict
import os, json
from datetime import datetime

router = APIRouter()

def simple_keyword_extract(texts: List[str], topk:int=10) -> List[str]:
    tokens = []
    for t in texts:
        tokens += re.findall(r"[A-Za-z가-힣0-9]{2,}", t.lower())
    cnt = Counter(tokens)
    return [w for w,_ in cnt.most_common(topk)]


@router.get("/summary")
def summary():
    # Load records if available
    records = _load_records()
    texts = [str(r.get("text","")) for r in records if r.get("text")]
    brands = [str(r.get("brand","")) for r in records if r.get("brand")]
    platforms = [str(r.get("platform","")) for r in records if r.get("platform")]

    # Tokenize and count (very simple, with Korean/ASCII)
    tokens = []
    for t in texts:
        tokens += re.findall(r"[A-Za-z가-힣0-9]{2,}", t.lower())

    # Simple stop-words (expand later)
    stop = set(["그리고","하지만","그러나","에서","으로","하다","좋아요","있음","최고","무난","예쁨"])
    tokens = [w for w in tokens if w not in stop]

    from collections import Counter
    kw_counter = Counter(tokens)
    top_keywords = [{"term": w, "count": c} for w, c in kw_counter.most_common(12)]

    # Naive sentiment baseline
    pos_words = {"좋음","좋다","최고","만족","빠르","예쁨","훌륭","추천"}
    neg_words = {"별로","느리","불만","나쁨","최악","실망"}
    pos = sum(any(p in t for p in pos_words) for t in texts)
    neg = sum(any(n in t for n in neg_words) for t in texts)
    total = max(len(texts), 1)
    neu = max(total - pos - neg, 0)
    sentiment = {
        "positive": round(pos/total, 3),
        "neutral": round(neu/total, 3),
        "negative": round(neg/total, 3)
    }

    # Shares
    plat_counter = Counter(platforms)
    brand_counter = Counter(brands)
    platform_share = [{"platform": k, "count": v} for k, v in plat_counter.most_common()]
    brand_share = [{"brand": k, "count": v} for k, v in brand_counter.most_common()]

    topics = []  # placeholder for future BERTopic/LDA

    return {
        "keywords": top_keywords,
        "sentiment": sentiment,
        "topics": topics,
        "platform_share": platform_share,
        "brand_share": brand_share
    }

DATA_PATHS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "collected.jsonl")),

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
        {"platform":"instagram","brand":"A","text":"브랜드A 가성비 최고","published_at":"2025-09-01T10:00:00"},
        {"platform":"news","brand":"B","text":"브랜드B 신제품 출시","published_at":"2025-09-02T09:00:00"},
        {"platform":"blog","brand":"C","text":"브랜드C 디자인 호평","published_at":"2025-09-03T18:00:00"},
    ]

@router.get("/timeseries")
def timeseries(metric: str = "mentions", brand: Optional[str]=None, platform: Optional[str]=None, period: str="day"):
    records = _load_records()
    def _ok(r):
        if brand and str(r.get("brand","")).lower() != brand.lower():
            return False
        if platform and str(r.get("platform","")).lower() != platform.lower():
            return False
        return True
    agg = defaultdict(int)
    for r in records:
        if not _ok(r):
            continue
        ts = r.get("published_at") or r.get("publishedAt") or r.get("time")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z",""))
            key = dt.date().isoformat()
        except Exception:
            continue
        agg[key] += 1
    series = [{"date": k, "value": agg[k]} for k in sorted(agg.keys())]
    return {"metric": metric, "period": period, "series": series}
