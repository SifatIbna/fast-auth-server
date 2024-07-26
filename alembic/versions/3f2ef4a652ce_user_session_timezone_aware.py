"""User session timezone aware

Revision ID: 3f2ef4a652ce
Revises: a2abb67e598a
Create Date: 2024-06-13 11:11:50.306895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f2ef4a652ce'
down_revision: Union[str, None] = 'a2abb67e598a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
