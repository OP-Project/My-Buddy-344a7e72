from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class InputQuery(BaseModel):
    """
    Represents a query input with a question and optional chat history.
    This model is used to structure the input for a query in the application.
    
    Attributes:
        query (str): The query being asked.
        chat_history (Optional[List[Dict[str, str]]]): Optional chat history to provide context for the question.
    """
    query: str = Field(..., description="The query being asked.")
    chat_history: Optional[List[Dict[str,Any]]] = Field(
        default=None, description="Optional chat history to provide context for the question."
    )

class ChatRequest(BaseModel):
    document_id: str
    query: str
    top_k: int = 3