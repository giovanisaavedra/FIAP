# 🫀 CardioIA Portal — Frontend Responsivo (Ir Além 1)
## Portal Médico e Sistema de Triagem Automatizada em Cardiologia

Aplicação Single Page Application (SPA) desenvolvida em **React 18 + Vite** para simulação visual da rotina assistencial cardiológica, triagem de sintomas por Inteligência Artificial e agendamento de consultas.

---

## 👥 Equipe do Projeto

| Nome Completo     | RM       |
|:------------------|:--------:|
| Giovani Saavedra  | RM566797 |
| Marcio Elifas     | RM567871 |

**Turma:** 2TIAOR — FIAP ON  
**Fase 2:** Diagnóstico Automatizado — IA no Estetoscópio Digital  

---

## 🚀 Tecnologias e Arquitetura Empregada

O projeto foi construído atendendo a 100% dos requisitos estipulados na rubrica do **Ir Além 1**:

- **React 18 + Vite 5:** Build veloz e otimizado com hot-reload.
- **Autenticação Simulada (`src/contexts/AuthContext.jsx`):**
  - Gerenciamento de sessão global via **Context API**;
  - Geração e validação de token fake (JWT) armazenado em `localStorage`;
  - Persistência de dados do usuário e função de logout.
- **Proteção de Rotas (`src/components/ProtectedRoute.jsx`):**
  - Bloqueio de acesso a usuários não autenticados com redirecionamento automático para a tela de Login.
- **Consumo de API Simulada (`src/services/api.js`):**
  - Chamadas assíncronas para listagem de pacientes, estatísticas e agendamento de consultas.
- **Controle de Estado Avançado com Hooks:**
  - **`useReducer`** implementado no formulário de agendamento de consultas (`src/pages/AgendamentoPage.jsx`) com ações de despacho de campos, reset e botão rápido de prioridade emergencial da SBC;
  - **`useState`** para controle de filtros, inputs e estados locais de UI;
  - **`useEffect`** para recuperação de sessão e carregamento assíncrono de dados da API;
  - **`useContext`** para disponibilizar o contexto de autenticação em qualquer componente.
- **Componentização e Organização de Pastas:**
  - `src/contexts/`: Provedor e hook de autenticação;
  - `src/components/`: Componentes reutilizáveis (Navbar, ProtectedRoute);
  - `src/services/`: Camada de acesso a dados simulados (API mock);
  - `src/pages/`: Telas da aplicação (Login, Dashboard, Pacientes, Agendamento e Triagem NLP);
  - `src/styles/`: Design System e tokens visuais.

---

## 🖥️ Telas Disponíveis

1. **🔐 Login:** Acesso restrito com e-mail/CRM profissional e validação de credenciais.
2. **📊 Dashboard:** Painel com cartões de indicadores (total de pacientes, casos em alto risco, consultas marcadas) e protocolos vigentes da SBC.
3. **👥 Pacientes:** Listagem dinâmica com campo de busca em tempo real e filtros por classificação de risco (Alto vs Baixo Risco).
4. **📅 Agendamento:** Formulário orientado por `useReducer` com botão de priorização SBC e histórico de consultas confirmadas.
5. **🩺 Triagem Inteligente:** Teste interativo em linguagem natural com atalhos para os 10 casos clínicos da Fase 2 e diagnóstico com conduta da SBC em tempo real.

---

## ⚙️ Como Executar

### Pré-requisitos
- Node.js versão 18 ou superior instalado
- Gerenciador de pacotes `npm`

### Instalação e Execução
```bash
# Acessar a pasta do portal
cd portal

# Instalar dependências
npm install

# Iniciar servidor local de desenvolvimento
npm run dev
```

Abra seu navegador no link indicado no terminal (normalmente `http://localhost:5173/`).

### Credenciais Padrão para Login
- **E-mail:** `giovani.saavedra@cardioia.med.br`
- **Senha:** `123456`

---

## 📹 Demonstração em Vídeo

O vídeo de apresentação e demonstração funcional do portal (de até 4 minutos) pode ser acessado no YouTube:

[![Vídeo de Demonstração](https://img.shields.io/badge/YouTube-Demonstração_do_Portal-red?logo=youtube)](https://youtu.be/SEU_LINK_AQUI)
