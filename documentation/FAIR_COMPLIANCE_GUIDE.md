# FAIR Compliance Guide

## Overview

This knowledge base implements **FAIR principles** (Findable, Accessible, Interoperable, Reusable) to ensure research data quality and scientific reproducibility.

**Current Status:**
- 47 papers processed
- Average FAIR score: 39.9/100
- Automated compliance validation
- Processing status tracking

**Note**: Low initial scores are expected due to automated PDF extraction limitations. Manual metadata curation improves scores significantly.

---

## What are FAIR Principles?

FAIR stands for:
- **F**indable: Data is easy to locate with metadata and identifiers
- **A**ccessible: Data is retrievable with clear access protocols
- **I**nteroperable: Data uses standard formats and vocabularies
- **R**eusable: Data is well-documented with usage licenses

**Why FAIR Matters:**
- Enables reproducible research
- Facilitates data sharing and collaboration
- Improves citation and impact
- Meets funding agency requirements (NSF, NIH, EU)
- Supports long-term preservation

**Reference**: Wilkinson et al., *The FAIR Guiding Principles for scientific data management and stewardship*, Scientific Data 3, 160018 (2016). DOI: 10.1038/sdata.2016.18

---

## FAIR Scoring System

Each paper is scored 0-100 across four dimensions (25 points each).

### Findable (F) - 25 points

**Criteria:**
1. ✓ **DOI or identifier** (10 pts) - Persistent unique identifier present
2. ✓ **Indexed** (5 pts) - Entry in `master-index.json`
3. ✓ **Complete metadata** (5 pts) - Title, authors, publication info filled
4. ✓ **Keywords present** (5 pts) - Standardized search terms assigned

**How to Improve:**
- Add DOI to `metadata.json`: `"doi": "10.1038/EXAMPLE"`
- Manually correct title from "--- Page 1 ---"
- Extract keywords from abstract
- Ensure indexed in `knowledge-base/index/master-index.json`

### Accessible (A) - 25 points

**Criteria:**
1. ✓ **Files exist** (10 pts) - All required files present
2. ✓ **Valid JSON metadata** (5 pts) - `metadata.json` well-formed
3. ✓ **Adequate text extraction** (5 pts) - `full_text.txt` ≥ 1000 chars
4. ✓ **Context documented** (5 pts) - `context.md` edited

**How to Improve:**
- Verify all files: `metadata.json`, `full_text.txt`, `context.md`, `annotations.md`
- Check JSON syntax: `python -m json.tool metadata.json`
- Re-process poor quality PDFs with GROBID
- Fill in context.md with research notes

### Interoperable (I) - 25 points

**Criteria:**
1. ✓ **Ontology links** (10 pts) - Paper uses terms from `ontology/*.json`
2. ✓ **Standard notations** (10 pts) - Units, abbreviations follow conventions
3. ✓ **Related papers** (5 pts) - Cross-references to other papers

**How to Improve:**
- Tag paper with ontology terms in `context.md`
- Link related papers in `interoperability.related_papers`
- Use standard abbreviations from `abbreviations.json`
- Document methods with standardized names

### Reusable (R) - 25 points

**Criteria:**
1. ✓ **Annotations** (10 pts) - `annotations.md` contains notes
2. ✓ **Research context** (10 pts) - Key findings, methods documented
3. ✓ **License/access info** (5 pts) - Copyright status clear

**How to Improve:**
- Fill out `annotations.md` template sections
- Complete `context.md` research context
- Specify license in `metadata.json`: `"access.license": "CC-BY-4.0"`
- Add reproducibility notes for experiments

---

## Validation Tools

### Check Single Paper

```bash
python scripts/fair_compliance.py --paper-id "nchem_2447"
```

**Output:**
```
═══════════════════════════════════════════════════════════
FAIR COMPLIANCE REPORT: nchem_2447
═══════════════════════════════════════════════════════════

Overall Score: 63.0 / 100

Detailed Scores:
  Findable (F):        15.0 / 25
  Accessible (A):      20.0 / 25
  Interoperable (I):   15.0 / 25
  Reusable (R):        13.0 / 25

Issues Found:
  ⚠ Title missing or not extracted properly
  ⚠ Keywords list is empty
  ⚠ Context file needs editing
```

### Check All Papers

```bash
python scripts/fair_compliance.py --all
```

### Check Processing Status

```bash
python scripts/processing_status.py --report
```

**Output:**
```
Processing Status Report
========================

Total PDFs: 47
Processed: 47 (100.0%)
Pending: 0 (0.0%)

FAIR Compliance:
  Average Score: 39.9
  Excellent (≥80): 0 papers
  Good (60-79): 5 papers
  Fair (40-59): 12 papers
  Needs Work (<40): 30 papers

Common Issues:
  - Title missing or not extracted properly: 38 papers
  - Keywords list is empty: 42 papers
  - Context file needs editing: 47 papers
```

