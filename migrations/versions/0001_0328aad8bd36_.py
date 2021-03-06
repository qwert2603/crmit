"""empty message

Revision ID: 0328aad8bd36
Revises: aac668a8ed85
Create Date: 2018-06-07 09:32:18.180539

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0328aad8bd36'
down_revision = 'aac668a8ed85'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('parents', 'passport',
                    existing_type=sa.VARCHAR(length=255),
                    nullable=True)
    op.add_column('payments', sa.Column('comment', sa.String(length=32), nullable=False, server_default=''))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('payments', 'comment')
    op.alter_column('parents', 'passport',
                    existing_type=sa.VARCHAR(length=255),
                    nullable=False)
    # ### end Alembic commands ###
