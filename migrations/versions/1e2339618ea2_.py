"""empty message

Revision ID: 1e2339618ea2
Revises: bac6d1a0577b
Create Date: 2019-08-20 14:38:37.189718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e2339618ea2'
down_revision = 'bac6d1a0577b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file', sa.Column('msg', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('file', 'msg')
    # ### end Alembic commands ###
