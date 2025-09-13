import { useState, useEffect } from 'react';
import styles from './App.module.css';
import Sidebar from './components/Sidebar/Sidebar';
import ChatHeader from './components/ChatHeader/ChatHeader';
import MessageInput from './components/MessageInput/MessageInput';
import DocumentModal from './components/DocumentModal/DocumentModal';
import { sendMessage, checkApiStatus, formatApiResponseToMessages } from './services/api';

function App() {
  const [chatMode, setChatMode] = useState('direct');
  const [showDocumentModal, setShowDocumentModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [messages, setMessages] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [apiStatus, setApiStatus] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Check API status on component mount
  useEffect(() => {
    const verifyApi = async () => {
      const status = await checkApiStatus();
      setApiStatus(status);
    };
    verifyApi();
  }, []);

  const handleNewChat = () => {
    const newChatId = Date.now().toString();
    setActiveChatId(newChatId);
    setMessages([]);
    setChatHistory(prev => [...prev, { id: newChatId, title: 'New Chat', mode: chatMode }]);
  };

  const handleSendMessage = async (message) => {
    if (!apiStatus) {
      alert('API is not available. Please check if the backend is running.');
      return;
    }

    setIsLoading(true);
    
    try {
      // Add user message immediately
      const userMessage = {
        id: Date.now(),
        text: message,
        sender: 'user',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);
      
      // Format chat history for API
      const formattedHistory = messages.map(msg => ({
        text: msg.text,
        sender: msg.sender
      }));

      // Call API
      const response = await sendMessage(message, formattedHistory);
      
      // Format API response and update messages
      const newMessages = formatApiResponseToMessages(response);
      setMessages(prev => [...prev, newMessages[1]]);
    } catch (error) {
      console.error('Error in handleSendMessage:', error);
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, there was an error processing your message.',
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.app}>
      <Sidebar 
        chatHistory={chatHistory} 
        onNewChat={handleNewChat}
        activeChatId={activeChatId}
        setActiveChatId={setActiveChatId}
      />
      
      <div className={styles.mainContent}>
        <ChatHeader 
          chatMode={chatMode} 
          setChatMode={setChatMode}
          selectedDocument={selectedDocument}
          apiStatus={apiStatus}
        />
        
        <div className={styles.messagesContainer}>
          {messages.map(message => (
            <div key={message.id} className={`${styles.message} ${message.sender === 'user' ? styles.userMessage : styles.aiMessage}`}>
              <div className={styles.messageContent}>
                <div className={styles.messageSender}>
                  {message.sender === 'user' ? 'You' : 'AI Assistant'}
                </div>
                <div className={styles.messageText}>{message.text}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className={`${styles.message} ${styles.aiMessage}`}>
              <div className={styles.messageContent}>
                <div className={styles.messageSender}>AI Assistant</div>
                <div className={styles.messageText}>Thinking...</div>
              </div>
            </div>
          )}
        </div>
        
        <MessageInput 
          onSendMessage={handleSendMessage}
          chatMode={chatMode}
          selectedDocument={selectedDocument}
          onDocumentSelectClick={() => setShowDocumentModal(true)}
          disabled={!apiStatus || isLoading}
        />
      </div>
      
      {showDocumentModal && (
        <DocumentModal 
          onClose={() => setShowDocumentModal(false)}
          selectedDocument={selectedDocument}
          setSelectedDocument={setSelectedDocument}
        />
      )}
    </div>
  );
}

export default App;