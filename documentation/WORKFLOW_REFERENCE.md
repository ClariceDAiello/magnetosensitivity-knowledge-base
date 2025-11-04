# Workflow Reference: Detailed Task Guides

This document contains step-by-step procedures, troubleshooting guides, and integration scenarios for working with the magnetosensitivity research knowledge base.

---

## Common Tasks

### Task 1: Add a New Paper

```bash
# 1. Place PDF in Literature/ folder
cp ~/Downloads/new-paper.pdf Literature/

# 2. Process the paper
python scripts/process_paper.py "Literature/new-paper.pdf"

# 3. Review and edit metadata
# Edit: knowledge-base/papers/[paper_id]/metadata.json
# Edit: knowledge-base/papers/[paper_id]/context.md

# 4. Extract ontology terms
# Read the paper, identify new terms/abbreviations/relationships
# Add to knowledge-base/ontology/*.json with source citations

# 5. Commit to git
git add knowledge-base/papers/[paper_id]/
git add knowledge-base/index/master-index.json
git commit -m "Add paper: [Title]"
```

### Task 2: Enhance Ontology from Paper

**Example: Adding a new term from a paper**

Edit `knowledge-base/ontology/terms.json`:
```json
{
  "categories": {
    "mechanisms": {
      "new_mechanism_name": {
        "definition": "Clear, concise definition",
        "synonyms": ["synonym1", "synonym2"],
        "related_terms": ["term1", "term2"],
        "source": "10.XXXX/PAPER.DOI"
      }
    }
  }
}
```

**Important Rules**:
- Always cite source with DOI or paper_id
- Use lowercase_with_underscores for term IDs
- Include definition, synonyms, related_terms
- Update version number and last_updated timestamp

### Task 3: Create Experimental Protocol

```bash
# 1. Copy template
cp research-contexts/experimental/protocols/TEMPLATE_protocol.md \
   research-contexts/experimental/protocols/my_protocol.md

# 2. Fill in sections:
# - Objective
# - Materials and reagents
# - Equipment
# - Safety considerations
# - Magnetic field configuration
# - Detailed procedure
# - Data analysis
# - Expected results
# - Troubleshooting

# 3. Link to relevant papers
# Reference: knowledge-base/papers/[paper_id]/

# 4. Commit
git add research-contexts/experimental/protocols/my_protocol.md
git commit -m "Add protocol: [Protocol name]"
```

### Task 4: Create Computational Model

```bash
# 1. Copy template
cp research-contexts/computational/models/TEMPLATE_model.md \
   research-contexts/computational/models/my_model.md

# 2. Fill in sections:
# - Model overview
# - Spin Hamiltonian
# - Parameters
# - Implementation
# - Validation
# - Usage examples
# - References

# 3. Include code if applicable
# - Python scripts for simulation
# - Jupyter notebooks for analysis

# 4. Commit
git add research-contexts/computational/models/my_model.md
git commit -m "Add model: [Model name]"
```

### Task 5: Answer Technical Questions

**When Clarice asks about a concept from a paper:**

1. **Locate the paper**:
   ```bash
   # Check master index
   cat knowledge-base/index/master-index.json | grep -i "keyword"

   # Find paper_id, then read
   cat knowledge-base/papers/[paper_id]/full_text.txt
   ```

2. **Search ontology**:
   ```bash
   # Search for relevant terms
   cat knowledge-base/ontology/terms.json | grep -i "concept"
   cat knowledge-base/ontology/relationships.json | grep -i "concept"
   ```

3. **Provide detailed explanation**:
   - Define the concept using ontology terminology
   - Explain the physical mechanism
   - Cite specific sections from the paper
   - Use mathematical relationships when relevant
   - Reference line numbers: `knowledge-base/papers/[paper_id]/full_text.txt:line_number`

**Example**: When asked about χₚ, χₐ, kF, kD relationship:
- Locate paper: `knowledge-base/papers/nchem_2447/full_text.txt`
- Find relevant sections on chemical amplification
- Explain: E = χₐ/χₚ ≈ √(kD/kF)
- Validate with experimental data from paper

---

## PDF Processing Details

### Processing Pipeline

The `pdf_processor.py` uses intelligent fallback:

1. **GROBID** (if available, for PDFs > 5 MB):
   - Most accurate for academic papers
   - Structured XML output
   - Requires Docker setup (see `documentation/GROBID-SETUP.md`)

2. **PyMuPDF** (primary Python fallback):
   - Fast and reliable
   - Good metadata extraction
   - Handles most PDFs well

3. **pdfplumber** (secondary fallback):
   - Better for complex layouts
   - More robust text extraction

### Known Limitations

- **Automated title extraction** often returns "--- Page 1 ---" for complex PDFs
  - **Solution**: Manually edit `metadata.json` after processing

- **Author parsing** may be imperfect
  - **Solution**: Review and correct `authors` field in metadata

- **Figure extraction** captures images but doesn't identify captions
  - **Solution**: Add figure descriptions in `annotations.md`

