import React, { useRef, useEffect, useState } from 'react';

const ChatWindow = ({ messages, isLoading, onSendMessage, selectedProvider, onVoiceInput, message, setMessage }) => {
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const [imageType, setImageType] = useState("url"); // 'url' | 'local'
  const [imageURL, setImageURL] = useState("");
  const [imageFile, setImageFile] = useState(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const images = [];
    if (imageType === 'url' && imageURL) images.push(imageURL);
    if (imageType === 'local' && imageFile) images.push(imageFile);

    if (!message.trim() && images.length === 0) return;

    onSendMessage(message, images);

    setMessage('');
    setImageURL('');
    setImageFile(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
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
    <div className="flex flex-col h-96">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${message.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 shadow-sm'}`}>
              <div className="text-sm">{message.text}</div>
              {message.sender === 'assistant' && (
                <div className="mt-2">
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getProviderColor(message.provider)}`}>
                    {getProviderName(message.provider)}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 shadow-sm max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
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
      <div className="border-t bg-white p-4">
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">

          {/* Text input */}
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

          {/* Voice button */}
          <button
            type="button"
            onClick={onVoiceInput}
            disabled={isLoading}
            className="px-3 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
            title="Speak your message"
          >
            🎤
          </button>

          {/* Image type selection */}
          <select
            value={imageType}
            onChange={(e) => setImageType(e.target.value)}
            className="px-2 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          >
            <option value="url">Image URL</option>
            <option value="local">Local Image</option>
          </select>

          {/* Image URL input */}
          {imageType === 'url' && (
            <input
              type="text"
              value={imageURL}
              onChange={(e) => setImageURL(e.target.value)}
              placeholder="Paste image URL"
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
          )}

          {/* Local Image input */}
          {imageType === 'local' && (
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onloadend = () => setImageFile(reader.result); // Base64 string
                reader.readAsDataURL(file);
              }}
            />
          )}

          {/* Send button */}
          <button
            type="submit"
            disabled={(message.trim() === "" && imageURL.trim() === "" && !imageFile) || isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          >
            🚀
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow;
