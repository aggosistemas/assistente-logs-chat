# ==============================================================
# 🧠 Função aprimorada: buscar contexto técnico real no Firestore
#    com filtro semântico baseado em embeddings
# ==============================================================

import math
from app.services.firestore_client import get_firestore_client
from app.utils.sanitize import sanitize_text
from firebase_admin import firestore

# --------------------------------------------------------------
# 🔧 Função auxiliar: calcular similaridade coseno
# --------------------------------------------------------------
def cosine_similarity(vec1, vec2):
    """Calcula similaridade coseno entre dois vetores numéricos."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    return dot / (norm1 * norm2) if norm1 and norm2 else 0.0


# --------------------------------------------------------------
# 🔍 Função principal
# --------------------------------------------------------------
def obter_contexto_firestone(pergunta: str, limite: int = 10) -> str:
    from app.services.openai_client import generate_embedding
    """
    Busca documentos no Firestore relacionados ao tema da pergunta.
    Utiliza embeddings para ranquear semanticamente os logs.
    Retorna um resumo textual consolidado para o modelo OpenAI.
    """
    db = get_firestore_client()
    pergunta_lower = pergunta.lower()

    # 🔎 Mapeamento expandido (mantido do seu código atual)
    colecao_map = {
        "vida nova": "vida_nova_logs",
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
        "serviço": "orcamento_contratacao_logs",
        "microserviço": "orcamento_contratacao_logs",
        "plataforma": "viagem_transmissao_logs",
    }

    # 🔍 Identifica qual coleção é mais provável
    colecao = None
    for termo, nome_colecao in colecao_map.items():
        if termo in pergunta_lower:
            colecao = nome_colecao
            break

    # 🔁 fallback multi-coleção
    if not colecao:
        print("⚠️ Nenhum termo específico encontrado, aplicando fallback multi-coleção.")
        colecoes = [
            "vida_nova_logs",
            "controle_auditoria_logs",
            "orcamento_contratacao_logs",
            "viagem_transmissao_logs",
        ]
    else:
        colecoes = [colecao]

    # ==============================================================
    # 🧠 Gera embedding da pergunta
    # ==============================================================
    pergunta_embedding = generate_embedding(pergunta)
    if not pergunta_embedding:
        print("⚠️ Não foi possível gerar embedding da pergunta.")
        return "Não foi possível gerar embedding da pergunta."

    # ==============================================================
    # 📥 Leitura e ranqueamento semântico dos documentos
    # ==============================================================
    candidatos = []
    for col in colecoes:
        try:
            print(f"📂 Buscando contexto em Firestore: coleção '{col}'")
            docs = (
                db.collection(col)
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limite * 3)  # lê mais registros para ranquear
                .stream()
            )

            for doc in docs:
                data = doc.to_dict()
                texto_log = " ".join([str(v) for v in data.values() if isinstance(v, str)])
                texto_log = sanitize_text(texto_log)
                if not texto_log:
                    continue

                # Gera embedding do log (modo leve)
                emb_log = generate_embedding(texto_log[:500])
                if not emb_log:
                    continue

                score = cosine_similarity(pergunta_embedding, emb_log)
                candidatos.append((score, col, texto_log))
        except Exception as e:
            print(f"⚠️ Erro ao ler coleção {col}: {e}")

    if not candidatos:
        return "Nenhum log relevante foi encontrado nas coleções disponíveis."

    # 🔢 Ordena por relevância
    candidatos.sort(key=lambda x: x[0], reverse=True)
    top = candidatos[:limite]

    # 🔗 Monta o contexto final consolidado
    contexto = [f"[{col}] {texto}" for _, col, texto in top]
    contexto_final = "\n".join(contexto)
    print(f"✅ Contexto coletado e ranqueado: {len(top)} registros de {len(colecoes)} coleções")
    return contexto_final[:6000]
