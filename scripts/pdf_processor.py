#!/usr/bin/env python3
"""
PDF Processing Module for Magnetosensitivity Research Knowledge Base

This module provides a flexible PDF processing pipeline with automatic fallback:
1. Try GROBID if available (best for large PDFs and books)
2. Fall back to Python-based extraction (PyMuPDF, pdfplumber)

Author: Research Knowledge Base System
Date: 2025-10-09
"""

import os
import sys
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

# Optional imports with graceful fallback
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("Warning: PyMuPDF not installed. Install with: pip install pymupdf")

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("Warning: pdfplumber not installed. Install with: pip install pdfplumber")

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    print("Warning: pypdf not installed. Install with: pip install pypdf")


class PDFProcessor:
    """Main PDF processing class with GROBID and fallback support."""

    def __init__(self, grobid_url: str = "http://localhost:8070", base_dir: str = None):
        """
        Initialize PDF processor.

        Args:
            grobid_url: URL of GROBID service (if available)
            base_dir: Base directory of the project
        """
        self.grobid_url = grobid_url
        self.grobid_available = self._check_grobid()
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

    def _check_grobid(self) -> bool:
        """Check if GROBID service is available."""
        try:
            response = requests.get(f"{self.grobid_url}/api/isalive", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate_paper_id(self, pdf_path: str) -> str:
        """
        Generate unique paper ID from PDF filename.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Unique paper ID (sanitized filename or hash)
        """
        filename = Path(pdf_path).stem
        # Sanitize filename to create valid ID
        paper_id = re.sub(r'[^a-zA-Z0-9_-]', '_', filename)
        return paper_id[:100]  # Limit length

    def extract_with_grobid(self, pdf_path: str) -> Dict:
        """
        Extract metadata and content using GROBID service.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing extracted data
        """
        if not self.grobid_available:
            raise Exception("GROBID service not available")

        try:
            with open(pdf_path, 'rb') as f:
                files = {'input': f}
                # Process full text
                response = requests.post(
                    f"{self.grobid_url}/api/processFulltextDocument",
                    files=files,
                    timeout=300
                )

            if response.status_code == 200:
                # GROBID returns TEI XML format
                return self._parse_grobid_xml(response.text)
            else:
                raise Exception(f"GROBID processing failed: {response.status_code}")

        except Exception as e:
            print(f"GROBID extraction failed: {e}")
            return None

    def _parse_grobid_xml(self, xml_content: str) -> Dict:
        """
        Parse GROBID TEI XML output.

        Args:
            xml_content: TEI XML string from GROBID

        Returns:
            Dictionary with structured data
        """
        # Simplified parsing - in production, use proper XML parser
        # This is a placeholder for the full implementation
        return {
            "title": "",
            "authors": [],
            "abstract": "",
            "full_text": xml_content,
            "method": "grobid"
        }

    def extract_with_pymupdf(self, pdf_path: str) -> Dict:
        """
        Extract text using PyMuPDF (fast, good for most PDFs).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing extracted text and metadata
        """
        if not HAS_PYMUPDF:
            raise Exception("PyMuPDF not available")

        doc = fitz.open(pdf_path)

        # Extract metadata
        metadata = doc.metadata

        # Extract text from all pages
        full_text = ""
        for page_num, page in enumerate(doc):
            full_text += f"\n\n--- Page {page_num + 1} ---\n\n"
            full_text += page.get_text()

        # Try to extract title from first page or metadata
        title = metadata.get('title', '') or self._extract_title_from_text(full_text)

        # Try to extract authors
        authors = self._extract_authors_from_text(full_text)

        # Try to extract abstract
        abstract = self._extract_abstract_from_text(full_text)

        doc.close()

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "full_text": full_text,
            "metadata": metadata,
            "page_count": len(doc),
            "method": "pymupdf"
        }

    def extract_with_pdfplumber(self, pdf_path: str) -> Dict:
        """
        Extract text using pdfplumber (good for tables and layout).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing extracted text and tables
        """
        if not HAS_PDFPLUMBER:
            raise Exception("pdfplumber not available")

        with pdfplumber.open(pdf_path) as pdf:
            # Extract text
            full_text = ""
            tables = []

            for page_num, page in enumerate(pdf.pages):
                full_text += f"\n\n--- Page {page_num + 1} ---\n\n"
                full_text += page.extract_text() or ""

                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend([{
                        "page": page_num + 1,
                        "data": table
                    } for table in page_tables])

            # Extract title and abstract
            title = self._extract_title_from_text(full_text)
            authors = self._extract_authors_from_text(full_text)
            abstract = self._extract_abstract_from_text(full_text)

            return {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "full_text": full_text,
                "tables": tables,
                "page_count": len(pdf.pages),
                "method": "pdfplumber"
            }

    def extract_metadata_with_pypdf(self, pdf_path: str) -> Dict:
        """
        Extract metadata using pypdf.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing PDF metadata
        """
        if not HAS_PYPDF:
            return {}

        try:
            reader = PdfReader(pdf_path)
            metadata = reader.metadata

            return {
                "pdf_title": metadata.get('/Title', ''),
                "pdf_author": metadata.get('/Author', ''),
                "pdf_subject": metadata.get('/Subject', ''),
                "pdf_creator": metadata.get('/Creator', ''),
                "pdf_producer": metadata.get('/Producer', ''),
                "page_count": len(reader.pages)
            }
        except:
            return {}

    def _extract_title_from_text(self, text: str) -> str:
        """Extract title from paper text (heuristic approach)."""
        lines = text.split('\n')
        # Title is usually in first few lines, often in larger font
        # Take first substantial line (>10 chars, not starting with numbers)
        for line in lines[:20]:
            line = line.strip()
            if len(line) > 10 and not line[0].isdigit():
                return line
        return ""

    def _extract_authors_from_text(self, text: str) -> List[str]:
        """Extract authors from paper text (heuristic approach)."""
        # Look for common author patterns after title
        # This is simplified - real implementation would be more sophisticated
        authors = []
        lines = text.split('\n')

        for i, line in enumerate(lines[:50]):
            # Look for patterns like "John Doe, Jane Smith"
            if ',' in line and len(line) < 200:
                # Simple heuristic: names separated by commas
                potential_authors = [name.strip() for name in line.split(',')]
                if all(len(name.split()) <= 4 for name in potential_authors):
                    authors.extend(potential_authors)
                    if authors:
                        break

        return authors[:10]  # Limit to reasonable number

    def _extract_abstract_from_text(self, text: str) -> str:
        """Extract abstract from paper text."""
        # Look for "Abstract" section
        abstract_match = re.search(
            r'(?i)abstract[:\s]+(.*?)(?=\n\n|\nintroduction|\n1\.|\nkey)',
            text,
            re.DOTALL
        )
        if abstract_match:
            return abstract_match.group(1).strip()[:1000]  # Limit length
        return ""

    def process_pdf(self, pdf_path: str, prefer_grobid: bool = True) -> Dict:
        """
        Process PDF with automatic fallback strategy.

        Args:
            pdf_path: Path to PDF file
            prefer_grobid: Try GROBID first if available

        Returns:
            Dictionary with extracted data
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Get file size to determine best method
        file_size = pdf_path.stat().st_size / (1024 * 1024)  # MB

        print(f"Processing: {pdf_path.name} ({file_size:.1f} MB)")

        result = None

        # Strategy: Try GROBID for large files if available
        if prefer_grobid and self.grobid_available and file_size > 5:
            print("  Using GROBID (large file)...")
            try:
                result = self.extract_with_grobid(str(pdf_path))
            except Exception as e:
                print(f"  GROBID failed: {e}, falling back...")

        # Fallback to Python methods
        if result is None:
            if HAS_PYMUPDF:
                print("  Using PyMuPDF...")
                try:
                    result = self.extract_with_pymupdf(str(pdf_path))
                except Exception as e:
                    print(f"  PyMuPDF failed: {e}")

            if result is None and HAS_PDFPLUMBER:
                print("  Using pdfplumber...")
                try:
                    result = self.extract_with_pdfplumber(str(pdf_path))
                except Exception as e:
                    print(f"  pdfplumber failed: {e}")

        if result is None:
            raise Exception("All PDF processing methods failed. Please install required libraries.")

        # Add PDF metadata
        pdf_metadata = self.extract_metadata_with_pypdf(str(pdf_path))
        result['pdf_metadata'] = pdf_metadata

        # Add file info
        result['file_info'] = {
            'filename': pdf_path.name,
            'path': str(pdf_path),
            'size_mb': file_size,
            'processed_date': datetime.now().isoformat()
        }

        return result


def main():
    """Command-line interface for PDF processing."""
    if len(sys.argv) < 2:
        print("Usage: python pdf_processor.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    processor = PDFProcessor()

    try:
        result = processor.process_pdf(pdf_path)

        # Print summary
        print("\n" + "="*80)
        print("EXTRACTION SUMMARY")
        print("="*80)
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Title: {result.get('title', 'N/A')[:100]}")
        print(f"Authors: {', '.join(result.get('authors', [])[:3])}")
        print(f"Abstract: {result.get('abstract', 'N/A')[:200]}...")
        print(f"Pages: {result.get('page_count', 'N/A')}")
        print("="*80)

        # Save full result to JSON
        output_path = Path(pdf_path).stem + "_extracted.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nFull extraction saved to: {output_path}")

    except Exception as e:
        print(f"Error processing PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
