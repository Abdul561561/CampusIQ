"""
Unit tests for text chunking and metadata preservation.
"""

import unittest
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TestChunking(unittest.TestCase):

    def test_chunking_metadata_preservation(self):
        text = "This is sentence one. " * 30 + "\n\n" + "This is unit two content. " * 30
        doc = Document(
            page_content=text,
            metadata={"source": "Test_Syllabus.pdf", "page": 1}
        )

        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        chunks = splitter.split_documents([doc])

        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertEqual(chunk.metadata["source"], "Test_Syllabus.pdf")
            self.assertEqual(chunk.metadata["page"], 1)
            self.assertLessEqual(len(chunk.page_content), 350)  # Margin for word boundaries

if __name__ == "__main__":
    unittest.main()
