import React, { useState } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { PacientesPage } from './pages/PacientesPage';
import { AgendamentoPage } from './pages/AgendamentoPage';
import { TriagemPage } from './pages/TriagemPage';
import './App.css';

function MainApp() {
  const [telaAtiva, setTelaAtiva] = useState('dashboard');

  return (
    <div className="cardio-layout">
      <Navbar telaAtiva={telaAtiva} setTelaAtiva={setTelaAtiva} />

      <main className="cardio-main">
        {telaAtiva === 'dashboard' && <DashboardPage setTelaAtiva={setTelaAtiva} />}
        {telaAtiva === 'pacientes' && <PacientesPage />}
        {telaAtiva === 'agendamento' && <AgendamentoPage />}
        {telaAtiva === 'triagem' && <TriagemPage />}
      </main>

      <footer className="cardio-footer">
        <p>
          CardioIA • Fase 2: Diagnóstico Automatizado — FIAP ON (Turma 2TIAOR)  
          <span> | Equipe: Giovani Saavedra (RM566797) e Marcio Elifas (RM567871)</span>
        </p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <MainApp />
      </ProtectedRoute>
    </AuthProvider>
  );
}
