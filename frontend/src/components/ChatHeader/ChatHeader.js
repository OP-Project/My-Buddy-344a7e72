import styles from './ChatHeader.module.css';

const ChatHeader = ({ chatMode, setChatMode, selectedDocument, apiStatus }) => {
  return (
    <div className={styles.header}>
      <div className={styles.statusIndicator}>
        <span className={apiStatus ? styles.statusOnline : styles.statusOffline}>
          {apiStatus ? 'Online' : 'Offline'}
        </span>
      </div>
      <div className={styles.chatModeSelector}>
        <button
          className={`${styles.modeButton} ${chatMode === 'direct' ? styles.active : ''}`}
          onClick={() => setChatMode('direct')}
        >
          Direct Chat
        </button>
        <button
          className={`${styles.modeButton} ${chatMode === 'document' ? styles.active : ''}`}
          onClick={() => setChatMode('document')}
          disabled={!apiStatus}
        >
          Document Chat
        </button>
      </div>
      {chatMode === 'document' && selectedDocument && (
        <div className={styles.documentInfo}>
          Currently analyzing: <span className={styles.documentName}>{selectedDocument.name}</span>
        </div>
      )}
    </div>
  );
};

export default ChatHeader;