"""001 initial schema

Revision ID: 001
Revises: None
Create Date: 2025-02-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "members",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(100)),
        sa.Column("skills", postgresql.ARRAY(sa.String())),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("category", sa.String(100)),
        sa.Column("complexity", sa.String(20)),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id"), nullable=True),
        sa.Column("status", sa.String(30), server_default="todo"),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("is_blocking", sa.Boolean(), server_default="false"),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("risk_level", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "task_outcomes",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id")),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id")),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("delay_days", sa.Integer(), server_default="0"),
        sa.Column("blocker_type", sa.String(200)),
        sa.Column("reason", sa.Text()),
        sa.Column("insight", sa.Text()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "strategy_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("trigger_pattern", sa.String(200)),
        sa.Column("failure_rate", sa.Float()),
        sa.Column("old_weights", postgresql.JSON()),
        sa.Column("new_weights", postgresql.JSON()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "sprints",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("sprint_number", sa.Integer()),
        sa.Column("name", sa.String(100)),
        sa.Column("start_date", sa.DateTime()),
        sa.Column("end_date", sa.DateTime()),
        sa.Column("goal", sa.Text()),
        sa.Column("status", sa.String(20), server_default="planning"),
        sa.Column("ai_plan", postgresql.JSON()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "agent_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("interaction_type", sa.String(50)),
        sa.Column("user_message", sa.Text()),
        sa.Column("agent_message", sa.Text(), nullable=False),
        sa.Column("context", postgresql.JSON()),
        sa.Column("memories_used", sa.Integer(), server_default="0"),
        sa.Column("was_proactive", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "nudges",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("nudge_type", sa.String(50)),
        sa.Column("message", sa.Text()),
        sa.Column("target_member", sa.String(100)),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("severity", sa.String(20), server_default="info"),
        sa.Column("was_read", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime()),
    )


def downgrade():
    for t in [
        "nudges", "agent_interactions", "sprints", "strategy_log",
        "task_outcomes", "tasks", "members", "projects",
    ]:
        op.drop_table(t)
