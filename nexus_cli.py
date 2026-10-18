#!/usr/bin/env python3
"""
NEXUS Command-Line Terminal Utility
Usage:
  python nexus_cli.py ask "Error message or question"
  python nexus_cli.py search "Search ProblemDNA vector memory"
  python nexus_cli.py growth
  python nexus_cli.py experts
"""

import sys
import argparse
import json
import os

import sys
import argparse
import json
import os

# Ensure safe UTF-8 output on Windows terminals
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_core.models import WorkLensInvestigationRequest, EscalationRequest
from nexus_core.problemdna import ProblemDNAService
from nexus_core.worklens import WorkLensController
from nexus_core.human_api import HumanAPIService
from nexus_core.skillquest import SkillQuestService

def main():
    parser = argparse.ArgumentParser(description="NEXUS CLI: Contextual Intelligence & Growth Terminal")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: ask
    ask_parser = subparsers.add_parser("ask", help="Trigger WorkLens to investigate an error or query")
    ask_parser.add_argument("query", type=str, help="Error message, stack trace, or technical problem description")
    ask_parser.add_argument("--error", type=str, default=None, help="Explicit error stack trace")

    # Command: search
    search_parser = subparsers.add_parser("search", help="Perform semantic vector search in ProblemDNA")
    search_parser.add_argument("term", type=str, help="Search query")

    # Command: growth
    subparsers.add_parser("growth", help="Display SkillQuest developer growth profile and recommendations")

    # Command: experts
    subparsers.add_parser("experts", help="List empirical experts registered in Human API")

    args = parser.parse_args()

    dna = ProblemDNAService()
    wl = WorkLensController(dna)
    human_api = HumanAPIService()
    sq = SkillQuestService(dna)

    if args.command == "ask":
        print("\n🔍 [NEXUS WorkLens] Initializing scoped investigation...")
        print("   - Collecting terminal log buffer & project directory map")
        print("   - Querying ProblemDNA vector memory")
        
        req = WorkLensInvestigationRequest(
            query=args.query,
            error_message=args.error or args.query,
            project_root=os.getcwd()
        )
        resp = wl.investigate(req)
        
        print("\n" + "="*60)
        print("💡 INVESTIGATION RESULT:")
        print("="*60)
        print(f"Confidence Score: {resp.confidence_score * 100:.1f}%\n")
        print("📌 ROOT CAUSE:")
        print(f"   {resp.root_cause}\n")
        print("📝 SUGGESTED FIX DIFF:")
        for line in resp.suggested_diff.split("\n"):
            if line.startswith("+"):
                print(f"\033[92m{line}\033[0m")
            elif line.startswith("-"):
                print(f"\033[91m{line}\033[0m")
            else:
                print(f"   {line}")
        print("\n🛠️ RECOMMENDED VERIFICATION STEPS:")
        for idx, step in enumerate(resp.recommended_verification_steps, 1):
            print(f"   {idx}. {step}")
        print("="*60 + "\n")

    elif args.command == "search":
        print(f"\n🧠 [ProblemDNA] Semantic Vector Search for: '{args.term}'...")
        results = dna.search_similar_problems(args.term)
        if not results:
            print("No matching verified cases found.")
        else:
            for idx, r in enumerate(results, 1):
                print(f"\n[{idx}] {r['title']} (Similarity: {r['similarity']*100:.1f}%)")
                print(f"    Root Cause: {r['root_cause']}")
                print(f"    Solution:   {r['verified_solution']}")
                print(f"    Tags:       {', '.join(r['technology_tags'])}")

    elif args.command == "growth":
        prof = sq.get_developer_profile()
        print("\n📈 [SkillQuest] Personal Engineering Growth Profile")
        print("="*60)
        print("🌟 STRONG AREAS:")
        for item in prof.strong_areas:
            print(f"   • {item.name} ({item.score}/100) - {item.recent_evidence_summary}")
        print("\n🎯 FOCUS AREAS:")
        for item in prof.focus_areas:
            print(f"   • {item.name} ({item.score}/100) - {item.recent_evidence_summary}")
        print("\n🚀 ACTIONABLE RECOMMENDATIONS:")
        for rec in prof.actionable_recommendations:
            print(f"   [{rec['impact']} Impact] {rec['title']}: {rec['insight']}")
        print("="*60 + "\n")

    elif args.command == "experts":
        experts = human_api.get_all_experts()
        print("\n👥 [Human API] Registered Organizational Experts")
        print("="*60)
        for exp in experts:
            status = "🟢 ONLINE" if exp.is_available else "🟡 OFF-HOURS (Visual Expert Enabled)"
            print(f"• {exp.name} [{status}]")
            print(f"  Domain: {exp.domain}")
            print(f"  Gitea Evidence Score: {exp.gitea_contributions_score} | ProblemDNA Solved: {exp.problemdna_solved_count}")
            print(f"  Skills: {', '.join(exp.technical_skills)}\n")
        print("="*60 + "\n")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
