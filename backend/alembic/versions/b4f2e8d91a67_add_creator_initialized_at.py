"""add_creator_initialized_at

Revision ID: b4f2e8d91a67
Revises: 7e2a1c9d5fb3
Create Date: 2026-04-19 21:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b4f2e8d91a67"
down_revision: Union[str, None] = "7e2a1c9d5fb3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "creators",
        sa.Column("initialized_at", sa.DateTime(timezone=True), nullable=True),
    )
    # 已存在的信源默认视为初始化完成，避免升级后前端全部显示初始化中。
    op.execute("UPDATE creators SET initialized_at = now() WHERE initialized_at IS NULL")


def downgrade() -> None:
    op.drop_column("creators", "initialized_at")
