"""
NEXUS Personal AI Twin & Long-Term Intelligence Services
Synthesizes engineering habits, problem-solving styles, and private knowledge vault.
"""

from typing import Dict, Any, List
from datetime import datetime
from nexus_core.models import PersonalAITwinProfile

class PersonalAITwinService:
    def __init__(self):
        self._profiles: Dict[str, PersonalAITwinProfile] = {}

    def get_or_create_twin(self, developer_id: str = "dev_nexus_primary") -> PersonalAITwinProfile:
        if developer_id not in self._profiles:
            self._profiles[developer_id] = PersonalAITwinProfile(
                developer_id=developer_id,
                problem_solving_style="Hypothesis-Driven & Test-First Diagnostic Approach",
                preferred_tools=[
                    "WorkLens Scoped Terminal Logs",
                    "Targeted ReadTool File Diffs",
                    "Local Ollama / Llama 3 Inference",
                    "Automated Verification Test Gates"
                ],
                long_term_career_trajectory="Staff Systems & Frontend Architect",
                learning_velocity="High (Average 4 verified technical problems internalized weekly)",
                knowledge_vault_items=[
                    {
                        "title": "Clean Module Resolution Strategy",
                        "content": "Always standardize barrel exports in index.js to prevent component pluralization ambiguities.",
                        "date_saved": "2026-10-10"
                    },
                    {
                        "title": "Postgres Container Idempotent Reset",
                        "content": "Verify volume stale lock cleanup before restarting orchestrators in test suites.",
                        "date_saved": "2026-10-11"
                    }
                ],
                updated_at=datetime.utcnow().isoformat()
            )
        return self._profiles[developer_id]

    def add_vault_item(self, developer_id: str, title: str, content: str) -> PersonalAITwinProfile:
        profile = self.get_or_create_twin(developer_id)
        profile.knowledge_vault_items.append({
            "title": title,
            "content": content,
            "date_saved": datetime.utcnow().strftime("%Y-%m-%d")
        })
        profile.updated_at = datetime.utcnow().isoformat()
        return profile
