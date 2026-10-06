"""
CampusIQ Core RAG Pipeline
Handles PDF loading, text extraction with page metadata, RecursiveCharacterTextSplitter chunking,
local HuggingFace FAISS vector indexing, similarity retrieval, and OpenRouter LLM answer generation.
"""

import os
import tempfile
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

import pypdf
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI

from config import Config
from prompt_templates import get_prompt_components, PROMPT_EXPLANATIONS


class CampusIQRAGPipeline:
    """Manages document processing, vector database, retrieval, and LLM inference for CampusIQ."""

    def __init__(self):
        self.vector_store: Optional[FAISS] = None
        self.embeddings: Optional[HuggingFaceEmbeddings] = None
        self.indexed_files: List[Dict[str, Any]] = []  # List of {"filename": str, "pages": int, "chunks": int}
        self.total_pages: int = 0
        self.total_chunks: int = 0
        self._init_embeddings()

    def _init_embeddings(self) -> None:
        """Initialize local HuggingFace embedding model."""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL_NAME,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            print(f"[CampusIQ] Warning: Failed to load local embedding model: {e}")
            self.embeddings = None

    def reset_session(self) -> str:
        """Clears all indexed documents and vector index for current session."""
        self.vector_store = None
        self.indexed_files = []
        self.total_pages = 0
        self.total_chunks = 0
        return "Session successfully reset. All indexed documents have been cleared."

    def extract_text_from_pdf(self, file_path: str, original_filename: str) -> Tuple[List[Document], List[str]]:
        """
        Extract text page-by-page from a PDF file preserving metadata.
        Returns (list of Document objects, list of warnings/errors).
        """
        documents: List[Document] = []
        warnings: List[str] = []

        try:
            reader = pypdf.PdfReader(file_path)
            
            # Check for encrypted / password protected PDF
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    return [], [f"File '{original_filename}' is password-protected and cannot be read."]

            total_pages = len(reader.pages)
            if total_pages == 0:
                return [], [f"File '{original_filename}' contains 0 pages."]

            empty_pages_count = 0
            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                try:
                    text = page.extract_text() or ""
                    text = text.strip()
                    if text:
                        documents.append(
                            Document(
                                page_content=text,
                                metadata={
                                    "source": original_filename,
                                    "page": page_num,
                                    "total_pages": total_pages
                                }
                            )
                        )
                    else:
                        empty_pages_count += 1
                except Exception as page_err:
                    warnings.append(f"Failed to extract text from page {page_num} of '{original_filename}': {page_err}")

            if empty_pages_count == total_pages:
                warnings.append(f"File '{original_filename}' has no extractable text (it might be scanned/image-only).")

        except Exception as e:
            return [], [f"Failed to process PDF '{original_filename}': {str(e)}"]

        return documents, warnings

    def process_pdf_files(self, file_paths: List[str]) -> Tuple[str, Dict[str, Any]]:
        """
        Process a list of uploaded PDF files: text extraction, chunking, and FAISS indexing.
        """
        if not file_paths:
            return "No files were uploaded.", self.get_stats()

        if self.embeddings is None:
            self._init_embeddings()
            if self.embeddings is None:
                return "Error: Embedding model failed to initialize. Check internet connection or PyTorch setup.", self.get_stats()

        all_chunks: List[Document] = []
        processing_logs: List[str] = []
        new_files_summary: List[Dict[str, Any]] = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        for file_path in file_paths:
            filename = os.path.basename(file_path)
            
            # Extract text
            raw_docs, warnings = self.extract_text_from_pdf(file_path, filename)
            processing_logs.extend(warnings)

            if not raw_docs:
                continue

            # Split into chunks
            chunks = text_splitter.split_documents(raw_docs)
            if not chunks:
                processing_logs.append(f"No text chunks created for '{filename}'.")
                continue

            num_pages = len(set(d.metadata['page'] for d in raw_docs))
            num_chunks = len(chunks)

            all_chunks.extend(chunks)
            new_files_summary.append({
                "filename": filename,
                "pages": num_pages,
                "chunks": num_chunks
            })

            self.total_pages += num_pages
            self.total_chunks += num_chunks

        if not all_chunks:
            return "No text could be extracted from the uploaded PDF files.\n" + "\n".join(processing_logs), self.get_stats()

        # Update or create FAISS vector index
        try:
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(all_chunks, self.embeddings)
            else:
                self.vector_store.add_documents(all_chunks)

            self.indexed_files.extend(new_files_summary)

            success_msg = f" Successfully processed {len(new_files_summary)} PDF file(s) into {len(all_chunks)} text chunks."
            if processing_logs:
                success_msg += "\n\nWarnings/Notes:\n- " + "\n- ".join(processing_logs)

            return success_msg, self.get_stats()

        except Exception as e:
            return f"Error indexing documents in FAISS: {str(e)}", self.get_stats()

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics of indexed documents."""
        return {
            "num_files": len(self.indexed_files),
            "total_pages": self.total_pages,
            "total_chunks": self.total_chunks,
            "file_list": [f["filename"] for f in self.indexed_files],
            "file_details": self.indexed_files
        }

    def retrieve_context(self, question: str, top_k: int = Config.TOP_K_RETRIEVAL) -> List[Document]:
        """Retrieve top_k relevant document chunks for a question."""
        if self.vector_store is None:
            return []

        try:
            docs = self.vector_store.similarity_search(question, k=top_k)
            return docs
        except Exception as e:
            print(f"[CampusIQ] Error during vector search: {e}")
            return []

    def format_retrieved_context(self, docs: List[Document]) -> str:
        """Format retrieved Document objects into a clean text context block with citations."""
        if not docs:
            return "No relevant context found in uploaded documents."

        formatted_passages = []
        for idx, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown Document")
            page = doc.metadata.get("page", "?")
            text = doc.page_content.strip()
            formatted_passages.append(
                f"--- [Passage {idx}] Source: {source} (Page {page}) ---\n{text}"
            )

        return "\n\n".join(formatted_passages)

    def query_rag(self, question: str, prompt_strategy: str = "Strategy C (Robust RAG)", top_k: int = Config.TOP_K_RETRIEVAL) -> Dict[str, Any]:
        """
        Executes complete RAG query flow:
        1. Validates vector store state
        2. Retrieves top-k chunks
        3. Formats context
        4. Selects prompt strategy
        5. Calls OpenRouter LLM
        6. Returns structured answer and metadata
        """
        if self.vector_store is None:
            return {
                "answer": "⚠️ **No documents uploaded.** Please upload and process academic PDFs in the left panel first before asking questions.",
                "context": "",
                "docs": [],
                "strategy": prompt_strategy,
                "model": Config.OPENROUTER_MODEL,
                "grounded": False,
                "error": "No indexed documents"
            }

        if not question or not question.strip():
            return {
                "answer": "Please enter a valid question.",
                "context": "",
                "docs": [],
                "strategy": prompt_strategy,
                "model": Config.OPENROUTER_MODEL,
                "grounded": False,
                "error": "Empty question"
            }

        # Step 1: Retrieve context
        docs = self.retrieve_context(question, top_k=top_k)
        if not docs:
            return {
                "answer": "Information not available in the provided documents.",
                "context": "No relevant document chunks retrieved.",
                "docs": [],
                "strategy": prompt_strategy,
                "model": Config.OPENROUTER_MODEL,
                "grounded": False,
                "error": None
            }

        formatted_context = self.format_retrieved_context(docs)

        # Step 2: Format prompt
        sys_prompt, user_prompt = get_prompt_components(prompt_strategy, formatted_context, question)

        # Step 3: Validate API Key
        if not Config.validate_api_key():
            return {
                "answer": "⚠️ **OpenRouter API Key Missing or Invalid.**\n\nPlease configure your `OPENROUTER_API_KEY` in `.env` or set it in your environment variables to enable AI answer generation.",
                "context": formatted_context,
                "docs": docs,
                "strategy": prompt_strategy,
                "model": Config.OPENROUTER_MODEL,
                "grounded": False,
                "error": "API Key missing"
            }

        # Step 4: Call OpenRouter LLM
        try:
            llm = ChatOpenAI(
                openai_api_base=Config.OPENROUTER_BASE_URL,
                openai_api_key=Config.OPENROUTER_API_KEY,
                model_name=Config.OPENROUTER_MODEL,
                temperature=0.1,  # Low temperature for factual precision
                max_tokens=1000
            )

            messages = [
                SystemMessage(content=sys_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = llm.invoke(messages)
            answer_text = response.content if hasattr(response, 'content') else str(response)

            return {
                "answer": answer_text,
                "context": formatted_context,
                "docs": docs,
                "strategy": prompt_strategy,
                "model": Config.OPENROUTER_MODEL,
                "grounded": True,
                "error": None
            }

        except Exception as e:
            err_str = str(e)
            user_friendly_err = f"⚠️ **OpenRouter API Request Failed:** {err_str}"
            if "401" in err_str or "unauthorized" in err_str.lower():
                user_friendly_err = "⚠️ **Invalid OpenRouter API Key.** Please verify your key at https://openrouter.ai/keys."
            elif "429" in err_str or "rate limit" in err_str.lower():
                user_friendly_err = "⚠️ **OpenRouter Rate Limit Exceeded.** Please wait a moment or try another model."

            return {
                "answer": user_friendly_err,
                "context": formatted_context,
                "docs": docs,
                "strategy": prompt_strategy,
                "model": Config.OPENROUTER_MODEL,
                "grounded": False,
                "error": err_str
            }
