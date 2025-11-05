#!/usr/bin/env python3
"""
Processing Status Tracker

This script tracks which papers have been processed and their quality status.
Maintains processing_status.json with current state of all PDFs.

Usage:
    python processing_status.py --init           # Initialize status from Literature/
    python processing_status.py --list-pending   # Show unprocessed papers
    python processing_status.py --report         # Generate summary report
    python processing_status.py --mark-processed <paper_id> --score <score>
    python processing_status.py --mark-failed <paper_id> --error "<error_msg>"

Author: Francois
Date: 2025-11-04
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ProcessingStatusTracker:
    """Track processing status of all papers in the knowledge base."""

    def __init__(self, base_dir: str = None):
        """Initialize tracker."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.literature_dir = self.base_dir / "Literature"
        self.papers_dir = self.base_dir / "knowledge-base" / "papers"
        self.index_dir = self.base_dir / "knowledge-base" / "index"
        self.status_file = self.index_dir / "processing_status.json"

    def initialize_status(self) -> Dict:
        """
        Initialize processing status by scanning Literature/ folder.
        Returns status dictionary.
        """
        print("Scanning Literature/ folder...")

        # Find all PDFs
        pdf_files = sorted(self.literature_dir.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files")

        # Load existing processed papers
        processed_papers = set()
        if self.papers_dir.exists():
            processed_papers = {
                d.name for d in self.papers_dir.iterdir()
                if d.is_dir() and not d.name.startswith('TEMPLATE')
            }
        print(f"Found {len(processed_papers)} already processed papers")

        # Create status entries
        status = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "total_pdfs": len(pdf_files),
            "processed": len(processed_papers),
            "pending": len(pdf_files) - len(processed_papers),
            "papers": []
        }

        for pdf_path in pdf_files:
            pdf_filename = pdf_path.name
            # Generate paper_id same way as process_paper.py
            paper_id = pdf_path.stem.replace(' ', '_').replace('(', '').replace(')', '')

            # Check if processed
            is_processed = paper_id in processed_papers

            entry = {
                "pdf_filename": pdf_filename,
                "paper_id": paper_id,
                "status": "completed" if is_processed else "pending",
                "date_processed": None,
                "fair_compliance_score": None,
                "issues": []
            }

            # If processed, try to get date from metadata
            if is_processed:
                metadata_file = self.papers_dir / paper_id / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            entry["date_processed"] = metadata.get("date_added")
                    except Exception as e:
                        entry["issues"].append(f"Failed to read metadata: {e}")

            status["papers"].append(entry)

        # Save status file
        self.index_dir.mkdir(parents=True, exist_ok=True)
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Initialized processing_status.json")
        print(f"  Total PDFs: {status['total_pdfs']}")
        print(f"  Processed: {status['processed']}")
        print(f"  Pending: {status['pending']}")

        return status

    def load_status(self) -> Dict:
        """Load current processing status."""
        if not self.status_file.exists():
            print("Warning: processing_status.json not found. Run --init first.")
            return None

        with open(self.status_file, 'r') as f:
            return json.load(f)

    def save_status(self, status: Dict):
        """Save processing status."""
        status["last_updated"] = datetime.now().isoformat()
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

    def list_pending(self) -> List[Dict]:
        """List all pending papers."""
        status = self.load_status()
        if not status:
            return []

        pending = [p for p in status["papers"] if p["status"] == "pending"]

        print(f"\nPending Papers ({len(pending)}):")
        print("=" * 80)
        for i, paper in enumerate(pending, 1):
            print(f"{i:3d}. {paper['pdf_filename']}")
            print(f"     Paper ID: {paper['paper_id']}")
        print("=" * 80)

        return pending

    def mark_processing(self, paper_id: str):
        """Mark a paper as currently processing."""
        status = self.load_status()
        if not status:
            return False

        for paper in status["papers"]:
            if paper["paper_id"] == paper_id:
                paper["status"] = "processing"
                paper["date_processed"] = datetime.now().isoformat()
                break

        self.save_status(status)
        return True

    def mark_completed(self, paper_id: str, fair_score: Optional[float] = None,
                      issues: Optional[List[str]] = None):
        """Mark a paper as successfully processed."""
        status = self.load_status()
        if not status:
            return False

        for paper in status["papers"]:
            if paper["paper_id"] == paper_id:
                paper["status"] = "completed"
                paper["date_processed"] = datetime.now().isoformat()
                if fair_score is not None:
                    paper["fair_compliance_score"] = fair_score
                if issues:
                    paper["issues"] = issues
                break

        # Update counts
        status["processed"] = sum(1 for p in status["papers"] if p["status"] == "completed")
        status["pending"] = sum(1 for p in status["papers"] if p["status"] == "pending")

        self.save_status(status)
        return True

    def mark_failed(self, paper_id: str, error: str):
        """Mark a paper as failed to process."""
        status = self.load_status()
        if not status:
            return False

        for paper in status["papers"]:
            if paper["paper_id"] == paper_id:
                paper["status"] = "failed"
                paper["date_processed"] = datetime.now().isoformat()
                paper["issues"].append(f"Processing failed: {error}")
                break

        self.save_status(status)
        return True

    def generate_report(self):
        """Generate summary report of processing status."""
        status = self.load_status()
        if not status:
            return

        print("\n" + "=" * 80)
        print("PROCESSING STATUS REPORT")
        print("=" * 80)
        print(f"Last Updated: {status['last_updated']}")
        print(f"\nTotal PDFs:   {status['total_pdfs']}")
        print(f"Processed:    {status['processed']} ({status['processed']/status['total_pdfs']*100:.1f}%)")
        print(f"Pending:      {status['pending']} ({status['pending']/status['total_pdfs']*100:.1f}%)")

        # Count by status
        failed = sum(1 for p in status["papers"] if p["status"] == "failed")
        processing = sum(1 for p in status["papers"] if p["status"] == "processing")
        if failed > 0:
            print(f"Failed:       {failed}")
        if processing > 0:
            print(f"Processing:   {processing}")

        # FAIR compliance summary
        completed_papers = [p for p in status["papers"]
                           if p["status"] == "completed" and p["fair_compliance_score"] is not None]
        if completed_papers:
            scores = [p["fair_compliance_score"] for p in completed_papers]
            avg_score = sum(scores) / len(scores)
            print(f"\nFAIR Compliance (n={len(scores)}):")
            print(f"  Average: {avg_score:.1f}/100")
            print(f"  Range: {min(scores):.1f} - {max(scores):.1f}")

            # Quality breakdown
            excellent = sum(1 for s in scores if s >= 90)
            good = sum(1 for s in scores if 70 <= s < 90)
            needs_work = sum(1 for s in scores if s < 70)
            print(f"  Excellent (≥90): {excellent}")
            print(f"  Good (70-89): {good}")
            print(f"  Needs Work (<70): {needs_work}")

        # Papers with issues
        papers_with_issues = [p for p in status["papers"] if p["issues"]]
        if papers_with_issues:
            print(f"\nPapers with Issues: {len(papers_with_issues)}")
            for paper in papers_with_issues[:5]:  # Show first 5
                print(f"  - {paper['paper_id']}")
                for issue in paper['issues'][:2]:  # Show first 2 issues
                    print(f"    • {issue}")

        print("=" * 80 + "\n")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Track processing status of papers in knowledge base"
    )
    parser.add_argument("--init", action="store_true",
                       help="Initialize status from Literature/ folder")
    parser.add_argument("--list-pending", action="store_true",
                       help="List all pending papers")
    parser.add_argument("--report", action="store_true",
                       help="Generate summary report")
    parser.add_argument("--mark-processed", metavar="PAPER_ID",
                       help="Mark paper as successfully processed")
    parser.add_argument("--mark-failed", metavar="PAPER_ID",
                       help="Mark paper as failed")
    parser.add_argument("--score", type=float,
                       help="FAIR compliance score (0-100)")
    parser.add_argument("--error", help="Error message for failed paper")
    parser.add_argument("--base-dir", help="Base directory of project",
                       default="/Users/clarice/Desktop/Claude test")

    args = parser.parse_args()

    tracker = ProcessingStatusTracker(base_dir=args.base_dir)

    if args.init:
        tracker.initialize_status()
    elif args.list_pending:
        tracker.list_pending()
    elif args.report:
        tracker.generate_report()
    elif args.mark_processed:
        success = tracker.mark_completed(args.mark_processed, args.score)
        if success:
            print(f"✓ Marked {args.mark_processed} as completed")
        else:
            print(f"✗ Failed to update status")
    elif args.mark_failed:
        if not args.error:
            print("Error: --error required when marking as failed")
            sys.exit(1)
        success = tracker.mark_failed(args.mark_failed, args.error)
        if success:
            print(f"✓ Marked {args.mark_failed} as failed")
        else:
            print(f"✗ Failed to update status")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
