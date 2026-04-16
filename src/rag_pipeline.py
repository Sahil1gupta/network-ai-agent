# src/rag_pipeline.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from llm_client import get_embeddings

load_dotenv()

RUNBOOKS_DIR = "data/runbooks"
CHROMA_DIR   = "data/chroma_db"


def build_vector_db():
    """
    Runbook .txt files padhke ChromaDB mein embed karke save karo.
    Ye sirf ek baar run karna hai.
    """

    # Step 1: Saare .txt files load karo
    loader    = DirectoryLoader(RUNBOOKS_DIR, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} runbook files")

    # Step 2: Bade documents ko chhote chunks mein todo
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks   = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    # Step 3: OpenAI embedding model
    embedding_model = get_embeddings()

    # Step 4: Chunks ko embed karke ChromaDB mein save karo
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )
    print(f"Vector DB saved → {CHROMA_DIR}")
    return vectordb


def load_vector_db():
    """Pehle se bani DB load karo."""
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings()
    )


def retrieve_context(query: str, k: int = 2) -> str:
    """
    Query ke basis pe most relevant runbook chunks return karo.

    query = "BGP session down on router"
    k     = kitne top results chahiye
    """
    vectordb = load_vector_db()
    results  = vectordb.similarity_search(query, k=k)

    # Saare chunks ko ek string mein join karo
    context  = "\n\n---\n\n".join([doc.page_content for doc in results])
    return context


if __name__ == "__main__":
    if not os.path.exists(CHROMA_DIR):
        build_vector_db()
    else:
        print("Vector DB already exists — loading...")

    # Test retrieval
    query   = "BGP session dropped with peer unreachable"
    context = retrieve_context(query)
    print(f"\n=== Retrieved Context ===\n{context[:400]}")