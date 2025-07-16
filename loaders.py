from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import pdfplumber
import pandas as pd
import os

def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def load_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    metadata = {"source": file_path}
    return [Document(page_content=text, metadata=metadata)]

def load_csv(file_path):
    loader = CSVLoader(file_path)
    documents = loader.load()
    return documents

def extract_tables_from_pdf(file_path):
    tables = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables.append({"table": df, "page": page.page_number})
    return tables

def custom_text_splitter(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def table_aware_splitter(documents, tables_metadata):
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    for doc in documents:
        if any(table.get("page") == doc.metadata.get("page") for table in tables_metadata):
            related_tables = [table for table in tables_metadata if table.get("page") == doc.metadata.get("page")]
            for table in related_tables:
                doc.metadata["contains_table"] = True
                doc.metadata["table_data"] = table["table"].to_dict()
        chunks.extend(text_splitter.split_documents([doc]))
    
    return chunks

def load_documents_from_directory(directory_path):
    documents = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.endswith(".pdf"):
                    documents.extend(load_pdf(file_path))
                elif file.endswith(".csv"):
                    documents.extend(load_csv(file_path))
                elif file.endswith(".txt"):
                    documents.extend(load_text_file(file_path))
                else:
                    # Skip other file types
                    print(f"Skipping unsupported file type: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return documents 