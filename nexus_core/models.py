"""
NEXUS Core Data Schemas & Models
Strict adherence to NEXUS Architectural Specifications
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# --- Stage 1 & 2: WorkLens Request & Scoped Context ---

class ContextHarvest(BaseModel):
    terminal_logs: List[str] = Field(default_factory=list, description="Latest 100 lines of terminal logs")
    folder_map: List[str] = Field(default_factory=list, description="Project directory structure")
    relevant_files: Dict[str, str] = Field(default_factory=dict, description="File paths and sampled lines")
    manifests: Dict[str, str] = Field(default_factory=dict, description="package.json, requirements.txt, etc.")

class WorkLensInvestigationRequest(BaseModel):
    query: str = Field(..., description="Developer description of the bug or problem")
    error_message: Optional[str] = Field(None, description="Stack trace or terminal error snippet")
    selected_code: Optional[str] = Field(None, description="Current code snippet developer has highlighted")
    project_root: Optional[str] = Field(None, description="Path to active workspace")
    use_rag: bool = Field(True, description="Query ProblemDNA vector store for past verified cases")
    developer_id: str = Field(default="dev_nexus_primary", description="Identifier of the requesting engineer")

class ToolExecutionLog(BaseModel):
    tool_name: str
    action_description: str
    output: Any
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class WorkLensInvestigationResponse(BaseModel):
    investigation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    root_cause: str
    suggested_diff: str
    suggested_fix_explanation: str
    recommended_verification_steps: List[str]
    confidence_score: float = Field(0.92, ge=0.0, le=1.0)
    tools_executed: List[ToolExecutionLog] = Field(default_factory=list)
    retrieved_problemdna_references: List[Dict[str, Any]] = Field(default_factory=list)
    state: str = Field("INVESTIGATION_COMPLETE")

# --- Stage 3: Developer Evaluation & Feedback ---

class EvaluationRequest(BaseModel):
    investigation_id: str
    developer_satisfied: bool
    feedback_notes: Optional[str] = None
    applied_patch: bool = False

# --- Stage 4: Human API & Visual Expert Escalation ---

class ExpertProfile(BaseModel):
    id: str
    name: str
    avatar: str
    domain: str
    technical_skills: List[str]
    gitea_contributions_score: float
    problemdna_solved_count: int
    is_available: bool
    status_message: str
    contact_channels: List[str] = Field(default_factory=lambda: ["Chat", "Voice Call", "Huddle"])

class EscalationRequest(BaseModel):
    investigation_id: str
    problem_summary: str
    domain_tags: List[str]
    developer_id: str

class EscalationResponse(BaseModel):
    escalation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    expert_type: str = Field(..., description="'HUMAN_EXPERT' or 'VISUAL_EXPERT'")
    matched_expert: Optional[ExpertProfile] = None
    visual_expert_persona: Optional[Dict[str, Any]] = None
    guidance_steps: List[str]
    attribution: str
    channel_url: Optional[str] = None

# --- Stage 5: Solution Verification & ProblemDNA Record ---

class ProblemDNARecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    problem_description: str
    symptoms: List[str]
    context_artifacts: Dict[str, Any]
    investigation_attempts: List[str]
    root_cause: str
    verified_solution: str
    diff_patch: Optional[str] = None
    verification_steps: List[str]
    verification_evidence: str
    is_verified: bool = True
    technology_tags: List[str]
    project_name: str
    developer_id: str
    expert_involved: Optional[str] = None
    confidence_score: float = 0.95
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class VerifyAndArchiveRequest(BaseModel):
    investigation_id: Optional[str] = None
    title: str
    problem_description: str
    symptoms: List[str]
    context_artifacts: Dict[str, Any] = Field(default_factory=dict)
    investigation_attempts: List[str] = Field(default_factory=list)
    root_cause: str
    verified_solution: str
    diff_patch: Optional[str] = None
    verification_command_or_action: str
    verification_evidence: str
    technology_tags: List[str]
    project_name: str = "Project_Nexus"
    developer_id: str = "dev_nexus_primary"
    expert_involved: Optional[str] = None

# --- Stage 6: SkillQuest Growth Analysis ---

class SkillQuadrantItem(BaseModel):
    name: str
    category: str
    score: float # 0 - 100
    evidence_count: int
    recent_evidence_summary: str

class SkillQuestProfile(BaseModel):
    developer_id: str
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    strong_areas: List[SkillQuadrantItem]
    good_areas: List[SkillQuadrantItem]
    focus_areas: List[SkillQuadrantItem]
    needs_practice: List[SkillQuadrantItem]
    actionable_recommendations: List[Dict[str, Any]]
    total_problems_resolved: int
    evidence_sources: Dict[str, int] # e.g. {"ProblemDNA": 14, "GiteaCommits": 38, "WorkLensSessions": 22}

# --- Personal AI Twin (Long-Term Vision) ---

class PersonalAITwinProfile(BaseModel):
    developer_id: str
    problem_solving_style: str # e.g. "Hypothesis-Driven & Test-First Diagnostic Approach"
    preferred_tools: List[str]
    long_term_career_trajectory: str
    learning_velocity: str
    knowledge_vault_items: List[Dict[str, str]]
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
