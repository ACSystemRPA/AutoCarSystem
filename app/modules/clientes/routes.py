from flask import render_template, redirect, url_for, flash, request
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
            (Cliente.nif.ilike(f'%{busca}%')) |
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
        nif = request.form.get('nif', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        codigo_postal = request.form.get('codigo_postal', '').strip()
        endereco = request.form.get('endereco', '').strip()
        localidade = request.form.get('localidade', '').strip()
        concelho = request.form.get('concelho', '').strip()
        distrito = request.form.get('distrito', '').strip()
        observacoes = request.form.get('observacoes', '').strip()

        if not nome:
            flash('O nome do cliente é obrigatório.', 'danger')
            return render_template('clientes/form.html', cliente=None)

        novo_cliente = Cliente(
            empresa_id=current_user.empresa_id,
            nome=nome,
            nif=nif,
            telefone=telefone,
            email=email,
            codigo_postal=codigo_postal,
            endereco=endereco,
            localidade=localidade,
            cidade=concelho,
            distrito=distrito,
            observacoes=observacoes
        )
        
        db.session.add(novo_cliente)
        db.session.commit()
        flash(f'Cliente "{nome}" registado com sucesso!', 'success')
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
        nif = request.form.get('nif', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        codigo_postal = request.form.get('codigo_postal', '').strip()
        endereco = request.form.get('endereco', '').strip()
        localidade = request.form.get('localidade', '').strip()
        concelho = request.form.get('concelho', '').strip()
        distrito = request.form.get('distrito', '').strip()
        observacoes = request.form.get('observacoes', '').strip()

        if not nome:
            flash('O nome do cliente é obrigatório.', 'danger')
            return render_template('clientes/form.html', cliente=cliente)

        cliente.nome = nome
        cliente.nif = nif
        cliente.telefone = telefone
        cliente.email = email
        cliente.codigo_postal = codigo_postal
        cliente.endereco = endereco
        cliente.localidade = localidade
        cliente.cidade = concelho
        cliente.distrito = distrito
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
    flash(f'Cliente "{nome}" e as respetivas viaturas foram removidos com sucesso.', 'info')
    return redirect(url_for('clientes.index'))