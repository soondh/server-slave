"""empty message

Revision ID: bac6d1a0577b
Revises: 2883f7071ac6
Create Date: 2019-08-16 17:08:45.708959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bac6d1a0577b'
down_revision = '2883f7071ac6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('dingMsgCode', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('history', 'dingMsgCode')
    # ### end Alembic commands ###
