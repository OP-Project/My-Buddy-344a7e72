from pydantic import BaseModel, Field
from typing import Optional, List

class OutputQuery(BaseModel):
    """
    Represents a query output with a question and an answer.
    This model is used to structure the output of a query in the application.
    Attributes:
        query (str): The query being asked.
        answer (str): The answer to the query.
    """
    query: str = Field(..., description="The query being asked.")
    answer: str = Field(..., description="The answer to the query.")

class ChatResponse(BaseModel):
    """
    Represents a response from the chat system.
    This model is used to structure the response returned by the chat system.

    Attributes:
        answer (str): The answer to the query.
        cost (Optional[float]): The cost of processing the query, if applicable.
        time_taken (Optional[float]): The time taken to process the query, if applicable.
    """
    answer: str = Field(..., description="The answer to the query.")
    cost: Optional[float] = Field(None, description="The cost of the query, if applicable.")
    time_taken: Optional[float] = Field(None, description="The time taken to process the query, if applicable.")