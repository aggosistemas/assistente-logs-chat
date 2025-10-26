import chromadb

# Caminho absoluto da base vetorial
CHROMA_PATH = "/Users/aggosistemas/Documents/Projetos/poc-assistente-logs/chroma_db"

client = chromadb.Client(
    settings=chromadb.config.Settings(persist_directory=CHROMA_PATH)
)

# Pega a coleção existente
collection = client.get_or_create_collection("logs_embeddings")

print(f"🧮 Total de embeddings salvos: {collection.count()}")

result = collection.peek()

for i, meta in enumerate(result['metadatas']):
    print(f"\n🧩 Embedding {i+1}")
    print(f"Metadata: {meta}")
