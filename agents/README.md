# Estrutura de Agentes Especialistas - AutoCarSystem

Esta pasta contém as definições dos **Agentes Especialistas** e o **Orquestrador de Tarefas** do projeto AutoCarSystem.

---

## 📁 Estrutura de Arquivos

```text
agents/
├── backend_engineer.md     # System prompt do Especialista Backend (Flask, SQLAlchemy, Multi-tenant)
├── frontend_designer.md    # System prompt do Design Engineer (UI/UX, Tailwind, Impeccable Design)
├── product_manager.md      # System prompt do Tech PM (Backlog, Roadmap, Sprints)
├── html_reporter.md        # System prompt do Especialista em Relatórios e Web2PDF
├── orchestrator.py         # Script Python para orquestração, listagem e geração de relatórios HTML
└── reports/
    └── project_status.html # Relatório visual interativo do status de desenvolvimento
```

---

## 🚀 Como Utilizar o Orquestrador

No terminal ou via Python no ambiente virtual:

### 1. Listar Agentes Disponíveis e Gerar Relatório HTML
```powershell
python agents/orchestrator.py
```

### 2. Exibir o Prompt Específico de um Agente
```powershell
python agents/orchestrator.py backend    # Exibe prompt do Backend Specialist
python agents/orchestrator.py frontend   # Exibe prompt do UI/UX Designer
python agents/orchestrator.py pm         # Exibe prompt do Product Manager
python agents/orchestrator.py reporter   # Exibe prompt do HTML Reporter
```

### 3. Atualizar Relatório HTML de Status
```powershell
python agents/orchestrator.py report
```
O arquivo gerado fica em `agents/reports/project_status.html` e pode ser aberto no navegador a qualquer momento.

---

## 🎯 Especialistas e Responsabilidades

| Agente | Arquivo | Responsabilidade |
|---|---|---|
| 📋 **PM** | `product_manager.md` | Acompanhamento do `roteiro_projeto.md`, definição de metas e sprints. |
| ⚙️ **Backend** | `backend_engineer.md` | Blueprints, queries multi-tenant com `empresa_id`, regras de negócio e cálculo de OS. |
| 🎨 **Frontend** | `frontend_designer.md` | Interfaces Jinja2 com TailwindCSS, estética SaaS premium e micro-interações. |
| 📑 **Reporter** | `html_reporter.md` | Templates de impressão de OS (A4 / 80mm), relatórios em PDF e relatórios de progresso. |
