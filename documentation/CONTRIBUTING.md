# Contributing to the Magnetosensitivity Research Knowledge Base

Thank you for contributing to this research knowledge base! This document provides guidelines for adding content, improving tools, and maintaining quality.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Adding Papers](#adding-papers)
3. [Creating Protocols](#creating-protocols)
4. [Developing Models](#developing-models)
5. [Improving Scripts](#improving-scripts)
6. [Updating the Ontology](#updating-the-ontology)
7. [Code Standards](#code-standards)
8. [Review Process](#review-process)

## Getting Started

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. **Familiarize yourself** with the project structure (see README.md)

3. **Review existing examples**:
   - Look at processed papers in `knowledge-base/papers/`
   - Review templates in `research-contexts/`
   - Check ontology in `knowledge-base/ontology/`

## Adding Papers

### Process

1. **Add PDF to Literature folder**:
   ```bash
   cp /path/to/paper.pdf Literature/
   ```

2. **Process the paper**:
   ```bash
   python scripts/process_paper.py Literature/paper.pdf
   ```

3. **Review and enhance**:
   - Check `knowledge-base/papers/{paper-id}/metadata.json`
   - Verify title, authors, DOI
   - Add missing publication info
   - Fill in research_context fields

4. **Add your annotations**:
   - Edit `knowledge-base/papers/{paper-id}/annotations.md`
   - Highlight key findings
   - Note methodology details
   - Link to related papers

5. **Tag with ontology terms**:
   - Add standardized keywords
   - Use terms from `knowledge-base/ontology/terms.json`
   - Add new terms if needed (see [Updating the Ontology](#updating-the-ontology))

### Best Practices

- **DOI**: Always include DOI if available
- **Keywords**: Use controlled vocabulary from ontology
- **Cross-references**: Link related papers in knowledge base
- **Quality check**: Verify extracted text is readable
- **Figures**: Extract key figures to `figures/` subdirectory
- **Data**: Extract data tables to `data/` subdirectory

### Example: Adding a Cryptochrome Paper

```bash
# 1. Process paper
python scripts/process_paper.py Literature/nuovo-cry-paper.pdf \
    --doi "10.1234/journal.2024.56789"

# 2. Open metadata file
# knowledge-base/papers/nuovo-cry-paper/metadata.json

# 3. Add research context
{
  "research_context": {
    "species_studied": ["Drosophila melanogaster"],
    "proteins": ["cryptochrome (CRY)"],
    "magnetic_field_parameters": {
      "field_strength": "50 μT",
      "frequency": "static",
      "field_type": "geomagnetic"
    },
    "experimental_techniques": ["transient absorption spectroscopy", "EPR"],
    "computational_methods": ["spin dynamics simulation"],
    "key_findings": [
      "CRY shows magnetic field sensitivity in vivo",
      "Effect saturates above 100 μT"
    ]
  }
}

# 4. Update topic map
# Edit knowledge-base/index/topic-map.json to include this paper
```

## Creating Protocols

### New Experimental Protocol

1. **Copy template**:
   ```bash
   cp research-contexts/experimental/protocols/TEMPLATE_protocol.md \
      research-contexts/experimental/protocols/my-new-protocol.md
   ```

2. **Fill in all sections**:
   - Metadata
   - Materials & Equipment
   - Safety Considerations
   - Detailed Procedure
   - Data Analysis
   - Troubleshooting

3. **Link to literature**:
   - Reference papers in knowledge base
   - Cite original sources for methods
   - Note modifications from published protocols

4. **Test the protocol**:
   - Follow your written protocol in the lab
   - Document any issues
   - Update troubleshooting section

5. **Mark validation status**:
   - Draft: Not yet tested
   - Validated: Successfully used
   - Published: Included in publication

### Protocol Checklist

- [ ] All materials listed with suppliers and catalog numbers
- [ ] Safety considerations documented
- [ ] Step-by-step procedure with timings
- [ ] Quality control checkpoints defined
- [ ] Data analysis methods specified
- [ ] Troubleshooting guide included
- [ ] References to source papers
- [ ] Validated by successful use

## Developing Models

### New Computational Model

1. **Copy template**:
   ```bash
   cp research-contexts/computational/models/TEMPLATE_model.md \
      research-contexts/computational/models/my-model/README.md
   ```

2. **Create code structure**:
   ```bash
   cd research-contexts/computational/models/my-model/
   mkdir -p src scripts data results
   ```

3. **Implement model**:
   - Write clear, documented code
   - Follow naming conventions
   - Include docstrings
   - Add usage examples

4. **Validate model**:
   - Test against published results
   - Document validation in README
   - Include benchmark results
   - Perform sensitivity analysis

5. **Create example scripts**:
   - Basic usage example
   - Parameter scan example
   - Comparison with data example

### Model Checklist

- [ ] Mathematical description in README
- [ ] All parameters documented with sources
- [ ] Code is modular and reusable
- [ ] Validation against literature
- [ ] Example usage scripts
- [ ] Performance benchmarks
- [ ] Uncertainty quantification
- [ ] References to source papers

### Code Quality Standards

```python
"""
Module docstring explaining what this does.

References:
    - Paper 1 (DOI): What method/parameters
    - Paper 2 (DOI): Validation data
"""

def calculate_singlet_yield(
    B_field: float,
    g1: float = 2.0023,
    g2: float = 2.0040,
    J: float = 0.0,
    **kwargs
) -> float:
    """
    Calculate radical pair singlet yield.

    Args:
        B_field: Magnetic field strength in Tesla
        g1: g-factor for radical 1 (default from Paper 1)
        g2: g-factor for radical 2 (default from Paper 1)
        J: Exchange coupling in Tesla
        **kwargs: Additional parameters

    Returns:
        Singlet yield (fraction between 0 and 1)

    Example:
        >>> yield_value = calculate_singlet_yield(50e-6)  # 50 μT
        >>> print(f"Singlet yield: {yield_value:.3f}")
        Singlet yield: 0.532

    References:
        Method from Smith et al. (2020), DOI: 10.xxxx/yyyy
    """
    # Implementation with comments
    ...
```

## Improving Scripts

### Modifying Processing Scripts

1. **Test on example PDFs first**:
   ```bash
   python scripts/process_paper.py Literature/test-paper.pdf
   ```

2. **Handle edge cases**:
   - PDFs with no metadata
   - Multi-column layouts
   - Non-English characters
   - Scanned images (OCR needed)

3. **Add error handling**:
   ```python
   try:
       result = process_pdf(pdf_path)
   except PDFProcessingError as e:
       logger.error(f"Failed to process {pdf_path}: {e}")
       # Graceful fallback
   ```

4. **Update requirements.txt** if adding dependencies

5. **Document changes** in script docstring

### Script Checklist

- [ ] Works with various PDF types
- [ ] Graceful error handling
- [ ] Clear error messages
- [ ] Progress indicators for long operations
- [ ] Logging for debugging
- [ ] Command-line help text
- [ ] Updated documentation

## Updating the Ontology

The ontology ensures consistent terminology across the knowledge base.

### Adding a New Term

1. **Check if term already exists**:
   ```bash
   grep -i "your_term" knowledge-base/ontology/terms.json
   ```

2. **Add to appropriate category**:
   ```json
   {
     "your_term": {
       "definition": "Clear, concise definition",
       "synonyms": ["alternative name 1", "alt 2"],
       "related_terms": ["related_term_1"],
       "source": "Paper DOI or standard reference"
     }
   }
   ```

3. **Add abbreviation** if applicable:
   ```json
   {
     "YT": "Your Term"
   }
   ```

4. **Define relationships**:
   ```json
   {
     "subject": "your_term",
     "predicate": "is_a",
     "object": "parent_category"
   }
   ```

### Ontology Guidelines

- **Definitions**: Must be clear and sourced
- **Synonyms**: Include all common variations
- **Consistency**: Check existing terms before adding
- **References**: Cite authoritative sources
- **Hierarchy**: Place terms in appropriate categories

## Code Standards

### Python

- **Style**: Follow PEP 8
- **Docstrings**: Use Google or NumPy style
- **Type hints**: Use for function signatures
- **Testing**: Include unit tests for new functions
- **Comments**: Explain *why*, not *what*

### Documentation

- **Markdown**: Use standard Markdown syntax
- **Links**: Use relative paths for internal links
- **Citations**: Include DOIs where possible
- **Examples**: Provide concrete, runnable examples
- **Formatting**: Use code blocks, tables, lists appropriately

### Version Control

- **Commits**: Clear, descriptive commit messages
- **Branches**: Use feature branches for development
- **Pull requests**: Include description of changes
- **Reviews**: Address reviewer comments promptly

## Review Process

### Self-Review Checklist

Before submitting contributions:

- [ ] Code runs without errors
- [ ] Documentation is clear and complete
- [ ] Examples work as described
- [ ] Cross-references are correct
- [ ] Ontology terms are used consistently
- [ ] No sensitive or proprietary information included
- [ ] Attribution to original sources
- [ ] Files are in correct locations

### Peer Review

For significant contributions:

1. **Submit description** of changes
2. **Explain rationale** for approach
3. **Highlight key changes**
4. **Request specific feedback** if needed

### Quality Standards

Contributions should:

- **Accuracy**: Verified against sources
- **Completeness**: All required sections filled
- **Consistency**: Follow existing patterns
- **Clarity**: Understandable by others
- **Reproducibility**: Others can replicate your work

## Getting Help

If you're unsure about:

- **Which category** to use for a paper → Check topic-map.json
- **How to structure** a protocol → See existing examples
- **Code standards** → Ask for review of a small example
- **Ontology terms** → Search existing terms first

## Recognition

Contributors are recognized in:

- Specific files they create (author field)
- Project-level CONTRIBUTORS.md
- Paper acknowledgments (when published)

Thank you for helping build this research resource!

---

**Questions?** Open an issue or contact the maintainers.

**Last Updated**: 2025-10-09
