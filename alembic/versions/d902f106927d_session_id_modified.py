"""Session id modified

Revision ID: d902f106927d
Revises: ac12ecc9d707
Create Date: 2024-06-13 09:23:02.748099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd902f106927d'
down_revision: Union[str, None] = 'ac12ecc9d707'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
