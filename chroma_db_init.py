import os
# import chardet
# import fitz  # PyMuPDF for PDF processing
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from postgresSQL import fetch_uploaded_file_content
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
model_name = "intfloat/e5-large-v2"

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

# embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key = os.getenv("GOOGLE_API_KEY"))

hf_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
)

PERSIST_DIR = './chroma_db'
vectorstore = None

file_document_ids = {}  # Dictionary to track file names and their associated document IDs

def initialize_chroma(splits=None):
    global vectorstore
    if splits:
        print("Initializing Chroma with new documents...")
        vectorstore = Chroma.from_documents(documents=splits, persist_directory=PERSIST_DIR, embedding=hf_embeddings)
    elif os.path.exists(PERSIST_DIR) and not splits:
        print("Loading Chroma from the existing database...")
        vectorstore = Chroma(persist_directory=PERSIST_DIR, embedding_function=hf_embeddings)
    else:
        raise ValueError("No documents to initialize and Chroma database does not exist.")
    return vectorstore


from langchain_community.document_loaders.csv_loader import CSVLoader
def extract_text_from_pdf(file_path):
    loader = CSVLoader(file_path=file_path)
    data = loader.load()
    return data


def push_files_to_chroma(file_names, directory='./uploaded_files/'):
    global file_document_ids
    documents = []
    
    if os.path.exists(PERSIST_DIR):
        for file_name in file_names:
        # Fetch the file content from the database
            file_content = fetch_uploaded_file_content(file_name)
            if not file_content:
                continue  # Skip if no content is found
    
        # Convert the binary content to a file-like object (CSV Loader expects a file path)
        from io import BytesIO
        file_like_object = BytesIO(file_content)
        # Extract text from the file-like object (pass this to your CSVLoader)
        text = extract_text_from_pdf(file_like_object)  # Use file-like object instead of path
         # Create a new Document with combined text
        document = Document(page_content=text, metadata={"file_name": file_name})
        documents.append(document)
    
    else:
        for file_name in file_names:
            file_path = os.path.join(file_name)
            print("file_name ", file_path)
            print("file name " ,file_name.endswith(".csv"))
            print("file path " ,file_path.endswith(".csv"))

            if file_name.endswith(".csv"):
                # Extract text from the CSV file
                extracted_documents = extract_text_from_pdf(file_path)

                # Combine the page content of each document into a single string
                text = "\n".join([doc.page_content for doc in extracted_documents])
            # Create a new Document with combined text
            document = Document(page_content=text, metadata={"file_name": file_name})
            documents.append(document)

    # Initialize Chroma with new documents and store document IDs
    vectorstore = initialize_chroma(splits=documents)
    
    # Store document IDs based on metadata (filename)
    file_document_ids[file_name] = [doc.metadata.get('file_name') for doc in documents]
    
    return vectorstore



def save_uploaded_file(uploaded_file, directory='./uploaded_files/'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def list_uploaded_files(directory='./uploaded_files/'):
    return os.listdir(directory) if os.path.exists(directory) else []


def delete_uploaded_file(file_name, directory='./uploaded_files/'):
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    delete_vectors_from_chroma(file_name)


def delete_vectors_from_chroma(file_name):
    global file_document_ids
    vectorstore = initialize_chroma()

    if file_name in file_document_ids:
        document_ids = file_document_ids[file_name]
        vectorstore.delete(ids=document_ids)  # Delete the vectors associated with the file
        del file_document_ids[file_name]
        print(f"Deleted vectors for {file_name}")
    else:
        print(f"No vectors found for {file_name}")
