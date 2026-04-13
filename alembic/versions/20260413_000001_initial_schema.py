"""Initial schema with users, emails and legacy backfill.

Revision ID: 20260413_000001
Revises:
Create Date: 2026-04-13 00:00:01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260413_000001"
down_revision = None
branch_labels = None
depends_on = None

LEGACY_USER_EMAIL = "legacy-migration@local.invalid"
LEGACY_USER_NAME = "Legacy Migration User"
LEGACY_USER_HASH = "alembic-managed-no-login"


def _has_table(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_column(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _has_index(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _has_fk(inspector: sa.Inspector, table_name: str, fk_name: str) -> bool:
    return any(fk["name"] == fk_name for fk in inspector.get_foreign_keys(table_name))


def _has_unique_constraint(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    return any(
        constraint.get("column_names") == [column_name]
        for constraint in inspector.get_unique_constraints(table_name)
    )


def _create_enums() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userStatus') THEN
                CREATE TYPE "userStatus" AS ENUM ('pending', 'active', 'deleted', 'blocked');
            END IF;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userRole') THEN
                CREATE TYPE "userRole" AS ENUM ('admin', 'general');
            END IF;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'emailstatus') THEN
                CREATE TYPE emailstatus AS ENUM ('pending', 'sent', 'failed');
            END IF;
        END$$;
        """
    )


def _create_update_timestamp_function() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def _create_users_table(inspector: sa.Inspector) -> None:
    if _has_table(inspector, "users"):
        return

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hash_password", sa.String(length=255), nullable=False),
        sa.Column("email_key", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "active",
                "deleted",
                "blocked",
                name="userStatus",
                create_type=False,
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "role",
            sa.Enum("admin", "general", name="userRole", create_type=False),
            nullable=False,
            server_default="general",
        ),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("email_verify", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )


