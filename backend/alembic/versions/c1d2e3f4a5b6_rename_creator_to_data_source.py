"""rename_creator_to_data_source

Revision ID: c1d2e3f4a5b6
Revises: b4f2e8d91a67
Create Date: 2026-04-19 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "b4f2e8d91a67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. drop 外键约束（按 PostgreSQL 自动生成的命名）
    with op.batch_alter_table("videos") as batch_op:
        batch_op.drop_constraint("uq_videos_creator_platform_video", type_="unique")
    with op.batch_alter_table("crawl_logs") as batch_op:
        batch_op.drop_constraint("crawl_logs_creator_id_fkey", type_="foreignkey")
    with op.batch_alter_table("videos") as batch_op:
        batch_op.drop_constraint("videos_creator_id_fkey", type_="foreignkey")
    with op.batch_alter_table("creators") as batch_op:
        batch_op.drop_constraint("uq_creators_user_platform_creator", type_="unique")

    # 2. rename 表
    op.rename_table("creators", "data_sources")

    # 3. rename enum 类型 platform → sourcetype（需要 AUTOCOMMIT，PG 限制）
    conn.execute(sa.text("ALTER TYPE platform RENAME TO sourcetype"))

    # 4. 添加新枚举值（每次 ADD VALUE 需在独立 DDL 语句执行）
    for val in ("wechat_article", "website", "rss", "pdf"):
        conn.execute(sa.text(f"ALTER TYPE sourcetype ADD VALUE IF NOT EXISTS '{val}'"))

    # 5. rename 列
    op.alter_column("data_sources", "platform", new_column_name="source_type")
    op.alter_column("data_sources", "platform_creator_id", new_column_name="external_id")
    op.alter_column("videos", "creator_id", new_column_name="data_source_id")
    op.alter_column("crawl_logs", "creator_id", new_column_name="data_source_id")

    # 6. 新增 source_config 字段
    op.add_column("data_sources", sa.Column("source_config", sa.JSON(), nullable=True))

    # 7. 重建外键与唯一约束
    op.create_unique_constraint(
        "uq_data_sources_user_type_external",
        "data_sources",
        ["user_id", "source_type", "external_id"],
    )
    op.create_foreign_key(
        "fk_videos_data_source", "videos", "data_sources", ["data_source_id"], ["id"]
    )
    op.create_unique_constraint(
        "uq_videos_data_source_platform_video",
        "videos",
        ["data_source_id", "platform_video_id"],
    )
    op.create_foreign_key(
        "fk_crawl_logs_data_source", "crawl_logs", "data_sources", ["data_source_id"], ["id"]
    )


def downgrade() -> None:
    conn = op.get_bind()

    # 反向：drop 新约束
    with op.batch_alter_table("crawl_logs") as batch_op:
        batch_op.drop_constraint("fk_crawl_logs_data_source", type_="foreignkey")
    with op.batch_alter_table("videos") as batch_op:
        batch_op.drop_constraint("uq_videos_data_source_platform_video", type_="unique")
        batch_op.drop_constraint("fk_videos_data_source", type_="foreignkey")
    with op.batch_alter_table("data_sources") as batch_op:
        batch_op.drop_constraint("uq_data_sources_user_type_external", type_="unique")

    # drop source_config 列
    op.drop_column("data_sources", "source_config")

    # rename 列（反向）
    op.alter_column("crawl_logs", "data_source_id", new_column_name="creator_id")
    op.alter_column("videos", "data_source_id", new_column_name="creator_id")
    op.alter_column("data_sources", "external_id", new_column_name="platform_creator_id")
    op.alter_column("data_sources", "source_type", new_column_name="platform")

    # rename 表（反向）
    op.rename_table("data_sources", "creators")

    # rename enum（反向，注意 enum 值无法真正删除）
    conn.execute(sa.text("ALTER TYPE sourcetype RENAME TO platform"))

    # 重建原约束
    op.create_unique_constraint(
        "uq_creators_user_platform_creator",
        "creators",
        ["user_id", "platform", "platform_creator_id"],
    )
    op.create_foreign_key(None, "videos", "creators", ["creator_id"], ["id"])
    op.create_unique_constraint(
        "uq_videos_creator_platform_video", "videos", ["creator_id", "platform_video_id"]
    )
    op.create_foreign_key(None, "crawl_logs", "creators", ["creator_id"], ["id"])
