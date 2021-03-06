"""empty message

Revision ID: 57106c479ac1
Revises: af2a18a6441e
Create Date: 2019-07-19 17:35:24.007581

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '57106c479ac1'
down_revision = 'af2a18a6441e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('date', sa.DateTime(), nullable=True))
    op.drop_column('history', 'dates')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('dates', mysql.DATETIME(), nullable=True))
    op.drop_column('history', 'date')
    # ### end Alembic commands ###
