# Agentic AI-Powered Finance Chatbot with RAG Workflow

## Introduction

This project leverages **LangGraph** to build an Agentic AI chatbot using the **Retrieval-Augmented Generation (RAG) tool**. The chatbot is designed to handle user queries using a multi-step agent workflow to retrieve and process data from CSV files. It utilizes Google’s Gemini 1.5 Pro for high-quality responses and is optimized for structured interactions, making it ideal for users who need contextual and data-driven answers.

---

## How to Run on Your PC

### Prerequisites

Ensure you have the following installed:
- Python 3.9 Tested Working Environment

### Steps to Set Up

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/ZainZia0341/AI_Agents_LangGraph
    ```

2. **Navigate to the Project Directory**:

    ```bash
    cd AI_Agents_LangGraph
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
    POSTGRES_SQL_URL="your-postgresql-url"
    ```

    Replace each placeholder with your actual credentials.

5. **Configure PostgreSQL**:

    - Create a PostgreSQL database and obtain the URL to access it.
    - Additionally, create a table in PostgreSQL for uploaded CSV file metadata using the following schema:

6. **Run the Application**:

    Launch the Streamlit app with the following command:

    ```bash
    streamlit run app.py
    ```

---

## Directory Structure

```plaintext
LangGraph_Agents_Nodes/
├── main.py                    # Main agent logic for handling queries
├── chroma_db_init.py          # Initializes and manages ChromaDB for vector storage
├── postgresSQL.py             # PostgreSQL interaction for conversation and file metadata
├── app.py                     # Streamlit UI for user interaction
├── uploaded_files/            # Directory for storing uploaded CSV files
├── .env                       # Environment variables (hidden in Git)
├── .gitignore                 # Git ignore file
├── README.md                  # Project README
├── requirements.txt           # Python dependencies
├── testing.ipynb              # Jupyter notebook for testing or experimentation
├── dummy_data_for_llm_testing.csv   # Sample data for LLM testing
...

## Working Flow of Agent in Action

The agent in this chatbot application follows a structured workflow to ensure relevant responses. Here’s how it works:

1. **Agent Decision**: The agent assesses the user’s question and determines the next step.
2. **Retrieve**: If additional information is required, the agent retrieves data from the uploaded CSV file.
3. **Rewrite**: If the retrieved data isn’t fully relevant, the agent refines the query to improve accuracy.
4. **Generate**: After confirming relevance, the agent generates a response.
5. **End**: The workflow concludes by delivering a tailored answer to the user.

This intelligent decision-making process enables the agent to adapt dynamically to various query types, ensuring responses are always based on accurate, context-driven information.

---

## Main Technologies Used in App

- **LLM Model**: Powered by Google’s Gemini 1.5 Pro for high-quality responses.
- **LangChain & LangGraph**: Manages the Agent workflow and state handling, allowing for seamless transitions and efficient query processing.
- **ChromaDB**: Vector storage for efficient data retrieval, enabling the agent to pull contextually relevant information.
- **PostgreSQL**: Used for storing conversation threads and file metadata, ensuring continuity across sessions.
- **Streamlit**: Provides an intuitive and interactive UI for users to engage with the chatbot, manage files, and view conversation history.


