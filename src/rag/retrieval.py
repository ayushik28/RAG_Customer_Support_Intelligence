def retrieval_node(state, vectorstore):
    if state.intent == "OVERVIEW":
        return state
    state.retrieved_docs = vectorstore.similarity_search(state.query, k=8)
    return state
