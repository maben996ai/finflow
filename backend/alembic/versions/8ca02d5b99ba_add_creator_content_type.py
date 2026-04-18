"""add_creator_content_type

Revision ID: 8ca02d5b99ba
Revises: d1f92a40cf92
Create Date: 2026-04-18 19:18:04.980483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8ca02d5b99ba'
down_revision: Union[str, None] = 'd1f92a40cf92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

content_type_enum = sa.Enum('video', 'article', 'news', 'market', name='contenttype')


def upgrade() -> None:
    content_type_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('creators', sa.Column(
        'content_type',
        content_type_enum,
        server_default='video',
        nullable=False,
    ))


def downgrade() -> None:
    op.drop_column('creators', 'content_type')
    content_type_enum.drop(op.get_bind(), checkfirst=True)
