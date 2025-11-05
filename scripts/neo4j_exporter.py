#!/usr/bin/env python3
"""
Neo4j Knowledge Graph Exporter

This script exports the magnetosensitivity knowledge base to Neo4j.
Supports full graph export and filtered subgraph exports with preview.

Usage:
    python neo4j_exporter.py --test-connection
    python neo4j_exporter.py --preview-full
    python neo4j_exporter.py --export-full
    python neo4j_exporter.py --preview-subgraph --categories mechanisms,proteins
    python neo4j_exporter.py --export-subgraph --paper-ids nchem_2447,annurev...
    python neo4j_exporter.py --clear-graph --confirm

Author: Francois
Date: 2025-11-04
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

from neo4j_connection import Neo4jConnection
from neo4j_schema import (
    get_node_type_for_category,
    get_relationship_type_for_predicate,
    create_indexes
)


class Neo4jExporter:
    """Export knowledge base to Neo4j graph database."""

    def __init__(self, base_dir: str = None, creds_file: str = None):
        """Initialize exporter."""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.kb_dir = self.base_dir / "knowledge-base"
        self.papers_dir = self.kb_dir / "papers"
        self.index_dir = self.kb_dir / "index"
        self.ontology_dir = self.kb_dir / "ontology"

        self.conn = Neo4jConnection(creds_file=creds_file)

    def load_papers(self) -> List[Dict]:
        """Load all papers from master index."""
        master_index_file = self.index_dir / "master-index.json"
        if not master_index_file.exists():
            print("Warning: master-index.json not found")
            return []

        with open(master_index_file, 'r') as f:
            data = json.load(f)
            return data.get("papers", [])

    def load_ontology_terms(self) -> Dict:
        """Load all ontology terms."""
        terms_file = self.ontology_dir / "terms.json"
        if not terms_file.exists():
            print("Warning: terms.json not found")
            return {}

        with open(terms_file, 'r') as f:
            return json.load(f)

    def load_ontology_relationships(self) -> Dict:
        """Load all ontology relationships."""
        rel_file = self.ontology_dir / "relationships.json"
        if not rel_file.exists():
            print("Warning: relationships.json not found")
            return {}

        with open(rel_file, 'r') as f:
            return json.load(f)

    def filter_subgraph(self, paper_ids: Optional[List[str]] = None,
                       categories: Optional[List[str]] = None,
                       organisms: Optional[List[str]] = None) -> Tuple[List, Dict, Dict]:
        """
        Filter papers and ontology to create a subgraph.

        Args:
            paper_ids: List of paper IDs to include
            categories: List of ontology categories to include
            organisms: List of organisms to include

        Returns:
            Tuple of (filtered_papers, filtered_terms, filtered_relationships)
        """
        all_papers = self.load_papers()
        all_terms = self.load_ontology_terms()
        all_rels = self.load_ontology_relationships()

        # Filter papers
        if paper_ids:
            filtered_papers = [p for p in all_papers if p['paper_id'] in paper_ids]
        else:
            filtered_papers = all_papers

        # Filter terms by category
        filtered_terms = {"categories": {}}
        if categories:
            for cat in categories:
                if cat in all_terms.get("categories", {}):
                    filtered_terms["categories"][cat] = all_terms["categories"][cat]
        else:
            filtered_terms = all_terms

        # Filter relationships
        # Get all term_ids in filtered terms
        term_ids = set()
        for cat_terms in filtered_terms.get("categories", {}).values():
            term_ids.update(cat_terms.keys())

        filtered_rels = {
            "relationships": [
                rel for rel in all_rels.get("relationships", [])
                if rel["subject"] in term_ids or rel["object"] in term_ids
            ]
        }

        # Also include hierarchies and process_flows if they exist
        if "hierarchies" in all_rels:
            filtered_rels["hierarchies"] = all_rels["hierarchies"]
        if "process_flows" in all_rels:
            filtered_rels["process_flows"] = all_rels["process_flows"]

        return filtered_papers, filtered_terms, filtered_rels

    def preview_export(self, papers: List[Dict], terms: Dict, relationships: Dict):
        """
        Preview what will be exported without actually exporting.

        Args:
            papers: List of paper dictionaries
            terms: Ontology terms dictionary
            relationships: Ontology relationships dictionary
        """
        print("\n" + "=" * 80)
        print("EXPORT PREVIEW")
        print("=" * 80)

        # Count nodes by type
        node_counts = defaultdict(int)
        node_counts["Paper"] = len(papers)

        # Count terms by category
        for category, cat_terms in terms.get("categories", {}).items():
            node_type = get_node_type_for_category(category)
            node_counts[node_type] += len(cat_terms)

        print(f"\nNodes to be created ({sum(node_counts.values())} total):")
        for node_type, count in sorted(node_counts.items()):
            print(f"  {node_type:20s} {count:4d}")

        # Count relationships
        rel_counts = defaultdict(int)
        for rel in relationships.get("relationships", []):
            rel_type = get_relationship_type_for_predicate(rel["predicate"])
            rel_counts[rel_type] += 1

        print(f"\nRelationships to be created ({sum(rel_counts.values())} total):")
        for rel_type, count in sorted(rel_counts.items()):
            print(f"  {rel_type:30s} {count:4d}")

        # List papers
        if papers:
            print(f"\nPapers ({len(papers)}):")
            for p in papers[:10]:  # Show first 10
                title = p.get('title', 'Unknown')[:60]
                print(f"  - {p['paper_id']:40s} {title}")
            if len(papers) > 10:
                print(f"  ... and {len(papers) - 10} more")

        # List term categories
        if terms.get("categories"):
            print(f"\nOntology Categories ({len(terms['categories'])}):")
            for cat in sorted(terms['categories'].keys()):
                term_count = len(terms['categories'][cat])
                print(f"  - {cat:30s} ({term_count} terms)")

        print("=" * 80 + "\n")

    def create_paper_nodes(self, session, papers: List[Dict]) -> int:
        """
        Create Paper nodes in Neo4j.

        Args:
            session: Neo4j session
            papers: List of paper dictionaries

        Returns:
            Number of nodes created
        """
        print(f"\nCreating {len(papers)} Paper nodes...")
        created = 0

        for paper in papers:
            try:
                query = """
                MERGE (p:Paper {paper_id: $paper_id})
                SET p.doi = $doi,
                    p.title = $title,
                    p.authors = $authors,
                    p.year = $year,
                    p.date_added = $date_added
                """

                session.run(query,
                           paper_id=paper["paper_id"],
                           doi=paper.get("doi", ""),
                           title=paper.get("title", ""),
                           authors=paper.get("authors", []),
                           year=paper.get("year"),
                           date_added=paper.get("date_added", ""))
                created += 1

                if created % 10 == 0:
                    print(f"  Progress: {created}/{len(papers)}")

            except Exception as e:
                print(f"  ✗ Failed to create Paper {paper['paper_id']}: {e}")

        print(f"✓ Created {created} Paper nodes")
        return created

    def create_term_nodes(self, session, terms: Dict) -> int:
        """
        Create Term/Protein/Mechanism nodes from ontology.

        Args:
            session: Neo4j session
            terms: Ontology terms dictionary

        Returns:
            Number of nodes created
        """
        total_created = 0

        for category, cat_terms in terms.get("categories", {}).items():
            node_type = get_node_type_for_category(category)

            print(f"\nCreating {len(cat_terms)} {node_type} nodes from '{category}'...")
            created = 0

            for term_id, term_data in cat_terms.items():
                try:
                    # Build properties dict
                    props = {
                        "name": term_id,
                        "definition": term_data.get("definition", ""),
                        "source": term_data.get("source", "")
                    }

                    # Add synonyms if present
                    if "synonyms" in term_data:
                        props["synonyms"] = term_data["synonyms"]

                    # Add category-specific properties
                    if "variants" in term_data:
                        props["variants"] = term_data["variants"]
                    if "organisms" in term_data:
                        props["organisms"] = term_data["organisms"]
                    if "radical_forms" in term_data:
                        props["radical_forms"] = term_data["radical_forms"]
                    if "typical_values" in term_data:
                        props["typical_values"] = term_data["typical_values"]
                    if "applications" in term_data:
                        props["applications"] = term_data["applications"]

                    # Create node
                    query = f"""
                    MERGE (n:{node_type} {{name: $name}})
                    SET n += $props
                    """

                    session.run(query, name=term_id, props=props)
                    created += 1

                except Exception as e:
                    print(f"  ✗ Failed to create {node_type} {term_id}: {e}")

            print(f"✓ Created {created} {node_type} nodes")
            total_created += created

        return total_created

    def create_relationships(self, session, relationships: Dict) -> int:
        """
        Create relationships from ontology.

        Args:
            session: Neo4j session
            relationships: Ontology relationships dictionary

        Returns:
            Number of relationships created
        """
        rels = relationships.get("relationships", [])
        print(f"\nCreating {len(rels)} relationships...")
        created = 0

        for rel in rels:
            try:
                subject = rel["subject"]
                predicate = rel["predicate"]
                obj = rel["object"]
                source = rel.get("source", "")

                # Get relationship type
                rel_type = get_relationship_type_for_predicate(predicate)

                # Create relationship
                query = f"""
                MATCH (a {{name: $subject}})
                MATCH (b {{name: $object}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r.predicate = $predicate,
                    r.source = $source
                """

                session.run(query, subject=subject, object=obj,
                           predicate=predicate, source=source)
                created += 1

                if created % 50 == 0:
                    print(f"  Progress: {created}/{len(rels)}")

            except Exception as e:
                print(f"  ✗ Failed to create relationship {subject}-[{predicate}]->{obj}: {e}")

        print(f"✓ Created {created} relationships")
        return created

    def export_to_neo4j(self, papers: List[Dict], terms: Dict, relationships: Dict):
        """
        Export data to Neo4j.

        Args:
            papers: List of paper dictionaries
            terms: Ontology terms dictionary
            relationships: Ontology relationships dictionary
        """
        print("\n" + "=" * 80)
        print("EXPORTING TO NEO4J")
        print("=" * 80)

        # Connect to Neo4j
        self.conn.connect()

        with self.conn.get_session() as session:
            # Create indexes
            create_indexes(session)

            # Create nodes
            paper_count = self.create_paper_nodes(session, papers)
            term_count = self.create_term_nodes(session, terms)

            # Create relationships
            rel_count = self.create_relationships(session, relationships)

        print("\n" + "=" * 80)
        print("EXPORT COMPLETE")
        print("=" * 80)
        print(f"Papers:        {paper_count}")
        print(f"Terms:         {term_count}")
        print(f"Relationships: {rel_count}")
        print("=" * 80 + "\n")

        # Get database info
        info = self.conn.get_database_info()
        print("Database now contains:")
        print(f"  Total nodes: {info['node_count']}")
        print(f"  Total relationships: {info['relationship_count']}")

        self.conn.close()

    def export_full(self):
        """Export full knowledge graph to Neo4j."""
        papers = self.load_papers()
        terms = self.load_ontology_terms()
        relationships = self.load_ontology_relationships()

        self.export_to_neo4j(papers, terms, relationships)

    def preview_full(self):
        """Preview full knowledge graph export."""
        papers = self.load_papers()
        terms = self.load_ontology_terms()
        relationships = self.load_ontology_relationships()

        self.preview_export(papers, terms, relationships)

    def export_subgraph(self, paper_ids: Optional[List[str]] = None,
                       categories: Optional[List[str]] = None):
        """Export filtered subgraph to Neo4j."""
        papers, terms, relationships = self.filter_subgraph(paper_ids, categories)

        self.export_to_neo4j(papers, terms, relationships)

    def preview_subgraph(self, paper_ids: Optional[List[str]] = None,
                        categories: Optional[List[str]] = None):
        """Preview filtered subgraph export."""
        papers, terms, relationships = self.filter_subgraph(paper_ids, categories)

        self.preview_export(papers, terms, relationships)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Export magnetosensitivity knowledge base to Neo4j"
    )

    # Actions
    parser.add_argument("--test-connection", action="store_true",
                       help="Test Neo4j connection")
    parser.add_argument("--preview-full", action="store_true",
                       help="Preview full graph export")
    parser.add_argument("--export-full", action="store_true",
                       help="Export full graph to Neo4j")
    parser.add_argument("--preview-subgraph", action="store_true",
                       help="Preview subgraph export")
    parser.add_argument("--export-subgraph", action="store_true",
                       help="Export subgraph to Neo4j")
    parser.add_argument("--clear-graph", action="store_true",
                       help="Clear all data from Neo4j (requires --confirm)")

    # Filters
    parser.add_argument("--paper-ids", help="Comma-separated list of paper IDs")
    parser.add_argument("--categories", help="Comma-separated list of ontology categories")

    # Options
    parser.add_argument("--confirm", action="store_true",
                       help="Confirm destructive operations")
    parser.add_argument("--base-dir", help="Base directory of project")
    parser.add_argument("--creds", help="Path to Neo4j credentials file")

    args = parser.parse_args()

    # Set base directory
    base_dir = args.base_dir if args.base_dir else "/Users/clarice/Desktop/Claude test"

    # Initialize exporter
    exporter = Neo4jExporter(base_dir=base_dir, creds_file=args.creds)

    # Parse filters
    paper_ids = args.paper_ids.split(',') if args.paper_ids else None
    categories = args.categories.split(',') if args.categories else None

    try:
        if args.test_connection:
            exporter.conn.test_connection()

        elif args.preview_full:
            exporter.preview_full()

        elif args.export_full:
            print("\n⚠️  This will export the FULL knowledge graph to Neo4j.")
            if not args.confirm:
                response = input("Continue? (yes/no): ")
                if response.lower() != 'yes':
                    print("Cancelled.")
                    sys.exit(0)
            exporter.export_full()

        elif args.preview_subgraph:
            exporter.preview_subgraph(paper_ids=paper_ids, categories=categories)

        elif args.export_subgraph:
            print("\n⚠️  This will export a SUBGRAPH to Neo4j.")
            if not args.confirm:
                response = input("Continue? (yes/no): ")
                if response.lower() != 'yes':
                    print("Cancelled.")
                    sys.exit(0)
            exporter.export_subgraph(paper_ids=paper_ids, categories=categories)

        elif args.clear_graph:
            exporter.conn.clear_database(confirm=args.confirm)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
