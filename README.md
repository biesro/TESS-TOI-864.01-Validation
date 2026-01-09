# Physical Vetting of the Ultra-Short-Period Sub-Earth TOI 864.01

![Python Version](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![arXiv](https://img.shields.io/badge/arXiv-2601.02171-b31b1b.svg)](https://arxiv.org/abs/2601.02171)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17881756.svg)](https://doi.org/10.5281/zenodo.17881756) 

**Principal Investigator:** Biel Escolà Rodrigo  
**Date:** January 2026  
**Paper:** [arXiv:2601.02171](https://arxiv.org/abs/2601.02171)

---

## 🔭 Abstract
This repository contains the complete validation analysis and vetting pipeline for **TOI 864.01** (TIC 231728511), a sub-Earth candidate observed by the NASA TESS mission.

Despite the low Signal-to-Noise Ratio (SNR) inherent to sub-Earth candidates, we present a robust **physical vetting framework** that confirms the planetary nature of the signal. By combining standard photometry with Bayesian model comparison (`juliet`) and False Positive Probability analysis (`triceratops`), we rule out astrophysical false positives such as background eclipsing binaries and hierarchical triples.

The analysis confirms a transit signal consistent with an **Ultra-Short Period (USP) Sub-Earth** ($0.55 R_\oplus$) orbiting an M-dwarf star with a period of just **0.52 days**.

## 🌍 Key Physical Parameters
Based on the analysis of **54 TESS Sectors**:

| Parameter | Value | Uncertainty | Method |
| :--- | :--- | :--- | :--- |
| **Target** | TIC 231728511 | - | TOI 864.01 |
| **Host Star Type** | M-Dwarf | - | Red Dwarf ($0.399 R_\odot$) |
| **Orbital Period** | **0.52067 days** | $\pm 10^{-5}$ | BLS Detection |
| **Planet Radius** | **0.55 $R_\oplus$** | - | `juliet` Modeling |
| **Semi-Major Axis** | 0.0093 AU | - | Kepler's 3rd Law |
| **Transit Depth** | ~158 ppm | - | MCMC Posterior |
| **Equilibrium Temp** | ~1100 K | - | Bond Albedo = 0 |

## ⚙️ Methodology & Software Stack
The validation process follows a rigorous sequential protocol implemented in Python. Special attention has been paid to reproducibility due to version constraints in legacy astronomical libraries.

### 1. Detection & Signal Recovery
* **Tool:** `Lightkurve` (v2.5.1) + Box Least Squares (BLS)
* **Process:** Downloads SPOC data, stitches sectors, removes outliers ($\sigma=5$), and recovers the periodic signal.
* **Script:** `code/01_detection_BLS.py`

### 2. Centroid Analysis
* **Tool:** `Lightkurve` + `Matplotlib` (v3.10.8)
* **Test:** Verifies that the center-of-light does not shift during transit events, ruling out background contaminants.
* **Script:** `code/02_centroid_test.py`

### 3. Statistical Vetting (FPP/NFPP)
* **Tool:** `triceratops` (v1.0.20)
* **Test:** Calculates the Nearby False Positive Probability (NFPP) via 50,000 Monte Carlo simulations. Result: **NFPP = 0.0000**.
* **Notebook:** `code/03_triceratops_vetting.ipynb`
* **Note:** This notebook includes a compatibility patch for `numpy` (v1.26.4) to handle deprecated `np.int` types required by `triceratops`.

### 4. Bayesian Model Comparison
* **Tool:** `juliet` (v2.2.8) powered by `dynesty` (v3.0.0) & `batman-package` (v2.5.3)
* **Test:** Compares the Bayesian Evidence ($\ln Z$) of a Planetary Model vs. an Eclipsing Binary Model.
* **Script:** `code/04_juliet_model_comparison.py`

### 5. Physical Sanity Checks
* **Test:**
    * **Odd-Even Asymmetry:** Checks for depth differences (ruled out at $<1\sigma$).
    * **Density Check:** Compares transit-derived stellar density with catalog density (`astropy` v6.1.7).
* **Script:** `code/05_sanity_checks.py`

## 📂 Repository Structure

```text
TOI-864.01-Vetting/
│
├── Physical Vetting of the Ultra-Short-Period Sub-Earth TOI 864.01.pdf   # Full scientific paper (arXiv preprint)
├── requirements.txt           # Main dependencies for .py scripts (Juliet, Astropy, etc.)
├── requirements-jupyter.txt   # Specific dependencies for the vetting Notebook (Triceratops env)
├── README.md                  # Project documentation
│
├── code/                      # Analysis scripts
    ├── 01_detection_BLS.py
    ├── 02_centroid_test.py
    ├── 03_triceratops_vetting.ipynb  <-- Run this for FPP validation
    ├── 04_juliet_model_comparison.py
    ├── 05_sanity_checks.py
    └── 06_planet_parameters.py
```
## 🚀 Usage & Reproducibility
To reproduce the analysis, please note that the Jupyter Notebook (03) requires a specific environment configuration to support triceratops.

1. Clone the repository
Bash
```text
git clone [https://github.com/biesro/TOI-864.01-Vetting.git](https://github.com/biesro/TOI-864.01-Vetting.git)
cd TOI-864.01-Vetting
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
If you use this data or methodology, please cite the arXiv paper:

**BibTeX:**
```bibtex
@article{escola2026toi864,
  title={Physical Vetting of the Ultra-Short-Period Sub-Earth TOI 864.01},
  author={Escolà Rodrigo, Biel},
  journal={arXiv preprint arXiv:2601.02171},
  year={2026},
  url={[https://arxiv.org/abs/2601.02171](https://arxiv.org/abs/2601.02171)}
}
```
This research made use of the NASA Exoplanet Archive and the TESS mission data.
