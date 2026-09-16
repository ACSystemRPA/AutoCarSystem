<div align="center">

# 🚗 AutoCarSystem

**Sistema de Gestão Multi-Oficina para Portugal** · Flask · SQLite · Multi-Tenant

`pt-PT` | `€ Euro` | `Flask 3` | `SQLAlchemy` | `TailwindCSS`

</div>

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Stack Tecnológico](#-stack-tecnologico)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Perfis de Utilizador](#-perfis-de-utilizador)
- [Instalação e Setup](#-instalacao-e-setup)
- [Estrutura do Banco de Dados](#-estrutura-do-banco-de-dados)
- [Testes](#-testes)
- [Localização PT-PT (Convenções)](#-localizacao-pt-pt-convencoes)
- [Agentes de IA](#-agentes-de-ia)
- [Roadmap das Fases](#-roadmap-das-fases)
- [Documentação Complementar](#-documentacao-complementar)

---

## 🔍 Sobre o Projeto

O **AutoCarSystem** é um sistema _multi-empresa (multi-tenant)_ para gestão completa de **oficinas automóveis em Portugal**.

Permite gerir **diversas oficinas no mesmo sistema**, mantendo o isolamento total dos dados de cada empresa através de uma chave única de `empresa_id`. Cada oficina tem a sua própria base de clientes, viaturas, peças, serviços, ordens de serviço e notificações.

A interface é moderna (design dark premium), responsiva e inteiramente **localizada em Português de Portugal (pt-PT)**, com moeda em **Euro (€)** e conformidade fiscal com **NIF** (Número de Identificação Fiscal).

---

## 🧰 Stack Tecnologico

| Camada | Tecnologia | Versão |
|---|---|---|
| **Linguagem** | Python | 3.13 |
| **Framework Web** | Flask (modular via Blueprints) | 3.0.0 |
| **ORM / Base de Dados** | Flask-SQLAlchemy + SQLite | 3.1.1 |
| **Migrações** | Flask-Migrate (Alembic) | 4.0.5 |
| **Autenticação** | Flask-Login | 0.6.3 |
| **E-mail** | Flask-Mail | 0.10.0 |
| **PDF** | xhtml2pdf | 0.2.20 |
| **Frontend** | Jinja2 + TailwindCSS (CDN) + FontAwesome 6 | — |
| **Configuração** | python-dotenv | 1.0.0 |
| **Testes** | unittest (stdlib) | — |

> **Ponto forte:** 0 dependências nativas de sistema — o PDF é gerado 100% em Python (xhtml2pdf), ideal para Windows sem GTK.

---

## ✨ Funcionalidades

### Fase 1 — Fundação ✅
- Registo e login de oficinas (multi-tenant)
- Isolamento total de dados por `empresa_id`
- Hash de palavras-passe PBKDF2 (Werkzeug)
- Health check (`/health`)

### Fase 2 — Cadastros Base ✅
- **Clientes:** CRUD completo, pesquisa (nome/NIF/telefone/e-mail)
- **Viaturas:** CRUD, matrícula, marca, modelo, ano, KM, combustível
- **Peças:** CRUD com gestão de stock (mínimo, baixo, valorização)
- **Serviços:** CRUD com preço padrão e tempo estimado

### Fase 3 — Motor de Ordem de Serviço (OS) ✅
- Abertura de OS com checklist de vistoria, KM, nível de combustível
- Adição/remoção de serviços (mão de obra) e peças (com stock)
- Cálculo automático de subtotais e total (`calcular_totais()`)
- Máquina de estados: `ORCAMENTO → APROVADA → EM_ANDAMENTO → CONCLUIDA → ENTREGUE`
- Baixa automática de stock ao concluir (e estorno ao cancelar)
- Número sequencial por ano: `OS-2026-0001`

### Fase 4 — Exportação e Comunicação ✅
- **PDF profissional** (A4) por OS/Orçamento via xhtml2pdf
- **WhatsApp:** link formatado com os dados da OS (`wa.me`)
- **E-mail:** envio do PDF gerado automaticamente com Flask-Mail

### Fase 5 — Dashboard e Rotinas ⏳ (planeada)
- Dashboard com gráficos (Chart.js): facturação mensal, top produtos/serviços, status de OS
- Backup automático da base de dados (schedule/APScheduler)

---

## 🏗 Arquitetura

### Estrutura Modular (Blueprints)

```text
AutoCarSystem/
├── app/
│   ├── __init__.py              # create_app(), registo de blueprints, filtros Jinja
│   ├── models.py                # Todas as tabelas (SQLAlchemy)
│   ├── extensions.py            # db, migrate, login_manager, mail
│   │
│   ├── modules/
│   │   ├── auth/                # Login, Registo de Oficina, Logout
│   │   ├── dashboard/           # Painel principal
│   │   ├── clientes/            # CRUD Clientes
│   │   ├── veiculos/            # CRUD Viaturas
│   │   ├── pecas/               # CRUD Peças / Stock
│   │   ├── servicos/            # CRUD Serviços (mão de obra)
│   │   ├── os/                  # Ordens de Serviço
│   │   └── notificacoes/        # PDF, Email, WhatsApp
│   │
│   ├── templates/               # Templates Jinja2 (dark theme pt-PT)
│   ├── static/                  # CSS, JS, imagens
│   └── utils/
│       └── auth.py              # Decorator requer_perfil() (permissões)
│
├── migrations/                  # Alembic / Flask-Migrate
├── backups/                     # Cópias de segurança da BD (auto)
├── agents/                      # Definições de agentes IA especializados
├── tests/                       # Testes unitários (unittest)
├── .kilo/agent/                 # Conhecimento canónico (AGENTS.md)
├── config.py                    # Configurações (BD, Mail, PDF, Permissões)
├── requirements.txt
├── run.py
└── roteiro_projeto.md           # Roadmap de desenvolvimento
```

### Padrão de Rota

```python
@bp.route('/')
@login_required
@requer_perfil('admin', 'gerente')   # proteção por perfil
def index():
    # SEMPRE filtrar pela empresa do utilizador logado
    query = Modelo.query.filter_by(empresa_id=current_user.empresa_id)
    ...
```

---

## 🔐 Perfis de Utilizador

O sistema define **4 perfis** com níveis de acesso distintos (campo `papel`):

| Perfil | Código | Acesso |
|---|---|---|
| 👑 **Administrador** | `admin` | Total: utilizadores, empresa, relatórios, configurações, backup |
| 🛠 **Gerente** | `gerente` | CRUD completo (sem gestão de utilizadores/empresa) |
| 🗂 **Rececionista** | `rececionista` | Clientes, viaturas, abertura de OS, notificações |
| 🔧 **Mecânico** | `mecanico` | Ver/atualizar OS atribuídas, diagnóstico técnico (sem financeiro) |

**Proteção de rotas:**

```python
from utils.auth import requer_perfil

@bp.route('/relatorios')
@login_required
@requer_perfil('admin', 'gerente')
def relatorios():
    ...
```

---

## 💻 Instalacao e Setup

### Pré-requisitos
- Python **3.13+**
- (Opcional) Git

### Passo a passo

```bash
# 1. Clonar
git clone https://github.com/ACSystemRPA/AutoCarSystem.git
cd AutoCarSystem

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar (Windows)
venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Configurar variáveis de ambiente
# Copie o bloco abaixo para um ficheiro .env
```

```env
SECRET_KEY=chave-secreta-ambiente-de-desenvolvimento-123
FLASK_APP=run.py
FLASK_DEBUG=1

# E-mail (opcional — para notificações)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=exemplo@gmail.com
MAIL_PASSWORD=sua-palavra-passe-app
MAIL_DEFAULT_SENDER=exemplo@gmail.com
```

```bash
# 6. Aplicar migrações do banco de dados
flask db upgrade

# 7. Executar
python run.py
```

Aceda em: **http://127.0.0.1:5000**

---

## 🗄 Estrutura do Banco de Dados

### Diagrama de Entidades

| Entidade | Tabela | Descrição |
|---|---|---|
| Empresa | `empresas` | Oficina/Tenant (NIF, denominação social, contacto) |
| Utilizador | `usuarios` | Acesso ao sistema (papel: admin/gerente/rececionista/mecanico) |
| Cliente | `clientes` | Cliente final (NIF, contacto, morada) |
| Viatura | `veiculos` | Viatura do cliente (matrícula, marca, modelo, KM) |
| Peça | `pecas` | Catálogo de peças/componentes com stock |
| Serviço | `servicos` | Catálogo de mão de obra |
| OS | `ordens_servico` | Ordem de Serviço principal |
| Item Serviço | `itens_servico` | Itens de serviço lançados na OS |
| Item Peça | `itens_peca` | Itens de peça lançados na OS |

### Campos-chave por entidade

```text
empresas        → id, razao_social, nome_fantasia, nif(cnpj), telefone, endereco, cidade
usuarios        → id, empresa_id, nome, email, senha_hash, papel, ativo
clientes        → id, empresa_id, nome, nif(cpf_cnpj), telefone, email, endereco, cidade, ativo
veiculos        → id, empresa_id, cliente_id, placa, marca, modelo, ano_fabricacao, km_atual, combustivel
pecas           → id, empresa_id, codigo_referencia, descricao, preco_custo, preco_venda, estoque_atual
servicos        → id, empresa_id, descricao, categoria, preco_padrao, tempo_estimado_minutos
ordens_servico  → id, empresa_id, numero_os, tipo, status, cliente_id, veiculo_id,
                  valor_servicos, valor_pecas, desconto, valor_total, forma_pagamento
itens_servico   → id, ordem_servico_id, servico_id, descricao, quantidade, valor_unitario, subtotal
itens_peca      → id, ordem_servico_id, peca_id, descricao, quantidade, valor_unitario, subtotal
```

> **Nota de retrocompatibilidade:** As colunas físicas do SQLite mantêm nomes antigos (`cnpj`, `cpf_cnpj`, `cidade`, `placa`) por compatibilidade; os modelos Python expõem nomes PT-PT (`nif`, `concelho`, `matricula`) via mapeamento SQLAlchemy `db.Column('coluna_fisica', ...)`.

### Máquina de Estados da OS

```
ORCAMENTO → EM_APROVACAO → APROVADA → EM_ANDAMENTO → CONCLUIDA → ENTREGUE
     ↓            ↓              ↓            ↓              ↓
 CANCELADA    CANCELADA     CANCELADA   AGUARDANDO_PECA  CANCELADA
```

---

## 🧪 Testes

Suite de testes em `tests/` (unittest):

| Ficheiro | Foco |
|---|---|
| `tests/test_fase1.py` | Registo de oficina, login, proteção de rotas |
| `tests/test_fase2.py` | CRUD de clientes, viaturas, peças, serviços |
| `tests/test_fase3.py` | Abertura de OS, itens, cálculos, estados |

### Executar todos os testes

```bash
python -m unittest discover -s tests -v
```

### Executar uma fase específica

```bash
python -m unittest tests.test_fase1 -v
```

---

## 🇵🇹 Localizacao PT-PT (Convencoes)

Conhecimento canónico completo em [`agents/canonical_ptpt.md`](agents/canonical_ptpt.md) e [`.kilo/agent/AGENTS.md`](.kilo/agent/AGENTS.md).

### Terminologia obrigatória

| ❌ Proibido (pt-BR) | ✅ Obrigatório (pt-PT) |
|---|---|
| CNPJ / CPF | **NIF** |
| Razão Social (UI) | **Denominação Social** |
| Nome Fantasia | **Nome Comercial** |
| Cidade + UF/Estado | **Cidade / Concelho** |
| CEP | **Código Postal** (XXXX-XXX) |
| Cadastrar | **Registar** |
| Salvar | **Guardar** |
| Buscar | **Pesquisar** |
| Senha | **Palavra-passe** |
| Faça login | **Inicie sessão** |
| Usuário | **Utilizador** |
| Veículo | **Viatura** |
| Placa (UI) | **Matrícula** |
| Estoque | **Stock** |
| Faturamento | **Facturação** |
| Endereço | **Morada** |

### Moeda e números

- Símbolo: **€** (Euro)
- Formato: `1.234,56 €` (vírgula decimal, ponto de milhar)
- Filtro Jinja: `{{ valor|currency_pt }}`

### Formato de contacto

- Telefones: `+351 9XX XXX XXX` (telemóvel)
- WhatsApp: dígitos apenas `3519XXXXXXXXX`

---

## 🤖 Agentes de IA

O projeto inclui definições de **agentes especializados** em `agents/` para desenvolvimento assistido (Copilot, Cline, Roo Code, Kilo):

| Agente | Ficheiro | Responsabilidade |
|---|---|---|
| 📋 **PM** | `agents/product_manager.md` | Roadmap, sprints, orquestração |
| ⚙️ **Backend** | `agents/backend_engineer.md` | Flask/SQLAlchemy, multi-tenant, regras de negócio |
| 🎨 **Frontend** | `agents/frontend_designer.md` | UI/UX, TailwindCSS, design premium |
| 📑 **Reporting** | `agents/html_reporter.md` | PDFs, relatórios, impressão |
| 🇵🇹 **Canónico PT-PT** | `agents/canonical_ptpt.md` | Regras de localização obrigatórias |

Orquestrador de tarefas:

```bash
python agents/orchestrator.py            # Lista agentes + gera relatório
python agents/orchestrator.py report     # Atualiza relatório HTML de status
```

---

## 🗺 Roadmap das Fases

| Fase | Descrição | Estado |
|---|---|---|
| **1** | Fundação: Flask, BD, Auth multi-tenant | ✅ Concluída |
| **2** | Cadastros base: Clientes, Viaturas, Peças, Serviços | ✅ Concluída |
| **3** | Motor de OS: abertura, itens, cálculos, estados | ✅ Concluída |
| **4** | Exportação: PDF, WhatsApp, E-mail | ✅ Concluída |
| **5** | Dashboard (Chart.js) + Backup automático | ⏳ Planeada |

---

## 📚 Documentacao Complementar

| Documento | Conteúdo |
|---|---|
| [`roteiro_projeto.md`](roteiro_projeto.md) | Roadmap detalhado, modelo de dados, convenções |
| [`agentes_especialistas.md`](agentes_especialistas.md) | System prompts dos agentes (VS Code) |
| [`agents/README.md`](agents/README.md) | Guia de utilização dos agentes |
| [`agents/canonical_ptpt.md`](agents/canonical_ptpt.md) | Localização PT-PT (obrigatório) |
| [`.kilo/agent/AGENTS.md`](.kilo/agent/AGENTS.md) | Conhecimento canónico do Kilo |

---

<div align="center">

**AutoCarSystem** · Feito para oficinas portuguesas · 🇵🇹

</div>