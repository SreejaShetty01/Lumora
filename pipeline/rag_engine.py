import streamlit as st
import numpy as np
import os
import pickle

@st.cache_resource
def get_sentence_transformer(model_name='all-MiniLM-L6-v2'):
    # Lazy import to avoid loading it on application startup
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name)

class RAGEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model_name = model_name

    def get_model(self):
        return get_sentence_transformer(self.model_name)

    def create_vector_store(self, text, save_path):
        """Chunk text, embed, and save to FAISS index."""
        import faiss
        model = self.get_model()
        # Simple chunking by sentences or fixed length
        chunks = [text[i:i+500] for i in range(0, len(text), 400)]
        
        embeddings = model.encode(chunks)
        dimension = embeddings.shape[1]
        
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype('float32'))
        
        # Save index and chunks
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
            
        faiss.write_index(index, f"{save_path}.index")
        with open(f"{save_path}.chunks", "wb") as f:
            pickle.dump(chunks, f)
            
        return save_path

    def query(self, query, index_path):
        """Query the vector store for top-k chunks."""
        import faiss
        model = self.get_model()
        index = faiss.read_index(f"{index_path}.index")
        with open(f"{index_path}.chunks", "rb") as f:
            chunks = pickle.load(f)
            
        query_embedding = model.encode([query])
        D, I = index.search(np.array(query_embedding).astype('float32'), k=3)
        
        relevant_chunks = [chunks[i] for i in I[0] if i != -1]
        return "\n".join(relevant_chunks)
