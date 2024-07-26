"""Timezone naive

Revision ID: 0dd1bd9c70f5
Revises: 3f2ef4a652ce
Create Date: 2024-06-13 11:21:58.854446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dd1bd9c70f5'
down_revision: Union[str, None] = '3f2ef4a652ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
