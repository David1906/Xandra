"""Add fixture mode

Revision ID: c681db10315a
Revises: c3cde4c9cad2
Create Date: 2023-04-14 12:23:59.894018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c681db10315a'
down_revision = 'c3cde4c9cad2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fixtures', sa.Column('mode', sa.Integer(), nullable=False, default=0))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fixtures', 'mode')
    # ### end Alembic commands ###
