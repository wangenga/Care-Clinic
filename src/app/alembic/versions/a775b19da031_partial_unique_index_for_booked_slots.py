"""partial unique index for booked slots

Revision ID: a775b19da031
Revises: a2e699a22ee6
Create Date: 2026-08-24 21:37:46.438417

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a775b19da031'
down_revision: str | Sequence[str] | None = 'a2e699a22ee6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("uq_doctor_date_timeslot", "appointments", type_="unique")
    op.create_index(
        "uq_doctor_date_timeslot_booked",
        "appointments",
        ["doctor_id", "date", "time_start"],
        unique=True,
        postgresql_where="status = 'booked'",
    )


def downgrade() -> None:
    op.drop_index("uq_doctor_date_timeslot_booked", table_name="appointments")
    op.create_unique_constraint(
        "uq_doctor_date_timeslot",
        "appointments",
        ["doctor_id", "date", "time_start"],
    )