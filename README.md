# Validation of Ultra-Short Period Sub-Earth TOI 864.01

## Abstract
This repository contains the validation analysis and vetting pipeline for the exoplanet candidate **TOI 864.01** (TIC 231728511), observed by the NASA TESS mission. 

Using custom Python scripts leveraging the `lightkurve` library, we performed detrending, Box Least Squares (BLS) period search, and rigorous vetting tests. The analysis confirms a transit signal consistent with an **Ultra-Short Period (USP) Sub-Earth** ($0.55 R_\oplus$) orbiting an M-dwarf star. False positive scenarios (eclipsing binaries, background stars) were ruled out via centroid analysis and secondary eclipse checks.

## Key Physical Parameters
Based on the analysis of TESS Sector 27 data:

| Parameter | Value | Uncertainty | Source/Note |
| :--- | :--- | :--- | :--- |
| **Target** | TIC 231728511 | - | TOI 864.01 |
| **Host Star Type** | M-Dwarf | - | Red Dwarf |
| **Stellar Radius** | $0.399 R_\odot$ | $\pm 0.02$ | TIC v8 |
| **Orbital Period** | **0.52067 days** | - | BLS Detection |
| **Planet Radius** | **0.55 $R_\oplus$** | - | Approx. 0.5x Earth |
| **Semi-Major Axis** | 0.0093 AU | - | USP |
| **Transit Depth** | 158 ppm | - | |
| **Equilibrium Temp** | ~1100 K | - | |

## Methodology & Pipeline
The validation process followed a standard vetting protocol using open-source tools:

1.  **Data Retrieval:** High-cadence TESS imagery (Sector 27).
2.  **Preprocessing:** * **Detrending:** Applied a flattening filter (window length: 501 cadences) to remove stellar variability.
    * **Cleaning:** Outlier removal using sigma-clipping ($\sigma=5$).
3.  **Detection:** Utilized the Box Least Squares (BLS) algorithm to recover the periodic signal ($P \approx 0.52 d$).

## Vetting & Validation Results
To certify the planetary nature of the candidate, the following tests were passed:

* **Signal-to-Noise Ratio (SNR):** The transit detection yielded an SNR of **10.96**, exceeding the standard validation threshold of 7.1.
* **Morphological Analysis:** The phase-folded light curve exhibits a distinct "U-shape" with a flat bottom, consistent with a planetary transit rather than the "V-shape" typical of grazing eclipsing binaries.
* **Centroid Analysis:** No significant shift in the photocenter (X/Y coordinates) was observed during transit, ruling out background star contamination.
* **Secondary Eclipse:** Inspection of Phase 0.5 showed no secondary eclipse, confirming the orbiting body is non-luminous (planetary).

## Repository Structure
* `analysis_script.py` / `notebook.ipynb`: The source code used for the light curve processing and plotting.
* `TOI 864.01 Validation.pdf`: Full technical report with detailed plots and discussion.
* `requirements.txt`: Python dependencies.

## Usage
To reproduce the analysis:

1.  Clone the repository:
    ```bash
    git clone [https://github.com/biesro/TOI-864-Validation.git](https://github.com/biesro/TOI-864-Validation.git)
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the script/notebook.

## Citation
If you use this data or methodology, please cite this repository via Zenodo:

> Escolà Rodrigo, B. (2025). *Validation of Ultra-Short Period Sub-Earth TOI 864.01*. [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17881756.svg)](https://doi.org/10.5281/zenodo.17881756)

---
**Principal Investigator:** Biel Escolà Rodrigo  
**Date:** December 9, 2025
