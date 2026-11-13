"""
Command-Line Runner for CSE476 Group 16: Academic Research Assistant Team
Executes the 6-agent pipeline and prints formatted step-by-step trace and findings.
"""

import sys
import io

# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from app.agents import AcademicPipelineOrchestrator

def main():
    print("\n" + "=" * 70)
    print("  CSE476: AGENTIC AI & INTELLIGENT AUTOMATION -- TASK 2 PROJECT")
    print("  GROUP 16: AUTOMATED ACADEMIC RESEARCH ASSISTANT TEAM")
    print("  Framework: Microsoft Semantic Kernel | Architecture: Pipeline + RAG + Critic")
    print("=" * 70 + "\n")

    inquiry = (
        sys.argv[1] if len(sys.argv) > 1
        else "What are the risks and coordination patterns in autonomous multi-agent workflows?"
    )

    print(f"[*] Research Inquiry: \"{inquiry}\"\n")
    orchestrator = AcademicPipelineOrchestrator()
    result = orchestrator.run_pipeline(question=inquiry)

    print(f"[SUCCESS] Execution Completed!")
    print(f"    - Run ID: {result['run_id']}")
    print(f"    - Duration: {result['metrics']['total_duration_ms']} ms")
    print(f"    - Sub-Queries: {result['metrics']['sub_queries_count']}")
    print(f"    - Passages Retrieved: {result['metrics']['passages_retrieved']}")
    print(f"    - Retained Grounded Claims: {result['metrics']['retained_claims']}")
    print(f"    - Critic Pruned Claims: {result['metrics']['dropped_claims']}")
    print(f"    - Contradiction Debates: {result['metrics']['contradictions_identified']}\n")

    print("=" * 70)
    print("  MULTI-AGENT EXECUTION TRACE (Step-by-Step)")
    print("=" * 70)
    for idx, step in enumerate(result['agent_trace'], 1):
        print(f"[{idx:02d}] {step['agent']:<25} | Tool: {step['tool']}() [{step['duration_ms']} ms]")

    print("\n" + "=" * 70)
    print("  FINAL SOURCED LITERATURE REPORT")
    print("=" * 70)
    print(result['final_report']['markdown_report'])

    if result['contradictions'].get('has_contradictions'):
        print("\n" + "=" * 70)
        print("  CONTRADICTION AGENT DOSSIER (Group of 3 Requirement)")
        print("=" * 70)
        for d in result['contradictions']['dossiers']:
            print(f"\n[Topic] {d['topic']}")
            print(f"  * Position A ({d['position_a']['source']}): {d['position_a']['argument']}")
            print(f"  * Position B ({d['position_b']['source']}): {d['position_b']['argument']}")
            print(f"  * Significance: {d['significance']}")

    print("\n[SUCCESS] Run trace recorded in append-only log: run_log.jsonl\n")

if __name__ == '__main__':
    main()
