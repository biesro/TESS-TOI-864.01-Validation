"""
04_juliet_model_comparison.py
-----------------------------
Performs a Bayesian model comparison using 'juliet' to distinguish between
a Planetary Model and an Eclipsing Binary (EB) Model.
It uses Nested Sampling (Dynesty) to calculate the Bayesian Evidence (lnZ).

Author: Biel Escolà Rodrigo
Target: TOI 864.01
"""

import os
import sys

# --- WINDOWS MULTIPROCESSING FIX ---
if 'HOME' not in os.environ:
    os.environ['HOME'] = os.environ['USERPROFILE']

import juliet
import numpy as np
import lightkurve as lk
import matplotlib.pyplot as plt
import astropy.units as u

# --- GLOBAL VARIABLES ---
ID = "TIC 231728511"
P_PERIOD = 0.52067
T0_OLD = 1411.1454 

if __name__ == '__main__':
    
    print("=================================================================")
    print("  ROBUST VALIDATION (MULTI-SECTOR) - TOI 864.01")
    print("=================================================================")

    # 1. DOWNLOAD AND PROCESS DATA
    print("\n[1/5] Downloading ALL TESS sectors...")
    try:
        # Cerca inicial
        search_result = lk.search_lightcurve(ID, mission="TESS", author="SPOC")
        if len(search_result) == 0: 
            search_result = lk.search_lightcurve(ID, mission="TESS")
        
        # --- BLOC DE COMPROVACIÓ (FILES vs SECTORS) ---
        import re
        unique_sectors = set()
        
        # Iterem per cada resultat trobat per extreure el número de sector real
        for mission_name in search_result.mission:
            # Busquem el patró "Sector XX"
            match = re.search(r'Sector\s+(\d+)', str(mission_name))
            if match:
                unique_sectors.add(int(match.group(1)))
        
        num_files = len(search_result)
        num_real_sectors = len(unique_sectors)
        
        print(f"       -> REPORT: Found {num_files} data files.")
        print(f"       -> REALITY: Covering {num_real_sectors} unique TESS Sectors.")
        
        if num_files > num_real_sectors:
            print(f"          (Info: {num_files - num_real_sectors} sectors are split into multiple files. Combining them now...)")
        elif num_files == num_real_sectors:
            print(f"          (Perfect match: 1 file per sector)")
            
        print(f"       -> Stitching data...")
        # -----------------------------------------------

        lc_raw = search_result.download_all().stitch().remove_nans()
        
        # FOLDING + BINNING
        lc_folded = lc_raw.fold(period=P_PERIOD, epoch_time=T0_OLD)
        lc_binned = lc_folded.bin(time_bin_size=5*u.min)
        lc_final = lc_binned.remove_nans()

        # Extract values for Juliet
        times = lc_final.time.value 
        flux = lc_final.flux.value
        flux_err = lc_final.flux_err.value
        
        print(f"       -> Data processed successfully. Points available: {len(times)}")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Prepare dictionaries
    tim, fl, fle = {}, {}, {}
    tim['TESS'] = np.array(times)
    fl['TESS'] = np.array(flux)
    fle['TESS'] = np.array(flux_err)

    # 2. CONFIGURE PLANET MODEL
    print("\n[2/5] Configuring Priors...")
    priors = {}

    # Fixed Period and T0 (since data is folded)
    priors['P_p1'] = {'distribution': 'fixed', 'hyperparameters': P_PERIOD}
    priors['t0_p1'] = {'distribution': 'uniform', 'hyperparameters': [-0.01, 0.01]}
    
    # Planet Parameters
    priors['a_p1'] = {'distribution': 'uniform', 'hyperparameters': [2.0, 15.0]} 
    priors['p_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 0.15]} 
    priors['b_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 0.9]} 
    priors['ecc_p1'] = {'distribution': 'fixed', 'hyperparameters': 0.0}
    priors['omega_p1'] = {'distribution': 'fixed', 'hyperparameters': 90.0}

    # Instrument
    priors['dilution_TESS'] = {'distribution': 'fixed', 'hyperparameters': 1.0} 
    priors['mdilution_TESS'] = {'distribution': 'fixed', 'hyperparameters': 0.0}
    priors['mflux_TESS'] = {'distribution': 'normal', 'hyperparameters': [0.0, 0.1]}
    priors['sigma_w_TESS'] = {'distribution': 'loguniform', 'hyperparameters': [0.1, 1000]}

    # 3. RUN PLANET MODEL
    print("\n[3/5] Running PLANET Model...")
    dataset_P = juliet.load(priors=priors, t_lc=tim, y_lc=fl, yerr_lc=fle, out_folder='results_planet_full')
    results_P = dataset_P.fit(sampler='dynesty', nthreads=1) 

    # 4. RUN BINARY MODEL
    print("\n[4/5] Running BINARY Model (EB)...")
    priors_EB = priors.copy()
    # Relax eccentricity and impact parameter for EB
    priors_EB['ecc_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 0.8]}
    priors_EB['omega_p1'] = {'distribution': 'uniform', 'hyperparameters': [-180, 180]}
    priors_EB['b_p1'] = {'distribution': 'uniform', 'hyperparameters': [0.0, 1.5]} 

    dataset_EB = juliet.load(priors=priors_EB, t_lc=tim, y_lc=fl, yerr_lc=fle, out_folder='results_binary_full')
    results_EB = dataset_EB.fit(sampler='dynesty', nthreads=1)

    # 5. RESULTS
    print("\n[5/5] FINAL VERDICT")
    lnZ_P = results_P.posteriors['lnZ']
    lnZ_EB = results_EB.posteriors['lnZ']
    delta = lnZ_P - lnZ_EB

    print(f"---------------------------------------")
    print(f"Planet Evidence (lnZ_P): {lnZ_P:.2f}")
    print(f"Binary Evidence (lnZ_EB): {lnZ_EB:.2f}")
    print(f"DELTA lnZ:               {delta:.2f}")
    print(f"---------------------------------------")
