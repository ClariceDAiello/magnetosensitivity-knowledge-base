# Data Management Plan

This document describes how data is managed, backed up, versioned, and shared within the Magnetosensitivity Research Knowledge Base.

## Table of Contents

1. [Data Organization](#data-organization)
2. [Version Control](#version-control)
3. [Backup Strategy](#backup-strategy)
4. [Data Sharing](#data-sharing)
5. [Long-term Preservation](#long-term-preservation)
6. [Privacy & Security](#privacy--security)
7. [Metadata Standards](#metadata-standards)

## Data Organization

### File Naming Conventions

#### Papers
- **Pattern**: `{first-author-last-name}_{year}_{short-title}`
- **Example**: `Hore_2016_cryptochrome-radical-pairs`
- **Notes**: Lowercase, hyphens for spaces, max 50 characters

#### Protocols
- **Pattern**: `{technique}_{system}_{variant}.md`
- **Example**: `transient-absorption_cryptochrome_low-temp.md`

#### Models
- **Pattern**: `{mechanism}_{system}_v{version}/`
- **Example**: `radical-pair-dynamics_cry_v1.0/`

#### Data Files
- **Pattern**: `{experiment-id}_{date}_{description}.{ext}`
- **Example**: `EXP001_2025-10-09_cry-magnetic-response.csv`

### Directory Structure Standards

Each paper directory must contain:

```
paper-id/
├── metadata.json          # Required: Structured metadata
├── context.md             # Required: FAIR-compliant context
├── annotations.md         # Required: User annotations
├── full_text.txt          # Optional: Extracted text
├── figures/               # Optional: Key figures
│   ├── figure1.png
│   └── figure2.png
└── data/                  # Optional: Extracted tables
    └── table1.csv
```

### Data Types

| Type | Format | Location | Size Limit | Backup Frequency |
|------|--------|----------|------------|------------------|
| Papers (PDF) | PDF | Literature/ | 100 MB | Daily |
| Metadata | JSON | knowledge-base/papers/ | 1 MB | Hourly |
| Context | Markdown | knowledge-base/papers/ | 1 MB | Hourly |
| Indices | JSON | knowledge-base/index/ | 10 MB | Hourly |
| Protocols | Markdown | research-contexts/experimental/ | 1 MB | Daily |
| Models | Python/Markdown | research-contexts/computational/ | 50 MB | Daily |
| Simulation Data | HDF5/CSV | projects/current/ | 1 GB | Weekly |

## Version Control

### Git Configuration

Initialize repository:

```bash
cd /Users/clarice/Desktop/Claude/Teste
git init
git add .
git commit -m "Initial commit: Knowledge base structure"
```

### .gitignore

Create `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# Large files (use Git LFS)
*.pdf
*.h5
*.hdf5
*.mat

# Temporary files
*.tmp
*.swp
*~
.DS_Store

# Build artifacts
build/
dist/
*.egg-info/

# Data outputs (too large for git)
projects/current/*/results/
research-contexts/computational/*/results/

# Personal notes (not for sharing)
PERSONAL_NOTES.md
```

### Git LFS for Large Files

For PDFs and data files >50 MB:

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pdf"
git lfs track "*.h5"
git lfs track "*.hdf5"

# Add .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS"
```

### Branching Strategy

- **main**: Stable, reviewed content
- **develop**: Integration branch for new content
- **feature/paper-name**: Adding new papers
- **feature/protocol-name**: New protocols/models
- **fix/issue-description**: Bug fixes

### Commit Message Format

```
<type>: <short summary>

<detailed description if needed>

<references to papers/issues>
```

Types:
- `paper`: Adding or updating papers
- `protocol`: Adding or updating protocols
- `model`: Adding or updating models
- `ontology`: Updating terminology
- `docs`: Documentation changes
- `fix`: Bug fixes
- `refactor`: Code improvements

Example:
```
paper: Add Hore 2016 cryptochrome review

Added comprehensive review paper on cryptochrome magnetosensitivity.
Includes 50+ references to other papers in our knowledge base.

Related to project: CRY-analysis-2025
```

## Backup Strategy

### Local Backups

#### Automated Time Machine (macOS)

```bash
# Ensure Time Machine is enabled
tmutil status

# Exclude large temporary files
tmutil addexclusion projects/current/*/results/large_data.h5
```

#### Manual Backups

```bash
#!/bin/bash
# backup.sh - Create timestamped backup

BACKUP_DIR="/Volumes/ExternalDrive/Backups"
DATE=$(date +%Y-%m-%d)
SOURCE="/Users/clarice/Desktop/Claude/Teste"

# Create backup
tar -czf "$BACKUP_DIR/knowledge-base-$DATE.tar.gz" \
    --exclude="*.h5" \
    --exclude="*/results/" \
    "$SOURCE"

echo "Backup created: knowledge-base-$DATE.tar.gz"
```

Run weekly:
```bash
crontab -e
# Add: 0 2 * * 0 /Users/clarice/scripts/backup.sh
```

### Cloud Backups

#### Option 1: GitHub/GitLab (Recommended)

```bash
# Add remote
git remote add origin https://github.com/username/magnetosensitivity-kb.git

# Push regularly
git push origin main

# For private repositories, use SSH key
```

**Advantages**:
- Version control included
- Easy collaboration
- Free for public repos, affordable for private

**Limitations**:
- File size limits (100 MB without LFS)
- Large PDFs need Git LFS

#### Option 2: Cloud Storage (Dropbox/Google Drive)

- Sync `Literature/` and `knowledge-base/` folders
- Keep `projects/current/` local or selective sync
- Use .dropboxignore or similar to exclude large results

#### Option 3: Research Data Repository

For published/citable data:
- **Zenodo**: Free, issues DOIs, unlimited storage for research
- **OSF**: Free, integrates with many tools
- **Institutional repository**: Check your institution's offerings

### Backup Schedule

| Data Type | Frequency | Method | Retention |
|-----------|-----------|--------|-----------|
| Metadata/Context | Hourly | Git auto-commit | Forever |
| PDFs | Daily | Cloud sync | Forever |
| Indices | Hourly | Git auto-commit | Forever |
| Protocols/Models | Daily | Git push | Forever |
| Simulation results | Weekly | Local backup | 1 year |
| Analysis scripts | Daily | Git push | Forever |

### Disaster Recovery

**Scenario 1: Accidental file deletion**

```bash
# Restore from git
git checkout HEAD -- knowledge-base/papers/paper-id/

# Or from Time Machine
tmutil restore /path/to/file
```

**Scenario 2: Corrupted database/index**

```bash
# Rebuild indices from paper metadata
python scripts/rebuild_indices.py
```

**Scenario 3: Complete system loss**

1. Restore from cloud repository (GitHub)
2. Sync PDFs from cloud storage (Dropbox/Drive)
3. Rebuild what can be rebuilt from scripts
4. Restore simulation data from weekly backups if needed

## Data Sharing

### Public vs. Private Data

#### Public (can be shared)
- Paper metadata (if paper is published/open access)
- Context files and annotations
- Protocols (your own work)
- Code and models
- Ontology and indices
- Analysis scripts

#### Private (should not be shared)
- PDFs of paywalled papers (copyright)
- Unpublished experimental data
- Proprietary protocols
- Personal notes marked confidential

### Sharing Protocols

#### Sharing a Protocol

```bash
# Export protocol with references
cd research-contexts/experimental/protocols/
zip my-protocol-package.zip my-protocol.md ../../../knowledge-base/index/master-index.json

# Or create public GitHub gist
gh gist create my-protocol.md --public
```

#### Sharing a Model

```bash
# Package model with documentation
cd research-contexts/computational/models/
tar -czf radical-pair-model-v1.0.tar.gz radical-pair-dynamics/

# Upload to Zenodo or GitHub release
gh release create v1.0.0 radical-pair-model-v1.0.tar.gz
```

### Collaboration

#### For Lab Members

1. **Clone repository**:
   ```bash
   git clone https://github.com/yourlab/magnetosensitivity-kb.git
   ```

2. **Install dependencies**:
   ```bash
   pip install -r scripts/requirements.txt
   ```

3. **Work on feature branch**:
   ```bash
   git checkout -b feature/my-contribution
   # Make changes
   git commit -am "Add new protocol"
   git push origin feature/my-contribution
   ```

4. **Create pull request** for review

#### For External Collaborators

- Share specific protocols or models as standalone packages
- Provide metadata exports (JSON) without full-text PDFs
- Use Zenodo DOIs for citable sharing

## Long-term Preservation

### File Formats for Longevity

| Data Type | Preferred Format | Alternative | Avoid |
|-----------|------------------|-------------|-------|
| Documents | Markdown, PDF/A | LaTeX | .docx |
| Metadata | JSON-LD, JSON | YAML | .xlsx |
| Data tables | CSV, HDF5 | TSV | .xlsx |
| Code | Python, Julia | R, MATLAB | Compiled only |
| Figures | SVG, PNG | PDF | .psd |
| Simulation | HDF5, NetCDF | CSV | Binary |

### Future-Proofing

1. **Use open standards**: JSON, CSV, Markdown
2. **Document thoroughly**: Future you needs to understand
3. **Include versions**: Tool versions, file format versions
4. **Plain text when possible**: Always readable
5. **Avoid proprietary formats**: Use open-source alternatives

### Migration Plan

Every 5 years, review:
- File format compatibility
- Software dependencies
- Storage medium health
- Access methods

### Archiving Completed Projects

When project completes:

```bash
# Move to archive
mv projects/current/my-project projects/archive/my-project-2025/

# Create archive package
cd projects/archive/
tar -czf my-project-2025.tar.gz my-project-2025/

# Upload to preservation service
# e.g., Zenodo, institutional repository

# Create DOI for citation

# Update project README with archive location
```

## Privacy & Security

### Sensitive Data

**Do NOT include**:
- Passwords or API keys
- Personal health information
- Proprietary corporate data
- Unpublished collaborator data
- Any data without permission to share

### Access Control

For private repositories:
```bash
# Set repository to private
gh repo create --private

# Add specific collaborators
gh repo add-collaborator username
```

### Encryption

For sensitive local data:
```bash
# Encrypt sensitive directory
tar -czf - projects/sensitive/ | openssl enc -aes-256-cbc -e > sensitive.tar.gz.enc

# Decrypt when needed
openssl enc -aes-256-cbc -d -in sensitive.tar.gz.enc | tar xzf -
```

### Compliance

Check if your institution requires:
- IRB approval for human subjects
- IACUC for animal work
- Export control compliance
- Data protection regulations (GDPR, etc.)

## Metadata Standards

### Minimum Metadata for Each Paper

Required fields in `metadata.json`:
```json
{
  "paper_id": "unique-identifier",
  "doi": "10.xxxx/yyyy",
  "title": "Full title",
  "authors": ["Author 1", "Author 2"],
  "publication": {
    "journal": "Journal Name",
    "year": 2025,
    "volume": "123",
    "pages": "456-789"
  },
  "date_added": "2025-10-09T12:00:00Z",
  "last_modified": "2025-10-09T12:00:00Z",
  "keywords": ["keyword1", "keyword2"]
}
```

### Metadata for Protocols

```json
{
  "protocol_id": "unique-id",
  "version": "1.0",
  "status": "validated",
  "author": "Your Name",
  "date_created": "2025-10-09",
  "date_validated": "2025-10-15",
  "based_on": ["DOI1", "DOI2"],
  "techniques": ["technique1", "technique2"],
  "species": ["organism"],
  "equipment": ["instrument1", "instrument2"]
}
```

### Metadata for Models

```json
{
  "model_id": "unique-id",
  "version": "1.0",
  "mechanism": "radical-pair",
  "system": "cryptochrome",
  "validated": true,
  "validation_data": "DOI",
  "code_doi": "10.5281/zenodo.xxxxx",
  "parameters_source": ["DOI1", "DOI2"],
  "accuracy": "±5%",
  "computational_cost": "10 CPU-hours per scan"
}
```

### Linked Data

For maximum interoperability, use JSON-LD:
```json
{
  "@context": "https://schema.org/",
  "@type": "ScholarlyArticle",
  "identifier": "https://doi.org/10.xxxx/yyyy",
  "name": "Paper Title",
  "author": [{
    "@type": "Person",
    "name": "Author Name",
    "identifier": "https://orcid.org/0000-0000-0000-0000"
  }]
}
```

## Monitoring & Auditing

### Regular Checks

Monthly checklist:
- [ ] All PDFs have metadata entries
- [ ] No orphaned files (files not in index)
- [ ] Indices are consistent
- [ ] Backups are current
- [ ] Git repository is pushed
- [ ] No sensitive data exposed

### Audit Script

```bash
#!/bin/bash
# audit.sh - Check knowledge base integrity

echo "Knowledge Base Audit $(date)"
echo "================================"

# Count papers
PDF_COUNT=$(ls Literature/*.pdf | wc -l)
META_COUNT=$(ls knowledge-base/papers/*/metadata.json | wc -l)

echo "PDFs in Literature/: $PDF_COUNT"
echo "Metadata files: $META_COUNT"

if [ $PDF_COUNT -ne $META_COUNT ]; then
    echo "WARNING: PDF count doesn't match metadata count!"
fi

# Check for large files
echo "\nLarge files (>50MB):"
find . -type f -size +50M

# Check last backup
echo "\nLast git push:"
git log -1 --format="%ai %s"

echo "\n=== Audit Complete ==="
```

Run monthly:
```bash
chmod +x audit.sh
./audit.sh > audit-reports/audit-$(date +%Y-%m).txt
```

## Data Management FAQs

**Q: How long should I keep simulation data?**
A: Raw simulation outputs: 1 year. Analyzed data and figures: Forever (these are small).

**Q: Should I commit PDFs to git?**
A: Only with Git LFS and if you have permission. Better to reference DOIs.

**Q: How do I handle papers without DOIs?**
A: Use a local identifier scheme: `LOCAL-YYYY-NNN` where NNN is a counter.

**Q: What if I lose my notes on a paper?**
A: As long as metadata.json is backed up, you can regenerate context from the PDF. Annotations may be lost - commit frequently!

**Q: How do I share my knowledge base with a new lab member?**
A: Clone from GitHub, sync PDFs from shared drive, install dependencies. Should take <1 hour.

---

**Review Schedule**: Review this plan annually
**Last Review**: 2025-10-09
**Next Review**: 2026-10-09
**Responsible**: Principal Investigator
