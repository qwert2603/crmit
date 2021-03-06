"""empty message

Revision ID: 0f60b647eb99
Revises: 54ebcc304732
Create Date: 2019-02-28 10:30:14.417310

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0f60b647eb99'
down_revision = '54ebcc304732'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bots',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('system_user_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['system_user_id'], ['system_users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('system_user_id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bots')
    # ### end Alembic commands ###
