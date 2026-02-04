import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import ReactMarkdown from 'react-markdown';
import logo from './logo.svg';
import './App.css';
import './Chat.css';

const API_BASE_URL = 'http://127.0.0.1:8000';
const ALLOWED_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-pro-vision"];
const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'pl', name: 'Polski' },
  { code: 'pt', name: 'Português' },
  { code: 'cs', name: 'Čeština' },
  { code: 'es', name: 'Español' },
  { code: 'de', name: 'Deutsch' },
];

function App() {
  const { t, i18n } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [geminiApiKey, setGeminiApiKey] = useState(() => localStorage.getItem('geminiApiKey') || '');
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme ? savedTheme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showApiKeyInput, setShowApiKeyInput] = useState(!geminiApiKey);
  const [selectedModel, setSelectedModel] = useState(() => localStorage.getItem('selectedModel') || ALLOWED_MODELS[0]);
  const [modalImage, setModalImage] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  useEffect(() => {
    localStorage.setItem('selectedModel', selectedModel);
  }, [selectedModel]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if ((!inputMessage.trim() && !selectedFile) || isLoading) {
      return;
    }

    if (!geminiApiKey) {
      alert(t('enterApiKey'));
      setShowApiKeyInput(true);
      return;
    }

    setIsLoading(true);
    const userMessage = {
      type: 'user',
      text: inputMessage,
      image: selectedFile ? URL.createObjectURL(selectedFile) : null,
    };

    const currentMessages = [...messages, userMessage];
    
    setMessages((prevMessages) => [...prevMessages, userMessage, { type: 'bot', text: '' }]);
    setInputMessage('');
    setSelectedFile(null);

    try {
      const history = currentMessages
        .filter(msg => msg.text)
        .map(msg => ({
          role: msg.type === 'user' ? 'user' : 'model',
          text: msg.text,
        }));

      const formData = new FormData();
      if (selectedFile) {
        formData.append('file', selectedFile);
      }
      formData.append('message', inputMessage);
      formData.append('model_name', selectedModel);
      formData.append('history', JSON.stringify(history));

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'X-Gemini-Api-Key': geminiApiKey,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
        throw new Error(errorData.detail || 'Something went wrong with the API request.');
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let isDone = false;

      while (!isDone) {
        const { value, done } = await reader.read();
        isDone = done;
        const chunk = decoder.decode(value, { stream: !isDone });

        if (chunk) {
          setMessages(prevMessages => {
            const lastMessage = prevMessages[prevMessages.length - 1];
            if (lastMessage && lastMessage.type === 'bot') {
              const updatedMessages = [...prevMessages];
              updatedMessages[prevMessages.length - 1] = {
                ...lastMessage,
                text: lastMessage.text + chunk,
              };
              return updatedMessages;
            }
            return prevMessages;
          });
        }
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => {
        const lastMessage = prevMessages[prevMessages.length - 1];
        if(lastMessage && lastMessage.type === 'bot' && lastMessage.text === '') {
            const updatedMessages = [...prevMessages];
            updatedMessages[prevMessages.length - 1] = { type: 'bot', text: `Error: ${error.message}` };
            return updatedMessages;
        }
        return [...prevMessages, { type: 'bot', text: `Error: ${error.message}` }];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    } else {
      setSelectedFile(null);
    }
  };
  
  const handlePaste = (e) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const file = items[i].getAsFile();
            setSelectedFile(file);
            break;
        }
    }
  };

  const handleApiKeyChange = (e) => {
    const newKey = e.target.value;
    setGeminiApiKey(newKey);
    localStorage.setItem('geminiApiKey', newKey);
    if (newKey) {
      setShowApiKeyInput(false);
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode((prevMode) => !prevMode);
  };
  
  const handleLanguageChange = (e) => {
    i18n.changeLanguage(e.target.value);
  };

  const openModal = (imageSrc) => {
    setModalImage(imageSrc);
  };

  const closeModal = () => {
    setModalImage(null);
  };

  return (
    <div className="App">
      <style>{`
        .message-image {
          max-width: 400px;
          max-height: 400px;
          cursor: pointer;
          transition: transform 0.2s;
        }
        .message-image:hover {
          transform: scale(1.02);
        }
        .image-modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0, 0, 0, 0.85);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 2000;
          backdrop-filter: blur(5px);
        }
        .image-modal-content {
          position: relative;
          max-width: 90%;
          max-height: 90%;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .image-modal-content img {
          max-width: 100%;
          max-height: 90vh;
          border-radius: 8px;
          box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .close-modal {
          position: absolute;
          top: -40px;
          right: 0;
          color: white;
          font-size: 35px;
          font-weight: bold;
          cursor: pointer;
          z-index: 2001;
        }
      `}</style>
      <header className="app-header">
        <div className="app-title">
          <img src={logo} className="app-logo" alt="logo" />
          <h1>{t('title')}</h1>
        </div>
        <div className="header-controls">
          <select className="language-selector" value={i18n.language} onChange={handleLanguageChange}>
            {LANGUAGES.map(lang => (
              <option key={lang.code} value={lang.code}>{lang.name}</option>
            ))}
          </select>
          <select
            className="model-selector"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={isLoading}
          >
            {ALLOWED_MODELS.map(model => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
          <button className="theme-toggle-button" onClick={toggleDarkMode}>
            {isDarkMode ? t('lightMode') : t('darkMode')}
          </button>
        </div>
      </header>

      <main className="chat-container">
        {showApiKeyInput && (
          <div className="api-key-input-overlay">
            <div className="api-key-input-card">
              <h2>{t('enterApiKey')}</h2>
              <input
                type="password"
                value={geminiApiKey}
                onChange={handleApiKeyChange}
                placeholder={t('yourApiKey')}
                className="api-key-input-field"
              />
              <button
                onClick={() => setShowApiKeyInput(false)}
                disabled={!geminiApiKey}
                className="api-key-save-button"
              >
                {t('saveKey')}
              </button>
              <p>{t('apiKeyStored')}</p>
            </div>
          </div>
        )}

        <div className="messages-display">
          {messages.length === 0 && !isLoading && (
            <div className="welcome-message">
              <p>{t('welcomeMessage')}</p>
              <p>{t('welcomeInstruction')}</p>
              {!geminiApiKey && (
                <button className="api-key-prompt-button" onClick={() => setShowApiKeyInput(true)}>
                  {t('enterApiKeyButton')}
                </button>
              )}
            </div>
          )}
          {messages.map((msg, index) => (
            <div key={index} className={`message-bubble ${msg.type}`}>
              {msg.image && (
                <img
                  src={msg.image}
                  alt={t('uploadedChartAlt')}
                  className="message-image"
                  onClick={() => openModal(msg.image)}
                />
              )}
              {msg.type === 'user' ? (
                msg.text && <p>{msg.text}</p>
              ) : ( /* 'bot' */
                msg.text ? (
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                ) : (
                  (isLoading && index === messages.length - 1) && <p>{t('thinking')}</p>
                )
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form className="message-input-form" onSubmit={handleSendMessage} onPaste={handlePaste}>
          {selectedFile && (
            <div className="image-preview">
              <img src={URL.createObjectURL(selectedFile)} alt={t('pastedPreviewAlt')} />
              <button type="button" onClick={() => setSelectedFile(null)}>{t('removeImage')}</button>
            </div>
          )}
          <div className="input-area">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={t('inputPlaceholder')}
              className="message-input-field"
              disabled={isLoading}
            />
            <label htmlFor="file-upload" className="file-upload-button" disabled={isLoading}>
              {t('fileUpload')}
              <input id="file-upload" type="file" accept="image/*" onChange={handleFileChange} disabled={isLoading} style={{display: 'none'}} />
            </label>
            <button type="submit" className="send-button" disabled={isLoading}>
              &#10148;
            </button>
          </div>
        </form>
      </main>

      {modalImage && (
        <div className="image-modal" onClick={closeModal}>
          <div className="image-modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="close-modal" onClick={closeModal}>&times;</span>
            <img src={modalImage} alt="Full size" />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
