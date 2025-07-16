from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

def create_qa_chain(vectorstore, model_name="gpt-3.5-turbo", temperature=0):
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    
    qa_prompt_template = """You are a banking assistant that helps with questions about loan products, regulatory requirements, and internal policies.
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    If the context contains tables, use that information appropriately.
    
    Context: {context}
    
    Question: {question}
    
    Answer:"""
    
    qa_prompt = PromptTemplate(
        template=qa_prompt_template,
        input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": qa_prompt},
        return_source_documents=True
    )
    
    return qa_chain

def create_conversational_chain(vectorstore, model_name="gpt-3.5-turbo", temperature=0):
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    conv_prompt_template = """You are a banking assistant that helps with questions about loan products, regulatory requirements, and internal policies.
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    If the context contains tables, use that information appropriately.
    
    Chat History: {chat_history}
    Context: {context}
    
    Question: {question}
    
    Answer:"""
    
    conv_prompt = PromptTemplate(
        template=conv_prompt_template,
        input_variables=["chat_history", "context", "question"]
    )
    
    conv_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": conv_prompt},
        return_source_documents=True
    )
    
    return conv_chain

def create_loan_calculation_chain(vectorstore, model_name="gpt-4", temperature=0):
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    
    loan_prompt_template = """You are a banking assistant that specializes in loan calculations.
    Use the following pieces of context to answer the question about loan products, interest rates, or amortization.
    Make sure your calculations are accurate and comply with banking regulations.
    If you see tables with interest rates or loan terms, use that information for your calculations.
    
    Context: {context}
    
    Question: {question}
    
    Answer:"""
    
    loan_prompt = PromptTemplate(
        template=loan_prompt_template,
        input_variables=["context", "question"]
    )
    
    loan_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": loan_prompt},
        return_source_documents=True
    )
    
    return loan_chain

def create_regulatory_compliance_chain(vectorstore, model_name="gpt-4", temperature=0):
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    
    regulatory_prompt_template = """You are a banking compliance expert.
    Use the following pieces of context to answer the question about regulatory requirements and compliance.
    Always cite the specific regulation or policy document when providing compliance information.
    Be precise and accurate as incorrect regulatory information could lead to compliance violations.
    
    Context: {context}
    
    Question: {question}
    
    Answer:"""
    
    regulatory_prompt = PromptTemplate(
        template=regulatory_prompt_template,
        input_variables=["context", "question"]
    )
    
    regulatory_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": regulatory_prompt},
        return_source_documents=True
    )
    
    return regulatory_chain

def verify_answer_consistency(query, results, llm):
    if len(results) < 2:
        return results[0] if results else None
    
    verification_prompt = f"""
    I have received multiple answers to the same banking question. Please analyze these answers for consistency:
    
    Question: {query}
    
    Answer 1: {results[0]}
    Answer 2: {results[1]}
    
    Are these answers consistent? If not, which one is more accurate based on banking regulations and best practices?
    Provide the most accurate consolidated answer.
    """
    
    response = llm.invoke(verification_prompt)
    return response.content 