### Processing Large Books

For books like `BIOELECTROMAGNETISM.pdf` (14+ MB):
- Processing takes 30-60 seconds
- Full text extraction may be incomplete
- Consider using GROBID for better results
- Extract specific chapters if needed

---

## Troubleshooting

### Issue: PDF processing fails

**Symptoms**: Script exits with error, no paper directory created

**Solutions**:
1. Check PDF is not corrupted: `pdfinfo Literature/paper.pdf`
2. Try manual processing with different backend:
   ```python
   from scripts.pdf_processor import PDFProcessor
   processor = PDFProcessor()
   result = processor.process_pdf("Literature/paper.pdf", prefer_grobid=False)
   ```
3. Install GROBID for large PDFs (see `documentation/GROBID-SETUP.md`)

### Issue: Metadata extraction incomplete

**Symptoms**: Title is "--- Page 1 ---", authors are malformed

**Solution**: Manually edit `knowledge-base/papers/[paper_id]/metadata.json`:
```json
{
  "title": "Correct title from PDF",
  "authors": ["Author 1", "Author 2"],
  "publication": {
    "journal": "Journal Name",
    "year": 2024
  }
}
```

### Issue: Git repository too large

**Symptoms**: Slow git operations, large .git folder

**Solutions**:
1. Use Git LFS for large PDFs:
   ```bash
   git lfs install
   git lfs track "Literature/*.pdf"
   git add .gitattributes
   ```
2. Exclude processed text files if needed (edit `.gitignore`)

### Issue: Ontology version conflicts

**Symptoms**: Multiple edits to ontology files, unclear which is latest

**Solution**:
- Always update `"last_updated"` timestamp in ISO 8601 format
- Increment `"version"` using semantic versioning (major.minor.patch)
- Review git log: `git log knowledge-base/ontology/`

---

## Integration with Research Workflow

### Scenario 1: Starting a New Experimental Project

1. **Literature review**:
   ```bash
   # Search existing papers
   grep -r "cryptochrome CRY4" knowledge-base/papers/*/full_text.txt
   ```

2. **Review relevant protocols**:
   ```bash
   ls research-contexts/experimental/protocols/
   ```

3. **Create project directory**:
   ```bash
   mkdir -p projects/current/cry4-magnetosensitivity
   cp research-contexts/integrated/experiment-simulation-pairs/TEMPLATE_integrated_study.md \
      projects/current/cry4-magnetosensitivity/plan.md
   ```

4. **Link to knowledge base**:
   - Reference papers: `[nchem_2447]`
   - Use ontology terms consistently
   - Document parameters in standard units

### Scenario 2: Computational Model Development

1. **Review existing models**:
   ```bash
   ls research-contexts/computational/models/
   ```

2. **Extract parameters from papers**:
   ```bash
   # Find hyperfine coupling values
   grep -r "hyperfine" knowledge-base/papers/*/full_text.txt

   # Check ontology
   cat knowledge-base/ontology/terms.json | grep -A5 "hyperfine_coupling"
   ```

3. **Create model**:
   - Copy template
   - Define Hamiltonian
   - Specify parameters with sources
   - Validate against experimental data

4. **Document results**:
   - Save simulation outputs in `projects/current/[project]/data/`
   - Create figures in `projects/current/[project]/figures/`
   - Write summary in project README

### Scenario 3: Writing a Paper/Thesis

1. **Generate bibliography**:
   ```bash
   # Extract all DOIs
   cat knowledge-base/index/master-index.json | grep "doi"
   ```

2. **Cite protocols/models**:
   - Reference specific files in `research-contexts/`
   - Include git commit hash for reproducibility

3. **Use ontology for consistency**:
   - Use standard abbreviations from `abbreviations.json`
   - Define terms on first use from `terms.json`

---

## Advanced Features

### Topic Map Generation

Future capability: Cluster papers by topics
- Use keywords and abstracts
- Build citation network
- Identify research gaps

### Author Network Analysis

Future capability: Co-authorship visualization
- Extract from `metadata.json` author fields
- Build network graph
- Identify key research groups

### Automated Literature Updates

Future capability: Monitor new papers
- RSS feeds from journals
- arXiv API queries
- Automatic processing pipeline

---

## Questions to Ask Clarice

When helping with research tasks, useful questions:

1. **For new papers**:
   - "What is the main focus of this paper for your research?"
   - "Are there specific terms or concepts you'd like me to add to the ontology?"

2. **For experiments**:
   - "What magnetic field parameters are you using?"
   - "Which cryptochrome variant are you studying?"
   - "What is your expected magnetic field effect magnitude?"

3. **For models**:
   - "What spin Hamiltonian are you using?"
   - "What are the relevant hyperfine coupling constants?"
   - "Are you modeling steady-state or time-resolved behavior?"

4. **For integration**:
   - "How can I help link this to existing papers or protocols?"
   - "Should I create a new project directory for this work?"
