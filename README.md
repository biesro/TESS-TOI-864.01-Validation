# Physical Vetting of the Ultra-Short-Period Sub-Earth TOI 864.01

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-submitted_to_arXiv-orange)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17881756.svg)](https://doi.org/10.5281/zenodo.17881756)

**Principal Investigator:** Biel Escolà Rodrigo  
**Date:** January 2026

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

## ⚙️ Methodology & Pipeline
The validation process follows a rigorous sequential protocol implemented in Python. The repository is structured to reproduce the analysis step-by-step:

### 1. Detection & Signal Recovery
* **Tool:** `Lightkurve` + Box Least Squares (BLS)
* **Process:** Downloads SPOC data, stitches sectors, removes outliers ($\sigma=5$), and recovers the periodic signal.
* **Script:** `code/01_detection_BLS.py`

### 2. Centroid Analysis
* **Tool:** `Lightkurve` (Moment analysis)
* **Test:** Verifies that the center-of-light does not shift during transit events, ruling out background contaminants.
* **Script:** `code/02_centroid_test.py`

### 3. Statistical Vetting (FPP/NFPP)
* **Tool:** `TRICERATOPS`
* **Test:** Calculates the Nearby False Positive Probability (NFPP) to quantify the risk of contamination from nearby stars. Result: **NFPP = 0.0000**.
* **Notebook:** `code/03_triceratops_vetting.ipynb`

### 4. Bayesian Model Comparison
* **Tool:** `juliet` (Nested Sampling via `dynesty`)
* **Test:** Compares the Bayesian Evidence ($\ln Z$) of a Planetary Model vs. an Eclipsing Binary Model.
* **Script:** `code/04_juliet_model_comparison.py`

### 5. Physical Sanity Checks
* **Test:**
    * **Odd-Even Asymmetry:** Checks for depth differences (ruled out at $<1\sigma$).
    * **Density Check:** Compares transit-derived stellar density with catalog density (Ratio $\approx 1.04$).
* **Script:** `code/05_sanity_checks.py`

## 📂 Repository Structure

```text
TOI-864.01-Vetting/
│
├── Final_864.01.pdf           # Full scientific paper (arXiv preprint)
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
│
├── code/                      # Analysis scripts
    ├── 01_detection_BLS.py
    ├── 02_centroid_test.py
    ├── 03_triceratops_vetting.ipynb
    ├── 04_juliet_model_comparison.py
    ├── 05_sanity_checks.py
    └── 06_planet_parameters.py

🚀 Usage
To reproduce the analysis on your local machine:

Clone the repository:

Bash

git clone [https://github.com/biesro/TOI-864.01-Vetting.git](https://github.com/biesro/TOI-864.01-Vetting.git)
cd TOI-864.01-Vetting
Install dependencies: It is recommended to use a virtual environment.

Bash

pip install -r requirements.txt
Run the pipeline: Execute the scripts in numerical order:

Bash

python code/01_detection_BLS.py
python code/02_centroid_test.py
# ... and so on
📄 Citation
If you use this data or methodology, please cite the associated arXiv paper or the Zenodo repository:

Escolà Rodrigo, B. (2026). Physical Vetting of the Ultra-Short-Period Sub-Earth TOI 864.01. arXiv preprint. DOI: 10.5281/zenodo.17881756

This research made use of the NASA Exoplanet Archive and the TESS mission data.
