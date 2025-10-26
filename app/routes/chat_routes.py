# ==============================================================
# 💬 app/routes/chat_routes.py
# --------------------------------------------------------------
# Rota para interação generativa com o assistente de sustentação.
# ==============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.validation import is_prompt_valid  # ou validar_pergunta, conforme versão final
from app.services.openai_client import gerar_resposta

router = APIRouter(prefix="/chat", tags=["Chat Assistente"])

# ==============================================================
# 📥 Modelo de entrada
# ==============================================================
class ChatRequest(BaseModel):
    pergunta: str

# ==============================================================
# 📤 Modelo de saída (opcional, melhora documentação Swagger)
# ==============================================================
class ChatResponse(BaseModel):
    pergunta: str
    resposta: str

# ==============================================================
# 🧠 Endpoint principal
# ==============================================================
@router.post("/", response_model=ChatResponse)
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
    resposta = gerar_resposta(pergunta)
    print(f"✅ Resposta gerada ({len(resposta)} caracteres).")

    return {"pergunta": pergunta, "resposta": resposta}
