import json
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import OrdemServico, ItemServico, ItemPeca, Cliente, Veiculo, Servico, Peca, Usuario
from app.modules.os import bp

def gerar_proximo_numero_os(empresa_id):
    """Gera um número sequencial amigável para a OS da empresa no ano atual."""
    ano_atual = datetime.utcnow().year
    prefixo = f"OS-{ano_atual}-"
    
    # Busca a última OS da empresa com esse prefixo
    ultima_os = OrdemServico.query.filter(
        OrdemServico.empresa_id == empresa_id,
        OrdemServico.numero_os.like(f"{prefixo}%")
    ).order_by(OrdemServico.id.desc()).first()
    
    if ultima_os and ultima_os.numero_os.startswith(prefixo):
        try:
            ultimo_seq = int(ultima_os.numero_os.replace(prefixo, ""))
            novo_seq = ultimo_seq + 1
        except ValueError:
            novo_seq = 1
    else:
        novo_seq = 1
        
    return f"{prefixo}{novo_seq:04d}"

@bp.route('/')
@login_required
def index():
    status_filtro = request.args.get('status', '').strip()
    busca = request.args.get('busca', '').strip()
    
    query = OrdemServico.query.filter_by(empresa_id=current_user.empresa_id)
    
    if status_filtro:
        query = query.filter_by(status=status_filtro)
        
    if busca:
        query = query.join(Cliente).join(Veiculo).filter(
            db.or_(
                OrdemServico.numero_os.ilike(f'%{busca}%'),
                Cliente.nome.ilike(f'%{busca}%'),
                Veiculo.placa.ilike(f'%{busca}%'),
                Veiculo.modelo.ilike(f'%{busca}%')
            )
        )
        
    ordens = query.order_by(OrdemServico.id.desc()).all()
    
    # Contadores rápidos para o topo da listagem
    total_abertas = OrdemServico.query.filter_by(empresa_id=current_user.empresa_id, status='ABERTA').count()
    total_andamento = OrdemServico.query.filter_by(empresa_id=current_user.empresa_id, status='EM_ANDAMENTO').count()
    total_aguardando = OrdemServico.query.filter_by(empresa_id=current_user.empresa_id, status='AGUARDANDO_PECA').count()
    total_concluidas = OrdemServico.query.filter_by(empresa_id=current_user.empresa_id, status='CONCLUIDA').count()
    
    return render_template(
        'os/index.html',
        ordens=ordens,
        status_filtro=status_filtro,
        busca=busca,
        total_abertas=total_abertas,
        total_andamento=total_andamento,
        total_aguardando=total_aguardando,
        total_concluidas=total_concluidas
    )

