import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export const LoginPage = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('giovani.saavedra@cardioia.med.br');
  const [password, setPassword] = useState('123456');
  const [erro, setErro] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const res = login(email, password);
    if (!res.success) {
      setErro(res.message);
    }
  };

  return (
    <div className="cardio-login-container">
      <div className="cardio-login-card">
        <div className="cardio-login-header">
          <span className="cardio-logo-badge large">🫀</span>
          <h2>CardioIA</h2>
          <p>Portal Médico e Triagem Automatizada</p>
          <div className="cardio-badge-fiap">FIAP ON • Turma 2TIAOR</div>
        </div>

        {erro && <div className="cardio-alert error">{erro}</div>}

        <form onSubmit={handleSubmit} className="cardio-login-form">
          <div className="cardio-form-group">
            <label htmlFor="email">E-mail Profissional / CRM</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="medico@hospital.com.br"
              required
            />
          </div>

          <div className="cardio-form-group">
            <label htmlFor="password">Senha de Acesso</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" className="cardio-btn-primary full">
            🔐 Acessar Portal Clínico
          </button>
        </form>

        <div className="cardio-login-footer">
          <small>Autenticação simulada com JWT e persistência em LocalStorage via Context API.</small>
        </div>
      </div>
    </div>
  );
};
