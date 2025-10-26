# ==============================================================
# 🐳 Dockerfile - Assistente de Sustentação IA (FastAPI + Frontend)
# --------------------------------------------------------------
# Backend (FastAPI) + Frontend (HTML estático) integrados
# Deploy pronto para o Cloud Run.
# ==============================================================

# ===== Etapa base ==========================================================
FROM python:3.13-slim AS base

# Desabilita buffer de logs e bytecode para execução limpa
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Define diretório padrão da aplicação
WORKDIR /app

# ===== Instala dependências =================================================
# Copia apenas o arquivo de dependências para otimizar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== Copia o restante do código ===========================================
COPY . .

# ===== Define variáveis de ambiente =========================================
ENV PORT=8080
EXPOSE 8080

# ===== Comando de inicialização =============================================
# Usa Uvicorn como servidor ASGI de produção (threaded e otimizado)
CMD ["uvicorn", "app.main_chat:app", "--host", "0.0.0.0", "--port", "8080"]
