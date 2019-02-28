"""empty message

Revision ID: 6053f9f75e68
Revises: 53eafd1e2da4
Create Date: 2019-02-28 11:49:57.534763

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6053f9f75e68'
down_revision = '53eafd1e2da4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('developers',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('fio', sa.String(length=255), nullable=False),
                    sa.Column('system_user_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['system_user_id'], ['system_users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('system_user_id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('developers')
    # ### end Alembic commands ###