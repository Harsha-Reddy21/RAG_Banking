import streamlit as st
import os
from dotenv import load_dotenv
from loaders import load_documents_from_directory, extract_tables_from_pdf, table_aware_splitter, custom_text_splitter
from vectorstore import VectorStoreManager
from chains import (
    create_qa_chain, 
    create_conversational_chain, 
    create_loan_calculation_chain, 
    create_regulatory_compliance_chain,
    verify_answer_consistency
)
from langchain_openai import ChatOpenAI

load_dotenv()

st.set_page_config(page_title="Banking Knowledge Assistant", layout="wide")

def initialize_vector_store(docs_directory="data/banking_docs"):
    if not os.path.exists(docs_directory):
        os.makedirs(docs_directory)
        st.info(f"Created documents directory at {docs_directory}. Please add your banking documents there.")
        return None, None
    
    documents = load_documents_from_directory(docs_directory)
    
    if not documents:
        st.info(f"No documents found in {docs_directory}. Please add your banking documents.")
        return None, None
    
    # Extract tables from PDFs
    tables_metadata = []
    for root, _, files in os.walk(docs_directory):
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                try:
                    tables_metadata.extend(extract_tables_from_pdf(file_path))
                except Exception as e:
                    st.error(f"Error extracting tables from {file_path}: {e}")
    
    # Process documents with table awareness if tables exist, otherwise use simple splitting
    if tables_metadata:
        processed_docs = table_aware_splitter(documents, tables_metadata)
    else:
        processed_docs = custom_text_splitter(documents)
    
    # Create vector store
    try:
        vector_manager = VectorStoreManager(embedding_model="openai")
        vectorstore = vector_manager.create_faiss_index(processed_docs)
        return vectorstore, vector_manager
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return None, None

def get_chain_by_query_type(query_type, vectorstore):
    if query_type == "General":
        return create_qa_chain(vectorstore)
    elif query_type == "Conversational":
        return create_conversational_chain(vectorstore)
    elif query_type == "Loan Calculation":
        return create_loan_calculation_chain(vectorstore)
    elif query_type == "Regulatory Compliance":
        return create_regulatory_compliance_chain(vectorstore)
    else:
        return create_qa_chain(vectorstore)

def main():
    st.title("Banking Knowledge Assistant")
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Document upload
        st.subheader("Document Upload")
        uploaded_file = st.file_uploader("Upload Banking Documents", type=["pdf", "csv", "txt"], accept_multiple_files=True)
        
        if uploaded_file:
            if not os.path.exists("data/banking_docs"):
                os.makedirs("data/banking_docs", exist_ok=True)
                
            for file in uploaded_file:
                with open(os.path.join("data/banking_docs", file.name), "wb") as f:
                    f.write(file.getbuffer())
            st.success(f"Uploaded {len(uploaded_file)} documents. Please refresh the app to process them.")
        
        # Query type selection
        st.subheader("Query Type")
        query_type = st.selectbox(
            "Select the type of query:",
            ["General", "Conversational", "Loan Calculation", "Regulatory Compliance"]
        )
        
        # Model selection
        st.subheader("Model Selection")
        model = st.selectbox(
            "Select LLM model:",
            ["gpt-3.5-turbo", "gpt-4"]
        )
        
        # Cost information
        st.subheader("Cost Information")
        if model == "gpt-3.5-turbo":
            st.info("Estimated cost: $0.002 per query")
        else:
            st.info("Estimated cost: $0.03 per query")
    
    # Main content area
    vectorstore, vector_manager = initialize_vector_store()
    
    if not vectorstore:
        st.warning("Please upload banking documents to get started.")
        
        # Display sample documents that are available
        st.subheader("Sample Documents Available")
        if os.path.exists("data/banking_docs"):
            files = os.listdir("data/banking_docs")
            if files:
                st.write("The following documents are available:")
                for file in files:
                    st.write(f"- {file}")
            else:
                st.write("No documents found in data/banking_docs directory.")
        return
    
    # Query input
    query = st.text_input("Ask a question about banking products, regulations, or policies:")
    
    if query:
        with st.spinner("Processing your query..."):
            try:
                chain = get_chain_by_query_type(query_type, vectorstore)
                
                if query_type == "Conversational":
                    result = chain({"question": query})
                    answer = result["answer"]
                    sources = result.get("source_documents", [])
                else:
                    result = chain({"query": query})
                    answer = result["result"]
                    sources = result.get("source_documents", [])
                
                # Store in chat history
                st.session_state.chat_history.append({"query": query, "answer": answer})
                
                # Display answer
                st.header("Answer")
                st.write(answer)
                
                # Display sources
                if sources:
                    st.subheader("Sources")
                    for i, source in enumerate(sources[:3]):
                        with st.expander(f"Source {i+1}"):
                            st.write(source.page_content[:500] + "..." if len(source.page_content) > 500 else source.page_content)
                            st.write(f"Source: {source.metadata.get('source', 'Unknown')}, Page: {source.metadata.get('page', 'Unknown')}")
            except Exception as e:
                st.error(f"Error processing query: {e}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.header("Chat History")
        for i, exchange in enumerate(st.session_state.chat_history[-5:]):
            st.subheader(f"Q: {exchange['query']}")
            st.write(f"A: {exchange['answer']}")

if __name__ == "__main__":
    main() 