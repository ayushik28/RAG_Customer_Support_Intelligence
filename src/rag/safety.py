import re
from langchain_core.documents import Document

def redact(text):
    return re.sub(r"\b\d{10}\b", "[REDACTED_PHONE]", text)

def safety_node(state):
    if not state.grounded:
        state.safe = False
        return state
    state.retrieved_docs = [
        Document(page_content=redact(d.page_content), metadata=d.metadata)
        for d in state.retrieved_docs
    ]
    return state
