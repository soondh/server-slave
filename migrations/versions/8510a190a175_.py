"""empty message

Revision ID: 8510a190a175
Revises: 1dfab794873a
Create Date: 2019-08-27 14:59:36.313608

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8510a190a175'
down_revision = '1dfab794873a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('swtich', sa.Integer(), nullable=True))
    op.drop_column('project', 'skwtich')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('skwtich', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('project', 'swtich')
    # ### end Alembic commands ###