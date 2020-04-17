"""empty message

Revision ID: b4d0b44ac132
Revises: 8defef1bfe68
Create Date: 2019-08-26 17:33:08.726296

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b4d0b44ac132'
down_revision = '8defef1bfe68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('groupId', sa.Integer(), nullable=True))
    op.drop_column('project', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('username', mysql.VARCHAR(length=50), nullable=True))
    op.drop_column('project', 'groupId')
    # ### end Alembic commands ###
