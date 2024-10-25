import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define database connection string
DB_URI = os.getenv("Postgres_sql_URL")

def get_db_connection():
    """Establish and return a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DB_URI, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        return None

def fetch_conversation_by_thread(thread_id):
    """Fetch all checkpoints for a given thread (thread_id) from PostgreSQL."""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        query = """
        SELECT thread_id, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata
        FROM checkpoints
        WHERE thread_id = %s
        ORDER BY checkpoint_id ASC  -- Ensure 'checkpoint_id' is indexed for performance
        """
        cursor.execute(query, (thread_id,))
        checkpoints = cursor.fetchall()
        return checkpoints
    except Exception as e:
        print(f"Error fetching conversation: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def fetch_all_conversations():
    """Fetch all conversation threads from the database."""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        # Check if 'created_at' column exists
        query = "SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id DESC"  # Adjusted for simplicity
        cursor.execute(query)
        conversations = cursor.fetchall()
        return conversations
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_conversation(thread_id):
    """Delete a conversation and its messages from the database."""
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        # Delete checkpoints related to the thread_id
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = %s", (thread_id,))
        conn.commit()
        print(f"Conversation with thread_id {thread_id} has been deleted.")
    except Exception as e:
        print(f"Error deleting conversation: {e}")
    finally:
        cursor.close()
        conn.close()

def save_uploaded_file(file_name, file):
    """Save an uploaded file to the uploaded_files table in the database."""
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        file_content = file.read()  # Read the file content
        cursor.execute("INSERT INTO uploaded_files (file_name, file_content) VALUES (%s, %s)", (file_name, file_content))
        conn.commit()
        print(f"File {file_name} uploaded successfully.")
    except Exception as e:
        print(f"Error saving uploaded file: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_uploaded_file(file_name):
    """Delete an uploaded file from the uploaded_files table in the database."""
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uploaded_files WHERE file_name = %s", (file_name,))
        conn.commit()
        print(f"File {file_name} deleted successfully.")
    except Exception as e:
        print(f"Error deleting uploaded file: {e}")
    finally:
        cursor.close()
        conn.close()

def fetch_uploaded_files():
    """Fetch all uploaded files from the uploaded_files table in the database."""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT file_name FROM uploaded_files")
        files = cursor.fetchall()
        
        # Log the fetched files for debugging
        print(f"Fetched files: {files}")  # This will help you see what is being returned
        
        # If no files were found, return an empty list
        if not files:
            print("No files found in the database.")
            return []

        # Extract file names from the RealDictRow
        return [file['file_name'] for file in files]  # Use dictionary access

    except Exception as e:
        print(f"Error fetching uploaded files: {e}")
        return []  # Return an empty list on error
    finally:
        cursor.close()
        conn.close()

def fetch_uploaded_file_content(file_name):
    """Fetch the content of the uploaded file from the PostgreSQL database."""
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT file_content FROM uploaded_files WHERE file_name = %s", (file_name,))
        file_content = cursor.fetchone()
        if file_content:
            return file_content[0]  # Return the content (stored as BLOB/BYTEA in PostgreSQL)
        else:
            print(f"No content found for file: {file_name}")
            return None
    except Exception as e:
        print(f"Error fetching file content from database: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
