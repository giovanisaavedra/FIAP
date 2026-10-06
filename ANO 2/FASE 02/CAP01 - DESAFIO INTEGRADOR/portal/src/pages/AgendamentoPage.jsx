import React, { useState, useEffect, useReducer } from 'react';
import { apiService } from '../services/api';

// Estado inicial do formulario gerenciado por useReducer
const initialFormState = {
  pacienteNome: '',
  data: '',
  horario: '',
  tipo: 'Eletiva / Rotina',
  prioridade: 'Normal',
  observacoes: ''
};

// Reducer para gerenciar as acoes do formulario de agendamento
function agendamentoReducer(state, action) {
  switch (action.type) {
    case 'CAMPO_ALTERADO':
      return {
        ...state,
        [action.campo]: action.valor
      };
    case 'DEFINIR_URGENCIA':
      return {
        ...state,
        tipo: 'Urgência Cardiológica (SBC)',
        prioridade: 'Alta',
        observacoes: 'Paciente com sintomas agudos triados em Alto Risco.'
      };
    case 'LIMPAR_FORMULARIO':
      return initialFormState;
    default:
      return state;
  }
}

export const AgendamentoPage = () => {
  // Uso obrigatorio de useReducer conforme exigido na rubrica
  const [formState, dispatch] = useReducer(agendamentoReducer, initialFormState);

  // Uso de useState para controle de feedback da interface e listagem
  const [consultas, setConsultas] = useState([]);
  const [mensagemSucesso, setMensagemSucesso] = useState('');
  const [erro, setErro] = useState('');
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    const carregarConsultas = async () => {
      const dados = await apiService.getConsultas();
      setConsultas(dados);
    };
    carregarConsultas();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    dispatch({ type: 'CAMPO_ALTERADO', campo: name, valor: value });
  };

  const handleAplicarUrgencia = () => {
    dispatch({ type: 'DEFINIR_URGENCIA' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setMensagemSucesso('');

    if (!formState.pacienteNome || !formState.data || !formState.horario) {
      setErro('Por favor, preencha todos os campos obrigatórios.');
      return;
    }

    setSalvando(true);
    try {
      const nova = await apiService.adicionarConsulta({
        pacienteNome: formState.pacienteNome,
        data: formState.data,
        horario: formState.horario,
        tipo: `${formState.tipo} (${formState.prioridade})`
      });

      setConsultas((prev) => [nova, ...prev]);
      setMensagemSucesso(`Consulta agendada com sucesso para ${formState.pacienteNome}!`);
      dispatch({ type: 'LIMPAR_FORMULARIO' });
    } catch (err) {
      setErro('Falha ao registrar agendamento. Tente novamente.');
    } finally {
      setSalvando(false);
    }
  };

  return (
    <div className="cardio-page">
      <div className="cardio-page-header">
        <div>
          <h2>Agendamento de Consultas Cardiológicas</h2>
          <p className="cardio-page-sub">Gestão de horários, retornos e encaminhamentos prioritários</p>
        </div>
      </div>

      <div className="cardio-grid-2col">
        {/* Formulario com useReducer */}
        <div className="cardio-card">
          <div className="cardio-card-header">
            <h3>Novo Agendamento</h3>
            <button
              type="button"
              onClick={handleAplicarUrgencia}
              className="cardio-btn-urgent"
              title="Preenche automaticamente com parâmetros de emergência da SBC"
            >
              ⚡ Prioridade SBC
            </button>
          </div>

          {mensagemSucesso && <div className="cardio-alert success">{mensagemSucesso}</div>}
          {erro && <div className="cardio-alert error">{erro}</div>}

          <form onSubmit={handleSubmit} className="cardio-form">
            <div className="cardio-form-group">
              <label htmlFor="pacienteNome">Nome do Paciente *</label>
              <input
                id="pacienteNome"
                name="pacienteNome"
                type="text"
                value={formState.pacienteNome}
                onChange={handleChange}
                placeholder="Ex: Carlos Eduardo Silva"
                required
              />
            </div>

            <div className="cardio-form-row">
              <div className="cardio-form-group">
                <label htmlFor="data">Data da Consulta *</label>
                <input
                  id="data"
                  name="data"
                  type="date"
                  value={formState.data}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="cardio-form-group">
                <label htmlFor="horario">Horário *</label>
                <input
                  id="horario"
                  name="horario"
                  type="time"
                  value={formState.horario}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="cardio-form-row">
              <div className="cardio-form-group">
                <label htmlFor="tipo">Modalidade / Tipo</label>
                <select
                  id="tipo"
                  name="tipo"
                  value={formState.tipo}
                  onChange={handleChange}
                >
                  <option value="Eletiva / Rotina">Eletiva / Rotina</option>
                  <option value="Retorno de Exames">Retorno de Exames (ECG / Holter)</option>
                  <option value="Avaliação Pós-Infarto">Avaliação Pós-Infarto</option>
                  <option value="Urgência Cardiológica (SBC)">Urgência Cardiológica (SBC)</option>
                </select>
              </div>

              <div className="cardio-form-group">
                <label htmlFor="prioridade">Nível de Prioridade</label>
                <select
                  id="prioridade"
                  name="prioridade"
                  value={formState.prioridade}
                  onChange={handleChange}
                >
                  <option value="Normal">Normal</option>
                  <option value="Moderada">Moderada</option>
                  <option value="Alta">Alta (Prioritário)</option>
                </select>
              </div>
            </div>

            <div className="cardio-form-group">
              <label htmlFor="observacoes">Observações Clínicas / Sintomas Triados</label>
              <textarea
                id="observacoes"
                name="observacoes"
                rows="3"
                value={formState.observacoes}
                onChange={handleChange}
                placeholder="Descreva sintomas identificados pelo módulo de IA..."
              />
            </div>

            <div className="cardio-form-actions">
              <button
                type="button"
                onClick={() => dispatch({ type: 'LIMPAR_FORMULARIO' })}
                className="cardio-btn-secondary"
              >
                Limpar
              </button>
              <button
                type="submit"
                disabled={salvando}
                className="cardio-btn-primary"
              >
                {salvando ? 'Salvando...' : 'Confirmar Agendamento'}
              </button>
            </div>
          </form>
        </div>

        {/* Lista de Consultas Confirmadas */}
        <div className="cardio-card">
          <div className="cardio-card-header">
            <h3>Consultas Confirmadas ({consultas.length})</h3>
          </div>
          <div className="cardio-list scrollable">
            {consultas.map((c) => (
              <div key={c.id} className="cardio-list-item">
                <div>
                  <strong style={{ fontSize: '15px' }}>{c.pacienteNome}</strong>
                  <div className="cardio-item-meta">{c.tipo}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="cardio-badge-time">{c.horario}</div>
                  <div className="cardio-item-meta">{c.data}</div>
                  <span className="cardio-status-chip">{c.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
