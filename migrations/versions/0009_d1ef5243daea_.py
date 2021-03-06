"""empty message

Revision ID: d1ef5243daea
Revises: a0d696dabd58
Create Date: 2018-09-19 18:23:39.688654

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd1ef5243daea'
down_revision = 'a0d696dabd58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('access_tokens', sa.Column('token_hash', sa.String(length=255), nullable=False))
    op.drop_column('access_tokens', 'token')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('access_tokens', sa.Column('token', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_column('access_tokens', 'token_hash')
    # ### end Alembic commands ###
