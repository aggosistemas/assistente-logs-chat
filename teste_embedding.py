# ==============================================================
# 🔍 Teste de geração de Embedding com OpenAI (projeto assistente-logs-chat)
# ==============================================================

from dotenv import load_dotenv
from app.services.openai_client import generate_embedding
import os

print("🚀 Iniciando teste de embedding...")

# Carrega variáveis do .env (estão no mesmo projeto)
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERRO: Variável OPENAI_API_KEY não encontrada no .env.")
    exit(1)

try:
    texto_teste = "erro de transmissão de dados"
    embedding = generate_embedding(texto_teste)

    if embedding and len(embedding) > 0:
        print("✅ Embedding gerado com sucesso!")
        print(f"Dimensão do vetor: {len(embedding)}")
        print(f"Primeiros 10 valores: {embedding[:10]}")
    else:
        print("⚠️ Nenhum embedding retornado (lista vazia). Verifique a chave da API.")
except Exception as e:
    print(f"❌ Erro ao gerar embedding: {e}")
