from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
from bson.objectid import ObjectId
# Load environment variables
load_dotenv()
DB_URI = os.getenv("DB_URI")
DB_NAME = os.getenv("DB_NAME")

# Set up logging to app.log in the project root
logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), "..", "..", "app.log"), 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Establishes a connection to MongoDB and returns the database object."""
    try:
        client = MongoClient(DB_URI)
        client.admin.command('ping')  # Test the connection
        return client[DB_NAME]
    except ConnectionFailure as e:
        logging.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

def initialize_database():
    """Ensures indexes exist for necessary collections in MongoDB."""
    db = get_db_connection()
    # Ensure application_logs indexes
    db.application_logs.create_index("session_id")  # Index for faster lookups by session_id
    logging.info("Indexes created for application_logs collection.")
    # Ensure document_store indexes
    db.document_store.create_index("filename", unique=True)  # Ensure filenames are unique
    logging.info("Indexes created for document_store collection.")
    logging.info("Database initialization complete.")

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
    logging.info("Log inserted successfully.")

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
    try:
        obj_id = ObjectId(file_id)  # Convert the string file_id to ObjectId
    except Exception as e:
        logging.error(f"Invalid file_id: {file_id}, error: {str(e)}")
        return False  # Return False if conversion fails (e.g., invalid ObjectId string)
    result = db.document_store.delete_one({"_id": obj_id})
    logging.info(f"Delete result for file_id {file_id}: deleted_count={result.deleted_count}")
    return result.deleted_count > 0  # Return True only if a document was actually deleted
    
def get_all_documents():
    """Retrieves all document records from document_store, sorted by upload_timestamp."""
    db = get_db_connection()
    documents = db.document_store.find().sort("upload_timestamp", -1)  # Sort by latest uploads first
    return [{"id": str(doc["_id"]), "filename": doc["filename"], "upload_timestamp": doc["upload_timestamp"]}
            for doc in documents]