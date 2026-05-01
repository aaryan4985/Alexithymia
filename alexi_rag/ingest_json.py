import os
import json
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
import chromadb
from config import EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, DB_PATH, JSON_DATA_PATH

def load_json_documents(data_path):
    documents = []
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print(f"Created {data_path}. Please scrape some novels first.")
        return documents

    for filename in os.listdir(data_path):
        if filename.endswith(".jsonl"):
            novel_name = filename.replace(".jsonl", "")
            file_path = os.path.join(data_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip(): continue
                        data = json.loads(line)
                        
                        chapter_title = data.get("chapter", "")
                        paragraphs = data.get("data", [])
                        text = "\n".join(paragraphs) if isinstance(paragraphs, list) else str(paragraphs)

                        metadata = {
                            "novel": novel_name,
                            "chapter": chapter_title,
                        }

                        doc = Document(text=text, metadata=metadata)
                        documents.append(doc)
                print(f"Loaded {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return documents

def ingest():
    print("Loading documents...")
    documents = load_json_documents(JSON_DATA_PATH)
    
    if not documents:
        print("No documents found to ingest.")
        return

    print("Setting up embedding model...")
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    Settings.embed_model = embed_model

    print("Setting up node parser...")
    node_parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    nodes = node_parser.get_nodes_from_documents(documents)

    print("Initializing ChromaDB...")
    db = chromadb.PersistentClient(path=DB_PATH)
    chroma_collection = db.get_or_create_collection("alexi_rag")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    print("Building index and generating embeddings...")
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True
    )
    
    print("Ingestion complete. Embeddings stored in ChromaDB.")

if __name__ == "__main__":
    ingest()
