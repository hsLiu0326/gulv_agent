from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeQuery, KnowledgeResponse

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.post("/query", response_model=List[KnowledgeResponse])
def query_knowledge(
    query_data: KnowledgeQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    kb = KnowledgeBase()
    results = kb.search(query_data.query, query_data.n_results)
    return results