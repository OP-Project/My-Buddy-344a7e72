from src.orchestrator.orchestrator import BuddyOrchestrator
from src.validation.input_schema import InputQuery, ChatRequest
from src.validation.output_schema import OutputQuery

from fastapi import FastAPI, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from src.orchestrator.agents.agent import root_agent

import os
import shutil
import requests
import platform
from io import BytesIO
import gradio as gr
from typing import List, Dict, Any
from markitdown import MarkItDown
from contextlib import asynccontextmanager

buddy_orchestrator = BuddyOrchestrator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Initializes the BuddyOrchestrator and cleans up resources on shutdown.
    """
    try:
        # Initialize session service and runner
        APP_NAME="test_agent_app"
        USER_ID="user1"
        SESSION_ID="1234"

        app.state.agent = root_agent
        app.state.session_service = InMemorySessionService()
        app.state.runner = Runner(
            agent=app.state.agent, 
            app_name=APP_NAME, 
            session_service= app.state.session_service,
            )
        session = await app.state.session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )

        # Ensure the ChromaDB directory exists
        chroma_db_path = "chroma_db"
        if not os.path.exists(chroma_db_path):
            os.makedirs(chroma_db_path)
        else:
            print(f"ChromaDB directory '{chroma_db_path}' already exists.")
        
        yield
    finally:
        # Cleanup resources if needed
        # For example, clear the ChromaDB directory on shutdown
        for filename in os.listdir(chroma_db_path):
            file_path = os.path.join(chroma_db_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

app = FastAPI(                                                      # http://127.0.0.1:8000/docs#
    title="Hey Buddy",
    version="0.1.0",
    description="A simple AI assistant for your daily tasks.",
    contact={
        "name": "Hey Buddy Team",
        "email": ""
        },
    lifespan=lifespan,
    )

origins = ["*"]
app.debug = platform.system() == "Windows"
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_runner(request: Request) -> Runner:
    return request.app.state.runner

def get_session_service(request: Request)-> InMemorySessionService:
    return request.app.state.session_service

@app.get("/buddy/status", summary="Root endpoint to check if the API is running.")
async def get_buddy_status():
    """
    Endpoint to check the status of the BuddyOrchestrator.
    Returns a simple message indicating the service is running.
    """
    message = "Buddy is running."
    return JSONResponse(content=message, status_code=200)

@app.post("/buddy/talk", response_model=OutputQuery, summary="Process a query and return an answer.")
async def buddy_talk_handler(query_data: InputQuery,
                             runner: Runner = Depends(get_runner),
                             session_service: InMemorySessionService = Depends(get_session_service)
                             ) -> OutputQuery:
    """
    Endpoint to process a query and return an answer.
    """
    # Add trackers, logs, Use HTTP requests, or any other logic here
    # To talk to gemini client
    # response = buddy_orchestrator.buddy_talk(query_data)

    # To talk to the agent
    response = await buddy_orchestrator.run_agent_interaction(query_data, runner, session_service)

    return response

@app.post("/upload-doc/") #, response_model=DocumentInfo, summary="Upload and process a single PDF file.")
async def upload_doc(file: UploadFile = File(...)):
    """
    This endpoint handles the uploading and processing of a single PDF file.
    - Extracts text from the PDF.
    - Splits text into chunks.
    - Generates embeddings for the chunks.
    - Creates and stores a FAISS vector index for the document.
    - Returns the processed document's info with its unique ID.
    """
    
    if not file:
        raise HTTPException(status_code=400, detail="No file was uploaded.")

    response = await buddy_orchestrator.document_ingestion(file)

    return response

@app.post("/chat-doc/")
async def chat_doc(request: ChatRequest) -> Dict[str, Any]:
    """
    Query a previously uploaded document.
    """
    if not request.document_id.strip():
        raise HTTPException(status_code=400, detail="document_id is required.")
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="query is required.")

    # Check document existence in ChromaDB
    doc_check = buddy_orchestrator.collection.get(
        where={"document_id": request.document_id},
        limit=1
    )
    if not doc_check["ids"]:
        raise HTTPException(status_code=404, detail=f"Document '{request.document_id}' not found.")

    # Embed query
    query_embedding = buddy_orchestrator.client["gemini-embedding-001"].embed_content(
        [request.query]
    )["embedding"][0]

    # Retrieve relevant chunks
    results = buddy_orchestrator.collection.query(
        query_embeddings=[query_embedding],
        n_results=request.top_k,
        where={"document_id": request.document_id}
    )
    if not results or results.get("documents") is None or not results["documents"]:
        raise HTTPException(status_code=404, detail="No relevant document chunks found for the given query.")
    retrieved_docs = results["documents"][0]

    if not results or results.get("metadatas") is None or not results["metadatas"]:
        raise HTTPException(status_code=404, detail="No relevant metadatas found for the given query.")
    retrieved_meta = results["metadatas"][0]

    # Build context
    context_text = "\n\n".join(retrieved_docs)

    # Generate answer with Gemini
    prompt = (
        f"You are a helpful assistant. Use the provided document excerpts to answer the question.\n\n"
        f"Document Context:\n{context_text}\n\n"
        f"Question: {request.query}\n\n"
        f"Answer:"
    )
    answer = buddy_orchestrator.client["gemini-1.5-flash"].ask(prompt).answer

    return {
        "query": request.query,
        "answer": answer,
        "sources": [
            {"chunk": doc, "metadata": meta}
            for doc, meta in zip(retrieved_docs, retrieved_meta)
        ]
    }

# -----------------------------
# Gradio ChatBot Logic
# -----------------------------

# def chatbot_gradio(user_input, chat_history):

#     # Call FastAPI endpoint
#     try:
#         response = requests.post(
#             "http://localhost:8000/buddy/talk",
#             json={"query": user_input, "chat_history": chat_history}
#         )
#         response.raise_for_status()
#         result = response.json()
#         answer = result["answer"]
#         return answer
#     except Exception as e:
#         error_msg = f"Error: {str(e)}"
#         return error_msg

# # -----------------------------
# # Gradio Interface
# # -----------------------------

# demo = gr.ChatInterface(
#     fn=chatbot_gradio,
#     type="messages",
#     chatbot=gr.Chatbot(height=525),
#     textbox=gr.Textbox(placeholder="Ask me any question", container=False, scale=7),
#     title="Buddy ChatBot",
#     description="Talk to Buddy! Powered by FastAPI.",
#     theme="ocean",
#     examples=["Hello", "Am I cool?", "Are tomatoes vegetables?"],
# )

# # -----------------------------
# # Mount Gradio into FastAPI
# # -----------------------------

# app = gr.mount_gradio_app(app, demo, path="/buddy/talk/ui") # http://localhost:8000/buddy/talk/ui/

# bye