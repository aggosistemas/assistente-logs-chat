# ==============================================================
# 💬 app/routes/chat_routes.py
# --------------------------------------------------------------
# Endpoint principal do Assistente de Sustentação.
# Agora aceita /chat e /chat/, com logs estruturados
# compatíveis com Fluent Bit para observabilidade.
# ==============================================================

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from app.utils.validation import is_prompt_valid
from app.services.openai_client import gerar_resposta
import json
import hashlib

router = APIRouter(tags=["Chat Assistente"])

# ==============================================================
# 📥 Modelo de entrada
# ==============================================================
class ChatRequest(BaseModel):
    pergunta: str

# ==============================================================
# 📤 Modelo de saída (Swagger e compatibilidade)
# ==============================================================
class ChatResponse(BaseModel):
    pergunta: str
    resposta: str
    timestamp: str
    status: str

# ==============================================================
# 🧠 Função auxiliar - log estruturado para Fluent Bit
# ==============================================================
def log_event(pergunta: str, resposta: str, status: str, erro: str = None):
    evento = {
        "service": "assistente-logs-chat",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": status,
        "mensagem_curta": f"Chat executado com status {status}",
        "pergunta": pergunta,
        "resposta_tamanho": len(resposta) if resposta else 0,
        "hash_execucao": hashlib.sha256(pergunta.encode()).hexdigest()[:12],
    }

    if erro:
        evento["erro"] = str(erro)

    print(json.dumps(evento, ensure_ascii=False))


# ==============================================================
# 🤖 Endpoint principal - POST /chat e /chat/
# ==============================================================
@router.post("/chat", response_model=ChatResponse)
@router.post("/chat/", response_model=ChatResponse)
async def chat_endpoint(request: Request, body: ChatRequest):
    """
    Recebe uma pergunta e retorna uma resposta contextual do assistente técnico.
    Aceita POST /chat e /chat/ para compatibilidade com front-end e Postman.
    """
    pergunta = body.pergunta.strip()

    # 🔍 Validação semântica da pergunta
    if not is_prompt_valid(pergunta):
        log_event(pergunta, "", "blocked", "Pergunta fora de contexto técnico")
        raise HTTPException(
            status_code=400,
            detail="❌ Pergunta fora do contexto técnico. O assistente responde apenas sobre sistemas, logs e sustentação."
        )

    try:
        print(f"💬 Pergunta recebida: {pergunta}")
        resposta = gerar_resposta(pergunta)
        log_event(pergunta, resposta, "success")

        return {
            "pergunta": pergunta,
            "resposta": resposta,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "success",
        }

    except Exception as e:
        log_event(pergunta, "", "error", str(e))
        print(f"❌ Erro ao gerar resposta: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar resposta.")


# ==============================================================
# 🔎 GET auxiliar - /chat e /chat/
# ==============================================================
@router.get("/chat")
@router.get("/chat/")
async def chat_info():
    """
    Endpoint auxiliar para teste e verificação via navegador.
    """
    return {
        "message": "✅ Endpoint /chat ativo. Use POST para enviar perguntas.",
        "example": {"pergunta": "Sou gestor e quero um resumo da saúde técnica dos sistemas."},
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
