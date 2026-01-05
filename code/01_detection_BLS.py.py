"""
01_detection_BLS.py
-------------------
Performs the initial detection of the transit signal using the Box Least Squares (BLS) algorithm.
This script downloads TESS SPOC data, cleans the light curve, and searches for periodic signals.

Author: Biel Escolà Rodrigo
Target: TOI 864.01 (TIC 231728511)
"""

import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION ---
TIC_ID = "TIC 231728511"
TOI_ID = "TOI 864.01"

# Initial hints for the search (broad range)
PERIOD_HINT = 0.523 
DURATION_HOURS_HINT = 1.0 

print(f"🔬 STARTING SCIENTIFIC ANALYSIS FOR {TOI_ID} ({TIC_ID})")
print("---------------------------------------------------------")

# --- 2. DATA DOWNLOAD AND PROCESSING ---
print("📡 Connecting to MAST servers...")
try:
    # Attempt to download SPOC data (High Quality, 2-min cadence)
    search = lk.search_lightcurve(TIC_ID, author="SPOC", exptime=120)
    if len(search) == 0:
        # Fallback to TESS-SPOC
        search = lk.search_lightcurve(TIC_ID, author="TESS-SPOC")
    
    if len(search) == 0:
        print("❌ High cadence data not found. Trying QLP data...")
        search = lk.search_lightcurve(TIC_ID, author="QLP")

    print(f"   Sectors found: {len(search)}")
    lc_collection = search.download_all()
    
    # Processing steps:
    # 1. Stitch: Merge all sectors.
    # 2. Remove Outliers: Sigma clipping (sigma=5).
    # 3. Flatten: Remove stellar variability.
    print("⚙️  Processing, cleaning, and flattening light curve...")
    lc_combined = lc_collection.stitch().remove_nans().remove_outliers(sigma=5).flatten(window_length=501)
    print("✅ Data ready for analysis.")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    exit()

# --- 3. AUTOMATIC PARAMETER SEARCH (BLS) ---
print("\n🔍 Initiating automatic signal search (BLS)...")
print("   Scanning period grid...")

# Define high-resolution grid
period_grid = np.linspace(PERIOD_HINT - 0.01, PERIOD_HINT + 0.01, 10000)

# Execute BLS
bls = lc_combined.to_periodogram(method='bls', period=period_grid, duration=DURATION_HOURS_HINT/24)

# Extract best-fit parameters
best_period = bls.period_at_max_power.value
best_t0 = bls.transit_time_at_max_power.value
best_depth = bls.depth_at_max_power.value

print(f"🎯 SYNCHRONIZATION COMPLETE:")
print(f"   Detected Period: {best_period:.6f} days")
print(f"   Detected Epoch (T0): {best_t0:.4f} BTJD")

# --- 4. SNR CALCULATION ---
# Fold light curve
lc_folded = lc_combined.fold(period=best_period, epoch_time=best_t0)

# Masks for In-Transit vs Out-of-Transit
duration_phase = (DURATION_HOURS_HINT / 24) / best_period
mask_transit = (np.abs(lc_folded.phase.value) < (duration_phase * 0.5))
mask_out = (np.abs(lc_folded.phase.value) > (duration_phase * 2.0))

# Flux extraction
flux_in = lc_folded.flux[mask_transit]
flux_out = lc_folded.flux[mask_out]

# Calculate depth and noise in ppm
depth_ppm = (np.nanmedian(flux_out) - np.nanmedian(flux_in)) * 1e6
noise_ppm = np.nanstd(flux_out) * 1e6
n_points = len(flux_in)

# Calculate SNR
snr_final = (depth_ppm / noise_ppm) * np.sqrt(n_points)

# --- 5. VISUALIZATION ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

# PLOT 1: Primary Transit
lc_folded.scatter(ax=ax1, color='black', alpha=0.1, s=1, label='Raw Data')
lc_folded.bin(time_bin_size=0.005).plot(ax=ax1, color='red', lw=2, label='Model (Smoothed)')
ax1.set_title(f'TRANSIT DETECTED\nPeriod: {best_period:.5f} d', fontsize=12, fontweight='bold')
ax1.set_xlim(-0.15, 0.15)
ax1.set_xlabel('Phase [days]')
ax1.set_ylabel('Normalized Flux')
ax1.legend(loc='lower left')
ax1.grid(True, alpha=0.3)

# PLOT 2: Secondary Eclipse Check (Phase 0.5)
lc_folded_sec = lc_combined.fold(period=best_period, epoch_time=best_t0 + (best_period/2))
lc_folded_sec.scatter(ax=ax2, color='blue', alpha=0.1, s=1, label='Phase 0.5 Data')
lc_folded_sec.bin(time_bin_size=0.005).plot(ax=ax2, color='orange', lw=2, label='Mean Flux')

ax2.set_title(f'FALSE POSITIVE CHECK (Phase 0.5)', fontsize=12, fontweight='bold')
ax2.set_xlim(-0.15, 0.15)
ax2.set_xlabel('Phase [days]')
ax2.axhline(1.0, color='green', linestyle='--', lw=2, label='Flux 1.0 (Ideal)')
ax2.legend(loc='lower left')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- 6. FINAL REPORT ---
print("\n" + "="*50)
print(f"📊 FINAL DETECTION REPORT: {TOI_ID}")
print("="*50)

print(f"1. Measured Depth:    {float(depth_ppm.value):.2f} ppm")
print(f"2. Background Noise:  {float(noise_ppm.value):.2f} ppm")
print("-" * 30)
print(f"3. SNR (Signal/Noise): {float(snr_final.value):.2f}")
print("-" * 30)

print("INTERPRETATION:")
if snr_final.value > 7.1:
    print("✅ SUCCESS: SNR > 7.1. Robust detection confirmed.")
    if abs(depth_ppm.value) < 500:
        print("   NOTE: Small depth (<500 ppm) observed, compatible with Earth/Super-Earth.")
else:
    print("⚠️ WARNING: Low SNR. Signal cannot be clearly confirmed.")

print("="*50)