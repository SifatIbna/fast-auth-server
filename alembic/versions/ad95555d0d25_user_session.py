"""User session

Revision ID: ad95555d0d25
Revises: de3725c15a0d
Create Date: 2024-06-12 15:48:16.490354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad95555d0d25'
down_revision: Union[str, None] = 'de3725c15a0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
