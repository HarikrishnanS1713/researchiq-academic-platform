import ollama
import os

from dotenv import load_dotenv

from modules.rag_pipeline import (
    retrieve_relevant_context,
    format_context
)


# ---------------------------------------
# ENVIRONMENT CONFIGURATION
# ---------------------------------------

load_dotenv()

MODEL_NAME = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b"
)


# ---------------------------------------
# RESEARCH IDEA ANALYZER
# ---------------------------------------

def analyze_research_idea(research_idea):

    """
    Analyze a proposed research idea using RAG
    and an Ollama Large Language Model.
    """

    # Step 1: Validate research idea

    if not research_idea or not research_idea.strip():

        return {
            "analysis": "Please enter a valid research idea.",
            "sources": []
        }

    try:

        # Step 2: Retrieve relevant research sections

        retrieved_chunks = retrieve_relevant_context(
            research_idea,
            top_k=5
        )

        # Step 3: Check retrieved results

        if not retrieved_chunks:

            return {
                "analysis": (
                    "No relevant research papers were found. "
                    "Please upload and process research papers first."
                ),
                "sources": []
            }

        # Step 4: Format retrieved context

        context = format_context(retrieved_chunks)

        # Step 5: Prepare academic analysis prompt

        prompt = f"""

You are an academic research assistant specializing
in research paper analysis, semantic search,
and Retrieval-Augmented Generation (RAG).

Your task is to carefully analyze the proposed
research idea using the supplied research context.

========================================
PROPOSED RESEARCH IDEA
========================================

{research_idea}


========================================
RETRIEVED RESEARCH PAPER CONTEXT
========================================

{context}


========================================
ANALYSIS REQUIREMENTS
========================================

Provide a detailed research analysis using
the following five sections.

1. RELATED EXISTING RESEARCH

- Explain how the retrieved research relates
  to the proposed research idea.
- Identify relevant existing methods and findings.
- Mention the research paper filename and page number.
- If a paper is unrelated, clearly explain why.

2. RESEARCH GAPS

- Identify possible research gaps supported
  by the retrieved research evidence.
- Explain what existing studies do not address.
- Provide supporting paper filenames and page numbers.
- Do not invent research gaps.
- If the retrieved papers are unrelated or insufficient,
  clearly state that reliable research gaps cannot
  be identified from the available evidence.

3. POTENTIAL NOVEL CONTRIBUTIONS

- Suggest possible improvements or contributions.
- Explain how the proposed idea could extend
  the existing research.
- Distinguish your suggestions from proven findings.
- Do not claim that the idea is completely novel.
- Do not claim that no previous research exists
  without sufficient evidence.

4. SUGGESTIONS FOR IMPROVEMENT

- Suggest practical improvements to the research idea.
- Recommend suitable technologies and methodologies.
- Suggest possible experiments and evaluation metrics.
- Explain how the proposed system could be evaluated.

5. LIMITATIONS OF THIS ANALYSIS

- Explain limitations of the retrieved documents.
- Mention when the available evidence is insufficient.
- Explain that only uploaded research papers
  were considered.
- Recommend reviewing additional academic papers
  before making novelty conclusions.


========================================
IMPORTANT ACADEMIC RULES
========================================

1. Use only the provided research context
   for factual claims about existing studies.

2. Never invent research papers, authors,
   publication details, or research findings.

3. Mention source filenames and page numbers
   whenever supporting evidence is discussed.

4. Clearly distinguish existing research,
   evidence, assumptions, and suggestions.

5. Never guarantee that a research idea
   is completely novel.

6. Do not treat missing information in uploaded
   papers as proof of a gap in the entire
   academic literature.

7. If retrieved papers are unrelated to the
   proposed research idea, clearly state that
   the available evidence is insufficient.

8. Do not generate unsupported research gaps
   or unsupported novelty claims.

9. Recommend reviewing additional relevant
   academic literature before making conclusions.

10. Semantic similarity scores do not prove
    research duplication or originality.


========================================
FINAL INSTRUCTION
========================================

Generate a clear, structured, academically
responsible research analysis.

Be honest about the limitations of the available
research evidence.

Do not make unsupported claims.
"""

        # Step 6: Generate AI analysis using Ollama

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Step 7: Extract AI response

        analysis = response["message"]["content"]

        # Step 8: Return analysis and sources

        return {
            "analysis": analysis,
            "sources": retrieved_chunks
        }

    except Exception as e:

        return {
            "analysis": (
                f"Research analysis failed: {str(e)}"
            ),
            "sources": []
        }