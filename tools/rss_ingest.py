
# lightweight Google News RSS 수집기
# - 입력: tools/keywords.yaml 의 queries 목록
# - 출력: data/collected.jsonl 에 (중복 제거 후) append
# - 중복 판별: link 또는 (title+published) 해시
# - 주의: 구글 뉴스 요청은 빈도 제한/약관을 반드시 준수하세요.
#
# 실행 예시:
#   cd tools
#   python -m venv .venv && source .venv/bin/activate
#   pip install -r requirements.txt
#   python rss_ingest.py --lang ko --region KR

import argparse, os, json, time, hashlib, pathlib
from urllib.parse import quote_plus
import requests, feedparser
from dateutil import parser as dtparser
from bs4 import BeautifulSoup
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)
COLLECTED = DATA / "collected.jsonl"
SEEN = DATA / "seen_hashes.txt"
KEYWORDS = ROOT / "tools" / "keywords.yaml"

def load_keywords():
    obj = yaml.safe_load(KEYWORDS.read_text(encoding="utf-8"))
    return [str(q) for q in obj.get("queries", []) if q]

def clean_html(html):
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)

def make_hash(link, title, published):
    base = (link or "") + "|" + (title or "") + "|" + (published or "")
    return hashlib.md5(base.encode("utf-8")).hexdigest()

def load_seen():
    s = set()
    if SEEN.exists():
        for line in SEEN.read_text(encoding="utf-8").splitlines():
            if line.strip():
                s.add(line.strip())
    return s

def save_seen(seen):
    SEEN.write_text("\n".join(sorted(seen)), encoding="utf-8")

def append_jsonl(records):
    with COLLECTED.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def fetch_google_news(query, lang="ko", region="KR"):
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl={lang}&gl={region}&ceid={region}:{lang}"
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (compatible; TrendBot/0.1)"})
    r.raise_for_status()
    return feedparser.parse(r.text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="ko")
    ap.add_argument("--region", default="KR")
    args = ap.parse_args()

    queries = load_keywords()
    seen = load_seen()
    new_records = []
    for q in queries:
        try:
            feed = fetch_google_news(q, lang=args.lang, region=args.region)
        except Exception as e:
            print("Fetch error:", e)
            continue
        for entry in feed.entries:
            link = entry.get("link")
            title = entry.get("title")
            summary = clean_html(entry.get("summary", ""))
            published = entry.get("published") or entry.get("updated") or ""
            try:
                pub_iso = dtparser.parse(published).isoformat()
            except Exception:
                pub_iso = None
            h = make_hash(link, title, published)
            if h in seen:
                continue
            rec = {
                "platform": "news",
                "brand": q,
                "text": f"{title} {summary}".strip(),
                "url": link,
                "published_at": pub_iso,
                "meta": {"source": "GoogleNewsRSS", "q": q}
            }
            new_records.append(rec)
            seen.add(h)
    if new_records:
        append_jsonl(new_records)
    save_seen(seen)
    print(f"Appended {len(new_records)} records to {COLLECTED}")

if __name__ == "__main__":
    main()
