import uuid
import json
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.database import Base


def _uuid():
    return str(uuid.uuid4())


class Project(Base):
    __tablename__ = "projects"
    id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("Member", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    sprints = relationship("Sprint", back_populates="project")


class Member(Base):
    __tablename__ = "members"
    id = Column(String(36), primary_key=True, default=_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"))
    name = Column(String(100), nullable=False)
    role = Column(String(100))
    _skills = Column("skills", Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="members")
    task_outcomes = relationship("TaskOutcome", back_populates="member")

    @property
    def skills(self):
        try:
            return json.loads(self._skills) if self._skills else []
        except (json.JSONDecodeError, TypeError):
            return []

    @skills.setter
    def skills(self, value):
        self._skills = json.dumps(value) if isinstance(value, list) else "[]"


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String(36), primary_key=True, default=_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"))
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100))
    complexity = Column(String(20))
    assigned_to = Column(String(36), ForeignKey("members.id"), nullable=True)
    status = Column(String(30), default="todo")
    due_date = Column(DateTime, nullable=True)
    is_blocking = Column(Boolean, default=False)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(10), nullable=True)
    confidence = Column(Float, nullable=True)
    assignment_reason = Column(Text, nullable=True)
    memory_evidence = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("Member", foreign_keys=[assigned_to])
    outcomes = relationship("TaskOutcome", back_populates="task")


class TaskOutcome(Base):
    __tablename__ = "task_outcomes"
    id = Column(String(36), primary_key=True, default=_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"))
    member_id = Column(String(36), ForeignKey("members.id"))
    completed_at = Column(DateTime)
    delay_days = Column(Integer, default=0)
    blocker_type = Column(String(200), nullable=True)
    reason = Column(Text, nullable=True)
    insight = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="outcomes")
    member = relationship("Member", back_populates="task_outcomes")


class StrategyLog(Base):
    __tablename__ = "strategy_log"
    id = Column(String(36), primary_key=True, default=_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"))
    trigger_pattern = Column(String(200))
    failure_rate = Column(Float)
    old_weights = Column(JSON)
    new_weights = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Sprint(Base):
    __tablename__ = "sprints"
    id = Column(String(36), primary_key=True, default=_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"))
    sprint_number = Column(Integer)
    name = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    goal = Column(Text)
    status = Column(String(20), default="planning")
    ai_plan = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="sprints")


class AgentInteraction(Base):
    __tablename__ = "agent_interactions"
    id = Column(String(36), primary_key=True, default=_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"))
    interaction_type = Column(String(50))
    user_message = Column(Text, nullable=True)
    agent_message = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    memories_used = Column(Integer, default=0)
    was_proactive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Nudge(Base):
    __tablename__ = "nudges"
    id = Column(String(36), primary_key=True, default=_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"))
    nudge_type = Column(String(50))
    message = Column(Text)
    target_member = Column(String(100), nullable=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=True)
    severity = Column(String(20), default="info")
    was_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
