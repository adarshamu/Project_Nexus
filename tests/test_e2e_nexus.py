"""
End-to-End Automated Verification Test Suite for NEXUS
Validates:
1. WorkLens Context Gathering & Tool Chain
2. Local Reasoning & Grounded RAG Retrieval
3. Evaluation & Verification Gate
4. ProblemDNA Vector Archival
5. Human API & Visual Expert Escalation
6. SkillQuest 4-Quadrant Growth Synthesis
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_core.models import (
    WorkLensInvestigationRequest,
    EscalationRequest,
    ProblemDNARecord
)
from nexus_core.problemdna import ProblemDNAService, VectorUtils
from nexus_core.worklens import WorkLensController
from nexus_core.human_api import HumanAPIService
from nexus_core.skillquest import SkillQuestService
from nexus_core.ai_twin import PersonalAITwinService
from nexus_core.gitea import GiteaEvidenceConnector
from nexus_core.tools import SearchTool, ReadTool, ContextTool, ExecuteTool

class TestNexusPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dna = ProblemDNAService()
        cls.wl = WorkLensController(cls.dna)
        cls.human_api = HumanAPIService()
        cls.sq = SkillQuestService(cls.dna)
        cls.twin = PersonalAITwinService()
        cls.gitea = GiteaEvidenceConnector()

    def test_01_vector_embedding_and_similarity(self):
        vec1 = VectorUtils.get_embedding("module not found import path error")
        vec2 = VectorUtils.get_embedding("module resolution failed import error")
        vec3 = VectorUtils.get_embedding("postgres database container docker")
        
        sim1_2 = VectorUtils.cosine_similarity(vec1, vec2)
        sim1_3 = VectorUtils.cosine_similarity(vec1, vec3)
        self.assertGreater(sim1_2, sim1_3, "Semantic similarity between related import terms must be higher than unrelated db terms.")

    def test_02_worklens_investigation_and_tools(self):
        req = WorkLensInvestigationRequest(
            query="Module not found: Can't resolve './ProductCard' in '/src/components/Shop'",
            error_message="Error: Module not found: Can't resolve './ProductCard'",
            project_root=os.getcwd()
        )
        res = cls = self.wl.investigate(req)
        self.assertIsNotNone(res.investigation_id)
        self.assertIn("ProductCard", res.root_cause)
        self.assertTrue(len(res.tools_executed) >= 3, "At least Search, Read, Context tools must execute.")
        self.assertIn("suggested_diff", res.model_dump())

    def test_03_execute_tool_permission_gate(self):
        # Without approval -> Denied
        unapproved = ExecuteTool.run("echo test", os.getcwd(), developer_approved=False)
        self.assertFalse(unapproved["success"])
        self.assertIn("denied", unapproved["error"].lower())

        # With approval -> Approved
        approved = ExecuteTool.run("echo NexusOnline", os.getcwd(), developer_approved=True)
        self.assertTrue(approved["success"])

    def test_04_human_api_and_visual_expert(self):
        # Online expert match
        req_online = EscalationRequest(
            investigation_id="inv-test-1",
            problem_summary="React state lifecycle hydration mismatch",
            domain_tags=["React", "Frontend"],
            developer_id="dev_nexus_primary"
        )
        resp_online = self.human_api.match_expert(req_online)
        self.assertEqual(resp_online.expert_type, "HUMAN_EXPERT")
        self.assertIsNotNone(resp_online.matched_expert)

        # Unavailable expert -> triggers Visual Expert fallback
        req_offline = EscalationRequest(
            investigation_id="inv-test-2",
            problem_summary="Postgres deadlock and kafka partition lag",
            domain_tags=["PostgreSQL", "Kafka", "Distributed Systems"],
            developer_id="dev_nexus_primary"
        )
        resp_offline = self.human_api.match_expert(req_offline)
        self.assertEqual(resp_offline.expert_type, "VISUAL_EXPERT")
        self.assertIsNotNone(resp_offline.visual_expert_persona)

    def test_05_problemdna_verification_gate(self):
        # Valid verified record
        record = ProblemDNARecord(
            title="Automated Test Record",
            problem_description="Test problem description",
            symptoms=["test symptom"],
            context_artifacts={},
            investigation_attempts=["attempt 1"],
            root_cause="Test root cause",
            verified_solution="Test solution",
            diff_patch="+ test",
            verification_steps=["ran automated test"],
            verification_evidence="Test passed with exit code 0",
            is_verified=True,
            technology_tags=["Python", "Testing"],
            project_name="TestProject",
            developer_id="tester"
        )
        rec_id = self.dna.store_record(record)
        self.assertIsNotNone(rec_id)

    def test_06_skillquest_quadrants(self):
        profile = self.sq.get_developer_profile("dev_nexus_primary")
        self.assertTrue(len(profile.strong_areas) > 0)
        self.assertTrue(len(profile.good_areas) > 0)
        self.assertTrue(len(profile.focus_areas) > 0)
        self.assertTrue(len(profile.needs_practice) > 0)
        self.assertTrue(len(profile.actionable_recommendations) > 0)

    def test_07_ai_twin_and_gitea(self):
        twin = self.twin.get_or_create_twin("dev_nexus_primary")
        self.assertIn("Hypothesis", twin.problem_solving_style)
        git_data = self.gitea.fetch_developer_contributions("adarsha_dev")
        self.assertGreater(git_data["total_commits_evaluated"], 0)

if __name__ == "__main__":
    unittest.main()
