from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Cliente, Veiculo
from app.modules.clientes import bp

@bp.route('/')
@login_required
def index():
    busca = request.args.get('busca', '').strip()
    query = Cliente.query.filter_by(empresa_id=current_user.empresa_id)
    
    if busca:
        query = query.filter(
            (Cliente.nome.ilike(f'%{busca}%')) |
            (Cliente.cpf_cnpj.ilike(f'%{busca}%')) |
            (Cliente.telefone.ilike(f'%{busca}%')) |
            (Cliente.email.ilike(f'%{busca}%'))
        )
        
    clientes = query.order_by(Cliente.nome.asc()).all()
    return render_template('clientes/index.html', clientes=clientes, busca=busca)


@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf_cnpj = request.form.get('cpf_cnpj', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('endereco', '').strip()
        cidade = request.form.get('cidade', '').strip()
        observacoes = request.form.get('observacoes', '').strip()

        if not nome:
            flash('O nome do cliente é obrigatório.', 'danger')
            return render_template('clientes/form.html', cliente=None)

        novo_cliente = Cliente(
            empresa_id=current_user.empresa_id,
            nome=nome,
            cpf_cnpj=cpf_cnpj,
            telefone=telefone,
            email=email,
            endereco=endereco,
            cidade=cidade,
            observacoes=observacoes
        )
        
        db.session.add(novo_cliente)
        db.session.commit()
        flash(f'Cliente "{nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('clientes.detalhes', id=novo_cliente.id))

    return render_template('clientes/form.html', cliente=None)


@bp.route('/<int:id>')
@login_required
def detalhes(id):
    cliente = Cliente.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    return render_template('clientes/detalhes.html', cliente=cliente)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    cliente = Cliente.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf_cnpj = request.form.get('cpf_cnpj', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('endereco', '').strip()
        cidade = request.form.get('cidade', '').strip()
        observacoes = request.form.get('observacoes', '').strip()

        if not nome:
            flash('O nome do cliente é obrigatório.', 'danger')
            return render_template('clientes/form.html', cliente=cliente)

        cliente.nome = nome
        cliente.cpf_cnpj = cpf_cnpj
        cliente.telefone = telefone
        cliente.email = email
        cliente.endereco = endereco
        cliente.cidade = cidade
        cliente.observacoes = observacoes

        db.session.commit()
        flash('Dados do cliente atualizados com sucesso!', 'success')
        return redirect(url_for('clientes.detalhes', id=cliente.id))

    return render_template('clientes/form.html', cliente=cliente)


@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    cliente = Cliente.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    nome = cliente.nome
    db.session.delete(cliente)
    db.session.commit()
    flash(f'Cliente "{nome}" e seus vínculos foram removidos com sucesso.', 'info')
    return redirect(url_for('clientes.index'))
