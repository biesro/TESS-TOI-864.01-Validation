# Vetting and False Positive Analysis of TOI 864.01

**Code repository for the paper:**
> *Vetting and False Positive Analysis of TOI 864.01: Evidence for a Likely Hierarchical Eclipsing Binary Masked by Dilution*

![Python Version](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![arXiv](https://img.shields.io/badge/arXiv-2601.02171-b31b1b.svg)](https://arxiv.org/abs/2601.02171)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17881756.svg)](https://doi.org/10.5281/zenodo.17881756)
[![Status](https://img.shields.io/badge/Status-Probable%20FP-orange.svg)]()

**Principal Investigator:** Biel Escolà Rodrigo  
**Date:** January 2026  

---

## 🔭 Abstract
This repository contains the complete analysis pipeline used to reclassify **TOI 864.01** (TIC 231728511), initially identified as a potential ultra-short-period ($P \approx 0.52$ d) Earth-sized candidate ($R_p \approx 1.1 R_\oplus$).

While standard vetting metrics (BLS, Centroids, RUWE) initially suggested a planetary nature, our comprehensive analysis incorporating **archival high-resolution imaging** and **Bayesian model comparison** reveals a critical contamination source. We present evidence that the signal is a **False Positive** caused by a Hierarchical Eclipsing Binary (HEB) on a bound stellar companion at 0.04", whose deep eclipses are heavily diluted by the primary star.

This repository provides the code to reproduce the detection, the statistical validation failure (due to extreme dilution), and the physical parameter derivation that led to this reclassification.

## 🌍 Key Findings & Reclassification Parameters

Based on the analysis of **12 TESS Sectors** and TFOP SG1 constraints:

| Parameter | Value | Note |
| :--- | :--- | :--- |
| **Target** | TIC 231728511 | M-Dwarf ($0.399 R_\odot$) |
| **Signal Period** | **0.52067 days** | Robust detection |
| **SPOC Depth** | ~640 ppm | Undiluted baseline |
| **Recovered Depth** | ~158 ppm | Attenuated by detrending |
| **Contaminant** | **0.04" Companion** | Detected by TFOP SG1 |
| **Validation Status** | **FALSE POSITIVE** | Statistical validation fails (NaN) |
| **Classification** | Hierarchical EB | Masked by heavy dilution |

## ⚙️ Methodology & Software Stack
The analysis follows a rigorous forensic protocol implemented in Python.

### 1. Detection & Signal Recovery
* **Tool:** `Lightkurve` (v2.5.1) + Box Least Squares (BLS)
* **Finding:** Recovers the periodic signal but highlights significant depth attenuation (~158 ppm) compared to SPOC, flagging potential dilution issues.
* **Script:** `code/01_detection_BLS.py`

### 2. Centroid Analysis
* **Tool:** `Lightkurve` + `Matplotlib`
* **Finding:** Centroids show no significant shift. **Critical Note:** This test fails to identify the false positive because the contaminant (0.04") is too close to be resolved by TESS pixel centroids (~21"/pixel).
* **Script:** `code/02_centroid_test.py`

### 3. Statistical Validation (TRICERATOPS)
* **Tool:** `triceratops` (v1.0.20)
* **Finding:** When the 0.04" companion is added to the aperture, the False Positive Probability (FPP) calculation **fails to converge (returns NaN)**. This non-convergence is a key result, indicating that statistical validation is inapplicable in regimes of such extreme contamination.
* **Notebook:** `code/03_triceratops_vetting.ipynb`

### 4. Bayesian Model Comparison
* **Tool:** `juliet` (v2.2.8) powered by `dynesty`
* **Finding:** Compares Planetary vs. Eclipsing Binary models. Result is inconclusive ($\Delta \ln Z \approx 0.09$), confirming that photometry alone cannot distinguish the scenarios due to the blending degeneracy.
* **Script:** `code/04_juliet_model_comparison.py`

## 📂 Repository Structure

```text
TOI-864.01-Vetting/
│
├── requirements.txt           # Main dependencies (juliet, lightkurve, etc.)
├── README.md                  # Project documentation
│
├── code/                      # Analysis scripts
    ├── 01_detection_BLS.py
    ├── 02_centroid_test.py
    ├── 03_triceratops_vetting.ipynb  <-- Key validation step
    ├── 04_juliet_model_comparison.py
    ├── 05_sanity_checks.py
    └── 06_planet_parameters.py
└── figures/                   # Generated plots (included in the paper)
```
## 🚀 Usage & Reproducibility
To reproduce the analysis, please note that the Jupyter Notebook (03) requires a specific environment configuration to support triceratops.

1. Clone the repository
Bash
```text
git clone [https://github.com/biesro/TESS-TOI-864.01-Validation.git](https://github.com/biesro/TESS-TOI-864.01-Validation.git)
cd TESS-TOI-864.01-Validation
```
2. Running the Python Scripts (Modeling)
For general scripts (BLS detection, Juliet modeling, Sanity checks):

Bash
```text
pip install -r requirements.txt
python code/01_detection_BLS.py
```
### 3. Running the Validation Notebook (Triceratops)
**⚠️ IMPORTANT:** The statistical vetting notebook requires a **specific legacy environment** (`numpy==1.26.4`). We strongly recommend creating a **fresh virtual environment** for this step to avoid conflicts.

Bash
```text
# Create and activate a new environment
conda create -n toi_validation python=3.10
conda activate toi_validation

# Install the specific validation stack AND Jupyter
pip install -r requirements-jupyter.txt notebook

# Launch the notebook
jupyter notebook code/03_triceratops_vetting.ipynb
```
Note: The notebook contains a built-in patch to resolve AttributeError: module 'numpy' has no attribute 'int'.

## 📄 Citation
If you use this data or methodology, please cite the arXiv paper. If you use the specific code pipeline, you may also cite the software record.

**Paper (BibTeX):**
```bibtex
@article{escola2026toi864,
  title={Vetting and False Positive Analysis of TOI 864.01: Evidence for a Likely Hierarchical Eclipsing Binary Masked by Dilution},
  author={Escolà Rodrigo, Biel},
  journal={arXiv preprint arXiv:2601.02171 },
  year={2026},
  url={[https://arxiv.org/abs/2601.02171](https://arxiv.org/abs/2601.02171)}
}
```
**Software (BibTeX):**
```bibtex

@software{escola2026code,
  author       = {Biel Escolà Rodrigo},
  title        = {TESS-TOI-864.01-Validation: Analysis Pipeline},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.17881756},
  url          = {[https://doi.org/10.5281/zenodo.17881756](https://doi.org/10.5281/zenodo.17881756)}
}
```

This research made use of the NASA Exoplanet Archive, TESS mission data, and the TFOP SG1 imaging notes.
