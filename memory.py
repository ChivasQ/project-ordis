import os.path

import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
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
        text_to_save = f"Operator: {user_text}\nOrdis: {bot_text}"

        self.collection.add(
            documents=[text_to_save],
            metadatas=[{"type": "conversation"}],
            ids=[str(uuid.uuid4())]
        )
        print(f"💾 [Memory] Saved interaction.")

    def get_relevant_context(self, query, n_results=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if not results['documents'][0]:
            return ""

        context_str = "\n---\n".join(results['documents'][0])
        return context_str