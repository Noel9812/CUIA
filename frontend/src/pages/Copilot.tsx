import Chat from '../components/Chat';

export default function Copilot() {
  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">AI Copilot</h2>
        <p className="text-gray-500">Ask questions about your workforce analytics and get instant insights.</p>
      </div>
      
      <div className="flex-1 min-h-0">
        <Chat />
      </div>
    </div>
  );
}
