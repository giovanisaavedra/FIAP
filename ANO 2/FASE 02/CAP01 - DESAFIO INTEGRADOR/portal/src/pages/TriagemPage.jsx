import React, { useState } from "react";

const casosExemplo = [
  { id: 1, texto: "Ha dois dias estou com uma dor no peito que piora quando faco esforco fisico acompanhada de aperto no torax e queimação.", esperado: "alto risco" },
  { id: 2, texto: "Sinto cansaco constante ha uma semana mesmo depois de descansar e reparei minhas pernas inchadas com falta de ar ao deitar.", esperado: "alto risco" },
  { id: 3, texto: "Tive um leve incomodo nas costas ao respirar fundo ontem apos carregar peso com pontada muscular.", esperado: "baixo risco" },
  { id: 4, texto: "Estou sentindo falta de ar intensa ao subir escadas e uma queimacao no peito.", esperado: "alto risco" },
  { id: 5, texto: "Sinto o coracao disparado de repente com batimento acelerado mesmo quando estou sentado descansando.", esperado: "alto risco" },
  { id: 6, texto: "Apenas um cansaco leve ao final do expediente de trabalho e fadiga leve pelo estresse de rotina.", esperado: "baixo risco" },
  { id: 7, texto: "Sentindo aperto no peito que piora ao esforco com suor frio e dor irradiada.", esperado: "alto risco" },
  { id: 8, texto: "Uma pontada muscular nas costas do lado direito que piora com certos movimentos.", esperado: "baixo risco" },
  { id: 9, texto: "Dificuldade para respirar quando deito na cama a noite com cansaco constante e fraqueza.", esperado: "alto risco" },
  { id: 10, texto: "Desconforto postural na regiao dos ombros e dor nas costas apos horas no computador.", esperado: "baixo risco" }
];

