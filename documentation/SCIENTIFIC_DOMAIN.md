# Scientific Domain Reference: Magnetosensitivity Research

This document contains technical concepts, notation standards, and indexed papers for the magnetosensitivity research knowledge base. Load this reference when engaging with domain-specific scientific questions.

---

## Key Technical Concepts

### 1. Radical Pair Mechanism (RPM)
- Magnetosensitivity via spin-correlated radical pairs (e.g., FAD•− + Trp•+)
- Hyperfine coupling drives singlet-triplet interconversion
- Geomagnetic field (~50 µT) modulates reaction yields
- Theoretical basis for magnetic compass in birds

### 2. Chemical Amplification
- **Prompt effect (χₚ)**: Fast (<1 ms) magnetic field effect from spin dynamics
- **Delayed effect (χₐ)**: Slow (100 ms - seconds) amplification from differential radical termination
- **Amplification factor**: E = χₐ/χₚ ≈ √(kD/kF)
  - kD: Donor radical (D•+) termination rate
  - kF: Flavin radical (F•−) termination rate
- Physical mechanism: When kD > kF, D•+ is removed faster, increasing [F•−] lifetime and depleting [F] ground state, amplifying fluorescence changes

### 3. Cryptochromes (CRY)
- Blue-light photoreceptors, FAD-containing flavoproteins
- Found in retina of migratory birds
- Variants: CRY1, CRY2, CRY4
- Photocycle: photoexcitation → electron transfer → radical pair formation → spin-selective recombination

### 4. Key Experimental Techniques
- **Transient Absorption Spectroscopy (TAS)**: Detects radical pairs
- **Electron Paramagnetic Resonance (EPR/ESR)**: Measures hyperfine coupling
- **Fluorescence Spectroscopy**: Monitors magnetic field effects
- **MARY Spectroscopy**: Magnetically Affected Reaction Yield

### 5. Computational Methods
- **Spin dynamics simulation**: Density matrix formalism, Liouville equation
- **Molecular Dynamics (MD)**: Protein conformational sampling
- **DFT**: g-tensor and hyperfine coupling calculations

---

## Notation Standards

### Magnetic Field Parameters

When documenting experiments, always specify:
- **Field strength**: µT (microtesla) or mT (millitesla)
- **Field type**: Static, oscillating, RF
- **Orientation**: Parallel/perpendicular to sample
- **Reference frame**: Lab frame, molecular frame

Example:
```markdown
**Magnetic Field Configuration**:
- Static field: 50 µT (geomagnetic equivalent)
- RF field: 1.4 MHz, 50 nT amplitude
- Orientation: Perpendicular to optical axis
```

### Spin Chemistry Notation

Use standard notation from `knowledge-base/ontology/abbreviations.json`:
- **Radical species**: FAD•−, Trp•+, FADH•
- **Spin states**: ¹(F•− D•+) for singlet, ³(F•− D•+) for triplet
- **Rate constants**: kF, kD, kBT, kISC
- **Observables**: χₚ, χₐ, E, B₁/₂

### Citation Format

Always cite sources:
- **Papers in knowledge base**: `[nchem_2447]` or `10.1038/NCHEM.2447`
- **Ontology terms**: Include source DOI in JSON
- **Experimental protocols**: Reference original paper

---

## Key Papers Currently in Knowledge Base

### 1. nchem_2447 (DOI: 10.1038/NCHEM.2447)
- Kattnig et al., Nature Chemistry 2016
- **Topic**: Chemical amplification of magnetic field effects
- **Key findings**: E ≈ √(kD/kF), FMN/lysozyme model system

### 2. annurev-biophys-032116-094545 (DOI: 10.1146/annurev-biophys-032116-094545)
- Annual Review of Biophysics
- **Topic**: Magnetic compass in migratory birds

### 3. 41557_2016_BFnchem2447_MOESM350_ESM (DOI: 10.1038/NCHEM.2447)
- Supplementary material for nchem_2447

### 4. Spin_Dynamics_in_Radical_Pairs_Alan_Lewis (DOI: 10.1007/978-3-030-00686-0)
- Comprehensive theoretical treatment
- **Topic**: Spin dynamics, density matrix formalism

### 5. Magnetobiology_Underlying_Physical_Problems_by_Vladimir_N__Binhi
- Book on weak magnetic field effects
- **Topic**: Biophysical mechanisms, ion cyclotron resonance

### 6. BIOELECTROMAGNETISM (DOI: 10.1201/9781003181354)
- History and foundations
- **Topic**: Bioelectromagnetic field effects, historical perspectives

---

## External Resources

- **Radical Pair Mechanism**: Hore & Mouritsen, Annu. Rev. Biophys. 2016
- **Spin Chemistry**: Steiner & Ulrich, Chem. Rev. 1989
- **Cryptochrome**: Dodson et al., Trends Biochem. Sci. 2013
