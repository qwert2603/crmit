"""empty message

Revision ID: 91215eaedf4b
Revises: 9e1c0facd25c
Create Date: 2018-05-21 10:04:40.087608

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '91215eaedf4b'
down_revision = '9e1c0facd25c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('parents', 'email', new_column_name='_email')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('parents', '_email', new_column_name='email')
    # ### end Alembic commands ###
