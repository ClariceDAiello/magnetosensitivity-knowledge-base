# Neo4j Knowledge Graph Integration

## Overview

This knowledge base now includes full Neo4j graph database integration, enabling powerful graph queries to explore relationships between papers, proteins, mechanisms, organisms, and other research entities.

**Current Status:**
- Neo4j sandbox deployed at `bolt://44.202.214.48`
- 84 nodes exported (47 papers + 37 ontology terms)
- 24 relationships established
- 11 indexes created for efficient querying

---

## Quick Start

### 1. Test the Connection

```bash
python scripts/neo4j_connection.py
```

Expected output:
```
Testing Neo4j connection...
✓ Connection successful!
Database: neo4j

Current graph contents:
Nodes: 84
Relationships: 24
Node types: ['Paper', 'Mechanism', 'Protein', ...]
Relationship types: ['CITES', 'STUDIES', 'EXHIBITS', ...]
```

### 2. Run Example Queries

```bash
python scripts/neo4j_query_examples.py

# Interactive menu:
# 1. List all available queries
# 2. Run specific query
# 3. Execute custom Cypher
```

### 3. Export Data to Neo4j

```bash
python scripts/neo4j_exporter.py

# Options:
# 1. Preview full export (without uploading)
# 2. Export full knowledge base
# 3. Export filtered subgraph
# 4. Clear database
```

---

## Graph Schema

### Node Types

1. **Paper**
   - Properties: `paper_id`, `doi`, `title`, `authors`, `year`, `journal`, `keywords`
   - Indexed on: `paper_id`, `doi`

2. **Mechanism**
   - Properties: `name`, `definition`, `synonyms`, `related_terms`
   - Indexed on: `name`

3. **Protein**
   - Properties: `name`, `full_name`, `function`, `structure`
   - Indexed on: `name`

4. **Cofactor**
   - Properties: `name`, `formula`, `role`, `wavelength`
   - Indexed on: `name`

5. **Organism**
   - Properties: `name`, `common_name`, `taxonomy`, `relevance`
   - Indexed on: `name`

6. **Technique**
   - Properties: `name`, `full_name`, `description`, `applications`
   - Indexed on: `name`

7. **MagneticField**
   - Properties: `name`, `field_strength`, `frequency`, `field_type`, `orientation`
   - Indexed on: `name`

8. **Term**
   - Properties: `name`, `category`, `definition`, `synonyms`
   - Indexed on: `name`, `category`

### Relationship Types

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `CITES` | Paper | Paper | Citation relationship |
| `STUDIES` | Paper | Protein/Organism | Research subject |
| `USES_TECHNIQUE` | Paper | Technique | Experimental method |
| `DEFINES_TERM` | Paper | Term | Introduces concept |
| `IS_A` | Term | Term | Hierarchical relationship |
| `RELATED_TO` | Term | Term | Conceptual connection |
| `EXHIBITS` | Protein | Mechanism | Demonstrates behavior |
| `CONTAINS` | Protein | Cofactor | Structural component |
| `DETECTS` | Technique | Mechanism | Can observe |
| `MODELS` | Technique | Mechanism | Can simulate |
| `SENSITIVE_TO` | Protein | MagneticField | Responds to field |
| `REQUIRES` | Mechanism | Cofactor | Needs for function |
| `FORMS_RADICAL_PAIR_WITH` | Cofactor | Cofactor | RPM connection |
| `ELECTRON_DONOR_FOR` | Cofactor | Cofactor | Redox relationship |

---

## Common Query Patterns

### Find Papers About a Topic

```cypher
// Papers studying cryptochrome
MATCH (p:Paper)-[:STUDIES]->(protein:Protein {name: 'cryptochrome'})
RETURN p.title, p.year, p.doi
ORDER BY p.year DESC
```

### Explore Protein Mechanisms

```cypher
// What mechanisms does cryptochrome exhibit?
MATCH (p:Protein {name: 'cryptochrome'})-[:EXHIBITS]->(m:Mechanism)
RETURN p.name, m.name, m.definition
```

### Find Radical Pair Cofactors

