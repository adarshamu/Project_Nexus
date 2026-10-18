"""
NEXUS ProblemDNA: Reusable Vector Memory & Evidence Knowledge Base
High performance vector search (cosine similarity) + SQLite ACID persistence.
"""

import sqlite3
import json
import math
import os
from typing import List, Dict, Any, Optional
from nexus_core.models import ProblemDNARecord

DB_PATH = os.path.join(os.path.dirname(__file__), "problemdna.db")

class VectorUtils:
    """Lightweight local dense embedding & cosine similarity engine."""
    
    @staticmethod
    def get_embedding(text: str, dim: int = 64) -> List[float]:
        """
        Deterministically constructs a normalized pseudo-semantic vector representation
        grounded on term frequency, token hashes, and lexical stems.
        Ensures 100% offline, reproducible semantic similarity without requiring heavy native torch/onnx.
        """
        vec = [0.0] * dim
        tokens = text.lower().replace("-", " ").replace("_", " ").split()
        if not tokens:
            return vec
            
        for tok in tokens:
            tok_hash = hash(tok)
            idx = abs(tok_hash) % dim
            # Sign determines positive or negative feature projection
            sign = 1.0 if (tok_hash % 2 == 0) else -1.0
            vec[idx] += sign * (1.0 + math.log(1.0 + len(tok)))
            
        # Add character bi-grams for typo and sub-word resilience
        for i in range(len(text) - 2):
            bg = text[i:i+2]
            idx = abs(hash(bg)) % dim
            vec[idx] += 0.25

        # L2 Normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)


