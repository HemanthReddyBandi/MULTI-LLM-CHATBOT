import React, { useRef, useEffect, useState } from 'react';

const ChatWindow = ({ messages, isLoading, onSendMessage, selectedProvider, onVoiceInput, message, setMessage }) => {
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const [showImageInput, setShowImageInput] = useState(false);
  const [imageType, setImageType] = useState("url"); 
  const [imageURL, setImageURL] = useState("");
  const [imageFile, setImageFile] = useState(null);

  // Focus input on new messages
  useEffect(() => {
    inputRef.current?.focus();
  }, [messages]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Suppress ResizeObserver warnings in console
  useEffect(() => {
    const resizeObserverErr = (e) => e.stopImmediatePropagation();
    window.addEventListener("error", resizeObserverErr);
    return () => window.removeEventListener("error", resizeObserverErr);
  }, []);

  // Clean messages from unwanted OpenAI/Gemini tags
  const cleanMessageText = (text) => {
    if (!text) return "";
    const match = text.match(/<\|message\|>([\s\S]*)/);
    if (match && match[1]) return match[1].trim();
    return text;
  };

  const handleSend = () => {
    const images = [];
    if (imageType === 'url' && imageURL) images.push(imageURL);
    if (imageType === 'local' && imageFile) images.push(imageFile);

    if (!message.trim() && images.length === 0) return;

    onSendMessage(message, images);

    setMessage('');
    setImageURL('');
    setImageFile(null);
    setShowImageInput(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getProviderColor = (provider) => {
    const colors = {
      openai: 'bg-green-100 text-green-800',
      gemini: 'bg-blue-100 text-blue-800',
      deepseek: 'bg-purple-100 text-purple-800',
      system: 'bg-gray-100 text-gray-800',
      error: 'bg-red-100 text-red-800'
    };
    return colors[provider] || 'bg-gray-100 text-gray-800';
  };

  const getProviderName = (provider) => {
    const names = {
      openai: 'OpenAI GPT',
      gemini: 'Google Gemini',
      deepseek: 'DeepSeek AI',
      system: 'System',
      error: 'Error'
    };
    return names[provider] || provider;
  };

  return (
    <div className="flex flex-col w-full max-w-full mx-auto h-[65vh] border rounded-lg shadow-lg">

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] px-4 py-2 rounded-lg ${msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 shadow-sm'}`}>
              <div className="text-sm">{cleanMessageText(msg.text)}</div>
              {msg.images?.map((img, i) => (
                <img key={i} src={img} alt="sent" className="mt-2 rounded max-w-full"/>
              ))}
              {msg.sender === 'assistant' && (
                <div className="mt-1">
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getProviderColor(msg.provider)}`}>
                    {getProviderName(msg.provider)}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 shadow-sm max-w-[70%] px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-500">{getProviderName(selectedProvider)} is thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-3 flex items-center space-x-2">

        <input
          ref={inputRef}
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={`Type your message for ${getProviderName(selectedProvider)}...`}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={isLoading}
        />

        {/* Mic button */}
        <button
          type="button"
          onClick={onVoiceInput}
          disabled={isLoading}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
          title="Speak your message"
        >
          🎤
        </button>

        {/* Send button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={(message.trim() === "" && !imageFile && !imageURL) || isLoading}
          className="px-8 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
        >
          🚀
        </button>

        {/* Image toggle button */}
        <button
          type="button"
          onClick={() => setShowImageInput(!showImageInput)}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
          title="Attach Image"
        >
          🖼️
        </button>
      </div>

      {/* Image input (toggleable) */}
      {showImageInput && (
        <div className="border-t bg-gray-100 p-2 flex space-x-2 items-center">
          <select
            value={imageType}
            onChange={(e) => setImageType(e.target.value)}
            className="px-2 py-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="url">Image URL</option>
            <option value="local">Local Image</option>
          </select>

          {imageType === 'url' && (
            <input
              type="text"
              value={imageURL}
              onChange={(e) => setImageURL(e.target.value)}
              placeholder="Paste image URL"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          )}

          {imageType === 'local' && (
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onloadend = () => setImageFile(reader.result);
                reader.readAsDataURL(file);
              }}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
