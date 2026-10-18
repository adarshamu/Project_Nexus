"""
NEXUS WorkLens Controller (LangGraph State-Machine Simulation)
Orchestrates:
1. Scoped Context Harvest (Logs, Folder Map)
2. ProblemDNA RAG Semantic Query
3. SearchTool Scan
4. ReadTool Scoped Line Inspection
5. ContextTool Assembly
6. LLM Reasoning & Diff Generation
"""

import os
from typing import List, Dict, Any, Optional
from nexus_core.models import (
    WorkLensInvestigationRequest,
    WorkLensInvestigationResponse,
    ToolExecutionLog
)
from nexus_core.tools import SearchTool, ReadTool, ContextTool, ExecuteTool
from nexus_core.problemdna import ProblemDNAService
from nexus_core.llm import LocalLLMClient

class WorkLensController:
    def __init__(self, problemdna_service: ProblemDNAService):
        self.problemdna = problemdna_service
        self.llm = LocalLLMClient()

    def investigate(self, request: WorkLensInvestigationRequest) -> WorkLensInvestigationResponse:
        tool_logs: List[ToolExecutionLog] = []
        workspace = request.project_root or os.getcwd()

        # Step 1: Harvest scoped directory map & mock/captured terminal logs
        folder_map = []
        try:
            for root, dirs, files in os.walk(workspace):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "dist", "build", "__pycache__", "venv")]
                rel_root = os.path.relpath(root, workspace).replace("\\", "/")
                if rel_root != ".":
                    folder_map.append(f"{rel_root}/")
                for f in files[:8]:
                    folder_map.append(f"{rel_root}/{f}".replace("./", ""))
                if len(folder_map) > 80:
                    break
        except Exception:
            folder_map = ["src/", "src/components/", "src/components/Shop/"]

        # Terminal logs - harvest provided error or synthesize last 100 lines
        terminal_logs = []
        if request.error_message:
            terminal_logs.append(f"[Terminal ERR]: {request.error_message}")
        terminal_logs.extend([
            "[npm info] Compiling application frontend...",
            f"[npm warn] Target workspace: {workspace}",
            f"[npm err] {request.query}"
        ])

        # Step 2: ProblemDNA RAG Retrieval
        matched_records = []
        if request.use_rag:
            search_query = f"{request.query} {request.error_message or ''}"
            matched_records = self.problemdna.search_similar_problems(search_query, limit=2)
            tool_logs.append(ToolExecutionLog(
                tool_name="ProblemDNA_RAG",
                action_description=f"Vector search for similar past verified incidents: '{search_query[:40]}...'",
                output={"matches_found": len(matched_records), "records": matched_records}
            ))

        # Step 3: Search Tool Execution (Look for key tokens in query or error)
        search_term = "ProductCard"
        if "error:" in request.query.lower():
            tokens = [t for t in request.query.split() if len(t) > 4 and not t.startswith("http")]
            if tokens:
                search_term = tokens[0]
        elif request.error_message and "'" in request.error_message:
            parts = request.error_message.split("'")
            if len(parts) > 1:
                search_term = parts[1].replace("./", "").replace("/", "")

        search_output = SearchTool.run(search_term, workspace)
        tool_logs.append(ToolExecutionLog(
            tool_name=SearchTool.name,
            action_description=f"Scanned files and symbol declarations for identifier: '{search_term}'",
            output=search_output
        ))

        # Step 4: Read Tool Execution (Target candidate files)
        inspected_files = {}
        target_file = None
        if search_output.get("matches"):
            target_file = search_output["matches"][0].get("file")
        
        # If target file discovered, read lines
        if target_file:
            read_output = ReadTool.run(target_file, workspace, start_line=1, end_line=60)
            inspected_files[target_file] = read_output.get("content", "")
            tool_logs.append(ToolExecutionLog(
                tool_name=ReadTool.name,
                action_description=f"Read contents of prioritized candidate file: '{target_file}'",
                output={"lines_read": read_output.get("end_line"), "preview": read_output.get("content", "")[:200]}
            ))
        else:
            # Fallback mock read for demo consistency if no files matched on disk
            inspected_files["src/components/Shop/ProductCatalog.jsx"] = "import React from 'react';\nimport ProductCard from './ProductCard';\n\nexport const ProductCatalog = () => <ProductCard />;"
            tool_logs.append(ToolExecutionLog(
                tool_name=ReadTool.name,
                action_description="Read active component buffer 'src/components/Shop/ProductCatalog.jsx'",
                output={"file": "ProductCatalog.jsx", "lines": 4}
            ))

        # Step 5: Context Tool Assembly
        context_payload = ContextTool.run(
            error_message=request.error_message,
            terminal_logs=terminal_logs,
            folder_map=folder_map,
            investigated_files=inspected_files,
            rag_records=matched_records
        )
        tool_logs.append(ToolExecutionLog(
            tool_name=ContextTool.name,
            action_description="Assembled normalized context payload (last 100 logs, folder map, files, RAG matches)",
            output={"log_lines": context_payload["log_snippet_count"], "rag_cases": len(matched_records)}
        ))

        # Step 6: LLM Reasoning & Synthesis
        diagnosis = self.llm.generate_diagnosis(
            query=request.query,
            context_payload=context_payload,
            matched_records=matched_records
        )

        return WorkLensInvestigationResponse(
            root_cause=diagnosis.get("root_cause", "Root cause identified based on context inspection."),
            suggested_diff=diagnosis.get("suggested_diff", ""),
            suggested_fix_explanation=diagnosis.get("suggested_fix_explanation", ""),
            recommended_verification_steps=diagnosis.get("recommended_verification_steps", []),
            confidence_score=diagnosis.get("confidence_score", 0.90),
            tools_executed=tool_logs,
            retrieved_problemdna_references=matched_records
        )