```cypher
// Which cofactors form radical pairs?
MATCH (c1:Cofactor)-[:FORMS_RADICAL_PAIR_WITH]->(c2:Cofactor)
RETURN c1.name, c2.name, c1.wavelength, c2.role
```

### Trace Research Networks

```cypher
// Papers citing papers about radical pair mechanism
MATCH (p1:Paper)-[:DEFINES_TERM]->(t:Term {category: 'mechanisms', name: 'radical_pair_mechanism'})
MATCH (p2:Paper)-[:CITES]->(p1)
RETURN p1.title AS source, p2.title AS citing, p2.year
```

### Find Techniques for Studying Mechanisms

```cypher
// Techniques that can detect or model a mechanism
MATCH (tech:Technique)-[r:DETECTS|MODELS]->(m:Mechanism {name: 'chemical_amplification'})
RETURN tech.name, type(r), m.name, tech.description
```

### Field Sensitivity Analysis

```cypher
// Proteins sensitive to geomagnetic fields
MATCH (p:Protein)-[:SENSITIVE_TO]->(mf:MagneticField)
WHERE mf.field_strength =~ '.*µT.*'
RETURN p.name, mf.field_strength, mf.field_type
```

---

## Workflow: Adding New Papers to the Graph

### Step 1: Process the Paper

```bash
python scripts/process_paper.py "Literature/new-paper.pdf" --doi "10.XXXX/EXAMPLE"
```

### Step 2: Verify FAIR Compliance

```bash
python scripts/fair_compliance.py --paper-id "new_paper_id"
```

If FAIR score < 50, manually edit:
- `knowledge-base/papers/new_paper_id/metadata.json`
- `knowledge-base/papers/new_paper_id/context.md`

### Step 3: Extract Ontology Terms

Review the paper and add new terms to:
- `knowledge-base/ontology/terms.json`
- `knowledge-base/ontology/abbreviations.json`
- `knowledge-base/ontology/relationships.json`

### Step 4: Export to Neo4j

```bash
python scripts/neo4j_exporter.py

# Choose option 2 or 3:
# 2. Export full knowledge base (incremental update)
# 3. Export filtered subgraph (test specific papers)
```

The exporter uses `MERGE` operations, so running it multiple times is safe (idempotent).

### Step 5: Verify in Neo4j

```bash
python scripts/neo4j_query_examples.py

# Run "Graph statistics" query to confirm new nodes
```

---

## Subgraph Export Options

When running `neo4j_exporter.py`, you can filter the export:

### Option A: Select Specific Papers

```python
from scripts.neo4j_exporter import Neo4jExporter

exporter = Neo4jExporter()
papers, terms, rels = exporter.filter_subgraph(
    paper_ids=["nchem_2447", "annurev-biophys-032116-094545"]
)
exporter.preview_export(papers, terms, rels)
```

### Option B: Select Ontology Categories

```python
papers, terms, rels = exporter.filter_subgraph(
    categories=["mechanisms", "proteins", "cofactors"]
)
exporter.preview_export(papers, terms, rels)
```

### Option C: Both

```python
papers, terms, rels = exporter.filter_subgraph(
    paper_ids=["nchem_2447"],
    categories=["mechanisms"]
)
```

### Option D: Complete Anthology (Current State)

All 47 papers + complete ontology (37 terms) exported.

---

## Database Management

### Check Current State

```bash
python scripts/neo4j_connection.py
```

### Clear the Database

```bash
python scripts/neo4j_exporter.py
# Choose option 4: Clear database
```

⚠️ **Warning**: This deletes all nodes and relationships. Cannot be undone.

### Backup the Graph

Neo4j Aura sandbox does not support direct backups, but you can:

1. **Export Cypher statements**:
   ```cypher
   CALL apoc.export.cypher.all("backup.cypher", {})
   ```
   (Requires APOC plugin)

2. **Recreate from knowledge base**:
   - The knowledge base is the source of truth
   - Re-run `neo4j_exporter.py` to rebuild graph

### Sandbox Expiry

Neo4j Aura sandboxes expire after inactivity. When this happens:

1. Create a new sandbox at https://neo4j.com/cloud/aura/
2. Update `neocreds.txt` with new credentials
3. Re-export: `python scripts/neo4j_exporter.py`

---

## Advanced Queries

