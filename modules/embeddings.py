from sentence_transformers import SentenceTransformer


# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(text_chunks):
    """
    Convert text chunks into numerical vectors.
    """

    texts = [chunk["text"] for chunk in text_chunks]

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True
    )

    return embeddings