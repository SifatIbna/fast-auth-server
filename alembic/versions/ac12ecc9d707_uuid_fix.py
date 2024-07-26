"""Uuid fix

Revision ID: ac12ecc9d707
Revises: a2b03454fd76
Create Date: 2024-06-12 16:01:42.125128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac12ecc9d707'
down_revision: Union[str, None] = 'a2b03454fd76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
