from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
import os
import hashlib

class VectorStoreManager:
    def __init__(self, embedding_model="openai"):
        if embedding_model == "openai":
            self.embeddings = OpenAIEmbeddings()
        else:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings()
        
        self.cache_dir = "embeddings_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def create_faiss_index(self, documents, index_name="banking_docs"):
        # Create FAISS index directly without pickling
        vectorstore = FAISS.from_documents(documents, self.embeddings)
        return vectorstore
    
    def create_chroma_index(self, documents, persist_directory="chroma_db"):
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=persist_directory
        )
        return vectorstore
    
    def hybrid_search(self, vectorstore, query, k=4):
        semantic_results = vectorstore.similarity_search(query, k=k)
        
        # Simple keyword filtering (could be enhanced with BM25 or other methods)
        keywords = query.lower().split()
        keyword_results = []
        
        for doc in vectorstore.docstore._dict.values():
            if any(keyword in doc.page_content.lower() for keyword in keywords):
                keyword_results.append(doc)
        
        # Combine and deduplicate results
        combined_results = semantic_results + keyword_results[:k]
        unique_results = []
        seen_ids = set()
        
        for doc in combined_results:
            if doc.metadata.get("id", id(doc)) not in seen_ids:
                seen_ids.add(doc.metadata.get("id", id(doc)))
                unique_results.append(doc)
        
        return unique_results[:k] 