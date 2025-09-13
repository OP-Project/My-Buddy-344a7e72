from src.validation.input_schema import InputQuery
from src.validation.output_schema import OutputQuery
from src.orchestrator.clients.gemini_client import GeminiClient

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import os

import chromadb
import uuid
from io import BytesIO
from google import genai

from typing import List, Dict, Any, Optional
from markitdown import MarkItDown
from fastapi import FastAPI, Request, Depends, UploadFile, File, Form, HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()

from src.config.logging import logger

class BuddyOrchestrator:
    """
    The BuddyOrchestrator class is responsible for managing the orchestration of tasks.
    It handles the initialization and execution of various components within the application.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initializes the BuddyOrchestrator with the given configuration.

        :param config: Configuration object containing necessary settings.
        """
        self.config = config
        MODEL_LIST = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-embedding-001"]
        self.client = {
            model: GeminiClient(
                gemini_api_key=os.getenv("GEMINI_API_KEY"),
                model_name=model
            ) for model in MODEL_LIST
        }
        self.aclient = {}
        self.genai_client = genai.Client()

        try:
            chroma_client = chromadb.PersistentClient(path="./chroma_db")
            # Get or create a collection to store document vectors
            self.collection = chroma_client.get_or_create_collection(name="documents_collection")
        except Exception as e:
            raise Exception(f"Failed to initialize ChromaDB: {e}. Make sure you have the required system dependencies for SQLite3.")
    
    async def document_ingestion(self, file: UploadFile) -> Dict[str, Any]:
        """
        Ingests a document, processes it, and stores it in the vector store.

        :param file: The document file to be ingested.
        :return: A dictionary containing the processed document's info.
        """
        if not file:
            raise HTTPException(status_code=400, detail="No file was uploaded.")

        content = await file.read()
        filename = file.filename

        # Extract text
        md = MarkItDown()
        result = md.convert(BytesIO(content))

        logger.info("Markitdown conversion Done")
        text = ""
        if result.title:
            text += f"# {result.title}\n\n"
        if result.text_content:
            text += result.text_content

        if not text:
            raise HTTPException(status_code=400, detail=f"Could not extract text from {filename}.")

        # Create a unique ID for the document
        document_id = str(uuid.uuid4())

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        text_chunks = text_splitter.split_text(text)

        logger.info("Document split into chunks")

        # Generate embeddings in one batch
        result = self.client["gemini-embedding-001"].embed_content(text_chunks)
        embeddings = result["embedding"]

        logger.info("Embeddings generated")

        # Unique IDs for chunks
        chunk_ids = [f"{document_id}_{i}" for i in range(len(text_chunks))]

        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=text_chunks,
            metadatas=[{"document_id": str(document_id), "filename": str(filename)} for _ in text_chunks],
            ids=chunk_ids
        )

        logger.info("Chunks stored in ChromaDB")

        return {"document_id": document_id}
    
    async def chat_with_document(self, query: str, document_id: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Answers a query based on the ingested document using the stored embeddings.

        :param query: The user's question.
        :param document_id: The ID of the document to search within.
        :param top_k: Number of relevant chunks to retrieve.
        :return: A dictionary containing the answer and sources.
        """
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        # Step 1: Embed the query
        query_embedding = self.client["gemini-embedding-001"].embed_content(
            text_chunks=[query],
            task_type="RETRIEVAL_QUERY"
        )["embedding"]

        # Step 2: Search relevant chunks in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"document_id": document_id}
        )

        if not results.get("documents") or results["documents"] is None or not results["documents"] or results["documents"][0] is None:
            raise HTTPException(status_code=404, detail="No relevant document chunks found for the given document_id.")

        retrieved_docs = results["documents"][0]

        if not results.get("metadatas") or results["metadatas"] is None or not results["metadatas"] or results["metadatas"][0] is None:
            raise HTTPException(status_code=404, detail="No relevant metadata found for the given document_id.")
        
        retrieved_meta = results["metadatas"][0]

        # Step 3: Build context
        context_text = "\n\n".join(retrieved_docs)

        # Step 4: Ask Gemini
        prompt = (
            f"You are a helpful assistant. Use the following document excerpts to answer the question.\n\n"
            f"Document Context:\n{context_text}\n\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )

        answer = self.client["gemini-1.5-flash"].ask(prompt).answer

        return {
            "query": query,
            "answer": answer,
            "sources": [
                {"chunk": doc, "metadata": meta}
                for doc, meta in zip(retrieved_docs, retrieved_meta)
            ]
        }

    async def buddy_talk(self, query_data: InputQuery) -> OutputQuery:
        """
        Processes a query and returns an answer.

        :param query: The query to be processed.
        :return: The answer to the query.
        """
        # Dummy logic — replace with your orchestrator / LLM call
        answer = f"You said: {query_data.query}"
        answer = self.client["gemini-1.5-flash"].ask_with_history(
            prompt=query_data.query,
            messages=query_data.chat_history or []
        )
        return OutputQuery(query=query_data.query, answer=answer.answer)
    
    async def run_agent_interaction(self, query_data: InputQuery, runner: Runner, session_service: InMemorySessionService):
        """
        Runs the agent interaction based on the provided query data. 
        Chat history is processed and the response is generated. 

        :param query_data: InputQuery object containing the query and chat history.
        :param runner: Runner instance to execute the agent.
        :param session_service: InMemorySessionService instance to manage session state.
        :return: OutputQuery object containing the query and the agent's response.
        """
        # Assuming runner and session_service are already initialized
        APP_NAME="test_agent_app"
        USER_ID="user1"
        SESSION_ID="1234"

        content = Content(role="user", parts=[Part(text=query_data.query)])
        logger.info(f"History: {query_data.chat_history}")
        logger.info(f"Running agent interaction with content: {content}")

        events = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content,
        )

        response = ""
        async for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                response = event.content.parts[0].text

        # Testing session events and state
        # Uncomment the following lines to explore session events
        # logger.info("========== Session Event Exploration ==========")
        # session = await session_service.get_session(
        #     app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        # )
        # logger.info(f"Type of session: {type(session)}")4
        # if session is not None:
        #     logger.info(f"Session State: {session.state}")
        #     logger.info(f"Session Events: {len(session.events)}")
        # else:
        #     logger.info("Session is None. Cannot display state or events.")
        # logger.info("===============================================")

        return OutputQuery(query=query_data.query, answer=f"This is a response from the agent interaction.\n{response}")
    
        

        

        