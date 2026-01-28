"""
02_centroid_test.py
-------------------
Performs a centroid shift analysis to rule out background false positives.
It calculates the center of light for each frame and checks for movement correlated with the transit.

Author: Biel Escolà Rodrigo
Target: TOI 864.01
"""

import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION ---
TIC_ID = "TIC 231728511"
KNOWN_PERIOD = 0.520667
KNOWN_T0 = 1411.1454 

print(f"🕵️‍♀️ STARTING CENTROID TEST FOR {TIC_ID}")

try:
    print("📡 Downloading Sector 27 Target Pixel File (TPF)...")
    # Using Sector 27 as reference
    tpf = lk.search_targetpixelfile(TIC_ID, author="SPOC", sector=27).download()
    
    if tpf is None:
        print("❌ Could not download TPF. Exiting.")
        exit()

    print("⚙️  Calculating center of light (Centroids)...")
    
    # 1. Create light curve
    lc = tpf.to_lightcurve(aperture_mask=tpf.pipeline_mask).remove_nans().flatten()
    
    # 2. Calculate X/Y positions
    centroids = tpf.estimate_centroids()
    centroid_col = centroids[0].value # X
    centroid_row = centroids[1].value # Y
    
    # 3. Create LightCurves for position
    lc_centroid_col = lk.LightCurve(time=lc.time, flux=centroid_col)
    folded_col = lc_centroid_col.fold(period=KNOWN_PERIOD, epoch_time=KNOWN_T0)
    
    lc_centroid_row = lk.LightCurve(time=lc.time, flux=centroid_row)
    folded_row = lc_centroid_row.fold(period=KNOWN_PERIOD, epoch_time=KNOWN_T0)
    
    # --- VISUALIZATION ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # GRAPH 1: X Axis
    folded_col.scatter(ax=ax1, s=1, alpha=0.3, c='gray')
    folded_col.bin(time_bin_size=0.01).plot(ax=ax1, c='red', lw=3, label='Mean Movement')
    ax1.set_title("Centroid Movement (X Axis - Columns)", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Pixels")
    ax1.set_xlim(-0.1, 0.1) 
    
    # GRAPH 2: Y Axis
    folded_row.scatter(ax=ax2, s=1, alpha=0.3, c='gray')
    folded_row.bin(time_bin_size=0.01).plot(ax=ax2, c='blue', lw=3, label='Mean Movement')
    ax2.set_title("Centroid Movement (Y Axis - Rows)", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Pixels")
    ax2.set_xlim(-0.1, 0.1)

    plt.suptitle(f"CENTROID VALIDATION - {TIC_ID}", fontsize=16)
    plt.tight_layout()
    plt.show()

    print("\n" + "="*50)
    print("📊 RESULT INTERPRETATION")
    print("="*50)
    print("✅ Flat lines? -> Transit is on-target (Real).")
    print("❌ 'U' or 'V' shapes? -> False Positive (Background Star).")
    print("="*50)

except Exception as e:
    print(f"❌ Error during analysis: {e}")
