"""Quitar default en nuevas columnas

Revision ID: 5b9bf345bec1
Revises: 8723dc3973d1
Create Date: 2025-07-03 23:28:45.392315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b9bf345bec1'
down_revision: Union[str, Sequence[str], None] = '8723dc3973d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('children', 'cronological_age', server_default=None)
    op.alter_column('children', 'corrected_age', server_default=None)
    op.alter_column('children', 'exam_date', server_default=None)



def downgrade() -> None:
    """Downgrade schema."""
    pass
