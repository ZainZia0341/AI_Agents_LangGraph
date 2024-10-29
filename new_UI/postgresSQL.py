import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from io import BytesIO
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

def save_uploaded_file(file, directory='./uploaded_files/'):
    """Save the uploaded file locally and store its metadata in the database."""
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Save the file locally
    file_path = os.path.join(directory, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    
    # Save metadata to the database (only file name and path)
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uploaded_files (file_name, file_path, created_at)
            VALUES (%s, %s, %s)
            """,
            (file.name, file_path, datetime.now())
        )
        conn.commit()
        print(f"File {file.name} saved locally and metadata stored in the database.")
    except Exception as e:
        print(f"Error saving uploaded file metadata: {e}")
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
    """Fetch all uploaded file metadata from the uploaded_files table in the database."""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT file_name, file_path FROM uploaded_files")
        files = cursor.fetchall()
        return files  # Returns a list of dictionaries with file_name and file_path
    except Exception as e:
        print(f"Error fetching uploaded files: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# def fetch_uploaded_file_content(file_name):
#     """Fetch the content of the uploaded file from the PostgreSQL database."""
#     conn = get_db_connection()
#     if conn is None:
#         return None

#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT file_content FROM uploaded_files WHERE file_name = %s", (file_name,))
#         result = cursor.fetchone()
#         if result and 'file_content' in result:
#             # Parse JSON to get binary data from 'data' array
#             file_content_json = result['file_content']
#             data = file_content_json.get('data', [])
#             file_content_bytes = bytes(data)  # Convert list of integers to bytes
#             return BytesIO(file_content_bytes)  # Return as BytesIO object for in-memory processing
#         else:
#             print(f"No content found for file: {file_name}")
#             return None
#     except Exception as e:
#         print(f"Error fetching file content from database: {e}")
#         return None
#     finally:
#         cursor.close()
#         conn.close()
