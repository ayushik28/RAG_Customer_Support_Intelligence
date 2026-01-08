
# Customer Support Intelligence System  
### Retrieval-Augmented Generation (RAG) with LangGraph Orchestration & Guardrails

---

## Project Overview

This project implements a **Customer Support Intelligence System** that answers user queries strictly using **internal support documentation** such as FAQs, Service Level Agreements (SLAs), Internal Policies, and Escalation Workflows.

The system is built using **Retrieval-Augmented Generation (RAG)** and orchestrated with **LangGraph** to ensure:
- No hallucinated answers
- Strict grounding in verified documents
- Deterministic multi-step reasoning
- Safety controls and audit logging

The solution is designed for **enterprise-grade customer support**, where accuracy, compliance, and traceability are critical.

---

## Key Objectives

- Retrieve only relevant internal documentation
- Prevent ungrounded or fabricated responses
- Enforce safety and PII redaction
- Provide transparent source attribution
- Maintain audit logs for every interaction

---

## System Architecture (High Level)
User Query
↓
Intent Detection (LangGraph)
↓
Semantic Retrieval (Chroma Vector DB)
↓
Grounding Validation
↓
Safety & PII Guardrails
↓
Response Synthesis
↓
Audit Logging


> **Important:**  
> The system never generates an answer unless relevant internal documents are retrieved and validated.

---

## Repository Structure

customer-support-intelligence-rag/
│
├── data/
│ └── raw/ # Source PDF documents
│
├── src/
│ ├── ingestion/ # Document ingestion & chunking
│ │ ├── pdf_loader.py
│ │ ├── chunking.py
│ │ └── build_vectorstore.py
│ │
│ ├── rag/ # LangGraph reasoning nodes
│ │ ├── state.py
│ │ ├── intent.py
│ │ ├── retrieval.py
│ │ ├── grounding.py
│ │ ├── safety.py
│ │ ├── response.py
│ │ └── audit.py
│ │
│ ├── ui/ # Gradio UI
│ │ └── gradio_app.py
│ │
│ ├── app.py # LangGraph pipeline entry point
│ └── config.py
│
├── notebooks/
│ └── final_run.ipynb # End-to-end execution notebook
│
├── vectorstore/ # Persisted Chroma vector database
│
├── reports/
│ ├── Technical_Report.pdf
│ └── Business_Presentation.pptx
│
├── requirements.txt
├── .gitignore
└── README.md


---

## Documents Used

The system ingests the following internal documents:

- **FAQs** – Customer-facing question/answer knowledge base  
- **Service Level Agreements (SLA)** – Uptime, response, and resolution commitments  
- **Internal Policy Handbook** – Compliance and conduct policies  
- **Escalation Workflows** – Issue escalation rules and timelines  

All documents are stored in `data/raw/` and are processed during ingestion.

---

## Core Components Explained

###  Document Ingestion & Vector Database (Task 1)
- PDFs are loaded and cleaned
- Documents are chunked based on structure:
  - FAQs → Q/A chunks
  - SLA / Policy / Escalation → Section-based chunks
- Chunks are embedded using `sentence-transformers`
- Stored in **Chroma vector database** with metadata for traceability

---

###  Semantic Retrieval (Task 2)
- User queries are embedded
- Top-k relevant chunks are retrieved from the vector database
- Retrieval is recall-oriented (filtering happens later)

---

###  LangGraph Reasoning Pipeline (Task 3)
LangGraph enforces a deterministic reasoning flow:
- Intent Detection
- Retrieval
- Grounding Validation
- Safety Checks
- Response Synthesis
- Audit Logging

Each step updates a shared `GraphState`.

---

###  Grounding & Safety Guardrails (Task 4)
- Answers are generated **only** from retrieved content
- If no grounded content is found, an explicit limitation message is returned
- PII (emails, phone numbers, etc.) is redacted before response generation
- Hallucinated responses are strictly disallowed

---

###  Session Management & Audit Logging (Task 5)
Every interaction is logged with:
- Session ID and timestamp
- User query and detected intent
- Grounding and safety flags
- Final answer
- Referenced document chunks

Logs are stored in `audit_logs.jsonl`.

---

###  Gradio-Based Chatbot Interface (Task 6)
- Simple, clean conversational UI
- Displays answers and sources
- Shows “No sources” for out-of-scope queries
- Integrated directly with the LangGraph pipeline

---

## How to Run the Project

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt

### Step 2: Add Documents
data/raw/

### Step 3: Build the Vector Database
python src/ingestion/build_vectorstore.py

### Step 4: Launch the Chatbot UI
python src/ui/gradio_app.py
 Example Queries

1.How do I reset my password? - Single Query
2.How do I track my order and contact the delivery driver? - Compound Query
3.how to apply for home loan? - Out Of Scope
