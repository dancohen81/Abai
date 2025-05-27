"""
rag_system.py

Retrieval Augmented Generation (RAG) system using ChromaDB.
Provides contextual knowledge to specialized agents.
"""

import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any

class RAGSystem:
    def __init__(self, collection_name: str = "music_knowledge", persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        # Ensure the model is downloaded or available. This might require an internet connection on first run.
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        print(f"RAGSystem initialized. Collection: {collection_name}, Persist Directory: {persist_directory}")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Adds documents to the ChromaDB collection.
        Documents should be a list of dictionaries, each with 'id', 'content', and 'metadata'.
        """
        ids = [doc["id"] for doc in documents]
        contents = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]

        self.collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to the collection.")

    def delete_documents(self, ids: List[str] = None, where: Dict[str, Any] = None, where_document: Dict[str, Any] = None):
        """
        Deletes documents from the ChromaDB collection.
        Documents can be deleted by ID, metadata filter, or document content filter.
        """
        self.collection.delete(ids=ids, where=where, where_document=where_document)
        print(f"Deleted documents from the collection.")

    def query(self, query_texts: List[str], n_results: int = 2) -> Dict[str, Any]:
        """
        Queries the ChromaDB collection for relevant documents.
        """
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results
        )
        return results

# Initialize the RAG system globally for the ableton_ai_controller
# Use a relative path for persist_directory within the ableton_ai_controller structure
rag_instance = RAGSystem(persist_directory="./ableton_ai_controller/chroma_db")

def retrieve_knowledge(query: str) -> str:
    """
    Retrieves contextual knowledge based on a query using the RAGSystem.
    """
    print(f"RAG: Retrieving knowledge for query: '{query}'")
    results = rag_instance.query(query_texts=[query], n_results=1) # Get top 1 result
    
    if results and results.get("documents") and results["documents"][0]:
        # Concatenate relevant documents into a single string
        knowledge_snippets = [doc for doc in results["documents"][0]]
        return "\n".join(knowledge_snippets)
    return ""

# Example usage (can be removed or adapted for testing)
if __name__ == "__main__":
    # Ensure the chroma_db directory exists for this example
    os.makedirs("./ableton_ai_controller/chroma_db", exist_ok=True)

    # Add some initial knowledge
    sample_knowledge = [
        {
            "id": "psytrance_bass_info",
            "content": "Psytrance rolling bass often uses a single note repeated in 16th or 8th note triplets, with a strong sub-bass and sidechain compression.",
            "metadata": {"genre": "psytrance", "element": "bass"}
        },
        {
            "id": "ableton_operator_uri",
            "content": "The URI for Ableton's Operator instrument is 'device/midi_instruments/operator.adg'.",
            "metadata": {"software": "ableton", "type": "instrument"}
        }
    ]
    rag_instance.add_documents(sample_knowledge)

    # Test retrieval
    retrieved = retrieve_knowledge("What is a psytrance bass?")
    print(f"\nRetrieved knowledge: {retrieved}")

    retrieved = retrieve_knowledge("Ableton Operator instrument URI")
    print(f"\nRetrieved knowledge: {retrieved}")
