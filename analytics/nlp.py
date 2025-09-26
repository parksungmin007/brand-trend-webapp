
"""NLP/ML 파이프라인 스켈레톤
- 감성 분석: (TODO) KoBERT/한국어 사전학습모델 연동
- 토픽 모델링: (TODO) BERTopic or LDA
- 시계열 예측: (TODO) Prophet/LSTM/Transformer
"""

from typing import List, Dict

def sentiment_scores(texts: List[str]) -> Dict[str, float]:
    # TODO: 실제 모델 추론 연결
    pos = 0.7; neu = 0.2; neg = 0.1
    return {"positive": pos, "neutral": neu, "negative": neg}

def extract_keywords(texts: List[str], topk:int=10) -> List[str]:
    # TODO: keyBERT/krwordrank 등 연동
    return ["가성비","품질","배송","디자인"]
