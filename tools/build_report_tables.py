
# 리포트 표 생성기
# - 입력: data/collected.jsonl (우선), fallback: data/sample.jsonl
# - 출력: docs/tables/*.csv, *.md
# 실행 예시:
#   cd tools
#   source .venv/bin/activate
#   python build_report_tables.py

import os, json, pathlib, re, collections
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PNG_DIR = DOCS / "png"
PNG_DIR.mkdir(parents=True, exist_ok=True)

def plot_mentions_line(mentions_df):
    if mentions_df.empty: 
        return
    plt.figure()
    plt.plot(mentions_df["date"], mentions_df["mentions"], marker="o")
    plt.title("일별 언급량")
    plt.xlabel("날짜")
    plt.ylabel("언급 수")
    plt.tight_layout()
    plt.savefig(PNG_DIR / "mentions_by_date.png")
    plt.close()

def plot_bar(df, xcol, ycol, title, fname):
    if df.empty:
        return
    plt.figure()
    plt.bar(df[xcol].astype(str), df[ycol])
    plt.title(title)
    plt.xlabel(xcol)
    plt.ylabel(ycol)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(PNG_DIR / fname)
    plt.close()


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs" / "tables"
DOCS.mkdir(parents=True, exist_ok=True)

def load_records():
    paths = [DATA/"collected.jsonl", DATA/"sample.jsonl"]
    for p in paths:
        if p.exists() and p.stat().st_size > 0:
            return pd.read_json(p, lines=True)
    return pd.DataFrame(columns=["platform","brand","text","url","published_at"])

def tokenize(text):
    toks = re.findall(r"[A-Za-z가-힣0-9]{2,}", str(text).lower())
    stop = set(["그리고","하지만","그러나","에서","으로","하다","있다","이다","합니다","있음","최고","무난","예쁨","가성비"])
    return [t for t in toks if t not in stop]

def to_markdown(df):
    header = "| " + " | ".join(df.columns) + " |\n"
    sep = "| " + " | ".join(["---"]*len(df.columns)) + " |\n"
    rows = "\n".join("| " + " | ".join(map(str, r)) + " |" for r in df.values.tolist())
    return header + sep + rows + "\n"

def main():
    df = load_records().copy()
    if "published_at" in df.columns:
        df["date"] = pd.to_datetime(df["published_at"], errors="coerce").dt.date

    mentions = df.dropna(subset=["date"]).groupby("date").size().reset_index(name="mentions")
    mentions.to_csv(DOCS/"mentions_by_date.csv", index=False)
    (DOCS/"mentions_by_date.md").write_text(to_markdown(mentions), encoding="utf-8")

    plat = df["platform"].fillna("unknown").value_counts().reset_index()
    plat.columns = ["platform","count"]
    plat.to_csv(DOCS/"platform_share.csv", index=False)
    (DOCS/"platform_share.md").write_text(to_markdown(plat), encoding="utf-8")

    brand = df["brand"].fillna("unknown").value_counts().reset_index()
    brand.columns = ["brand","count"]
    brand.to_csv(DOCS/"brand_share.csv", index=False)
    (DOCS/"brand_share.md").write_text(to_markdown(brand), encoding="utf-8")

    all_tokens = []
    for t in df["text"].dropna().tolist():
        all_tokens += tokenize(t)
    kc = collections.Counter(all_tokens)
    kw = pd.DataFrame(kc.most_common(20), columns=["term","count"])
    kw.to_csv(DOCS/"top_keywords.csv", index=False)
    (DOCS/"top_keywords.md").write_text(to_markdown(kw), encoding="utf-8")

    plot_mentions_line(mentions)
    plot_bar(plat, "platform", "count", "플랫폼 분포", "platform_share.png")
    plot_bar(brand, "brand", "count", "브랜드 분포", "brand_share.png")
    plot_bar(kw.head(20), "term", "count", "상위 키워드 Top20", "top_keywords.png")
    print("Tables & PNG charts written to", DOCS, "and", PNG_DIR)

if __name__ == "__main__":
    main()
