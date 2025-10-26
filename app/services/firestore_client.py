# ==============================================================
# 🧠 app/services/firestore_context.py
# --------------------------------------------------------------
# Conecta ao Firestore e extrai contexto técnico dos logs
# para enriquecer o prompt enviado à OpenAI.
# ==============================================================

from google.cloud import firestore
from app.utils.sanitize import sanitize_text
import os

# ==============================================================
# 🔧 Conexão Firestore
# ==============================================================

def get_firestore_client():
    """Inicializa o cliente Firestore."""
    project_id = os.getenv("PROJECT_ID")
    return firestore.Client(project=project_id)


# ==============================================================
# 🧠 Função: obter contexto técnico dos logs
# ==============================================================

def obter_contexto_firestone(pergunta: str, limite: int = 8) -> str:
    """
    Busca contexto técnico real no Firestore com base na pergunta.
    Se não encontrar termos específicos, faz busca ampla em todas as coleções.
    """
    db = get_firestore_client()
    pergunta_lower = pergunta.lower()

    # Mapeamento semântico das coleções
    colecao_map = {
        "vida": "vida_nova_logs",
        "nova": "vida_nova_logs",
        "auditoria": "controle_auditoria_logs",
        "controle": "controle_auditoria_logs",
        "orcamento": "orcamento_contratacao_logs",
        "contratacao": "orcamento_contratacao_logs",
        "contratação": "orcamento_contratacao_logs",
        "viagem": "viagem_transmissao_logs",
        "transmissao": "viagem_transmissao_logs",
        "transmissão": "viagem_transmissao_logs",
        "erro": "controle_auditoria_logs",
        "falha": "controle_auditoria_logs",
        "api": "orcamento_contratacao_logs",
        "sistema": "vida_nova_logs",
    }

    # Escolhe coleção específica ou todas
    colecao = None
    for termo, nome_colecao in colecao_map.items():
        if termo in pergunta_lower:
            colecao = nome_colecao
            break

    colecoes = [colecao] if colecao else [
        "vida_nova_logs",
        "controle_auditoria_logs",
        "orcamento_contratacao_logs",
        "viagem_transmissao_logs"
    ]

    contexto = []

    for col in colecoes:
        try:
            print(f"📂 Lendo contexto Firestore: {col}")
            # Lê os últimos documentos sem depender de campo timestamp
            docs = db.collection(col).limit_to_last(limite).stream()
            for doc in docs:
                data = doc.to_dict()
                texto = " ".join([
                    str(v) for k, v in data.items()
                    if isinstance(v, str) and len(v) > 10
                ])
                texto = sanitize_text(texto)
                if texto:
                    contexto.append(f"[{col}] {texto}")
        except Exception as e:
            print(f"⚠️ Erro ao ler {col}: {e}")

    if not contexto:
        return "Nenhum log relevante foi encontrado nas coleções disponíveis."

    contexto_final = "\n".join(contexto)
    print(f"✅ Contexto Firestore: {len(contexto)} registros coletados.")
    return contexto_final[:7000]
