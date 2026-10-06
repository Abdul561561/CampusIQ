# CampusIQ Prompt Engineering Deep Dive

Prompt engineering carries **10 evaluation marks** in the assessment. This document details the design philosophy, security measures, and comparative analysis of the 3 prompt strategies implemented in CampusIQ.

---

## 1. Comparative Analysis of Prompt Strategies

| Feature | Strategy A (Basic) | Strategy B (Structured RAG) | Strategy C (Robust RAG) |
|---|---|---|---|
| **Context Boundaries** | Minimal | Explicit delimiters (`=== CONTEXT ===`) | Secure tags (`=== SECURE CONTEXT ===`) |
| **Grounding Mandate** | Implicit | Strict (Context-only) | Strict + Evidence/Interpretation split |
| **Missing Info Rule** | None (Risk of invention) | Explicit fallback statement | Explicit fallback + zero-speculation |
| **Citation Enforcement** | Optional | Compulsory `[File, Page]` | Compulsory `[File, Page]` in list |
| **Prompt Injection Resilience** | ❌ Vulnerable | ⚠️ Partial | ✅ Defended (`UNTRUSTED DATA SAFEGUARD`) |
| **Conflict Resolution** | ❌ Fails / Pick random | ⚠️ Unpredictable | ✅ Explicit contradiction highlighting |

---

## 2. Prompt Strategy Definitions

### Strategy A: Basic Prompting
- **Purpose**: Baseline comparison. Demonstrates standard context injection without safety rails.
- **Vulnerability**: Susceptible to hallucination when information is missing from documents.

### Strategy B: Structured RAG Prompting
- **Purpose**: Production-grade RAG prompt. Enforces boundaries and citations.
- **Key Directive**: Requires explicit admission when information is missing (`Information not available in the provided documents`).

### Strategy C: Robust Security RAG Prompting
- **Purpose**: Enterprise RAG prompt designed for untrusted user uploads.
- **Key Directives**:
  1. **Untrusted Data Isolation**: Prevents malicious text in uploaded PDFs from hijacking LLM system behavior.
  2. **Conflict Resolution**: Resolves opposing guidelines across different uploaded PDFs (e.g. syllabus vs handbook).
  3. **Strict Citation & Evidence Separation**: Forces LLM to differentiate direct document facts from logical interpretation.
