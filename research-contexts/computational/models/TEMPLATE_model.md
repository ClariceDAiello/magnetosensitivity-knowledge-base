# Computational Model: [Model Name]

## Metadata
- **Model ID**: [Unique identifier]
- **Version**: 1.0
- **Date Created**: [ISO 8601 date]
- **Last Modified**: [ISO 8601 date]
- **Author**: [Name]
- **Based On**: [Citation to paper(s)]
- **Code Repository**: [GitHub/GitLab link if applicable]

## Overview

### Purpose
[What biological phenomenon this model simulates]

### Theoretical Background
[Physical/chemical principles underlying the model]
[Link to relevant papers in knowledge base]

### Scope
- **System Scale**: [Molecular/cellular/organism]
- **Time Scale**: [Nanoseconds to seconds/minutes/hours]
- **Spatial Scale**: [Atomic/molecular/cellular]

## Model Description

### Physical System
- **Molecular System**: [Protein(s), cofactor(s)]
- **Magnetic Field**: [Field parameters being modeled]
- **Environment**: [Solvent, temperature, etc.]

### Hamiltonian / Governing Equations

```
[Mathematical description of the model]

H = H_zeeman + H_exchange + H_hyperfine + H_dipolar + ...

Where:
- H_zeeman: Zeeman interaction with external field
- H_exchange: Exchange interaction between radical pairs
- ...
```

### Key Assumptions
1. [Assumption 1 and justification]
2. [Assumption 2 and justification]
3. [Assumption 3 and justification]

### Limitations
1. [Limitation 1]
2. [Limitation 2]

## Parameters

### Magnetic Parameters
| Parameter | Symbol | Value | Unit | Source | Uncertainty |
|-----------|--------|-------|------|--------|-------------|
| g-factor (radical 1) | g₁ | [value] | dimensionless | [ref] | [±value] |
| g-factor (radical 2) | g₂ | [value] | dimensionless | [ref] | [±value] |
| Exchange coupling | J | [value] | μT | [ref] | [±value] |
| Hyperfine coupling | A | [value] | μT | [ref] | [±value] |

### Kinetic Parameters
| Parameter | Symbol | Value | Unit | Source |
|-----------|--------|-------|------|--------|
| Radical pair lifetime | τ | [value] | ns | [ref] |
| Singlet decay rate | k_S | [value] | s⁻¹ | [ref] |
| Triplet decay rate | k_T | [value] | s⁻¹ | [ref] |
| Recombination rate | k_rec | [value] | s⁻¹ | [ref] |

### Environmental Parameters
| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| Temperature | [value] | K | [conditions] |
| Viscosity | [value] | cP | [solvent] |
| Dielectric constant | [value] | dimensionless | [medium] |

## Implementation

### Method
- **Numerical Method**: [Runge-Kutta, Monte Carlo, etc.]
- **Integration Scheme**: [Details]
- **Time Step**: [Value and justification]
- **Convergence Criteria**: [How to ensure accuracy]

### Software Requirements
```bash
# Required packages
python >= 3.8
numpy >= 1.20
scipy >= 1.7
matplotlib >= 3.4

# Optional (for parallel computing)
mpi4py >= 3.0
numba >= 0.54
```

### Code Structure
```
model_directory/
├── src/
│   ├── hamiltonian.py       # Hamiltonian construction
│   ├── spin_dynamics.py     # Time evolution
│   ├── observables.py       # Calculate observables
│   └── parameters.py        # Parameter definitions
├── scripts/
│   ├── run_simulation.py    # Main simulation script
│   └── analyze_results.py   # Analysis script
├── data/
│   └── parameters/          # Parameter sets
└── results/
    └── [simulation outputs]
```

## Usage

### Basic Simulation

