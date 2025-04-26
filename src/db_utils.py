from pymongo import MongoClient
from datetime import datetime


# MongoDB Connection Details
DB_URI = "mongodb+srv://vidhi:0fk1MdT1xxgVe9DY@cluster-rag.bsgynsv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-rag"  # Update this if connecting to a remote MongoDB
DB_NAME = "vidhi"  # No file extension needed

def get_db_connection():
    """Establishes a connection to MongoDB and returns the database object."""
    client = MongoClient(DB_URI)  # Connect to MongoDB
    db = client[DB_NAME]  # Get the database
    return db  # Return the database instance



def get_db_connection():
    """Establishes a connection to MongoDB and returns the database object."""
    client = MongoClient(DB_URI)
    db = client[DB_NAME]
    return db

def create_application_logs():
    """Ensures indexes exist for the application_logs collection in MongoDB."""
    db = get_db_connection()
    collection = db.application_logs

    # Creating an index on session_id for faster lookups
    collection.create_index("session_id")

    print("Indexes created for application_logs collection.")

def create_document_store():
    """Ensures indexes exist for the document_store collection in MongoDB."""
    db = get_db_connection()
    collection = db.document_store

    # Creating an index on filename to ensure unique file tracking
    collection.create_index("filename", unique=True)

    print("Indexes created for document_store collection.")


def get_db_connection():
    """Establishes a connection to MongoDB and returns the database object."""
    client = MongoClient(DB_URI)
    db = client[DB_NAME]
    return db

def insert_application_logs(session_id, user_query, gpt_response, model):
    """Inserts a log entry into the application_logs collection in MongoDB."""
    db = get_db_connection()
    db.application_logs.insert_one({
        "session_id": session_id,
        "user_query": user_query,
        "gpt_response": gpt_response,
        "model": model,
        "created_at": datetime.utcnow()  # MongoDB doesn't auto-set timestamps like SQL
    })
    print("Log inserted successfully.")

def get_chat_history(session_id):
    """Retrieves chat history for a session from MongoDB."""
    db = get_db_connection()
    logs = db.application_logs.find({"session_id": session_id}).sort("created_at", 1)  # Sort by timestamp ASC

    messages = []
    for log in logs:
        messages.extend([
            {"role": "human", "content": log["user_query"]},
            {"role": "ai", "content": log["gpt_response"]}
        ])
    
    return messages


def get_db_connection():
    """Establishes a connection to MongoDB and returns the database object."""
    client = MongoClient(DB_URI)
    db = client[DB_NAME]
    return db

def insert_document_record(filename):
    """Inserts a document record into the document_store collection."""
    db = get_db_connection()
    document = {
        "filename": filename,
        "upload_timestamp": datetime.utcnow()  # Manually adding timestamp
    }
    result = db.document_store.insert_one(document)  # Insert document into MongoDB
    return str(result.inserted_id)  # Return the inserted document's ObjectId as a string

def delete_document_record(file_id):
    """Deletes a document record from the document_store collection."""
    db = get_db_connection()
    result = db.document_store.delete_one({"_id": file_id})  # Delete document by its unique ID
    return result.deleted_count > 0  # Return True if a document was deleted

def get_all_documents():
    """Retrieves all document records from document_store, sorted by upload_timestamp."""
    db = get_db_connection()
    documents = db.document_store.find().sort("upload_timestamp", -1)  # Sort by latest uploads first

    return [{"id": str(doc["_id"]), "filename": doc["filename"], "upload_timestamp": doc["upload_timestamp"]}
            for doc in documents]


def initialize_database():
    """Ensures indexes exist for necessary collections in MongoDB."""
    db = get_db_connection()

    # Ensure application_logs indexes
    db.application_logs.create_index("session_id")  # Index for faster lookups by session_id

    # Ensure document_store indexes
    db.document_store.create_index("filename", unique=True)  # Ensure filenames are unique

    print("Database initialization complete: Indexes created.")

