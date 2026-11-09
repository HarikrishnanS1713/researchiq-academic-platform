from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    """
    Extract text from every page of a PDF research paper.
    """

    try:
        reader = PdfReader(pdf_path)

        source_file = getattr(
            pdf_path,
            "name",
            "uploaded_research_paper.pdf"
        )

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text()

            if text and text.strip():
                extracted_pages.append({
                    "page_number": page_number,
                    "source_file": source_file,
                    "text": text.strip()
                })

        if not extracted_pages:
            raise ValueError("No readable text found in the PDF.")

        return extracted_pages

    except Exception as e:
        raise Exception(f"PDF extraction failed: {e}")