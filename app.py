"""
CampusIQ - AI Academic Document Assistant
Gradio User Interface Application
Implements session state isolation via gr.State to ensure no document leakage across users.
"""

import os
import gradio as gr
from config import Config
from rag_pipeline import CampusIQRAGPipeline
from prompt_templates import PROMPT_EXPLANATIONS, get_prompt_components
from evaluation import RAGEvaluator, EVALUATION_TEST_CASES

# Custom Academic Dashboard CSS
CUSTOM_CSS = """
/* CampusIQ Dashboard Theme */
.container {
    max-width: 1200px;
    margin: 0 auto;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.header-box {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.2);
}
.header-box h1 {
    color: white !important;
    font-weight: 800;
    margin-bottom: 4px;
    font-size: 2.2rem;
}
.header-box p {
    color: #e0f2fe;
    font-size: 1.05rem;
    margin: 0;
}
.stat-card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: center;
}
.stat-number {
    font-size: 1.6rem;
    font-weight: 700;
    color: #2563eb;
}
.stat-label {
    font-size: 0.85rem;
    color: #64748b;
    font-weight: 500;
}
.citation-box {
    background-color: #f1f5f9;
    border-left: 4px solid #3b82f6;
    padding: 12px;
    margin-top: 8px;
    font-size: 0.9rem;
    border-radius: 0 6px 6px 0;
}
.badge-tech {
    background-color: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
}
"""


def get_pipeline(session_pipeline):
    """Ensures each session has its own isolated CampusIQRAGPipeline instance."""
    if session_pipeline is None or not isinstance(session_pipeline, CampusIQRAGPipeline):
        session_pipeline = CampusIQRAGPipeline()
    return session_pipeline


def update_stats_display(pipeline: CampusIQRAGPipeline) -> str:
    """Generates Markdown stats summary for current isolated session."""
    stats = pipeline.get_stats()
    num_files = stats["num_files"]
    total_pages = stats["total_pages"]
    total_chunks = stats["total_chunks"]
    file_list = stats["file_list"]

    files_str = ", ".join(file_list) if file_list else "None"
    
    return f"""
<div style="display: flex; gap: 16px; margin: 12px 0;">
    <div class="stat-card" style="flex: 1;">
        <div class="stat-number">{num_files}</div>
        <div class="stat-label">PDF Documents</div>
    </div>
    <div class="stat-card" style="flex: 1;">
        <div class="stat-number">{total_pages}</div>
        <div class="stat-label">Extracted Pages</div>
    </div>
    <div class="stat-card" style="flex: 1;">
        <div class="stat-number">{total_chunks}</div>
        <div class="stat-label">FAISS Text Chunks</div>
    </div>
</div>

**Indexed Files:** `{files_str}`
"""


def process_documents_handler(files, session_pipeline):
    """Handles PDF file upload and processing for session."""
    pipeline = get_pipeline(session_pipeline)

    if not files:
        return "⚠️ Please select at least one PDF file to upload.", update_stats_display(pipeline), pipeline

    file_paths = [f.name if hasattr(f, 'name') else f for f in files]
    status_msg, stats = pipeline.process_pdf_files(file_paths)
    return status_msg, update_stats_display(pipeline), pipeline


def chat_handler(question, history, top_k, session_pipeline):
    """Processes question in Q&A chat tab using session pipeline."""
    pipeline = get_pipeline(session_pipeline)

    if not question or not question.strip():
        return history, "", "No question provided."

    res = pipeline.query_rag(question, prompt_strategy="Strategy C (Robust RAG)", top_k=int(top_k))
    answer = res["answer"]
    
    # Format source citation list for accordion
    if res["docs"]:
        sources_md = "### 📚 Retrieved Context Passages:\n\n"
        for idx, doc in enumerate(res["docs"], 1):
            src = doc.metadata.get("source", "Unknown File")
            pg = doc.metadata.get("page", "?")
            snippet = doc.page_content.strip()
            sources_md += f"**[Source {idx}] {src} — Page {pg}**\n```text\n{snippet}\n```\n\n"
    else:
        sources_md = "*No document passages retrieved.*"

    history = history or []
    history.append((question, answer))
    
    return history, "", sources_md


def reset_session_handler(session_pipeline):
    """Resets session vector state."""
    pipeline = get_pipeline(session_pipeline)
    msg = pipeline.reset_session()
    return [], update_stats_display(pipeline), "*Session reset. No documents indexed.*", msg, pipeline


