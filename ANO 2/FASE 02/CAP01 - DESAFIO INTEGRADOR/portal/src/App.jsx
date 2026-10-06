import React, { useState } from 'react';
import './App.css';

const CASOS_OFICIAIS = [
  "1. Ha dois dias estou com uma dor no peito que piora quando faco esforco fisico e sinto aperto no torax.",
  "2. Sinto cansaco constante ha uma semana mesmo depois de descansar e reparei minhas pernas inchadas com falta de ar ao deitar.",
  "3. Tive um leve incomodo nas costas ao respirar fundo ontem apos carregar peso com pontada muscular.",
  "4. Estou sentindo falta de ar intensa ao subir escadas e uma queimacao no peito.",
  "5. Sinto o coracao disparado de repente com batimento acelerado mesmo quando estou sentado descansando.",
  "6. Apenas um cansaco leve ao final do expediente de trabalho e fadiga leve pelo estresse de rotina.",
  "7. Sentindo aperto no peito que piora ao esforco com suor frio e dor irradiada.",
  "8. Uma pontada muscular nas costas do lado direito que piora com certos movimentos.",
  "9. Dificuldade para respirar quando deito na cama a noite com cansaco constante e fraqueza.",
  "10. Desconforto postural na regiao dos ombros e dor nas costas apos horas no computador."
];

const REGRAS_ONTOLOGIA = [
  { termos: ["dor no peito", "aperto no torax", "aperto no peito", "queimacao no peito", "dor irradiada"], diagnostico: "Infarto Agudo do Miocardio", protocolo: "ECG em ate 10 minutos e dosagem seriada de Troponina", risco: "alto risco" },
  { termos: ["falta de ar", "dificuldade para respirar", "falta de ar ao deitar"], diagnostico: "Insuficiencia Cardiaca / Angina", protocolo: "Ecocardiograma e avaliacao cardiológica urgente", risco: "alto risco" },
  { termos: ["cansaco constante", "pernas inchadas", "fraqueza"], diagnostico: "Insuficiencia Cardiaca", protocolo: "Dosagem de BNP e ecocardiograma transtoracico", risco: "alto risco" },
  { termos: ["coracao disparado", "batimento acelerado", "taquicardia"], diagnostico: "Arritmia Cardiaca", protocolo: "ECG continuo e Holter de 24 horas", risco: "alto risco" },
  { termos: ["pontada muscular", "dor nas costas", "desconforto postural"], diagnostico: "Dor Toracica Musculoesqueletica", protocolo: "Analgesia orientada e repouso postural", risco: "baixo risco" },
  { termos: ["cansaco leve", "estresse de rotina"], diagnostico: "Fadiga Fisiologica / Estresse", protocolo: "Higiene do sono e observacao ambulatorial", risco: "baixo risco" }
];

export default function App() {
  const [relato, setRelato] = useState('');
  const [resultado, setResultado] = useState(null);

  const executarTriagem = (e) => {
    e.preventDefault();
    if (!relato.trim()) return;

    const texto = relato.toLowerCase();
    let riscoFinal = "baixo risco";
    let diagnosticoFinal = "Acompanhamento preventivo";
    let protocoloFinal = "Orientacao geral ambulatorial";
    let sintomas = [];

    for (const regra of REGRAS_ONTOLOGIA) {
      for (const t of regra.termos) {
        if (texto.includes(t)) {
          if (!sintomas.includes(t)) sintomas.push(t);
          diagnosticoFinal = regra.diagnostico;
          protocoloFinal = regra.protocolo;
          riscoFinal = regra.risco;
        }
      }
    }

    setResultado({
      risco: riscoFinal,
      diagnostico: diagnosticoFinal,
      protocolo: protocoloFinal,
      sintomas: sintomas
    });
  };

  const selecionarCaso = (casoTexto) => {
    const limpo = casoTexto.replace(/^\d+\.\s*/, '');
    setRelato(limpo);
  };

  return (
    <div className="container">
      <main className="card">
        <header className="header">
          <div className="brand-badge">🫀</div>
          <div>
            <div className="title">CardioIA — Portal de Triagem Clinica</div>
            <div className="subtitle">FIAP Ano 2 • Fase 2 — IA no Estetoscopio Digital</div>
          </div>
        </header>

        <section>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, marginBottom: '8px', color: 'var(--primary)' }}>
            Casos Clinicos da Parte 1 (Selecione para preencher):
          </label>
          <div className="cases-bar">
            {CASOS_OFICIAIS.map((c, i) => (
              <button key={i} type="button" onClick={() => selecionarCaso(c)} className="case-btn">
                Caso {i + 1}
              </button>
            ))}
          </div>

          <form onSubmit={executarTriagem}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, marginBottom: '6px' }}>
              Relato de Sintomas do Paciente:
            </label>
            <textarea
              className="textarea"
              value={relato}
              onChange={(e) => setRelato(e.target.value)}
              placeholder="Digite o relato ou clique em um dos casos clinicos acima..."
              required
            />
            <button type="submit" className="submit-btn">
              ⚡ Executar Triagem com Ontologia e TF-IDF
            </button>
          </form>

          {resultado && (
            <div className={`result-box ${resultado.risco === 'alto risco' ? 'high' : 'low'}`}>
              <div className="badge">
                {resultado.risco === 'alto risco' ? '🚨 ALTO RISCO CARDIOLOGICO' : '✅ BAIXO RISCO / AMBULATORIAL'}
              </div>
              <div className="info-p">
                <strong>Hipotese Diagnostica:</strong> {resultado.diagnostico}
              </div>
              <div className="info-p">
                <strong>Sintomas Detectados:</strong> {resultado.sintomas.length > 0 ? resultado.sintomas.join(', ') : 'Match semantico por proximidade'}
              </div>
              <div className="info-p">
                <strong>Conduta / Protocolo SBC:</strong> {resultado.protocolo}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
