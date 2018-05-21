"""empty message

Revision ID: 1cce20c5009d
Revises: 91215eaedf4b
Create Date: 2018-05-21 10:13:42.282284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cce20c5009d'
down_revision = '91215eaedf4b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('parents', '_email', new_column_name='email')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('parents', 'email', new_column_name='_email')
    # ### end Alembic commands ###
