import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export const PacientesPage = () => {
  const [pacientes, setPacientes] = useState([]);
  const [busca, setBusca] = useState('');
  const [filtroRisco, setFiltroRisco] = useState('todos');
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    const carregar = async () => {
      setCarregando(true);
      const dados = await apiService.getPacientes();
      setPacientes(dados);
      setCarregando(false);
    };
    carregar();
  }, []);

  const pacientesFiltrados = pacientes.filter((p) => {
    const matchBusca = p.nome.toLowerCase().includes(busca.toLowerCase()) ||
                       p.queixa.toLowerCase().includes(busca.toLowerCase());
    const matchRisco = filtroRisco === 'todos' || p.risco === filtroRisco;
    return matchBusca && matchRisco;
  });

  return (
    <div className="cardio-page">
      <div className="cardio-page-header">
        <div>
          <h2>Cadastro de Pacientes Cardiológicos</h2>
          <p className="cardio-page-sub">Monitoramento ambulatorial e histórico de queixas clínicas</p>
        </div>
      </div>

      <div className="cardio-filter-bar">
        <input
          type="text"
          placeholder="Buscar por nome do paciente ou queixa..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="cardio-input-search"
        />

        <div className="cardio-filter-buttons">
          <button
            onClick={() => setFiltroRisco('todos')}
            className={`cardio-filter-pill ${filtroRisco === 'todos' ? 'active' : ''}`}
          >
            Todos ({pacientes.length})
          </button>
          <button
            onClick={() => setFiltroRisco('alto risco')}
            className={`cardio-filter-pill danger ${filtroRisco === 'alto risco' ? 'active' : ''}`}
          >
            Alto Risco ({pacientes.filter(p => p.risco === 'alto risco').length})
          </button>
          <button
            onClick={() => setFiltroRisco('baixo risco')}
            className={`cardio-filter-pill success ${filtroRisco === 'baixo risco' ? 'active' : ''}`}
          >
            Baixo Risco ({pacientes.filter(p => p.risco === 'baixo risco').length})
          </button>
        </div>
      </div>

      {carregando ? (
        <div className="cardio-loading-box">Carregando base de pacientes...</div>
      ) : (
        <div className="cardio-table-container">
          <table className="cardio-table">
            <thead>
              <tr>
                <th>Paciente</th>
                <th>Idade / Sexo</th>
                <th>Queixa Principal / Sintoma</th>
                <th>Classificação de Risco</th>
                <th>Status Clínico</th>
                <th>Última Avaliação</th>
              </tr>
            </thead>
            <tbody>
              {pacientesFiltrados.map((p) => (
                <tr key={p.id}>
                  <td>
                    <strong>{p.nome}</strong>
                  </td>
                  <td>{p.idade} anos ({p.sexo})</td>
                  <td>{p.queixa}</td>
                  <td>
                    <span className={`cardio-risk-badge ${p.risco === 'alto risco' ? 'danger' : 'success'}`}>
                      {p.risco.toUpperCase()}
                    </span>
                  </td>
                  <td>{p.status}</td>
                  <td>{p.dataUltima}</td>
                </tr>
              ))}
              {pacientesFiltrados.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '24px' }}>
                    Nenhum paciente encontrado para os filtros selecionados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
