"""
04_juliet_model_comparison_final.py
-----------------------------
Bayesian Model Comparison (Planet vs. Eclipsing Binary) using Juliet.
Optimized for robust validation of TESS candidates.

Author: Biel Escolà Rodrigo
Target: TOI 864.01
"""

import os
import sys
import shutil  # Required to delete old folders
import copy    # Required to safely copy dictionaries

# --- WINDOWS MULTIPROCESSING FIX ---
if 'HOME' not in os.environ:
    os.environ['HOME'] = os.environ['USERPROFILE']

import juliet
import numpy as np
import lightkurve as lk
import astropy.units as u

# =============================================================================
#  SECTION 1: GLOBAL VARIABLES (USER DEFINED)
# =============================================================================

# 1. Target ID
ID = "TIC 231728511"

# 2. ORBITAL PERIOD (Days)
# [USER ANALYSIS]: Value derived from your own BLS/TLS search.
# Accurate determination of the period is critical for the folding process.
P_PERIOD = 0.52067

# 3. EPOCH (T0 - Central Transit Time)
# [USER ANALYSIS]: Value derived from your own analysis (BJD - 2457000).
# This is used to center the transit at phase 0.0.
T0_OLD = 1411.1454 

if __name__ == '__main__':
    
    print("=================================================================")
    print(f"  ROBUST VALIDATION - {ID}")
    print("=================================================================")

    # --- AUTOMATIC CLEANUP (Prevents 'KeyError' or data mixing) ---
    folders_to_clean = ['results_planet_full', 'results_binary_full']
    print("\n[0/5] Cleaning old results to avoid conflicts...")
    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"       -> Deleted old folder: {folder}")
            except Exception as e:
                print(f"       -> WARNING: Could not delete {folder}. Error: {e}")

    # =========================================================================
    #  SECTION 2: DATA DOWNLOAD AND PROCESSING
    # =========================================================================
    print("\n[1/5] Downloading and Processing data...")
    try:
        # Search for TESS SPOC data
        search_result = lk.search_lightcurve(ID, mission="TESS", author="SPOC")
        if len(search_result) == 0: 
            search_result = lk.search_lightcurve(ID, mission="TESS")
        
        print(f"       -> Found {len(search_result)} files. Stitching...")
        lc_raw = search_result.download_all().stitch().remove_nans()
        
        # --- FOLDING ---
        # We fold the light curve using YOUR derived Period and T0.
        # NOTE: After folding, the new 'Time' becomes Phase time (centered at 0.0).
        lc_folded = lc_raw.fold(period=P_PERIOD, epoch_time=T0_OLD)
        
        # --- BINNING ---
        # [GUIDE]: 'time_bin_size' reduces noise and computation time.
        # - For normal transits (>2h): 5*u.min or 10*u.min is fine.
        # - For very short/fast transits (<1h): Use 2*u.min to preserve shape.
        lc_binned = lc_folded.bin(time_bin_size=5*u.min)
        lc_final = lc_binned.remove_nans()

        # Extract arrays for Juliet
        times = lc_final.time.value 
        flux = lc_final.flux.value
        flux_err = lc_final.flux_err.value
        
        print(f"       -> Data processed successfully. Points available: {len(times)}")

    except Exception as e:
        print(f"ERROR downloading/processing data: {e}")
        sys.exit(1)

    # Prepare dictionaries for Juliet
    tim, fl, fle = {}, {}, {}
    tim['TESS'] = np.array(times)
    fl['TESS'] = np.array(flux)
    fle['TESS'] = np.array(flux_err)

    # =========================================================================
    #  SECTION 3: CONFIGURE PLANET MODEL
    # =========================================================================
    print("\n[2/5] Configuring Priors (PLANET Model)...")
    priors = {}

    # --- A) LIMB DARKENING (Mandatory) ---
    # We use a quadratic law. Uniform [0,1] is a safe, conservative prior.
    priors['ld_law_TESS'] = {'distribution': 'fixed', 'hyperparameters': 'quadratic'}
    priors['q1_TESS'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 1.0]}
    priors['q2_TESS'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 1.0]}

    # --- B) PERIOD AND T0 ---
    # Since data is folded, Period is fixed, and T0 is near 0.0.
    priors['P_p1'] = {'distribution': 'fixed', 'hyperparameters': P_PERIOD}
    priors['t0_p1'] = {'distribution': 'uniform', 'hyperparameters': [-0.05, 0.05]} 
    
    # --- C) ORBITAL PARAMETERS ---
    
    # 1. Scaled Semimajor Axis (a/R*) -> 'a_p1'
    # [PHYSICS]: Relates to stellar density. 
    # For P=0.5d, the orbit is very tight, so 'a/R*' must be small (approx 2.0 - 5.0).
    # We set a wide range [1.5, 30.0] to be safe.
    priors['a_p1'] = {'distribution': 'uniform', 'hyperparameters': [1.5, 30.0]} 
    
    # 2. Radius Ratio (Rp/R*) -> 'p_p1'
    # [PLANET MODEL]: We restrict this to < 0.15 (15% of star size).
    # If it's bigger than this, it's likely not a planet.
    priors['p_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 0.15]} 
    
    # 3. Impact Parameter (b) -> 'b_p1'
    priors['b_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 0.9]} 
    
    # 4. Eccentricity -> 'ecc_p1'
    # [PLANET MODEL]: Simple planets are usually assumed circular (e=0).
    priors['ecc_p1'] = {'distribution': 'fixed', 'hyperparameters': 0.0}
    priors['omega_p1'] = {'distribution': 'fixed', 'hyperparameters': 90.0}

    # --- D) INSTRUMENT DILUTION ---
    # [EXOFOP]: You found Contamination Ratio ~ 0.001 (very low).
    # So Dilution = 1.0 is physically correct.
    priors['dilution_TESS'] = {'distribution': 'fixed', 'hyperparameters': 1.0} 
    
    # Jitter/Offset
    priors['mdilution_TESS'] = {'distribution': 'fixed', 'hyperparameters': 0.0}
    priors['mflux_TESS'] = {'distribution': 'normal', 'hyperparameters': [0.0, 0.1]}
    priors['sigma_w_TESS'] = {'distribution': 'loguniform', 'hyperparameters': [0.1, 10000]}

    # RUN PLANET MODEL
    print("\n[3/5] Running PLANET Model...")
    dataset_P = juliet.load(priors=priors, t_lc=tim, y_lc=fl, yerr_lc=fle, out_folder='results_planet_full')
    results_P = dataset_P.fit(sampler='dynesty', nthreads=1) 

    # =========================================================================
    #  SECTION 4: CONFIGURE BINARY MODEL (EB)
    # =========================================================================
    print("\n[4/5] Running BINARY Model (EB)...")
    
    # Deepcopy to modify priors without affecting the original dictionary
    priors_EB = copy.deepcopy(priors)
    
    # --- RELAX PARAMETERS FOR BINARY HYPOTHESIS ---
    
    # 1. Allow Eccentricity (V-shape dips)
    priors_EB['ecc_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 0.8]}
    priors_EB['omega_p1'] = {'distribution': 'uniform', 'hyperparameters': [-180, 180]}
    
    # 2. Allow Grazing Eclipses (Impact parameter > 1.0)
    priors_EB['b_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 1.5]} 

    # 3. Allow Large Radius (Stellar Companion)
    # [BINARY MODEL]: The companion can be as large as the host star (p=1.0).
    priors_EB['p_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 1.0]} 

    # RUN BINARY MODEL
    dataset_EB = juliet.load(priors=priors_EB, t_lc=tim, y_lc=fl, yerr_lc=fle, out_folder='results_binary_full')
    results_EB = dataset_EB.fit(sampler='dynesty', nthreads=1)

    # =========================================================================
    #  SECTION 5: FINAL COMPARISON
    # =========================================================================
    print("\n[5/5] FINAL VERDICT")
    
    # Retrieve Log-Evidence (lnZ)
    try:
        lnZ_P = results_P.posteriors['lnZ']
        lnZ_EB = results_EB.posteriors['lnZ']
    except KeyError:
        # Fallback for different juliet versions
        lnZ_P = results_P.posteriors['lnZ_dynesty']
        lnZ_EB = results_EB.posteriors['lnZ_dynesty']

    delta = lnZ_P - lnZ_EB

    print(f"---------------------------------------")
    print(f"Planet Evidence (lnZ_P): {lnZ_P:.2f}")
    print(f"Binary Evidence (lnZ_EB): {lnZ_EB:.2f}")
    print(f"DELTA lnZ (P - EB):      {delta:.2f}")
    print(f"---------------------------------------")
    
    # INTERPRETATION OF RESULTS
    if delta > 5:
        print("RESULT: Strong evidence for PLANET model.")
    elif delta < -5:
        print("RESULT: Strong evidence for ECLIPSING BINARY model.")
    else:
        print("RESULT: Inconclusive (|Delta| < 5).")
        print("        Note: For very shallow/low-SNR signals, this is the expected result.")
        print("        It means the data isn't precise enough to distinguish the shapes.")