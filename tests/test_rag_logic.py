"""
Unit tests for RAG pipeline logic (PDF processing, vector indexing, retrieval, and mocked LLM inference).
"""

import unittest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from rag_pipeline import CampusIQRAGPipeline

class TestRAGLogic(unittest.TestCase):

    def setUp(self):
        self.pipeline = CampusIQRAGPipeline()

    def test_session_reset(self):
        self.pipeline.total_pages = 5
        self.pipeline.total_chunks = 20
        self.pipeline.indexed_files = [{"filename": "doc.pdf", "pages": 5, "chunks": 20}]
        
        msg = self.pipeline.reset_session()
        stats = self.pipeline.get_stats()

        self.assertEqual(stats["num_files"], 0)
        self.assertEqual(stats["total_pages"], 0)
        self.assertEqual(stats["total_chunks"], 0)
        self.assertIsNone(self.pipeline.vector_store)

    def test_format_retrieved_context(self):
        docs = [
            Document(page_content="Attendance is 75%.", metadata={"source": "Syllabus.pdf", "page": 1}),
            Document(page_content="Unit 3 is DP.", metadata={"source": "Syllabus.pdf", "page": 2})
        ]
        formatted = self.pipeline.format_retrieved_context(docs)

        self.assertIn("--- [Passage 1] Source: Syllabus.pdf (Page 1) ---", formatted)
        self.assertIn("Attendance is 75%.", formatted)
        self.assertIn("--- [Passage 2] Source: Syllabus.pdf (Page 2) ---", formatted)

    @patch("rag_pipeline.ChatOpenAI")
    def test_query_rag_with_mocked_llm(self, mock_chat_openai):
        # Setup mock vector store
        mock_docs = [
            Document(page_content="Attendance requirement is 75%.", metadata={"source": "Rules.pdf", "page": 4})
        ]
        self.pipeline.vector_store = MagicMock()
        self.pipeline.vector_store.similarity_search.return_value = mock_docs

        # Setup mock ChatOpenAI response
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "According to [Rules.pdf, Page 4], the minimum attendance required is 75%."
        mock_llm_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm_instance

        # Execute query_rag
        with patch("config.Config.validate_api_key", return_value=True):
            res = self.pipeline.query_rag("What is attendance?", prompt_strategy="Strategy C (Robust RAG)")

        self.assertTrue(res["grounded"])
        self.assertIn("75%", res["answer"])
        self.assertEqual(len(res["docs"]), 1)

if __name__ == "__main__":
    unittest.main()
