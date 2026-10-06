# CampusIQ Architecture Documentation

## 1. System Overview

CampusIQ is an enterprise-grade Retrieval-Augmented Generation (RAG) system built to parse, index, search, and answer student questions grounded in academic documents (syllabi, regulations, exam guides, placement policies).

```
                      +---------------------------------+
                      |     User Web UI (Gradio)        |
                      +---------------------------------+
                                       |
                1. Upload PDF          | 2. Ask Question
                                       v
                      +---------------------------------+
                      |     CampusIQ RAG Pipeline       |
                      +---------------------------------+
                         /           |           \
       3. Text Extraction           |             \ 6. Query Prompt
      (pypdf + Metadata)            |              \ (Strategy A/B/C)
                       /             |               \
                      v              | 5. Vector      v
         +-----------------------+   |    Search   +--------------------+
         | Recursive Character   |   |   (Top-K)   |  OpenRouter LLM    |
         | Splitter (800/120)    |   |             | (Llama-3.3 / etc) |
         +-----------------------+   |             +--------------------+
                      |              v                       |
       4. Local Embed |    +-------------------+             | 7. Grounded Answer
    (all-MiniLM-L6-v2)|    |  FAISS Vector DB  |             |  + Citations
                      +--->|  (In-Memory RAM)  |<------------+
                           +-------------------+
```

---

## 2. Component Design & Local vs Remote Runtime

| Layer | Component | Execution Location | Technology | Key Responsibility |
|---|---|---|---|---|
| **UI** | Dashboard UI | 💻 Local / Container | Gradio | Modern responsive web interface, tabbed navigation, source accordions |
| **PDF Extraction** | Document Loader | 💻 Local | `pypdf` | Extracts clean text and attaches `{"source": filename, "page": page_num}` |
| **Chunking** | Text Splitter | 💻 Local | `RecursiveCharacterTextSplitter` | Splits text into 800-character windows with 120-character overlap |
| **Embeddings** | Vector Embedder | 💻 Local | `sentence-transformers/all-MiniLM-L6-v2` | Converts text chunks into 384-dimensional semantic dense vectors |
| **Vector DB** | Vector Index | 💻 Local (RAM) | `FAISS` | Similarity search (L2 / Cosine) over document embeddings |
| **LLM Inference** | Answer Generator | 🌐 Remote API | `OpenRouter API` | Generates student-friendly answers using context and prompt rules |

---

## 3. Data Flow Step-by-Step

1. **PDF Upload & Validation**: User uploads PDFs. PyPDF checks encryption, zero-length files, and page count.
2. **Text Extraction with Metadata**: Text extracted page-by-page. Metadata contains `source` filename and 1-indexed `page`.
3. **Chunking**: Text chunks generated while preserving document metadata on every single chunk.
4. **Local Embedding Generation**: HuggingFace `all-MiniLM-L6-v2` runs on CPU locally to embed text chunks into vectors.
5. **FAISS Indexing**: Vector index built or updated in memory.
6. **Query Processing**: User submits question $\rightarrow$ question embedded $\rightarrow$ FAISS retrieves Top-K relevant chunks.
7. **Prompt Selection**: User query and formatted context wrapped inside selected Prompt Strategy (A, B, or C).
8. **LLM Generation**: Prompt payload sent to OpenRouter API $\rightarrow$ LLM returns grounded answer with page citations.
