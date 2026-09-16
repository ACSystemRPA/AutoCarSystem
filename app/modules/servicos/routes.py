from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Servico
from app.modules.servicos import bp

@bp.route('/')
@login_required
def index():
    busca = request.args.get('busca', '').strip()
    query = Servico.query.filter_by(empresa_id=current_user.empresa_id)
    
    if busca:
        query = query.filter(
            (Servico.descricao.ilike(f'%{busca}%')) |
            (Servico.categoria.ilike(f'%{busca}%'))
        )
        
    servicos = query.order_by(Servico.categoria.asc(), Servico.descricao.asc()).all()
    return render_template('servicos/index.html', servicos=servicos, busca=busca)


@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', 'Mecânica Geral').strip()
        preco_padrao = float(request.form.get('preco_padrao', 0) or 0)
        tempo_estimado_minutos = int(request.form.get('tempo_estimado_minutos', 60) or 60)

        if not descricao or preco_padrao < 0:
            flash('Descrição e Preço Padrão válido são obrigatórios.', 'danger')
            return render_template('servicos/form.html', servico=None)

        novo_servico = Servico(
            empresa_id=current_user.empresa_id,
            descricao=descricao,
            categoria=categoria,
            preco_padrao=preco_padrao,
            tempo_estimado_minutos=tempo_estimado_minutos
        )
        
        db.session.add(novo_servico)
        db.session.commit()
        flash(f'Serviço/Mão de obra "{descricao}" cadastrado com sucesso!', 'success')
        return redirect(url_for('servicos.index'))

    return render_template('servicos/form.html', servico=None)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    servico = Servico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()

    if request.method == 'POST':
        servico.descricao = request.form.get('descricao', '').strip()
        servico.categoria = request.form.get('categoria', 'Mecânica Geral').strip()
        servico.preco_padrao = float(request.form.get('preco_padrao', 0) or 0)
        servico.tempo_estimado_minutos = int(request.form.get('tempo_estimado_minutos', 60) or 60)

        if not servico.descricao or servico.preco_padrao < 0:
            flash('Descrição e Preço Padrão válido são obrigatórios.', 'danger')
            return render_template('servicos/form.html', servico=servico)

        db.session.commit()
        flash(f'Serviço "{servico.descricao}" atualizado com sucesso!', 'success')
        return redirect(url_for('servicos.index'))

    return render_template('servicos/form.html', servico=servico)


@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    servico = Servico.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    desc = servico.descricao
    db.session.delete(servico)
    db.session.commit()
    flash(f'Serviço "{desc}" removido da tabela de mão de obra.', 'info')
    return redirect(url_for('servicos.index'))
