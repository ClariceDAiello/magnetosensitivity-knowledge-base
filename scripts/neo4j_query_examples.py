#!/usr/bin/env python3
"""
Neo4j Query Examples

Useful Cypher queries for exploring the magnetosensitivity knowledge graph.

Usage:
    python neo4j_query_examples.py --run <query_name>
    python neo4j_query_examples.py --list

Author: Francois
Date: 2025-11-04
"""

import sys
import argparse
from neo4j_connection import Neo4jConnection


# Query catalog
QUERIES = {
    "all_papers": {
        "description": "List all papers in the graph",
        "cypher": """
        MATCH (p:Paper)
        RETURN p.paper_id, p.title, p.year
        ORDER BY p.year DESC
        """
    },

    "papers_studying_cryptochrome": {
        "description": "Find all papers studying cryptochrome",
        "cypher": """
        MATCH (p:Paper)-[:STUDIES]->(protein:Protein {name: 'cryptochrome'})
        RETURN p.paper_id, p.title, p.year
        ORDER BY p.year DESC
        """
    },

    "cryptochrome_mechanisms": {
        "description": "Find mechanisms exhibited by cryptochrome",
        "cypher": """
        MATCH (p:Protein {name: 'cryptochrome'})-[:EXHIBITS]->(m:Mechanism)
        RETURN p.name, m.name, m.definition
        """
    },

    "radical_pair_papers": {
        "description": "Papers studying the radical pair mechanism",
        "cypher": """
        MATCH (p:Paper)-[:STUDIES]->(m:Mechanism {name: 'radical_pair_mechanism'})
        RETURN p.paper_id, p.title, p.year
        ORDER BY p.year DESC
        """
    },

    "techniques_for_radical_pairs": {
        "description": "Techniques used to detect radical pairs",
        "cypher": """
        MATCH (t:Technique)-[r:DETECTS]->(term)
        WHERE term.name CONTAINS 'radical'
        RETURN t.name, type(r), term.name, r.source
        """
    },

    "protein_cofactor_network": {
        "description": "Proteins and their cofactors",
        "cypher": """
        MATCH (p:Protein)-[:CONTAINS]->(c:Cofactor)
        RETURN p.name, c.name, c.radical_forms
        """
    },

    "radical_pair_formation": {
        "description": "Cofactors that form radical pairs",
        "cypher": """
        MATCH (c1:Cofactor)-[:FORMS_RADICAL_PAIR_WITH]->(c2:Cofactor)
        RETURN c1.name, c2.name
        """
    },

    "mechanism_requirements": {
        "description": "What mechanisms require (dependencies)",
        "cypher": """
        MATCH (m:Mechanism)-[:REQUIRES]->(req)
        RETURN m.name, req.name, req.definition
        """
    },

    "paper_citation_network": {
        "description": "Citation relationships between papers",
        "cypher": """
        MATCH (p1:Paper)-[:CITES]->(p2:Paper)
        RETURN p1.paper_id, p1.title, p2.paper_id, p2.title
        """
    },

    "most_studied_proteins": {
        "description": "Proteins studied by most papers",
        "cypher": """
        MATCH (p:Paper)-[:STUDIES]->(protein:Protein)
        RETURN protein.name, count(p) AS paper_count
        ORDER BY paper_count DESC
        LIMIT 10
        """
    },

    "most_used_techniques": {
        "description": "Most frequently used techniques",
        "cypher": """
        MATCH (p:Paper)-[:USES_TECHNIQUE]->(t:Technique)
        RETURN t.name, t.type, count(p) AS usage_count
        ORDER BY usage_count DESC
        LIMIT 10
        """
    },

    "magnetic_field_sensitivity": {
        "description": "Mechanisms sensitive to magnetic fields",
        "cypher": """
        MATCH (m:Mechanism)-[:SENSITIVE_TO]->(mf:MagneticField)
        RETURN m.name, mf.name, mf.typical_values
        """
    },

    "shortest_path_hyperfine_compass": {
        "description": "Shortest path from hyperfine coupling to magnetic compass",
        "cypher": """
        MATCH path = shortestPath(
          (start {name: 'hyperfine_coupling'})-[*]-(end {name: 'magnetic_compass'})
        )
        RETURN [node in nodes(path) | node.name] AS path_nodes,
               length(path) AS path_length
        """
    },

    "term_hierarchy": {
        "description": "Hierarchical relationships (IS_A)",
        "cypher": """
        MATCH (child)-[:IS_A]->(parent)
        RETURN child.name, parent.name
        ORDER BY parent.name, child.name
        """
    },

    "cryptochrome_neighborhood": {
        "description": "All nodes connected to cryptochrome (1 hop)",
        "cypher": """
        MATCH (crypto:Protein {name: 'cryptochrome'})-[r]-(connected)
        RETURN crypto.name, type(r) AS relationship, connected.name, labels(connected)[0] AS node_type
        """
    },

    "papers_by_year": {
        "description": "Count of papers by year",
        "cypher": """
        MATCH (p:Paper)
        WHERE p.year IS NOT NULL
        RETURN p.year, count(p) AS paper_count
        ORDER BY p.year
        """
    },

    "graph_statistics": {
        "description": "Overall graph statistics",
        "cypher": """
        MATCH (n)
        WITH labels(n)[0] AS label, count(n) AS count
        RETURN label, count
        ORDER BY count DESC
        UNION ALL
        MATCH ()-[r]->()
        WITH type(r) AS rel_type, count(r) AS count
        RETURN rel_type AS label, count
        ORDER BY count DESC
        """
    },

    "find_papers_with_doi": {
        "description": "Papers with valid DOIs",
        "cypher": """
        MATCH (p:Paper)
        WHERE p.doi IS NOT NULL AND p.doi <> ''
        RETURN p.paper_id, p.doi, p.title
        ORDER BY p.paper_id
        """
    },

    "organisms_and_proteins": {
        "description": "Organisms and the proteins they contain",
        "cypher": """
        MATCH (o:Organism)<-[:RELATED_TO]-(p:Protein)
        RETURN o.name, collect(p.name) AS proteins
        """
    },

    "computational_vs_experimental": {
        "description": "Count of computational vs experimental techniques",
        "cypher": """
        MATCH (t:Technique)
        RETURN t.type, count(t) AS count
        ORDER BY count DESC
        """
    }
}


