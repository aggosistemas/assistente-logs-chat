# ==============================================================
# 🐳 Dockerfile - Assistente de Sustentação IA (FastAPI + Frontend)
# ==============================================================

# Etapa base
FROM python:3.13-slim AS base

# Evita buffer de logs
ENV PYTHONUNBUFFERED=1

# Cria diretório de app
WORKDIR /app

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . .

# Expõe a porta padrão do FastAPI
EXPOSE 8080

# Define variável para Cloud Run
ENV PORT=8080

# Comando padrão do contêiner
CMD ["uvicorn", "main_chat:app", "--host", "0.0.0.0", "--port", "8080"]
