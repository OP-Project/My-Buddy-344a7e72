import { useState } from 'react';
import { FiX, FiTrash2, FiCheck, FiUpload } from 'react-icons/fi';
import styles from './DocumentModal.module.css';

const DocumentModal = ({ onClose, selectedDocument, setSelectedDocument }) => {
  const [documents, setDocuments] = useState([
    { id: '1', name: 'Annual Report 2023.pdf', size: '2.4 MB' },
    { id: '2', name: 'Project Proposal.docx', size: '1.1 MB' },
    { id: '3', name: 'Research Paper.pdf', size: '3.2 MB' },
  ]);
  const [uploadProgress, setUploadProgress] = useState(null);

  const handleFileUpload = (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    if (documents.length + files.length > 5) {
      alert('You can upload a maximum of 5 documents');
      return;
    }

    // Simulate file upload progress
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return null;
        }
        return prev + 10;
      });
    }, 200);

    // Process each file
    Array.from(files).forEach((file, index) => {
      setTimeout(() => {
        const newDocument = {
          id: Date.now().toString() + index,
          name: file.name,
          size: formatFileSize(file.size),
          file: file // Store the actual file object
        };
        setDocuments(prev => [...prev, newDocument]);
      }, 1000);
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDeleteDocument = (id) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id));
    if (selectedDocument?.id === id) {
      setSelectedDocument(null);
    }
  };

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modal}>
        <div className={styles.modalHeader}>
          <h3>Manage Documents</h3>
          <button onClick={onClose} className={styles.closeButton}>
            <FiX />
          </button>
        </div>
        
        <div className={styles.documentList}>
          {documents.map(document => (
            <div key={document.id} className={styles.documentItem}>
              <div className={styles.documentInfo}>
                <span className={styles.documentName}>{document.name}</span>
                <span className={styles.documentSize}>{document.size}</span>
              </div>
              <div className={styles.documentActions}>
                <button 
                  onClick={() => setSelectedDocument(document)}
                  className={`${styles.selectButton} ${selectedDocument?.id === document.id ? styles.selected : ''}`}
                >
                  {selectedDocument?.id === document.id ? <FiCheck /> : 'Select'}
                </button>
                <button 
                  onClick={() => handleDeleteDocument(document.id)}
                  className={styles.deleteButton}
                >
                  <FiTrash2 />
                </button>
              </div>
            </div>
          ))}
        </div>
        
        {uploadProgress !== null && (
          <div className={styles.uploadProgress}>
            <div 
              className={styles.progressBar} 
              style={{ width: `${uploadProgress}%` }}
            ></div>
            <span>{uploadProgress}%</span>
          </div>
        )}
        
        <div className={styles.uploadSection}>
          <label htmlFor="file-upload" className={styles.uploadButton}>
            <FiUpload /> Upload Document
            <input
              id="file-upload"
              type="file"
              onChange={handleFileUpload}
              multiple
              accept=".pdf,.doc,.docx,.txt,.ppt,.pptx"
              style={{ display: 'none' }}
            />
          </label>
          <p className={styles.uploadHint}>
            Supported formats: PDF, DOC, DOCX, TXT, PPT, PPTX
            <br />
            Max 5 documents
          </p>
        </div>
        
        <div className={styles.modalFooter}>
          <button onClick={onClose} className={styles.doneButton}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentModal;