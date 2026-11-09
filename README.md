# ResearchIQ – Academic Research Intelligence Platform

An AI-powered academic research intelligence platform that helps researchers explore existing research papers, identify potential research gaps, and discover opportunities for novel research contributions using Retrieval-Augmented Generation (RAG).

## 🚀 Project Overview

ResearchIQ combines Artificial Intelligence, Natural Language Processing, and semantic search to make academic research analysis easier and more efficient.

Users can upload research papers in PDF format and interact with an AI research assistant to investigate research ideas using information retrieved from their uploaded documents.

## ✨ Key Features

- **PDF Research Paper Upload:** Upload and process academic research papers.
- **Text Extraction:** Extract text from PDF documents.
- **Text Chunking:** Divide research papers into manageable text sections.
- **Semantic Embeddings:** Generate vector embeddings using Sentence Transformers.
- **Vector Database:** Store and retrieve research content using ChromaDB.
- **AI Research Assistant:** Analyze research ideas using Retrieval-Augmented Generation.
- **Research Gap Identification:** Explore potential research gaps based on retrieved documents.
- **Novelty Analysis:** Identify potential novel research contributions.
- **Research Analytics:** View research-related statistics.
- **Analysis History:** Maintain a history of previous analyses.
- **Report Generation:** Generate downloadable research analysis reports.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Streamlit | User interface |
| MongoDB Atlas | Database |
| ChromaDB | Vector database |
| Sentence Transformers | Text embeddings |
| Ollama | Local Large Language Model |
| Qwen 2.5 (3B) | AI language model |
| PyPDF | PDF text extraction |
| Retrieval-Augmented Generation | Context-based AI analysis |

## 📂 Project Structure

```text
ResearchIQ/
│
├── modules/
│   ├── embeddings.py
│   ├── novelty_analyzer.py
│   ├── pdf_processor.py
│   ├── rag_pipeline.py
│   ├── text_chunker.py
│   └── vector_store.py
│
├── reports/
├── uploads/
├── vector_db/
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/HarikrishnanS1713/researchiq-academic-platform.git
```

### 2. Navigate to the Project

```bash
cd researchiq-academic-platform
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

Windows:

```powershell
.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your own MongoDB Atlas configuration:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB