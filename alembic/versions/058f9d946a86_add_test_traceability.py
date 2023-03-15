"""Add test traceability

Revision ID: 058f9d946a86
Revises: 0c8c5702da0b
Create Date: 2023-03-15 14:40:45.304959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '058f9d946a86'
down_revision = '0c8c5702da0b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tests', sa.Column('traceability', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tests', 'traceability')
    # ### end Alembic commands ###