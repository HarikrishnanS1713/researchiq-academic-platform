import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime, timezone

from bson import ObjectId
from database import (
    save_paper, save_research_idea, save_analysis,
    get_uploaded_papers, get_analysis_history, get_database_statistics
)

from modules.pdf_processor import extract_text_from_pdf
from modules.text_chunker import split_text_into_chunks
from modules.embeddings import generate_embeddings
from modules.vector_store import store_document_chunks, collection
from modules.novelty_analyzer import analyze_research_idea


# =====================================================
# 1. CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ResearchIQ | Intelligence Platform",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. SESSION STATE
# =====================================================

defaults = {
    "processed_papers": [],
    "analysis_history": [],
    "last_analysis": None,
    "total_chunks": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================================
# 3. PREMIUM DARK UI
# =====================================================

st.markdown("""
<style>

/* MAIN BACKGROUND */

.stApp {
    background: #101418 !important;
    color: #E8EEF2 !important;
}

[data-testid="stAppViewContainer"] {
    background: #101418 !important;
}

[data-testid="stHeader"] {
    background: #101418 !important;
}

/* CONTENT WIDTH */

.block-container {
    max-width: 1450px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #090D12 !important;
    border-right: 1px solid #26343D;
}

section[data-testid="stSidebar"] * {
    color: #DCE7EC !important;
}

/* HEADINGS */

h1, h2, h3, h4 {
    color: #F1F6F8 !important;
    font-weight: 700 !important;
}

/* TEXT */

p {
    color: #AAB8C1;
}

/* BRAND */

.brand-title {
    color: #F1F6F8;
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1.5px;
}

.brand-subtitle {
    color: #8FA2AD;
    font-size: 15px;
    margin-top: 5px;
}

.section-label {
    color: #00D6B2;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}

/* DIVIDER */

hr {
    border: none;
    border-top: 1px solid #26343D;
    margin-top: 25px;
    margin-bottom: 25px;
}

/* BUTTONS */

.stButton > button {
    background: #00BFA5 !important;
    color: #071411 !important;
    border: 1px solid #00D6B2 !important;
    border-radius: 8px !important;
    min-height: 44px;
    font-weight: 700;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #00D6B2 !important;
    border-color: #35BDF2 !important;
    color: #071411 !important;
}

/* DOWNLOAD BUTTON */

.stDownloadButton > button {
    background: #17252D !important;
    color: #00D6B2 !important;
    border: 1px solid #00BFA5 !important;
    border-radius: 8px !important;
    min-height: 44px;
}

/* METRICS */

[data-testid="stMetric"] {
    background: #1B242B !important;
    border: 1px solid #2B3A43 !important;
    border-radius: 12px !important;
    padding: 22px !important;
}

[data-testid="stMetricLabel"] {
    color: #91A5B0 !important;
}

[data-testid="stMetricValue"] {
    color: #00D6B2 !important;
}

/* FEATURE CARDS */

.feature-card {
    background: #1B242B;
    border: 1px solid #2B3A43;
    border-radius: 12px;
    padding: 25px;
    min-height: 170px;
    transition: 0.2s ease;
}

.feature-card:hover {
    border-color: #00D6B2;
    transform: translateY(-3px);
}

.feature-title {
    color: #F1F6F8;
    font-size: 19px;
    font-weight: 700;
    margin-top: 12px;
}

.feature-description {
    color: #91A5B0;
    font-size: 14px;
    margin-top: 8px;
}

/* INPUTS */

.stTextArea textarea,
.stTextInput input {
    background: #1B242B !important;
    color: #F1F6F8 !important;
    border: 1px solid #354650 !important;
    border-radius: 8px !important;
}

.stTextArea textarea:focus {
    border: 1px solid #00D6B2 !important;
}

/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background: #1B242B !important;
    border: 1px dashed #00A991 !important;
    border-radius: 10px !important;
    padding: 15px;
}

/* EXPANDERS */

[data-testid="stExpander"] {
    background: #1B242B !important;
    border: 1px solid #354650 !important;
    border-radius: 9px !important;
}

/* DATAFRAMES */

[data-testid="stDataFrame"] {
    border: 1px solid #354650;
    border-radius: 9px;
}

/* RADIO NAVIGATION */

section[data-testid="stSidebar"] [role="radiogroup"] label {
    background: transparent;
    border-radius: 7px;
    padding: 8px;
}

/* STATUS */

.status-badge {
    display: inline-block;
    background: #123B32;
    color: #00D6B2;
    padding: 7px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}

/* FOOTER */

.footer-text {
    text-align: center;
    color: #71818B;
    font-size: 12px;
    padding: 25px;
}

/* HIDE DEFAULT ELEMENTS */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 4. HELPER FUNCTIONS
# =====================================================

def paper_count():
    try:
        return get_database_statistics()["total_papers"]
    except Exception:
        return len({item["name"] for item in st.session_state.processed_papers})


def chunk_count():
    try:
        return collection.count()
    except Exception:
        return st.session_state.total_chunks


def create_report(idea, result, generated_date):

    report = f"""
RESEARCHIQ
ACADEMIC RESEARCH INTELLIGENCE REPORT

Generated: {generated_date}

==================================================

PROPOSED RESEARCH IDEA

{idea}

==================================================

AI RESEARCH ANALYSIS

{result.get("analysis", "No analysis available.")}

==================================================

RETRIEVED RESEARCH SOURCES
"""

    for index, source in enumerate(
        result.get("sources", []), 1
    ):

        report += f"""

SOURCE {index}

Document: {source.get("source_file", "Unknown")}

Page: {source.get("page_number", "Unknown")}

Content:

{source.get("text", "")}

--------------------------------------------------
"""

    report += """

DISCLAIMER:

This AI-generated analysis supports academic research.
It does not guarantee originality or prove that a research
idea is completely novel.

Developed using Python, Streamlit, RAG, ChromaDB,
Sentence Transformers and Ollama.
"""

    return report


# =====================================================
# 5. SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown(
        "<div style='font-size:28px;font-weight:800;'>"
        "RESEARCH<span style='color:#00D6B2;'>IQ</span>"
        "</div>",
        unsafe_allow_html=True
    )

    st.caption("ACADEMIC INTELLIGENCE PLATFORM")

    st.divider()

    st.markdown("### WORKSPACE")

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Research Library",
            "AI Research Assistant",
            "Research Analytics",
            "Analysis History"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### SYSTEM INFORMATION")

    st.caption("Python")
    st.caption("Streamlit")
    st.caption("Ollama / Qwen 2.5")
    st.caption("ChromaDB")
    st.caption("Sentence Transformers")

    st.divider()

    st.markdown(
        "<span class='status-badge'>● SYSTEM ONLINE</span>",
        unsafe_allow_html=True
    )

    st.caption("ResearchIQ · Version 6.0")


# =====================================================
# 6. HEADER
# =====================================================

st.markdown(
    "<div class='section-label'>RESEARCH INTELLIGENCE PLATFORM</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='brand-title'>ResearchIQ</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='brand-subtitle'>"
    "Discover knowledge. Explore research. Identify possibilities."
    "</div>",
    unsafe_allow_html=True
)

st.divider()


# =====================================================
# 7. OVERVIEW
# =====================================================

if page == "Overview":

    st.markdown("## Overview")

    st.caption("Your academic research workspace at a glance.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Research Papers", paper_count())

    with c2:
        st.metric("Indexed Sections", chunk_count())

    with c3:
        try:
            total_analyses = get_database_statistics()["total_analyses"]
        except Exception:
            total_analyses = len(st.session_state.analysis_history)
        st.metric("Analyses Generated", total_analyses)

    st.divider()

    st.markdown("## Workspace")

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("""
        <div class="feature-card">
            <div style="color:#00D6B2;font-size:26px;">01</div>
            <div class="feature-title">Research Library</div>
            <div class="feature-description">
                Upload, process and organize academic
                PDF research documents.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class="feature-card">
            <div style="color:#00D6B2;font-size:26px;">02</div>
            <div class="feature-title">AI Research Assistant</div>
            <div class="feature-description">
                Explore research ideas using RAG,
                semantic retrieval and LLM analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    c3, c4 = st.columns(2)

    with c3:

        st.markdown("""
        <div class="feature-card">
            <div style="color:#00D6B2;font-size:26px;">03</div>
            <div class="feature-title">Research Analytics</div>
            <div class="feature-description">
                Examine retrieved sections and
                document-processing statistics.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c4:

        st.markdown("""
        <div class="feature-card">
            <div style="color:#00D6B2;font-size:26px;">04</div>
            <div class="feature-title">Research Reports</div>
            <div class="feature-description">
                Review findings and export
                research analysis reports.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("## Research Workflow")

    steps = [
        ("01", "Upload", "Import academic papers."),
        ("02", "Process", "Extract text and create embeddings."),
        ("03", "Retrieve", "Find relevant research sections."),
        ("04", "Analyze", "Generate evidence-based insights."),
        ("05", "Export", "Download your research report.")
    ]

    for number, title, description in steps:

        left, right = st.columns([1, 8])

        with left:
            st.markdown(
                f"<h3 style='color:#00D6B2;'>{number}</h3>",
                unsafe_allow_html=True
            )

        with right:
            st.markdown(f"**{title}**")
            st.caption(description)


# =====================================================
# 8. RESEARCH LIBRARY
# =====================================================

elif page == "Research Library":

    st.markdown("## Research Library")

    st.caption(
        "Import and process academic PDF documents."
    )

    uploaded_files = st.file_uploader(
        "Upload PDF research papers",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:

        st.markdown("### Selected Documents")

        rows = []

        for file in uploaded_files:

            rows.append({
                "Document": file.name,
                "Size": f"{file.size / 1024:.1f} KB",
                "Format": "PDF"
            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

    if st.button(
        "PROCESS DOCUMENTS",
        use_container_width=True
    ):

        if not uploaded_files:

            st.warning("Upload at least one PDF first.")

        else:

            progress = st.progress(0)

            successful = 0
            total_chunks = 0

            for index, file in enumerate(uploaded_files):

                try:

                    if file.size == 0:
                        st.warning(f"{file.name} is empty.")
                        continue

                    if file.size > 20 * 1024 * 1024:
                        st.warning(f"{file.name} exceeds 20 MB.")
                        continue

                    with st.spinner(
                        f"Processing {file.name}..."
                    ):

                        file.seek(0)

                        pages = extract_text_from_pdf(file)

                        chunks = split_text_into_chunks(pages)

                        if not chunks:
                            st.warning(
                                f"No readable content in {file.name}."
                            )
                            continue

                        embeddings = generate_embeddings(chunks)

                        store_document_chunks(
                            chunks,
                            embeddings
                        )

                        # Save paper metadata permanently in MongoDB.
                        save_paper(
                            filename=file.name,
                            page_count=len(pages),
                            chunk_count=len(chunks)
                        )

                        successful += 1
                        total_chunks += len(chunks)

                        st.session_state.processed_papers.append({
                            "name": file.name,
                            "pages": len(pages),
                            "chunks": len(chunks),
                            "processed_at": datetime.now().strftime(
                                "%d-%m-%Y %H:%M"
                            )
                        })

                    progress.progress(
                        (index + 1) / len(uploaded_files)
                    )

                except Exception as e:

                    st.error(
                        f"Failed to process {file.name}: {e}"
                    )

            st.session_state.total_chunks += total_chunks

            if successful:

                st.success(
                    f"Successfully processed {successful} document(s)."
                )

                st.info(
                    f"Created {total_chunks} searchable sections."
                )

    st.divider()

    st.markdown("### Document Collection")

    try:
        saved_papers = get_uploaded_papers()
        display_papers = [
            {
                "Document": paper.get("filename", "Unknown"),
                "Pages": paper.get("page_count", 0),
                "Indexed Sections": paper.get("chunk_count", 0),
                "Uploaded At": paper.get("uploaded_at").astimezone().strftime("%d-%m-%Y %H:%M")
                    if paper.get("uploaded_at") else "Unknown"
            }
            for paper in saved_papers
        ]
        if display_papers:
            st.dataframe(pd.DataFrame(display_papers), use_container_width=True, hide_index=True)
        else:
            st.info("No documents have been saved yet.")
    except Exception as e:
        st.error(f"Could not load saved papers from MongoDB: {e}")


# =====================================================
# 9. AI RESEARCH ASSISTANT
# =====================================================

elif page == "AI Research Assistant":

    st.markdown("## AI Research Assistant")

    st.caption(
        "Evaluate your research idea using your indexed papers."
    )

    if chunk_count() == 0:

        st.warning(
            "Your research collection is empty. "
            "Upload and process papers first."
        )

    research_idea = st.text_area(
        "PROPOSED RESEARCH IDEA",
        height=180,
        placeholder=(
            "Describe your research problem, objectives, "
            "proposed technology and expected contribution..."
        )
    )

    if st.button(
        "GENERATE ANALYSIS",
        use_container_width=True
    ):

        if not research_idea.strip():

            st.warning("Enter a research idea.")

        elif chunk_count() == 0:

            st.warning("Process research papers first.")

        else:

            try:

                with st.spinner(
                    "Searching documents and generating AI analysis..."
                ):

                    result = analyze_research_idea(
                        research_idea.strip()
                    )

                    # Save the idea and its generated analysis permanently.
                    save_research_idea(research_idea.strip())
                    save_analysis(
                        research_idea.strip(),
                        result.get("analysis", ""),
                        result.get("sources", [])
                    )

                    analysis_data = {
                        "idea": research_idea.strip(),
                        "result": result,
                        "date": datetime.now().strftime(
                            "%d-%m-%Y %H:%M:%S"
                        )
                    }

                    st.session_state.last_analysis = analysis_data

                    st.session_state.analysis_history.append(
                        analysis_data
                    )

                st.success("Analysis generated successfully.")

            except Exception as e:

                st.error(f"Analysis failed: {e}")

    if st.session_state.last_analysis:

        data = st.session_state.last_analysis

        result = data["result"]

        st.divider()

        st.markdown("### Analysis Results")

        st.caption(
            f"Generated: {data['date']}"
        )

        st.markdown("#### Proposed Research Idea")

        st.info(data["idea"])

        st.markdown("#### AI-Generated Analysis")

        st.markdown(
            result.get("analysis", "No analysis available.")
        )

        st.divider()

        st.markdown("### Retrieved Evidence")

        sources = result.get("sources", [])

        if sources:

            for index, source in enumerate(sources, 1):

                filename = source.get(
                    "source_file",
                    "Unknown PDF"
                )

                page_number = source.get(
                    "page_number",
                    "Unknown"
                )

                with st.expander(
                    f"Source {index} | {filename} | Page {page_number}"
                ):

                    st.write(source.get("text", ""))

        else:

            st.warning("No supporting sources were retrieved.")

        report = create_report(
            data["idea"],
            result,
            data["date"]
        )

        st.download_button(
            "DOWNLOAD RESEARCH REPORT",
            data=report,
            file_name="ResearchIQ_Analysis_Report.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.caption(
            "AI-generated analysis does not guarantee research originality. "
            "Verify conclusions using a broader literature review."
        )


# =====================================================
# 10. RESEARCH ANALYTICS
# =====================================================

elif page == "Research Analytics":

    st.markdown("## Research Analytics")

    st.caption(
        "Document processing statistics and research collection overview."
    )

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Total Documents", paper_count())

    with c2:
        st.metric("Indexed Sections", chunk_count())

    try:
        db_stats = get_database_statistics()
        st.caption(
            f"MongoDB records: {db_stats['total_papers']} papers · "
            f"{db_stats['total_ideas']} ideas · {db_stats['total_analyses']} analyses"
        )
    except Exception as e:
        st.warning(f"MongoDB statistics unavailable: {e}")

    try:
        saved_papers = get_uploaded_papers()
        analytics_rows = [
            {
                "name": paper.get("filename", "Unknown"),
                "chunks": paper.get("chunk_count", 0),
                "pages": paper.get("page_count", 0)
            }
            for paper in saved_papers
        ]
    except Exception as e:
        analytics_rows = []
        st.error(f"Could not load MongoDB analytics: {e}")

    if analytics_rows:

        df = pd.DataFrame(analytics_rows)

        st.divider()

        st.markdown("### Document Processing Statistics")

        fig = px.bar(
            df,
            x="name",
            y="chunks",
            title="Sections Created Per Research Paper",
            labels={
                "name": "Research Document",
                "chunks": "Number of Sections"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#101418",
            plot_bgcolor="#101418",
            font_color="#E8EEF2"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("### Document Details")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Process research papers to view analytics."
        )


# =====================================================
# 11. ANALYSIS HISTORY
# =====================================================

elif page == "Analysis History":

    st.markdown("## Analysis History")

    st.caption(
        "Review your previous research analyses in this session."
    )

    try:
        saved_history = get_analysis_history()
    except Exception as e:
        saved_history = []
        st.error(f"Could not load analysis history from MongoDB: {e}")

    if saved_history:

        for index, item in enumerate(saved_history, start=1):
            created_at = item.get("created_at")
            display_date = created_at.astimezone().strftime("%d-%m-%Y %H:%M:%S") if created_at else "Unknown date"
            idea = item.get("research_idea", "")
            result = {
                "analysis": item.get("analysis", "No analysis available."),
                "sources": item.get("sources", [])
            }

            with st.expander(f"Analysis {index} | {display_date}"):

                st.markdown("#### Research Idea")
                st.write(idea)

                st.markdown("#### Analysis")
                st.markdown(result["analysis"])

                report = create_report(idea, result, display_date)

                st.download_button(
                    "DOWNLOAD REPORT",
                    data=report,
                    file_name=f"ResearchIQ_Report_{index}.txt",
                    mime="text/plain",
                    key=f"history_report_{index}"
                )

    else:

        st.info("No saved research analyses found in MongoDB yet.")


# =====================================================
# 12. FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div class="footer-text">
        RESEARCHIQ<br><br>
        ACADEMIC RESEARCH INTELLIGENCE PLATFORM<br><br>
        Python · Streamlit · RAG · ChromaDB · MongoDB · Ollama
    </div>
    """,
    unsafe_allow_html=True
)