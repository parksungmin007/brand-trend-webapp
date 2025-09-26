
from pydantic import BaseModel

class Settings(BaseModel):
    project_name: str = "brand-trend-webapp"
    index_name: str = "posts"

settings = Settings()
