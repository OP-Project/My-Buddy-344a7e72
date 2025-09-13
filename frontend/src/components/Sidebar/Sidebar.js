import { FiPlus } from 'react-icons/fi';
import styles from './Sidebar.module.css';

const Sidebar = ({ chatHistory, onNewChat, activeChatId, setActiveChatId }) => {
  return (
    <div className={styles.sidebar}>
      <button className={styles.newChatButton} onClick={onNewChat}>
        <FiPlus /> New Chat
      </button>
      
      <div className={styles.chatHistory}>
        {chatHistory.map(chat => (
          <div 
            key={chat.id} 
            className={`${styles.chatItem} ${activeChatId === chat.id ? styles.active : ''}`}
            onClick={() => setActiveChatId(chat.id)}
          >
            {chat.title} ({chat.mode})
          </div>
        ))}
      </div>
      
      <div className={styles.userProfile}>
        <div className={styles.profileIcon}>U</div>
        <span className={styles.userName}>User</span>
      </div>
    </div>
  );
};

export default Sidebar;