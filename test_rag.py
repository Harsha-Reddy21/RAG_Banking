import os
import sys
from dotenv import load_dotenv
from loaders import load_pdf, extract_tables_from_pdf, table_aware_splitter
from vectorstore import VectorStoreManager
from chains import create_qa_chain, create_loan_calculation_chain
from cross_references import resolve_cross_references, enhance_retrieval_with_references
from compliance import verify_compliance, validate_interest_rate_ranges

load_dotenv()

def test_document_loading():
    print("Testing document loading...")
    if not os.path.exists("data"):
        os.makedirs("data")
        print("Created data directory. Please add test documents.")
        return False
    
    pdf_files = [f for f in os.listdir("data") if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in data directory.")
        return False
    
    test_file = os.path.join("data", pdf_files[0])
    documents = load_pdf(test_file)
    print(f"Loaded {len(documents)} pages from {pdf_files[0]}")
    
    tables = extract_tables_from_pdf(test_file)
    print(f"Extracted {len(tables)} tables from {pdf_files[0]}")
    
    return len(documents) > 0

def test_vector_store():
    print("\nTesting vector store...")
    if not os.path.exists("data"):
        print("Data directory not found.")
        return False
    
    pdf_files = [f for f in os.listdir("data") if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in data directory.")
        return False
    
    test_file = os.path.join("data", pdf_files[0])
    documents = load_pdf(test_file)
    tables = extract_tables_from_pdf(test_file)
    processed_docs = table_aware_splitter(documents, tables)
    
    vector_manager = VectorStoreManager(embedding_model="openai")
    vectorstore = vector_manager.create_faiss_index(processed_docs, index_name="test_index")
    
    print(f"Created vector store with {len(processed_docs)} documents")
    return vectorstore is not None

def test_query():
    print("\nTesting query...")
    if not os.path.exists("data"):
        print("Data directory not found.")
        return False
    
    pdf_files = [f for f in os.listdir("data") if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in data directory.")
        return False
    
    test_file = os.path.join("data", pdf_files[0])
    documents = load_pdf(test_file)
    tables = extract_tables_from_pdf(test_file)
    processed_docs = table_aware_splitter(documents, tables)
    
    # Resolve cross-references
    processed_docs = resolve_cross_references(processed_docs)
    
    vector_manager = VectorStoreManager(embedding_model="openai")
    vectorstore = vector_manager.create_faiss_index(processed_docs, index_name="test_index")
    
    chain = create_qa_chain(vectorstore)
    
    test_query = "What are the interest rates for personal loans?"
    print(f"Test query: {test_query}")
    
    try:
        result = chain({"query": test_query})
        print(f"Answer: {result['result'][:100]}...")
        return True
    except Exception as e:
        print(f"Error during query: {e}")
        return False

def test_loan_calculation():
    print("\nTesting loan calculation chain...")
    if not os.path.exists("data"):
        print("Data directory not found.")
        return False
    
    pdf_files = [f for f in os.listdir("data") if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in data directory.")
        return False
    
    test_file = os.path.join("data", pdf_files[0])
    documents = load_pdf(test_file)
    tables = extract_tables_from_pdf(test_file)
    processed_docs = table_aware_splitter(documents, tables)
    
    vector_manager = VectorStoreManager(embedding_model="openai")
    vectorstore = vector_manager.create_faiss_index(processed_docs, index_name="test_index")
    
    chain = create_loan_calculation_chain(vectorstore)
    
    test_query = "Calculate the monthly payment for a $200,000 mortgage at 4.5% for 30 years."
    print(f"Test query: {test_query}")
    
    try:
        result = chain({"query": test_query})
        print(f"Answer: {result['result'][:100]}...")
        
        # Verify compliance
        compliance_result = validate_interest_rate_ranges([4.5], 'mortgage')
        print(f"Compliance check: {compliance_result}")
        
        return True
    except Exception as e:
        print(f"Error during loan calculation: {e}")
        return False

def run_tests():
    tests = [
        test_document_loading,
        test_vector_store,
        test_query,
        test_loan_calculation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n=== Test Results ===")
    for i, result in enumerate(results):
        print(f"Test {i+1}: {'PASS' if result else 'FAIL'}")
    
    return all(results)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 