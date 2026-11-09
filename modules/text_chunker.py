def split_text_into_chunks(pages, chunk_size=1000, chunk_overlap=200):
    """
    Divide PDF text into smaller chunks while
    preserving source filename and page number.
    """

    chunks = []

    for page in pages:

        text = page["text"]
        page_number = page["page_number"]
        source_file = page.get(
            "source_file",
            "unknown.pdf"
        )

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            if chunk_text.strip():

                chunks.append({
                    "source_file": source_file,
                    "page_number": page_number,
                    "text": chunk_text.strip()
                })

            start += chunk_size - chunk_overlap

    return chunks