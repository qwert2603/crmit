"""empty message

Revision ID: a7b292e8d28a
Revises: f42af39ce5b6
Create Date: 2018-10-04 09:31:19.405456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression

revision = 'a7b292e8d28a'
down_revision = 'f42af39ce5b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('system_users', sa.Column('force_ask_to_login_app', sa.Boolean(), nullable=False,
                                            server_default=expression.false()))
    op.add_column('system_users', sa.Column('force_ask_to_login_site', sa.Boolean(), nullable=False,
                                            server_default=expression.false()))
    op.drop_column('system_users', 'force_ask_to_login')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('system_users', sa.Column('force_ask_to_login', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    op.drop_column('system_users', 'force_ask_to_login_site')
    op.drop_column('system_users', 'force_ask_to_login_app')
    # ### end Alembic commands ###