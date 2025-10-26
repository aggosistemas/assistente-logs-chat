def is_prompt_valid(pergunta: str) -> bool:
    """Retorna True se a pergunta estiver dentro do contexto técnico."""
    if not pergunta or not pergunta.strip():
        return False

    pergunta_lower = pergunta.lower()

    temas_validos = [
        "erro", "falha", "log", "serviço", "transmissão", "aplicação",
        "monitoramento", "latência", "proposta", "contratação",
        "auditoria", "mensagem", "api", "timeout", "microserviço",
        "infraestrutura", "kubernetes", "pipeline", "deploy", "integração",
        "sistema", "banco de dados", "servidor", "rede", "backup",
        "recuperação", "alerta", "incidente", "suporte", "diagnóstico",
        "estado do sistema", "desempenho", "disponibilidade", "escalabilidade",
        "configuração", "segurança", "autenticação", "autorização", "criptografia",
        "microsserviços", "contêiner", "docker", "ci/cd", "logs de auditoria"
    ]

    blacklist = [
        "bolo", "carro", "namoro", "história", "receita", "música",
        "filme", "piada", "jogo", "vida pessoal", "conselho", "filosofia",
        "política", "religião", "esporte","cultura",
        "arte", "literatura", "história mundial", "ciência geral"
    ]

    if any(word in pergunta_lower for word in blacklist):
        return False

    return any(word in pergunta_lower for word in temas_validos)
