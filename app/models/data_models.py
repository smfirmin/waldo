from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class LocationData(BaseModel):
    name: str
    latitude: float
    longitude: float
    events_summary: Optional[str] = None


class ArticleRequest(BaseModel):
    url: HttpUrl


class ArticleResponse(BaseModel):
    article_title: Optional[str] = None
    article_text: str
    locations: List[LocationData]
    processing_time: float
