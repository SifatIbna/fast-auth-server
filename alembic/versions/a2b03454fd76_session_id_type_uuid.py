"""Session id type Uuid

Revision ID: a2b03454fd76
Revises: ad95555d0d25
Create Date: 2024-06-12 16:00:57.855267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2b03454fd76'
down_revision: Union[str, None] = 'ad95555d0d25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
