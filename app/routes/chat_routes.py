# ==============================================================
# 💬 app/routes/chat_routes.py
# --------------------------------------------------------------
# Rota para interação generativa com o assistente de sustentação.
# ==============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.validation import is_prompt_valid
from app.services.openai_client import gerar_resposta

router = APIRouter(prefix="/chat", tags=["Chat Assistente"])

# ==============================================================
# 📥 Modelo de entrada
# ==============================================================
class ChatRequest(BaseModel):
    pergunta: str

# ==============================================================
# 📤 Modelo de saída (melhora documentação Swagger)
# ==============================================================
class ChatResponse(BaseModel):
    pergunta: str
    resposta: str

# ==============================================================
# 🧠 Endpoint principal - POST /chat
# ==============================================================
@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Recebe uma pergunta e retorna uma resposta contextual do assistente técnico.
    O assistente responde apenas perguntas relacionadas a logs, falhas,
    infraestrutura, integrações e sistemas corporativos.
    """
    pergunta = request.pergunta.strip()

    # 🔍 Validação de contexto
    if not is_prompt_valid(pergunta):
        print(f"🚫 Pergunta bloqueada por contexto: {pergunta}")
        raise HTTPException(
            status_code=400,
            detail=(
                "❌ Pergunta fora do contexto técnico. "
                "O assistente responde apenas sobre sistemas, logs e sustentação."
            ),
        )

    print(f"💬 Pergunta recebida: {pergunta}")

    # 🧠 Geração de resposta via OpenAI
    try:
        resposta = gerar_resposta(pergunta)
        print(f"✅ Resposta gerada ({len(resposta)} caracteres).")
    except Exception as e:
        print(f"❌ Erro ao gerar resposta: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar resposta.")

    return {"pergunta": pergunta, "resposta": resposta}


# ==============================================================
# 🔎 GET auxiliar para diagnóstico - GET /chat
# ==============================================================
@router.get("")
async def chat_info():
    """
    Endpoint auxiliar para teste rápido de disponibilidade.
    """
    return {
        "message": "✅ Endpoint /chat ativo. Use POST para enviar perguntas.",
        "example": {"pergunta": "Sou gestor e quero um resumo da saúde técnica dos sistemas."},
    }
