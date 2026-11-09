from modules.embeddings import embedding_model
from modules.vector_store import search_similar_chunks


def retrieve_relevant_context(question, top_k=5):
    """
    Retrieve relevant research sections with source details.
    """

    query_embedding = embedding_model.encode(
        question,
        convert_to_numpy=True
    )

    results = search_similar_chunks(
        query_embedding,
        top_k=top_k
    )

    retrieved_context = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):

        retrieved_context.append({
            "text": document,
            "source_file": metadata.get(
                "source_file", "Unknown"
            ),
            "page_number": metadata.get(
                "page_number", "Unknown"
            ),
            "distance": float(distance)
        })

    return retrieved_context


def format_context(retrieved_chunks):
    """
    Format retrieved sections for the LLM.
    """

    context = ""

    for index, chunk in enumerate(
        retrieved_chunks, start=1
    ):

        context += f"""
Research Source {index}
Paper: {chunk['source_file']}
Page: {chunk['page_number']}
Content:
{chunk['text']}

-------------------------
"""

    return context