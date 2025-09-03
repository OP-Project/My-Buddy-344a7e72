class AskParams:
    """
    AskParams is a class that encapsulates parameters for asking questions to an AI model.
    It includes parameters such as the number of responses, frequency and presence penalties,
    """
    def __init__(self):
        """
        Initializes the AskParams instance with default values.
        This class is used to store parameters for asking questions to the AI model.
        The parameters include:
        - n: The number of responses to generate.
        - frequency_penalty: The penalty for using frequent tokens.
        - presence_penalty: The penalty for using new tokens.
        - temperature: The temperature for sampling.
        - top_p: The top probability for nucleus sampling.
        - stop: The stopping criteria for the model.
        - max_tokens: The maximum number of tokens to generate.
        - logprobs: Whether to return log probabilities of the generated tokens.
        """
        self.n = 1
        # self.frequency_penalty = 0.0
        # self.presence_penalty = 0.0
        self.temperature = 0.7
        # self.top_p = 1.0
        # self.stop = None
        # self.max_tokens = 1024
        # self.logprobs = False

    def __str__(self) -> str:
        """
        Returns a string representation of the AskParams instance.
        This method is useful for debugging and logging purposes.  
        It returns the string representation of the instance's dictionary.
        """
        return str(self.__dict__)