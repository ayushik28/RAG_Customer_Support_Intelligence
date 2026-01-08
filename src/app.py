from langgraph.graph import StateGraph
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config import VECTORSTORE_DIR, EMBEDDING_MODEL
from src.rag.state import GraphState
from src.rag.intent import intent_detection_node
from src.rag.retrieval import retrieval_node
from src.rag.grounding import grounding_node
from src.rag.safety import safety_node
from src.rag.response import response_node
from src.rag.audit import audit_node

embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(
    persist_directory=VECTORSTORE_DIR,
    embedding_function=embedding
)

graph = StateGraph(GraphState)

graph.add_node("intent", intent_detection_node)
graph.add_node("retrieval", lambda s: retrieval_node(s, vectorstore))
graph.add_node("grounding", grounding_node)
graph.add_node("safety", safety_node)
graph.add_node("response", response_node)
graph.add_node("audit", audit_node)

graph.set_entry_point("intent")
graph.add_edge("intent", "retrieval")
graph.add_edge("retrieval", "grounding")
graph.add_edge("grounding", "safety")
graph.add_edge("safety", "response")
graph.add_edge("response", "audit")

app = graph.compile()
