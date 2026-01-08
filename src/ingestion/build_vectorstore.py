import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunking import chunk_faq, chunk_numbered_sections
from src.config import VECTORSTORE_DIR, EMBEDDING_MODEL

pdfs = {
    "FAQ": "data/raw/FoodDeliveryApp_FAQs.pdf",
    "SLA": "data/raw/FoodDeliveryApp_SLAs.pdf",
    "POLICY": "data/raw/FoodDeliveryApp_Internal_Policies.pdf",
    "ESCALATION": "data/raw/FoodDeliveryApp_Escalation_Workflow.pdf"
}

embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
documents = []

for doc_type, path in pdfs.items():
    text = load_pdf(path)
    chunks = chunk_faq(text) if doc_type == "FAQ" else chunk_numbered_sections(text)

    for i, c in enumerate(chunks):
        metadata = {
            "document_type": doc_type,
            "chunk_id": f"{doc_type}_{i}",
            "source": os.path.basename(path)
        }
        content = c["content"] if doc_type == "FAQ" else c
        documents.append(Document(page_content=content, metadata=metadata))

Chroma.from_documents(
    documents=documents,
    embedding=embedding,
    persist_directory=VECTORSTORE_DIR
).persist()

print("Vectorstore built successfully.")
