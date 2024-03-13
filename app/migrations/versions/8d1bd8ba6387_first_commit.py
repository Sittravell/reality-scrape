"""First commit

Revision ID: 8d1bd8ba6387
Revises: 
Create Date: 2023-03-01 20:04:03.226353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d1bd8ba6387'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=True),
    sa.Column('link', sa.String(length=256), nullable=True),
    sa.Column('img_link', sa.String(length=256), nullable=True),
    sa.Column('time', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_id'), 'news', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_news_id'), table_name='news')
    op.drop_table('news')
    # ### end Alembic commands ###