@bp.route('/nova', methods=['GET', 'POST'])
@bp.route('/novo', methods=['GET', 'POST'], endpoint='novo')
@login_required
def nova():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        veiculo_id = request.form.get('veiculo_id', type=int)
        tipo = request.form.get('tipo', 'ORDEM_SERVICO')
        km_atual = request.form.get('km_atual', type=int)
        nivel_combustivel = request.form.get('nivel_combustivel', '')
        defeito_reclamado = request.form.get('defeito_reclamado', '').strip()
        diagnostico_tecnico = request.form.get('diagnostico_tecnico', '').strip()
        observacoes_internas = request.form.get('observacoes_internas', '').strip()
        responsavel_id = request.form.get('usuario_responsavel_id', type=int)
        data_previsao_str = request.form.get('data_previsao_entrega', '')
        
        # Validar pertencimento do cliente e veiculo
        cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first()
        veiculo = Veiculo.query.filter_by(id=veiculo_id, empresa_id=current_user.empresa_id).first()
        
        if not cliente or not veiculo:
            flash('Cliente ou Veículo inválido para a sua empresa.', 'danger')
            return redirect(url_for('os.nova'))
            
        data_previsao = None
        if data_previsao_str:
            try:
                data_previsao = datetime.strptime(data_previsao_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    data_previsao = datetime.strptime(data_previsao_str, '%Y-%m-%d')
                except ValueError:
                    pass
                    
        # Montar checklist em formato JSON
        checklist_dados = {
            'estepe': bool(request.form.get('chk_estepe')),
            'macaco': bool(request.form.get('chk_macaco')),
            'chave_roda': bool(request.form.get('chk_chave_roda')),
            'triangulo': bool(request.form.get('chk_triangulo')),
            'documento': bool(request.form.get('chk_documento')),
            'pertences': request.form.get('chk_pertences', '').strip(),
            'avarias_visuais': request.form.get('chk_avarias', '').strip(),
        }
        
        numero_os = gerar_proximo_numero_os(current_user.empresa_id)
        status_inicial = 'ORCAMENTO' if tipo == 'ORCAMENTO' else 'ABERTA'
        
        nova_os = OrdemServico(
            empresa_id=current_user.empresa_id,
            numero_os=numero_os,
            tipo=tipo,
            status=status_inicial,
            cliente_id=cliente.id,
            veiculo_id=veiculo.id,
            usuario_responsavel_id=responsavel_id,
            km_atual=km_atual,
            nivel_combustivel=nivel_combustivel,
            defeito_reclamado=defeito_reclamado,
            diagnostico_tecnico=diagnostico_tecnico,
            observacoes_internas=observacoes_internas,
            checklist=json.dumps(checklist_dados),
            data_previsao_entrega=data_previsao
        )
        
        db.session.add(nova_os)
        db.session.commit()
        
        # Atualiza o km do veículo se informado
        if km_atual and (veiculo.km_atual is None or km_atual > veiculo.km_atual):
            veiculo.km_atual = km_atual
            db.session.commit()
            
        flash(f'Ordem de Serviço #{nova_os.numero_os} aberta com sucesso! Agora você pode adicionar os serviços e peças.', 'success')
        return redirect(url_for('os.detalhes', id=nova_os.id))
        
    clientes = Cliente.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).order_by(Cliente.nome).all()
    veiculos = Veiculo.query.filter_by(empresa_id=current_user.empresa_id).order_by(Veiculo.modelo).all()
    usuarios = Usuario.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
    
    return render_template('os/form.html', os=None, clientes=clientes, veiculos=veiculos, usuarios=usuarios)

@bp.route('/<int:id>')
@login_required
def detalhes(id):
    ordem = OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    
    # Serviços e peças disponíveis para adição rápida no modal
    servicos_disponiveis = Servico.query.filter_by(empresa_id=current_user.empresa_id).order_by(Servico.descricao).all()
    pecas_disponiveis = Peca.query.filter_by(empresa_id=current_user.empresa_id).order_by(Peca.descricao).all()
    mecanicos = Usuario.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
    
    checklist_dict = {}
    if ordem.checklist:
        try:
            checklist_dict = json.loads(ordem.checklist)
        except Exception:
            checklist_dict = {}
            
    return render_template(
        'os/detalhes.html',
        os=ordem,
        servicos_disponiveis=servicos_disponiveis,
        pecas_disponiveis=pecas_disponiveis,
        mecanicos=mecanicos,
        checklist=checklist_dict
    )

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    ordem = OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    
    if request.method == 'POST':
        ordem.tipo = request.form.get('tipo', ordem.tipo)
        ordem.km_atual = request.form.get('km_atual', type=int)
        ordem.nivel_combustivel = request.form.get('nivel_combustivel', '')
        ordem.defeito_reclamado = request.form.get('defeito_reclamado', '').strip()
        ordem.diagnostico_tecnico = request.form.get('diagnostico_tecnico', '').strip()
        ordem.observacoes_internas = request.form.get('observacoes_internas', '').strip()
        ordem.usuario_responsavel_id = request.form.get('usuario_responsavel_id', type=int)
        ordem.forma_pagamento = request.form.get('forma_pagamento', '').strip()
        ordem.desconto = request.form.get('desconto', type=float, default=0.0)
        
        data_previsao_str = request.form.get('data_previsao_entrega', '')
        if data_previsao_str:
            try:
                ordem.data_previsao_entrega = datetime.strptime(data_previsao_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    ordem.data_previsao_entrega = datetime.strptime(data_previsao_str, '%Y-%m-%d')
                except ValueError:
                    pass
                    
        checklist_dados = {
            'estepe': bool(request.form.get('chk_estepe')),
            'macaco': bool(request.form.get('chk_macaco')),
            'chave_roda': bool(request.form.get('chk_chave_roda')),
            'triangulo': bool(request.form.get('chk_triangulo')),
            'documento': bool(request.form.get('chk_documento')),
            'pertences': request.form.get('chk_pertences', '').strip(),
            'avarias_visuais': request.form.get('chk_avarias', '').strip(),
        }
        ordem.checklist = json.dumps(checklist_dados)
        
        ordem.calcular_totais()
        db.session.commit()
        
        flash('Ordem de Serviço atualizada com sucesso!', 'success')
        return redirect(url_for('os.detalhes', id=ordem.id))
        
    clientes = Cliente.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).order_by(Cliente.nome).all()
    veiculos = Veiculo.query.filter_by(empresa_id=current_user.empresa_id).order_by(Veiculo.modelo).all()
    usuarios = Usuario.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).all()
    
    checklist_dict = {}
    if ordem.checklist:
        try:
            checklist_dict = json.loads(ordem.checklist)
        except Exception:
            checklist_dict = {}
            
    return render_template(
        'os/form.html',
        os=ordem,
        clientes=clientes,
        veiculos=veiculos,
        usuarios=usuarios,
        checklist=checklist_dict
    )

