"""Initial application schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


dataset_type = sa.Enum(
    "pdf",
    "txt",
    "docx",
    "csv",
    "unknown",
    name="dataset_type",
    native_enum=False,
)

dataset_scope = sa.Enum(
    "admin",
    "user",
    name="dataset_scope",
    native_enum=False,
)

llm_type = sa.Enum(
    "simple",
    "rag",
    "user_rag",
    name="llm_type",
    native_enum=False,
)

message_role = sa.Enum(
    "user",
    "assistant",
    "system",
    name="message_role",
    native_enum=False,
)


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        op.execute(
            "CREATE EXTENSION IF NOT EXISTS vector"
        )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "username",
            sa.String(length=255),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_users_username",
        "users",
        ["username"],
        unique=True,
    )

    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "file_name",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "storage_file_name",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "dataset_type",
            dataset_type,
            nullable=False,
        ),
        sa.Column(
            "scope",
            dataset_scope,
            nullable=False,
        ),
        sa.Column(
            "owner_user_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "admin_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "expertise",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "file_size_mb",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "content",
            sa.LargeBinary(),
            nullable=True,
        ),
        sa.Column(
            "content_type",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "is_vectorized",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "embedding_provider",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "embedding_model",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "embedding_dimension",
            sa.Integer(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_datasets_admin_id",
        "datasets",
        ["admin_id"],
        unique=False,
    )
    op.create_index(
        "ix_datasets_name",
        "datasets",
        ["name"],
        unique=False,
    )
    op.create_index(
        "ix_datasets_owner_user_id",
        "datasets",
        ["owner_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_datasets_scope",
        "datasets",
        ["scope"],
        unique=False,
    )

    op.create_table(
        "rag_systems",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "dataset_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["datasets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_rag_systems_dataset_id",
        "rag_systems",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "ix_rag_systems_name",
        "rag_systems",
        ["name"],
        unique=False,
    )

    op.create_table(
        "rag_accesses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "rag_system_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["rag_system_id"],
            ["rag_systems.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "rag_system_id",
            name="uq_rag_access_user_rag_system",
        ),
    )
    op.create_index(
        "ix_rag_accesses_rag_system_id",
        "rag_accesses",
        ["rag_system_id"],
        unique=False,
    )
    op.create_index(
        "ix_rag_accesses_user_id",
        "rag_accesses",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "llm_type",
            llm_type,
            nullable=False,
        ),
        sa.Column(
            "rag_system_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "user_dataset_id",
            sa.Uuid(),
            nullable=True,
        ),
        sa.Column(
            "last_active_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["rag_system_id"],
            ["rag_systems.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_dataset_id"],
            ["datasets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_chat_sessions_rag_system_id",
        "chat_sessions",
        ["rag_system_id"],
        unique=False,
    )
    op.create_index(
        "ix_chat_sessions_user_dataset_id",
        "chat_sessions",
        ["user_dataset_id"],
        unique=False,
    )
    op.create_index(
        "ix_chat_sessions_user_id",
        "chat_sessions",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "role",
            message_role,
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["chat_sessions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_chat_messages_session_id",
        "chat_messages",
        ["session_id"],
        unique=False,
    )

    op.create_table(
        "vector_documents",
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "dataset_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "embedding",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "metadata_json",
            sa.JSON(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_vector_documents_dataset_id",
        "vector_documents",
        ["dataset_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("vector_documents")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("rag_accesses")
    op.drop_table("rag_systems")
    op.drop_table("datasets")
    op.drop_table("users")
