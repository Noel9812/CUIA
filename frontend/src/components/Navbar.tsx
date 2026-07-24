import { Persona } from '../types';
import { UserCircle, ChevronDown } from 'lucide-react';
import { useState } from 'react';

export default function Navbar({ persona, setPersona }: { persona: Persona, setPersona: (p: Persona) => void }) {
  const [open, setOpen] = useState(false);

  const getPersonaLabel = (p: Persona) => {
    if (p === 'leadership') return 'Leadership';
    if (p === 'dm-1') return 'Alice Smith (Delivery)';
    if (p === 'dm-2') return 'Bob Johnson (Delivery)';
    return 'Unknown';
  };

  return (
    <header className="bg-white shadow-sm z-10 border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center">
          <span className="text-gray-800 text-lg font-bold">Global Engineering Corp</span>
        </div>
        <div className="relative">
          <button 
            onClick={() => setOpen(!open)}
            className="flex items-center space-x-3 hover:bg-gray-50 p-2 rounded-lg transition-colors focus:outline-none"
          >
            <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700">
              <UserCircle className="w-5 h-5" />
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-sm font-medium text-gray-700">{getPersonaLabel(persona)}</p>
              <p className="text-xs text-gray-500 capitalize">{persona === 'leadership' ? 'Leadership' : 'Delivery Manager'}</p>
            </div>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>

          {open && (
            <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-20">
              <div className="py-1">
                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Role
                </div>
                <button
                  onClick={() => { setPersona('leadership'); setOpen(false); }}
                  className={`w-full text-left block px-4 py-2 text-sm ${persona === 'leadership' ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-700 hover:bg-gray-100'}`}
                >
                  Leadership
                </button>
                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider border-t mt-1 pt-2">
                  Delivery Managers
                </div>
                <button
                  onClick={() => { setPersona('dm-1'); setOpen(false); }}
                  className={`w-full text-left block px-4 py-2 text-sm ${persona === 'dm-1' ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-700 hover:bg-gray-100'}`}
                >
                  Alice Smith
                </button>
                <button
                  onClick={() => { setPersona('dm-2'); setOpen(false); }}
                  className={`w-full text-left block px-4 py-2 text-sm ${persona === 'dm-2' ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-700 hover:bg-gray-100'}`}
                >
                  Bob Johnson
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