def prompt_lab_handler(question, strategy, top_k, session_pipeline):
    """Processes question under selected prompt strategy in Prompt Lab."""
    pipeline = get_pipeline(session_pipeline)
    evaluator = RAGEvaluator(pipeline)

    if not question or not question.strip():
        return "Please enter a question to evaluate.", "", "", ""

    res = pipeline.query_rag(question, prompt_strategy=strategy, top_k=int(top_k))
    
    answer = res["answer"]
    context = res["context"]

    # Groundedness & evidence check
    has_citation = evaluator.check_citation_presence(answer)
    admits_missing = evaluator.check_missing_info_honest_admission(answer)
    groundedness = evaluator.check_groundedness_approx(answer, context)

    eval_summary = f"""### 🔬 Strategy Evaluation Summary

- **Selected Strategy:** `{strategy}`
- **Source Citations Present:** `{"Yes ✅" if has_citation else "No ❌"}`
- **Honest Missing Info Handling:** `{"Yes ✅" if admits_missing else "N/A"}`
- **Context Grounding Score:** `{groundedness * 100:.0f}%`
- **LLM Model:** `{Config.OPENROUTER_MODEL}`
"""

    exp = PROMPT_EXPLANATIONS.get(strategy, {})
    strategy_info = f"""### ℹ️ Prompt Engineering Breakdown

**Strategy Name:** {exp.get('name', strategy)}  
**Description:** {exp.get('description', '')}  
**Pros:** {exp.get('pros', '')}  
**Cons:** {exp.get('cons', '')}  
**Security Level:** `{exp.get('security', 'Medium')}`
"""

    sys_prompt, user_prompt = get_prompt_components(strategy, context or "[Retrieved passages will appear here]", question)
    full_prompt_display = f"=== SYSTEM PROMPT ===\n{sys_prompt}\n\n=== USER PROMPT ===\n{user_prompt}"

    return answer, eval_summary, full_prompt_display, strategy_info


def run_benchmark_handler(strategy, session_pipeline):
    """Runs automated benchmark evaluation suite on session pipeline."""
    pipeline = get_pipeline(session_pipeline)
    evaluator = RAGEvaluator(pipeline)
    report_data = evaluator.run_full_benchmark(prompt_strategy=strategy)
    return report_data["markdown_report"]


