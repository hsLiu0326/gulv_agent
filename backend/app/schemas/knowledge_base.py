from pydantic import BaseModel
from typing import Optional


class KnowledgeQuery(BaseModel):
    query: str
    n_results: int = 5


class KnowledgeResponse(BaseModel):
    content: str
    metadata: Optional[dict] = None
    distance: Optional[float] = None