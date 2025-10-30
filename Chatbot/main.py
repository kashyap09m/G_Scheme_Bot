import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# --- Add parent directory to system path ---
# This is crucial so that Python can find the 'rag_pipeline' module
# when you run this file directly.
# It adds the 'Chatbot/' directory to the list of places Python looks for modules.
# We go up one level ('..') from the current file's directory and add it.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# --- Import RAG Logic ---
# This import will now work because of the sys.path.append above.
# We import the single function that does all the work.
try:
    from rag_pipeline import get_rag_response, rag_chain
except ImportError:
    print("Error: Could not import 'rag_pipeline'.")
    print("Make sure 'rag_pipeline.py' is in the same directory.")
    sys.exit(1)

# --- Initialize FastAPI App ---
app = FastAPI(
    title="G Scheme Bot - Chatbot API",
    description="API to interface with an offline RAG pipeline for government schemes.",
    version="1.0.0"
)

# --- Configure CORS (Cross-Origin Resource Sharing) ---
# This is ESSENTIAL for your React frontend (running on http://localhost:3000)
# to be able to make requests to this server (running on http://localhost:8000).
origins = [
    "http://localhost:3000",  # The address of your React frontend
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allow specific origins
    allow_credentials=True,    # Allow cookies (if you use them)
    allow_methods=["*"],         # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],         # Allow all HTTP headers
)

# --- Pydantic Models ---
# This defines the expected structure of the JSON data
# that your API will receive in the request body.
class ChatQuery(BaseModel):
    query: str

# This defines the structure of the JSON data your API will send back.
class ChatResponse(BaseModel):
    response: str

# --- API Endpoints ---

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint to check if the server is alive and running.
    """
    return {"message": "G Scheme Bot - Chatbot API is running."}

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def handle_chat_query(chat_query: ChatQuery):
    """
    The main endpoint for the chatbot.
    
    - Receives a JSON with a "query" key (e.g., {"query": "What schemes for students?"})
    - Passes the query string to the RAG pipeline.
    - Returns a JSON with a "response" key (e.g., {"response": "..."})
    """
    print(f"Received query: {chat_query.query}")
    
    if rag_chain is None:
        # This checks the global 'rag_chain' variable from rag_pipeline.py
        print("Error: RAG chain is not initialized.")
        return {"response": "Sorry, the chatbot is not properly configured. Please check the server logs."}
    
    # Call the main RAG function
    response_text = get_rag_response(chat_query.query)
    
    print(f"Sending response: {response_text}")
    return {"response": response_text}

# --- Run the Server ---
if __name__ == "__main__":
    """
    This block allows you to run the server directly from your terminal
    by executing: python chatbot/main.py
    
    'uvicorn.run' starts the server.
    - "main:app": 'main' is the filename (main.py), 'app' is the FastAPI object.
    - host="0.0.0.0": Makes the server accessible on your local network.
    - port=8000: The port the server will run on (http://localhost:8000).
    - reload=True: The server will automatically restart if you save changes
                   to this file (useful for development).
    """
    print("Starting FastAPI server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)