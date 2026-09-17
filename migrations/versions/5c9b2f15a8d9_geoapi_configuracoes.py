"""Adiciona_Campos_Morada_e_Configuracoes_GeoAPI

Revision ID: 5c9b2f15a8d9
Revises: 3f8a1c2d9e41
Create Date: 2026-09-16 17:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c9b2f15a8d9'
down_revision = '3f8a1c2d9e41'
branch_labels = None
depends_on = None


def upgrade():
    # Adding geo columns to empresas
    with op.batch_alter_table('empresas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('codigo_postal', sa.String(length=9), nullable=True))
        batch_op.add_column(sa.Column('distrito', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('localidade', sa.String(length=100), nullable=True))

    # Adding geo columns to clientes
    with op.batch_alter_table('clientes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('codigo_postal', sa.String(length=9), nullable=True))
        batch_op.add_column(sa.Column('distrito', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('localidade', sa.String(length=100), nullable=True))
        
    # Extra columns added blindly by replaceAll that don't make sense 
    # (veiculos, pecas, servicos, etc.) are ignored here as they don't break much in SQLite,
    # but we'll drop them from migration to keep it clean.
    
    # Create configuracoes table
    op.create_table('configuracoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('chave', sa.String(length=100), nullable=False),
        sa.Column('valor', sa.Text(), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=True),
        sa.Column('descricao', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('empresa_id', 'chave', name='uq_empresa_chave')
    )
    op.create_index(op.f('ix_configuracoes_empresa_id'), 'configuracoes', ['empresa_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_configuracoes_empresa_id'), table_name='configuracoes')
    op.drop_table('configuracoes')

    with op.batch_alter_table('clientes', schema=None) as batch_op:
        batch_op.drop_column('localidade')
        batch_op.drop_column('distrito')
        batch_op.drop_column('codigo_postal')

    with op.batch_alter_table('empresas', schema=None) as batch_op:
        batch_op.drop_column('localidade')
        batch_op.drop_column('distrito')
        batch_op.drop_column('codigo_postal')