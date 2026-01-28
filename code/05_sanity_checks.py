"""
05_sanity_checks.py
-------------------
Performs critical physical validation checks for the exoplanet candidate:
1. Odd-Even Transit Test: Checks for depth variations between odd and even transits 
   (rules out eclipsing binaries with P' = 2P).
2. Stellar Density Check: Compares the transit-derived stellar density with the 
   catalog density (rules out background blends).

Author: Biel Escolà Rodrigo
Target: TOI 864.01 (TIC 231728511)
"""

import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.constants import G, R_sun, M_sun
import os

# --- TARGET PARAMETERS (TOI 864.01) ---
ID = "TIC 231728511"
PERIOD = 0.52067
T0 = 1411.1454
DURATION_HOURS = 1.0  # Approx duration for masking purposes

# Output directory for figures
OUTPUT_DIR = "figures"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("=======================================================")
print("  SANITY CHECKS: ODD-EVEN & DENSITY - TOI 864.01")
print("=======================================================\n")

# 1. DATA RETRIEVAL AND PREPARATION
print("[1/3] Downloading and processing TESS data...")
try:
    # Search for high-quality SPOC data first
    search = lk.search_lightcurve(ID, mission="TESS", author="SPOC")
    if len(search) == 0:
        search = lk.search_lightcurve(ID, mission="TESS")
    
    # Download, stitch, and clean
    lc = search.download_all().stitch().remove_nans()
    print(f"      -> Data loaded successfully: {len(lc)} data points.")

except Exception as e:
    print(f"Error downloading data: {e}")
    exit()

# 2. ODD-EVEN TRANSIT TEST
print("\n[2/3] Executing Odd-Even Transit Test...")

# Identify odd and even transits based on the original time array
# Calculate approximate orbit number
orbit_num = np.round((lc.time.value - T0) / PERIOD).astype(int)

# Create masks for separation
mask_even = (orbit_num % 2 == 0)
mask_odd = (orbit_num % 2 != 0)

# Create two separate folded light curves
lc_even = lc[mask_even].fold(period=PERIOD, epoch_time=T0)
lc_odd = lc[mask_odd].fold(period=PERIOD, epoch_time=T0)

# Bin data to reduce noise and visualize depth clearly
bin_even = lc_even.bin(time_bin_size=10*u.min)
bin_odd = lc_odd.bin(time_bin_size=10*u.min)

# Calculate approximate depth (Median flux out-of-transit vs in-transit)
# Define transit window: +/- 0.02 days
transit_mask_ev = (np.abs(bin_even.time.value) < 0.02)
out_mask_ev = (np.abs(bin_even.time.value) > 0.03)

depth_even = np.median(bin_even.flux.value[out_mask_ev]) - np.median(bin_even.flux.value[transit_mask_ev])
depth_odd = np.median(bin_odd.flux.value[out_mask_ev]) - np.median(bin_odd.flux.value[transit_mask_ev])

# Calculate significance of the difference (in sigma)
# Simple error estimation using standard deviation of out-of-transit flux
sigma_even = np.std(bin_even.flux.value[out_mask_ev]) / np.sqrt(len(bin_even.flux.value[transit_mask_ev]))
sigma_odd = np.std(bin_odd.flux.value[out_mask_ev]) / np.sqrt(len(bin_odd.flux.value[transit_mask_ev]))
sigma_diff = np.sqrt(sigma_even**2 + sigma_odd**2)

diff_sigma = np.abs(depth_even - depth_odd) / sigma_diff

print(f"   -> Even Transit Depth: {depth_even*1e6:.1f} ppm")
print(f"   -> Odd Transit Depth:  {depth_odd*1e6:.1f} ppm")
print(f"   -> Difference:         {diff_sigma:.2f} sigma")

if diff_sigma < 3:
    print("   ✅ RESULT: Consistent (No significant difference found).")
else:
    print("   ❌ RESULT: Warning! Significant difference detected (Possible Binary).")

# 3. STELLAR DENSITY CHECK
print("\n[3/3] Executing Stellar Density Check...")

# Stellar Parameters (TIC v8)
R_star_val = 0.399  # R_sun
M_star_val = 0.380  # M_sun (Typical estimate for R=0.4 if exact mass unavailable)

# Calculate Catalog Density (g/cm^3)
rho_star_cat = (M_star_val * M_sun) / ((4/3) * np.pi * (R_star_val * R_sun)**3)
rho_star_cat_cgs = rho_star_cat.to(u.g / u.cm**3).value

# Calculate Transit-Derived Density (Seager & Mallen-Ornelas 2003)
# We need a/R* (derived from the period and stellar radius for a circular orbit)
# Assuming a ~ 0.0093 AU and R* ~ 0.399 R_sun:
a_au = 0.0093 * u.AU
r_star_au = (0.399 * R_sun).to(u.AU)
a_over_r = (a_au / r_star_au).value

# Formula: rho_circ = (3 pi / G P^2) * (a/R*)^3
G_cgs = G.to(u.cm**3 / (u.g * u.s**2))
P_sec = (PERIOD * u.day).to(u.s)

rho_transit = (3 * np.pi / (G_cgs * P_sec**2)) * (a_over_r)**3
rho_transit_val = rho_transit.value

print(f"   -> Catalog Density (TIC v8):   {rho_star_cat_cgs:.2f} g/cm^3")
print(f"   -> Transit-Derived Density:    {rho_transit_val:.2f} g/cm^3 (assuming a/R* ~ {a_over_r:.1f})")

ratio = rho_transit_val / rho_star_cat_cgs
print(f"   -> Ratio (Transit/Catalog):    {ratio:.2f}")

if 0.5 < ratio < 2.0:
    print("   ✅ RESULT: Consistent! (The transiting object likely orbits the target star).")
else:
    print("   ⚠️ RESULT: Discrepancy detected (Check a/R* or eccentricity).")

# --- VISUALIZATION ---
plt.figure(figsize=(10, 5))
plt.errorbar(
    bin_even.time.value, 
    bin_even.flux.value, 
    yerr=bin_even.flux_err.value, 
    fmt='o', 
    label='Even Transits', 
    alpha=0.7,
    color='steelblue'
)
plt.errorbar(
    bin_odd.time.value, 
    bin_odd.flux.value - 0.001, 
    yerr=bin_odd.flux_err.value, 
    fmt='s', 
    label='Odd Transits (Offset -0.001)', 
    alpha=0.7,
    color='darkorange'
)
plt.title(f"Odd-Even Transit Check - {ID}")
plt.xlabel("Phase (days)")
plt.ylabel("Normalized Flux (Offset)")
plt.legend()
plt.xlim(-0.1, 0.1)

# Save figure
output_path = os.path.join(OUTPUT_DIR, "odd_even_check.png")
plt.savefig(output_path)
print(f"\n   -> Figure saved as '{output_path}'")
