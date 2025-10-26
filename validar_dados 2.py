from firebase_admin import credentials, firestore, initialize_app
import os

cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
initialize_app(cred)
db = firestore.client()

docs = list(db.collection("logs_poc_sistemas").stream())
print(f"📘 Total de logs no Firestore: {len(docs)}")

for doc in docs[:5]:
    data = doc.to_dict()
    print(f"\n🧩 Log ID: {doc.id}")
    print(f"Level: {data.get('level')}")
    print(f"Message: {data.get('message')[:120]}...")
