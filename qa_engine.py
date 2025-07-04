from langchain_community.vectorstores import FAISS
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os

# Step 1: Convert AWS data (strings) into LangChain Documents
def create_documents(text_chunks):
    return [Document(page_content=chunk) for chunk in text_chunks]

# Step 2: Split into chunks
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_documents(documents)

# Step 3: Build FAISS vectorstore
def build_vectorstore(chunks, model_name='nomic-embed-text'):
    embeddings = OllamaEmbeddings(model=model_name)
    return FAISS.from_documents(chunks, embeddings)

# Step 4: Setup Retrieval QA
def setup_qa_chain(vectorstore, ollama_model='qwen:0.5b'):
    llm = Ollama(model=ollama_model)
    return RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# Step 5: Run query

def query_aws_knowledgebase(query, text_documents, embed_model='nomic-embed-text', llm_model='qwen:0.5b'):
    docs = create_documents(text_documents)
    chunks = split_documents(docs)
    vs = build_vectorstore(chunks, model_name=embed_model)
    qa_chain = setup_qa_chain(vs, ollama_model=llm_model)
    return qa_chain.run(query)

# Example usage:
# from aws_collector import collect_selected_services, format_data_for_llm
# services = ['EC2', 'IAM']
# data = collect_selected_services(services)
# docs = format_data_for_llm(data)
# print(query_aws_knowledgebase("How many EC2 instances are running?", docs))
