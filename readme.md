# Multi-Agent LLM Application Using LangGraph

This project leverages **LangGraph** to build a multi-agent network where each agent specializes in handling different types of user queries. The agents use various tools such as Tavily Search, Python REPL, Weather API, Alpha Vantage, and Eleven Labs to provide accurate and diverse responses.

## Overview

This project is designed as a **multi-agent LLM (Large Language Model)** application where each agent is responsible for handling specific tasks, such as:
- Searching the web for relevant information
- Fetching weather data
- Performing Python code execution
- Fetching financial data
- Converting text to speech

The agents are part of a **divide-and-conquer** approach where each specialized agent solves part of the problem and collaborates with other agents to generate the final response.

## Features

- **Retriever-Augmented Generation (RAG)**: Uses retrieval-based methods for grounded answers.
- **Multiple Tool Integration**: Utilizes Tavily Search, Python REPL, Alpha Vantage, Weather API, and Eleven Labs.
- **LangGraph Checkpointing**: Saves chat history during the conversation.
- **PostgreSQL Integration**: For long-term chat history storage.

## Setup

### Prerequisites

Make sure you have the following installed:
- Python 3.9+
- PostgreSQL (for chat history storage)
- API keys for services such as OpenAI, OpenWeatherMap, Alpha Vantage, and Eleven Labs

### Installing Dependencies

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/multi-agent-llm-app.git
    ```

2. Navigate to the project directory:

    ```bash
    cd multi-agent-llm-app
    ```

3. Install the required packages:

    ```bash
    pip install -U langchain langchain_openai langsmith pandas langgraph langchain_core elevenlabs
    ```

4. Set up your environment variables:

    ```bash
    export OPENAI_API_KEY="your-openai-api-key"
    export OPENWEATHER_API_KEY="your-openweather-api-key"
    export ALPHA_VANTAGE_KEY="your-alpha-vantage-api-key"
    export ELEVEN_LABS_KEY="your-eleven-labs-api-key"
    ```

5. Configure PostgreSQL:

    Set up a PostgreSQL database to store chat history.

    ```sql
    CREATE DATABASE chat_history;
    CREATE USER yourusername WITH PASSWORD 'yourpassword';
    GRANT ALL PRIVILEGES ON DATABASE chat_history TO yourusername;
    ```

    Modify `config.py` to include your PostgreSQL credentials.

## Project Structure

```plaintext
multi-agent-llm-app/
├── agents/
│   ├── rag_agent.py             # Handles retriever-augmented generation
│   ├── weather_agent.py         # Handles weather queries
│   ├── financial_agent.py       # Handles financial data queries
│   ├── code_execution_agent.py  # Handles Python code execution
│   ├── text2speech_agent.py     # Handles text-to-speech conversion
├── tools/
│   ├── tavily_search.py         # Tavily search integration
│   ├── openweather.py           # OpenWeatherMap API integration
│   ├── alpha_vantage.py         # Alpha Vantage API integration
│   └── python_repl.py           # Python REPL tool
├── utils/
│   ├── db.py                    # Database utility for chat history
├── config.py                    # Configuration for API keys and database
├── app.py                       # Main application logic
├── README.md                    # Project README
└── requirements.txt             # Python dependencies


