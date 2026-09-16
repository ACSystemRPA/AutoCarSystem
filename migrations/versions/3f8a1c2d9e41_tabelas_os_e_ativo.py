"""Adiciona tabelas de OS, itens e coluna ativo

Revision ID: 3f8a1c2d9e41
Revises: 2d662a3c2cb5
Create Date: 2026-09-16 16:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f8a1c2d9e41'
down_revision = '2d662a3c2cb5'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Coluna ativo em usuarios (se não existir)
    if 'usuarios' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('usuarios')]
        if 'ativo' not in cols:
            op.add_column('usuarios', sa.Column('ativo', sa.Boolean(), nullable=True))
            op.execute("UPDATE usuarios SET ativo = 1 WHERE ativo IS NULL")

    # Coluna ativo em clientes (se não existir)
    if 'clientes' in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns('clientes')]
        if 'ativo' not in cols:
            op.add_column('clientes', sa.Column('ativo', sa.Boolean(), nullable=True))
            op.execute("UPDATE clientes SET ativo = 1 WHERE ativo IS NULL")

    # Tabela ordens_servico
    if 'ordens_servico' not in insp.get_table_names():
        op.create_table('ordens_servico',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('empresa_id', sa.Integer(), nullable=False),
            sa.Column('numero_os', sa.String(length=20), nullable=False),
            sa.Column('tipo', sa.String(length=20), nullable=True),
            sa.Column('status', sa.String(length=30), nullable=True),
            sa.Column('cliente_id', sa.Integer(), nullable=False),
            sa.Column('veiculo_id', sa.Integer(), nullable=False),
            sa.Column('usuario_responsavel_id', sa.Integer(), nullable=True),
            sa.Column('km_atual', sa.Integer(), nullable=True),
            sa.Column('nivel_combustivel', sa.String(length=20), nullable=True),
            sa.Column('defeito_reclamado', sa.Text(), nullable=True),
            sa.Column('diagnostico_tecnico', sa.Text(), nullable=True),
            sa.Column('observacoes_internas', sa.Text(), nullable=True),
            sa.Column('checklist', sa.Text(), nullable=True),
            sa.Column('valor_servicos', sa.Float(), nullable=True),
            sa.Column('valor_pecas', sa.Float(), nullable=True),
            sa.Column('desconto', sa.Float(), nullable=True),
            sa.Column('valor_total', sa.Float(), nullable=True),
            sa.Column('forma_pagamento', sa.String(length=50), nullable=True),
            sa.Column('data_abertura', sa.DateTime(), nullable=True),
            sa.Column('data_previsao_entrega', sa.DateTime(), nullable=True),
            sa.Column('data_conclusao', sa.DateTime(), nullable=True),
            sa.Column('data_entrega', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
            sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
            sa.ForeignKeyConstraint(['usuario_responsavel_id'], ['usuarios.id'], ),
            sa.ForeignKeyConstraint(['veiculo_id'], ['veiculos.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('numero_os')
        )
        op.create_index('ix_ordens_servico_empresa_id', 'ordens_servico', ['empresa_id'])
        op.create_index('ix_ordens_servico_cliente_id', 'ordens_servico', ['cliente_id'])
        op.create_index('ix_ordens_servico_veiculo_id', 'ordens_servico', ['veiculo_id'])

    # Tabela itens_servico
    if 'itens_servico' not in insp.get_table_names():
        op.create_table('itens_servico',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('ordem_servico_id', sa.Integer(), nullable=False),
            sa.Column('servico_id', sa.Integer(), nullable=True),
            sa.Column('mecanico_id', sa.Integer(), nullable=True),
            sa.Column('descricao', sa.String(length=200), nullable=False),
            sa.Column('quantidade', sa.Float(), nullable=False),
            sa.Column('valor_unitario', sa.Float(), nullable=False),
            sa.Column('desconto', sa.Float(), nullable=True),
            sa.Column('subtotal', sa.Float(), nullable=False),
            sa.ForeignKeyConstraint(['mecanico_id'], ['usuarios.id'], ),
            sa.ForeignKeyConstraint(['ordem_servico_id'], ['ordens_servico.id'], ),
            sa.ForeignKeyConstraint(['servico_id'], ['servicos.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_itens_servico_ordem_servico_id', 'itens_servico', ['ordem_servico_id'])
        op.create_index('ix_itens_servico_servico_id', 'itens_servico', ['servico_id'])

    # Tabela itens_peca
    if 'itens_peca' not in insp.get_table_names():
        op.create_table('itens_peca',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('ordem_servico_id', sa.Integer(), nullable=False),
            sa.Column('peca_id', sa.Integer(), nullable=True),
            sa.Column('descricao', sa.String(length=200), nullable=False),
            sa.Column('quantidade', sa.Float(), nullable=False),
            sa.Column('valor_unitario', sa.Float(), nullable=False),
            sa.Column('desconto', sa.Float(), nullable=True),
            sa.Column('subtotal', sa.Float(), nullable=False),
            sa.ForeignKeyConstraint(['ordem_servico_id'], ['ordens_servico.id'], ),
            sa.ForeignKeyConstraint(['peca_id'], ['pecas.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_itens_peca_ordem_servico_id', 'itens_peca', ['ordem_servico_id'])
        op.create_index('ix_itens_peca_peca_id', 'itens_peca', ['peca_id'])


def downgrade():
    op.drop_index('ix_itens_peca_peca_id', table_name='itens_peca')
    op.drop_index('ix_itens_peca_ordem_servico_id', table_name='itens_peca')
    op.drop_table('itens_peca')
    op.drop_index('ix_itens_servico_servico_id', table_name='itens_servico')
    op.drop_index('ix_itens_servico_ordem_servico_id', table_name='itens_servico')
    op.drop_table('itens_servico')
    op.drop_index('ix_ordens_servico_veiculo_id', table_name='ordens_servico')
    op.drop_index('ix_ordens_servico_cliente_id', table_name='ordens_servico')
    op.drop_index('ix_ordens_servico_empresa_id', table_name='ordens_servico')
    op.drop_table('ordens_servico')
    op.drop_column('clientes', 'ativo')
    op.drop_column('usuarios', 'ativo')