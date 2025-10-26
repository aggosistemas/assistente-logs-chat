# ==============================================================
# 🤖 app/services/openai_client.py
# --------------------------------------------------------------
# Gera respostas técnicas com base em logs reais do Firestore.
# Inclui sumarização local automática e filtro semântico de contexto.
# ==============================================================

import os
from dotenv import load_dotenv
from openai import OpenAI
from app.utils.validation import is_prompt_valid
from app.services.firestore_context import obter_contexto_firestone
from app.utils.sanitize import sanitize_text

load_dotenv()

# ==============================================================
# 🔑 Inicialização do cliente OpenAI
# ==============================================================

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ Variável de ambiente OPENAI_API_KEY não encontrada.")

try:
    client = OpenAI(api_key=api_key)
    print("✅ [OpenAI] Cliente inicializado com sucesso.")
except Exception as e:
    raise RuntimeError(f"⚠️ Falha ao inicializar o cliente OpenAI: {e}")

# ==============================================================
# 🧩 Função auxiliar: sumarização local
# ==============================================================

def resumir_contexto_local(contexto: str, limite: int = 3000) -> str:
    """
    Reduz o tamanho do contexto antes de enviar à API da OpenAI.
    Mantém apenas os trechos técnicos mais relevantes.
    """
    if not contexto:
        return "Sem contexto técnico relevante disponível."

    linhas = contexto.split("\n")
    linhas_filtradas = []

    for linha in linhas:
        linha_lower = linha.lower()
        if any(p in linha_lower for p in ["erro", "falha", "exception", "timeout", "api", "warn", "sucesso", "mensagem"]):
            linhas_filtradas.append(linha)
        if len(linhas_filtradas) >= 50:
            break

    texto_final = "\n".join(linhas_filtradas) or contexto[:limite]
    texto_final = sanitize_text(texto_final)
    print(f"🧠 [Resumo local] Contexto reduzido para {len(texto_final)} caracteres.")
    return texto_final


# ==============================================================
# 🧠 Função principal: gerar resposta
# ==============================================================

def gerar_resposta(pergunta: str) -> str:
    """
    Gera resposta técnica com base em logs do Firestore.
    - Valida o contexto da pergunta.
    - Busca contexto real dos logs.
    - Aplica resumo local antes de enviar à OpenAI.
    """

    # 🛡️ 1. Validação semântica
    if not is_prompt_valid(pergunta):
        return (
            "🚫 Sua pergunta parece fora do contexto técnico. "
            "Por favor, pergunte algo relacionado a logs, falhas, "
            "monitoramento, sistemas corporativos ou incidentes."
        )

    if len(pergunta) > 1000:
        return "⚠️ A pergunta é muito longa. Resuma o problema e tente novamente."

    # 🔍 2. Buscar contexto técnico real do Firestore
    try:
        contexto_logs = obter_contexto_firestone(pergunta)
    except Exception as e:
        print(f"⚠️ [Firestore] Erro ao obter contexto: {e}")
        contexto_logs = "Não foi possível recuperar o contexto técnico neste momento."

    # 🧩 3. Reduzir o contexto localmente para otimizar custo e foco
    contexto_resumido = resumir_contexto_local(contexto_logs)

    # 🧱 4. Montar o prompt técnico
    prompt = f"""
    Você é um assistente técnico especializado em sustentação de sistemas corporativos.
    Use o contexto real de logs abaixo como base para responder à pergunta.

    🔹 CONTEXTO FIRESTORE (resumido):
    {contexto_resumido}

    🔹 PERGUNTA:
    {pergunta}

    Responda com foco técnico, descrevendo possíveis causas, sintomas e recomendações.
    Se possível, cite a origem dos logs (ex: [vida_nova_logs], [controle_auditoria_logs]).
    """

    # 🤖 5. Geração da resposta via OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente técnico de sustentação de sistemas, "
                        "com experiência em observabilidade, logs, análise de falhas e APIs corporativas. "
                        "Responda sempre com base nos dados do Firestore e evite generalizações."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.35,
            max_tokens=700,
        )

        resposta = response.choices[0].message.content.strip()
        print(f"✅ [OpenAI] Resposta gerada com sucesso ({len(resposta)} caracteres).")
        return resposta

    except Exception as e:
        print(f"❌ [OpenAI] Erro ao gerar resposta: {e}")
        return (
            "⚠️ Ocorreu um erro ao gerar a resposta. "
            "Verifique os logs de execução para mais detalhes."
        )
