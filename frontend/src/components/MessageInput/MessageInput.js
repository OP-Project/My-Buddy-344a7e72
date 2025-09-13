import { useState } from 'react';
import { FiSend, FiPaperclip } from 'react-icons/fi';
import styles from './MessageInput.module.css';

const MessageInput = ({ onSendMessage, chatMode, selectedDocument, onDocumentSelectClick, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className={styles.inputContainer}>
      {chatMode === 'document' && (
        <div className={styles.documentSelector}>
          <button 
            className={styles.addDocumentButton} 
            onClick={onDocumentSelectClick}
            disabled={disabled}
          >
            <FiPaperclip /> {selectedDocument ? 'Change Document' : 'Add Document'}
          </button>
          {selectedDocument && (
            <span className={styles.selectedDocument}>{selectedDocument.name}</span>
          )}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className={styles.inputForm}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={disabled ? "API is offline" : "Type your message here..."}
          className={styles.messageInput}
          disabled={disabled}
        />
        <button 
          type="submit" 
          className={styles.sendButton}
          disabled={disabled || !message.trim()}
        >
          <FiSend />
        </button>
      </form>
    </div>
  );
};

export default MessageInput;