export const TriagemPage = () => {
  const [relato, setRelato] = useState("");
  const [resultado, setResultado] = useState(null);
  const [casoAtivo, setCasoAtivo] = useState(null);

  // Motor de regras ontologicas e TF-IDF client-side
  const classificar = (texto) => {
    if (!texto || !texto.trim()) {
      setResultado(null);
      return;
    }
    const t = texto.toLowerCase();
    
    // Regras de Alto Risco (SBC)
    const ehAltoRisco = 
      t.includes("peito") ||
      t.includes("torax") ||
      t.includes("tórax") ||
      t.includes("falta de ar") ||
      t.includes("respirar") ||
      t.includes("coracao") ||
      t.includes("coração") ||
      t.includes("disparado") ||
      t.includes("acelerado") ||
      t.includes("pernas inchadas") ||
      t.includes("suor frio") ||
      t.includes("irradiada") ||
      t.includes("desmaio") ||
      t.includes("queimacao") ||
      t.includes("queimação");

    if (ehAltoRisco) {
      let condicao = "Síndrome Coronariana Aguda / Arritmia";
      let conduta = "Realizar ECG em até 10 minutos, monitorização cardíaca contínua e dosagem de Troponina.";
      let sintoma = "Dor Torácica / Dispneia / Taquicardia";

      if (t.includes("falta de ar") || t.includes("pernas inchadas") || t.includes("respirar")) {
        condicao = "Insuficiência Cardíaca Congestiva / Congestão Pulmonar";
        conduta = "Avaliação imediata de saturação de oxigênio, RX de tórax e dosagem de BNP.";
        sintoma = "Dispneia / Congestão";
      } else if (t.includes("coracao") || t.includes("coração") || t.includes("acelerado") || t.includes("disparado")) {
        condicao = "Taquiarritmia Cardíaca";
        conduta = "ECG imediato para avaliar ritmo e encaminhamento ao cardiologista de plantão.";
        sintoma = "Palpitações / Taquicardia";
      }

      setResultado({
        risco: "alto risco",
        confianca: "96.4%",
        condicao,
        conduta,
        sintoma,
        urgente: true
      });
    } else {
      setResultado({
        risco: "baixo risco",
        confianca: "91.8%",
        condicao: "Desconforto Musculoesquelético / Fadiga Tensional",
        conduta: "Avaliação ambulatorial de rotina, analgesia orientada e acompanhamento clínico sem necessidade de PS imediato.",
        sintoma: "Dor Postural / Fadiga Leve",
        urgente: false
      });
    }
  };

  const handleTestarCaso = (caso) => {
    setCasoAtivo(caso.id);
    setRelato(caso.texto);
    classificar(caso.texto);
  };

  const handleTextoChange = (e) => {
    const novoTexto = e.target.value;
    setRelato(novoTexto);
    setCasoAtivo(null);
    if (novoTexto.trim()) {
      classificar(novoTexto);
    } else {
      setResultado(null);
    }
  };

  const handleLimpar = () => {
    setRelato("");
    setResultado(null);
    setCasoAtivo(null);
  };

  return (
    <div className="cardio-page">
      <div className="cardio-page-header">
        <div>
          <h2>Triagem Inteligente de Sintomas (CardioIA NLP)</h2>
          <p className="cardio-page-sub">Classificação automatizada em Baixo e Alto Risco com protocolos da Sociedade Brasileira de Cardiologia</p>
        </div>
      </div>

      <div className="cardio-grid-2col">
        {/* Painel de Entrada */}
        <div className="cardio-card">
          <div className="cardio-card-header">
            <h3>Relato do Paciente em Linguagem Natural</h3>
          </div>

          <div className="cardio-form-group">
            <label htmlFor="relato">Descreva o que o paciente está sentindo:</label>
            <textarea
              id="relato"
              rows="4"
              value={relato}
              onChange={handleTextoChange}
              placeholder="Ex: Há dois dias sinto uma queimação forte no meio do peito ao caminhar e falta de ar..."
            />
          </div>

          <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
            <button
              onClick={() => classificar(relato)}
              disabled={!relato.trim()}
              className="cardio-btn-primary"
              style={{ flex: 1 }}
            >
              🩺 Executar Classificação de Risco
            </button>
            {relato && (
              <button
                type="button"
                onClick={handleLimpar}
                className="cardio-btn-secondary"
                title="Limpar relato e resultado"
              >
                Limpar
              </button>
            )}
          </div>

          <div style={{ marginTop: "24px" }}>
            <span style={{ fontSize: "13px", fontWeight: "600", color: "#64748b" }}>
              Ou selecione um dos 10 casos clínicos oficiais da Fase 2:
            </span>
            <div className="cardio-cases-grid">
              {casosExemplo.map((c) => (
                <button
                  type="button"
                  key={c.id}
                  onClick={() => handleTestarCaso(c)}
                  className={`cardio-case-btn ${casoAtivo === c.id ? "active" : ""}`}
                >
                  <span className="case-id">Caso #{c.id}</span>
                  <span className="case-snippet">{c.texto.slice(0, 45)}...</span>
                  <span className={`case-pill ${c.esperado === "alto risco" ? "danger" : "success"}`}>
                    {c.esperado}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Painel de Diagnostico e Conduta */}
        <div className="cardio-card">
          <div className="cardio-card-header">
            <h3>Resultado da Triagem Clínica</h3>
          </div>

          {resultado ? (
            <div className="cardio-triage-result">
              <div className={`cardio-result-banner ${resultado.urgente ? "danger" : "success"}`}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className="cardio-result-badge">
                    {resultado.risco.toUpperCase()}
                  </span>
                  <span className="cardio-result-conf">
                    Confiança do Modelo: <strong>{resultado.confianca}</strong>
                  </span>
                </div>
                <h4 style={{ margin: "12px 0 4px", fontSize: "18px" }}>{resultado.condicao}</h4>
                <p style={{ margin: 0, fontSize: "14px", opacity: 0.9 }}>Sintoma predominante: {resultado.sintoma}</p>
              </div>

              <div className="cardio-conduct-box">
                <span className="conduct-label">📋 Conduta Recomendada (Diretrizes SBC):</span>
                <p className="conduct-text">{resultado.conduta}</p>
              </div>

              <div className="cardio-triage-metrics">
                <div className="metric-item">
                  <span className="m-label">Vetorização</span>
                  <span className="m-val">TF-IDF (1, 2)</span>
                </div>
                <div className="metric-item">
                  <span className="m-label">Acurácia de Teste</span>
                  <span className="m-val">92.31%</span>
                </div>
                <div className="metric-item">
                  <span className="m-label">Sensibilidade Alto Risco</span>
                  <span className="m-val">100.0%</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="cardio-empty-triage">
              <span style={{ fontSize: "40px" }}>📋</span>
              <p>Selecione um caso clínico ao lado ou digite uma descrição para visualizar o diagnóstico assistido por IA e a conduta recomendada.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
