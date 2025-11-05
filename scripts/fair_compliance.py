#!/usr/bin/env python3
"""
FAIR Compliance Validator

This script validates papers against FAIR principles:
- Findable: Has DOI, indexed, complete metadata
- Accessible: Files exist, correct paths, valid JSON
- Interoperable: Linked to ontology, standard notation
- Reusable: Annotations exist, context populated, license info

Usage:
    python fair_compliance.py --validate <paper_id>     # Validate single paper
    python fair_compliance.py --validate-all             # Validate all processed papers
    python fair_compliance.py --report                   # Generate compliance report

Author: Francois
Date: 2025-11-04
"""

import json
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class FAIRComplianceValidator:
    """Validate FAIR compliance for papers in knowledge base."""

    def __init__(self, base_dir: str = None):
        """Initialize validator."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.papers_dir = self.base_dir / "knowledge-base" / "papers"
        self.index_dir = self.base_dir / "knowledge-base" / "index"
        self.ontology_dir = self.base_dir / "knowledge-base" / "ontology"

    def validate_paper(self, paper_id: str) -> Dict:
        """
        Validate a single paper against FAIR principles.
        Returns dict with score and detailed findings.
        """
        paper_dir = self.papers_dir / paper_id
        if not paper_dir.exists():
            return {
                "paper_id": paper_id,
                "score": 0,
                "valid": False,
                "error": f"Paper directory not found: {paper_dir}"
            }

        results = {
            "paper_id": paper_id,
            "findable": self._check_findable(paper_dir),
            "accessible": self._check_accessible(paper_dir),
            "interoperable": self._check_interoperable(paper_dir, paper_id),
            "reusable": self._check_reusable(paper_dir)
        }

        # Calculate total score
        total_score = (
            results["findable"]["score"] +
            results["accessible"]["score"] +
            results["interoperable"]["score"] +
            results["reusable"]["score"]
        )

        results["score"] = total_score
        results["valid"] = True
        results["timestamp"] = datetime.now().isoformat()

        return results

    def _check_findable(self, paper_dir: Path) -> Dict:
        """
        Check Findable criteria (25 points max).
        - Has valid DOI or unique identifier (10 pts)
        - Indexed in master-index.json (5 pts)
        - Metadata complete (title, authors, year) (10 pts)
        """
        score = 0
        issues = []
        details = {}

        # Load metadata
        metadata_file = paper_dir / "metadata.json"
        if not metadata_file.exists():
            return {"score": 0, "issues": ["metadata.json not found"], "details": {}}

        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except Exception as e:
            return {"score": 0, "issues": [f"Failed to read metadata: {e}"], "details": {}}

        # Check DOI (10 points)
        doi = metadata.get("doi", "")
        if doi and doi != "" and re.match(r'10\.\d{4,}/', doi):
            score += 10
            details["has_valid_doi"] = True
        elif metadata.get("paper_id"):
            score += 5  # Has unique ID but no DOI
            details["has_unique_id"] = True
            issues.append("No valid DOI found")
        else:
            details["has_valid_doi"] = False
            issues.append("No DOI or unique identifier")

        # Check indexed in master-index (5 points)
        master_index_file = self.index_dir / "master-index.json"
        if master_index_file.exists():
            try:
                with open(master_index_file, 'r') as f:
                    master_index = json.load(f)
                    paper_ids = [p.get("paper_id") for p in master_index.get("papers", [])]
                    if metadata.get("paper_id") in paper_ids:
                        score += 5
                        details["indexed"] = True
                    else:
                        issues.append("Not indexed in master-index.json")
                        details["indexed"] = False
            except Exception as e:
                issues.append(f"Failed to check master index: {e}")
                details["indexed"] = False
        else:
            issues.append("master-index.json not found")
            details["indexed"] = False

        # Check metadata completeness (10 points)
        title = metadata.get("title", "")
        authors = metadata.get("authors", [])
        year = metadata.get("publication", {}).get("year")

        completeness_score = 0
        if title and title != "--- Page 1 ---" and title != "":
            completeness_score += 4
            details["has_title"] = True
        else:
            issues.append("Title missing or not extracted properly")
            details["has_title"] = False

        if authors and len(authors) > 0 and authors[0] != "":
            completeness_score += 3
            details["has_authors"] = True
        else:
            issues.append("Authors missing or not extracted")
            details["has_authors"] = False

        if year is not None:
            completeness_score += 3
            details["has_year"] = True
        else:
            issues.append("Publication year missing")
            details["has_year"] = False

        score += completeness_score

        return {"score": score, "max_score": 25, "issues": issues, "details": details}

    def _check_accessible(self, paper_dir: Path) -> Dict:
        """
        Check Accessible criteria (25 points max).
        - File paths correct (10 pts)
        - full_text.txt exists and non-empty (10 pts)
        - metadata.json valid JSON (5 pts)
        """
        score = 0
        issues = []
        details = {}

        # Check file paths (10 points)
        required_files = ["metadata.json", "context.md", "annotations.md", "full_text.txt"]
        existing_files = [f for f in required_files if (paper_dir / f).exists()]

        if len(existing_files) == 4:
            score += 10
            details["all_files_exist"] = True
        else:
            missing = set(required_files) - set(existing_files)
            score += int(len(existing_files) / len(required_files) * 10)
            issues.append(f"Missing files: {', '.join(missing)}")
            details["all_files_exist"] = False
            details["missing_files"] = list(missing)

        # Check full_text.txt (10 points)
        full_text_file = paper_dir / "full_text.txt"
        if full_text_file.exists():
            try:
                text = full_text_file.read_text()
                if len(text) > 1000:  # At least 1KB of text
                    score += 10
                    details["full_text_adequate"] = True
                else:
                    score += 5
                    issues.append(f"full_text.txt is short ({len(text)} chars)")
                    details["full_text_adequate"] = False
            except Exception as e:
                issues.append(f"Failed to read full_text.txt: {e}")
                details["full_text_adequate"] = False
        else:
            issues.append("full_text.txt not found")
            details["full_text_adequate"] = False

        # Check metadata.json valid (5 points) - already validated in findable
        metadata_file = paper_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    json.load(f)
                score += 5
                details["metadata_valid_json"] = True
            except Exception as e:
                issues.append(f"metadata.json invalid JSON: {e}")
                details["metadata_valid_json"] = False
        else:
            details["metadata_valid_json"] = False

        return {"score": score, "max_score": 25, "issues": issues, "details": details}

    def _check_interoperable(self, paper_dir: Path, paper_id: str) -> Dict:
        """
        Check Interoperable criteria (25 points max).
        - Linked to ≥1 ontology term (10 pts)
        - Uses standard notation (DOI format, units) (10 pts)
        - Context.md follows template (5 pts)
        """
        score = 0
        issues = []
        details = {}

        # Load metadata
        metadata_file = paper_dir / "metadata.json"
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except:
            return {"score": 0, "max_score": 25, "issues": ["Cannot read metadata"], "details": {}}

        # Check ontology links (10 points)
        ontology_terms = metadata.get("interoperability", {}).get("ontology_terms", [])
        if len(ontology_terms) >= 3:
            score += 10
            details["ontology_linked"] = True
            details["ontology_term_count"] = len(ontology_terms)
        elif len(ontology_terms) >= 1:
            score += 5
            details["ontology_linked"] = True
            details["ontology_term_count"] = len(ontology_terms)
            issues.append(f"Only {len(ontology_terms)} ontology terms linked (3+ recommended)")
        else:
            issues.append("No ontology terms linked")
            details["ontology_linked"] = False
            details["ontology_term_count"] = 0

        # Check standard notation (10 points)
        notation_score = 0

        # DOI format
        doi = metadata.get("doi", "")
        if doi and re.match(r'10\.\d{4,}/', doi):
            notation_score += 5
            details["uses_doi_format"] = True
        else:
            details["uses_doi_format"] = False

        # Check for standard units in research context
        mag_field = metadata.get("research_context", {}).get("magnetic_field_parameters", {})
        if mag_field.get("field_strength") or mag_field.get("frequency"):
            notation_score += 5
            details["uses_standard_units"] = True
        else:
            details["uses_standard_units"] = False

        score += notation_score

        # Check context.md follows template (5 points)
        context_file = paper_dir / "context.md"
        if context_file.exists():
            try:
                context = context_file.read_text()
                # Check for expected sections
                has_header = "# Paper Context:" in context or "# Context:" in context
                has_doi = "DOI:" in context or "doi:" in context

                if has_header and len(context) > 200:
                    score += 5
                    details["context_follows_template"] = True
                elif has_header or has_doi:
                    score += 3
                    details["context_follows_template"] = "partial"
                    issues.append("context.md partially follows template")
                else:
                    issues.append("context.md does not follow template")
                    details["context_follows_template"] = False
            except Exception as e:
                issues.append(f"Failed to read context.md: {e}")
                details["context_follows_template"] = False
        else:
            issues.append("context.md not found")
            details["context_follows_template"] = False

        return {"score": score, "max_score": 25, "issues": issues, "details": details}

    def _check_reusable(self, paper_dir: Path) -> Dict:
        """
        Check Reusable criteria (25 points max).
        - Annotations.md exists (5 pts)
        - Research context populated (10 pts)
        - License/access info present (10 pts)
        """
        score = 0
        issues = []
        details = {}

        # Load metadata
        metadata_file = paper_dir / "metadata.json"
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except:
            return {"score": 0, "max_score": 25, "issues": ["Cannot read metadata"], "details": {}}

        # Check annotations.md (5 points)
        annotations_file = paper_dir / "annotations.md"
        if annotations_file.exists():
            try:
                content = annotations_file.read_text()
                if len(content) > 100:  # Has some content
                    score += 5
                    details["has_annotations"] = True
                else:
                    score += 2
                    details["has_annotations"] = "minimal"
            except:
                issues.append("Failed to read annotations.md")
                details["has_annotations"] = False
        else:
            issues.append("annotations.md not found")
            details["has_annotations"] = False

        # Check research context populated (10 points)
        research_context = metadata.get("research_context", {})
        populated_fields = sum([
            bool(research_context.get("species_studied")),
            bool(research_context.get("proteins")),
            bool(research_context.get("magnetic_field_parameters", {}).get("field_strength")),
            bool(research_context.get("experimental_techniques")),
            bool(research_context.get("computational_methods")),
            bool(research_context.get("key_findings"))
        ])

        context_score = int(populated_fields / 6 * 10)
        score += context_score
        details["research_context_fields_populated"] = populated_fields

        if populated_fields < 3:
            issues.append(f"Research context under-populated ({populated_fields}/6 fields)")

        # Check license/access info (10 points)
        access_info = metadata.get("access", {})
        has_license = access_info.get("license") and access_info.get("license") != "Unknown"
        has_access_level = access_info.get("access_level")
        has_original_file = access_info.get("original_file")

        access_score = 0
        if has_license:
            access_score += 5
            details["has_license"] = True
        else:
            issues.append("License information missing")
            details["has_license"] = False

        if has_access_level and has_original_file:
            access_score += 5
            details["has_access_info"] = True
        else:
            details["has_access_info"] = "partial"

        score += access_score

        return {"score": score, "max_score": 25, "issues": issues, "details": details}

    def validate_all_papers(self) -> List[Dict]:
        """Validate all processed papers."""
        if not self.papers_dir.exists():
            print(f"Error: Papers directory not found: {self.papers_dir}")
            return []

        paper_ids = [
            d.name for d in self.papers_dir.iterdir()
            if d.is_dir() and not d.name.startswith('TEMPLATE')
        ]

        print(f"Validating {len(paper_ids)} papers...")
        results = []

        for i, paper_id in enumerate(paper_ids, 1):
            print(f"  [{i}/{len(paper_ids)}] {paper_id}...", end=" ")
            result = self.validate_paper(paper_id)
            if result.get("valid"):
                print(f"{result['score']}/100")
                results.append(result)
            else:
                print(f"FAILED: {result.get('error')}")

        return results

    def generate_report(self, results: List[Dict] = None):
        """Generate compliance report."""
        if results is None:
            results = self.validate_all_papers()

        if not results:
            print("No results to report")
            return

        print("\n" + "=" * 80)
        print("FAIR COMPLIANCE REPORT")
        print("=" * 80)

        # Overall statistics
        scores = [r["score"] for r in results]
        avg_score = sum(scores) / len(scores)
        print(f"\nPapers Validated: {len(results)}")
        print(f"Average Score: {avg_score:.1f}/100")
        print(f"Range: {min(scores):.1f} - {max(scores):.1f}")

        # Score distribution
        excellent = sum(1 for s in scores if s >= 90)
        good = sum(1 for s in scores if 70 <= s < 90)
        needs_work = sum(1 for s in scores if s < 70)

        print(f"\nScore Distribution:")
        print(f"  Excellent (≥90): {excellent} ({excellent/len(results)*100:.1f}%)")
        print(f"  Good (70-89):    {good} ({good/len(results)*100:.1f}%)")
        print(f"  Needs Work (<70): {needs_work} ({needs_work/len(results)*100:.1f}%)")

        # Category breakdown
        findable = [r["findable"]["score"] for r in results]
        accessible = [r["accessible"]["score"] for r in results]
        interoperable = [r["interoperable"]["score"] for r in results]
        reusable = [r["reusable"]["score"] for r in results]

        print(f"\nFAIR Category Averages:")
        print(f"  Findable:       {sum(findable)/len(findable):.1f}/25")
        print(f"  Accessible:     {sum(accessible)/len(accessible):.1f}/25")
        print(f"  Interoperable:  {sum(interoperable)/len(interoperable):.1f}/25")
        print(f"  Reusable:       {sum(reusable)/len(reusable):.1f}/25")

        # Papers needing attention
        low_scorers = sorted([r for r in results if r["score"] < 70],
                            key=lambda x: x["score"])

        if low_scorers:
            print(f"\nPapers Needing Attention ({len(low_scorers)}):")
            for r in low_scorers[:10]:  # Show top 10
                print(f"  {r['paper_id']:40s} {r['score']:5.1f}/100")
                # Show top issues
                all_issues = (r["findable"]["issues"] + r["accessible"]["issues"] +
                             r["interoperable"]["issues"] + r["reusable"]["issues"])
                for issue in all_issues[:2]:
                    print(f"    • {issue}")

        print("=" * 80 + "\n")

        # Save report
        report_file = self.index_dir / "fair_compliance_report.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_papers": len(results),
                    "average_score": avg_score,
                    "score_distribution": {
                        "excellent": excellent,
                        "good": good,
                        "needs_work": needs_work
                    }
                },
                "results": results
            }, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved report to {report_file}")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Validate FAIR compliance for papers"
    )
    parser.add_argument("--validate", metavar="PAPER_ID",
                       help="Validate single paper")
    parser.add_argument("--validate-all", action="store_true",
                       help="Validate all processed papers")
    parser.add_argument("--report", action="store_true",
                       help="Generate compliance report")
    parser.add_argument("--base-dir", help="Base directory of project",
                       default="/Users/clarice/Desktop/Claude test")

    args = parser.parse_args()

    validator = FAIRComplianceValidator(base_dir=args.base_dir)

    if args.validate:
        result = validator.validate_paper(args.validate)
        print(json.dumps(result, indent=2))
    elif args.validate_all or args.report:
        results = validator.validate_all_papers()
        if args.report:
            validator.generate_report(results)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
