"""User info revision 3.0

Revision ID: 2f7a9aa9c238
Revises: f75e1ca0680c
Create Date: 2024-06-05 10:24:15.999992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f7a9aa9c238'
down_revision: Union[str, None] = 'f75e1ca0680c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
