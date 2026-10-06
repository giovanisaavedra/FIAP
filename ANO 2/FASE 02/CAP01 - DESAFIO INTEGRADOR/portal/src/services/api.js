/**
 * Servico de API simulada para o portal CardioIA
 * Simula consumo de dados de pacientes e consultas cardiológicas
 */

let pacientesIniciais = [
  { id: 1, nome: "Carlos Eduardo Silva", idade: 58, sexo: "M", queixa: "Dor no peito ao esforco", risco: "alto risco", status: "Em observação", dataUltima: "2026-10-01" },
  { id: 2, nome: "Mariana Souza Lima", idade: 42, sexo: "F", queixa: "Palpitacoes e taquicardia", risco: "alto risco", status: "Aguardando Holter", dataUltima: "2026-10-03" },
  { id: 3, nome: "Roberto Mendes", idade: 67, sexo: "M", queixa: "Falta de ar ao deitar", risco: "alto risco", status: "Em tratamento ICC", dataUltima: "2026-09-28" },
  { id: 4, nome: "Ana Paula Ferreira", idade: 35, sexo: "F", queixa: "Check-up preventivo anual", risco: "baixo risco", status: "Liberada", dataUltima: "2026-10-04" },
  { id: 5, nome: "Joao Batista de Oliveira", idade: 51, sexo: "M", queixa: "Incomodo muscular nas costas", risco: "baixo risco", status: "Ambulatorial", dataUltima: "2026-10-05" },
  { id: 6, nome: "Luciana Alves Costa", idade: 46, sexo: "F", queixa: "Fadiga leve ao fim do dia", risco: "baixo risco", status: "Orientada", dataUltima: "2026-10-02" }
];

let consultasIniciais = [
  { id: 101, pacienteNome: "Carlos Eduardo Silva", data: "2026-10-07", horario: "09:00", tipo: "Urgência - Avaliação Coronariana", status: "Confirmada" },
  { id: 102, pacienteNome: "Mariana Souza Lima", data: "2026-10-07", horario: "10:30", tipo: "Retorno de Holter", status: "Confirmada" },
  { id: 103, pacienteNome: "Ana Paula Ferreira", data: "2026-10-08", horario: "14:00", tipo: "Check-up de Rotina", status: "Pendente" }
];

export const apiService = {
  getPacientes: async () => {
    // Simula atraso de rede assincrono
    await new Promise(r => setTimeout(r, 100));
    return [...pacientesIniciais];
  },

  getConsultas: async () => {
    await new Promise(r => setTimeout(r, 100));
    return [...consultasIniciais];
  },

  adicionarConsulta: async (novaConsulta) => {
    await new Promise(r => setTimeout(r, 150));
    const consulta = {
      id: Date.now(),
      ...novaConsulta,
      status: "Confirmada"
    };
    consultasIniciais = [consulta, ...consultasIniciais];
    return consulta;
  },

  getEstatisticas: async () => {
    await new Promise(r => setTimeout(r, 50));
    const totalPacientes = pacientesIniciais.length;
    const altoRisco = pacientesIniciais.filter(p => p.risco === "alto risco").length;
    const totalConsultas = consultasIniciais.length;
    return { totalPacientes, altoRisco, totalConsultas };
  }
};
