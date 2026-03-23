from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ─── Enums ───────────────────────────────────────────────────────────────────
class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    blocked = "blocked"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Complexity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskCategory(str, Enum):
    Backend = "Backend"
    Frontend = "Frontend"
    ML = "ML"
    Testing = "Testing"
    Design = "Design"
    DevOps = "DevOps"
    General = "General"


# ─── Task Schemas ────────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str
    description: str = ""
    category: str
    complexity: str
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    project_id: str
    is_blocking: bool = False


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    complexity: Optional[str] = None
    assigned_to: Optional[str] = None
    status: str
    due_date: Optional[datetime] = None
    is_blocking: bool = False
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    assignment_reason: Optional[str] = None
    memory_evidence: Optional[list] = None
    project_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskRiskResult(BaseModel):
    task_id: str
    task_title: str
    risk_score: float
    risk_level: str
    top_factors: list[str] = []
    explanation: str = ""


# ─── Member Schemas ──────────────────────────────────────────────────────────
class MemberCreate(BaseModel):
    name: str
    role: str
    skills: list[str] = []
    project_id: str


class MemberResponse(BaseModel):
    id: str
    name: str
    role: Optional[str] = None
    skills: list[str] = []
    project_id: str
    created_at: Optional[datetime] = None
    active_tasks: int = 0
    completion_rate: float = 0.0
    avg_delay_days: float = 0.0

    class Config:
        from_attributes = True


class BehaviorProfile(BaseModel):
    member_id: str
    name: str
    memory_count: int = 0
    raw_memories: list[str] = []
    profile_summary: str = ""
    reliability_score: float = 0.5


# ─── Meeting Schemas ─────────────────────────────────────────────────────────
class MeetingTranscriptRequest(BaseModel):
    transcript: str
    project_id: str


class ActionItem(BaseModel):
    task: str
    assigned_to: str
    due_date: str = ""


class Decision(BaseModel):
    decision: str
    owner: str
    context: str = ""


class Blocker(BaseModel):
    description: str
    raised_by: str
    severity: str = "medium"


class MeetingSummaryResponse(BaseModel):
    date: str = ""
    participants: list[str] = []
    decisions: list[Decision] = []
    action_items: list[ActionItem] = []
    blockers: list[Blocker] = []
    behavioral_insights: list[str] = []
    summary: str = ""
    memories_stored: int = 0


# ─── Chat Schemas ────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    project_id: str
    memory_enabled: bool = True


class ChatResponse(BaseModel):
    response: str
    answer_type: str = "llm"
    memories_used: int = 0
    memory_snippets: list[str] = []


# ─── Assignment Schemas ──────────────────────────────────────────────────────
class AssignTaskRequest(BaseModel):
    task_title: str
    task_category: str
    complexity: str
    deadline: str = ""
    days_remaining: int = 7
    is_blocking: bool = False
    project_id: str
    candidates: list[str] = []
    memory_enabled: bool = True


class AssignTaskResponse(BaseModel):
    assigned_to: str
    risk: str
    risk_score: float = 0.5
    confidence: float = 0.75
    reason: str = ""
    memory_evidence: list[str] = []
    warnings: list[str] = []
    alternative: Optional[str] = None
    strategy_weights: dict = {}
    all_scores: list = []
    acts_trace: list[str] = []
    memory_enabled: bool = True


# ─── Outcome Schemas ─────────────────────────────────────────────────────────
class StoreOutcomeRequest(BaseModel):
    task_id: str
    task_title: str
    member: str
    status: str
    delay_days: int = 0
    blocker_type: str = ""
    reason: str = ""
    insight: str = ""


class StoreOutcomeResponse(BaseModel):
    status: str
    memories_stored: int = 0
    strategy_changed: bool = False
    new_weights: dict = {}


# ─── Sprint Schemas ──────────────────────────────────────────────────────────
class SprintCreate(BaseModel):
    project_id: str
    sprint_number: int
    name: str
    start_date: str
    end_date: str
    goal: str


class SprintResponse(BaseModel):
    id: str
    project_id: str
    sprint_number: int
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    goal: Optional[str] = None
    status: str = "planning"
    ai_plan: Optional[dict] = None
    created_at: Optional[datetime] = None
    task_count: int = 0
    completion_rate: float = 0.0

    class Config:
        from_attributes = True


class SprintPlanRequest(BaseModel):
    project_id: str
    sprint_number: int = 1
    available_members: list[str] = []
    available_tasks: list[dict] = []
    velocity_target: int = 5


class SprintPlanResponse(BaseModel):
    sprint_id: str = ""
    recommended_tasks: list[dict] = []
    assigned_members: dict = {}
    risk_summary: str = ""
    reasoning: str = ""
    memories_used: int = 0
    capacity_warnings: list[str] = []
    sprint_health: Optional[dict] = None


# ─── Agent Schemas ───────────────────────────────────────────────────────────
class AgentInteractionResponse(BaseModel):
    id: str
    interaction_type: str
    user_message: Optional[str] = None
    agent_message: str
    context: Optional[dict] = None
    memories_used: int = 0
    was_proactive: bool = False
    created_at: Optional[datetime] = None


class NudgeResponse(BaseModel):
    id: str
    nudge_type: str
    message: str
    target_member: Optional[str] = None
    task_id: Optional[str] = None
    severity: str = "info"
    was_read: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentStatusResponse(BaseModel):
    agent_name: str = "NEXUS"
    persona: str = ""
    memory_bank_counts: dict = {}
    total_interactions: int = 0
    active_nudges: int = 0
    last_active: str = ""
    is_learning: bool = True


class OnboardingRequest(BaseModel):
    member_name: str
    role: str
    skills: list[str] = []
    project_id: str
    background_notes: str = ""


class OnboardingResponse(BaseModel):
    member_id: str
    welcome_message: str
    initial_tasks_suggested: list[str] = []
    skill_gaps_detected: list[str] = []
    memories_created: int = 0


class BeforeAfterRequest(BaseModel):
    task_title: str
    task_category: str
    complexity: str
    deadline: str = ""
    candidates: list[str] = []
    project_id: str


class BeforeAfterDecision(BaseModel):
    assigned_to: str
    reason: str = ""
    confidence: float = 0.5
    risk_level: str = "MEDIUM"
    memory_evidence: list[str] = []


class BeforeAfterResponse(BaseModel):
    without_memory: BeforeAfterDecision
    with_memory: BeforeAfterDecision
    difference_summary: str = ""
    memory_impact_score: float = 0.0


class StrategyLogEntry(BaseModel):
    id: str
    project_id: str
    trigger_pattern: str
    failure_rate: float
    old_weights: dict = {}
    new_weights: dict = {}
    created_at: Optional[datetime] = None
