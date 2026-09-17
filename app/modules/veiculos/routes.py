from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Veiculo, Cliente
from app.modules.veiculos import bp

@bp.route('/')
@login_required
def index():
    busca = request.args.get('busca', '').strip()
    query = Veiculo.query.filter_by(empresa_id=current_user.empresa_id)
    
    if busca:
        query = query.join(Cliente).filter(
            (Veiculo.placa.ilike(f'%{busca}%')) |
            (Veiculo.modelo.ilike(f'%{busca}%')) |
            (Veiculo.marca.ilike(f'%{busca}%')) |
            (Veiculo.chassi.ilike(f'%{busca}%')) |
            (Cliente.nome.ilike(f'%{busca}%'))
        )
        
    veiculos = query.order_by(Veiculo.data_cadastro.desc()).all()
    return render_template('veiculos/index.html', veiculos=veiculos, busca=busca)


@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    cliente_id_pre = request.args.get('cliente_id', type=int)
    clientes = Cliente.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).order_by(Cliente.nome.asc()).all()

    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        placa = request.form.get('placa', '').strip().upper()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        ano_fabricacao = request.form.get('ano_fabricacao', type=int)
        ano_modelo = request.form.get('ano_modelo', type=int)
        cor = request.form.get('cor', '').strip()
        km_atual = request.form.get('km_atual', type=int) or 0
        chassi = request.form.get('chassi', '').strip().upper()
        combustivel = request.form.get('combustivel', 'Gasolina')
        observacoes = request.form.get('observacoes', '').strip()

        if not cliente_id or not placa or not modelo or not marca:
            flash('Preencha os campos obrigatórios: Proprietário, Matrícula, Marca e Modelo.', 'danger')
            return render_template('veiculos/form.html', veiculo=None, clientes=clientes, cliente_id_pre=cliente_id_pre)

        cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first()
        if not cliente:
            flash('Cliente inválido selecionado.', 'danger')
            return render_template('veiculos/form.html', veiculo=None, clientes=clientes, cliente_id_pre=cliente_id_pre)

        novo_veiculo = Veiculo(
            empresa_id=current_user.empresa_id,
            cliente_id=cliente_id,
            placa=placa,
            marca=marca,
            modelo=modelo,
            ano_fabricacao=ano_fabricacao,
            ano_modelo=ano_modelo,
            cor=cor,
            km_atual=km_atual,
            chassi=chassi,
            combustivel=combustivel,
            observacoes=observacoes
        )
        
        db.session.add(novo_veiculo)
        db.session.commit()
        flash(f'Viatura {placa} ({modelo}) registada com sucesso!', 'success')
        return redirect(url_for('clientes.detalhes', id=cliente_id))

    return render_template('veiculos/form.html', veiculo=None, clientes=clientes, cliente_id_pre=cliente_id_pre)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    veiculo = Veiculo.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    clientes = Cliente.query.filter_by(empresa_id=current_user.empresa_id, ativo=True).order_by(Cliente.nome.asc()).all()

    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id', type=int)
        placa = request.form.get('placa', '').strip().upper()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        ano_fabricacao = request.form.get('ano_fabricacao', type=int)
        ano_modelo = request.form.get('ano_modelo', type=int)
        cor = request.form.get('cor', '').strip()
        km_atual = request.form.get('km_atual', type=int) or 0
        chassi = request.form.get('chassi', '').strip().upper()
        combustivel = request.form.get('combustivel', 'Gasolina')
        observacoes = request.form.get('observacoes', '').strip()

        if not cliente_id or not placa or not modelo or not marca:
            flash('Preencha os campos obrigatórios: Proprietário, Matrícula, Marca e Modelo.', 'danger')
            return render_template('veiculos/form.html', veiculo=veiculo, clientes=clientes, cliente_id_pre=None)

        veiculo.cliente_id = cliente_id
        veiculo.placa = placa
        veiculo.marca = marca
        veiculo.modelo = modelo
        veiculo.ano_fabricacao = ano_fabricacao
        veiculo.ano_modelo = ano_modelo
        veiculo.cor = cor
        veiculo.km_atual = km_atual
        veiculo.chassi = chassi
        veiculo.combustivel = combustivel
        veiculo.observacoes = observacoes

        db.session.commit()
        flash(f'Viatura {placa} atualizada com sucesso!', 'success')
        return redirect(url_for('veiculos.index'))

    return render_template('veiculos/form.html', veiculo=veiculo, clientes=clientes, cliente_id_pre=None)


@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    veiculo = Veiculo.query.filter_by(id=id, empresa_id=current_user.empresa_id).first_or_404()
    placa = veiculo.placa
    db.session.delete(veiculo)
    db.session.commit()
    flash(f'Viatura {placa} eliminada com sucesso.', 'info')
    return redirect(url_for('veiculos.index'))