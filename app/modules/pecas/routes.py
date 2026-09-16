from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Peca
from app.modules.pecas import bp

@bp.route('/')
@login_required
def index():
    busca = request.args.get('busca', '').strip()
    filtro_estoque = request.args.get('filtro_estoque', '')
    query = Peca.query.filter_by(empresa_id=current_user.empresa_id)
    
    if busca:
        query = query.filter(
            (Peca.descricao.ilike(f'%{busca}%')) |
            (Peca.codigo_referencia.ilike(f'%{busca}%')) |
            (Peca.marca.ilike(f'%{busca}%')) |
            (Peca.localizacao.ilike(f'%{busca}%'))
        )
        
    if filtro_estoque == 'baixo':
        query = query.filter(Peca.estoque_atual <= Peca.estoque_minimo)
        
    pecas = query.order_by(Peca.descricao.asc()).all()
    
    # Métricas de estoque
    total_itens = len(pecas)
    itens_baixo_estoque = sum(1 for p in pecas if p.estoque_baixo)
    valor_total_estoque = sum(p.estoque_atual * p.preco_custo for p in pecas)
    
    stats = {
        'total_itens': total_itens,
        'total_baixo_estoque': itens_baixo_estoque,
        'valor_estoque_custo': valor_total_estoque,
        'valor_total_estoque': valor_total_estoque
    }
    
    return render_template('pecas/index.html', 
                           pecas=pecas, 
                           busca=busca, 
                           filtro_estoque=filtro_estoque,
                           stats=stats,
                           total_itens=total_itens,
                           itens_baixo_estoque=itens_baixo_estoque,
                           valor_total_estoque=valor_total_estoque)


@bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if request.method == 'POST':
        codigo_referencia = request.form.get('codigo_referencia', '').strip()
        descricao = request.form.get('descricao', '').strip()
        marca = request.form.get('marca', '').strip()
        unidade_medida = request.form.get('unidade_medida', 'UN').strip()
        preco_custo = float(request.form.get('preco_custo', 0) or 0)
        preco_venda = float(request.form.get('preco_venda', 0) or 0)
        estoque_atual = float(request.form.get('estoque_atual', 0) or 0)
        estoque_minimo = float(request.form.get('estoque_minimo', 0) or 0)
        localizacao = request.form.get('localizacao', '').strip()

        if not descricao or preco_venda <= 0:
            flash('Descrição e Preço de Venda válido são obrigatórios.', 'danger')
            return render_template('pecas/form.html', peca=None)

        nova_peca = Peca(
            empresa_id=current_user.empresa_id,
            codigo_referencia=codigo_referencia,
            descricao=descricao,
            marca=marca,
            unidade_medida=unidade_medida,
            preco_custo=preco_custo,
            preco_venda=preco_venda,
            estoque_atual=estoque_atual,
            estoque_minimo=estoque_minimo,
            localizacao=localizacao
        )
        
        db.session.add(nova_peca)
        db.session.commit()
        flash(f'Peça/Item "{descricao}" adicionado com sucesso ao estoque!', 'success')
        return redirect(url_for('pecas.index'))

    return render_template('pecas/form.html', peca=None)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    peca = Peca.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()

    if request.method == 'POST':
        peca.codigo_referencia = request.form.get('codigo_referencia', '').strip()
        peca.descricao = request.form.get('descricao', '').strip()
        peca.marca = request.form.get('marca', '').strip()
        peca.unidade_medida = request.form.get('unidade_medida', 'UN').strip()
        peca.preco_custo = float(request.form.get('preco_custo', 0) or 0)
        peca.preco_venda = float(request.form.get('preco_venda', 0) or 0)
        peca.estoque_atual = float(request.form.get('estoque_atual', 0) or 0)
        peca.estoque_minimo = float(request.form.get('estoque_minimo', 0) or 0)
        peca.localizacao = request.form.get('localizacao', '').strip()

        if not peca.descricao or peca.preco_venda <= 0:
            flash('Descrição e Preço de Venda válido são obrigatórios.', 'danger')
            return render_template('pecas/form.html', peca=peca)

        db.session.commit()
        flash(f'Peça/Item "{peca.descricao}" atualizado com sucesso!', 'success')
        return redirect(url_for('pecas.index'))

    return render_template('pecas/form.html', peca=peca)


@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    peca = Peca.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    desc = peca.descricao
    db.session.delete(peca)
    db.session.commit()
    flash(f'Item "{desc}" removido do catálogo.', 'info')
    return redirect(url_for('pecas.index'))
