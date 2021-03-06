"""empty message

Revision ID: 1dfab794873a
Revises: ebc3b2525d55
Create Date: 2019-08-27 14:59:27.703180

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1dfab794873a'
down_revision = 'ebc3b2525d55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('skwtich', sa.Integer(), nullable=True))
    op.drop_column('project', 'Swtich')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('Swtich', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('project', 'skwtich')
    # ### end Alembic commands ###
