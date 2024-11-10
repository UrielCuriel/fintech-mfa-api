"""add otp config columns to user table

Revision ID: f16259f62b21
Revises: 188b74fffbce
Create Date: 2024-11-08 18:09:30.843095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f16259f62b21'
down_revision: Union[str, None] = '188b74fffbce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('otp_enabled', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('otp_secret', sa.String(), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('user', 'otp_secret')
    op.drop_column('user', 'otp_enabled')
    pass
