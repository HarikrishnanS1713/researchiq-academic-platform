import chromadb
from pathlib import Path
import uuid


# Create persistent ChromaDB storage
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_DB_PATH = PROJECT_ROOT / "vector_db"

client = chromadb.PersistentClient(
    path=str(VECTOR_DB_PATH)
)

collection = client.get_or_create_collection(
    name="research_papers"
)


def store_document_chunks(chunks, embeddings):
    """
    Store research chunks with source information.
    """

    ids = [str(uuid.uuid4()) for _ in chunks]

    documents = [chunk["text"] for chunk in chunks]

    metadatas = [
        {
            "page_number": chunk["page_number"],
            "source_file": chunk.get(
                "source_file",
                "unknown.pdf"
            )
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    return ids


def search_similar_chunks(query_embedding, top_k=5):

    if collection.count() == 0:
        return {
            "documents": [[]],
            "metadatas": [[]]
        }

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=min(top_k, collection.count())
    )

    return results