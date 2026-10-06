import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export const Navbar = ({ telaAtiva, setTelaAtiva }) => {
  const { user, logout } = useAuth();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'pacientes', label: 'Pacientes', icon: '👥' },
    { id: 'agendamento', label: 'Agendamento', icon: '📅' },
    { id: 'triagem', label: 'Triagem Inteligente (IA)', icon: '🩺' }
  ];

  return (
    <header className="cardio-header">
      <div className="cardio-header-content">
        <div className="cardio-brand" onClick={() => setTelaAtiva('dashboard')} style={{ cursor: 'pointer' }}>
          <span className="cardio-logo-badge">🫀</span>
          <div>
            <h1 className="cardio-brand-title">CardioIA Portal</h1>
            <p className="cardio-brand-sub">Sistema de Diagnóstico e Gestão Cardiológica</p>
          </div>
        </div>

        <nav className="cardio-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setTelaAtiva(item.id)}
              className={`cardio-nav-btn ${telaAtiva === item.id ? 'active' : ''}`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="cardio-user-profile">
          <div className="cardio-user-avatar">GS</div>
          <div className="cardio-user-info">
            <span className="cardio-user-name">{user?.nome || 'Dr. Giovani Saavedra'}</span>
            <span className="cardio-user-crm">CRM {user?.crm || '566797-SP'}</span>
          </div>
          <button onClick={logout} className="cardio-btn-logout" title="Sair do Sistema">
            🚪 Sair
          </button>
        </div>
      </div>
    </header>
  );
};
