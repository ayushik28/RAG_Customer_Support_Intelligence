import re

def grounding_node(state):
    if not state.retrieved_docs:
        return state
    terms = set(re.findall(r"[a-zA-Z]+", state.query.lower()))
    grounded = [
        d for d in state.retrieved_docs
        if terms & set(d.page_content.lower().split())
    ]
    state.retrieved_docs = grounded
    state.grounded = bool(grounded)
    return state