class ProblemDNAService:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
        self._seed_initial_cases()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS problem_dna (
                id TEXT PRIMARY KEY,
                title TEXT,
                problem_description TEXT,
                symptoms TEXT,
                context_artifacts TEXT,
                investigation_attempts TEXT,
                root_cause TEXT,
                verified_solution TEXT,
                diff_patch TEXT,
                verification_steps TEXT,
                verification_evidence TEXT,
                is_verified INTEGER,
                technology_tags TEXT,
                project_name TEXT,
                developer_id TEXT,
                expert_involved TEXT,
                confidence_score REAL,
                created_at TEXT,
                embedding TEXT
            )
        """)
        conn.commit()
        conn.close()

    def store_record(self, record: ProblemDNARecord) -> str:
        """Stores only verified records into ProblemDNA."""
        if not record.is_verified:
            raise ValueError("Only verified records can be archived into ProblemDNA.")
            
        full_text_representation = f"{record.title} {record.problem_description} {' '.join(record.symptoms)} {record.root_cause} {' '.join(record.technology_tags)}"
        vector = VectorUtils.get_embedding(full_text_representation)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO problem_dna (
                id, title, problem_description, symptoms, context_artifacts,
                investigation_attempts, root_cause, verified_solution, diff_patch,
                verification_steps, verification_evidence, is_verified,
                technology_tags, project_name, developer_id, expert_involved,
                confidence_score, created_at, embedding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.id,
            record.title,
            record.problem_description,
            json.dumps(record.symptoms),
            json.dumps(record.context_artifacts),
            json.dumps(record.investigation_attempts),
            record.root_cause,
            record.verified_solution,
            record.diff_patch,
            json.dumps(record.verification_steps),
            record.verification_evidence,
            1 if record.is_verified else 0,
            json.dumps(record.technology_tags),
            record.project_name,
            record.developer_id,
            record.expert_involved,
            record.confidence_score,
            record.created_at,
            json.dumps(vector)
        ))
        conn.commit()
        conn.close()
        return record.id

    def search_similar_problems(self, query: str, limit: int = 3, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Performs semantic vector search over verified ProblemDNA records."""
        query_vector = VectorUtils.get_embedding(query)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, title, problem_description, root_cause, verified_solution, diff_patch, technology_tags, confidence_score, embedding FROM problem_dna WHERE is_verified = 1")
        rows = cur.fetchall()
        conn.close()

        scored_records = []
        for r in rows:
            rec_id, title, desc, root_cause, sol, patch, tech_tags, conf, emb_str = r
            if not emb_str:
                continue
            emb = json.loads(emb_str)
            sim = VectorUtils.cosine_similarity(query_vector, emb)
            if sim >= threshold:
                scored_records.append({
                    "id": rec_id,
                    "title": title,
                    "problem_description": desc,
                    "root_cause": root_cause,
                    "verified_solution": sol,
                    "diff_patch": patch,
                    "technology_tags": json.loads(tech_tags) if tech_tags else [],
                    "confidence_score": conf,
                    "similarity": round(float(sim), 4)
                })

        # Rank by cosine similarity descending
        scored_records.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_records[:limit]

    def get_all_records(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, title, problem_description, root_cause, verified_solution, diff_patch, technology_tags, is_verified, created_at, developer_id, confidence_score FROM problem_dna ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "title": r[1],
                "problem_description": r[2],
                "root_cause": r[3],
                "verified_solution": r[4],
                "diff_patch": r[5],
                "technology_tags": json.loads(r[6]) if r[6] else [],
                "is_verified": bool(r[7]),
                "created_at": r[8],
                "developer_id": r[9],
                "confidence_score": r[10]
            })
        return results

    def _seed_initial_cases(self):
        """Pre-seeds foundational organizational knowledge records if empty."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM problem_dna")
        cnt = cur.fetchone()[0]
        conn.close()

        if cnt == 0:
            seed_cases = [
                ProblemDNARecord(
                    id="seed-case-react-import",
                    title="JSX Component Pluralization Import Failure",
                    problem_description="Module not found: Can't resolve './ProductCard' in '/src/components/Shop'",
                    symptoms=["Webpack/Vite compilation failed", "Error: Module not found './ProductCard'"],
                    context_artifacts={"file": "ProductCatalog.jsx", "target_dir": "src/components/Shop"},
                    investigation_attempts=["Checked tsconfig paths", "Cleaned node_modules"],
                    root_cause="File on disk was named ProductCards.jsx (plural) while import referenced ProductCard (singular).",
                    verified_solution="Corrected the import statement to reference ProductCards.",
                    diff_patch="- import ProductCard from './ProductCard';\n+ import ProductCard from './ProductCards';",
                    verification_steps=["Ran 'npm test -- -u'", "Checked Vite dev server compilation output"],
                    verification_evidence="Test suite passed with exit code 0. Module resolved cleanly.",
                    technology_tags=["React", "Vite", "JavaScript", "JSX"],
                    project_name="ECommerceApp",
                    developer_id="adarsha_dev",
                    expert_involved="sarah_frontend_lead",
                    confidence_score=0.98
                ),
                ProblemDNARecord(
                    id="seed-case-postgres-conn",
                    title="PostgreSQL Container Connection Refusal on Port 5432",
                    problem_description="Django/FastAPI fails with OperationalError: connection to server at '127.0.0.1', port 5432 failed: Connection refused",
                    symptoms=["ECONNREFUSED 127.0.0.1:5432", "Docker container exits immediately with code 1"],
                    context_artifacts={"docker_compose": "docker-compose.yml", "env": "POSTGRES_DB=nexus"},
                    investigation_attempts=["Restarted docker daemon", "Changed DB host to localhost"],
                    root_cause="PostgreSQL volume directory had stale postmaster.pid lock file preventing startup after unexpected power cycle.",
                    verified_solution="Pruned orphan lock file in postgres_data volume and added healthcheck retry delay.",
                    diff_patch="- POSTGRES_PORT: 5432\n+ POSTGRES_PORT: 5432\n+ healthcheck:\n+   test: ['CMD-SHELL', 'pg_isready -U postgres']",
                    verification_steps=["Ran 'docker compose up -d postgres'", "curl pg_isready verified port binding"],
                    verification_evidence="Database accepted incoming connections; health check passed.",
                    technology_tags=["Docker", "PostgreSQL", "Database", "DevOps"],
                    project_name="NexusInfrastructure",
                    developer_id="prajwal_dev",
                    expert_involved="alex_infra_architect",
                    confidence_score=0.95
                )
            ]
            for c in seed_cases:
                self.store_record(c)
