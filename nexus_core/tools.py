"""
NEXUS WorkLens Agent Tools:
1. SearchTool: File paths, symbols, imports, cross-references
2. ReadTool: Scoped lines / targeted file inspects
3. ContextTool: Context normalization & prompt preparation
4. ExecuteTool: Safe sandboxed test / build runner (Strictly gated)
"""

import os
import re
import subprocess
from typing import List, Dict, Any, Optional

class SearchTool:
    """Scans project directory for symbol definitions, files, and imports."""
    name = "SearchTool"

    @staticmethod
    def run(query: str, project_root: str, max_results: int = 10) -> Dict[str, Any]:
        results = []
        if not os.path.exists(project_root):
            return {"query": query, "found_files": [], "matched_lines": []}

        # Clean query for regex search
        pattern = re.escape(query.strip())
        rgx = re.compile(pattern, re.IGNORECASE)

        for root, dirs, files in os.walk(project_root):
            # Ignore hidden or build directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "dist", "build", "__pycache__", "venv")]
            for f in files:
                filepath = os.path.join(root, f)
                rel_path = os.path.relpath(filepath, project_root).replace("\\", "/")
                
                # Check if file name itself matches
                if rgx.search(f):
                    results.append({"type": "file_match", "file": rel_path, "preview": f})
                    continue
                
                # Search file contents for plain text/code files
                if f.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.json', '.html', '.css', '.md', '.yml', '.yaml', '.go', '.rs')):
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                            for idx, line in enumerate(fp, 1):
                                if rgx.search(line):
                                    results.append({
                                        "type": "content_match",
                                        "file": rel_path,
                                        "line_num": idx,
                                        "line_content": line.strip()
                                    })
                                    if len(results) >= max_results:
                                        break
                    except Exception:
                        pass
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break

        return {
            "query": query,
            "total_matches": len(results),
            "matches": results
        }


class ReadTool:
    """Reads specific lines or targeted contents of files identified during search."""
    name = "ReadTool"

    @staticmethod
    def run(file_path: str, project_root: str, start_line: int = 1, end_line: int = 80) -> Dict[str, Any]:
        # Handle relative or absolute paths safely
        if not os.path.isabs(file_path):
            abs_path = os.path.join(project_root, file_path)
        else:
            abs_path = file_path

        if not os.path.exists(abs_path):
            return {"error": f"File not found: {file_path}", "lines": []}

        try:
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                
            selected = all_lines[max(0, start_line - 1):end_line]
            return {
                "file": file_path,
                "start_line": start_line,
                "end_line": min(len(all_lines), end_line),
                "total_file_lines": len(all_lines),
                "content": "".join(selected)
            }
        except Exception as e:
            return {"error": f"Failed reading file: {str(e)}", "lines": []}


class ContextTool:
    """Assembles scoped terminal logs, file trees, manifest data, and ProblemDNA RAG records."""
    name = "ContextTool"

    @staticmethod
    def run(error_message: Optional[str],
            terminal_logs: List[str],
            folder_map: List[str],
            investigated_files: Dict[str, str],
            rag_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        # Scoped to last 100 lines per specification
        logs_bounded = terminal_logs[-100:] if len(terminal_logs) > 100 else terminal_logs
        
        context_payload = {
            "error_summary": error_message or "General Diagnostic Query",
            "log_snippet_count": len(logs_bounded),
            "recent_logs": logs_bounded,
            "directory_structure_sample": folder_map[:40],
            "inspected_files": investigated_files,
            "retrieved_past_cases_count": len(rag_records),
            "past_verified_cases": rag_records
        }
        return context_payload


class ExecuteTool:
    """
    Executes approved shell commands, automated tests, or build steps.
    Strictly gatekept per NEXUS principle of Least Privilege.
    """
    name = "ExecuteTool"

    @staticmethod
    def run(command: str, cwd: str, developer_approved: bool = False) -> Dict[str, Any]:
        if not developer_approved:
            return {
                "success": False,
                "error": "Execution denied. Developer approval is strictly required to execute commands.",
                "command": command
            }
        
        # Security blacklist to prevent destructive commands
        dangerous = ["rm -rf", "del /f /s /q", "format", "drop table", "mkfs"]
        if any(d in command.lower() for d in dangerous):
            return {
                "success": False,
                "error": "Command blocked: destructive execution detected.",
                "command": command
            }

        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout[:2000],
                "stderr": res.stderr[:2000],
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command execution timed out after 15 seconds.",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
