from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json


class Empresa(db.Model):
    __tablename__ = 'empresas'

    id = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(150), nullable=False)
    nome_fantasia = db.Column(db.String(150))
    nif = db.Column('cnpj', db.String(20), unique=True, nullable=True)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(255))
    cidade = db.Column('cidade', db.String(100))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    usuarios = db.relationship('Usuario', back_populates='empresa', cascade="all, delete-orphan")

    @property
    def nome_comercial(self):
        return self.nome_fantasia

    def __repr__(self):
        return f"<Empresa {self.nome_fantasia or self.razao_social}>"


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    PERFIS_PERMITIDOS = ('admin', 'gerente', 'rececionista', 'mecanico')

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    papel = db.Column(db.String(20), default='admin')
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship('Empresa', back_populates='usuarios')

    @property
    def perfil(self):
        return self.papel

    @property
    def is_admin(self):
        return self.papel == 'admin'

    @property
    def is_gerente(self):
        return self.papel == 'gerente'

    @property
    def is_rececionista(self):
        return self.papel == 'rececionista'

    @property
    def is_mecanico(self):
        return self.papel == 'mecanico'

    @property
    def pode_ver_financeiro(self):
        return self.papel in ('admin', 'gerente')

    @property
    def pode_gerir_utilizadores(self):
        return self.papel == 'admin'

    @property
    def pode_gerir_empresa(self):
        return self.papel == 'admin'

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def __repr__(self):
        return f"<Utilizador {self.nome}>"


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False, index=True)
    nome = db.Column(db.String(150), nullable=False)
    nif = db.Column('cpf_cnpj', db.String(20))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    endereco = db.Column(db.String(255))
    cidade = db.Column('cidade', db.String(100))
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship('Empresa', backref=db.backref('clientes', lazy='dynamic', cascade='all, delete-orphan'))
    veiculos = db.relationship('Veiculo', back_populates='cliente', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Cliente {self.nome}>"


class Veiculo(db.Model):
    __tablename__ = 'veiculos'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False, index=True)
    placa = db.Column('placa', db.String(10), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    ano_fabricacao = db.Column(db.Integer)
    ano_modelo = db.Column(db.Integer)
    cor = db.Column(db.String(30))
    km_atual = db.Column(db.Integer, default=0)
    chassi = db.Column(db.String(30))
    combustivel = db.Column(db.String(30), default='Gasolina')
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship('Empresa', backref=db.backref('veiculos', lazy='dynamic', cascade='all, delete-orphan'))
    cliente = db.relationship('Cliente', back_populates='veiculos')

    @property
    def matricula(self):
        return self.placa

    def __repr__(self):
        return f"<Viatura {self.placa} - {self.modelo}>"


class Peca(db.Model):
    __tablename__ = 'pecas'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False, index=True)
    codigo_referencia = db.Column(db.String(50))
    descricao = db.Column(db.String(150), nullable=False)
    marca = db.Column(db.String(60))
    unidade_medida = db.Column(db.String(10), default='UN')
    preco_custo = db.Column(db.Float, default=0.0)
    preco_venda = db.Column(db.Float, nullable=False, default=0.0)
    estoque_atual = db.Column(db.Float, default=0.0)
    estoque_minimo = db.Column(db.Float, default=0.0)
    localizacao = db.Column(db.String(50))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship('Empresa', backref=db.backref('pecas', lazy='dynamic', cascade='all, delete-orphan'))

    @property
    def quantidade_estoque(self):
        return self.estoque_atual

    @property
    def estoque_baixo(self):
        return self.estoque_atual <= self.estoque_minimo

    @property
    def margem_lucro(self):
        if self.preco_custo and self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return 0.0

    def __repr__(self):
        return f"<Peca {self.descricao}>"


