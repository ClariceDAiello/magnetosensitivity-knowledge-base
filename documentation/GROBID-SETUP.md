# GROBID Setup Guide

## Overview
GROBID (GeneRation Of BIbliographic Data) is a machine learning library for extracting and structuring raw documents (especially PDFs). It's particularly useful for processing large academic papers and books.

## Option 1: Docker Installation (Recommended)

### Prerequisites
- Docker Desktop for macOS: https://www.docker.com/products/docker-desktop

### Installation Steps

1. **Install Docker Desktop**
   ```bash
   # Download from https://www.docker.com/products/docker-desktop
   # Or install via Homebrew:
   brew install --cask docker
   ```

2. **Pull GROBID Docker Image**
   ```bash
   docker pull grobid/grobid:0.8.0
   ```

3. **Run GROBID Server**
   ```bash
   docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0
   ```

4. **Verify Installation**
   ```bash
   curl http://localhost:8070/api/isalive
   ```

### Using GROBID with This Project

Once GROBID is running, use our Python wrapper:

```bash
cd /Users/clarice/Desktop/Claude/Teste
python scripts/process_pdf.py --pdf Literature/BIOELECTROMAGNETISM.pdf --output knowledge-base/papers/
```

## Option 2: Python-Only Processing (No Docker Required)

Our fallback system uses pure Python libraries for PDF processing:

- **PyMuPDF (fitz)**: Fast PDF text extraction
- **pdfplumber**: Table and layout analysis
- **pypdf**: Metadata extraction
- **PyPDF2**: Comprehensive PDF manipulation

### Installation

```bash
pip install pymupdf pdfplumber pypdf PyPDF2 requests
```

### Usage

The Python processing script automatically falls back to this method if GROBID is unavailable.

## Performance Comparison

| Method | Speed | Accuracy | Structure Extraction | Large PDFs |
|--------|-------|----------|---------------------|------------|
| GROBID | Fast  | High     | Excellent           | Excellent  |
| Python | Medium| Medium   | Good                | Good       |

## Recommended Workflow

1. **For papers <5MB**: Use Python-only processing (faster setup)
2. **For books and large documents >5MB**: Use GROBID via Docker
3. **For batch processing**: Use GROBID for consistency

## Troubleshooting

### Docker Issues
- **Port already in use**: Change port with `-p 8071:8070`
- **Memory issues**: Increase Docker memory allocation in Docker Desktop preferences
- **Connection refused**: Wait 30 seconds after starting container

### Python Issues
- **Missing libraries**: Run `pip install -r requirements.txt`
- **Encoding errors**: Papers with non-standard encodings may need manual inspection
- **Memory errors**: Process large PDFs in chunks using the `--chunk-size` flag

## Next Steps

After installation, run the automated processing pipeline:

```bash
python scripts/process_all_papers.py
```

This will:
1. Detect available processing methods
2. Choose optimal method for each PDF
3. Generate FAIR-compliant context files
4. Update all indices
