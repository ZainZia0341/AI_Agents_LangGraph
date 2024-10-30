# Agentic AI-Powered Finance Chatbot with RAG Workflow

## Introduction

This project leverages **LangGraph** to build an Agentic AI chatbot using **Retrieval-Augmented Generation (RAG)**. The chatbot is designed to handle user queries by using a multi-step agent workflow to retrieve and process data from CSV files. It uses Google’s Gemini 1.5 Pro for high-quality responses and is optimized for structured interactions. This application is ideal for users who want contextual and data-driven responses.

## How to Run on Your PC

### Prerequisites

Ensure you have the following installed:
- Python 3.9+
- PostgreSQL (for chat history storage)
- API keys for services like Google API for LLM and other credentials as needed.

### Steps to Set Up

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/your-username/finance-agent-chatbot.git
    ```

2. **Navigate to the Project Directory**:

    ```bash
    cd finance-agent-chatbot
    ```

3. **Install the Required Packages**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:

    Create a `.env` file in the root directory with the following content:

    ```plaintext
    LANGCHAIN_API_KEY="your-langchain-api-key"
    GOOGLE_API_KEY="your-google-api-key"
    Postgres_sql_URL="your-postgresql-url"
    ```

    Replace each placeholder with your actual credentials.

5. **Configure PostgreSQL**:

    Create a PostgreSQL database to store chat history and metadata.

    ```sql
    CREATE DATABASE chat_history;
    CREATE USER yourusername WITH PASSWORD 'yourpassword';
    GRANT ALL PRIVILEGES ON DATABASE chat_history TO yourusername;
    ```

6. **Run the Application**:

    Launch the Streamlit app with the following command:

    ```bash
    streamlit run app/app.py
    ```

## Directory Structure


LangGraph_Agents_Nodes/
├── agents/
│   ├── main.py                # Main agent logic for handling queries
├── tools/
│   ├── chroma_db_init.py      # Initializes and manages ChromaDB for vector storage
│   ├── postgresSQL.py         # PostgreSQL interaction for conversation and file metadata
├── app/
│   ├── app.py                 # Streamlit UI for user interaction
│   ├── app.py_new_UI          # Alternate or updated UI version (if applicable)
├── uploaded_files/            # Directory for storing uploaded CSV files
├── your_persist_directory/    # Directory for ChromaDB persistence (vector storage)
├── .env                       # Environment variables (hidden in Git)
├── .gitignore                 # Git ignore file
├── README.md                  # Project README
├── requirements.txt           # Python dependencies
├── testing.ipynb              # Jupyter notebook for testing or experimentation
├── dummy_data_for_llm_testing.csv   # Sample data for LLM testing
├── zain_financial_data.csv    # Example CSV file for financial data queries
└── Multi_Tool_Agent_ENV_3.9.0 # Virtual environment or environment configuration


# Working Flow of Agent in Action

The agent in this chatbot application follows a structured workflow to ensure relevant responses. Here’s how it works:

Agent Decision: The agent assesses the user’s question and determines the next step.
Retrieve: If additional information is required, the agent retrieves data from the uploaded CSV file.
Rewrite: If the retrieved data isn’t fully relevant, the agent refines the query to improve accuracy.
Generate: After confirming relevance, the agent generates a response.
End: The workflow concludes by delivering a tailored answer to the user.
This intelligent decision-making process allows the agent to adapt dynamically to different types of queries and ensures responses are always based on accurate, context-driven information.

# Main Technologies Used in App

LLM Model: Powered by Google’s Gemini 1.5 Pro for high-quality responses.

LangChain & LangGraph: Manages the Agent workflow and state handling, allowing for seamless transitions and efficient query processing.

ChromaDB: Vector storage for efficient data retrieval, enabling the agent to pull contextually relevant information.

PostgreSQL: Used for storing conversation threads and file metadata, ensuring continuity across sessions.

Streamlit: Provides an intuitive and interactive UI for users to engage with the chatbot, manage files, and view conversation history.
























🚀 Introducing the Agentic AI-Powered Chatbot with RAG Workflow 🚀

🔍 Built with Agentic AI, this chatbot project leverages advanced technologies to handle complex queries by retrieving and processing data from user-provided CSV files. The intelligent agent flow ensures every interaction is relevant and efficient.

⚙️ Agent Workflow:
Agent Decision: The agent assesses the user’s question and determines the next step.
Retrieve: When additional information is needed, it fetches data from the uploaded CSV file.
Rewrite: If the retrieved data isn’t fully relevant, the agent refines the query for improved accuracy.
Generate: After verifying relevance, the agent crafts an accurate response.
End: The workflow concludes with a targeted answer.
🌐 Key Features & Technologies:
CSV File Upload: Upload individual CSV files for each conversation, keeping data organized.
File Management: Easily delete files from the database when they’re no longer needed.
State-Persisting Conversations: Each conversation thread is independent, allowing for seamless interactions.
🛠️ Tech Stack:
LLM Model: Powered by Google’s Gemini 1.5 Pro for high-quality responses.
LangChain & LangGraph: Manages the Agent workflow and state handling.
ChromaDB: Vector storage for efficient data retrieval.
PostgreSQL: Handles conversation threads and file metadata for continuity.
Streamlit: Provides an intuitive and interactive UI for users to engage with the chatbot.
💡 Crafted for Intelligent Interactions: This chatbot combines RAG (Retrieval-Augmented Generation) with a flexible agentic workflow, making it adaptable and responsive to user data.

💼 Check out the code and explore more! [GitHub link here]

🔗 #AgenticAI #RAG #Chatbot #AI #MachineLearning #LangChain #LangGraph #ChromaDB #PostgreSQL #Streamlit