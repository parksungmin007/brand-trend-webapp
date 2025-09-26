
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    project_name: str = "brand-trend-webapp"
    index_name: str = "posts"
    # 확장: DB URL, SNS API 키 등

settings = Settings()
