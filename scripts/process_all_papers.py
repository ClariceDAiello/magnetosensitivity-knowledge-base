#!/usr/bin/env python3
"""
Batch Processing Script for All Papers

This script processes all PDFs in the Literature folder.

Usage:
    python process_all_papers.py

Author: Research Knowledge Base System
Date: 2025-10-09
"""

import os
import sys
from pathlib import Path
from process_paper import PaperProcessor


def main():
    """Process all papers in the Literature folder."""
    base_dir = Path(__file__).parent.parent
    literature_dir = base_dir / "Literature"

    if not literature_dir.exists():
        print(f"Error: Literature directory not found: {literature_dir}")
        sys.exit(1)

    # Find all PDFs
    pdf_files = list(literature_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in Literature directory")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDF files to process\n")

    processor = PaperProcessor(base_dir=str(base_dir))

    results = []
    for pdf_path in pdf_files:
        try:
            result = processor.process_paper(str(pdf_path))
            results.append(result)
        except Exception as e:
            print(f"\n✗ Failed to process {pdf_path.name}: {e}\n")
            results.append({
                "pdf_file": pdf_path.name,
                "success": False,
                "error": str(e)
            })

    # Summary
    print("\n" + "="*80)
    print("BATCH PROCESSING SUMMARY")
    print("="*80)
    successful = sum(1 for r in results if r.get("success", False))
    print(f"Total files: {len(pdf_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(pdf_files) - successful}")
    print("="*80 + "\n")

    # List failures
    failures = [r for r in results if not r.get("success", False)]
    if failures:
        print("Failed files:")
        for fail in failures:
            print(f"  - {fail.get('pdf_file', 'Unknown')}: {fail.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