---

## Manual Curation Workflow

### Step 1: Identify Low-Scoring Papers

```bash
python scripts/fair_compliance.py --all | grep "Score:" | sort -t: -k2 -n
```

### Step 2: Edit Metadata

Open `knowledge-base/papers/[paper_id]/metadata.json`

**Before:**
```json
{
  "title": "--- Page 1 ---",
  "authors": ["sametime", "physically"],
  "publication": {
    "journal": "",
    "year": null
  },
  "doi": "",
  "keywords": []
}
```

**After:**
```json
{
  "title": "Chemical amplification of magnetic field effects",
  "authors": ["Daniel R. Kattnig", "Christiane R. Timmel"],
  "publication": {
    "journal": "Nature Chemistry",
    "year": 2016,
    "volume": "8",
    "pages": "384-387"
  },
  "doi": "10.1038/nchem.2447",
  "keywords": [
    "radical pair mechanism",
    "chemical amplification",
    "magnetosensitivity",
    "cryptochrome",
    "spin chemistry"
  ]
}
```

**Sources for Information:**
- Read first few lines of `full_text.txt`
- Check DOI database: https://doi.org/
- Search CrossRef API: https://api.crossref.org/works/[DOI]
- Original PDF file

### Step 3: Fill Context Template

Open `knowledge-base/papers/[paper_id]/context.md`

**Fill these sections:**

#### Core Findings
```markdown
### Core Findings
- Chemical amplification factor E ≈ √(kD/kF) derived theoretically
- Experimental validation in FMN/lysozyme model system
- Delayed magnetic field effects observed over 100 ms timescale
- Amplification explains weak field sensitivity in biological systems
```

#### Radical Pair Mechanisms
```markdown
### Radical Pair Mechanisms
- **Species Studied**: FMN (flavin mononucleotide), lysozyme
- **Magnetic Field Parameters**: 0-50 mT static field
- **Proposed Mechanisms**: Differential radical termination rates drive amplification
```

#### Experimental Methods
```markdown
### Experimental Methods
- **Techniques**: Fluorescence spectroscopy, transient absorption spectroscopy
- **Key Equipment**: Xenon flash lamp, photomultiplier tube, electromagnet
- **Sample Preparation**: Anaerobic conditions, pH 7.0 phosphate buffer
```

#### Computational Approaches
```markdown
### Computational Approaches
- **Models Used**: Stochastic Liouville equation, rate equation analysis
- **Parameters**: kF = 10^6 s^-1, kD = 10^7 s^-1, HFC constants
```

### Step 4: Add Annotations

Open `knowledge-base/papers/[paper_id]/annotations.md`

**Example:**
```markdown
## Critical Findings

1. Chemical Amplification Theory
   - **Significance**: Explains how weak geomagnetic fields (~50 µT) produce measurable biological effects despite small prompt effect
   - **Page/Section**: Equation 2, Figure 2
   - **Related Work**: Extends radical pair mechanism to include kinetic amplification

2. Experimental Validation
   - **Significance**: First direct measurement of delayed magnetic field effect
   - **Page/Section**: Figure 3, fluorescence decay curves
   - **Related Work**: Confirms predictions from Timmel group's earlier theoretical work

## Methodology Highlights

- **Strengths**: Clean model system (FMN/lysozyme), well-controlled magnetic field
- **Weaknesses**: Not directly applicable to cryptochrome (different kF/kD ratio)
- **Reproducibility**: Detailed experimental conditions provided

## Integration Notes

### How This Relates to Our Work
- Key paper for understanding magnetosensitivity amplification
- E factor calculation applicable to cryptochrome radical pairs
- Suggests slow spin-selective recombination is critical for avian compass

### Questions & Uncertainties
1. What is kD/kF ratio for CRY4 Trp triad?
2. Can amplification be enhanced by protein engineering?

### Ideas for Future Work
- Measure E factor in intact cryptochrome
- Test whether CRY4 shows delayed MFE
- Model E factor for different Trp positions
```

### Step 5: Update Ontology

Add new terms to `knowledge-base/ontology/terms.json`:

```json
{
  "categories": {
    "mechanisms": {
      "chemical_amplification": {
        "definition": "Enhancement of magnetic field effects through differential radical termination rates",
        "synonyms": ["kinetic amplification", "delayed MFE"],
        "related_terms": ["radical_pair_mechanism", "spin_selective_recombination"],
        "source": "10.1038/nchem.2447"
      }
    }
  }
}
```

