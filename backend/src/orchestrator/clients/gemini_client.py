from typing import List, Dict, Any, Optional
from src.validation.output_schema import ChatResponse
from src.config.app_settings import AskParams

from openai import OpenAI, OpenAIError
import time
import json

from src.config.logging import logger

chat_model_params = AskParams()  

class GeminiClient:
    """
    A client for interacting with the Gemini model.
    """

    def __init__(self, gemini_api_key, model_name="gemini-1.5-flash", embedding_model_name="gemini-embedding-001"):
        """
        Initializes the GeminiClient.

        Args:
            api_key: Your Gemini API key. If None, it attempts to get it from the environment.
        """

        self.client_gemini = OpenAI(
            api_key=gemini_api_key,  # Google Gemini API key
            base_url="https://generativelanguage.googleapis.com/v1beta/"  # Gemini base URL
        )
        self.model = model_name
        self.embedding_model = embedding_model_name

    def embed_content(self, text_chunks: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> Dict[str, Any]:
        """
        Generates embeddings for a list of text chunks.
        Note: The OpenAI Python client's standard `embeddings.create` does not directly support
        the `task_type` parameter in its signature. This is a feature of the native Google GenAI SDK.
        We will call the API in a loop for simplicity here.
        A more advanced implementation might use batching if the custom endpoint supports it.
        """
        try:
            # The 'openai' library's standard `create` method doesn't support lists of content for this endpoint structure.
            # We must loop through the chunks.
            embeddings = []
            import requests

            for chunk in text_chunks:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.embedding_model}:embedContent?key={self.client_gemini.api_key}"
                payload = {
                    "content": {"parts": [{"text": chunk}]},
                    "task_type": task_type
                }
                response = requests.post(url, json=payload)
                response.raise_for_status()
                embeddings.append(response.json()['embedding']['values'])
            return {'embedding': embeddings}
        except Exception as e:
            logger.info(f"Error creating embeddings with custom client: {e}")
            raise OpenAIError(f"Failed to create embeddings: {e}")

    def _calc_cost(self,data: Any) -> float:
        """
        Calculates the cost of the request.
        This is a placeholder function and should be implemented based on the actual cost calculation logic.
        """
        prompt_tokens= data['usage']['prompt_tokens']
        completion_tokens= data['usage']['completion_tokens']
        total_tokens= data['usage']['total_tokens']
        cost = 0.0
        # Example cost calculation logic (this is just a placeholder)

        return cost

    def _create_chat_completion(
            self,
            messages: List[Dict[str, str]],
            other_params: Optional[AskParams] = None
            ) -> ChatResponse:
        
        start_time = time.time()

        try:
            response = self.client_gemini.chat.completions.with_raw_response.create(
                model=self.model,
                messages=messages,
                **vars(other_params),
            )
            data = json.loads(response.content)
            answer = data['choices'][0]['message']['content'].strip()
            cost = self._calc_cost(data)
            response_time = time.time() - start_time
            return ChatResponse(answer=answer, cost=cost, time_taken=response_time)
        
        except Exception as e:
            logger.info(f"Error with Gemini request: {e}")
            raise OpenAIError


    def ask(
            self, 
            prompt: str = "What can you help me with?",
            system_message: str = "You are a helpful assistant.",
            # assistant_message: str = "Sure, I can help with that.",
            custom_params: Optional[AskParams] = None
            ) -> ChatResponse:
        """ 
        Asks the Gemini model a question.
        Args:
            prompt: The question to ask.
            system_message: The system message to set the context.
            assistant_message: The initial message from the assistant.
            custom_params: Additional parameters for the chat completion.
            Returns:
            The model's response as a ChatResponse object."""
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
            # {"role": "assistant", "content": assistant_message}
        ]
        return self._create_chat_completion(
            messages=messages,
            other_params=custom_params if custom_params else chat_model_params
        )


    def ask_with_history(
            self, 
            messages: List[Dict[str, Any]],
            prompt: str = "What can you help me with?",
            system_message: str = "You are a helpful assistant.",
            custom_params: Optional[AskParams] = None
            ) -> ChatResponse:
        
        prompt = prompt.strip() or "Ask me to ask anything."
        content = [{"type": "text", "text": prompt}]
        messages += [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        return self._create_chat_completion(
            messages=messages,
            other_params=custom_params if custom_params else chat_model_params
        )
