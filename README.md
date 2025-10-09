# Magnetosensitivity Research Knowledge Base

A FAIR-compliant research knowledge management system for studying magnetic field effects in biology, with a focus on the radical pair mechanism in proteins.

## Overview

This knowledge base organizes scientific literature, experimental protocols, and computational models related to magnetosensitivity research. It enables efficient literature review, experiment design, and computational simulation by providing:

- **Structured paper contexts** following FAIR principles (Findable, Accessible, Interoperable, Reusable)
- **Searchable indices** by topic, author, chronology, and methodology
- **Research context templates** for experimental and computational work
- **Integrated wet-lab/dry-lab workflows**
- **Domain-specific ontology** for consistent terminology

## Project Structure

```
magnetosensitivity-research/
│
├── Literature/                    # Original PDF files
│
├── knowledge-base/                # Organized knowledge system
│   ├── papers/                   # Individual paper directories
│   │   ├── {paper-id}/
│   │   │   ├── metadata.json     # FAIR-compliant metadata
│   │   │   ├── context.md        # Structured context file
│   │   │   ├── annotations.md    # User notes & highlights
│   │   │   ├── figures/          # Key figures
│   │   │   └── data/             # Extracted tables
│   │   └── TEMPLATE_*.{json,md}  # Templates for new entries
│   │
│   ├── index/                    # Global indices
│   │   ├── master-index.json     # All papers
│   │   ├── topic-map.json        # Topic organization
│   │   ├── author-network.json   # Author collaborations
│   │   └── chronology.json       # Timeline
│   │
│   └── ontology/                 # Domain terminology
│       ├── terms.json            # Controlled vocabulary
│       ├── abbreviations.json    # Common abbreviations
│       └── relationships.json    # Concept relationships
│
├── research-contexts/             # Reusable research templates
│   ├── experimental/             # Wet lab protocols
│   │   ├── protocols/
│   │   ├── equipment-specs/
│   │   └── sample-preparation/
│   │
│   ├── computational/            # Computational models
│   │   ├── models/               # Model implementations
│   │   ├── simulations/          # Simulation scripts
│   │   ├── analysis-pipelines/   # Data analysis
│   │   └── visualizations/       # Plotting templates
│   │
│   └── integrated/               # Combined approaches
│       ├── experiment-simulation-pairs/
│       └── validation-frameworks/
│
├── projects/                      # Active research projects
│   ├── current/
│   └── archive/
│
├── scripts/                       # Processing tools
│   ├── pdf_processor.py          # PDF extraction
│   ├── process_paper.py          # Paper processing pipeline
│   ├── process_all_papers.py     # Batch processing
│   └── requirements.txt          # Python dependencies
│
└── documentation/
    ├── README.md                 # This file
    ├── CONTRIBUTING.md           # Contribution guidelines
    ├── DATA-MANAGEMENT.md        # Data management plan
    └── GROBID-SETUP.md           # GROBID installation guide
```

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Optional: Install Docker for GROBID (large PDF processing)
# See documentation/GROBID-SETUP.md
```

### 2. Process Your First Paper

```bash
# Process a single paper
python scripts/process_paper.py Literature/your-paper.pdf

# Or process all papers at once
python scripts/process_all_papers.py
```

### 3. Explore the Knowledge Base

Papers are organized in `knowledge-base/papers/{paper-id}/`:
- `metadata.json` - Structured metadata
- `context.md` - FAIR-compliant context
- `annotations.md` - Your notes and highlights
- `full_text.txt` - Extracted text

Indices are in `knowledge-base/index/`:
- `master-index.json` - Search all papers
- `topic-map.json` - Browse by topic
- `author-network.json` - Find collaborations
- `chronology.json` - Timeline of discoveries

## Features

### FAIR Principles

All paper contexts follow FAIR data principles:

- **Findable**: Unique identifiers (DOIs), rich metadata, searchable indices
- **Accessible**: Standardized formats, clear file organization
- **Interoperable**: JSON-LD compatible, controlled vocabularies, linked references
- **Reusable**: Clear provenance, licensing info, detailed documentation

### Intelligent PDF Processing

- **Automatic method selection**: Choose best extraction method based on file size
- **GROBID integration**: Superior extraction for large books and complex PDFs
- **Python fallback**: Works without Docker using PyMuPDF/pdfplumber
- **Metadata extraction**: Authors, titles, DOIs, abstracts

### Research Context Templates

#### Experimental Protocols
Standardized templates for:
- Magnetic field exposure experiments
- Spectroscopy measurements
- Behavioral assays
- Cellular assays

#### Computational Models
Templates for:
- Radical pair spin dynamics
- Quantum mechanics simulations
- Kinetic modeling
- Data analysis pipelines

#### Integrated Studies
Frameworks combining wet-lab and computational approaches with iterative feedback loops.

### Domain Ontology

Controlled vocabulary covering:
- Radical pair mechanisms
- Proteins (cryptochrome, flavoproteins)
- Magnetic field types and parameters
- Experimental techniques
- Computational methods

## Usage Examples

### Search for Papers on a Topic

```python
import json