### Find Research Gaps

```cypher
// Organisms studied in papers but not linked to mechanisms
MATCH (p:Paper)-[:STUDIES]->(o:Organism)
WHERE NOT (o)-[:EXHIBITS]->(:Mechanism)
RETURN o.name, COUNT(p) AS paper_count
ORDER BY paper_count DESC
```

### Technique Co-occurrence

```cypher
// Which techniques are used together in papers?
MATCH (p:Paper)-[:USES_TECHNIQUE]->(t1:Technique)
MATCH (p)-[:USES_TECHNIQUE]->(t2:Technique)
WHERE t1.name < t2.name
RETURN t1.name, t2.name, COUNT(p) AS co_occurrence
ORDER BY co_occurrence DESC
LIMIT 10
```

### Citation Network

```cypher
// Papers with most citations in knowledge base
MATCH (cited:Paper)<-[:CITES]-(citing:Paper)
RETURN cited.title, cited.year, COUNT(citing) AS citations
ORDER BY citations DESC
LIMIT 10
```

### Temporal Analysis

```cypher
// Research activity by year
MATCH (p:Paper)
WHERE p.year IS NOT NULL
RETURN p.year AS year, COUNT(p) AS papers
ORDER BY year
```

### Protein-Cofactor Networks

```cypher
// Proteins and their cofactors forming radical pairs
MATCH (protein:Protein)-[:CONTAINS]->(c1:Cofactor)
MATCH (c1)-[:FORMS_RADICAL_PAIR_WITH]->(c2:Cofactor)
RETURN protein.name, c1.name, c2.name, c1.wavelength
```

---

## Cypher Query Tips

### Pattern Matching
- `()` - Any node
- `(p:Paper)` - Node with label Paper
- `(p:Paper {year: 2016})` - Node with label and property
- `()-[r]->()` - Any relationship
- `()-[:CITES]->()` - Specific relationship type
- `()-[:CITES|STUDIES]->()` - Multiple relationship types

### Filtering
- `WHERE` - Filter results
- `WHERE p.year > 2015` - Property comparison
- `WHERE p.title CONTAINS "cryptochrome"` - String matching
- `WHERE p.title =~ ".*[Cc]ryptochrome.*"` - Regex matching

### Aggregation
- `COUNT()` - Count results
- `COLLECT()` - Aggregate into list
- `AVG()`, `MIN()`, `MAX()`, `SUM()` - Numeric aggregations

### Ordering and Limiting
- `ORDER BY p.year DESC` - Sort results
- `LIMIT 10` - Return top N results

### Path Queries
- `MATCH p = (a)-[*1..3]->(b)` - Paths of length 1-3
- `MATCH p = shortestPath((a)-[*]-(b))` - Shortest path

---

## Visualization

### Neo4j Browser

Access Neo4j Browser at sandbox URL (check Neo4j Aura console).

**Useful Browser Commands:**
```cypher
// Visualize ontology structure
MATCH (t:Term)-[r:IS_A|RELATED_TO]->(t2:Term)
RETURN t, r, t2
LIMIT 50

// Visualize paper network
MATCH (p:Paper)-[r:CITES|STUDIES|USES_TECHNIQUE]->(n)
RETURN p, r, n
LIMIT 100

// Visualize radical pair mechanism
MATCH (p:Protein)-[:CONTAINS]->(c1:Cofactor)-[:FORMS_RADICAL_PAIR_WITH]->(c2:Cofactor)
RETURN p, c1, c2
```

### Neo4j Bloom

Neo4j Bloom provides no-code graph exploration (Aura Professional only).

### Python Visualization

For local visualization:

```python
import networkx as nx
import matplotlib.pyplot as plt
from scripts.neo4j_connection import Neo4jConnection

conn = Neo4jConnection()
# Fetch data and create NetworkX graph
# Plot with matplotlib
```

---

## Troubleshooting

### Connection Fails

**Error**: `Failed to establish connection`

**Solutions**:
1. Check `neocreds.txt` has correct credentials
2. Verify sandbox is active (Neo4j Aura console)
3. Test with Neo4j Browser first
4. Check firewall/network settings

### Query Times Out

**Error**: `Query execution exceeded timeout`

