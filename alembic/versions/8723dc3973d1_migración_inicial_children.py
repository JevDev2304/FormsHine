"""Migración inicial Children

Revision ID: 8723dc3973d1
Revises: 
Create Date: 2025-07-03 23:17:17.925878
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = '8723dc3973d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Agregar nuevas columnas con valores por defecto temporales
    op.add_column('children', sa.Column('cronological_age', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='0'))
    op.add_column('children', sa.Column('corrected_age', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='0'))
    op.add_column('children', sa.Column('exam_date', sa.Date(), nullable=False, server_default='2024-01-01'))

    # Cambiar tipos de columnas existentes
    op.alter_column('children', 'gestational_age',
                    existing_type=sa.INTEGER(),
                    type_=sqlmodel.sql.sqltypes.AutoString(),
                    existing_nullable=False)
    op.alter_column('children', 'head_circumference',
                    existing_type=sa.DOUBLE_PRECISION(precision=53),
                    type_=sqlmodel.sql.sqltypes.AutoString(),
                    existing_nullable=False)

    # Eliminar columna no deseada
    op.drop_column('children', 'document_type')


def downgrade():
    # Revertir cambios hechos arriba
    op.add_column('children', sa.Column('document_type', sa.VARCHAR(length=50), nullable=False, server_default='Registro Civil'))

    op.alter_column('children', 'head_circumference',
                    existing_type=sqlmodel.sql.sqltypes.AutoString(),
                    type_=sa.DOUBLE_PRECISION(precision=53),
                    existing_nullable=False)
    op.alter_column('children', 'gestational_age',
                    existing_type=sqlmodel.sql.sqltypes.AutoString(),
                    type_=sa.INTEGER(),
                    existing_nullable=False)

    op.drop_column('children', 'exam_date')
    op.drop_column('children', 'corrected_age')
    op.drop_column('children', 'cronological_age')
