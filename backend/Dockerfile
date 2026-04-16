FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Split into two layers: heavy ML deps first, then lighter ones
# Heavy ML packages rarely change — they stay cached
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch==2.1.0+cpu \
    sentence-transformers==2.7.0 \
    llama-index==0.10.68 \
    llama-index-vector-stores-pinecone==0.1.9 \
    llama-index-embeddings-huggingface==0.2.3 \
    mlflow==2.13.0

# Light deps change more often — cached separately
RUN pip install --no-cache-dir \
    fastapi==0.111.0 \
    uvicorn[standard]==0.29.0 \
    sqlalchemy==2.0.30 \
    alembic==1.13.1 \
    psycopg2-binary==2.9.9 \
    pydantic==2.7.1 \
    pydantic-settings==2.3.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    bcrypt==4.0.1 \
    python-multipart==0.0.9 \
    aiofiles==23.2.1 \
    celery==5.4.0 \
    redis==5.0.4 \
    openai==1.30.1 \
    langchain==0.2.1 \
    langchain-openai==0.1.8 \
    langchain-community==0.2.1 \
    pinecone==5.0.1 \
    onnxruntime==1.18.0 \
    websockets==12.0 \
    httpx==0.27.0 \
    python-dotenv==1.0.1 \
    reportlab==4.2.0 \
    pytest==8.2.0 \
    pytest-asyncio==0.23.7

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]