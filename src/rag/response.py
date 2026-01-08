def response_node(state: GraphState) -> GraphState:
    # 1. Handle overview intent (system-generated)
    if state.intent == "OVERVIEW":
        state.answer = (
            "[System Overview]\n"
            "The following internal documents are available:\n"
            "- FAQs\n"
            "- Service Level Agreements (SLA)\n"
            "- Internal Policies\n"
            "- Escalation Workflows\n\n"
            "Please ask a specific question about any of these documents."
        )
        return state
 
    # 2. Enforce grounding & safety
    if not state.grounded or not state.safe:
        state.answer = "I could not find relevant information in the internal documents."
        return state
 
    # 3. Enforce retrieval
    if not state.retrieved_docs:
        state.answer = "I could not find relevant information in the internal documents."
        return state
 
    # --------------------------------------------------
    # FAQ DETECTION 
    # --------------------------------------------------
    faq_docs = [
        d for d in state.retrieved_docs
        if d.metadata.get("document_type") == "FAQ"
    ]
 
    # --------------------------------------------------
    # COMPOUND QUERY LIMITATION (NON-FAQ ONLY)
    # --------------------------------------------------
    if not faq_docs and len(split_compound_query(state.query)) > 1:
        state.answer = (
            "Your question contains multiple parts. "
            "To avoid partial or incorrect answers for policy documents, "
            "please ask each question separately."
        )
        return state
 
    # 4. Identify PRIMARY document by QUERY RELEVANCE
    query_terms = {
        t for t in re.findall(r"[a-zA-Z]+", state.query.lower())
        if len(t) > 4
    }
 
    def relevance_score(doc):
        return sum(1 for t in query_terms if t in doc.page_content.lower())
 
    primary_doc = max(state.retrieved_docs, key=relevance_score)
 
    def format_section(text: str) -> str:
        return re.sub(r'^(\d+\.\d+)\s+', r'\1\n', text.strip())
 
    def clean_for_display(text: str) -> str:
        return re.sub(r'^\d+\.\d+\s*\n?', '', text).strip()
 
    primary_content = format_section(primary_doc.page_content)
 
    # 5. FAQ handling (compound-safe, unchanged)
    if faq_docs:
        selected_faqs, top_score = select_relevant_faqs(
            state.query,
            faq_docs,
            embedding_model
        )
 
        if top_score < 0.45:
            state.answer = "I could not find relevant information in the internal documents."
            return state
 
        faq_answers = [
            doc.page_content.split("A:", 1)[1].strip()
            for doc in selected_faqs
            if "A:" in doc.page_content
        ]
 
        if faq_answers:
            state.answer = (
                "\n\n".join(f"- {a}" for a in faq_answers) + "\n\n"
                f"Primary Source: {selected_faqs[0].metadata.get('source')} (FAQ)"
            )
            return state
 
    # 6. Single-question Policy / SLA / Escalation
    state.answer = (
        f"{clean_for_display(primary_content)}\n\n"
        f"Primary Source: {primary_doc.metadata.get('source')} "
        f"({primary_doc.metadata.get('document_type')})"
    )
 
    return state