```python
"""
Example: Simulate radical pair dynamics under 50 μT magnetic field
"""

from src.hamiltonian import RadicalPairHamiltonian
from src.spin_dynamics import SpinEvolution
from src.observables import calculate_singlet_yield

# Define parameters
params = {
    'B_field': 50e-6,  # 50 μT in Tesla
    'g1': 2.0023,
    'g2': 2.0040,
    'J': 0.0,  # μT
    'A_tensor': [...],  # Hyperfine coupling tensor
    'tau': 1e-6,  # 1 μs lifetime
}

# Initialize Hamiltonian
H = RadicalPairHamiltonian(params)

# Simulate time evolution
t_max = 10e-6  # 10 μs
dt = 1e-9  # 1 ns steps
evolution = SpinEvolution(H, t_max, dt)

# Calculate observables
singlet_yield = calculate_singlet_yield(evolution)

print(f"Singlet yield at {params['B_field']*1e6:.1f} μT: {singlet_yield:.3f}")
```

### Parameter Scan

```python
"""
Example: Scan magnetic field effect on singlet yield
"""

import numpy as np
from src.run_field_scan import run_parameter_scan

# Define field range
B_fields = np.linspace(0, 100e-6, 100)  # 0-100 μT

# Run scan
results = run_parameter_scan(
    parameter='B_field',
    values=B_fields,
    other_params=params,
    n_cores=4  # Parallel execution
)

# Plot results
import matplotlib.pyplot as plt
plt.plot(B_fields * 1e6, results['singlet_yield'])
plt.xlabel('Magnetic Field (μT)')
plt.ylabel('Singlet Yield')
plt.title('Magnetic Field Effect')
plt.savefig('results/field_scan.png')
```

## Validation

### Comparison with Experimental Data
- **Experimental Data Source**: [Paper reference]
- **Validation Metrics**: [How to compare model vs experiment]
- **Agreement**: [Quantitative measure of fit]

### Benchmark Results
| Test Case | Expected Result | Model Result | Agreement |
|-----------|----------------|--------------|-----------|
| [Test 1] | [Value] | [Value] | [%/metric] |
| [Test 2] | [Value] | [Value] | [%/metric] |

### Sensitivity Analysis
- **Critical Parameters**: [Which parameters most affect results]
- **Robustness**: [How sensitive is model to parameter uncertainty]

## Example Results

### Typical Output

```
Simulation: Radical Pair in Earth's Magnetic Field
================================================
Magnetic field: 50.0 μT
Temperature: 298 K
Simulation time: 10.0 μs
Time step: 1.0 ns

Results:
--------
Singlet yield: 0.532 ± 0.003
Triplet yield: 0.468 ± 0.003
Recombination product: 0.312 ± 0.002
Escape probability: 0.688 ± 0.002

Magnetic field effect:
ΔΦ(50μT) = 0.042 (7.9% change from zero field)
```

### Visualization

[Include example figures showing:
- Time evolution of spin states
- Magnetic field dependence curves
- Angular dependence plots
]

## Performance

### Computational Requirements
- **Single simulation**: [CPU time, memory]
- **Parameter scan (100 points)**: [Total time with N cores]
- **Recommended hardware**: [Specs]

### Optimization Notes
- [Tips for faster execution]
- [Parallelization strategy]
- [Memory management considerations]

## Extensions & Future Directions

### Possible Improvements
1. [Enhancement 1]
2. [Enhancement 2]

### Variants
- **[Variant 1 name]**: [Brief description]
- **[Variant 2 name]**: [Brief description]

## References

### Primary Literature
- [Paper 1 - internal link to knowledge base]
- [Paper 2 - internal link to knowledge base]

### Related Models
- [Model 1 - internal link]
- [Model 2 - internal link]

### External Resources
- [Textbook/review article]
- [Software documentation]

## Appendices

### Appendix A: Derivation of Key Equations
[Mathematical details]

### Appendix B: Parameter Estimation Methods
[How parameters were determined]

### Appendix C: Coordinate System Conventions
[Definition of axes, angles, etc.]

---

**Model Status**: [Development/Validated/Published]
**Validation Date**: [Date if validated]
**Code DOI**: [If code is archived (e.g., Zenodo)]
