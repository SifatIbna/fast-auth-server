"""User id unique for one-to-one relation

Revision ID: a2abb67e598a
Revises: d902f106927d
Create Date: 2024-06-13 10:17:53.438480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2abb67e598a'
down_revision: Union[str, None] = 'd902f106927d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
