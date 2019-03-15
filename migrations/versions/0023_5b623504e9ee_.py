"""empty message

Revision ID: 5b623504e9ee
Revises: 769ed00c4809
Create Date: 2019-03-15 09:59:57.278385

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5b623504e9ee'
down_revision = '769ed00c4809'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('access_tokens', sa.Column('app_version', sa.Text(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('access_tokens', 'app_version')
    # ### end Alembic commands ###