class Servico(db.Model):
    __tablename__ = 'servicos'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False, index=True)
    descricao = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(50), default='Mecânica Geral')
    preco_padrao = db.Column(db.Float, nullable=False, default=0.0)
    tempo_estimado_minutos = db.Column(db.Integer, default=60)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship('Empresa', backref=db.backref('servicos', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Servico {self.descricao}>"


class OrdemServico(db.Model):
    __tablename__ = 'ordens_servico'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False, index=True)
    numero_os = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(20), default='ORDEM_SERVICO')
    status = db.Column(db.String(30), default='ABERTA')

    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    usuario_responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    km_atual = db.Column(db.Integer, nullable=True)
    nivel_combustivel = db.Column(db.String(20), nullable=True)
    defeito_reclamado = db.Column(db.Text, nullable=True)
    diagnostico_tecnico = db.Column(db.Text, nullable=True)
    observacoes_internas = db.Column(db.Text, nullable=True)
    checklist = db.Column(db.Text, nullable=True)

    valor_servicos = db.Column(db.Float, default=0.0)
    valor_pecas = db.Column(db.Float, default=0.0)
    desconto = db.Column(db.Float, default=0.0)
    valor_total = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(50), nullable=True)

    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_previsao_entrega = db.Column(db.DateTime, nullable=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    data_entrega = db.Column(db.DateTime, nullable=True)

    empresa = db.relationship('Empresa', backref=db.backref('ordens_servico', lazy='dynamic', cascade='all, delete-orphan'))
    cliente = db.relationship('Cliente', backref=db.backref('ordens_servico', lazy='dynamic'))
    veiculo = db.relationship('Veiculo', backref=db.backref('ordens_servico', lazy='dynamic'))
    responsavel = db.relationship('Usuario', foreign_keys=[usuario_responsavel_id], backref=db.backref('ordens_responsaveis', lazy='dynamic'))

    itens_servicos = db.relationship('ItemServico', backref='ordem_servico', cascade='all, delete-orphan', lazy='dynamic')
    itens_pecas = db.relationship('ItemPeca', backref='ordem_servico', cascade='all, delete-orphan', lazy='dynamic')

    def calcular_totais(self):
        tot_servicos = sum(item.subtotal for item in self.itens_servicos)
        tot_pecas = sum(item.subtotal for item in self.itens_pecas)
        self.valor_servicos = round(tot_servicos, 2)
        self.valor_pecas = round(tot_pecas, 2)
        self.valor_total = max(0.0, round((self.valor_servicos + self.valor_pecas) - (self.desconto or 0.0), 2))

    @property
    def numero(self):
        return self.numero_os

    @property
    def valor_desconto(self):
        return self.desconto or 0.0

    @property
    def combustivel_nivel(self):
        return self.nivel_combustivel

    @property
    def data_previsao(self):
        return self.data_previsao_entrega

    @property
    def observacoes(self):
        return self.observacoes_internas

    @property
    def usuario_abertura(self):
        return self.responsavel

    @property
    def itens_servico(self):
        return self.itens_servicos.all()

    @property
    def itens_peca(self):
        return self.itens_pecas.all()

    @property
    def checklist_dict(self):
        if self.checklist:
            try:
                return json.loads(self.checklist)
            except Exception:
                return {}
        return {}

    @property
    def status_badge_class(self):
        badges = {
            'ORCAMENTO': 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
            'ABERTA': 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
            'EM_ANDAMENTO': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300',
            'AGUARDANDO_PECA': 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300',
            'AGUARDANDO_PECAS': 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300',
            'APROVADA': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
            'CONCLUIDA': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
            'ENTREGUE': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
            'CANCELADA': 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300'
        }
        return badges.get(self.status, 'bg-slate-100 text-slate-800')

    def __repr__(self):
        return f"<OS {self.numero_os} - {self.status}>"


class ItemServico(db.Model):
    __tablename__ = 'itens_servico'

    id = db.Column(db.Integer, primary_key=True)
    ordem_servico_id = db.Column(db.Integer, db.ForeignKey('ordens_servico.id'), nullable=False, index=True)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=True)
    mecanico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    descricao = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Float, nullable=False, default=1.0)
    valor_unitario = db.Column(db.Float, nullable=False, default=0.0)
    desconto = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)

    servico = db.relationship('Servico')
    mecanico = db.relationship('Usuario', foreign_keys=[mecanico_id])

    def calcular_subtotal(self):
        bruto = (self.quantidade or 1.0) * (self.valor_unitario or 0.0)
        self.subtotal = max(0.0, round(bruto - (self.desconto or 0.0), 2))
        return self.subtotal

    @property
    def valor_total(self):
        return self.subtotal

    def __repr__(self):
        return f"<ItemServico {self.descricao} (€{self.subtotal:.2f})>"


class ItemPeca(db.Model):
    __tablename__ = 'itens_peca'

    id = db.Column(db.Integer, primary_key=True)
    ordem_servico_id = db.Column(db.Integer, db.ForeignKey('ordens_servico.id'), nullable=False, index=True)
    peca_id = db.Column(db.Integer, db.ForeignKey('pecas.id'), nullable=True)

    descricao = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Float, nullable=False, default=1.0)
    valor_unitario = db.Column(db.Float, nullable=False, default=0.0)
    desconto = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)

    peca = db.relationship('Peca')

    def calcular_subtotal(self):
        bruto = (self.quantidade or 1.0) * (self.valor_unitario or 0.0)
        self.subtotal = max(0.0, round(bruto - (self.desconto or 0.0), 2))
        return self.subtotal

    @property
    def valor_total(self):
        return self.subtotal

    def __repr__(self):
        return f"<ItemPeca {self.descricao} (€{self.subtotal:.2f})>"


from app.extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))