import os
import faiss
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.docstore import InMemoryDocstore
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredExcelLoader

# Embedding model configurations
model = "nomic-embed-text"
base_url = "http://localhost:11434"
embeddings = OllamaEmbeddings(model=model, base_url=base_url)
db_name = "Financial data"

# Getting a test embed query to get length of index dimension size
em = embeddings.embed_query("test")             
dim = len(em)
index = faiss.IndexFlatL2(dim)

vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
)

def create_vector_store():
    # Get file paths in mock data
    raw_files = []
    for root, dirs, files in os.walk("mock_data"):
        for file in files: 
            if file.endswith((".pdf", ".xlsx")):
                raw_files.append(os.path.join(root, file))

    # Load mock data into document chunks
    docs = []
    for file in raw_files:
        if file.endswith("pdf"):
            loader = PyMuPDFLoader(file)
            temp = loader.load()
            docs.extend(temp)
        elif file.endswith("xlsx"):
            loader = UnstructuredExcelLoader(file)
            temp = loader.load()
            docs.extend(temp)

    # Split document chunks into smaller chunks for vector stores
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)

    vector_store.add_documents(chunks)
    vector_store.save_local(db_name)


def load_vector_store():
    vs  = vector_store.load_local(db_name, embeddings, allow_dangerous_deserialization=True)
    return vs





