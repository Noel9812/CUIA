import { useState, useRef, useEffect } from 'react';
import { chatWithCopilot } from '../services/api';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { Persona } from '../types';

// Minimal markdown renderer: bold (**text**) and bullet lines (- text)
function renderMarkdown(text: string) {
  const lines = text.split('\n');
  const elements: JSX.Element[] = [];

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) {
      elements.push(<div key={idx} className="h-2" />);
      return;
    }

    // Bullet line
    if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
      const content = trimmed.slice(2);
      elements.push(
        <div key={idx} className="flex items-start gap-2 my-0.5">
          <span className="mt-1 w-1.5 h-1.5 rounded-full bg-current flex-shrink-0 opacity-60" />
          <span>{renderInline(content)}</span>
        </div>
      );
    } else {
      elements.push(<p key={idx} className="my-0.5">{renderInline(trimmed)}</p>);
    }
  });

  return elements;
}

// Render inline bold: **text**
function renderInline(text: string): JSX.Element {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**')
          ? <strong key={i}>{part.slice(2, -2)}</strong>
          : <span key={i}>{part}</span>
      )}
    </>
  );
}

export default function Chat({ persona }: { persona: Persona }) {
  const [messages, setMessages] = useState<{role: 'user'|'assistant', text: string}[]>([{
    role: 'assistant',
    text: 'Hello! I am your Capacity & Utilization Intelligence Copilot. What would you like to analyze?'
  }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationContext, setConversationContext] = useState<Record<string, unknown> | undefined>(undefined);
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
      const res = await chatWithCopilot(userMsg, persona, conversationContext);
      setMessages(prev => [...prev, { role: 'assistant', text: res.answer }]);
      if (res.conversation_context) {
        setConversationContext(res.conversation_context);
      }
    } catch (error: any) {
      let errorMsg = 'Sorry, I encountered an error. Please try again.';
      if (error.response && error.response.data && error.response.data.detail) {
        const detail = error.response.data.detail;
        if (detail.error_type === 'ServiceUnavailable') {
          errorMsg = 'AI service is currently unavailable. Please check AWS Bedrock configuration.';
        } else if (detail.error_type === 'RateLimit') {
          errorMsg = 'AI service is rate-limited. Please wait a moment and try again.';
        } else {
          errorMsg = detail.message || 'An unexpected error occurred.';
        }
      } else if (error.message) {
        errorMsg = `Connection error: ${error.message}`;
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
            <div className={`flex items-start max-w-[82%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-indigo-600 ml-3' : 'bg-green-600 mr-3'}`}>
                {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
              </div>
              <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-gray-100 text-gray-800 rounded-tl-none'}`}>
                {msg.role === 'assistant' ? renderMarkdown(msg.text) : <p>{msg.text}</p>}
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
              <div className="px-4 py-3 rounded-2xl bg-gray-100 rounded-tl-none flex items-center space-x-2">
                <Loader2 className="w-4 h-4 text-gray-500 animate-spin" />
                <span className="text-sm text-gray-500">Analyzing...</span>
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
            placeholder="Ask about utilization, capacity, burnout risk, forecasts..."
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
