"""empty message

Revision ID: d64f7a2a49e3
Revises: 1c515c847a5b
Create Date: 2019-07-18 16:21:59.969579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd64f7a2a49e3'
down_revision = '1c515c847a5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('ip', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'ip')
    # ### end Alembic commands ###
