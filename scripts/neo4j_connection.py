#!/usr/bin/env python3
"""
Neo4j Connection Manager

This module handles Neo4j connection using credentials from neocreds.txt.
Provides connection testing and management functions.

Usage:
    from neo4j_connection import Neo4jConnection

    conn = Neo4jConnection()
    if conn.test_connection():
        # Use conn.driver for queries
        pass

Author: Francois
Date: 2025-11-04
"""

import sys
from pathlib import Path
from typing import Dict, Optional


def load_neo4j_credentials(creds_file: str = None) -> Dict[str, str]:
    """
    Load Neo4j credentials from neocreds.txt.

    Args:
        creds_file: Path to credentials file (default: neocreds.txt in project root)

    Returns:
        Dictionary with uri, username, password, database
    """
    if creds_file is None:
        # Default to project root
        base_dir = Path(__file__).parent.parent
        creds_file = base_dir / "neocreds.txt"
    else:
        creds_file = Path(creds_file)

    if not creds_file.exists():
        raise FileNotFoundError(f"Credentials file not found: {creds_file}")

    creds = {}
    with open(creds_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                # Convert NEO4J_URI to uri, etc.
                clean_key = key.replace('NEO4J_', '').lower()
                creds[clean_key] = value

    # Validate required fields
    required = ['uri', 'username', 'password', 'database']
    missing = [k for k in required if k not in creds]
    if missing:
        raise ValueError(f"Missing required credentials: {', '.join(missing)}")

    return creds


class Neo4jConnection:
    """Neo4j connection manager."""

    def __init__(self, creds_file: str = None):
        """
        Initialize Neo4j connection.

        Args:
            creds_file: Path to credentials file (default: neocreds.txt)
        """
        self.creds = load_neo4j_credentials(creds_file)
        self.driver = None
        self._connected = False

    def connect(self):
        """Establish connection to Neo4j."""
        try:
            from neo4j import GraphDatabase
        except ImportError:
            raise ImportError(
                "neo4j package not installed. Run: pip install neo4j"
            )

        try:
            self.driver = GraphDatabase.driver(
                self.creds['uri'],
                auth=(self.creds['username'], self.creds['password'])
            )
            self._connected = True
            print(f"✓ Connected to Neo4j at {self.creds['uri']}")
        except Exception as e:
            print(f"✗ Failed to connect to Neo4j: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test Neo4j connection.

        Returns:
            True if connection successful, False otherwise
        """
        if not self._connected:
            try:
                self.connect()
            except:
                return False

        try:
            with self.driver.session(database=self.creds['database']) as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]
                if test_value == 1:
                    print("✓ Connection test passed")
                    return True
        except Exception as e:
            print(f"✗ Connection test failed: {e}")
            return False

        return False

    def get_session(self):
        """
        Get a Neo4j session.

        Returns:
            Neo4j session object
        """
        if not self._connected:
            self.connect()

        return self.driver.session(database=self.creds['database'])

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            self._connected = False
            print("✓ Closed Neo4j connection")

    def get_database_info(self) -> Dict:
        """
        Get information about the Neo4j database.

        Returns:
            Dictionary with database statistics
        """
        if not self._connected:
            self.connect()

        info = {}

        with self.get_session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) AS node_count")
            info['node_count'] = result.single()["node_count"]

            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS rel_count")
            info['relationship_count'] = result.single()["rel_count"]

            # Get node labels
            result = session.run("CALL db.labels()")
            info['labels'] = [record["label"] for record in result]

            # Get relationship types
            result = session.run("CALL db.relationshipTypes()")
            info['relationship_types'] = [record["relationshipType"] for record in result]

        return info

    def clear_database(self, confirm: bool = False):
        """
        Clear all nodes and relationships from database.

        WARNING: This is destructive and cannot be undone!

        Args:
            confirm: Must be True to actually clear the database
        """
        if not confirm:
            print("⚠️  WARNING: This will delete ALL data from the database!")
            print("   Set confirm=True to proceed")
            return False

        if not self._connected:
            self.connect()

        print("Clearing database...")

        with self.get_session() as session:
            # Delete all nodes and relationships
            session.run("MATCH (n) DETACH DELETE n")

        print("✓ Database cleared")
        return True

    def __enter__(self):
        """Context manager entry."""
        if not self._connected:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Command-line interface for testing connection."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Neo4j connection")
    parser.add_argument("--info", action="store_true",
                       help="Show database information")
    parser.add_argument("--clear", action="store_true",
                       help="Clear database (requires --confirm)")
    parser.add_argument("--confirm", action="store_true",
                       help="Confirm destructive operations")
    parser.add_argument("--creds", help="Path to credentials file",
                       default=None)

    args = parser.parse_args()

    try:
        conn = Neo4jConnection(creds_file=args.creds)

        print("\n" + "=" * 80)
        print("NEO4J CONNECTION TEST")
        print("=" * 80)
        print(f"URI: {conn.creds['uri']}")
        print(f"Database: {conn.creds['database']}")
        print(f"Username: {conn.creds['username']}")
        print("=" * 80 + "\n")

        if conn.test_connection():
            print("\n✓ Connection successful!\n")

            if args.info:
                print("=" * 80)
                print("DATABASE INFORMATION")
                print("=" * 80)
                info = conn.get_database_info()
                print(f"Nodes: {info['node_count']}")
                print(f"Relationships: {info['relationship_count']}")

                if info['labels']:
                    print(f"\nNode Labels ({len(info['labels'])}):")
                    for label in info['labels']:
                        print(f"  - {label}")

                if info['relationship_types']:
                    print(f"\nRelationship Types ({len(info['relationship_types'])}):")
                    for rel_type in info['relationship_types']:
                        print(f"  - {rel_type}")

                print("=" * 80 + "\n")

            if args.clear:
                conn.clear_database(confirm=args.confirm)
        else:
            print("\n✗ Connection failed!\n")
            sys.exit(1)

        conn.close()

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
