"""change system_settings to singular

Revision ID: 59933f8e0172
Revises: 787e19ea9fc5
Create Date: 2023-09-28 12:43:37.489824

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "59933f8e0172"
down_revision = "787e19ea9fc5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "system_setting",
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_theme", sa.Text(), nullable=False),
        sa.Column("preferred_language", sa.Text(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="customer",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("system_setting", schema="customer")
    # ### end Alembic commands ###