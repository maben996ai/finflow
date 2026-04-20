"""add_video_notified_at

Revision ID: 7e2a1c9d5fb3
Revises: 8ca02d5b99ba
Create Date: 2026-04-19 20:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "7e2a1c9d5fb3"
down_revision: Union[str, None] = "8ca02d5b99ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "videos",
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_videos_notified_at", "videos", ["notified_at"])
    # Backfill：历史数据全部视为已通知，避免升级即爆量推送
    op.execute("UPDATE videos SET notified_at = now() WHERE notified_at IS NULL")


def downgrade() -> None:
    op.drop_index("ix_videos_notified_at", table_name="videos")
    op.drop_column("videos", "notified_at")