def _align_users_table(inspector: sa.Inspector) -> None:
    if not _has_table(inspector, "users"):
        return

    if not _has_column(inspector, "users", "name"):
        op.add_column("users", sa.Column("name", sa.String(length=255), nullable=True))
        op.execute("UPDATE users SET name = COALESCE(name, split_part(email, '@', 1), 'User')")
        op.alter_column("users", "name", existing_type=sa.String(length=255), nullable=False)

    if not _has_column(inspector, "users", "hash_password"):
        op.add_column("users", sa.Column("hash_password", sa.String(length=255), nullable=True))
        op.execute(
            f"""
            UPDATE users
            SET hash_password = '{LEGACY_USER_HASH}'
            WHERE hash_password IS NULL
            """
        )
        op.alter_column("users", "hash_password", existing_type=sa.String(length=255), nullable=False)

    optional_columns: list[tuple[str, sa.TypeEngine]] = [
        ("email_key", sa.String(length=255)),
        ("last_login", sa.DateTime()),
        ("email_verify", sa.Boolean()),
    ]
    for column_name, column_type in optional_columns:
        if not _has_column(inspector, "users", column_name):
            op.add_column("users", sa.Column(column_name, column_type, nullable=True))

    if not _has_column(inspector, "users", "status"):
        op.add_column(
            "users",
            sa.Column(
                "status",
                sa.Enum(
                    "pending",
                    "active",
                    "deleted",
                    "blocked",
                    name="userStatus",
                    create_type=False,
                ),
                nullable=True,
                server_default="active",
            ),
        )
        op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")
        op.alter_column("users", "status", nullable=False)

    if not _has_column(inspector, "users", "role"):
        op.add_column(
            "users",
            sa.Column(
                "role",
                sa.Enum("admin", "general", name="userRole", create_type=False),
                nullable=True,
                server_default="general",
            ),
        )
        op.execute("UPDATE users SET role = 'general' WHERE role IS NULL")
        op.alter_column("users", "role", nullable=False)

    if not _has_column(inspector, "users", "created_at"):
        op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
        op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        op.alter_column("users", "created_at", nullable=False)

    if not _has_column(inspector, "users", "updated_at"):
        op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))
        op.execute("UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        op.alter_column("users", "updated_at", nullable=False)


def _ensure_user_indexes(inspector: sa.Inspector) -> None:
    indexes = {
        "ix_users_name": ["name"],
        "ix_users_email": ["email"],
        "ix_users_email_key": ["email_key"],
    }

    for name, columns in indexes.items():
        if not _has_index(inspector, "users", name):
            op.create_index(name, "users", columns, unique=False)

    if not _has_unique_constraint(inspector, "users", "email"):
        op.create_unique_constraint("uq_users_email", "users", ["email"])


def _create_emails_table(inspector: sa.Inspector) -> None:
    if _has_table(inspector, "emails"):
        return

    op.create_table(
        "emails",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("html_body", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "sent", "failed", name="emailstatus", create_type=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def _align_emails_table(inspector: sa.Inspector) -> None:
    if not _has_table(inspector, "emails"):
        return

    required_columns: list[tuple[str, sa.TypeEngine]] = [
        ("user_id", sa.Integer()),
        ("recipient", sa.String(length=255)),
        ("subject", sa.String(length=500)),
        ("body", sa.Text()),
        ("html_body", sa.Text()),
        ("status", sa.Enum("pending", "sent", "failed", name="emailstatus", create_type=False)),
        ("error_message", sa.Text()),
        ("sent_at", sa.DateTime()),
        ("created_at", sa.DateTime()),
        ("updated_at", sa.DateTime()),
    ]

    for column_name, column_type in required_columns:
        if not _has_column(inspector, "emails", column_name):
            nullable = column_name not in {"recipient", "subject"}
            op.add_column("emails", sa.Column(column_name, column_type, nullable=nullable))

    if _has_column(inspector, "emails", "created_at"):
        op.execute("UPDATE emails SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        op.alter_column("emails", "created_at", existing_type=sa.DateTime(), nullable=False)

    if _has_column(inspector, "emails", "updated_at"):
        op.execute("UPDATE emails SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        op.alter_column("emails", "updated_at", existing_type=sa.DateTime(), nullable=False)


def _ensure_legacy_user(bind: sa.Connection) -> int:
    legacy_id = bind.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": LEGACY_USER_EMAIL},
    ).scalar()

    if legacy_id is not None:
        return int(legacy_id)

    inserted_id = bind.execute(
        sa.text(
            """
            INSERT INTO users (
                name,
                email,
                hash_password,
                status,
                role,
                email_verify,
                created_at,
                updated_at
            )
            VALUES (
                :name,
                :email,
                :hash_password,
                'active',
                'admin',
                TRUE,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            RETURNING id
            """
        ),
        {
            "name": LEGACY_USER_NAME,
            "email": LEGACY_USER_EMAIL,
            "hash_password": LEGACY_USER_HASH,
        },
    ).scalar_one()
    return int(inserted_id)


def _backfill_email_user_id(bind: sa.Connection) -> None:
    legacy_user_id = _ensure_legacy_user(bind)
    bind.execute(
        sa.text(
            """
            UPDATE emails
            SET user_id = :legacy_user_id
            WHERE user_id IS NULL
            """
        ),
        {"legacy_user_id": legacy_user_id},
    )


def _ensure_email_constraints(inspector: sa.Inspector) -> None:
    indexes = {
        "idx_emails_recipient": ["recipient"],
        "idx_emails_status": ["status"],
        "idx_emails_created_at": ["created_at"],
        "idx_emails_user_id": ["user_id"],
    }
    for name, columns in indexes.items():
        if not _has_index(inspector, "emails", name):
            op.create_index(name, "emails", columns, unique=False)

    if not _has_fk(inspector, "emails", "fk_emails_user_id_users"):
        op.create_foreign_key(
            "fk_emails_user_id_users",
            "emails",
            "users",
            ["user_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def _ensure_triggers() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")
    op.execute(
        """
        CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column()
        """
    )
    op.execute("DROP TRIGGER IF EXISTS update_emails_updated_at ON emails")
    op.execute(
        """
        CREATE TRIGGER update_emails_updated_at
        BEFORE UPDATE ON emails
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column()
        """
    )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    _create_enums()
    _create_update_timestamp_function()
    _create_users_table(inspector)
    inspector = sa.inspect(bind)
    _align_users_table(inspector)
    inspector = sa.inspect(bind)
    _ensure_user_indexes(inspector)
    inspector = sa.inspect(bind)
    _create_emails_table(inspector)
    inspector = sa.inspect(bind)
    _align_emails_table(inspector)

    _backfill_email_user_id(bind)
    op.alter_column("emails", "user_id", existing_type=sa.Integer(), nullable=False)

    inspector = sa.inspect(bind)
    _ensure_email_constraints(inspector)
    _ensure_triggers()


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_emails_updated_at ON emails")
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    op.drop_table("emails")
    op.drop_table("users")
    op.execute('DROP TYPE IF EXISTS emailstatus')
    op.execute('DROP TYPE IF EXISTS "userRole"')
    op.execute('DROP TYPE IF EXISTS "userStatus"')
