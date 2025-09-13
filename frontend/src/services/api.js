const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Check if the API is running
 * @returns {Promise<boolean>} True if API is running, false otherwise
 */
export const checkApiStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/buddy/status`);
    return response.ok;
  } catch (error) {
    console.error('API status check failed:', error);
    return false;
  }
};

/**
 * Send a message to the buddy API
 * @param {string} message - The message to send
 * @param {Array} chatHistory - Previous chat history
 * @returns {Promise<{query: string, answer: string}>} The response from the API
 */
export const sendMessage = async (message, chatHistory = []) => {
  try {
    const response = await fetch(`${API_BASE_URL}/buddy/talk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: message,
        chat_history: chatHistory.map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text
        }))
      }),
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

/**
 * Convert API response to chat message format
 * @param {Object} apiResponse - The API response
 * @param {string} apiResponse.query - The original query
 * @param {string} apiResponse.answer - The response answer
 * @returns {Array} Array of chat messages
 */
export const formatApiResponseToMessages = (apiResponse) => {
  return [
    {
      id: Date.now().toString(),
      text: apiResponse.query,
      sender: 'user',
      timestamp: new Date().toISOString()
    },
    {
      id: (Date.now() + 1).toString(),
      text: apiResponse.answer,
      sender: 'ai',
      timestamp: new Date().toISOString()
    }
  ];
};