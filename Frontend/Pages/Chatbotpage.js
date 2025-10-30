import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios'; // Using axios directly for the FastAPI endpoint

// The API for your Python/FastAPI chatbot server
const CHATBOT_API_URL = 'http://localhost:8000/api/chat';

const ChatbotPage = () => {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello! How can I help you with government schemes today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    'Chat from 10/28/2025',
    'Chat from 10/27/2025'
  ]); // Mock chat history

  // This ref is used to auto-scroll to the bottom of the chat
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Auto-scroll whenever a new message is added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Send the user's message to the FastAPI server
      const res = await axios.post(CHATBOT_API_URL, { query: input });
      
      const botMessage = { sender: 'bot', text: res.data.response };
      setMessages((prev) => [...prev, botMessage]);

    } catch (err) {
      console.error("Error communicating with chatbot:", err);
      const errorMsg = { 
        sender: 'bot', 
        text: 'Sorry, I am having trouble connecting to the chat service.' 
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* 1. Chat History Sidebar */}
      <div style={styles.sidebar}>
        <h3>Chat History</h3>
        <ul style={styles.historyList}>
          {chatHistory.map((chat, index) => (
            <li key={index} style={styles.historyItem}>{chat}</li>
          ))}
        </ul>
      </div>

      {/* 2. Main Chat Window */}
      <div style={styles.chatWindow}>
        {/* Messages */}
        <div style={styles.messageList}>
          {messages.map((msg, index) => (
            <div key={index} style={styles.messageRow(msg.sender)}>
              <div style={styles.messageBubble(msg.sender)}>
                {msg.text}
              </div>
            </div>
          ))}
          {/* This empty div is the target for auto-scrolling */}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input Form */}
        <form onSubmit={handleSubmit} style={styles.inputForm}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={styles.input}
            placeholder="Ask anything about government schemes..."
            disabled={loading}
          />
          <button type="submit" style={styles.sendButton(loading)} disabled={loading}>
            {loading ? '...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
};

// --- Styles ---
const styles = {
  container: {
    display: 'flex',
    height: 'calc(85vh - 40px)', // Full viewport height minus header/padding
    margin: '20px 0',
    background: '#fff',
    border: '1px solid #ddd',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  },
  sidebar: {
    width: '25%',
    minWidth: '200px',
    borderRight: '1px solid #eee',
    padding: '20px',
    backgroundColor: '#f9f9f9',
  },
  historyList: {
    listStyleType: 'none',
    padding: 0,
    margin: 0,
  },
  historyItem: {
    padding: '10px',
    cursor: 'pointer',
    borderRadius: '5px',
    marginBottom: '5px',
  },
  chatWindow: {
    width: '75%',
    display: 'flex',
    flexDirection: 'column',
  },
  messageList: {
    flexGrow: 1,
    overflowY: 'auto',
    padding: '20px',
  },
  messageRow: (sender) => ({
    display: 'flex',
    justifyContent: sender === 'user' ? 'flex-end' : 'flex-start',
    marginBottom: '10px',
  }),
  messageBubble: (sender) => ({
    maxWidth: '70%',
    padding: '10px 15px',
    borderRadius: '18px',
    color: sender === 'user' ? '#fff' : '#000',
    backgroundColor: sender === 'user' ? '#007bff' : '#f1f0f0',
  }),
  inputForm: {
    display: 'flex',
    borderTop: '1px solid #eee',
    padding: '10px',
  },
  input: {
    flexGrow: 1,
    border: '1px solid #ccc',
    borderRadius: '20px',
    padding: '10px 15px',
    fontSize: '16px',
    marginRight: '10px',
  },
  sendButton: (loading) => ({
    padding: '10px 20px',
    backgroundColor: loading ? '#ccc' : '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '20px',
    cursor: loading ? 'not-allowed' : 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
  }),
};

export default ChatbotPage;