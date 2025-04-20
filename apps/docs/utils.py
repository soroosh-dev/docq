import os
import glob
import uuid
import chromadb
from typing import List
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from openai import OpenAI
import openai
from django.conf import settings
from .models import Document

# # ==== CONFIGURATION ====
# CHROMA_DIR = "./chroma_storage"
# TEXT_DIR = "./documents"
CHUNK_SIZE = 500  # characters

# # Set your OpenAI key
# openai.api_key = "YOUR_OPENAI_API_KEY"

# # Embedding function using OpenAI
# embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
#     api_key=openai.api_key,
#     model_name="text-embedding-3-small"
# )

# # Initialize Chroma client with persistence
# client = chromadb.Client(Settings(
#     chroma_db_impl="duckdb+parquet",
#     persist_directory=CHROMA_DIR
# ))

# collection = client.get_or_create_collection(
#     name="documents",
#     embedding_function=embedding_fn
# )

# # ==== UTILITIES ====

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# def ingest_documents():
#     """Reads .txt files, chunks them, and adds to Chroma if not already present."""
#     doc_files = glob.glob(os.path.join(TEXT_DIR, "*.txt"))
#     all_texts = []
#     all_metadatas = []
#     all_ids = []

#     for file_path in doc_files:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             text = f.read()
#             chunks = chunk_text(text)

#             for idx, chunk in enumerate(chunks):
#                 uid = str(uuid.uuid4())
#                 all_texts.append(chunk)
#                 all_metadatas.append({
#                     "source": os.path.basename(file_path),
#                     "chunk_index": idx
#                 })
#                 all_ids.append(uid)

#     if all_texts:
#         collection.add(documents=all_texts, metadatas=all_metadatas, ids=all_ids)
#         client.persist()  # Save to disk

# # ==== QUERY FUNCTION ====

# def get_relevant_chunks(query: str, top_k: int = 5) -> List[dict]:
#     results = collection.query(
#         query_texts=[query],
#         n_results=top_k
#     )

#     chunks = []
#     for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
#         chunks.append({
#             "text": doc,
#             "source": meta.get("source"),
#             "chunk_index": meta.get("chunk_index")
#         })

#     return chunks

# # ==== EXAMPLE ====

# if __name__ == "__main__":
#     ingest_documents()
#     query = "What is the main argument in the first chapter?"
#     chunks = get_relevant_chunks(query)
#     for c in chunks:
#         print(f"\n[{c['source']} - chunk {c['chunk_index']}]\n{c['text']}\n{'-' * 80}")


# Cursor
# Initialize persistent Chroma client
CHROMA_DB_PATH = os.path.join(settings.BASE_DIR, 'public', 'chroma_db')
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Get or create collection
try:
    collection = chroma_client.get_collection("documents")
except:
    collection = chroma_client.create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )

def query_documents(query_text: str, n_results: int = 5):
    """
    Query the Chroma DB for relevant document chunks based on the input query.
    
    Args:
        query_text (str): The query text to search for
        n_results (int): Number of results to return
        
    Returns:
        list: List of dictionaries containing:
            - text: The relevant text chunk
            - document: The Document object the chunk belongs to
            - distance: The similarity score
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        include=["metadatas", "documents", "distances"]
    )
    
    # Process results
    formatted_results = []
    for i in range(len(results['ids'][0])):
        doc_id = results['metadatas'][0][i]['document_id']
        try:
            document = Document.objects.get(id=doc_id)
            formatted_results.append({
                'text': results['documents'][0][i],
                'document': document,
                'distance': results['distances'][0][i]
            })
        except Document.DoesNotExist:
            continue
            
    return formatted_results