Add abbreviations to `abbreviations.json`:

```json
{
  "kF": {
    "full_form": "Flavin radical termination rate constant",
    "context": "Chemical kinetics",
    "source": "10.1038/nchem.2447"
  },
  "kD": {
    "full_form": "Donor radical termination rate constant",
    "context": "Chemical kinetics",
    "source": "10.1038/nchem.2447"
  }
}
```

### Step 6: Re-validate

```bash
python scripts/fair_compliance.py --paper-id "nchem_2447"
```

**Expected improvement**: Score should increase from ~40 to 70-85.

### Step 7: Commit Changes

```bash
git add knowledge-base/papers/nchem_2447/
git add knowledge-base/ontology/
git commit -m "Curate metadata for nchem_2447: Chemical amplification paper

- Correct title, authors, publication details
- Add 5 keywords
- Complete research context with findings and methods
- Add detailed annotations with significance notes
- Extract 8 new ontology terms (chemical_amplification, kF, kD, etc.)
- FAIR score improved: 39 → 78

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Batch Curation Strategy

For 47 papers, prioritize curation effort:

### Priority 1: Core Papers (High Impact)
**Papers to curate first** (5-10 papers):
- Most cited in knowledge base
- Define key mechanisms (radical pair, chemical amplification)
- Experimental protocols you will replicate
- Computational models you will implement

**Time investment**: 30-60 min per paper

### Priority 2: Directly Relevant Papers (15-20 papers)
- Specific to your current project
- Cryptochrome studies
- Magnetic field effect measurements

**Time investment**: 15-30 min per paper

### Priority 3: Background/Reference (Remaining papers)
- Textbooks, reviews
- Technique manuals
- Historical background

**Time investment**: 5-10 min per paper (minimal curation)

### Automated Assistance

Use Claude Code to help:
```
"Read knowledge-base/papers/nchem_2447/full_text.txt and extract:
1. Correct title and authors
2. Publication year and journal
3. 5 key terms for keywords
4. Main findings for context.md"
```

---

## Common Issues and Fixes

### Issue 1: "--- Page 1 ---" Title

**Cause**: PyMuPDF/pdfplumber cannot extract title from PDF metadata

**Fix**:
1. Read first page of `full_text.txt`
2. Identify actual title (usually first bold text)
3. Update `metadata.json`

**Automation**:
```python
# Extract title from full_text.txt
with open("full_text.txt") as f:
    lines = f.readlines()
    # Title is usually in first 20 lines, all caps or bold
    for line in lines[:20]:
        if len(line) > 20 and line.isupper():
            title = line.strip()
            break
```

### Issue 2: Malformed Authors

**Cause**: PDF text extraction picks up random fragments

**Example**: `"authors": ["sametime", "physically"]`

**Fix**:
1. Search for author names in `full_text.txt`
2. Look for patterns: "Author1 and Author2" or "Author1, Author2"
3. Manually correct in `metadata.json`

### Issue 3: Missing DOI

**Cause**: Not all PDFs have DOI embedded

**Fix**:
1. Search paper title on Google Scholar
2. Check journal website
3. Use CrossRef search: https://search.crossref.org/
4. If not available, use paper_id as identifier

### Issue 4: Empty Keywords

**Cause**: PDFs rarely include keyword metadata

**Fix**:
1. Read abstract in `full_text.txt`
2. Extract 5-10 key concepts
3. Match to ontology terms when possible
4. Add to `metadata.json`

### Issue 5: Minimal Full Text

**Cause**: Scanned PDFs or OCR failures

**Symptoms**: `full_text.txt` < 1000 characters

**Fix**:
1. Try GROBID processing (better OCR)
2. Check if PDF is image-based (needs OCR)
3. Consider alternative source (arXiv, journal site)
4. If unfixable, note in `context.md`: "Limited text extraction"

### Issue 6: Broken JSON

**Cause**: Comma errors, unclosed quotes in metadata

**Detection**:
```bash
python -m json.tool metadata.json
# If error, fix the line indicated
```

**Prevention**:
- Use JSON validator in editor (VS Code, Sublime)
- Run validation script after manual edits

---

## Quality Metrics

### Target FAIR Scores

| Paper Priority | Minimum FAIR Score | Target Components |
|----------------|-------------------|-------------------|
| Priority 1 (Core) | 80/100 | All fields complete, detailed annotations |
| Priority 2 (Relevant) | 60/100 | Metadata corrected, basic context |
| Priority 3 (Background) | 40/100 | Metadata corrected, indexed |

### Knowledge Base Quality Goals

**Short-term (1 month)**:
- All Priority 1 papers: FAIR ≥ 80
- All papers: FAIR ≥ 40 (metadata corrected)
- 100% indexed with correct titles

**Long-term (6 months)**:
- Average FAIR score: ≥ 65
- All papers: Annotations complete
- Ontology: 100+ terms, fully linked

### Continuous Improvement

**Monthly review**:
```bash
python scripts/fair_compliance.py --all > fair_report_$(date +%Y%m).txt
```

Compare scores month-over-month.

**Quarterly audit**:
- Spot-check 10 random papers
- Verify ontology links are accurate
- Update documentation
- Git tag: `v1.1-fair-audit-2025Q1`

---

## Metadata Standards

### Controlled Vocabularies

Use standardized terms from:
- `knowledge-base/ontology/terms.json`
- NCBI Taxonomy (organisms)
- UniProt (proteins)
- ChEBI (chemicals)
- Gene Ontology (biological processes)

### Date Formats

ISO 8601 standard:
```json
{
  "date_added": "2025-11-05T07:51:11.263338",
  "last_modified": "2025-11-05T14:32:05.112233"
}
```

### Units

Always specify units explicitly:
- Magnetic field: µT (microtesla), mT (millitesla), T (tesla)
- Wavelength: nm (nanometers)
- Time: ns, µs, ms, s
- Frequency: Hz, MHz, GHz
- Rate constants: s^-1, M^-1 s^-1

### DOI Format

Standard DOI format:
```json
{
  "doi": "10.1038/nchem.2447"
}
```

Not:
- `https://doi.org/10.1038/nchem.2447` (too long)
- `doi:10.1038/nchem.2447` (non-standard prefix)

