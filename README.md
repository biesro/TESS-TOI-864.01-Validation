# Vetting and False Positive Analysis of TOI 864.01

**Code repository for the paper:**
> *Vetting and False Positive Analysis of TOI 864.01: Evidence for a Likely Hierarchical Eclipsing Binary Masked by Dilution*

![Python Version](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![arXiv](https://img.shields.io/badge/arXiv-2602.14840-b31b1b.svg)](https://arxiv.org/abs/2602.14840)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17881756.svg)](https://doi.org/10.5281/zenodo.17881756)
[![Status](https://img.shields.io/badge/Status-Probable%20FP-orange.svg)]()

**Principal Investigator:** Biel Escolà Rodrigo  
**Date:** January 2026  

---

## 🔭 Abstract

This repository contains the complete analysis pipeline used to reclassify **TOI 864.01** (TIC 231728511), initially identified as a potential ultra-short-period ($P \approx 0.52$ d) Earth-sized candidate ($R_p \approx 1.1 R_\oplus$).

While standard vetting metrics (BLS, Centroids, RUWE) initially suggested a planetary nature, our comprehensive analysis incorporating **archival high-resolution imaging**, **ground-based follow-up photometry**, and **Bayesian model comparison** reveals a critical contamination source. We present evidence that the signal is a **False Positive** caused by a Hierarchical Eclipsing Binary (HEB) on a bound stellar companion at 0.04", whose deep eclipses are heavily diluted by the primary star.

Key findings supporting this reclassification include:

* **Unresolved Companion:** A 0.04" neighbor detected via speckle interferometry (TFOP SG1).
* **Depth Discrepancy:** Ground-based transit depth ($\approx 0.37$ ppt) is significantly shallower than the TESS prediction ($\approx 0.64$ ppt), confirming extreme dilution.
* **Timing Instability:** A measured timing offset of **6.3 minutes late** (along with historical TTVs) consistent with binary orbital dynamics.

This repository provides the code to reproduce the detection, the statistical validation analysis (which yields misleading results due to the unresolved companion), and the physical parameter derivation that led to this reclassification.

## 🌍 Key Findings & Reclassification Parameters

Based on the analysis of **12 TESS Sectors** and TFOP SG1 constraints:

| Parameter | Value | Note |
| :--- | :--- | :--- |
| **Target** | TIC 231728511 | M-Dwarf ($0.399 R_\odot$) |
| **Signal Period** | **0.52067 days** | Robust detection |
| **SPOC Depth** | ~640 ppm | Undiluted baseline |
| **Recovered Depth** | ~158 ppm | Attenuated by detrending |
| **Contaminant** | **0.04" Companion** | Detected by TFOP SG1 |
| **Validation Status** | **FPP ~0.25 (Unreliable)** | Misleading due to catalog incompleteness |
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
* **Finding:** The analysis yields a False Positive Probability (FPP) of **~0.25**. This result is **misleadingly optimistic** because the tool relies on Gaia catalogs, which do not resolve the 0.04" companion. This demonstrates the limitation of statistical validation when catalogs are incomplete.
* **Notebook:** `code/03_triceratops_vetting.ipynb`

### 4. Bayesian Model Comparison
* **Tool:** `juliet` (v2.2.8) powered by `dynesty`
* **Finding:** Compares Planetary vs. Eclipsing Binary models. Result is inconclusive ($\Delta \ln Z \approx 0.25$), confirming that photometry alone cannot distinguish the scenarios due to the blending degeneracy.
* **Script:** `code/04_juliet_model_comparison.py`

## 📂 Repository Structure

```text
TOI-864.01-Vetting/
│
├── requirements.txt                  # Main dependencies (juliet, lightkurve, etc.)
├── README.md                         # Project documentation
├── TOI864_01_ALL_SECTORS_FOLDED.csv  # Lightkurve sectors folded for triceratops
│
├── code/                             # Analysis scripts
    ├── 01_detection_BLS.py
    ├── 02_centroid_test.py
    ├── 03_triceratops_vetting.ipynb  <-- Key validation step
    ├── 03extra_generate_folded_csv.py
    ├── 04_juliet_model_comparison.py
    ├── 05_sanity_checks.py
    └── 06_planet_parameters.py
```
## 🚀 Usage & Reproducibility
To reproduce the analysis, please note that the ipynb (03) requires a specific environment configuration to support triceratops.

1. Clone the repository
Bash
```text
git clone https://github.com/biesro/TESS-TOI-864.01-Validation.git
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
**⚠️ IMPORTANT:** To use Triceratops I recommend following steps in the readme.md of https://github.com/JGB276/TRICERATOPS-plus/tree/main and using jupyter lab (in an isolated python 3.10 environment).

## 📄 Citation
If you use this data or methodology, please cite the arXiv paper. If you use the specific code pipeline, you may also cite the software record.

**Paper (BibTeX):**
```bibtex
@article{escola2026toi864,
  title={Vetting and False Positive Analysis of TOI 864.01: Evidence for a Likely Hierarchical Eclipsing Binary Masked by Dilution},
  author={Escolà Rodrigo, Biel},
  journal={arXiv preprint arXiv:2601.02171},
  year={2026},
  url={https://arxiv.org/abs/2601.02171}
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
  url          = {https://doi.org/10.5281/zenodo.17881756}
}
```

This research made use of the NASA Exoplanet Archive, TESS mission data, and the TFOP SG1 imaging notes.
