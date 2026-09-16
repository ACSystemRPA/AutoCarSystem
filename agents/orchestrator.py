"""
AutoCarSystem - Orquestrador de Agentes Especialistas
Este script gerencia e orquestra a chamada e acompanhamento dos agentes especialistas do projeto.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Configurar encoding seguro para stdout em consoles Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE_DIR / "agents"
REPORTS_DIR = AGENTS_DIR / "reports"

AGENTS = {
    "pm": {
        "name": "Product Manager & Backlog Maestro",
        "file": "product_manager.md",
        "role": "Orquestração de sprints, roadmap e divisão de tarefas.",
        "icon": "📋"
    },
    "backend": {
        "name": "Backend Specialist (Python/Flask)",
        "file": "backend_engineer.md",
        "role": "Modelagem de dados, Blueprints, regras de negócio e multi-empresa.",
        "icon": "⚙️"
    },
    "frontend": {
        "name": "Frontend & UI/UX Designer",
        "file": "frontend_designer.md",
        "role": "Design refinado, templates Jinja2, TailwindCSS e micro-interações.",
        "icon": "🎨"
    },
    "reporter": {
        "name": "HTML Reporting & Web2PDF Specialist",
        "file": "html_reporter.md",
        "role": "Templates de impressão para OS, cupons e relatórios gerenciais.",
        "icon": "📑"
    }
}

PROJECT_PHASES = [
    {
        "id": 1,
        "title": "Fase 1: Fundação, Arquitetura e Autenticação",
        "description": "Estrutura Flask, SQLite + SQLAlchemy, Multi-Empresa, Login e Registro.",
        "status": "completed", # pending, in_progress, completed
        "progress": 100,
        "tasks": [
            {"title": "Estrutura de diretórios e Application Factory", "done": True, "agent": "backend"},
            {"title": "Configuração do SQLite e Extensões (db, migrate, login)", "done": True, "agent": "backend"},
            {"title": "Models Empresa e Usuario com Multi-tenant", "done": True, "agent": "backend"},
            {"title": "Migração inicial do banco de dados", "done": True, "agent": "backend"},
            {"title": "Blueprint de Autenticação (Login, Logout, Registro)", "done": True, "agent": "backend"},
            {"title": "Telas de Login e Registro com UI Moderna (Tailwind)", "done": True, "agent": "frontend"},
            {"title": "Dashboard Base com Proteção de Sessão e Tenant", "done": True, "agent": "frontend"},
        ]
    },
    {
        "id": 2,
        "title": "Fase 2: Cadastros Base (Clientes, Veículos, Peças, Serviços)",
        "description": "CRUDs fundamentais para a operação da oficina com validações.",
        "status": "completed",
        "progress": 100,
        "tasks": [
            {"title": "Modelos Cliente e Veiculo com FK de Empresa", "done": True, "agent": "backend"},
            {"title": "Modelos Servico e Peca com controle de estoque", "done": True, "agent": "backend"},
            {"title": "Blueprints e Rotas CRUD para cadastros base", "done": True, "agent": "backend"},
            {"title": "Telas e Modais de Cadastros com validação visual", "done": True, "agent": "frontend"},
            {"title": "Suíte de testes automatizados e isolamento multi-tenant", "done": True, "agent": "backend"},
        ]
    },
    {
        "id": 3,
        "title": "Fase 3: Ordem de Serviço (OS), Estoque & Checklist",
        "description": "Coração operacional: Abertura, serviços, peças, checklist visual, cálculo dinâmico e baixa de estoque.",
        "status": "completed",
        "progress": 100,
        "tasks": [
            {"title": "Modelos OrdemServico, ItemServico, ItemPeca e Checklist JSON", "done": True, "agent": "backend"},
            {"title": "Lógica de cálculo de subtotais, descontos e transições de status", "done": True, "agent": "backend"},
            {"title": "Interface moderna de criação, edição e visualização detalhada da OS", "done": True, "agent": "frontend"},
            {"title": "Modais de adição rápida de peças/serviços e baixa automática de estoque", "done": True, "agent": "backend"},
            {"title": "Suíte completa de testes automatizados de integração da Fase 3", "done": True, "agent": "backend"},
        ]
    },
    {
        "id": 4,
        "title": "Fase 4: Relatórios, Exportação em PDF & Impressão",
        "description": "Emissão de comprovantes de OS, orçamentos e relatórios em PDF.",
        "status": "pending",
        "progress": 0,
        "tasks": [
            {"title": "Template HTML para Impressão de OS (A4 Timbrado)", "done": False, "agent": "reporter"},
            {"title": "Template HTML para Cupom Térmico (80mm)", "done": False, "agent": "reporter"},
            {"title": "Integração do motor de renderização PDF no Flask", "done": False, "agent": "backend"},
            {"title": "Relatório de faturamento e serviços por período", "done": False, "agent": "reporter"},
        ]
    },
    {
        "id": 5,
        "title": "Fase 5: Dashboard Gerencial & Polimento",
        "description": "Métricas, faturamento, ticket médio e refinamento de UX.",
        "status": "pending",
        "progress": 0,
        "tasks": [
            {"title": "Queries analíticas para métricas do Dashboard", "done": False, "agent": "backend"},
            {"title": "Interface do Dashboard com Gráficos e Cards de KPIs", "done": False, "agent": "frontend"},
            {"title": "Auditoria de acessibilidade, micro-interações e testes finais", "done": False, "agent": "frontend"},
        ]
    }
]

def list_agents():
    """Lista todos os agentes disponíveis no terminal."""
    print("=" * 60)
    print("🤖 AGENTES ESPECIALISTAS - AUTOCARSYSTEM")
    print("=" * 60)
    for key, info in AGENTS.items():
        print(f"{info['icon']} [{key.upper()}] - {info['name']}")
        print(f"   Papel: {info['role']}")
        print(f"   Arquivo: agents/{info['file']}")
        print("-" * 60)

def get_agent_prompt(agent_key):
    """Retorna o prompt do agente solicitado."""
    if agent_key not in AGENTS:
        print(f"❌ Agente '{agent_key}' não encontrado. Opções: {list(AGENTS.keys())}")
        return None
    agent_file = AGENTS_DIR / AGENTS[agent_key]["file"]
    if agent_file.exists():
        return agent_file.read_text(encoding="utf-8")
    return None

def generate_html_report():
    """Gera um relatório HTML completo e moderno sobre o status do desenvolvimento."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / "project_status.html"
    
    total_tasks = sum(len(p["tasks"]) for p in PROJECT_PHASES)
    done_tasks = sum(sum(1 for t in p["tasks"] if t["done"]) for p in PROJECT_PHASES)
    overall_progress = round((done_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    phases_html = ""
    for phase in PROJECT_PHASES:
        badge_class = {
            "completed": "badge-completed",
            "in_progress": "badge-progress",
            "pending": "badge-pending"
        }.get(phase["status"], "badge-pending")
        
        badge_text = {
            "completed": "Concluída",
            "in_progress": "Em Andamento",
            "pending": "Pendente"
        }.get(phase["status"], "Pendente")
        
        tasks_html = ""
        for t in phase["tasks"]:
            agent_info = AGENTS.get(t["agent"], {"icon": "👤", "name": t["agent"]})
            checked = "checked" if t["done"] else ""
            task_status_class = "task-done" if t["done"] else "task-pending"
            tasks_html += f"""
            <li class="task-item {task_status_class}">
                <div class="task-left">
                    <input type="checkbox" {checked} disabled>
                    <span class="task-title">{t["title"]}</span>
                </div>
                <span class="agent-tag" title="{agent_info['name']}">
                    {agent_info['icon']} {t['agent'].upper()}
                </span>
            </li>
            """
            
        phases_html += f"""
        <div class="phase-card">
            <div class="phase-header">
                <div>
                    <h3 class="phase-title">{phase["title"]}</h3>
                    <p class="phase-desc">{phase["description"]}</p>
                </div>
                <span class="badge {badge_class}">{badge_text}</span>
            </div>
            <ul class="task-list">
                {tasks_html}
            </ul>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoCarSystem - Status de Desenvolvimento</title>
    <style>
        :root {{
            --bg: #090d16;
            --card-bg: #111827;
            --card-border: #1f2937;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --accent: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            padding: 32px 20px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 960px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--card-border);
        }}
        .header-title h1 {{
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        .header-title p {{
            color: var(--text-muted);
            font-size: 14px;
            margin-top: 4px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 18px;
        }}
        .stat-label {{
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: 700;
            margin-top: 4px;
        }}
        .progress-bar-bg {{
            background: #1f2937;
            border-radius: 999px;
            height: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .progress-bar-fill {{
            background: linear-gradient(90deg, #3b82f6, #10b981);
            height: 100%;
            border-radius: 999px;
            width: {overall_progress}%;
        }}
        .phase-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 20px;
        }}
        .phase-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }}
        .phase-title {{
            font-size: 18px;
            font-weight: 600;
        }}
        .phase-desc {{
            color: var(--text-muted);
            font-size: 13px;
            margin-top: 2px;
        }}
        .badge {{
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 999px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge-completed {{ background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-progress {{ background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }}
        .badge-pending {{ background: rgba(156, 163, 175, 0.1); color: #9ca3af; border: 1px solid rgba(156, 163, 175, 0.2); }}
        .task-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .task-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #182234;
            padding: 12px 14px;
            border-radius: 8px;
            border: 1px solid #243248;
        }}
        .task-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .task-done .task-title {{
            text-decoration: line-through;
            color: var(--text-muted);
        }}
        .agent-tag {{
            font-size: 11px;
            font-weight: 600;
            background: #0f172a;
            padding: 3px 8px;
            border-radius: 6px;
            color: #93c5fd;
            border: 1px solid #1e293b;
        }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">
                <h1>AutoCarSystem &bull; Relatório de Desenvolvimento</h1>
                <p>Orquestrador de Agentes Especialistas | Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Progresso Geral</div>
                <div class="stat-value">{overall_progress}%</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Tarefas Concluídas</div>
                <div class="stat-value">{done_tasks} / {total_tasks}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Fase Atual</div>
                <div class="stat-value" style="font-size: 20px; color: #3b82f6;">Fase 1 (Auth & Base)</div>
            </div>
        </div>

        <div>
            {phases_html}
        </div>

        <div class="footer">
            AutoCarSystem &bull; Framework de Orquestração com Impeccable Design &copy; {datetime.now().year}
        </div>
    </div>
</body>
</html>
"""
    report_file.write_text(html_content, encoding="utf-8")
    print(f" Relatório HTML gerado com sucesso: {report_file}")
    return report_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "list":
            list_agents()
        elif cmd == "report":
            generate_html_report()
        elif cmd in AGENTS:
            prompt = get_agent_prompt(cmd)
            print(prompt)
        else:
            print(f"Comando inválido. Opções: list, report, {', '.join(AGENTS.keys())}")
    else:
        list_agents()
        generate_html_report()
