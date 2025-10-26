# ==============================================================
# 🐳 Dockerfile - Assistente de Sustentação IA (FastAPI + Web)
# --------------------------------------------------------------
# Container unificado com backend (FastAPI) e frontend (HTML/CSS/JS)
# Deploy pronto para o Cloud Run com limpeza completa de cache.
# ==============================================================

# ===== Etapa base ==========================================================
FROM python:3.13-slim AS base

# Desativa buffer de logs, bytecode e cache do pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

# Cria diretório da aplicação
WORKDIR /app

# ===== Instala dependências =================================================
# Copia apenas o requirements.txt primeiro para otimizar cache de build
COPY requirements.txt .

# Instala dependências sem cache e limpa após instalação
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# ===== Copia o restante do código ===========================================
COPY . .

# ===== Verifica se diretório web existe =====================================
RUN mkdir -p /app/app/web

# ===== Exposição da porta padrão ============================================
EXPOSE 8080

# ===== Healthcheck opcional (executado pelo Cloud Run) ======================
HEALTHCHECK CMD curl --fail http://localhost:8080/healthz || exit 1

# ===== Comando padrão =======================================================
CMD ["uvicorn", "app.main_chat:app", "--host", "0.0.0.0", "--port", "8080"]
