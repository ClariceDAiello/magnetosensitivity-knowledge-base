#!/usr/bin/env python3
"""
Batch Processing Script for All Papers

This script processes all PDFs in the Literature folder with status tracking
and FAIR compliance validation.

Usage:
    python process_all_papers.py                # Process all pending papers
    python process_all_papers.py --skip-processed  # Skip already processed
    python process_all_papers.py --force-all    # Reprocess all papers

Author: Francois (Enhanced 2025-11-04)
Original: Research Knowledge Base System (2025-10-09)
"""

import os
import sys
import argparse
from pathlib import Path
from process_paper import PaperProcessor
from processing_status import ProcessingStatusTracker
from fair_compliance import FAIRComplianceValidator


def main():
    """Process all papers in the Literature folder."""
    parser = argparse.ArgumentParser(
        description="Batch process papers with status tracking and FAIR validation"
    )
    parser.add_argument("--skip-processed", action="store_true",
                       help="Skip papers already marked as processed")
    parser.add_argument("--force-all", action="store_true",
                       help="Reprocess all papers regardless of status")
    parser.add_argument("--validate-fair", action="store_true", default=True,
                       help="Run FAIR compliance check after processing (default: True)")
    parser.add_argument("--base-dir", help="Base directory of project",
                       default=None)

    args = parser.parse_args()

    base_dir = Path(args.base_dir) if args.base_dir else Path(__file__).parent.parent
    literature_dir = base_dir / "Literature"

    if not literature_dir.exists():
        print(f"Error: Literature directory not found: {literature_dir}")
        sys.exit(1)

    # Initialize processors
    paper_processor = PaperProcessor(base_dir=str(base_dir))
    status_tracker = ProcessingStatusTracker(base_dir=str(base_dir))
    fair_validator = FAIRComplianceValidator(base_dir=str(base_dir))

    # Initialize or load status
    print("\n" + "=" * 80)
    print("INITIALIZING PROCESSING STATUS")
    print("=" * 80)
    status = status_tracker.load_status()
    if status is None:
        print("No existing status found. Initializing...")
        status = status_tracker.initialize_status()
    else:
        print(f"Loaded existing status: {status['processed']} processed, {status['pending']} pending")

    # Determine which papers to process
    if args.force_all:
        papers_to_process = status["papers"]
        print(f"\nForce mode: Processing all {len(papers_to_process)} papers")
    elif args.skip_processed:
        papers_to_process = [p for p in status["papers"] if p["status"] == "pending"]
        print(f"\nSkip mode: Processing {len(papers_to_process)} pending papers")
    else:
        # Default: process pending and failed
        papers_to_process = [p for p in status["papers"]
                            if p["status"] in ["pending", "failed"]]
        print(f"\nDefault mode: Processing {len(papers_to_process)} pending/failed papers")

    if not papers_to_process:
        print("No papers to process!")
        sys.exit(0)

    # Process each paper
    print("\n" + "=" * 80)
    print("PROCESSING PAPERS")
    print("=" * 80 + "\n")

    results = []
    for i, paper_entry in enumerate(papers_to_process, 1):
        pdf_filename = paper_entry["pdf_filename"]
        paper_id = paper_entry["paper_id"]
        pdf_path = literature_dir / pdf_filename

        print(f"\n[{i}/{len(papers_to_process)}] Processing: {pdf_filename}")
        print("-" * 80)

        # Mark as processing
        status_tracker.mark_processing(paper_id)

        try:
            # Process paper
            result = paper_processor.process_paper(str(pdf_path))

            # Validate FAIR compliance if requested
            fair_score = None
            if args.validate_fair and result["success"]:
                print(f"\nValidating FAIR compliance for {paper_id}...")
                fair_result = fair_validator.validate_paper(paper_id)
                fair_score = fair_result.get("score", 0)
                print(f"  FAIR Score: {fair_score}/100")

                # Collect issues
                issues = []
                for category in ["findable", "accessible", "interoperable", "reusable"]:
                    if category in fair_result:
                        issues.extend(fair_result[category].get("issues", []))

                # Mark as completed with FAIR score
                status_tracker.mark_completed(paper_id, fair_score, issues[:5])  # Top 5 issues
            else:
                status_tracker.mark_completed(paper_id)

            result["fair_score"] = fair_score
            results.append(result)

        except Exception as e:
            print(f"\n✗ Failed to process {pdf_filename}: {e}")
            import traceback
            traceback.print_exc()

            # Mark as failed
            status_tracker.mark_failed(paper_id, str(e))

            results.append({
                "pdf_file": pdf_filename,
                "paper_id": paper_id,
                "success": False,
                "error": str(e)
            })

    # Final summary
    print("\n" + "=" * 80)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r.get("success", False))
    failed = len(results) - successful

    print(f"\nTotal Processed: {len(results)}")
    print(f"  Successful: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"  Failed: {failed} ({failed/len(results)*100:.1f}%)")

    # FAIR score summary
    fair_scores = [r.get("fair_score") for r in results if r.get("fair_score") is not None]
    if fair_scores:
        avg_fair = sum(fair_scores) / len(fair_scores)
        print(f"\nFAIR Compliance:")
        print(f"  Average Score: {avg_fair:.1f}/100")
        print(f"  Range: {min(fair_scores):.1f} - {max(fair_scores):.1f}")

        excellent = sum(1 for s in fair_scores if s >= 90)
        good = sum(1 for s in fair_scores if 70 <= s < 90)
        needs_work = sum(1 for s in fair_scores if s < 70)

        print(f"  Excellent (≥90): {excellent}")
        print(f"  Good (70-89): {good}")
        print(f"  Needs Work (<70): {needs_work}")

    print("=" * 80)

    # List failures
    failures = [r for r in results if not r.get("success", False)]
    if failures:
        print("\nFailed Papers:")
        for fail in failures:
            print(f"  - {fail.get('pdf_file', 'Unknown')}")
            print(f"    Error: {fail.get('error', 'Unknown error')}")

    # Show papers needing attention
    if fair_scores:
        low_scorers = [r for r in results
                      if r.get("fair_score", 100) < 70 and r.get("success")]
        if low_scorers:
            print("\nPapers Needing Attention (FAIR < 70):")
            for paper in low_scorers:
                print(f"  - {paper['paper_id']}: {paper['fair_score']}/100")

    print("\n✓ Processing complete!")
    print(f"\nNext steps:")
    print(f"  1. Review processing status: python scripts/processing_status.py --report")
    print(f"  2. Generate FAIR report: python scripts/fair_compliance.py --report")
    print(f"  3. Fix low-scoring papers manually")
    print(f"  4. Enhance ontology with new terms from papers")


if __name__ == "__main__":
    main()
