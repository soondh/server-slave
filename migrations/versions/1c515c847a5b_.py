"""empty message

Revision ID: 1c515c847a5b
Revises: b18c1d64c2a6
Create Date: 2019-07-18 15:41:25.867415

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1c515c847a5b'
down_revision = 'b18c1d64c2a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('createTime', sa.DateTime(), nullable=True),
    sa.Column('updateTime', sa.DateTime(), nullable=True),
    sa.Column('isDelete', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('address', sa.String(length=50), nullable=True),
    sa.Column('msg', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('createTime', sa.DateTime(), nullable=True),
    sa.Column('updateTime', sa.DateTime(), nullable=True),
    sa.Column('isDelete', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('isTiming', sa.Integer(), nullable=True),
    sa.Column('projectId', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.drop_table('addsvn')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('addsvn',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('createTime', mysql.DATETIME(), nullable=True),
    sa.Column('updateTime', mysql.DATETIME(), nullable=True),
    sa.Column('isDelete', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('projectId', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('address', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('packname', mysql.VARCHAR(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.drop_table('file')
    op.drop_table('project')
    # ### end Alembic commands ###
