# RAG Banking Knowledge Assistant

A Retrieval Augmented Generation (RAG) system for banking knowledge using LangChain and Streamlit. This system helps answer questions about loan products, regulatory requirements, and internal policies using a knowledge base of banking documents.

## Features

- Document processing for various banking document types (PDF, TXT, CSV)
- Table-aware chunking to preserve table context
- Cross-reference resolution for maintaining document references
- Specialized chains for different banking queries
- Compliance verification for regulatory requirements
- Cost-optimized implementation with multiple deployment options
- Streamlit user interface for easy interaction

## Architecture

```
                  +----------------------------+
                  |  User Query (LLM Prompt)   |
                  +-------------+--------------+
                                |
                                v
                     +----------+-----------+
                     |  Conversational Memory|
                     +----------+-----------+
                                |
                                v
+-------------------+  +----------------------+  +-------------------------+
| Document Loaders  |->| Text Splitters (custom)|->| Embeddings (OpenAI/HF) |
+-------------------+  +----------------------+  +-------------------------+
                                                         |
                                                         v
                                          +------------------------------+
                                          | Vector Store (Chroma/FAISS) |
                                          +------------------------------+
                                                         |
                                                         v
                                            +-------------------------+
                                            | RetrievalQA / CustomChain|
                                            +-------------------------+
                                                         |
                                                         v
                                            +------------------------+
                                            |  LLM (GPT-4, Claude)   |
                                            +------------------------+
                                                         |
                                                         v
                                             +---------------------+
                                             | Final Answer Output |
                                             +---------------------+
```

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Place your banking documents in the `data/banking_docs` directory
2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
3. Ask questions about banking products, regulations, or policies

## Sample Documents

The system comes with several sample banking documents in the `data/banking_docs` directory:
- `sample_loan_policy.txt`: Example loan policy guidelines
- `regulatory_compliance.txt`: Banking regulations and compliance information
- `mortgage_handbook.txt`: Mortgage lending procedures and guidelines
- `commercial_lending_guide.txt`: Commercial loan products and requirements
- `rate_sheet.csv`: Current interest rates for various loan products
- `mortgage_guide.pdf`: Comprehensive mortgage lending manual
- `banking_compliance_manual.txt`: Detailed regulatory compliance information

## Components

- `loaders.py`: Document loaders for different file types (PDF, TXT, CSV)
- `vectorstore.py`: Vector database and embedding functionality using FAISS/Chroma
- `chains.py`: LangChain chains for different query types (general, loan calculation, compliance)
- `compliance.py`: Regulatory compliance verification module
- `cross_references.py`: Cross-reference resolution for document citations
- `app.py`: Streamlit user interface
- `cost_analysis.md`: Detailed cost analysis and optimization guide
- `test_rag.py`: Test suite for RAG functionality

## Troubleshooting

If you encounter errors when running the application:

1. Make sure you have installed all required packages:
   ```
   pip install unstructured langchain-community
   ```

2. Verify that your `.env` file contains a valid OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

3. If you encounter pickle errors with thread locks, try restarting the application

## Cost Optimization

This implementation includes three deployment options:
1. Premium: GPT-4 + Pinecone + cloud hosting ($2,000-$5,000/month)
2. Optimized: Local LLMs + Chroma/FAISS + self-hosted ($200-$500/month)
3. Hybrid: Mixed approach with tiered model strategy ($500-$1,500/month)

See `cost_analysis.md` for detailed cost breakdown and ROI calculations.