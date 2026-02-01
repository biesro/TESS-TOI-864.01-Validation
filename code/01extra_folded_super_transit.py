"""
01_extra_folded_super_transit.py

Description:
    This script generates the high-resolution "Super-Transit" visualization (Panel B in the paper).
    It processes the TESS photometry to create a phase-folded, binned light curve that reveals
    the specific morphology of the transit event.

    Steps:
    1. Downloads high-fidelity SPOC data for the target.
    2. Stitches and detrends the light curve (flattening).
    3. Phase-folds the data using the determined period and epoch.
    4. Bins the data to reduce scatter and compute error bars.
    5. Plots the result using RNAAS-compliant styling.

    Output: 'recreated_panel_A.png'

Author: Biel Escolà Rodrigo
Target: TIC 231728511 (TOI 864.01)
"""

import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u

# --- 1. CONFIGURATION ---
TIC_ID = "TIC 231728511"
PERIOD = 0.52067       # Orbital Period (days)
T0 = 1411.1454         # Epoch (BTJD)
BIN_SIZE_MINS = 10     # Bin size in minutes (Controls data density)

print(f"📥 Downloading data for {TIC_ID}...")

# --- 2. DATA PROCESSING ---
# Download all available sectors. 
# We prioritize SPOC author for the highest quality reduction.
search = lk.search_lightcurve(TIC_ID, mission="TESS", author="SPOC")
lc = search.download_all().stitch()

# Basic cleaning: 
# - remove_nans: Handle missing data.
# - flatten: Removes stellar variability and instrumental trends.
#   CRITICAL: A large window_length (1001) is used to preserve the transit depth 
#   while removing lower frequency trends.
lc_clean = lc.remove_nans().flatten(window_length=1001).remove_outliers(sigma=5)

print("🔄 Folding light curve...")
# Fold the data: Centers the transit at Phase 0.0 based on Ephemeris.
folded_lc = lc_clean.fold(period=PERIOD, epoch_time=T0)

print("📊 Binning data...")
# Binning is essential to visualize the "average" transit shape amidst the noise.
# This calculates the mean flux and error for each time bin.
binned_lc = folded_lc.bin(time_bin_size=BIN_SIZE_MINS * u.min)

# --- 3. PLOTTING (RNAAS Style) ---
print("🎨 Generating plot...")
plt.figure(figsize=(10, 6))

# Plotting with error bars to show statistical significance
plt.errorbar(
    binned_lc.time.value,      # X-Axis: Phase (days)
    binned_lc.flux.value,      # Y-Axis: Normalized Flux
    yerr=binned_lc.flux_err.value, # Error bars derived from binning
    fmt='o',                   # Format: circle markers
    color='steelblue',         # Aesthetic choice matching paper style
    alpha=0.7,                 # Slight transparency for overlapping points
    markersize=5,              
    elinewidth=1.5,            # Width of the error bar lines
    capsize=0,                 # Clean look without caps
    label='Binned Data'        
)

# --- 4. STYLING AND EXPORT ---
plt.title(f"Folded Super-Transit - {TIC_ID}", fontsize=14, fontweight='bold')
plt.xlabel("Phase (days)", fontsize=12)
plt.ylabel("Normalized Flux", fontsize=12)

# Zoom in on the transit event (Window of +/- 0.15 days)
plt.xlim(-0.15, 0.15)

# Force matplotlib to use offset notation (e.g., +1) on the Y-axis
# This makes the scale readable (showing deviations from 1.0)
plt.ticklabel_format(useOffset=True, axis='y')

plt.legend(loc='upper right', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3) # Subtle grid for readability

# Save the final figure
output_filename = "recreated_panel_A.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')

print(f"✅ Success! Image saved as: {output_filename}")
plt.show()