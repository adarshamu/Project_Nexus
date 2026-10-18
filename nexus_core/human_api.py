"""
NEXUS Human Technical Expertise Layer:
1. Human API: Evidence-based expert matcher (Gitea activity & ProblemDNA cases)
2. Visual Expert: Fallback AI persona based on senior architect approved patterns
"""

from typing import List, Dict, Any, Optional
from nexus_core.models import (
    ExpertProfile,
    EscalationRequest,
    EscalationResponse
)

# Registry of organizational experts with empirical evidence
TEAM_EXPERTS: List[ExpertProfile] = [
    ExpertProfile(
        id="expert_amara_osei",
        name="Amara Osei",
        avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80",
        domain="Senior Frontend Engineer & React Specialist",
        technical_skills=["React", "State management", "TypeScript", "Next.js", "Component Architecture"],
        gitea_contributions_score=96.8,
        problemdna_solved_count=29,
        is_available=True,
        status_message="Available for React state management & component lifecycle pairing",
        contact_channels=["Slack Huddle", "Voice Call", "Pair Programming Screen Share"]
    ),
    ExpertProfile(
        id="expert_sarah_chen",
        name="Sarah Chen",
        avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80",
        domain="Frontend Architecture & React Internals",
        technical_skills=["React", "TypeScript", "Vite", "Next.js", "Module Federation"],
        gitea_contributions_score=94.5,
        problemdna_solved_count=23,
        is_available=True,
        status_message="Available for 1:1 huddle on Frontend & Bundler issues",
        contact_channels=["Slack Huddle", "Voice Call", "Pair Programming Screen Share"]
    ),
    ExpertProfile(
        id="expert_marcus_vance",
        name="Marcus Vance",
        avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80",
        domain="Distributed Systems & Database Reliability",
        technical_skills=["PostgreSQL", "Docker", "Kubernetes", "FastAPI", "Go", "Kafka"],
        gitea_contributions_score=89.2,
        problemdna_solved_count=18,
        is_available=False,  # Currently off-hours / in meeting -> triggers Visual Expert fallback!
        status_message="In architectural review until 18:00 UTC",
        contact_channels=["Async Thread", "Scheduled Call"]
    ),
    ExpertProfile(
        id="expert_elena_rostova",
        name="Elena Rostova",
        avatar="https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80",
        domain="DevOps & Platform Engineering",
        technical_skills=["CI/CD", "Gitea Actions", "Terraform", "Security", "Linux"],
        gitea_contributions_score=91.0,
        problemdna_solved_count=15,
        is_available=True,
        status_message="Online & reviewing pull requests",
        contact_channels=["Direct Chat", "Huddle"]
    )
]

class HumanAPIService:
    def __init__(self, experts: List[ExpertProfile] = TEAM_EXPERTS):
        self.experts = experts

    def get_all_experts(self) -> List[ExpertProfile]:
        return self.experts

    def match_expert(self, request: EscalationRequest) -> EscalationResponse:
        tags = [t.lower() for t in request.domain_tags]
        summary_tokens = request.problem_summary.lower()

        # Score experts based on domain skill matching and empirical contributions
        scored: List[tuple[ExpertProfile, float]] = []
        for exp in self.experts:
            score = 0.0
            for skill in exp.technical_skills:
                s_lower = skill.lower()
                if s_lower in tags or s_lower in summary_tokens:
                    score += 15.0
            # Weigh evidence from Gitea & ProblemDNA
            score += (exp.gitea_contributions_score * 0.2) + (exp.problemdna_solved_count * 0.5)
            scored.append((exp, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_match = scored[0][0] if scored else self.experts[0]

        # Branching based on real-time availability:
        if top_match.is_available:
            return EscalationResponse(
                expert_type="HUMAN_EXPERT",
                matched_expert=top_match,
                guidance_steps=[
                    f"Direct session opened with {top_match.name} ({top_match.domain}).",
                    "Context package, last 100 terminal logs, and attempted patches automatically transferred.",
                    f"Recommended collaboration format: {top_match.contact_channels[0]}."
                ],
                attribution=f"Matched using empirical Gitea commit density ({top_match.gitea_contributions_score}) and {top_match.problemdna_solved_count} verified ProblemDNA solutions.",
                channel_url="https://meet.nexus.internal/room/debug-session-" + request.investigation_id[:8]
            )
        else:
            # Fallback to Visual Expert AI Persona
            return EscalationResponse(
                expert_type="VISUAL_EXPERT",
                matched_expert=top_match,
                visual_expert_persona={
                    "persona_name": f"Visual Expert: {top_match.name} (AI Archetype)",
                    "pattern_basis": f"Modeled on {top_match.problemdna_solved_count} verified ProblemDNA postmortems and approved architectural patterns.",
                    "consent_status": "Opt-in Architect Persona with developer consent",
                    "transparency_notice": "Primary expert is currently unavailable. This guidance synthesizes their verified past resolutions with strict uncertainty bounding."
                },
                guidance_steps=[
                    f"[Pattern Synthesis from {top_match.name}]: Inspect file naming parity between module import definitions and physical filesystem entries.",
                    "Verify if case-sensitivity or pluralization mismatch causes the build tool bundle resolver to fail.",
                    "Recommended check: Run exact directory listing and normalize casing before re-triggering compilation."
                ],
                attribution=f"Visual Expert fallback synthesized from {top_match.name}'s verified solutions under explicit opt-in governance.",
                channel_url=None
            )
