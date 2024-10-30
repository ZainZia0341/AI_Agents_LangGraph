import streamlit as st
import asyncio
from session_manager import generate_new_session_id
from main import execute_workflow, initialize_retriever_tool
from chroma_db_init import push_files_to_chroma, fetch_files_in_vector_db, delete_vectors_from_chroma
from postgresSQL import (
    fetch_conversation_by_thread,
    fetch_all_conversations,
    delete_conversation,
    save_uploaded_file,
    delete_uploaded_file,
    fetch_uploaded_files,
)

# Set page configuration
st.set_page_config(page_title="💬 Finance Chatbot with Agentic RAG", layout="wide")

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

vector_db_files = fetch_files_in_vector_db()

def update_key():
    st.session_state.uploader_key += 1

# Load conversations from PostgreSQL on page load
if 'conversations_loaded' not in st.session_state:
    conversations = fetch_all_conversations()
    st.session_state['conversations'] = {
        conv['thread_id']: fetch_conversation_by_thread(conv['thread_id']) for conv in conversations
    }
    st.session_state['conversations_loaded'] = True

# Automatically start a new conversation if none exists
if 'current_thread_id' not in st.session_state or st.session_state['current_thread_id'] is None:
    new_thread_id = generate_new_session_id()
    st.session_state['current_thread_id'] = new_thread_id
    st.session_state['conversations'][new_thread_id] = []

# Initialize uploaded files list and key for file uploader refresh
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []

if 'uploaded_files_db' not in st.session_state:
    st.session_state['uploaded_files_db'] = fetch_uploaded_files()

if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0  # Key for refreshing file uploader

def files_in_DataBase():
    st.session_state['uploaded_files_db'] = fetch_uploaded_files()
    return st.session_state['uploaded_files_db']

def uncheck():
    for file_name in st.session_state['selected_files']:
        st.session_state['selected_files'][file_name] = False

# Function to display selected files
def display_selected_files():
    st.subheader("Selected Files")
    if st.session_state['uploaded_files']:
        for i, file_name in enumerate(st.session_state['uploaded_files']):
            cols = st.columns([0.8, 0.2])
            with cols[0]:
                st.write(file_name)
            with cols[1]:
                if st.button("❌", key=f"delete_file_{i}"):
                    st.session_state['uploaded_files'].pop(i)

def display_vectordb_files():
    if vector_db_files:
            for i, file_name in enumerate(vector_db_files):
                cols = st.columns([0.8, 0.2])  # Create columns for file name and delete button
                with cols[0]:
                    st.write(file_name)  # Display file name
                with cols[1]:
                    # Delete button for each file
                    if st.button("❌", key=f"delete_vector_file_{i}"):
                        delete_vectors_from_chroma(file_name)  # Call the delete function
    else:
            st.write("No files currently in the vector database.")

