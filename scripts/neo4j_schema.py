#!/usr/bin/env python3
"""
Neo4j Graph Schema Definition

This module defines the schema for the magnetosensitivity knowledge graph.
Includes node types, relationship types, and property specifications.

Author: Francois
Date: 2025-11-04
"""

from typing import Dict, List

# Node type definitions with properties
NODE_TYPES = {
    "Paper": {
        "description": "Research paper or book",
        "properties": {
            "paper_id": "str (required, unique)",
            "doi": "str (optional)",
            "title": "str (required)",
            "authors": "list[str]",
            "year": "int (optional)",
            "date_added": "str (ISO 8601)",
            "abstract": "str (optional)",
            "journal": "str (optional)"
        },
        "indexes": ["paper_id", "doi"]
    },

    "Term": {
        "description": "Ontology term (mechanism, concept, etc.)",
        "properties": {
            "term_id": "str (required, unique)",
            "category": "str (required)",
            "definition": "str (required)",
            "synonyms": "list[str]",
            "source": "str (DOI or paper_id)"
        },
        "indexes": ["term_id", "category"]
    },

    "Protein": {
        "description": "Protein involved in magnetosensitivity",
        "properties": {
            "name": "str (required, unique)",
            "variants": "list[str]",
            "organisms": "list[str]",
            "definition": "str"
        },
        "indexes": ["name"]
    },

    "Organism": {
        "description": "Species studied for magnetosensitivity",
        "properties": {
            "name": "str (required, unique)",
            "scientific_name": "str (optional)",
            "common_names": "list[str]"
        },
        "indexes": ["name"]
    },

    "Technique": {
        "description": "Experimental or computational technique",
        "properties": {
            "name": "str (required, unique)",
            "type": "str (experimental|computational)",
            "applications": "list[str]",
            "synonyms": "list[str]"
        },
        "indexes": ["name", "type"]
    },

    "MagneticField": {
        "description": "Magnetic field type or configuration",
        "properties": {
            "name": "str (required, unique)",
            "field_type": "str (static|oscillating|RF)",
            "typical_values": "str (range or value with units)",
            "definition": "str"
        },
        "indexes": ["name"]
    },

    "Cofactor": {
        "description": "Molecular cofactor (e.g., FAD, FMN)",
        "properties": {
            "name": "str (required, unique)",
            "radical_forms": "list[str]",
            "definition": "str"
        },
        "indexes": ["name"]
    },

    "Mechanism": {
        "description": "Biological or physical mechanism",
        "properties": {
            "name": "str (required, unique)",
            "definition": "str (required)",
            "synonyms": "list[str]"
        },
        "indexes": ["name"]
    }
}

# Relationship type definitions
RELATIONSHIP_TYPES = {
    "CITES": {
        "description": "Paper cites another paper",
        "from": "Paper",
        "to": "Paper",
        "properties": {}
    },

    "STUDIES": {
        "description": "Paper studies a protein, organism, or mechanism",
        "from": "Paper",
        "to": ["Protein", "Organism", "Mechanism"],
        "properties": {}
    },

    "USES_TECHNIQUE": {
        "description": "Paper uses an experimental or computational technique",
        "from": "Paper",
        "to": "Technique",
        "properties": {}
    },

    "DEFINES_TERM": {
        "description": "Paper defines or introduces a term",
        "from": "Paper",
        "to": "Term",
        "properties": {}
    },

    "IS_A": {
        "description": "Hierarchical relationship (term is a type of another term)",
        "from": "Term",
        "to": "Term",
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    },

    "RELATED_TO": {
        "description": "Terms are related in some way",
        "from": "Term",
        "to": "Term",
        "properties": {
            "relationship_type": "str",
            "source": "str (DOI or paper_id)"
        }
    },

    "EXHIBITS": {
        "description": "Protein exhibits a mechanism",
        "from": "Protein",
        "to": "Mechanism",
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    },

    "CONTAINS": {
        "description": "Protein contains a cofactor",
        "from": "Protein",
        "to": "Cofactor",
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    },

    "DETECTS": {
        "description": "Technique detects a term/phenomenon",
        "from": "Technique",
        "to": "Term",
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    },

    "MODELS": {
        "description": "Technique models a mechanism or phenomenon",
        "from": "Technique",
        "to": ["Mechanism", "Term"],
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    },

    "SENSITIVE_TO": {
        "description": "Mechanism is sensitive to a magnetic field type",
        "from": "Mechanism",
        "to": "MagneticField",
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    },

    "REQUIRES": {
        "description": "Mechanism requires a term/concept",
        "from": "Mechanism",
        "to": "Term",
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    },

    "FORMS_RADICAL_PAIR_WITH": {
        "description": "Cofactor forms radical pair with another cofactor",
        "from": "Cofactor",
        "to": "Cofactor",
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    },

    "ELECTRON_DONOR_FOR": {
        "description": "Cofactor acts as electron donor for another",
        "from": "Cofactor",
        "to": "Cofactor",
        "properties": {
            "source": "str (DOI or paper_id)"
        }
    }
}

