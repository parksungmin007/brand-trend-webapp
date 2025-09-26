
from fastapi import APIRouter
from typing import Dict, List, Optional
import re
from collections import Counter, defaultdict
import os, json
from datetime import datetime

router = APIRouter()

# ==== Text normalization & lexicons ====
import unicodedata

KOREAN_STOPWORDS = {
    "그리고","그러나","하지만","또한","및","또","그래서","따라서","즉","그러므로",
    "이","그","저","것","수","등","점","및","및","등등","에서","으로","으로써","으로서",
    "하다","되다","있다","이다","합니다","했다","했다가","중","및","및","같은","같이",
    "대한","대해","관련","관련된","기반","위한","위해서","때문","때문에","보다","되는","까지",
    "만","좀","더","최고","무난","예쁨","좋아요","있음","로","를","은","는","이","가","에","의","와","과","도"
}

POSITIVE_LEX = {
    "좋다","좋음","만족","추천","최고","훌륭","빠르","친절","예쁨","가성비","재구매","정직","신뢰","감동","멋지",
    "편하","괜찮"," 만족","만족도","만점","최상","프리미엄","쾌적","깔끔","예쁘","고급","단단","튼튼","내구","셀링"
}

NEGATIVE_LEX = {
    "나쁘","별로","아쉬","느리","불만","실망","최악","허접","부정","고장","하자","지연","파손","불량","환불","반품",
    "짜증","불편","과대","허위","문제","버그","끊김","지저분","복잡","어렵","비싸","가격대비","가성비없","두껍","무겁"
}

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE
)

def norm_platform(p: str) -> str:
    if not p: return ""
    p = str(p).strip().lower()
    mapping = {
        "뉴스": "news", "news": "news", "article": "news",
        "블로그": "blog", "blog": "blog",
        "유튜브": "youtube", "youtube": "youtube", "yt": "youtube",
        "인스타그램": "instagram", "instagram": "instagram", "ig": "instagram",
        "트위터": "twitter", "x": "twitter"
    }
    return mapping.get(p, p)

def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        s = str(s or "")
    s = unicodedata.normalize("NFKC", s)
    s = EMOJI_RE.sub(" ", s)
    s = re.sub(r"[\r\n\t]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokenize_ko(s: str):
    s = normalize_text(s).lower()
    toks = re.findall(r"[A-Za-z가-힣0-9]{2,}", s)
    toks = [t for t in toks if t not in KOREAN_STOPWORDS]
    return toks

def simple_keyword_extract(texts: List[str], topk:int=10) -> List[str]:
    tokens = []
    for t in texts:
        tokens += re.findall(r"[A-Za-z가-힣0-9]{2,}", t.lower())
    cnt = Counter(tokens)
    return [w for w,_ in cnt.most_common(topk)]


@router.get("/summary")
def summary(brand: Optional[str]=None, platform: Optional[str]=None, start_date: Optional[str]=None, end_date: Optional[str]=None):
    # Load records if available
    records = _load_records()
        # filters
    from datetime import datetime
    def pass_filters(r):
        rb = str(r.get("brand",""))
        rp = str(r.get("platform",""))
        if brand and brand.lower() not in rb.lower():
            return False
        if platform and norm_platform(platform) != "" and norm_platform(rp) != norm_platform(platform):
            return False
        if start_date or end_date:
            ts = r.get("published_at") or r.get("publishedAt") or r.get("time")
            try:
                dt = datetime.fromisoformat(str(ts).replace("Z","")) if ts else None
            except Exception:
                dt = None
            if start_date:
                try:
                    if not dt or dt.date() < datetime.fromisoformat(start_date).date(): return False
                except Exception:
                    pass
            if end_date:
                try:
                    if not dt or dt.date() > datetime.fromisoformat(end_date).date(): return False
                except Exception:
                    pass
        return True
    records = [r for r in records if pass_filters(r)]

    texts = [normalize_text(r.get("text","")) for r in records if r.get("text")]
    brands = [str(r.get("brand","")) for r in records if r.get("brand")]
    platforms = [str(r.get("platform","")) for r in records if r.get("platform")]

    # Tokenize and count (very simple, with Korean/ASCII)
        tokens = []
    for t in texts:
        tokens += tokenize_ko(t)

    from collections import Counter
    kw_counter = Counter(tokens)
    top_keywords = [{"term": w, "count": c} for w, c in kw_counter.most_common(12)]

    # Sentiment baseline with expanded lexicon
    pos = sum(any(p in t for p in POSITIVE_LEX) for t in texts)
    neg = sum(any(n in t for n in NEGATIVE_LEX) for t in texts)
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
        rb = str(r.get("brand",""))
        rp = str(r.get("platform",""))
        if brand and brand.lower() not in rb.lower():
            return False
        if platform and norm_platform(platform) != "" and norm_platform(rp) != norm_platform(platform):
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
