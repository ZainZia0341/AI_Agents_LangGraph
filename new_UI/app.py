import streamlit as st
import asyncio
from main import execute_workflow  # Import your main workflow function

# Set the page configuration to have a similar style
st.set_page_config(page_title="💬 Finance Chatbot with Agentic RAG", layout="wide")

# Sidebar content (Optional)
with st.sidebar:
    st.title('💬 Finance Chatbot')
    st.markdown("This chatbot answers financial-related queries based on your data.")


# Display the chat messages in reverse order (most recent messages at the bottom)
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to handle chatbot response generation
async def get_chat_response(user_input):
    response = await execute_workflow(user_input)  # Call your workflow for processing
    return response

# Create the chat input at the bottom
prompt = st.chat_input("Type your message here...", disabled=False)

# Handle user input and generate response
if prompt:
    # Add user message to chat history
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    # Display user message instantly
    with st.chat_message("user"):
        st.write(prompt)
    
    # Thinking spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Fetch the chatbot response asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(get_chat_response(prompt))
            
            # Append assistant's message
            st.session_state["messages"].append({"role": "assistant", "content": response["messages"][-1].content})
            
            # Display assistant's response
            st.write(response["messages"][-1].content)
