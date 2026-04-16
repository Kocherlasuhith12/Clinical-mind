"""
RAG Engine: retrieves relevant medical knowledge from Pinecone
to ground diagnosis in evidence-based guidelines.
Sources: PubMed, NHM India, WHO clinical guidelines.

Uses BAAI/bge-small-en-v1.5 embeddings (1024 dim) — free, runs locally.
Matches Pinecone index dimension: 1024
"""
from llama_index.core import VectorStoreIndex, Settings as LlamaSettings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pinecone import Pinecone
from app.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)

# Free local embedding model — 1024 dimensions, matches Pinecone index
EMBED_MODEL = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")
LlamaSettings.embed_model = EMBED_MODEL


def get_pinecone_index():
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    pinecone_index = pc.Index(settings.PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    return VectorStoreIndex.from_vector_store(vector_store)


def retrieve_medical_context(query: str, top_k: int = 5) -> List[dict]:
    """
    Retrieve relevant medical guidelines for a given symptom query.
    Returns list of {text, source, score} dicts.
    """
    try:
        index = get_pinecone_index()
        retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        return [
            {
                "text": node.get_content(),
                "source": node.metadata.get("source", "Medical Guidelines"),
                "score": round(node.score, 3) if node.score else None,
            }
            for node in nodes
        ]
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        return []


def build_rag_enhanced_prompt(symptoms: str, context_docs: List[dict]) -> str:
    """Build a prompt that includes retrieved medical context."""
    if not context_docs:
        return symptoms

    context_text = "\n\n".join([
        f"[{doc['source']}]: {doc['text']}"
        for doc in context_docs[:3]
    ])

    return f"""Patient Symptoms:
{symptoms}

Relevant Medical Guidelines:
{context_text}

Based on the above symptoms and guidelines, provide your clinical assessment."""


def ingest_medical_documents(documents: List[dict]):
    """
    Ingest medical documents into Pinecone vector store.
    Each doc: {text, source, metadata}
    Run once during setup: python -m app.rag.ingest
    Uses free local HuggingFace embeddings — no OpenAI needed for ingestion.
    """
    from llama_index.core import Document

    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    pinecone_index = pc.Index(settings.PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    llama_docs = [
        Document(text=d["text"], metadata={"source": d["source"], **d.get("metadata", {})})
        for d in documents
    ]

    index = VectorStoreIndex.from_documents(llama_docs, vector_store=vector_store)
    logger.info(f"Ingested {len(llama_docs)} documents into Pinecone")
    return index
