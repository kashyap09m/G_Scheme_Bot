import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import Ollama
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- 1. Define Constants ---

# Define the path to the CSV file, assuming it's in a sibling 'Data' folder
# os.path.dirname(__file__) gets the directory of the current file (Chatbot/)
# os.path.join(..., '..', 'Data', 'schemes.csv') goes up one level and then into Data/
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data', 'schemes.csv')

# Use a popular, small, and fast offline model for embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# The Ollama model you specified
LLM_MODEL = "gemma3:4B"


# --- 2. Define RAG Prompt Template ---
# This template is crucial for guiding the LLM
template = """
You are a helpful and polite assistant for 'G Scheme Bot'.
Your task is to answer questions about Indian government schemes based *only* on the context provided.
Do not use any external knowledge.
If the answer is not in the context, simply state: "I'm sorry, I don't have information about that specific scheme or query."

Context:
{context}

Question:
{question}

Helpful Answer:
"""

# --- 3. Function to Load and Process Data ---
def load_and_process_data():
    """
    Loads data from the CSV, combines relevant columns into a single text
    for embedding, and splits it into chunks.
    """
    print(f"Loading data from: {DATA_PATH}")
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"Error: schemes.csv not found at {DATA_PATH}")
        print("Please make sure the 'Data/schemes.csv' file exists.")
        return []

    # Fill any missing values with empty strings to prevent errors
    df = df.fillna("")

    # Combine all relevant columns into a single 'combined_text' column
    # This text will be embedded. We assume your CSV has these columns.
    # Adjust column names if they are different in your file.
    df['combined_text'] = (
        "Scheme Title: " + df['title'].astype(str) + ". " +
        "Description: " + df['description'].astype(str) + ". " +
        "Eligibility: " + df['eligibility'].astype(str) + ". " +
        "Benefits: " + df['benefits'].astype(str) + ". " +
        "State: " + df['state'].astype(str) + ". " +
        "Required Documents: " + df['required_documents'].astype(str)
    )

    # Use LangChain's DataFrameLoader
    loader = DataFrameLoader(df, page_content_column='combined_text')
    docs = loader.load()

    # Split the documents into smaller chunks for the vector store
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    
    print(f"Loaded and chunked {len(docs)} documents into {len(chunks)} chunks.")
    return chunks

# --- 4. Function to Set Up the RAG Chain ---
def setup_rag_chain():
    """
    Builds the entire RAG pipeline and returns it as a runnable chain.
    This function does all the heavy lifting:
    1. Loads data chunks
    2. Creates offline embeddings
    3. Initializes the FAISS vector store
    4. Initializes the Ollama LLM
    5. Defines the final chain
    """
    chunks = load_and_process_data()
    if not chunks:
        raise ValueError("No data loaded. RAG pipeline setup failed.")

    # 1. Embeddings: Offline model
    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # 2. Vector Store: FAISS (offline, in-memory)
    print("Creating FAISS vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    # 3. Retriever: Gets relevant documents from the vector store
    retriever = vector_store.as_retriever(search_kwargs={'k': 3}) # Get top 3 chunks

    # 4. LLM: Ollama
    print(f"Initializing Ollama with model: {LLM_MODEL}")
    llm = Ollama(model=LLM_MODEL)

    # 5. Prompt Template
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    # 6. Helper to format retrieved documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 7. Create the RAG Chain using LCEL (LangChain Expression Language)
    print("Assembling RAG chain...")
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("RAG pipeline setup complete.")
    return rag_chain

# --- 5. Global Setup ---
# This code runs ONCE when this module is imported by main.py
# It creates the 'rag_chain' object that will be used for all queries.
try:
    rag_chain = setup_rag_chain()
except Exception as e:
    print(f"FATAL ERROR: Could not set up RAG pipeline: {e}")
    rag_chain = None

# --- 6. Main Function for FastAPI ---
def get_rag_response(query: str) -> str:
    """
    The single function that FastAPI will call to get a response.
    """
    if rag_chain is None:
        return "Error: The chatbot pipeline is not initialized. Please check the server logs."
        
    print(f"Invoking RAG chain with query: {query}")
    try:
        # Use the globally-created chain to get a response
        response = rag_chain.invoke(query)
        return response
    except Exception as e:
        print(f"Error during RAG chain invocation: {e}")
        return "Sorry, I encountered an error while processing your request."

# --- Standalone Test ---
# You can run this file directly (python chatbot/rag_pipeline.py)
# to test if your RAG pipeline is working.
if __name__ == "__main__":
    if rag_chain:
        print("\n--- RAG Pipeline Test ---")
        print("Type 'exit' to quit.")
        while True:
            query = input("Ask a question about a scheme: ")
            if query.lower() == 'exit':
                break
            response = get_rag_response(query)
            print(f"\nResponse:\n{response}\n")
    else:
        print("RAG chain failed to initialize. Cannot run test.")