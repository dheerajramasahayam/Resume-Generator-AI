"""Add generation counters to User

Revision ID: 49223461e8e2
Revises: 0b6c3f673e2d
Create Date: 2025-04-10 16:33:08.158660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49223461e8e2'
down_revision = '0b6c3f673e2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - adjusted for SQLite! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Provide server_default='0' for SQLite compatibility
        batch_op.add_column(sa.Column('resume_generations', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('cover_letter_generations', sa.Integer(), nullable=False, server_default='0'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - adjusted for SQLite! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('cover_letter_generations')
        batch_op.drop_column('resume_generations')
    # ### end Alembic commands ###