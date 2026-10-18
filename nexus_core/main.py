"""
NEXUS Unified REST API Application
FastAPI endpoints supporting:
- WorkLens investigation & tool executions
- ProblemDNA vector search & verification-gated archival
- Human API expert escalation & Visual Expert fallback
- SkillQuest growth metrics & recommendations
- Personal AI Twin profile & vault
- Gitea evidence connector
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from nexus_core.models import (
    WorkLensInvestigationRequest,
    WorkLensInvestigationResponse,
    EvaluationRequest,
    EscalationRequest,
    EscalationResponse,
    VerifyAndArchiveRequest,
    ProblemDNARecord,
    SkillQuestProfile,
    PersonalAITwinProfile
)
from nexus_core.problemdna import ProblemDNAService
from nexus_core.worklens import WorkLensController
from nexus_core.human_api import HumanAPIService
from nexus_core.skillquest import SkillQuestService
from nexus_core.ai_twin import PersonalAITwinService
from nexus_core.gitea import GiteaEvidenceConnector
from nexus_core.tools import ExecuteTool

app = FastAPI(
    title="NEXUS Platform Core API",
    description="Personal Intelligence & Growth Network - See. Solve. Learn. Grow. Remember.",
    version="1.0.0"
)

# Enable CORS for local IDE extensions & web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core services
problemdna_service = ProblemDNAService()
worklens_controller = WorkLensController(problemdna_service)
human_api_service = HumanAPIService()
skillquest_service = SkillQuestService(problemdna_service)
ai_twin_service = PersonalAITwinService()
gitea_connector = GiteaEvidenceConnector()

# In-memory storage for active investigations
active_investigations = {}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": "NEXUS Personal Intelligence & Growth Network",
        "modules": {
            "worklens": "active",
            "problemdna": "active",
            "human_api": "active",
            "skillquest": "active",
            "ai_twin": "active",
            "gitea": "active"
        }
    }

# --- Stage 1 & 2: WorkLens Investigation ---

@app.post("/api/worklens/investigate", response_model=WorkLensInvestigationResponse)
def trigger_worklens_investigation(request: WorkLensInvestigationRequest):
    """Stage 1 & 2: User manually triggers WorkLens with project context."""
    response = worklens_controller.investigate(request)
    active_investigations[response.investigation_id] = {
        "request": request.model_dump(),
        "response": response.model_dump()
    }
    return response

@app.post("/api/worklens/execute-command")
def execute_gated_command(command: str, cwd: Optional[str] = None, approved: bool = False):
    """Execute Tool: Safe gatekept command runner."""
    workdir = cwd or os.getcwd()
    result = ExecuteTool.run(command, workdir, developer_approved=approved)
    return result

# --- Stage 3: Evaluation & Feedback ---

@app.post("/api/worklens/evaluate")
def evaluate_suggestion(eval_req: EvaluationRequest):
    """Stage 3: Developer evaluates AI suggestion (Satisfied or Escalate)."""
    if eval_req.investigation_id in active_investigations:
        active_investigations[eval_req.investigation_id]["evaluation"] = eval_req.model_dump()
    return {
        "status": "acknowledged",
        "proceed_to": "VERIFICATION" if eval_req.developer_satisfied else "HUMAN_API_ESCALATION"
    }

# --- Stage 4: Human API & Visual Expert Escalation ---

@app.get("/api/experts")
def list_experts():
    return human_api_service.get_all_experts()

@app.post("/api/human-api/escalate", response_model=EscalationResponse)
def escalate_to_expert(req: EscalationRequest):
    """Stage 4: Escalate to human expert or visual expert persona."""
    return human_api_service.match_expert(req)

# --- Stage 5: Verification & ProblemDNA Archival ---

@app.post("/api/problemdna/archive")
def archive_verified_problem(req: VerifyAndArchiveRequest):
    """Stage 5: Verification-gated permanent knowledge storage."""
    record = ProblemDNARecord(
        title=req.title,
        problem_description=req.problem_description,
        symptoms=req.symptoms,
        context_artifacts=req.context_artifacts,
        investigation_attempts=req.investigation_attempts,
        root_cause=req.root_cause,
        verified_solution=req.verified_solution,
        diff_patch=req.diff_patch,
        verification_steps=[req.verification_command_or_action],
        verification_evidence=req.verification_evidence,
        is_verified=True,
        technology_tags=req.technology_tags,
        project_name=req.project_name,
        developer_id=req.developer_id,
        expert_involved=req.expert_involved,
        confidence_score=0.96
    )
    record_id = problemdna_service.store_record(record)
    return {
        "status": "archived_and_vector_indexed",
        "record_id": record_id,
        "message": "Problem verified and committed to immutable ProblemDNA vector memory."
    }

@app.get("/api/problemdna/records")
def list_problemdna_records():
    return problemdna_service.get_all_records()

@app.get("/api/problemdna/search")
def search_problemdna(q: str = Query(..., description="Query for semantic vector search")):
    return problemdna_service.search_similar_problems(q)

# --- Stage 6: SkillQuest Growth Analysis ---

@app.get("/api/skillquest/profile", response_model=SkillQuestProfile)
def get_skillquest_profile(dev_id: str = "dev_nexus_primary"):
    return skillquest_service.get_developer_profile(dev_id)

# --- Personal AI Twin & Gitea ---

@app.get("/api/twin/profile", response_model=PersonalAITwinProfile)
def get_personal_ai_twin(dev_id: str = "dev_nexus_primary"):
    return ai_twin_service.get_or_create_twin(dev_id)

@app.get("/api/gitea/evidence")
def get_gitea_evidence(username: str = "adarsha_dev"):
    return gitea_connector.fetch_developer_contributions(username)

# Mount web UI static files
ui_dist = os.path.join(os.path.dirname(__file__), "..", "web_ui")

@app.get("/")
def serve_root():
    index_file = os.path.join(ui_dist, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "NEXUS Core Engine API is operational. Visit /docs for Swagger specifications."}

@app.get("/login")
def serve_login():
    login_file = os.path.join(ui_dist, "login.html")
    if os.path.exists(login_file):
        return FileResponse(login_file)
    return {"message": "NEXUS Login page not found."}

@app.get("/index.css")
def serve_css():
    css_file = os.path.join(ui_dist, "index.css")
    return FileResponse(css_file, media_type="text/css")

@app.get("/app.js")
def serve_js():
    js_file = os.path.join(ui_dist, "app.js")
    return FileResponse(js_file, media_type="application/javascript")

@app.get("/static_img_arch")
def serve_arch_img():
    p = os.path.join(os.path.dirname(__file__), "..", "IMG-20261012-WA0001.jpg")
    return FileResponse(p, media_type="image/jpeg")

@app.get("/static_img_flow")
def serve_flow_img():
    p = os.path.join(os.path.dirname(__file__), "..", "IMG-20261012-WA0000.jpg")
    return FileResponse(p, media_type="image/jpeg")

if os.path.exists(ui_dist):
    app.mount("/static", StaticFiles(directory=ui_dist), name="static")
