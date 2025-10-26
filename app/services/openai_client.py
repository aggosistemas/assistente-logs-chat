# ==============================================================
# 🤖 app/services/openai_client.py
# --------------------------------------------------------------
# Gera respostas técnicas, de sustentação, de engenharia ou gerenciais
# com base em logs reais do Firestore.
# Inclui sumarização local, filtro semântico de contexto e
# adaptação automática de linguagem conforme o perfil da pergunta.
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
# 🧮 Função de geração de Embeddings
# ==============================================================

def generate_embedding(texto: str) -> list:
    """
    Gera o embedding semântico de um texto (log, pergunta ou contexto).
    Usa o modelo `text-embedding-3-small` para custo otimizado.
    Retorna uma lista de floats representando o vetor semântico.
    """
    if not texto or not isinstance(texto, str):
        print("⚠️ [OpenAI] Texto inválido para geração de embedding.")
        return []

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texto
        )
        embedding = response.data[0].embedding
        print(f"✅ [OpenAI] Embedding gerado ({len(embedding)} dimensões).")
        return embedding
    except Exception as e:
        print(f"❌ [OpenAI] Erro ao gerar embedding: {e}")
        return []

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
        if any(p in linha_lower for p in [
            "erro", "falha", "exception", "timeout", "api", "warn", "sucesso", "mensagem"
        ]):
            linhas_filtradas.append(linha)
        if len(linhas_filtradas) >= 50:
            break

    texto_final = "\n".join(linhas_filtradas) or contexto[:limite]
    texto_final = sanitize_text(texto_final)
    print(f"🧠 [Resumo local] Contexto reduzido para {len(texto_final)} caracteres.")
    return texto_final


# ==============================================================
# 🧠 Função principal: gerar resposta com perfis automáticos
# ==============================================================

def gerar_resposta(pergunta: str) -> str:
    """
    Gera resposta adaptada ao perfil do usuário:
    - Gestor/Diretor → visão gerencial e estratégica
    - Analista de Sustentação/SRE → visão operacional
    - Desenvolvedor → visão de engenharia de software
    - Técnico (default) → visão técnica genérica
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

    # 🧭 2. Detecção de perfil do usuário (gerencial, sustentação, engenharia, técnico)
    pergunta_lower = pergunta.lower()

    if any(p in pergunta_lower for p in [
        "gestor", "diretor", "gerente", "saúde técnica", "status",
        "resumo geral", "panorama", "visão executiva", "indicadores"
    ]):
        estilo_usuario = "gerencial"
        estilo_instrucao = (
            "Adote uma linguagem gerencial e analítica, "
            "fornecendo uma visão executiva da saúde técnica dos sistemas. "
            "Evite jargões de código e foque em indicadores, riscos, tendências "
            "e recomendações estratégicas para decisão."
        )

    elif any(p in pergunta_lower for p in [
        "analista", "sustentação", "suporte", "infraestrutura", "técnico", "sre"
    ]):
        estilo_usuario = "sustentação"
        estilo_instrucao = (
            "Adote uma linguagem técnica operacional, "
            "focando em logs, sintomas, causas prováveis e etapas de mitigação. "
            "Forneça instruções práticas para diagnóstico e correção, "
            "sem se aprofundar em código-fonte."
        )

    elif any(p in pergunta_lower for p in [
        "dev", "programador", "engenheiro", "desenvolvedor", "pleno", "sênior"
    ]):
        estilo_usuario = "engenharia"
        estilo_instrucao = (
            "Adote uma linguagem técnica avançada voltada a desenvolvedores, "
            "incluindo detalhes sobre classes, APIs, dependências, arquitetura e performance. "
            "Forneça insights sobre padrões de projeto, refatoração e boas práticas de código."
        )

    else:
        estilo_usuario = "técnico"
        estilo_instrucao = (
            "Adote uma linguagem técnica e detalhada, "
            "analisando causas, sintomas, logs e possíveis soluções operacionais. "
            "Inclua recomendações práticas e diagnósticos específicos."
        )

    print(f"🧩 Modo de resposta: {estilo_usuario.upper()}")

    # 🔍 3. Buscar contexto técnico real do Firestore
    try:
        contexto_logs = obter_contexto_firestone(pergunta)
    except Exception as e:
        print(f"⚠️ [Firestore] Erro ao obter contexto: {e}")
        contexto_logs = "Não foi possível recuperar o contexto técnico neste momento."

    # 🧩 4. Reduzir o contexto localmente para otimizar custo e foco
    contexto_resumido = resumir_contexto_local(contexto_logs)

    # 🧱 5. Montar o prompt adaptado
    prompt = f"""
    Você é um assistente especializado em sustentação e engenharia de sistemas corporativos.
    {estilo_instrucao}

    🔹 CONTEXTO FIRESTORE (resumido):
    {contexto_resumido}

    🔹 PERGUNTA:
    {pergunta}

    Responda de acordo com o estilo acima.
    """

    # 🤖 6. Geração da resposta via OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente técnico e gerencial de sustentação de sistemas. "
                        "Seu objetivo é transformar logs e métricas em insights claros e úteis. "
                        "Respeite o estilo pedido no prompt: "
                        "gerencial (executivo), sustentação (operacional), engenharia (dev) ou técnico (padrão)."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.35,
            max_tokens=900,
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