def list_queries():
    """List all available queries."""
    print("\n" + "=" * 80)
    print("AVAILABLE QUERIES")
    print("=" * 80 + "\n")

    for name, info in sorted(QUERIES.items()):
        print(f"{name}:")
        print(f"  {info['description']}")
        print()

    print("=" * 80)
    print(f"\nTotal queries: {len(QUERIES)}")
    print("\nUsage: python neo4j_query_examples.py --run <query_name>")
    print("=" * 80 + "\n")


def run_query(query_name: str, conn: Neo4jConnection, limit: int = 100):
    """
    Run a named query and display results.

    Args:
        query_name: Name of query from QUERIES dict
        conn: Neo4j connection
        limit: Maximum number of results to display
    """
    if query_name not in QUERIES:
        print(f"Error: Query '{query_name}' not found")
        print(f"Available queries: {', '.join(QUERIES.keys())}")
        return

    query_info = QUERIES[query_name]

    print("\n" + "=" * 80)
    print(f"QUERY: {query_name}")
    print("=" * 80)
    print(f"Description: {query_info['description']}")
    print("\nCypher:")
    print(query_info['cypher'])
    print("=" * 80 + "\n")

    try:
        with conn.get_session() as session:
            result = session.run(query_info['cypher'])
            records = list(result)

            if not records:
                print("No results found.\n")
                return

            print(f"Results ({len(records)} total, showing first {min(len(records), limit)}):\n")

            # Display results
            for i, record in enumerate(records[:limit], 1):
                print(f"{i}. {dict(record)}")

            if len(records) > limit:
                print(f"\n... and {len(records) - limit} more results")

            print()

    except Exception as e:
        print(f"Error running query: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Run example Cypher queries on the knowledge graph"
    )
    parser.add_argument("--list", action="store_true",
                       help="List all available queries")
    parser.add_argument("--run", metavar="QUERY_NAME",
                       help="Run a named query")
    parser.add_argument("--limit", type=int, default=100,
                       help="Maximum number of results to display (default: 100)")
    parser.add_argument("--creds", help="Path to Neo4j credentials file")

    args = parser.parse_args()

    if args.list:
        list_queries()
    elif args.run:
        try:
            conn = Neo4jConnection(creds_file=args.creds)
            if conn.test_connection():
                run_query(args.run, conn, limit=args.limit)
                conn.close()
            else:
                print("Failed to connect to Neo4j")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