---

## Compliance Checklist

Before considering a paper "complete":

### Metadata ✓
- [ ] Title is correct (not "--- Page 1 ---")
- [ ] All authors listed accurately
- [ ] Publication year present
- [ ] Journal/conference name included
- [ ] DOI or stable identifier present
- [ ] 5+ relevant keywords assigned

### Files ✓
- [ ] `metadata.json` valid JSON
- [ ] `full_text.txt` ≥ 1000 characters
- [ ] `context.md` research sections filled
- [ ] `annotations.md` has ≥ 2 critical findings

### Interoperability ✓
- [ ] Paper linked in `master-index.json`
- [ ] ≥ 3 ontology terms tagged
- [ ] Related papers cross-referenced
- [ ] Standard notations used in context

### Reusability ✓
- [ ] License/access level documented
- [ ] Key findings summarized
- [ ] Methods documented (if experimental)
- [ ] Parameters documented (if computational)

---

## FAIR and Open Science

### Data Sharing

FAIR principles support open science:
- **Share metadata openly** (always)
- **Share full text** (if license permits)
- **Share derived data** (annotations, ontology) under CC-BY
- **Respect copyright** (do not redistribute copyrighted PDFs)

### Citing the Knowledge Base

If you use this knowledge base in publications:

```
Magnetosensitivity Research Knowledge Base v1.0 (2025).
Repository: [GitHub URL]
DOI: [Zenodo DOI if archived]
```

### Archival

For long-term preservation:
1. Archive on Zenodo: https://zenodo.org/
2. Get DOI for knowledge base
3. Include in citations
4. Update README with archive link

---

## Compliance Reporting

### Generate Report for Funders

```bash
python scripts/fair_compliance.py --report > fair_compliance_report.txt
```

Include in grant progress reports to demonstrate data management compliance.

### NSF Data Management Plan

Address FAIR principles:
```
"All research papers are processed and indexed following FAIR principles
(Findable, Accessible, Interoperable, Reusable). Each paper receives a
unique identifier, standardized metadata, and is linked to a controlled
vocabulary ontology. Current FAIR compliance score: XX/100 across YY papers.
Data is version-controlled with Git and archived on Zenodo."
```

### NIH Data Sharing Plan

```
"Literature corpus is managed in a FAIR-compliant knowledge base with
persistent identifiers, structured metadata, and standard vocabularies.
All metadata and annotations are shared under CC-BY license. Access is
provided via Git repository and Neo4j graph database for query-based
retrieval."
```

---

## References

- **FAIR Principles**: Wilkinson et al., *Scientific Data* 3, 160018 (2016). https://doi.org/10.1038/sdata.2016.18
- **GO FAIR Initiative**: https://www.go-fair.org/
- **FAIR Cookbook**: https://faircookbook.elixir-europe.org/
- **RDA FAIR Data Maturity Model**: https://www.rd-alliance.org/

---

## Version History

- **v1.0** (2025-11-05): Initial FAIR compliance system
  - 47 papers processed, average score 39.9/100
  - Automated validation script
  - Manual curation workflow documented
  - Integration with processing pipeline
