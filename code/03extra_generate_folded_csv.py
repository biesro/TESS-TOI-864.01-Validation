"""
03_extra_generate_folded_csv.py

Description:
    This utility script prepares the light curve data for the Triceratops validation tool.
    It performs the following steps:
    1. Downloads high-quality SPOC data for all available sectors.
    2. Stitches (combines) and normalizes the sectors.
    3. Phase-folds the data based on the known orbital period and epoch.
    4. Bins the data to reduce noise and computational load.
    5. Exports the processed data to a CSV file (Time vs Flux) centered at 0.

    Output: 'TOI864_01_ALL_SECTORS_FOLDED.csv'

Author: Biel Escolà Rodrigo
Target: TIC 231728511
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lightkurve import search_lightcurve, LightCurveCollection

# --- 1. CONFIGURATION ---
TIC_ID = 231728511
P_ORB = 0.52067           # Orbital Period (days)
T0 = 1411.1454  # Epoch (BTJD) - Converted from BJD if necessary

# List of sectors with confirmed data availability
SECTORS_LIST = [4, 5, 6, 27, 31, 32, 33, 37, 64, 67, 87, 94]

print(f"🚀 Starting download and stitching for {len(SECTORS_LIST)} sectors...")

lc_list = []

# --- 2. DATA RETRIEVAL LOOP ---
for sector in SECTORS_LIST:
    try:
        # Search for light curves (Mission: TESS)
        search = search_lightcurve(f"TIC {TIC_ID}", mission="TESS", sector=sector)
        if len(search) == 0: continue
            
        # Prioritize SPOC (Science Processing Operations Center) data 
        # as it is the official high-fidelity NASA pipeline.
        if "SPOC" in search.author:
            lc_file = search[search.author == "SPOC"][0].download()
        else:
            # Fallback to whatever is available (e.g., QLP, TESS-SPOC)
            lc_file = search[0].download()
            
        if lc_file is None: continue

        # Basic cleaning for each sector
        # - remove_nans: Remove empty values
        # - normalize: Put flux on relative scale (around 1.0)
        # - remove_outliers: Remove cosmic rays (5 sigma)
        lc_clean = lc_file.remove_nans().normalize().remove_outliers(sigma=5)
        lc_list.append(lc_clean)
        
        print(f"   ✅ Sector {sector} added.")
        
    except Exception as e:
        print(f"   ⚠️ Error processing Sector {sector}: {e}")

# --- 3. STITCHING ---
print("🧵 Stitching all sectors into a single light curve...")
lc_collection = LightCurveCollection(lc_list)
lc_stitched = lc_collection.stitch() # Normalizes and merges all sectors

# --- 4. FOLDING AND BINNING ---
print("🔄 Folding and binning the combined light curve...")

# Step 1: Fold the data
# This centers the transit at Phase 0.0 based on P_ORB and T0.
lc_folded_raw = lc_stitched.fold(period=P_ORB, epoch_time=T0)

# Step 2: CRITICAL - Binning
# With 12 sectors, the raw data is too dense and noisy for rapid statistical validation.
# We bin the data into 5-minute intervals.
# Calculation: 5 mins / 1440 mins_per_day = 0.00347 days
lc_folded_binned = lc_folded_raw.bin(time_bin_size=5/1440) 

# Step 3: CRITICAL - Unit Conversion (Phase -> Days)
# Lightkurve returns 'phase' (dimensionless, -0.5 to 0.5). 
# Triceratops expects time units (days relative to transit center).
time_in_days = lc_folded_binned.time.value * P_ORB
flux_val = lc_folded_binned.flux.value
flux_err = lc_folded_binned.flux_err.value

# --- 5. EXPORT TO CSV ---
df = pd.DataFrame({
    'time': time_in_days,  # Now in days, centered at 0.0
    'flux': flux_val,
    'flux_err': flux_err
})

# Save without header (header=False) to match the format expected by Triceratops
filename = "TOI864_01_ALL_SECTORS_FOLDED.csv"
df.to_csv(filename, index=False, header=False)

print(f"\n🎉 SUCCESS! File '{filename}' generated.")
print(f"   - Original points: {len(lc_folded_raw)}")
print(f"   - Final points (binned): {len(df)} (Optimized for Triceratops)")

# --- 6. VISUAL VERIFICATION (OPTIONAL) ---
plt.figure(figsize=(10,5))
plt.scatter(df['time'], df['flux'], s=5, alpha=0.7, c='black')
plt.xlim(-0.1, 0.1) # Zoom in on the transit event (center)
plt.title("Preview of Generated CSV (Zoom on Transit)")
plt.xlabel("Days from mid-transit")
plt.ylabel("Normalized Flux")
plt.grid(True, alpha=0.3)
plt.show()