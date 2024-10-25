# %% [markdown]
# # Agentic RAG for Finance Chatbot

# %%
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.utilities.python import PythonREPL
from langchain_core.tools import Tool
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader

# %%
# Load Environment Variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY")

# %% [markdown]
# # LLM Define

# %%
llm = ChatGoogleGenerativeAI(
    google_api_key = os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    # other params...
)

# %% [markdown]
# # CSV File Loader

# %%
file_path = (
    "./dummy_data_for_llm_testing.csv"
)

loader = CSVLoader(file_path=file_path)
data = loader.load()
# print(data)

# for d in data:
#     print(d)

# %% [markdown]
# # Embedding The data

# %%
model_name = "intfloat/e5-large-v2"

hf_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
)

print(hf_embeddings)

# %%
persist_directory='./chroma_db'

# %%
from langchain_chroma import Chroma

if persist_directory == "./chroma_db":
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=hf_embeddings)
else:
    vectorstore = Chroma.from_documents(documents=data, persist_directory=persist_directory, embedding=hf_embeddings)

# %%
from langchain_chroma import Chroma
vectorstore = Chroma.from_documents(documents=data, persist_directory=persist_directory, embedding=hf_embeddings)

# %%
retriever = vectorstore.as_retriever()

# %%
# retriever.invoke("what is my january budget of R&D")

# %%
# vectorAllData = vectorstore.get(include=['embeddings', 'documents', 'metadatas'])

# %%
# print(vectorAllData)

# %% [markdown]
# # retriever tool

# %%
from langchain.tools.retriever import create_retriever_tool

retriever_tool = create_retriever_tool(
    retriever,
    "Financial_data_csv",
    "This is the financial data of user in a csv format. If user want to know something about its financial data then search it and provide details to user.",
)

tools = [retriever_tool]

# %% [markdown]
# # Agent State
# We will define a graph.
# 
# A state object that it passes around to each node.
# 
# Our state will be a list of messages.
# 
# Each node in our graph will append to it.

# %%
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[Sequence[BaseMessage], add_messages]


# %% [markdown]
# # grade documents for Agentic RAG 

# %%
from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict

from langchain import hub
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
# from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field


from langgraph.prebuilt import tools_condition

### Edges


def grade_documents(state) -> Literal["generate", "rewrite"]:
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (messages): The current state

    Returns:
        str: A decision for whether the documents are relevant or not
    """

    print("---CHECK RELEVANCE---")

    # Data model
    class grade(BaseModel):
        """Binary score for relevance check."""

        binary_score: str = Field(description="Relevance score 'yes' or 'no'")

    # LLM
    # model = ChatOpenAI(temperature=0, model="gpt-4-0125-preview", streaming=True)

    # LLM with tool and validation
    llm_with_tool = llm.with_structured_output(grade)

    # Prompt
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.""",
        input_variables=["context", "question"],
    )

    # Chain
    chain = prompt | llm_with_tool

    messages = state["messages"]
    last_message = messages[-1]

    question = messages[0].content
    docs = last_message.content

    scored_result = chain.invoke({"question": question, "context": docs})

    score = scored_result.binary_score

    if score == "yes":
        print("---DECISION: DOCS RELEVANT---")
        return "generate"

    else:
        print("---DECISION: DOCS NOT RELEVANT---")
        print(score)
        return "rewrite"

# %%
def rewrite(state):
    """
    Transform the query to produce a better question.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with re-phrased question
    """

    print("---TRANSFORM QUERY---")
    messages = state["messages"]
    question = messages[0].content

    msg = [
        HumanMessage(
            content=f""" \n 
    Look at the input and try to reason about the underlying semantic intent / meaning. \n 
    Here is the initial question:
    \n ------- \n
    {question} 
    \n ------- \n
    Formulate an improved question: """,
        )
    ]

    # Grader
    # model = ChatOpenAI(temperature=0, model="gpt-4-0125-preview", streaming=True)
    response = llm.invoke(msg)
    return {"messages": [response]}


