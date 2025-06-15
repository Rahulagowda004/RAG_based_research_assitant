FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create credentials directory
RUN mkdir -p /app/credentials

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY artifacts/Vector_databases/biology ./artifacts/Vector_databases/biology

# Copy application files
COPY app.py .

# Set the credentials directory as a volume
VOLUME /app/credentials

CMD ["streamlit", "run", "app.py"]

# Build Command:
# -----------------------------
# docker build -t rahula004/rag-research-assistant .
#
# Run Command:
# -----------------------------
# For Windows PowerShell:
# docker run -it -p 8501:8501 -e AZURE_OPENAI_ENDPOINT="<AZURE_OPENAI_ENDPOINT>" -e AZURE_OPENAI_API_KEY="<AZURE_OPENAI_API_KEY>" -e AZURE_OPENAI_API_VERSION="2024-12-01-preview" -e AZURE_OPENAI_LLM_DEPLOYMENT="gpt-4o" -e AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-small" -e FIRECRAWL_API_KEY="<FIRECRAWL_API_KEY>" rahula004/rag-research-assistant