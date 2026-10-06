# Use lightweight Python 3.10 slim base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files & enable unbuffered stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Install system dependencies (build-essential, git for HuggingFace embeddings)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Pre-download sentence-transformer embedding model into image build stage
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')"

# Copy application code into container (excluding patterns in .dockerignore)
COPY . .

# Generate sample documents inside container
RUN python sample_documents/generate_samples.py

# Expose server port (default 7860 for Hugging Face Spaces)
EXPOSE 7860

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Launch application
CMD ["python", "app.py"]
