import os
from dotenv import load_dotenv
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from config import EMBED_MODEL, TOP_K, DB_PATH
from prompts import SYSTEM_PROMPT

load_dotenv()

class AlexiEngine:
    def __init__(self):
        # Setup Models
        self.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL)
        
        # Setup LLM - configure API key via .env
        api_key = os.getenv("GROQ_API_KEY", "")
        self.llm = Groq(
            model=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
            api_key=api_key,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.0
        )
        
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm
        
        # Load ChromaDB
        db = chromadb.PersistentClient(path=DB_PATH)
        chroma_collection = db.get_or_create_collection("alexi_rag")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        self.index = VectorStoreIndex.from_vector_store(
            vector_store,
        )

    def query(self, user_query, history_context="", filters_dict=None):
        llama_filters = None
        if filters_dict:
            filter_list = []
            for k, v in filters_dict.items():
                if v is not None:
                    filter_list.append(ExactMatchFilter(key=k, value=v))
            if filter_list:
                llama_filters = MetadataFilters(filters=filter_list)

        retriever = self.index.as_retriever(
            similarity_top_k=TOP_K,
            filters=llama_filters,
        )
        
        # Only embed the user's specific question for high-accuracy vector retrieval
        nodes = retriever.retrieve(user_query)
        
        if not nodes:
            return "This detail is not present in the retrieved material."
            
        # Manually assemble the context
        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        
        # Inject memory and context into the prompt
        prompt = f"Retrieved Context:\n{context_str}\n\n"
        if history_context:
            prompt += f"{history_context}\n"
        prompt += f"Current Question: {user_query}"
        
        # Generate response using our Groq LLM initialized with Alexi's persona
        response = self.llm.complete(prompt)
        response_text = str(response).strip()
        
        # Extra safety check in case the LLM generates a refusal that violates persona
        weak_keywords = ["not mentioned", "not present", "does not contain", "no information"]
        if any(kw in response_text.lower() for kw in weak_keywords) and len(response_text) < 100:
            return "This detail is not present in the retrieved material."
            
        return response_text
