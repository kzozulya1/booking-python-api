"""empty message

Revision ID: 7c59668a93a7
Revises: 22f22eca202e
Create Date: 2018-11-30 08:43:54.204697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c59668a93a7'
down_revision = '22f22eca202e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reservation',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('book_from', sa.DateTime(), nullable=False),
    sa.Column('book_to', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('room', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('room', sa.Column('modified_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('room', 'modified_at')
    op.drop_column('room', 'created_at')
    op.drop_table('reservation')
    # ### end Alembic commands ###