# Category mapping from ontology to node types
ONTOLOGY_CATEGORY_MAPPING = {
    "mechanisms": "Mechanism",
    "proteins": "Protein",
    "cofactors_and_radicals": "Cofactor",
    "organisms": "Organism",
    "magnetic_fields": "MagneticField",
    "experimental_techniques": "Technique",
    "computational_methods": "Technique",
    "magnetic_interactions": "Term",
    "photochemistry": "Term",
    "spin_states": "Term"
}

# Relationship predicate mapping from ontology to Neo4j relationship types
PREDICATE_MAPPING = {
    "is_a": "IS_A",
    "contains": "CONTAINS",
    "exhibits": "EXHIBITS",
    "located_in": "RELATED_TO",
    "related_to": "RELATED_TO",
    "sensitive_to": "SENSITIVE_TO",
    "requires": "REQUIRES",
    "depends_on": "RELATED_TO",
    "detects": "DETECTS",
    "measures": "DETECTS",
    "monitors": "DETECTS",
    "models": "MODELS",
    "predicts": "MODELS",
    "drives": "REQUIRES",
    "provides": "RELATED_TO",
    "isolates": "RELATED_TO",
    "cofactor_of": "CONTAINS",
    "forms_radical_pair_with": "FORMS_RADICAL_PAIR_WITH",
    "electron_donor_for": "ELECTRON_DONOR_FOR",
    "triggers": "REQUIRES",
    "forms": "RELATED_TO",
    "interconverts_with": "RELATED_TO",
    "uses": "RELATED_TO",
    "produces": "RELATED_TO",
    "characteristic_of": "RELATED_TO",
    "enhances": "RELATED_TO"
}


def get_node_type_for_category(category: str) -> str:
    """
    Get Neo4j node type for an ontology category.

    Args:
        category: Ontology category name

    Returns:
        Node type string (e.g., "Mechanism", "Protein")
    """
    return ONTOLOGY_CATEGORY_MAPPING.get(category, "Term")


def get_relationship_type_for_predicate(predicate: str) -> str:
    """
    Get Neo4j relationship type for an ontology predicate.

    Args:
        predicate: Ontology relationship predicate

    Returns:
        Relationship type string (e.g., "IS_A", "CONTAINS")
    """
    return PREDICATE_MAPPING.get(predicate, "RELATED_TO")


def get_schema_summary() -> str:
    """
    Get a formatted summary of the graph schema.

    Returns:
        Multi-line string with schema information
    """
    summary = []
    summary.append("=" * 80)
    summary.append("NEO4J GRAPH SCHEMA")
    summary.append("=" * 80)

    summary.append(f"\nNode Types ({len(NODE_TYPES)}):")
    for node_type, spec in NODE_TYPES.items():
        summary.append(f"\n  {node_type}: {spec['description']}")
        summary.append(f"    Properties: {len(spec['properties'])}")
        if spec.get('indexes'):
            summary.append(f"    Indexes: {', '.join(spec['indexes'])}")

    summary.append(f"\nRelationship Types ({len(RELATIONSHIP_TYPES)}):")
    for rel_type, spec in RELATIONSHIP_TYPES.items():
        to_types = spec['to'] if isinstance(spec['to'], list) else [spec['to']]
        summary.append(f"\n  {rel_type}: ({spec['from']})-[:{rel_type}]->({', '.join(to_types)})")
        summary.append(f"    {spec['description']}")

    summary.append("\n" + "=" * 80)

    return "\n".join(summary)


def create_indexes(session):
    """
    Create indexes for all node types in Neo4j.

    Args:
        session: Neo4j session object
    """
    print("Creating indexes...")

    for node_type, spec in NODE_TYPES.items():
        if 'indexes' in spec:
            for index_prop in spec['indexes']:
                try:
                    # Create index
                    query = f"CREATE INDEX IF NOT EXISTS FOR (n:{node_type}) ON (n.{index_prop})"
                    session.run(query)
                    print(f"  ✓ Index on {node_type}.{index_prop}")
                except Exception as e:
                    print(f"  ✗ Failed to create index on {node_type}.{index_prop}: {e}")

    print("✓ Indexes created")


def main():
    """Print schema summary."""
    print(get_schema_summary())


if __name__ == "__main__":
    main()
