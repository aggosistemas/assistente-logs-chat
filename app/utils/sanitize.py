# ==============================================================
# 🧹 app/utils/sanitize.py
# --------------------------------------------------------------
# Funções auxiliares para limpeza e normalização de textos de log.
# ==============================================================

import re

def sanitize_text(text: str) -> str:
    """
    Remove caracteres especiais, espaços duplicados e informações sensíveis.
    É usada para preparar logs antes de enviar ao Firestore ou à OpenAI.
    """
    if not text:
        return ""

    # Remove quebras de linha e tabs
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # Remove sequências de caracteres não alfanuméricos
    text = re.sub(r"[^a-zA-Z0-9áéíóúãõçÁÉÍÓÚÂÊÔÛàèìòùÀÈÌÒÙüÜ.,;:_@%/()\- ]", "", text)

    # Remove e-mails e CPFs
    text = re.sub(r"\S+@\S+", "[email_removido]", text)
    text = re.sub(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", "[cpf_removido]", text)

    # Remove múltiplos espaços
    text = re.sub(r"\s+", " ", text).strip()

    return text
