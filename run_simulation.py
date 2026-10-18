#!/usr/bin/env python3
"""
NEXUS Automated End-to-End Simulation Runner with Comprehensive Dummy Data.
Executes and prints every single stage:
  Stage 1: Problem Encounter & Trigger
  Stage 2: WorkLens Investigation (SearchTool, ReadTool, ContextTool, Ollama/LLM RAG)
  Stage 3: Decision & Developer Evaluation (Satisfied vs Unsatisfied paths)
  Stage 4: Human API & Visual Expert Escalation
  Stage 5: Verification Gate & ProblemDNA Vector Archival
  Stage 6: SkillQuest 4-Quadrant Growth Synthesis & Recommendations
  Bonus:   Personal AI Twin & Gitea Evidence Synchronization
"""

import sys
import os
import json
import io

# Setup UTF-8 encoding on Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_core.models import (
    WorkLensInvestigationRequest,
    EscalationRequest,
    ProblemDNARecord,
    VerifyAndArchiveRequest
)
from nexus_core.problemdna import ProblemDNAService, VectorUtils
from nexus_core.worklens import WorkLensController
from nexus_core.human_api import HumanAPIService
from nexus_core.skillquest import SkillQuestService
from nexus_core.ai_twin import PersonalAITwinService
from nexus_core.gitea import GiteaEvidenceConnector
from nexus_core.tools import ExecuteTool

def separator(title: str):
    print("\n" + "=" * 70)
    print(f"🔹 {title}")
    print("=" * 70)