@bp.route('/<int:id>/adicionar-servico', methods=['POST'])
@login_required
def adicionar_servico(id):
    ordem = OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    
    servico_id = request.form.get('servico_id', type=int)
    descricao = request.form.get('descricao', '').strip()
    quantidade = request.form.get('quantidade', type=float, default=1.0)
    valor_unitario = request.form.get('valor_unitario', type=float, default=0.0)
    desconto = request.form.get('desconto', type=float, default=0.0)
    mecanico_id = request.form.get('mecanico_id', type=int)
    
    if servico_id:
        servico = Servico.query.filter_by(id=servico_id, empresa_id=current_user.empresa_id).first()
        if servico and not descricao:
            descricao = servico.descricao
        if servico and valor_unitario <= 0:
            valor_unitario = servico.preco_padrao
            
    if not descricao:
        flash('Informe a descrição do serviço.', 'danger')
        return redirect(url_for('os.detalhes', id=ordem.id))
        
    item = ItemServico(
        ordem_servico_id=ordem.id,
        servico_id=servico_id,
        mecanico_id=mecanico_id,
        descricao=descricao,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
        desconto=desconto
    )
    item.calcular_subtotal()
    
    db.session.add(item)
    db.session.flush()
    ordem.calcular_totais()
    db.session.commit()
    
    flash(f'Serviço "{descricao}" adicionado à OS!', 'success')
    return redirect(url_for('os.detalhes', id=ordem.id))

@bp.route('/<int:id>/remover-servico/<int:item_id>', methods=['POST'])
@login_required
def remover_servico(id, item_id):
    ordem = OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    item = ItemServico.query.filter_by(id=item_id, ordem_servico_id=ordem.id).first_or_404()
    
    db.session.delete(item)
    db.session.flush()
    ordem.calcular_totais()
    db.session.commit()
    
    flash('Item de serviço removido.', 'info')
    return redirect(url_for('os.detalhes', id=ordem.id))

@bp.route('/<int:id>/adicionar-peca', methods=['POST'])
@login_required
def adicionar_peca(id):
    ordem = OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    
    peca_id = request.form.get('peca_id', type=int)
    descricao = request.form.get('descricao', '').strip()
    quantidade = request.form.get('quantidade', type=float, default=1.0)
    valor_unitario = request.form.get('valor_unitario', type=float, default=0.0)
    desconto = request.form.get('desconto', type=float, default=0.0)
    
    if peca_id:
        peca = Peca.query.filter_by(id=peca_id, empresa_id=current_user.empresa_id).first()
        if peca:
            if not descricao:
                descricao = peca.descricao
            if valor_unitario <= 0:
                valor_unitario = peca.preco_venda
            # Alerta de stock insuficiente (não bloqueia para orçamentos, mas avisa)
            if peca.quantidade_stock < quantidade:
                flash(f'Atenção: A peça "{peca.descricao}" possui apenas {peca.quantidade_stock} em stock.', 'warning')
                
    if not descricao:
        flash('Informe a descrição da peça.', 'danger')
        return redirect(url_for('os.detalhes', id=ordem.id))
        
    item = ItemPeca(
        ordem_servico_id=ordem.id,
        peca_id=peca_id,
        descricao=descricao,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
        desconto=desconto
    )
    item.calcular_subtotal()
    
    db.session.add(item)
    db.session.flush()
    ordem.calcular_totais()
    db.session.commit()
    
    flash(f'Peça/Produto "{descricao}" adicionado à OS!', 'success')
    return redirect(url_for('os.detalhes', id=ordem.id))

