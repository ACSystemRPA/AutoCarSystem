from flask import render_template
from flask_login import login_required, current_user
from app.modules.dashboard import dashboard_bp
from app.extensions import db
from app.models import OrdemServico, Veiculo, Cliente, Peca

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Coletar estatísticas reais do banco de dados
    empresa_id = current_user.empresa_id
    
    total_os_andamento = OrdemServico.query.filter_by(empresa_id=empresa_id, status='EM_ANDAMENTO').count()
    total_veiculos = Veiculo.query.filter_by(empresa_id=empresa_id).count()
    total_clientes = Cliente.query.filter_by(empresa_id=empresa_id, ativo=True).count()
    
    # Faturamento deste mês (soma de totais de OS concluídas/entregues)
    from datetime import datetime
    import calendar
    
    hoje = datetime.utcnow()
    primeiro_dia = datetime(hoje.year, hoje.month, 1)
    ultimo_dia = datetime(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1], 23, 59, 59)
    
    faturamento_query = db.session.query(db.func.sum(OrdemServico.valor_total)).filter(
        OrdemServico.empresa_id == empresa_id,
        OrdemServico.status.in_(['CONCLUIDA', 'ENTREGUE']),
        OrdemServico.data_abertura >= primeiro_dia,
        OrdemServico.data_abertura <= ultimo_dia
    ).scalar()
    
    faturamento_mes = faturamento_query or 0.0

    return render_template(
        'dashboard/index.html',
        usuario=current_user,
        empresa=current_user.empresa,
        stats={
            'os_andamento': total_os_andamento,
            'total_veiculos': total_veiculos,
            'total_clientes': total_clientes,
            'faturamento_mes': faturamento_mes
        }
    )