# Load topic map
with open('knowledge-base/index/topic-map.json') as f:
    topics = json.load(f)

# Find papers on cryptochrome
crypto_papers = topics['topics']['radical_pair_mechanism']['subtopics']['cryptochrome']
print(f"Found {len(crypto_papers)} papers on cryptochrome")
```

### Create a New Experimental Protocol

```bash
# Copy template
cp research-contexts/experimental/protocols/TEMPLATE_protocol.md \
   research-contexts/experimental/protocols/my-assay.md

# Edit with your protocol details
# The template guides you through all necessary sections
```

### Run a Computational Model

```bash
# Navigate to model directory
cd research-contexts/computational/models/radical-pair-dynamics/

# Run simulation
python run_simulation.py --field 50e-6 --time 1e-5

# Analyze results
python analyze_results.py results/simulation_001.h5
```

## Research Workflow

### Literature Review Workflow

1. **Add papers** to `Literature/` folder
2. **Process papers** with `process_paper.py`
3. **Review context files** and add annotations
4. **Search and synthesize** using indices

### Experimental Design Workflow

1. **Search literature** for relevant protocols
2. **Copy protocol template** to your project
3. **Customize** based on literature and equipment
4. **Link to relevant papers** in knowledge base
5. **Document results** back in the system

### Computational Workflow

1. **Extract parameters** from literature
2. **Implement model** using templates
3. **Validate** against published results
4. **Generate predictions** for experiments
5. **Compare** with experimental data

### Integrated Workflow

1. **Plan integrated study** using template
2. **Run initial experiments** and simulations
3. **Extract parameters** from data
4. **Refine model** with experimental constraints
5. **Generate and test** new predictions
6. **Iterate** until convergence

## Maintenance

### Adding New Papers

Papers are automatically processed, but you should:
1. Review extracted metadata for accuracy
2. Add missing DOIs manually
3. Fill in publication details
4. Add your annotations and highlights
5. Tag with relevant ontology terms

### Updating Indices

Indices are automatically updated during paper processing, but you can rebuild them:

```bash
python scripts/rebuild_indices.py
```

### Curating the Ontology

As you work, you'll discover new terms and relationships:
1. Add to `knowledge-base/ontology/terms.json`
2. Define clearly with sources
3. Link relationships in `relationships.json`
4. Document abbreviations

## Requirements

### Python Dependencies
- pymupdf >= 1.23.0 (PDF extraction)
- pdfplumber >= 0.10.0 (table extraction)
- pypdf >= 3.17.0 (metadata)
- requests >= 2.31.0 (GROBID API)

### Optional
- Docker (for GROBID - recommended for large PDFs)
- spacy (for advanced NLP)

## Contributing

See [CONTRIBUTING.md](documentation/CONTRIBUTING.md) for guidelines on:
- Adding new papers
- Creating protocols and models
- Improving extraction scripts
- Extending the ontology

## Data Management

See [DATA-MANAGEMENT.md](documentation/DATA-MANAGEMENT.md) for:
- Backup strategies
- Version control
- Data sharing policies
- Long-term preservation

## References

### Key Papers in Knowledge Base
Check `knowledge-base/index/master-index.json` for the current catalog.

### Methodological References
- FAIR Principles: https://www.go-fair.org/fair-principles/
- GROBID: https://github.com/kermitt2/grobid
- Radical Pair Mechanism: [See papers in knowledge base]

## License

This knowledge base structure is released under MIT License.

**Note**: Individual papers retain their original copyrights. This system organizes metadata and annotations, not the papers themselves.

## Contact

For questions about this knowledge base system, please open an issue or contact the maintainers.

## Acknowledgments

- GROBID team for PDF processing tools
- FAIR data principles community
- Magnetobiology research community

---

**Status**: Active Development
**Last Updated**: 2025-10-09
**Version**: 1.0.0
