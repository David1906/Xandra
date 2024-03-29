"""Add maintenance

Revision ID: 117f1504ed6c
Revises: 49396c222215
Create Date: 2023-04-20 12:51:31.731847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '117f1504ed6c'
down_revision = '49396c222215'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('maintenance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fixtureId', sa.Integer(), nullable=True),
    sa.Column('fixtureIp', sa.String(length=64), nullable=True),
    sa.Column('employee', sa.Integer(), nullable=True),
    sa.Column('dateTime', sa.DateTime(), nullable=True),
    sa.Column('part', sa.String(length=512), nullable=True),
    sa.Column('action', sa.String(length=512), nullable=True),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.Column('testId', sa.Integer(), nullable=True),
    sa.Column('resultStatus', sa.Boolean(), nullable=True),
    sa.Column('stepLabel', sa.String(length=512), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('maintenance')
    # ### end Alembic commands ###
