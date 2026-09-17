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
        palavra_passe = request.form.get('senha', '')
        lembrar = True if request.form.get('lembrar') else False
        
        if not email or not palavra_passe:
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('auth/login.html')
        
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario or not usuario.check_password(palavra_passe):
            flash('Credenciais inválidas. Verifique o seu e-mail e palavra-passe.', 'danger')
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
        nome_comercial = request.form.get('nome_comercial', '').strip()
        nif = request.form.get('nif', '').strip() or None
        telefone = request.form.get('telefone', '').strip()
        concelho = request.form.get('concelho', '').strip()
        
        nome = request.form.get('nome_admin', '').strip() or request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        palavra_passe = request.form.get('senha', '')
        
        if not all([razao_social, nome, email, palavra_passe]):
            flash('Preencha todos os campos obrigatórios marcados com (*).', 'warning')
            return render_template('auth/register.html')
            
        if len(palavra_passe) < 6:
            flash('A palavra-passe deve ter no mínimo 6 caracteres.', 'warning')
            return render_template('auth/register.html')
            
        if nif and Empresa.query.filter_by(nif=nif).first():
            flash('Já existe uma oficina registada com este NIF.', 'danger')
            return render_template('auth/register.html')
            
        if Usuario.query.filter_by(email=email).first():
            flash('Este e-mail já está em uso por outro utilizador.', 'danger')
            return render_template('auth/register.html')
            
        try:
            nova_empresa = Empresa(
                razao_social=razao_social,
                nome_fantasia=nome_comercial or razao_social,
                nif=nif,
                telefone=telefone,
                cidade=concelho
            )
            db.session.add(nova_empresa)
            db.session.flush()
            
            novo_usuario = Usuario(
                empresa_id=nova_empresa.id,
                nome=nome,
                email=email,
                papel='admin'
            )
            novo_usuario.set_password(palavra_passe)
            db.session.add(novo_usuario)
            
            db.session.commit()
            
            login_user(novo_usuario)
            flash(f'Oficina "{nova_empresa.nome_fantasia or nova_empresa.razao_social}" registada com sucesso! Bem-vindo ao AutoCarSystem.', 'success')
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
    flash('Saiu do sistema com segurança.', 'info')
    return redirect(url_for('auth.login'))
