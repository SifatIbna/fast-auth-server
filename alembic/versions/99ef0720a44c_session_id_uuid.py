"""Session id uuid

Revision ID: 99ef0720a44c
Revises: 0dd1bd9c70f5
Create Date: 2024-06-14 15:47:12.997292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99ef0720a44c'
down_revision: Union[str, None] = '0dd1bd9c70f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