def generate(state):
    """
    Generate answer

    Args:
        state (messages): The current state

    Returns:
         dict: The updated state with re-phrased question
    """
    print("---GENERATE---")
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]

    docs = last_message.content

    # Prompt
    prompt = hub.pull("rlm/rag-prompt")

    # LLM
    # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, streaming=True)

    # Post-processing
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    response = rag_chain.invoke({"context": docs, "question": question})
    return {"messages": [response]}


# %% [markdown]
# # To see what prompt looks like 

# %%
from langchain import hub
print("*" * 20 + "Prompt[rlm/rag-prompt]" + "*" * 20)
prompt = hub.pull("rlm/rag-prompt").pretty_print()  # Show what the prompt looks like

# %% [markdown]
# # Nodes

# %%
def agent(state):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply end.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    print("---CALL AGENT---")
    messages = state["messages"]
    # model = ChatOpenAI(temperature=0, streaming=True, model="gpt-4-turbo")
    model = llm.bind_tools(tools)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

# %% [markdown]
# # Graph
# Start with an agent, call_model
# 
# Agent make a decision to call a function
# 
# If so, then action to call tool (retriever)
# 
# Then call agent with the tool output added to messages (state)

# %%
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes we will cycle between
workflow.add_node("agent", agent)  # agent
retrieve = ToolNode([retriever_tool])
workflow.add_node("retrieve", retrieve)  # retrieval
workflow.add_node("rewrite", rewrite)  # Re-writing the question
workflow.add_node(
    "generate", generate
)  # Generating a response after we know the documents are relevant
# Call agent node to decide to retrieve or not
workflow.add_edge(START, "agent")

# Decide whether to retrieve
workflow.add_conditional_edges(
    "agent",
    # Assess agent decision
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
)
workflow.add_edge("generate", END)
workflow.add_edge("rewrite", "agent")

# %% [markdown]
# # PostgresSQL with SupaBase.com

# %% [markdown]
# # Adding Memory to Agent Locally

# %%
# from langgraph.checkpoint.memory import MemorySaver

# memory = MemorySaver()
# # Compile
# graph = workflow.compile(checkpointer=memory)

# %% [markdown]
# # Display flow

# %%
# from IPython.display import Image, display

# try:
#     display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
# except Exception:
#     # This requires some extra dependencies and is optional
#     pass

# %% [markdown]
# # Using Agent 

# %%
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

DB_URI = os.getenv("Postgres_sql_URL")

# async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
#     await checkpointer.setup()
#     graph = workflow.compile(checkpointer=checkpointer)
#     config = {"configurable": {"thread_id": "1"}}
    
#     # Invoke the graph and capture the result
#     res = await graph.ainvoke(
#         {"messages": [("human", "Do you know my name?")]}, config
#     )
    
#     # Print the result to the console
#     print("Result from graph.ainvoke:")
#     print(res)
    
#     # Print checkpoint tuples
#     checkpoint_tuples = [c async for c in checkpointer.alist(config)]
#     print("Checkpoint tuples:")
#     for tuple_ in checkpoint_tuples:
#         print(tuple_)


# %%
async def drop_prepared_statements(conn):
    async with conn.cursor() as cursor:
        await cursor.execute("DEALLOCATE ALL;")

# async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
#     # Use the underlying psycopg connection to drop existing prepared statements
#     async with checkpointer.conn.transaction():
#         await drop_prepared_statements(checkpointer.conn)
    
#     await checkpointer.setup()
#     graph = workflow.compile(checkpointer=checkpointer)
#     config = {"configurable": {"thread_id": "4"}}
    
#     res = await graph.ainvoke(
#         {"messages": [("human", "What are Expenses in February for marketing department?")]}, config
#     )
    
#     messages = res.get("messages", [])
#     if messages:
#         all_contents = [msg.content for msg in messages]  # access content directly from object
#         print("All message contents:", all_contents)


async def execute_workflow(input_message):
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        # Use the underlying psycopg connection to drop existing prepared statements
        async with checkpointer.conn.transaction():
            await drop_prepared_statements(checkpointer.conn)
        await checkpointer.setup()
        graph = workflow.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "9"}}
        res = await graph.ainvoke({"messages": [("human", input_message)]}, config)
        return res



# %%



