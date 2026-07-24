import { useState, useRef, useEffect } from 'react';
import { chatWithCopilot } from '../services/api';
import { Send, Bot, User, Loader2 } from 'lucide-react';

export default function Chat() {
  const [messages, setMessages] = useState<{role: 'user'|'assistant', text: string}[]>([{
    role: 'assistant',
    text: 'Hello! I am your Capacity & Utilization Intelligence Assistant. How can I help you analyze the data today?'
  }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const res = await chatWithCopilot(userMsg);
      setMessages(prev => [...prev, { role: 'assistant', text: res.answer }]);
    } catch (error: any) {
      let errorMsg = 'Sorry, I encountered an error. Please try again.';
      if (error.response && error.response.data && error.response.data.detail) {
        const detail = error.response.data.detail;
        errorMsg = `Error: ${detail.error_type || 'Unknown'} - ${detail.message || JSON.stringify(detail)}`;
      } else if (error.message) {
        errorMsg = `Error: ${error.message}`;
      }
      setMessages(prev => [...prev, { role: 'assistant', text: errorMsg }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex items-start max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-indigo-600 ml-3' : 'bg-green-600 mr-3'}`}>
                {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
              </div>
              <div className={`p-3 rounded-2xl ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-gray-100 text-gray-800 rounded-tl-none'}`}>
                <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-600 mr-3 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="p-4 rounded-2xl bg-gray-100 rounded-tl-none flex items-center space-x-2">
                <Loader2 className="w-4 h-4 text-gray-500 animate-spin" />
                <span className="text-sm text-gray-500">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="p-4 border-t bg-gray-50">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about team utilization, burnout risk, etc..."
            className="flex-1 rounded-lg border-gray-300 border p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            disabled={loading}
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="bg-indigo-600 text-white p-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