@bp.route('/<int:id>/remover-peca/<int:item_id>', methods=['POST'])
@login_required
def remover_peca(id, item_id):
    ordem = OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    item = ItemPeca.query.filter_by(id=item_id, ordem_servico_id=ordem.id).first_or_404()
    
    db.session.delete(item)
    db.session.flush()
    ordem.calcular_totais()
    db.session.commit()
    
    flash('Item de peça removido.', 'info')
    return redirect(url_for('os.detalhes', id=ordem.id))

@bp.route('/<int:id>/alterar-status', methods=['POST'])
@bp.route('/<int:id>/mudar-status', methods=['POST'], endpoint='mudar_status')
@login_required
def alterar_status(id):
    ordem = OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    novo_status = request.form.get('status', '').strip()
    
    status_validos = ['ORCAMENTO', 'ABERTA', 'EM_ANDAMENTO', 'AGUARDANDO_PECA', 'CONCLUIDA', 'ENTREGUE', 'CANCELADA']
    if novo_status not in status_validos:
        flash('Status inválido.', 'danger')
        return redirect(url_for('os.detalhes', id=ordem.id))
        
    status_anterior = ordem.status
    ordem.status = novo_status
    
    # Regra de negócio: Se foi marcada como CONCLUIDA ou ENTREGUE e antes não estava, efetua a baixa no stock
    if novo_status in ['CONCLUIDA', 'ENTREGUE'] and status_anterior not in ['CONCLUIDA', 'ENTREGUE']:
        ordem.data_conclusao = datetime.utcnow()
        if novo_status == 'ENTREGUE':
            ordem.data_entrega = datetime.utcnow()
            
        # Baixa no stock das peças cadastradas
        for item in ordem.itens_pecas:
            if item.peca_id and item.peca:
                item.peca.quantidade_stock = max(0.0, item.peca.quantidade_stock - item.quantidade)
                
        flash(f'Status alterado para {novo_status} e stock de peças baixado com sucesso!', 'success')
        
    elif novo_status == 'CANCELADA' and status_anterior in ['CONCLUIDA', 'ENTREGUE']:
        # Estorna peças de volta ao stock se a OS for cancelada após conclusão
        for item in ordem.itens_pecas:
            if item.peca_id and item.peca:
                item.peca.quantidade_stock += item.quantidade
        flash('Status alterado para CANCELADA e itens estornados ao stock.', 'warning')
    else:
        flash(f'Status da OS #{ordem.numero_os} atualizado para {novo_status}.', 'success')
        
    db.session.commit()
    return redirect(url_for('os.detalhes', id=ordem.id))

@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    ordem = OrdemServico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    num = ordem.numero_os
    
    # Se já foi concluída, devolve ao stock antes de excluir
    if ordem.status in ['CONCLUIDA', 'ENTREGUE']:
        for item in ordem.itens_pecas:
            if item.peca_id and item.peca:
                item.peca.quantidade_stock += item.quantidade
                
    db.session.delete(ordem)
    db.session.commit()
    
    flash(f'Ordem de Serviço #{num} excluída.', 'info')
    return redirect(url_for('os.index'))

# API para busca dinâmica de veículos do cliente (AJAX / Fetch)
@bp.route('/api/veiculos-cliente/<int:cliente_id>')
@login_required
def api_veiculos_cliente(cliente_id):
    cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first_or_404()
    veiculos = [{
        'id': v.id,
        'placa': v.placa,
        'modelo': v.modelo,
        'marca': v.marca,
        'ano': f"{v.ano_fabricacao or ''}/{v.ano_modelo or ''}".strip('/'),
        'km_atual': v.km_atual or 0
    } for v in cliente.veiculos]
    
    return jsonify({'status': 'success', 'veiculos': veiculos})