# Sidebar content for managing conversations and files
with st.sidebar:
    st.title('💬 Finance Chatbot')
    st.markdown("This chatbot answers financial-related queries based on your data.")

    # Start a new conversation button
    if st.button("Start New Conversation"):
        new_thread_id = generate_new_session_id()
        st.session_state['current_thread_id'] = new_thread_id
        st.session_state['conversations'][new_thread_id] = []

    # List all conversations loaded from the database
    st.subheader("Conversations")
    keys_to_delete = []
    for thread_id in st.session_state['conversations'].keys():
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            if st.button(f"View Conversation {thread_id[:8]}", key=f"view_{thread_id}"):
                st.session_state['current_thread_id'] = thread_id
                st.session_state['conversations'][thread_id] = fetch_conversation_by_thread(thread_id)

        with cols[1]:
            if st.button("❌", key=f"delete_{thread_id}"):
                keys_to_delete.append(thread_id)

    # Perform deletions after iteration
    for thread_id in keys_to_delete:
        delete_conversation(thread_id)
        del st.session_state['conversations'][thread_id]

    # File Upload Section
    st.subheader("Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key=f"uploader_{st.session_state.uploader_key}")
    print("checking upload file ", uploaded_file)
    # Check if a new file is uploaded and add it to session state if not already there
    if uploaded_file is not None:
        file_name = uploaded_file.name
        if file_name not in st.session_state['uploaded_files']:
            st.session_state['uploaded_files'].append(file_name)
            st.session_state['uploaded_files_cleared'] = False

    # Display selected files
    display_selected_files()

    # Button to upload files to the database
    if st.button("Upload to Database",):
        update_key()
        for file_name in st.session_state['uploaded_files']:
            save_uploaded_file(uploaded_file)

        # Refresh the uploader key to reset file uploader widget
        st.session_state['uploaded_files'] = []
        st.session_state['uploaded_files_db'] = fetch_uploaded_files()
        display_selected_files()

    # Display uploaded files from the database
    st.subheader("Files in Database")
    # Create a dictionary to store the selected files (checkbox states)
    if 'selected_files' not in st.session_state:
        st.session_state['selected_files'] = {}

    # Loop through the files and add checkboxes
    if st.session_state['uploaded_files_db']:
        for i, file_row in enumerate(st.session_state['uploaded_files_db']):
            file_name = file_row['file_name']
            cols = st.columns([0.1, 0.7, 0.2])  # Added column for checkboxes
            with cols[0]:
                # Checkbox to select the file
                st.session_state['selected_files'][file_name] = st.checkbox("", key=f"select_file_{i}", label_visibility="collapsed")
            with cols[1]:
                st.write(file_name)
            with cols[2]:
                if st.button("❌", key=f"delete_db_file_{i}"):
                    delete_uploaded_file(file_name)
                    st.session_state['uploaded_files_db'].pop(i)
                    st.session_state['uploaded_files_db'] = fetch_uploaded_files()  # Refresh the list after deletion

    # Button to push selected files to RAG
    if st.button("Push to RAG"):
        selected_files = [file_name for file_name, selected in st.session_state['selected_files'].items() if selected]
        if selected_files:
            # Push the selected files to Chroma for embedding
            vectorstore = push_files_to_chroma(selected_files)
        # Here, add the logic to handle pushing these files to RAG
        # Reset the checkboxes (uncheck all)
        initialize_retriever_tool()
        uncheck()
        # Display files currently in the vector database under "Push to RAG"

    st.subheader("Files in Vector Database")    
    # Fetch the files in the vector database and display them with delete buttons
    vector_db_files = fetch_files_in_vector_db()  # Call the function to get file names

    display_vectordb_files()        

def display_conversation_streamlit(conversation_data):
    """Display conversation in Streamlit using human and assistant messages."""
    user_message = None
    final_assistant_message = None

    for checkpoint in conversation_data:
        metadata = checkpoint['metadata']
        writes = metadata.get("writes", {})

        if writes is not None:  # Add this check to ensure 'writes' is not None
            if '__start__' in writes:
                user_message = writes['__start__']['messages'][0][1]
                with st.chat_message("human"):
                    st.write("H", user_message)

            if 'generate' in writes:
                final_assistant_message = writes['generate']['messages'][0]
                with st.chat_message("assistant"):
                    st.write("W tool" ,final_assistant_message)
            elif 'agent' in writes:
                if writes['agent']['messages'][0]['kwargs'].get('content') is not "":
                    if 'messages' in writes['agent']:
                        final_assistant_message = writes['agent']['messages'][0]['kwargs'].get('content', 'No content available')
                        with st.chat_message("assistant"):
                            st.write("With tool" ,final_assistant_message)

# Load conversations from PostgreSQL on page load
if 'conversations_loaded' not in st.session_state:
    conversations = fetch_all_conversations()
    st.session_state['conversations'] = {
        conv['thread_id']: fetch_conversation_by_thread(conv['thread_id']) for conv in conversations
    }
    st.session_state['conversations_loaded'] = True

# Select a conversation to display
if 'current_thread_id' in st.session_state and st.session_state['current_thread_id']:
    thread_id = st.session_state['current_thread_id']
    st.subheader(f"Conversation: {thread_id[:8]}")
    conversation_data = st.session_state['conversations'].get(thread_id, [])
    display_conversation_streamlit(conversation_data)

# Handle new messages from the user
prompt = st.chat_input("Type your message here...")
if prompt:
    thread_id = st.session_state.get('current_thread_id', None)
    if thread_id:
        # Structure the user message
        user_message_structure = {
            "metadata": {
                "writes": {
                    "__start__": {
                        "messages": [["human", prompt]]
                    }
                }
            }
        }
        
        # Append the user's message structure to the conversation in session state
        st.session_state["conversations"][thread_id].append(user_message_structure)

        # Display the user's message immediately
        with st.chat_message("human"):
            st.write(prompt)

        # Fetch assistant's response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = asyncio.run(execute_workflow(prompt, thread_id))
                assistant_message_content = response["messages"][-1].content

                # Structure the assistant's message
                assistant_message_structure = {
                    "metadata": {
                        "writes": {
                            "agent": {
                                "messages": [
                                    {
                                        "kwargs": {
                                            "content": assistant_message_content if assistant_message_content else "No content available"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }

                # Append the assistant's message structure to the conversation in session state
                st.session_state["conversations"][thread_id].append(assistant_message_structure)

                # Display the assistant's message immediately
                st.write(assistant_message_content)