"""empty message

Revision ID: 428ea621969c
Revises: 58e78fda9fcc
Create Date: 2019-03-04 14:29:20.797975

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '428ea621969c'
down_revision = '58e78fda9fcc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_messages_owner_id'), 'messages', ['owner_id'], unique=False)
    op.drop_index('ix_messages_sender_id', table_name='messages')
    op.drop_constraint('messages_sender_id_fkey', 'messages', type_='foreignkey')
    op.create_foreign_key(None, 'messages', 'system_users', ['owner_id'], ['id'])
    op.drop_column('messages', 'sender_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('sender_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.create_foreign_key('messages_sender_id_fkey', 'messages', 'system_users', ['sender_id'], ['id'])
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'], unique=False)
    op.drop_index(op.f('ix_messages_owner_id'), table_name='messages')
    op.drop_column('messages', 'owner_id')
    # ### end Alembic commands ###