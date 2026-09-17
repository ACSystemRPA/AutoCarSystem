from flask import render_template, jsonify
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

@dashboard_bp.route('/api/dash/fat-ultimos-meses')
@login_required
def api_faturacao_mensal():
    from datetime import datetime, timedelta
    import calendar
    from sqlalchemy import func
    
    empresa_id = current_user.empresa_id
    hoje = datetime.utcnow()
    
    # Gera os últimos 6 meses (labels)
    meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    dados_grafico = []
    
    for i in range(5, -1, -1):
        # A charada dos meses
        cmes = hoje.month - i
        cano = hoje.year
        if cmes <= 0:
            cmes += 12
            cano -= 1
            
        prim_dia = datetime(cano, cmes, 1)
        ult_dia = datetime(cano, cmes, calendar.monthrange(cano, cmes)[1], 23, 59, 59)
        
        sum_fat = db.session.query(func.sum(OrdemServico.valor_total)).filter(
            OrdemServico.empresa_id == empresa_id,
            OrdemServico.status.in_(['CONCLUIDA', 'ENTREGUE']),
            OrdemServico.data_abertura >= prim_dia,
            OrdemServico.data_abertura <= ult_dia
        ).scalar()
        
        dados_grafico.append({
            'label': f"{meses_pt[cmes-1]} {cano}",
            'valor': sum_fat or 0.0
        })
        
    return jsonify({
        'labels': [d['label'] for d in dados_grafico],
        'valores': [d['valor'] for d in dados_grafico]
    })


@dashboard_bp.route('/api/dash/os-status')
@login_required
def api_os_status():
    from sqlalchemy import func
    empresa_id = current_user.empresa_id
    
    contagens = db.session.query(OrdemServico.status, func.count(OrdemServico.id)).filter(
        OrdemServico.empresa_id == empresa_id
    ).group_by(OrdemServico.status).all()
    
    mapa = {k: v for k, v in contagens}
    
    # Cores fixas ou padronizadas do Tailwind/branding
    labels = ['Abertas', 'Em Curso', 'Aguardando Peça', 'Concluídas']
    valores = [
        mapa.get('ABERTA', 0),
        mapa.get('EM_ANDAMENTO', 0),
        mapa.get('AGUARDANDO_PECA', 0) + mapa.get('AGUARDANDO_PECAS', 0),
        mapa.get('CONCLUIDA', 0) + mapa.get('ENTREGUE', 0)
    ]
    
    return jsonify({
        'labels': labels,
        'valores': valores
    })
