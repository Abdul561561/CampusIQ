# CampusIQ — AI Academic Document Assistant

> **Tagline:** *Your academic documents. Your answers. Your sources.*

CampusIQ is an enterprise-grade Retrieval-Augmented Generation (RAG) web application designed for students and academic institutions. It enables users to upload academic PDF documents (syllabi, examination rules, placement guidelines, course notes) and receive precise, context-grounded answers with source filename and page citations.

---

## 🌟 Key Features

1. **Academic PDF Intelligence**: Upload multiple PDF documents (Syllabus, Exam Guidelines, Placement Manuals) and extract structured text with preserved page numbers.
2. **Local Embedding & FAISS Vector Indexing**: Document embeddings are generated 100% locally using HuggingFace `sentence-transformers/all-MiniLM-L6-v2` into an in-memory FAISS vector index. No paid embedding API is required.
3. **Context-Grounded Q&A Chat**: OpenRouter LLM answer generation strictly restricted to retrieved document context.
4. **Expandable Source Citations**: Displays exact filename and page number badges for every factual assertion.
5. **Prompt Engineering Lab (10 Assessment Marks)**: Interactive Prompt Lab comparing three strategy tiers:
   - **Strategy A (Basic)**: Standard prompt.
   - **Strategy B (Structured RAG)**: Strict context boundaries and citation enforcement.
   - **Strategy C (Robust RAG)**: Prompt injection defense, conflict resolution, and strict evidence vs. interpretation split.
6. **Automated RAG Evaluation Suite**: 5 canonical test cases evaluating fact extraction, section queries, multi-chunk synthesis, missing info handling, and security resilience.
7. **Session Isolation**: Clear session state with one-click reset to prevent multi-tenant document leaks.
8. **Docker & Cloud Deployment Ready**: Pre-configured Dockerfile for containerized deployment on Hugging Face Spaces.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **User Interface** | Gradio (Custom CSS Academic Theme) |
| **PDF Extraction** | `pypdf` |
| **Text Chunking** | `RecursiveCharacterTextSplitter` (LangChain) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (Local Execution) |
| **Vector Database** | `FAISS` (`faiss-cpu`) |
| **Orchestration** | LangChain |
| **LLM Provider** | OpenRouter API (`ChatOpenAI` wrapper) |
| **Containerization** | Docker / Docker Compose |

---

## 🚀 Quickstart Guide (Windows PowerShell)

Follow these step-by-step instructions to set up and run CampusIQ on Windows.

### Step 1: Clone or Open Workspace
Open Windows PowerShell and navigate to the project directory:
```powershell
cd C:\Users\shabi\Desktop\CampusIQ
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment named venv
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Generate Sample Academic PDFs
Generate the realistic test PDFs (Syllabus, Exam Guidelines, Placement Manual):
```powershell
python sample_documents/generate_samples.py
```

### Step 5: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` in Notepad or VS Code and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
```
*(Get a free API key at [https://openrouter.ai/keys](https://openrouter.ai/keys))*

### Step 6: Launch the Application
```powershell
python app.py
```
Open your web browser at: `http://localhost:7860`

---

## 🧪 Running Automated Unit Tests

Run the test suite offline without consuming API credits:
```powershell
pytest
```
To run specific test modules:
```powershell
pytest tests/test_chunking.py
pytest tests/test_prompt_templates.py
pytest tests/test_rag_logic.py
```

---

## 🐳 Docker Build & Execution

Build and run CampusIQ locally inside a Docker container.

### Build Image:
```bash
docker build -t campusiq .
```

### Run Container:
```bash
docker run --rm -p 7860:7860 -e OPENROUTER_API_KEY="your_openrouter_api_key_here" campusiq
```
Access the application at `http://localhost:7860`.

---

## 🐙 Push Project to GitHub

Follow these commands to push CampusIQ to your GitHub repository:

```powershell
# Initialize Git repository
git init

# Add all project files
git add .

# Initial commit
git commit -m "Initial commit: CampusIQ AI Academic Document Assistant"

# Rename branch to main
git branch -M main

# Add your GitHub remote repository URL
git remote add origin https://github.com/YOUR_USERNAME/CampusIQ.git

# Push code to GitHub
git push -u origin main
```

*(Ensure `.env` is never committed. `.gitignore` automatically excludes it.)*

---

## ☁️ Deployment Guide (Hugging Face Spaces)

1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Choose **Docker** as the SDK.
3. Select **Blank** template.
4. Go to **Settings** $\rightarrow$ **Variables and secrets**:
   - Add Secret: `OPENROUTER_API_KEY` = `your_actual_key`
   - Add Variable: `OPENROUTER_MODEL` = `meta-llama/llama-3.3-70b-instruct:free`
5. Connect your GitHub repository or push your code directly to HF Spaces Git repository.
6. Hugging Face Spaces will build the Docker image and deploy CampusIQ automatically on port `7860`.

---

## 📚 Project Documentation & Assessment Files

- 🏛️ **Architecture & Component Specs**: [docs/architecture.md](file:///c:/Users/shabi/Desktop/CampusIQ/docs/architecture.md)
- 🔬 **Prompt Engineering Analysis**: [docs/prompt_engineering.md](file:///c:/Users/shabi/Desktop/CampusIQ/docs/prompt_engineering.md)
- 🎓 **Viva Q&A & Demo Script**: [docs/viva_questions.md](file:///c:/Users/shabi/Desktop/CampusIQ/docs/viva_questions.md)

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).
