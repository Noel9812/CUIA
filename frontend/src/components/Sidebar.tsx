import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileText, MessageSquare } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();

  const links = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/reports', label: 'Reports', icon: FileText },
    { to: '/copilot', label: 'AI Copilot', icon: MessageSquare },
  ];

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-screen">
      <div className="p-6">
        <h1 className="text-2xl font-bold tracking-wider">CUIA</h1>
        <p className="text-gray-400 text-xs mt-1">Intelligence Agent</p>
      </div>
      <nav className="flex-1 px-4 mt-6">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = location.pathname === link.to || (link.to === '/' && location.pathname.startsWith('/dashboard'));
          return (
            <Link
              key={link.to}
              to={link.to}
              className={`flex items-center px-4 py-3 mb-2 rounded-lg transition-colors ${
                isActive ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              {link.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
