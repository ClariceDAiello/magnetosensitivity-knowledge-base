#!/usr/bin/env python3
"""
Complete Paper Processing Pipeline

This script processes a PDF paper and creates FAIR-compliant context files.

Usage:
    python process_paper.py <pdf_path> [--doi DOI] [--paper-id ID]

Author: Research Knowledge Base System
Date: 2025-10-09
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Import our PDF processor
from pdf_processor import PDFProcessor


class PaperProcessor:
    """Process academic papers into FAIR-compliant knowledge base entries."""

    def __init__(self, base_dir: str = None):
        """Initialize the paper processor."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.kb_dir = self.base_dir / "knowledge-base"
        self.papers_dir = self.kb_dir / "papers"
        self.index_dir = self.kb_dir / "index"
        self.pdf_processor = PDFProcessor(base_dir=base_dir)

    def load_index(self, index_name: str) -> Dict:
        """Load an index file."""
        index_path = self.index_dir / f"{index_name}.json"
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_index(self, index_name: str, data: Dict):
        """Save an index file."""
        index_path = self.index_dir / f"{index_name}.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_paper_directory(self, paper_id: str) -> Path:
        """Create directory structure for a paper."""
        paper_dir = self.papers_dir / paper_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        (paper_dir / "figures").mkdir(exist_ok=True)
        (paper_dir / "data").mkdir(exist_ok=True)
        return paper_dir

    def extract_doi_from_text(self, text: str) -> Optional[str]:
        """Try to extract DOI from paper text."""
        import re
        # Common DOI patterns
        patterns = [
            r'doi:\s*(10\.\d{4,}/[^\s]+)',
            r'DOI:\s*(10\.\d{4,}/[^\s]+)',
            r'https?://doi\.org/(10\.\d{4,}/[^\s]+)',
            r'\b(10\.\d{4,}/[^\s]+)\b'
        ]

        for pattern in patterns:
            match = re.search(pattern, text[:5000], re.IGNORECASE)  # Search first 5000 chars
            if match:
                doi = match.group(1)
                # Clean up DOI
                doi = doi.rstrip('.,;)')
                return doi
        return None

    def generate_metadata(self, pdf_data: Dict, paper_id: str, doi: Optional[str] = None) -> Dict:
        """Generate metadata.json from extracted PDF data."""
        # Extract DOI if not provided
        if not doi and pdf_data.get('full_text'):
            doi = self.extract_doi_from_text(pdf_data['full_text'])

        metadata = {
            "paper_id": paper_id,
            "doi": doi or "",
            "title": pdf_data.get('title', ''),
            "authors": pdf_data.get('authors', []),
            "publication": {
                "journal": "",  # To be filled by user
                "year": None,
                "volume": "",
                "issue": "",
                "pages": "",
                "publisher": ""
            },
            "keywords": [],  # To be filled by user
            "abstract": pdf_data.get('abstract', ''),
            "date_added": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "access": {
                "license": "Unknown",
                "access_level": "restricted",
                "original_file": pdf_data['file_info']['path'],
                "alternative_formats": []
            },
            "interoperability": {
                "related_papers": [],
                "cites": [],
                "cited_by": [],
                "ontology_terms": [],
                "data_formats": [],
                "methods_used": []
            },
            "research_context": {
                "species_studied": [],
                "proteins": [],
                "magnetic_field_parameters": {
                    "field_strength": "",
                    "frequency": "",
                    "field_type": ""
                },
                "experimental_techniques": [],
                "computational_methods": [],
                "key_findings": [],
                "applications": []
            }
        }

        return metadata

    def generate_context_md(self, metadata: Dict, pdf_data: Dict) -> str:
        """Generate context.md file from metadata and PDF data."""
        template_path = self.papers_dir / "TEMPLATE_context.md"

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            template = "# Paper Context: [Title]\n\n[Template not found]"

        # Fill in template with available data
        context = template.replace("[Title]", metadata.get('title', 'Unknown Title'))
        context = context.replace("[DOI or unique ID]", metadata.get('doi', metadata.get('paper_id', '')))
        context = context.replace("[Full title]", metadata.get('title', ''))
        context = context.replace("[Author list with ORCIDs if available]", ', '.join(metadata.get('authors', [])))
        context = context.replace("[ISO 8601 format]", metadata.get('date_added', ''))

        # Add abstract if available
        abstract = metadata.get('abstract', '')
        if abstract:
            context += f"\n\n## Abstract\n\n{abstract}\n"

        return context

    def generate_annotations_md(self, metadata: Dict) -> str:
        """Generate annotations.md file."""
        template_path = self.papers_dir / "TEMPLATE_annotations.md"

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()

            # Fill in template
            annotations = template.replace("[Paper Title]", metadata.get('title', 'Unknown Title'))
            annotations = annotations.replace("[Unique identifier]", metadata.get('paper_id', ''))
            annotations = annotations.replace("[Date]", datetime.now().strftime("%Y-%m-%d"))
            annotations = annotations.replace("[User]", "System")

            return annotations
        else:
            return f"# Annotations: {metadata.get('title', 'Unknown Title')}\n\n[Template not found]"

    def update_master_index(self, metadata: Dict):
        """Update the master index with new paper."""
        master_index = self.load_index("master-index")

        if "papers" not in master_index:
            master_index["papers"] = []

        # Add paper entry
        paper_entry = {
            "paper_id": metadata["paper_id"],
            "doi": metadata.get("doi", ""),
            "title": metadata.get("title", ""),
            "authors": metadata.get("authors", []),
            "year": metadata.get("publication", {}).get("year"),
            "date_added": metadata.get("date_added"),
            "file_path": f"knowledge-base/papers/{metadata['paper_id']}"
        }

        # Check if paper already exists
        existing = [p for p in master_index["papers"] if p["paper_id"] == metadata["paper_id"]]
        if existing:
            # Update existing entry
            master_index["papers"] = [p if p["paper_id"] != metadata["paper_id"] else paper_entry
                                      for p in master_index["papers"]]
        else:
            # Add new entry
            master_index["papers"].append(paper_entry)

        master_index["last_updated"] = datetime.now().isoformat()

        self.save_index("master-index", master_index)

    def process_paper(self, pdf_path: str, doi: Optional[str] = None,
                     paper_id: Optional[str] = None) -> Dict:
        """
        Process a paper through the complete pipeline.

        Args:
            pdf_path: Path to PDF file
            doi: Optional DOI
            paper_id: Optional custom paper ID

        Returns:
            Dictionary with processing results
        """
        print(f"\n{'='*80}")
        print(f"Processing Paper: {Path(pdf_path).name}")
        print(f"{'='*80}\n")

        # Step 1: Extract PDF content
        print("Step 1: Extracting PDF content...")
        pdf_data = self.pdf_processor.process_pdf(pdf_path)

        # Step 2: Generate paper ID
        if not paper_id:
            paper_id = self.pdf_processor.generate_paper_id(pdf_path)
        print(f"Step 2: Generated paper ID: {paper_id}")

        # Step 3: Create paper directory
        print("Step 3: Creating paper directory...")
        paper_dir = self.create_paper_directory(paper_id)

        # Step 4: Generate metadata
        print("Step 4: Generating metadata...")
        metadata = self.generate_metadata(pdf_data, paper_id, doi)

        # Step 5: Generate context file
        print("Step 5: Generating context file...")
        context_md = self.generate_context_md(metadata, pdf_data)

        # Step 6: Generate annotations file
        print("Step 6: Generating annotations file...")
        annotations_md = self.generate_annotations_md(metadata)

        # Step 7: Save all files
        print("Step 7: Saving files...")
        with open(paper_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        with open(paper_dir / "context.md", 'w', encoding='utf-8') as f:
            f.write(context_md)

        with open(paper_dir / "annotations.md", 'w', encoding='utf-8') as f:
            f.write(annotations_md)

        # Save full extracted text for reference
        with open(paper_dir / "full_text.txt", 'w', encoding='utf-8') as f:
            f.write(pdf_data.get('full_text', ''))

        # Step 8: Update indices
        print("Step 8: Updating indices...")
        self.update_master_index(metadata)

        print(f"\n{'='*80}")
        print(f"✓ Successfully processed: {metadata.get('title', 'Unknown Title')}")
        print(f"✓ Paper directory: {paper_dir}")
        print(f"{'='*80}\n")

        return {
            "paper_id": paper_id,
            "paper_dir": str(paper_dir),
            "metadata": metadata,
            "success": True
        }


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Process academic paper into FAIR-compliant knowledge base entry"
    )
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--doi", help="Paper DOI (optional)")
    parser.add_argument("--paper-id", help="Custom paper ID (optional)")
    parser.add_argument("--base-dir", help="Base directory of project",
                       default="/Users/clarice/Desktop/Claude/Teste")

    args = parser.parse_args()

    processor = PaperProcessor(base_dir=args.base_dir)

    try:
        result = processor.process_paper(args.pdf_path, args.doi, args.paper_id)

        if result["success"]:
            print("\n✓ Paper processing complete!")
            print(f"\nNext steps:")
            print(f"1. Review and edit: {result['paper_dir']}/metadata.json")
            print(f"2. Add annotations: {result['paper_dir']}/annotations.md")
            print(f"3. Update context: {result['paper_dir']}/context.md")

    except Exception as e:
        print(f"\n✗ Error processing paper: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
