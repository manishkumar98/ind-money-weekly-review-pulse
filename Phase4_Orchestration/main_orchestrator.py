"""
main_orchestrator.py
Phase 4 - Final Orchestration Engine

This script ties together the entire INDmoney AI workflow:
  Phase 1: Data Ingestion (Scraping PlayStore & AppStore)
  Phase 2: LLM Processing (Groq chunking & synthesis)
  Phase 3: MCP Tool Integration (Groq orchestrating file generation based on human approval)

Usage:
  python main_orchestrator.py [--skip-ingestion] [--skip-llm]

Ensure you run this terminal natively since Phase 3 has an interactive Y/N prompt.
"""

import sys
import os
import argparse
from pathlib import Path

# Setup paths so we can import from other phases
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "Phase1_Data_Ingestion"))
sys.path.insert(0, str(project_root / "Phase2_LLM_Processing"))
sys.path.insert(0, str(project_root / "Phase3_MCP_Integration"))

try:
    from phase1_data_ingestion import main as run_phase1
except ImportError:
    run_phase1 = None

try:
    from phase2_llm_processing import run_phase2
except ImportError:
    run_phase2 = None

try:
    from phase3_mcp_orchestration import run_phase3
except ImportError:
    run_phase3 = None


def run_pipeline(skip_ingestion=False, skip_llm=False):
    print("=" * 60)
    print("🚀 STARTING INDMONEY WEEKLY PULSE ORCHESTRATOR")
    print("=" * 60 + "\n")

    # ────────────────────────────────────────────────────────
    # Phase 1: Data Ingestion
    # ────────────────────────────────────────────────────────
    phase1_output = project_root / "Phase1_Data_Ingestion" / "sanitized_indmoney_reviews.csv"
    if skip_llm:
        print("⏭️  Skipping Phase 1 (Data Ingestion) - Implied by skip_llm...")
    elif skip_ingestion and os.path.exists(phase1_output):
        print("⏭️  Skipping Phase 1 (Data Ingestion) - Using existing data...")
    else:
        if run_phase1 is None:
            print("❌ Error: Could not import Phase 1. Exiting.")
            return False
            
        print("▶️  Executing Phase 1: Data Ingestion...")
        # Save current dir to restore later since Phase 1 might write relatively
        original_cwd = os.getcwd()
        os.chdir(project_root / "Phase1_Data_Ingestion")
        try:
            run_phase1()
        except Exception as e:
            print(f"❌ Phase 1 failed: {e}")
            os.chdir(original_cwd)
            return False
        os.chdir(original_cwd)
        print("✅ Phase 1 completed successfully.\n")

    # ────────────────────────────────────────────────────────
    # Phase 2: LLM Processing
    # ────────────────────────────────────────────────────────
    phase2_pulse_output = project_root / "Phase2_LLM_Processing" / "weekly_pulse_output.json"
    phase2_fee_output = project_root / "Phase2_LLM_Processing" / "fee_explanation.json"
    
    if skip_llm and os.path.exists(phase2_pulse_output):
        print("⏭️  Skipping Phase 2 (LLM Processing) - Using existing LLM output...")
    else:
        if run_phase2 is None:
            print("❌ Error: Could not import Phase 2. Exiting.")
            return False
            
        print("▶️  Executing Phase 2: LLM Processing...")
        # Save current dir and move to Phase 2 to ensure relative outputs write there
        original_cwd = os.getcwd()
        os.chdir(project_root / "Phase2_LLM_Processing")
        try:
            # We explicitly pass the CSV path to Phase 2 runner
            csv_path = str(phase1_output)
            run_phase2(csv_path)
        except Exception as e:
            print(f"❌ Phase 2 failed: {e}")
            os.chdir(original_cwd)
            return False
        os.chdir(original_cwd)
        print("✅ Phase 2 completed successfully.\n")

    # ────────────────────────────────────────────────────────
    # Phase 3: MCP Tool Integration (Gate)
    # ────────────────────────────────────────────────────────
    if run_phase3 is None:
         print("❌ Error: Could not import Phase 3. Exiting.")
         return False

    print("▶️  Executing Phase 3: MCP Tool Integration (Human Approval Gate)...")
    original_cwd = os.getcwd()
    os.chdir(project_root / "Phase3_MCP_Integration")
    try:
        pulse_path = str(phase2_pulse_output)
        run_phase3(pulse_path)
    except Exception as e:
         print(f"❌ Phase 3 failed: {e}")
         os.chdir(original_cwd)
         return False
    os.chdir(original_cwd)
    print("✅ Phase 3 completed successfully.\n")

    print("=" * 60)
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"Check the outputs in:")
    print(f" - Phase 2: {phase2_pulse_output.name} and {phase2_fee_output.name}")
    print(f" - Phase 3: weekly_pulse_notes.md and email_draft.txt")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the full INDmoney AI Workflow")
    parser.add_argument("--skip-ingestion", action="store_true", help="Skip Phase 1 and use existing CSV")
    parser.add_argument("--skip-llm", action="store_true", help="Skip Phase 2 and use existing LLM JSON outputs. Also implies --skip-ingestion")
    args = parser.parse_args()
    
    # If skipping LLM, we naturally skip ingestion since we don't need its output
    if args.skip_llm:
        args.skip_ingestion = True
        
    run_pipeline(skip_ingestion=args.skip_ingestion, skip_llm=args.skip_llm)
