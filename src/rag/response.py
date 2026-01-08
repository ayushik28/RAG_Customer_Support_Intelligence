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

    # 4. Identify primary document (deterministic)
    primary_doc = max(
        state.retrieved_docs,
        key=lambda d: len(d.page_content)
    )

    def format_section(text: str) -> str:
        # Keep section numbering internally
        return re.sub(r'^(\d+\.\d+)\s+', r'\1\n', text.strip())

    def clean_for_display(text: str) -> str:
        # Remove section numbers for user-facing output
        return re.sub(r'^\d+\.\d+\s*\n?', '', text).strip()

    primary_content = format_section(primary_doc.page_content)

    # 5. FAQ handling (atomic Q/A)
    faq_docs = [
        d for d in state.retrieved_docs
        if d.metadata.get("document_type") == "FAQ"
    ]

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
            final_answer = "\n\n".join(f"- {ans}" for ans in faq_answers)
            state.answer = (
                f"{final_answer}\n\n"
                f"Primary Source: {selected_faqs[0].metadata.get('source')} (FAQ)"
            )
            return state

    # 6. Policy / SLA / Escalation handling (compound-safe)
    is_compound = len(split_compound_query(state.query)) > 1

    query_terms = {
        t for t in re.findall(r"[a-zA-Z]+", state.query.lower())
        if len(t) > 4
    }

    sections = [primary_content]

    if is_compound:
        for doc in state.retrieved_docs[1:]:

            # HARD LIMIT: max 2 sections
            if len(sections) >= 2:
                break

            if doc.metadata.get("document_type") != primary_doc.metadata.get("document_type"):
                continue

            text = doc.page_content.strip()

            match = re.match(r'\d+\.\d+\s+([A-Za-z\s\-–]+)', text)
            section_title = match.group(1).lower() if match else ""

            if any(term in section_title for term in query_terms):
                sections.append(format_section(text))

    #DEDUPLICATE SECTIONS (fixes repeated answers from PDFs)
    unique_sections = []
    seen = set()

    for s in sections:
        normalized = re.sub(r"\s+", " ", s.strip().lower())
        if normalized not in seen:
            unique_sections.append(s)
            seen.add(normalized)

    sections = unique_sections

    final_content = "\n\n".join(clean_for_display(s) for s in sections)

    # Partial answer detection
    partial_answer = is_compound and len(sections) < 2

    if partial_answer:
        state.answer = (
            f"{final_content}\n\n"
            "Note: Only part of your question could be answered based on the available internal documents.\n\n"
            f"Primary Source: {primary_doc.metadata.get('source')} "
            f"({primary_doc.metadata.get('document_type')})"
        )
    else:
        state.answer = (
            f"{final_content}\n\n"
            f"Primary Source: {primary_doc.metadata.get('source')} "
            f"({primary_doc.metadata.get('document_type')})"
        )

    return state
