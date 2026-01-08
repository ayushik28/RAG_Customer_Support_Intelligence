from dataclasses import dataclass, field
from typing import List, Optional
from langchain_core.documents import Document
import uuid
from datetime import datetime, timezone

@dataclass
class GraphState:
    query: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    intent: Optional[str] = None
    retrieved_docs: List[Document] = field(default_factory=list)
    grounded: bool = False
    safe: bool = True
    answer: Optional[str] = None
