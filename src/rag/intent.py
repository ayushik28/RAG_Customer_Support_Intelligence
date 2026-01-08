def intent_detection_node(state):
    keywords = ["what documents", "what is available", "overview"]
    state.intent = "OVERVIEW" if any(k in state.query.lower() for k in keywords) else "FACT"
    return state
