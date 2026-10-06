import React, { useEffect, useState } from 'react';
import { apiService } from '../services/api';

export const DashboardPage = ({ setTelaAtiva }) => {
  const [stats, setStats] = useState({ totalPacientes: 0, altoRisco: 0, totalConsultas: 0 });
  const [consultasHoje, setConsultasHoje] = useState([]);

  useEffect(() => {
    const carregar = async () => {
      const s = await apiService.getEstatisticas();
      const c = await apiService.getConsultas();
      setStats(s);
      setConsultasHoje(c.slice(0, 3));
    };
    carregar();
  }, []);

  return (
    <div className="cardio-dashboard">
      <div className="cardio-page-header">
        <div>
          <h2>Painel Geral de Cardiologia</h2>
          <p className="cardio-page-sub">Visão consolidada do fluxo assistencial e triagem hospitalar</p>
        </div>
        <button onClick={() => setTelaAtiva('triagem')} className="cardio-btn-primary">
          🩺 Nova Triagem por Sintomas
        </button>
      </div>

      {/* Cards com Métricas Principais */}
      <div className="cardio-metric-grid">
        <div className="cardio-metric-card">
          <div className="cardio-metric-icon blue">👥</div>
          <div>
            <span className="cardio-metric-num">{stats.totalPacientes}</span>
            <span className="cardio-metric-label">Pacientes Cadastrados</span>
          </div>
        </div>

        <div className="cardio-metric-card danger">
          <div className="cardio-metric-icon red">🚨</div>
          <div>
            <span className="cardio-metric-num">{stats.altoRisco}</span>
            <span className="cardio-metric-label">Casos de Alto Risco / Emergência</span>
          </div>
        </div>

        <div className="cardio-metric-card">
          <div className="cardio-metric-icon green">📅</div>
          <div>
            <span className="cardio-metric-num">{stats.totalConsultas}</span>
            <span className="cardio-metric-label">Consultas Agendadas</span>
          </div>
        </div>
      </div>

      {/* Grid de Conteúdo */}
      <div className="cardio-grid-2col">
        {/* Proximas consultas */}
        <div className="cardio-card">
          <div className="cardio-card-header">
            <h3>Agenda de Consultas Recentes</h3>
            <button onClick={() => setTelaAtiva('agendamento')} className="cardio-btn-text">
              Ver Todas →
            </button>
          </div>
          <div className="cardio-list">
            {consultasHoje.map((c) => (
              <div key={c.id} className="cardio-list-item">
                <div>
                  <strong>{c.pacienteNome}</strong>
                  <div className="cardio-item-meta">{c.tipo}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className="cardio-badge-time">{c.horario}</span>
                  <div className="cardio-item-meta">{c.data}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Protocolos SBC Ativos */}
        <div className="cardio-card">
          <div className="cardio-card-header">
            <h3>Protocolos Clínicos Integrados (SBC)</h3>
          </div>
          <div className="cardio-protocols-list">
            <div className="cardio-protocol-item alert">
              <strong>Dor Torácica Típica:</strong>
              <p>Realização mandatória de ECG em até 10 minutos da chegada ao PS.</p>
            </div>
            <div className="cardio-protocol-item warning">
              <strong>Dispneia Aguda:</strong>
              <p>Oximetria imediata e investigação de congestão pulmonar ou ICC descompensada.</p>
            </div>
            <div className="cardio-protocol-item info">
              <strong>Inteligência Artificial:</strong>
              <p>Módulo NLP TF-IDF operacional para classificação de risco pré-atendimento.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
