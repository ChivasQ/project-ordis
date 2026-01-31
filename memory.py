import os.path

import chromadb
from chromadb.utils import embedding_functions
import uuid

os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

class OrdisMemory:
    def __init__(self, db_path="./ordis_memory"):
        self.client = chromadb.PersistentClient(path=db_path)

        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=os.path.abspath("models/all-MiniLM-L6-v2")
        )

        self.collection = self.client.get_or_create_collection(
            name="chat_history",
            embedding_function=self.embedding_fn
        )

    def save_interaction(self, user_text, bot_text):
        self.collection.add(
            documents=[f"Operator: {user_text}", f"Ordis: {bot_text}"],
            metadatas=[{"role": "user"}, {"role": "ordis"}],
            ids=[f"user_{uuid.uuid4()}", f"ordis_{uuid.uuid4()}"]
        )

    def get_relevant_context(self, query, n_results=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if not results['documents'][0]:
            return ""

        context_str = "\n---\n".join(results['documents'][0])
        return context_str