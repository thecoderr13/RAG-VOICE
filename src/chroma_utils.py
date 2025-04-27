from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import logging

# Set up logging to app.log in the project root
logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), "..", "..", "app.log"), 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the embedding function
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Get the absolute path to the project root (RAG VOICE) and set persist_directory
# Since this file is in src/, go up two levels to RAG VOICE, then into data/chroma_db
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
persist_dir = os.path.join(project_root, "data", "chroma_db")
logging.info(f"Setting persist directory to: {persist_dir}")

# Ensure the directory exists and is writable
try:
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)
        logging.info(f"Created directory: {persist_dir}")
    # Test write access by creating a temporary file
    test_file = os.path.join(persist_dir, "test_write.txt")
    with open(test_file, "w") as f:
        f.write("Test")
    os.remove(test_file)
    logging.info(f"Confirmed write access to: {persist_dir}")
except Exception as e:
    logging.error(f"Failed to create or write to {persist_dir}: {str(e)}")
    raise

# Initialize Chroma vector store
vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embedding_function)

from typing import List
from langchain_core.documents import Document

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300, length_function=len)

# Document loading and splitting
def load_and_split_document(file_path: str) -> List[Document]:
    logging.info(f"Attempting to load and split document from: {file_path}")
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
        logging.info("Using PyPDFLoader for PDF file")
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
        logging.info("Using Docx2txtLoader for DOCX file")
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
        logging.info("Using UnstructuredHTMLLoader for HTML file")
    else:
        logging.error(f"Unsupported file type: {file_path}")
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    logging.info(f"Loaded {len(documents)} document(s) from {file_path}")
    split_docs = text_splitter.split_documents(documents)
    logging.info(f"Split into {len(split_docs)} chunks")
    return split_docs

# Indexing documents
def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:
        logging.info(f"Starting indexing process for file: {file_path} with file_id: {file_id}")
        splits = load_and_split_document(file_path)
        logging.info(f"Loaded and split {len(splits)} document chunks")

        # Add metadata to each split
        for split in splits:
            split.metadata['file_id'] = file_id
            logging.debug(f"Added metadata file_id={file_id} to chunk: {split.page_content[:50]}...")

        logging.info(f"Adding {len(splits)} documents to Chroma vector store")
        vectorstore.add_documents(splits)
        logging.info(f"Successfully indexed {len(splits)} documents to Chroma")
        logging.info(f"Chroma collection count after indexing: {vectorstore._collection.count()}")
        return True
    except Exception as e:
        logging.error(f"Error indexing document {file_path}: {str(e)}")
        return False

# Deleting documents
def delete_doc_from_chroma(file_id: int):
    try:
        logging.info(f"Attempting to delete documents with file_id: {file_id}")
        docs = vectorstore.get(where={"file_id": file_id})
        logging.info(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")

        vectorstore._collection.delete(where={"file_id": file_id})
        logging.info(f"Deleted all instances with file_id {file_id}")
        logging.info(f"Chroma collection count after deletion: {vectorstore._collection.count()}")

        return True
    except Exception as e:
        logging.error(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False