**Solutions**:
1. Add `LIMIT` clause to reduce result set
2. Create indexes on queried properties
3. Simplify pattern matching
4. Use `PROFILE` to identify slow operations

### Duplicate Nodes Created

**Error**: Multiple nodes with same `paper_id`

**Solutions**:
1. Run constraint creation in `neo4j_schema.py`
2. Clear database and re-export
3. Use `MERGE` instead of `CREATE` in custom queries

### Missing Relationships

**Error**: Expected relationships not present

**Solutions**:
1. Check ontology files for relationship definitions
2. Re-export with full ontology
3. Verify paper metadata has required fields
4. Review `neo4j_exporter.py` relationship mapping logic

---

## Integration with Research Workflow

### Scenario: Finding Related Papers

You're reading `nchem_2447` (Kattnig et al. on chemical amplification).

**Query**: Find papers studying similar mechanisms

```cypher
MATCH (p1:Paper {paper_id: 'nchem_2447'})-[:DEFINES_TERM]->(t:Term)
MATCH (p2:Paper)-[:DEFINES_TERM]->(t)
WHERE p1 <> p2
RETURN DISTINCT p2.title, p2.year, COLLECT(t.name) AS shared_terms
```

### Scenario: Literature Review

You're writing a review on radical pair mechanisms.

**Query**: Get chronological overview

```cypher
MATCH (p:Paper)-[:DEFINES_TERM]->(t:Term {name: 'radical_pair_mechanism'})
RETURN p.year, p.title, p.authors, p.doi
ORDER BY p.year
```

### Scenario: Experimental Design

You want to know which techniques detect chemical amplification.

**Query**: Find applicable methods

```cypher
MATCH (tech:Technique)-[:DETECTS|MODELS]->(m:Mechanism)
WHERE m.name CONTAINS 'amplification'
RETURN tech.name, tech.description, tech.applications
```

---

## Python API Usage

### Basic Query

```python
from scripts.neo4j_connection import Neo4jConnection

conn = Neo4jConnection()

query = """
MATCH (p:Paper)-[:STUDIES]->(protein:Protein)
RETURN p.title, protein.name
LIMIT 10
"""

results = conn.execute_query(query)
for record in results:
    print(f"{record['p.title']} studies {record['protein.name']}")

conn.close()
```

### Parameterized Query

```python
query = """
MATCH (p:Paper)
WHERE p.year >= $min_year
RETURN p.title, p.year
ORDER BY p.year
"""

results = conn.execute_query(query, parameters={"min_year": 2015})
```

### Transaction Handling

```python
with Neo4jConnection() as conn:
    # Queries here run in a transaction
    results = conn.execute_query(query)
    # Automatic cleanup
```

---

## Future Enhancements

### Planned Features

1. **Automated Relationship Extraction**
   - Parse paper text to identify entity relationships
   - Use NLP to extract protein-technique associations

2. **Full-Text Search**
   - Index paper abstracts and full text
   - Enable semantic similarity queries

3. **Author Networks**
   - Create `Author` nodes
   - Map co-authorship relationships
   - Identify research clusters

4. **Impact Metrics**
   - Citation counts
   - PageRank scores
   - Temporal trends

5. **Integration with External Databases**
   - Link to PubMed, PDB, UniProt
   - Import external citation data
   - Sync with reference managers

### Contributing

To enhance the graph schema:

1. Edit `scripts/neo4j_schema.py` to add node/relationship types
2. Update `scripts/neo4j_exporter.py` to populate new entities
3. Modify `knowledge-base/ontology/*.json` to define new terms
4. Update this documentation

---

## References

- **Neo4j Cypher Manual**: https://neo4j.com/docs/cypher-manual/current/
- **Neo4j Python Driver**: https://neo4j.com/docs/python-manual/current/
- **Neo4j Aura Documentation**: https://neo4j.com/docs/aura/
- **Graph Data Science Library**: https://neo4j.com/docs/graph-data-science/current/

---

## Version History

- **v1.0** (2025-11-05): Initial Neo4j integration
  - 84 nodes (47 papers + 37 ontology terms)
  - 24 relationships
  - 8 node types, 14 relationship types
  - Query examples and export tools