# Build Gradio Blocks Application
with gr.Blocks(css=CUSTOM_CSS, title="CampusIQ — AI Academic Document Assistant") as demo:

    # Per-session isolated RAG pipeline state
    session_pipeline = gr.State(CampusIQRAGPipeline)

    # Header Section
    gr.HTML("""
    <div class="header-box">
        <h1>CampusIQ</h1>
        <p>Your academic documents. Your answers. Your sources. — AI Academic Document Assistant</p>
        <div style="margin-top: 10px;">
            <span class="badge-tech">LangChain RAG</span>
            <span class="badge-tech">FAISS Vector Index</span>
            <span class="badge-tech">HuggingFace Embeddings</span>
            <span class="badge-tech">OpenRouter LLM</span>
        </div>
    </div>
    """)

    with gr.Row():
        # Left Panel: PDF Upload & Session Control
        with gr.Column(scale=1):
            gr.Markdown("### 📄 Document Upload")
            pdf_uploader = gr.File(
                label="Upload Academic PDFs",
                file_count="multiple",
                file_types=[".pdf"],
                type="filepath"
            )
            process_btn = gr.Button("⚡ Process Documents", variant="primary")
            
            top_k_slider = gr.Slider(
                minimum=1,
                maximum=8,
                value=4,
                step=1,
                label="Top-K Retrieval Count"
            )
            
            status_output = gr.Textbox(
                label="Processing Status",
                interactive=False,
                lines=3,
                value="Upload PDFs and click 'Process Documents' to begin."
            )

            stats_markdown = gr.Markdown(value="*No documents uploaded yet.*")

            reset_btn = gr.Button("🔄 Reset Session Index", variant="stop", size="sm")

            gr.Markdown("---")
            gr.Markdown("### 💡 Quick Sample Questions")
            sample_q1 = gr.Button("Attendance requirements?", size="sm")
            sample_q2 = gr.Button("Topics in Unit 3?", size="sm")
            sample_q3 = gr.Button("Placement eligibility criteria?", size="sm")

        # Right Panel: Main Application Tabs
        with gr.Column(scale=2):
            with gr.Tabs():
                
                # TAB 1: Academic Assistant (Chat & Sources)
                with gr.Tab("💬 Academic Assistant"):
                    chatbot = gr.Chatbot(
                        label="CampusIQ Academic Assistant",
                        height=440,
                        bubble_full_width=False,
                        avatar_images=None
                    )
                    
                    with gr.Row():
                        question_input = gr.Textbox(
                            show_label=False,
                            placeholder="Ask a question about your academic documents...",
                            container=False,
                            scale=4
                        )
                        ask_btn = gr.Button("Ask Question", variant="primary", scale=1)

                    clear_chat_btn = gr.Button("Clear Chat Window", size="sm")

                    with gr.Accordion("📚 View Source Citations & Passages", open=True):
                        sources_display = gr.Markdown(value="*Retrieved source passages will appear here after you ask a question.*")

                # TAB 2: Prompt Lab (Prompt Engineering Evaluation)
                with gr.Tab("🔬 Prompt Lab"):
                    gr.Markdown("### Prompt Engineering & Strategy Testing Lab")
                    gr.Markdown("Test how different prompt strategies affect hallucination, citation enforcement, and response security.")

                    with gr.Row():
                        prompt_question_input = gr.Textbox(
                            label="Test Question",
                            value="What is the minimum attendance percentage required?",
                            scale=3
                        )
                        strategy_dropdown = gr.Dropdown(
                            label="Prompt Strategy",
                            choices=["Strategy A (Basic)", "Strategy B (Structured RAG)", "Strategy C (Robust RAG)"],
                            value="Strategy C (Robust RAG)",
                            scale=2
                        )
                        eval_prompt_btn = gr.Button("Run Prompt Lab", variant="primary", scale=1)

                    with gr.Row():
                        with gr.Column():
                            lab_answer_output = gr.Textbox(label="Generated LLM Answer", lines=8)
                            lab_eval_markdown = gr.Markdown()
                        with gr.Column():
                            lab_strategy_info = gr.Markdown()
                            with gr.Accordion("View Construct Prompt Sent to LLM", open=False):
                                lab_prompt_display = gr.Textbox(label="Full Prompt Payload", lines=10)

                # TAB 3: Benchmark & Evaluation
                with gr.Tab("📊 RAG Evaluation Suite"):
                    gr.Markdown("### Automated RAG Benchmark & Viva Assessment Report")
                    gr.Markdown("Evaluate CampusIQ against 5 standard test cases (Fact extraction, Page queries, Multi-chunk synthesis, Absent information, Prompt injection resilience).")

                    with gr.Row():
                        eval_strategy_select = gr.Dropdown(
                            label="Strategy to Evaluate",
                            choices=["Strategy A (Basic)", "Strategy B (Structured RAG)", "Strategy C (Robust RAG)"],
                            value="Strategy C (Robust RAG)"
                        )
                        run_bench_btn = gr.Button("▶️ Run Automated Benchmark Suite", variant="primary")

                    benchmark_report_display = gr.Markdown(
                        value="*Click 'Run Automated Benchmark Suite' above to execute the 5 test cases.*"
                    )

                # TAB 4: Architecture & Config Info
                with gr.Tab("⚙️ System Architecture & Setup"):
                    api_status = "✅ Configured" if Config.validate_api_key() else "⚠️ Not Configured"
                    masked_key = Config.get_masked_api_key()

                    gr.Markdown(f"""
### 🛠️ CampusIQ Runtime System Status

- **OpenRouter API Key Status:** `{api_status}` (`{masked_key}`)
- **Configured OpenRouter LLM Model:** `{Config.OPENROUTER_MODEL}`
- **Local Embedding Model:** `{Config.EMBEDDING_MODEL_NAME}` (Runs 100% locally on CPU)
- **Vector Index:** FAISS (Isolated Per-Session Store)
- **Text Splitter:** RecursiveCharacterTextSplitter (Chunk Size: {Config.CHUNK_SIZE}, Overlap: {Config.CHUNK_OVERLAP})

---

### 🏛️ Local vs. External Component Breakdown

| Component | Execution Environment | Description |
|---|---|---|
| **PDF Extraction** | 💻 Local | `pypdf` extracts text and page metadata locally |
| **Text Chunking** | 💻 Local | `RecursiveCharacterTextSplitter` splits text locally |
| **Embeddings** | 💻 Local | `sentence-transformers/all-MiniLM-L6-v2` runs locally |
| **Vector DB** | 💻 Local | `FAISS` stores and searches embeddings per session in RAM |
| **UI Dashboard** | 💻 Local | `Gradio` interface running on port `{Config.PORT}` |
| **LLM Inference** | 🌐 External API | `OpenRouter API` calls remote model (`{Config.OPENROUTER_MODEL}`) |
""")

    # Event Handlers & Interactions
    process_btn.click(
        fn=process_documents_handler,
        inputs=[pdf_uploader, session_pipeline],
        outputs=[status_output, stats_markdown, session_pipeline]
    )

    ask_btn.click(
        fn=chat_handler,
        inputs=[question_input, chatbot, top_k_slider, session_pipeline],
        outputs=[chatbot, question_input, sources_display]
    )

    question_input.submit(
        fn=chat_handler,
        inputs=[question_input, chatbot, top_k_slider, session_pipeline],
        outputs=[chatbot, question_input, sources_display]
    )

    clear_chat_btn.click(lambda: [], outputs=[chatbot])

    reset_btn.click(
        fn=reset_session_handler,
        inputs=[session_pipeline],
        outputs=[chatbot, stats_markdown, sources_display, status_output, session_pipeline]
    )

    # Sample Question Click Handlers
    sample_q1.click(lambda: "What is the minimum attendance percentage required?", outputs=[question_input])
    sample_q2.click(lambda: "What topics are included in Unit 3 of the syllabus?", outputs=[question_input])
    sample_q3.click(lambda: "What are the eligibility criteria for placement registration?", outputs=[question_input])

    # Prompt Lab Click Handler
    eval_prompt_btn.click(
        fn=prompt_lab_handler,
        inputs=[prompt_question_input, strategy_dropdown, top_k_slider, session_pipeline],
        outputs=[lab_answer_output, lab_eval_markdown, lab_prompt_display, lab_strategy_info]
    )

    # Benchmark Click Handler
    run_bench_btn.click(
        fn=run_benchmark_handler,
        inputs=[eval_strategy_select, session_pipeline],
        outputs=[benchmark_report_display]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=Config.PORT,
        share=False
    )
