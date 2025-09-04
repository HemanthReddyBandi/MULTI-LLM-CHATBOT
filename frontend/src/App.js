import React, { useState, useRef, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import Dropdown from './components/Dropdown';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';
const API_KEY = process.env.REACT_APP_API_KEY;

const providers = [
  { value: 'openai', label: 'OpenAI GPT-3.5' },
  { value: 'gemini', label: 'Gemini (Image + Text)' },
  { value: 'deepseek', label: 'DeepSeek AI' }
];

function App() {
  // --- Session ID for conversation continuity ---
  const [sessionId] = useState("sess-" + Math.random().toString(36).substring(2, 10));

  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "👋 Hello! I'm your AI assistant. Select an LLM provider above and start chatting!",
      sender: 'assistant',
      provider: 'system'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // --- Scroll chat to bottom ---
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => { scrollToBottom(); }, [messages]);

  // Add images parameter
const sendMessage = async (messageText, images = []) => {
  if (!messageText.trim() && images.length === 0) return; // require at least text or image

  const userMessage = {
    id: Date.now(),
    text: messageText || (images.length > 0 ? "📷 Image sent" : ""),
    sender: 'user',
    provider: selectedProvider
  };
  setMessages(prev => [...prev, userMessage]);
  setIsLoading(true);

  try {
    const response = await fetch(`${API_BASE_URL}/chat?session_id=${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
      },
      body: JSON.stringify({ provider: selectedProvider, message: messageText, images }) // send images
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();

    const assistantMessage = {
      id: Date.now() + 1,
      text: data.response,
      sender: 'assistant',
      provider: data.provider
    };
    setMessages(prev => [...prev, assistantMessage]);

  } catch (error) {
    console.error('Error sending message:', error);
    setMessages(prev => [...prev, {
      id: Date.now() + 1,
      text: `❌ Error: ${error.message}. Make sure backend is running`,
      sender: 'assistant',
      provider: 'error'
    }]);
  } finally {
    setIsLoading(false);
    setMessage("");
  }
};


  // --- Provider change ---
  const handleProviderChange = (provider) => setSelectedProvider(provider);

  // --- Voice input ---
  const handleVoiceInput = async () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Voice recognition not supported.');
      return;
    }
    try { await navigator.mediaDevices.getUserMedia({ audio: true }); }
    catch { alert('Microphone access denied.'); return; }

    if (recognitionRef.current) recognitionRef.current.abort();
    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setMessage(transcript);
    };
    recognition.onerror = (event) => {
      if (event.error !== 'aborted') alert('Voice recognition error: ' + event.error);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  return (
    <div className="app-container">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">

          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
            <h1 className="text-3xl font-bold text-center mb-4">Multi-LLM Chatbot</h1>
            <div className="flex justify-center">
              <Dropdown
                options={providers}
                value={selectedProvider}
                onChange={handleProviderChange}
                label="Select LLM Provider"
              />
            </div>
          </div>

          {/* Chat Window */}
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSendMessage={sendMessage}
            selectedProvider={selectedProvider}
            message={message}
            setMessage={setMessage}
            onVoiceInput={handleVoiceInput}
          />
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        Created with <span className="heart">♥</span> and passion.<br/>
        &copy; Hemanth Reddy Bandi 2025
      </footer>
    </div>
  );
}

export default App;
