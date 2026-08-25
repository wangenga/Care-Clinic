"""switch working hours to day of week

Revision ID: 546db7679118
Revises: a775b19da031
Create Date: 2026-08-25 13:16:01.208481

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '546db7679118'
down_revision: str | Sequence[str] | None = 'a775b19da031'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DELETE FROM working_hours")
    op.drop_column("working_hours", "date")
    op.add_column(
        "working_hours",
        sa.Column("day_of_week", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("working_hours", "day_of_week", server_default=None)
    op.create_unique_constraint(
        "uq_doctor_day_of_week", "working_hours", ["doctor_id", "day_of_week"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_doctor_day_of_week", "working_hours", type_="unique")
    op.drop_column("working_hours", "day_of_week")
    op.add_column(
        "working_hours",
        sa.Column("date", sa.Date(), nullable=False, server_default="2000-01-01"),
    )
    op.alter_column("working_hours", "date", server_default=None)