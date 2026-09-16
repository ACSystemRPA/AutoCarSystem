---
name: AutoCarSystem — Canonical PT-PT Knowledge (Shared)
description: Regras obrigatórias de localização (Portugal), fiscalização, terminologia, moeda e perfis de utilizador. Deve ser respeitado por TODOS os agentes (Backend, Frontend, PM, Reporting).
---

# CONHECIMENTO CANÓNICO — AutoCarSystem (pt-PT)

> **Fonte de verdade única:** `roteiro_projeto.md` e `.kilo/agent/AGENTS.md`.
> O sistema é **de e para Portugal**. Tudo o que for escrito (código, UI, PDF, e-mails, documentação) deve seguir estas regras. **Nunca usar português do Brasil.**

## 1. Termos Obrigatórios

| ❌ Proibido (pt-BR) | ✅ Obrigatório (pt-PT) | Uso |
|---|---|---|
| CNPJ / CPF / CPF-CNPJ | **NIF** (Número de Identificação Fiscal) | Empresa e Cliente |
| Razão Social (só exibição) | **Denominação Social** | Formulários |
| Nome Fantasia | **Nome Comercial** | Formulários |
| Cidade + UF/Estado | **Cidade / Concelho** (+ Distrito opcional) | Endereços |
| CEP | **Código Postal** (XXXX-XXX) | Endereços |
| Cadastrar | **Registar** | Ações |
| Salvar | **Guardar** | Ações |
| Buscar / Pesquisa | **Pesquisar** | Ações |
| Senha | **Palavra-passe** | Auth |
| Logar / Login | **Iniciar sessão** | Auth |
| Usuário | **Utilizador** | Roles/auth |
| Veículo | **Viatura** (preferencial) | UI |
| Placa (exibição) | **Matrícula** | UI |
| Estoque | **Stock** (preferencial) | UI |
| Faturamento | **Facturação** | Financeiro |
| Baixa de estoque | **Atualização de stock** | OS |
| Imprimir | Imprimir (ok) | UI |
| Endereço | **Morada** (preferencial) | UI |
| Excluir | **Eliminar / Remover** | Ações |
| Cliente desde | Cliente desde (ok) | UI |

**Nota BD:** As colunas físicas do SQLite **mantêm** nomes antigos (`cnpj`, `cpf_cnpj`, `cidade`, `placa`) por retrocompatibilidade. Os modelos mapeiam atributos PT-PT (`nif`, `concelho`, `matricula`) para essas colunas via `db.Column('coluna_antiga', ...)`. **Não criar migration desnecessária para renomear colunas.**

## 2. Moeda e Números

- Moeda: **Euro (€)**.
- Formato preferencial: `1 234,56 €` ou `1.234,56 €` (vírgula decimal, ponto/ espaço milhar).
- Filtro Jinja disponível: `{{ valor|currency_pt }}`.
- Em Python, nunca prefixar com R$: use `f"{valor:.2f}".replace('.', ',') + ' €'`.

## 3. Formato de Contactos

- Telefones PT: `+351 9XX XXX XXX` (móvel), `+351 2X XXX XXXX` (fixo).
- WhatsApp: sempre dígitos apenas (`3519XXXXXXXXX`), link `https://api.whatsapp.com/send?phone=...`.

## 4. NIF — Validação

- 9 dígitos (permitir com/sem hífen).
- Regras de validação PT (módulo 11) devem ser implementadas na camada de serviço.
- Nunca usar validação de CPF/CNPJ brasileiro.

## 5. Perfis de Utilizador (papel)

| Código | Nome exibido | Permissões |
|---|---|---|
| `admin` | Administrador | Total: utilizadores, empresa, relatórios, configurações, backup |
| `gerente` | Gerente | CRUD completo; sem gestão de utilizadores/empresa |
| `rececionista` | Rececionista | Clientes, viaturas, abrir OS, notificações |
| `mecanico` | Mecânico | Ver/atualizar OS atribuídas, diagnóstico técnico, sem financeiro |

- Decorator disponível: `from utils.auth import requer_perfil`
- Uso: `@requer_perfil('admin', 'gerente')`.

## 6. Localização do Código

- `lang="pt-PT"` em todos os templates.
- Flash messages sempre em pt-PT.
- Placeholders, tooltips, confirm() e labels: pt-PT.
- Datas: `DD/MM/AAAA`.

## 7. Data e Hora

- Exibição: `%d/%m/%Y` e `%d/%m/%Y às %H:%M`.
- Não usar `%d/%m/%Y` com "às" em pt-PT: usar "às".