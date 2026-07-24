import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import DashboardController from './pages/DashboardController';
import Reports from './pages/Reports';
import Copilot from './pages/Copilot';
import TeamDetails from './pages/TeamDetails';
import EngineerDetails from './pages/EngineerDetails';
import { Persona } from './types';

function App() {
  const [persona, setPersona] = useState<Persona>(() => {
    const saved = localStorage.getItem('cuia_persona');
    return (saved as Persona) || 'leadership';
  });

  React.useEffect(() => {
    localStorage.setItem('cuia_persona', persona);
  }, [persona]);

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Navbar persona={persona} setPersona={setPersona} />
          
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
              <Routes>
                <Route path="/" element={<DashboardController persona={persona} />} />
                <Route path="/team/:teamId" element={<TeamDetails />} />
                <Route path="/engineer/:engineerId" element={<EngineerDetails />} />
                <Route path="/reports" element={<Reports persona={persona} />} />
                <Route path="/copilot" element={<Copilot persona={persona} />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
