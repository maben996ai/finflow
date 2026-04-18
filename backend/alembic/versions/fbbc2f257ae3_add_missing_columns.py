"""add_missing_columns

Revision ID: fbbc2f257ae3
Revises: 93d01521081c
Create Date: 2026-04-18 14:58:30.426129

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'fbbc2f257ae3'
down_revision: Union[str, None] = '93d01521081c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('crawl_logs', sa.Column('videos_found', sa.Integer(), nullable=False, server_default='0'))
    op.alter_column('crawl_logs', 'message', existing_type=sa.Text(), nullable=True)
    op.add_column('videos', sa.Column('raw_data', sa.JSON(), nullable=True))
    op.create_unique_constraint('uq_creators_user_platform_creator', 'creators', ['user_id', 'platform', 'platform_creator_id'])
    op.create_unique_constraint('uq_videos_creator_platform_video', 'videos', ['creator_id', 'platform_video_id'])


def downgrade() -> None:
    op.drop_constraint('uq_videos_creator_platform_video', 'videos', type_='unique')
    op.drop_constraint('uq_creators_user_platform_creator', 'creators', type_='unique')
    op.drop_column('videos', 'raw_data')
    op.alter_column('crawl_logs', 'message', existing_type=sa.Text(), nullable=False)
    op.drop_column('crawl_logs', 'videos_found')
