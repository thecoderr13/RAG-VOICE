from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

# Initialize the embedding function
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Use the correct persist_dir based on the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
persist_dir = os.path.join(project_root, "data", "chroma_db")
print(f"Checking persist directory: {persist_dir}")

# Load the existing vector store
vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embedding_function)

# Retrieve all documents and their embeddings
docs = vectorstore.get(include=["embeddings", "documents", "metadatas"])

# Print the number of documents and embeddings
print(f"Number of documents: {len(docs['documents'])}")
print(f"Number of embeddings: {len(docs['embeddings'])}")

# Example: Print the first document and its embedding
if docs['documents'] and docs['embeddings']:  # Check if both lists are non-empty
    print("First document:", docs['documents'][0])
    print("First embedding shape:", len(docs['embeddings'][0]))
    print("First metadata:", docs['metadatas'][0])
else:
    print("No documents or embeddings found in Chroma database")