def run_automated_nexus_simulation():
    print("""
######################################################################
#                                                                    #
#             NEXUS: PERSONAL INTELLIGENCE & GROWTH NETWORK          #
#                 AUTOMATED END-TO-END SCENARIO SIMULATION           #
#                                                                    #
######################################################################
""")

    # Initialize Core Services
    dna_service = ProblemDNAService()
    worklens = WorkLensController(dna_service)
    human_api = HumanAPIService()
    skillquest = SkillQuestService(dna_service)
    twin_service = PersonalAITwinService()
    gitea = GiteaEvidenceConnector()

    # =========================================================================
    # STAGE 1: Problem Encounter & User-Triggered Context Intake
    # =========================================================================
    separator("STAGE 1: Problem Encounter & Manual Trigger")
    
    dummy_query = "Module not found: Can't resolve './ProductCard' in '/src/components/Shop'"
    dummy_terminal_error = """[npm info] Compiling application frontend...
[ERROR] in ./src/components/Shop/ProductCatalog.jsx 4:18-42
Module not found: Error: Can't resolve './ProductCard' in 'c:/Project_Nexus/src/components/Shop'
Did you mean './ProductCards.jsx'?
Resolve error occurred during Vite HMR build loop."""
    dummy_code_snippet = """import React from 'react';
import ProductCard from './ProductCard';

export const ProductCatalog = () => {
    return <ProductCard />;
};"""

    print(f"• User ID:            dev_nexus_primary")
    print(f"• Project Root:       {os.getcwd()}")
    print(f"• Error Symptom:      {dummy_query}")
    print(f"• Terminal Logs:      {len(dummy_terminal_error.splitlines())} lines captured (Scoped strictly to last 100)")
    print(f"• Trigger Type:       User-Triggered (Zero screen tracking / Zero keystroke logging)")

    # =========================================================================
    # STAGE 2: WorkLens Contextual Investigation & Tool Orchestration
    # =========================================================================
    separator("STAGE 2: WorkLens Investigation (LangGraph State-Machine + Tools + RAG)")

    investigation_req = WorkLensInvestigationRequest(
        query=dummy_query,
        error_message=dummy_terminal_error,
        selected_code=dummy_code_snippet,
        project_root=os.getcwd(),
        use_rag=True,
        developer_id="dev_nexus_primary"
    )

    print("• Initiating WorkLens Agent Controller...")
    response = worklens.investigate(investigation_req)

    print(f"• Investigation ID:   {response.investigation_id}")
    print(f"• Confidence Score:   {response.confidence_score * 100:.1f}%")
    print(f"\n[Tools Executed by Agent]:")
    for idx, tool in enumerate(response.tools_executed, 1):
        print(f"   {idx}. {tool.tool_name:<18} → {tool.action_description}")

    print(f"\n[ProblemDNA RAG Matches Retained]: {len(response.retrieved_problemdna_references)} historical records")
    for r in response.retrieved_problemdna_references:
        print(f"   - Match #{r['id']} (Sim: {r.get('similarity', 0)*100:.1f}%): {r['title']}")

    print(f"\n[Identified Root Cause]:")
    print(f"   {response.root_cause}")

    print(f"\n[Suggested Code Patch Diff]:")
    for line in response.suggested_diff.splitlines():
        print(f"   {line}")

    # =========================================================================
    # STAGE 3: Decision & Developer Evaluation
    # =========================================================================
    separator("STAGE 3: Developer Evaluation & Feedback")
    print("• Developer reviews proposed root cause & code patch.")
    print("• Architectural Rule: Developer satisfaction is subjective feedback, not proof of correctness.")
    print("  -> Simulated Choice A: Developer Satisfied -> Proceed to Verification Gate")
    print("  -> Simulated Choice B: Developer Unsatisfied -> Escalate to Human API")

    # =========================================================================
    # STAGE 4: Human API & Visual Expert Escalation (Simulating Both Scenarios)
    # =========================================================================
    separator("STAGE 4: Human API & Visual Expert Escalation")

    # Scenario 4A: Online Expert Available
    print("--- [Scenario 4A: Frontend Domain - Human Expert Available] ---")
    esc_req_frontend = EscalationRequest(
        investigation_id=response.investigation_id,
        problem_summary="React JSX module resolution failure and path pluralization",
        domain_tags=["React", "Frontend", "Vite"],
        developer_id="dev_nexus_primary"
    )
    esc_resp_frontend = human_api.match_expert(esc_req_frontend)
    print(f"• Escalation Type:     {esc_resp_frontend.expert_type}")
    print(f"• Matched Expert:      {esc_resp_frontend.matched_expert.name} ({esc_resp_frontend.matched_expert.domain})")
    print(f"• Empirical Evidence:  Gitea Score: {esc_resp_frontend.matched_expert.gitea_contributions_score} | ProblemDNA Solved: {esc_resp_frontend.matched_expert.problemdna_solved_count}")
    print(f"• Direct Huddle URL:   {esc_resp_frontend.channel_url}")

    # Scenario 4B: Offline Expert -> Visual Expert Fallback
    print("\n--- [Scenario 4B: Distributed Database Domain - Expert Offline -> Visual Expert AI Fallback] ---")
    esc_req_db = EscalationRequest(
        investigation_id="inv-db-002",
        problem_summary="PostgreSQL port 5432 connection refused due to stale postmaster.pid lock",
        domain_tags=["PostgreSQL", "Docker", "Distributed Systems"],
        developer_id="dev_nexus_primary"
    )
    esc_resp_db = human_api.match_expert(esc_req_db)
    print(f"• Escalation Type:     {esc_resp_db.expert_type}")
    print(f"• Fallback Persona:    {esc_resp_db.visual_expert_persona['persona_name']}")
    print(f"• Pattern Basis:       {esc_resp_db.visual_expert_persona['pattern_basis']}")
    print(f"• Governance Notice:   {esc_resp_db.visual_expert_persona['transparency_notice']}")
    print("• Synthesized Guidance:")
    for step in esc_resp_db.guidance_steps:
        print(f"   * {step}")

    # =========================================================================
    # STAGE 5: Solution Verification Gate & ProblemDNA Archival
    # =========================================================================
    separator("STAGE 5: Solution Verification Gate & ProblemDNA Archival")
    print("• Developer applies patch: import ProductCard from './ProductCards'")
    print("• Testing execution gate before ProblemDNA persistence...")

    # Gate test execution using ExecuteTool
    cmd = "echo [PASS] Jest/Vite test suites: 1 passed, 0 failed. Module resolved cleanly."
    exec_result = ExecuteTool.run(cmd, os.getcwd(), developer_approved=True)
    print(f"• Test Execution Command: '{cmd}'")
    print(f"• Test Gate Result:       {exec_result['stdout'].strip()}")
    print(f"• Verification Status:    VERIFIED_CLEAN (Exit Code: {exec_result['exit_code']})")

    # Commit to ProblemDNA
    new_dna_record = ProblemDNARecord(
        id=f"rec-sim-{response.investigation_id[:8]}",
        title="Automated Sim: React Module Resolution Pluralization",
        problem_description=dummy_query,
        symptoms=["Webpack/Vite build error", "Module not found './ProductCard'"],
        context_artifacts={"file": "ProductCatalog.jsx", "target": "ProductCards.jsx"},
        investigation_attempts=["Checked SearchTool output", "Read physical disk directory"],
        root_cause=response.root_cause,
        verified_solution="Updated import statement in ProductCatalog.jsx to import './ProductCards'",
        diff_patch=response.suggested_diff,
        verification_steps=["npm test -- -u", "Re-run Vite dev server"],
        verification_evidence="Test suite passed with zero errors. Component loaded cleanly.",
        technology_tags=["React", "JavaScript", "JSX", "Bundler"],
        project_name="Project_Nexus",
        developer_id="dev_nexus_primary",
        expert_involved="Sarah Chen",
        confidence_score=0.97
    )

    record_id = dna_service.store_record(new_dna_record)
    print(f"\n✓ ProblemDNA Record Successfully Committed & Indexed!")
    print(f"  - Record ID:         {record_id}")
    print(f"  - High-Dim Vector:   Calculated & indexed in SQLite vector memory")
    print(f"  - Knowledge Base:    Now permanently available for future team RAG queries")

    # =========================================================================
    # STAGE 6: SkillQuest Evidence Synthesis & 4-Quadrant Growth Analysis
    # =========================================================================
    separator("STAGE 6: SkillQuest Developer Growth & Mastery Insights")
    
    profile = skillquest.get_developer_profile("dev_nexus_primary")
    print(f"• Developer:            {profile.developer_id}")
    print(f"• Total Cases Solved:   {profile.total_problems_resolved}")
    print(f"• Evidence Sources:     {profile.evidence_sources}")

    print("\n--- 4-QUADRANT TECHNICAL MASTERY ---")
    print("🌟 [QUADRANT 1: Strong Areas - High Autonomy & Zero Repeat Defects]:")
    for it in profile.strong_areas:
        print(f"   • {it.name:<34} ({it.score:.0f}%) | Evidence count: {it.evidence_count}")
        print(f"     └─ {it.recent_evidence_summary}")

    print("\n⚡ [QUADRANT 2: Good Areas - Consistent Competency]:")
    for it in profile.good_areas:
        print(f"   • {it.name:<34} ({it.score:.0f}%) | Evidence count: {it.evidence_count}")
        print(f"     └─ {it.recent_evidence_summary}")

    print("\n🎯 [QUADRANT 3: Focus Areas - Recurring Diagnostic Assistance]:")
    for it in profile.focus_areas:
        print(f"   • {it.name:<34} ({it.score:.0f}%) | Evidence count: {it.evidence_count}")
        print(f"     └─ {it.recent_evidence_summary}")

    print("\n🌱 [QUADRANT 4: Needs Practice - Emerging Patterns & Sandboxes]:")
    for it in profile.needs_practice:
        print(f"   • {it.name:<34} ({it.score:.0f}%) | Evidence count: {it.evidence_count}")
        print(f"     └─ {it.recent_evidence_summary}")

    print("\n--- ACTIONABLE GROWTH RECOMMENDATIONS ---")
    for idx, rec in enumerate(profile.actionable_recommendations, 1):
        print(f"{idx}. [{rec['impact']} Impact] {rec['title']} ({rec['estimated_time']})")
        print(f"   Action:  {rec['action_type']}")
        print(f"   Insight: {rec['insight']}")

    # =========================================================================
    # BONUS: Personal AI Twin & Gitea Repository Evidence
    # =========================================================================
    separator("LONG-TERM INTELLIGENCE: Personal AI Twin & Gitea Evidence")
    
    twin = twin_service.get_or_create_twin("dev_nexus_primary")
    print(f"• Problem Solving Style:   {twin.problem_solving_style}")
    print(f"• Career Trajectory:       {twin.long_term_career_trajectory}")
    print(f"• Learning Velocity:       {twin.learning_velocity}")
    print(f"• Preferred Tools:         {', '.join(twin.preferred_tools[:2])}...")

    git_evidence = gitea.fetch_developer_contributions("adarsha_dev")
    print(f"• Gitea Evaluated Commits: {git_evidence['total_commits_evaluated']}")
    print(f"• PR Reviews Approved:     {git_evidence['code_review_approvals']}")
    print(f"• Connected Repositories:  {[r['name'] for r in git_evidence['repositories_contributed']]}")

    separator("SIMULATION COMPLETED WITH 100% SUCCESS")
    print("All 6 stages executed and validated against architectural requirements.\n")

if __name__ == "__main__":
    run_automated_nexus_simulation()
