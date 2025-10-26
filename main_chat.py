# ==============================================================
# 🚀 main_chat.py
# --------------------------------------------------------------
# Ponto de entrada da API FastAPI do Assistente de Sustentação.
# Fornece endpoints de chat (/chat) e status operacional (/status).
# Inclui suporte completo a CORS para integração com o front-end
# hospedado no Cloud Run e execução local.
# ==============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat_routes import router as chat_router
from app.routes.status_routes import router as status_router

# ==============================================================
# ⚙️ Configuração principal da aplicação
# ==============================================================
app = FastAPI(
    title="Assistente de Sustentação",
    description="API para interação com logs operacionais e saúde dos sistemas.",
    version="1.0.0",
)

# ==============================================================
# 🌐 Configuração de CORS
# --------------------------------------------------------------
# Permite chamadas do front-end hospedado no Cloud Run,
# do bucket estático (HTML) e também execução local.
# ==============================================================
origins = [
    "http://127.0.0.1:5500",  # execução local com Live Server
    "http://localhost:5500",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "https://assistente-logs-chat-p62nlxrygq-uc.a.run.app",  # frontend hospedado no Cloud Run
    "https://storage.googleapis.com",  # caso o front seja publicado em bucket público
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # permite GET, POST, etc.
    allow_headers=["*"],   # permite headers customizados
)

# ==============================================================
# 🔗 Rotas principais
# ==============================================================
app.include_router(chat_router)
app.include_router(status_router)

# ==============================================================
# 🩺 Endpoint raiz de verificação
# ==============================================================
@app.get("/")
async def root():
    """
    Endpoint de verificação da API.
    Retorna status operacional e as rotas disponíveis.
    """
    return {
        "message": "Assistente de Sustentação ativo 🚀",
        "endpoints": ["/chat", "/status", "/docs", "/openapi.json"],
    }

# ==============================================================
# 🔎 Endpoint de diagnóstico rápido (opcional)
# --------------------------------------------------------------
# Pode ser usado para monitoramento via UptimeRobot ou Cloud Monitoring.
# ==============================================================
@app.get("/healthz")
async def health_check():
    """
    Endpoint leve para verificação de saúde do serviço.
    Retorna 200 OK se a API estiver operacional.
    """
    return {"status": "ok", "service": "assistente-logs-chat", "version": "1.0.0"}
