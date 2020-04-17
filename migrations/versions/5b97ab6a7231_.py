"""empty message

Revision ID: 5b97ab6a7231
Revises: 9c8bf6125f18
Create Date: 2019-08-26 18:19:55.360916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b97ab6a7231'
down_revision = '9c8bf6125f18'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('isGit', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'isGit')
    # ### end Alembic commands ###