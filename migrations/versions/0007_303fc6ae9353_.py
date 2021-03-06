"""empty message

Revision ID: 303fc6ae9353
Revises: 05ec8f0ec9bf
Create Date: 2018-07-06 16:29:08.484828

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = '303fc6ae9353'
down_revision = '05ec8f0ec9bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('students', sa.Column('filled', sa.Boolean(), nullable=False, server_default=expression.true()))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('students', 'filled')
    # ### end Alembic commands ###
