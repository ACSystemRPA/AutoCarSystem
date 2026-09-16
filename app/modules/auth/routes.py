from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.modules.auth import auth_bp
from app.extensions import db
from app.models import Empresa, Usuario

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        lembrar = True if request.form.get('lembrar') else False
        
        if not email or not senha:
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('auth/login.html')
        
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario or not usuario.check_password(senha):
            flash('Credenciais inválidas. Verifique seu e-mail e senha.', 'danger')
            return render_template('auth/login.html')
        
        login_user(usuario, remember=lembrar)
        flash(f'Bem-vindo de volta, {usuario.nome}!', 'success')
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard.index')
        return redirect(next_page)
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        razao_social = request.form.get('razao_social', '').strip()
        nome_fantasia = request.form.get('nome_fantasia', '').strip()
        cnpj = request.form.get('cnpj', '').strip() or None
        telefone = request.form.get('telefone', '').strip()
        cidade = request.form.get('cidade', '').strip()
        
        nome = request.form.get('nome_admin', '').strip() or request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        
        if not all([razao_social, nome, email, senha]):
            flash('Preencha todos os campos obrigatórios marcados com (*).', 'warning')
            return render_template('auth/register.html')
            
        if len(senha) < 6:
            flash('A senha deve possuir no mínimo 6 caracteres.', 'warning')
            return render_template('auth/register.html')
            
        if cnpj and Empresa.query.filter_by(cnpj=cnpj).first():
            flash('Já existe uma oficina cadastrada com este CNPJ/CPF.', 'danger')
            return render_template('auth/register.html')
            
        if Usuario.query.filter_by(email=email).first():
            flash('Este e-mail já está em uso por outro usuário.', 'danger')
            return render_template('auth/register.html')
            
        try:
            nova_empresa = Empresa(
                razao_social=razao_social,
                nome_fantasia=nome_fantasia or razao_social,
                cnpj=cnpj,
                telefone=telefone,
                cidade=cidade
            )
            db.session.add(nova_empresa)
            db.session.flush() # Gera o ID da empresa antes do commit
            
            novo_usuario = Usuario(
                empresa_id=nova_empresa.id,
                nome=nome,
                email=email,
                papel='admin'
            )
            novo_usuario.set_password(senha)
            db.session.add(novo_usuario)
            
            db.session.commit()
            
            login_user(novo_usuario)
            flash(f'Oficina "{nova_empresa.nome_fantasia}" criada com sucesso! Bem-vindo ao AutoCarSystem.', 'success')
            return redirect(url_for('dashboard.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao criar a conta: {str(e)}', 'danger')
            return render_template('auth/register.html')
            
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema com segurança.', 'info')
    return redirect(url_for('auth.login'))
