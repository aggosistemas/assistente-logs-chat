# ==============================================================
# 🩺 app/routes/status_routes.py
# --------------------------------------------------------------
# Endpoint de status e saúde do Assistente de Sustentação.
# Ideal para monitoramento em Cloud Run e verificações executivas.
# ==============================================================

import os
import time
from fastapi import APIRouter
from google.cloud import firestore
from openai import OpenAI

router = APIRouter(prefix="/status", tags=["Status"])

# ==============================================================
# ⚙️ Funções utilitárias
# ==============================================================

def verificar_firestore() -> bool:
    """Verifica se a conexão com o Firestore está operacional."""
    try:
        db = firestore.Client(project=os.getenv("PROJECT_ID"))
        collections = [c.id for c in db.collections()]
        return len(collections) > 0
    except Exception as e:
        print(f"⚠️ [Firestore] Erro: {e}")
        return False


def verificar_openai() -> bool:
    """Verifica se o cliente OpenAI está funcional via token."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False

    try:
        client = OpenAI(api_key=api_key)
        # Faz uma chamada mínima para validar credenciais (sem custo relevante)
        client.models.list()
        return True
    except Exception as e:
        print(f"⚠️ [OpenAI] Erro: {e}")
        return False


# ==============================================================
# 🚀 Endpoint principal
# ==============================================================

@router.get("/")
def status_endpoint():
    """Retorna o status geral do sistema (Firestore + OpenAI + Env)."""
    start_time = time.time()

    firestore_ok = verificar_firestore()
    openai_ok = verificar_openai()

    status = {
        "status": "🟢 OK" if firestore_ok and openai_ok else "🟠 Parcial" if firestore_ok else "🔴 Indisponível",
        "firestore": "✅ Conectado" if firestore_ok else "❌ Falha na conexão",
        "openai": "✅ Autenticado" if openai_ok else "❌ Token inválido ou sem acesso",
        "project_id": os.getenv("PROJECT_ID", "❓ Não definido"),
        "env": os.getenv("ENVIRONMENT", "dev").upper(),
        "region": os.getenv("REGION", "us-central1"),
        "runtime": f"{time.time() - start_time:.2f}s",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Log amigável no console
    print(f"📊 [Status] {status}")

    return status
