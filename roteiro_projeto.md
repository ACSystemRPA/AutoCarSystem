# AutoCarSystem — Roteiro de Desenvolvimento (Gestão de Oficinas Automóveis)

Sistema multi-empresa (multi-tenant) para gestão de oficinas automóveis em Portugal.

## 1. Stack Tecnológico

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.13 |
| Framework Web | Flask 3.0 (Blueprints modulares) |
| Base de Dados | SQLite (ficheiro único, backup simples) |
| Frontend | HTML/Jinja2 + TailwindCSS (CDN) + FontAwesome 6 |
| PDF | xhtml2pdf (HTML → PDF, sem dependências de sistema) |
| E-mail | Flask-Mail |
| Localização | Português de Portugal (pt-PT) |
| Moeda | Euro (€) |
| Arquitetura | Multi-tenant (isolamento por `empresa_id`) |

## 2. Estrutura de Diretórios

```text
AutoCarSystem/
├── app/
│   ├── __init__.py              # create_app(), registo de blueprints, filtros
│   ├── models.py                # Tabelas SQLAlchemy (pt-PT)
│   ├── extensions.py            # db, migrate, login_manager, mail
│   ├── modules/
│   │   ├── auth/                # Login, Registo de Oficina, Logout
│   │   ├── dashboard/           # Painel principal com métricas
│   │   ├── clientes/            # CRUD Clientes
│   │   ├── veiculos/            # CRUD Viaturas
│   │   ├── pecas/               # CRUD Peças/Componentes (stock)
│   │   ├── servicos/            # CRUD Serviços (mão de obra)
│   │   ├── os/                  # Ordens de Serviço
│   │   └── notificacoes/        # PDF, Email, WhatsApp
│   ├── templates/               # Templates Jinja2 (dark theme)
│   ├── static/                  # CSS, JS, imagens
│   └── utils/
│       └── auth.py              # requer_perfil() decorator
├── agents/                      # Definições de agentes IA
├── .kilo/agent/                 # Conhecimento canónico
├── backups/                     # Cópias de segurança da BD
├── migrations/                  # Alembic/Flask-Migrate
├── config.py                    # Configurações
├── requirements.txt             # Dependências Python
└── run.py                       # Ponto de entrada
```

## 3. Modelagem do Banco de Dados

Todas as entidades têm `empresa_id` para isolamento multi-tenant.

| Entidade | Campos Principais (PT-PT) |
|---|---|
| **Empresa** | `razao_social`, `nome_fantasia`, `nif`, `telefone`, `endereco`, `cidade` |
| **Utilizador** | `empresa_id`, `nome`, `email`, `senha_hash`, `papel` (admin/gerente/rececionista/mecanico), `ativo` |
| **Cliente** | `empresa_id`, `nome`, `nif`, `telefone`, `email`, `endereco`, `cidade`, `observacoes`, `ativo` |
| **Viatura** | `empresa_id`, `cliente_id`, `placa` (matrícula), `marca`, `modelo`, `ano_fabricacao`, `ano_modelo`, `cor`, `km_atual`, `combustivel` |
| **Peça** | `empresa_id`, `codigo_referencia`, `descricao`, `marca`, `preco_custo`, `preco_venda`, `estoque_atual`, `estoque_minimo`, `localizacao` |
| **Serviço** | `empresa_id`, `descricao`, `categoria`, `preco_padrao`, `tempo_estimado_minutos` |
| **Ordem de Serviço** | `numero_os`, `tipo`, `status`, `cliente_id`, `veiculo_id`, `defeito_reclamado`, `diagnostico_tecnico`, `valor_total`, `forma_pagamento` |
| **Item de Serviço** | `ordem_servico_id`, `servico_id`, `descricao`, `quantidade`, `valor_unitario`, `subtotal` |
| **Item de Peça** | `ordem_servico_id`, `peca_id`, `descricao`, `quantidade`, `valor_unitario`, `subtotal` |

### Máquina de Estados da OS

```
ORCAMENTO → EM_APROVACAO → APROVADA → EM_ANDAMENTO → CONCLUIDA → ENTREGUE
     ↓            ↓              ↓            ↓              ↓
 CANCELADA    CANCELADA     CANCELADA   AGUARDANDO_PECA  CANCELADA
```

## 4. Perfis de Utilizador

| Perfil | Código | Acesso |
|---|---|---|
| **Administrador** | `admin` | Total (utilizadores, empresa, relatórios, configurações) |
| **Gerente** | `gerente` | CRUD completo (sem gestão de utilizadores/empresa) |
| **Rececionista** | `rececionista` | Clientes, viaturas, abrir OS, notificações |
| **Mecânico** | `mecanico` | Ver/atualizar OS atribuídas, diagnóstico |

## 5. Fases de Desenvolvimento

### Fase 1: Fundação ✅
- Flask, SQLite, Auth multi-tenant, modelos Empresa/Utilizador

### Fase 2: Cadastros Base ✅
- CRUD Clientes, Viaturas, Peças, Serviços

### Fase 3: Motor de OS ✅
- Abertura, itens (peças/serviços), cálculos, estados, baixa de stock

### Fase 4: Exportação e Comunicação ✅
- PDF (xhtml2pdf), WhatsApp (wa.me), Email (Flask-Mail)

### Fase 5: Dashboard e Rotinas ⏳
- Dashboard com gráficos (Chart.js), Backup automático

## 6. Convenções PT-PT

- **NIF** em vez de CPF/CNPJ
- **Cidade / Concelho** em vez de Cidade/UF
- **Matrícula** em vez de Placa (para exibição, campo BD mantém `placa`)
- **Stock** em vez de Estoque (preferencialmente)
- **Viatura** em vez de Veículo (preferencialmente)
- **Euro (€)** — formato: `1.234,56 €`
- **Palavra-passe** em vez de Senha
- **Iniciar sessão** em vez de Fazer Login
- **Registar** em vez de Cadastrar
- **Guardar** em vez de Salvar
- **Pesquisar** em vez de Buscar
