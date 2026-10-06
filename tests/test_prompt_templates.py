"""
Unit tests for prompt strategy formatting and prompt injection safeguards.
"""

import unittest
from prompt_templates import get_prompt_components, PROMPT_EXPLANATIONS

class TestPromptTemplates(unittest.TestCase):

    def test_prompt_strategy_components(self):
        context = "--- Source: Syllabus.pdf (Page 1) ---\nAttendance required is 75%."
        question = "What is attendance requirement?"

        sys_a, user_a = get_prompt_components("Strategy A (Basic)", context, question)
        sys_b, user_b = get_prompt_components("Strategy B (Structured RAG)", context, question)
        sys_c, user_c = get_prompt_components("Strategy C (Robust RAG)", context, question)

        # Verify system prompts exist and differ
        self.assertNotEqual(sys_a, sys_b)
        self.assertNotEqual(sys_b, sys_c)

        # Strategy C must contain security isolation directive
        self.assertIn("UNTRUSTED DATA SAFEGUARD", sys_c)
        self.assertIn("CONFLICT RESOLUTION", sys_c)

        # Strategy B must contain citation rule
        self.assertIn("Cite source filenames", sys_b)

    def test_prompt_explanations(self):
        self.assertIn("Strategy A (Basic)", PROMPT_EXPLANATIONS)
        self.assertIn("Strategy B (Structured RAG)", PROMPT_EXPLANATIONS)
        self.assertIn("Strategy C (Robust RAG)", PROMPT_EXPLANATIONS)

if __name__ == "__main__":
    unittest.main()
