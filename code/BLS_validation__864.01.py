import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION ---
TIC_ID = "TIC 231728511"
TOI_ID = "TOI 864.01"

# I provide an initial hint to the algorithm, but I will let it search for the precise value
PERIOD_HINT = 0.523 
DURATION_HOURS_HINT = 1.0 

print(f"🔬 I AM STARTING THE SCIENTIFIC ANALYSIS FOR {TOI_ID} ({TIC_ID})")
print("---------------------------------------------------------")

# --- 2. DATA DOWNLOAD AND PROCESSING ---
print("📡 I am connecting to NASA servers (MAST)...")
try:
    # I attempt to download SPOC data (High Quality, 2-min cadence)
    search = lk.search_lightcurve(TIC_ID, author="SPOC", exptime=120)
    if len(search) == 0:
        # If unavailable, I try TESS-SPOC
        search = lk.search_lightcurve(TIC_ID, author="TESS-SPOC")
    
    if len(search) == 0:
        print("❌ High cadence data not found. I am trying QLP data instead...")
        search = lk.search_lightcurve(TIC_ID, author="QLP")

    print(f"   Sectors found: {len(search)}")
    lc_collection = search.download_all()
    
    # Processing steps I am applying:
    # 1. Stitch: I merge all sectors together.
    # 2. Remove Outliers: I remove cosmic rays (sigma=5).
    # 3. Flatten: I remove stellar variability to isolate the transit.
    print("⚙️  I am processing, cleaning, and flattening gigabytes of data...")
    lc_combined = lc_collection.stitch().remove_nans().remove_outliers(sigma=5).flatten(window_length=501)
    print("✅ My data is ready for analysis.")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    exit()

# --- 3. AUTOMATIC PARAMETER SEARCH (BLS) ---
# Here I apply the Box Least Squares (BLS) algorithm to detect the periodic signal
print("\n🔍 I am initiating the automatic signal search (BLS)...")
print("   I am scanning thousands of possible periods to synchronize the transit...")

# I define a high-resolution grid of periods around my initial hint
period_grid = np.linspace(PERIOD_HINT - 0.01, PERIOD_HINT + 0.01, 10000)

# I execute the BLS algorithm on my processed light curve
bls = lc_combined.to_periodogram(method='bls', period=period_grid, duration=DURATION_HOURS_HINT/24)

# I extract the best-fitting parameters found by the algorithm
best_period = bls.period_at_max_power.value
best_t0 = bls.transit_time_at_max_power.value
best_depth = bls.depth_at_max_power.value

print(f"🎯 SYNCHRONIZATION COMPLETED:")
print(f"   Period I detected: {best_period:.6f} days")
print(f"   Epoch (T0) I detected: {best_t0:.4f} BTJD")

# --- 4. SCIENTIFIC SNR CALCULATION ---
# I fold the light curve using the precise parameters I just found
lc_folded = lc_combined.fold(period=best_period, epoch_time=best_t0)

# I define the masks to separate "In-Transit" flux from "Out-of-Transit" flux
duration_phase = (DURATION_HOURS_HINT / 24) / best_period
mask_transit = (np.abs(lc_folded.phase.value) < (duration_phase * 0.5))
mask_out = (np.abs(lc_folded.phase.value) > (duration_phase * 2.0))

# I extract the flux values for the calculation
flux_in = lc_folded.flux[mask_transit]
flux_out = lc_folded.flux[mask_out]

# I calculate the depth and the noise floor in parts per million (ppm)
depth_ppm = (np.nanmedian(flux_out) - np.nanmedian(flux_in)) * 1e6
noise_ppm = np.nanstd(flux_out) * 1e6
n_points = len(flux_in)

# I calculate the final Signal-to-Noise Ratio (SNR)
snr_final = (depth_ppm / noise_ppm) * np.sqrt(n_points)

# --- 5. VISUALIZATION ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

# PLOT 1: I visualize the Primary Transit (Phase 0)
lc_folded.scatter(ax=ax1, color='black', alpha=0.1, s=1, label='Raw Data')
lc_folded.bin(time_bin_size=0.005).plot(ax=ax1, color='red', lw=2, label='My Model (Smoothed)')
ax1.set_title(f'TRANSIT DETECTED\nPeriod: {best_period:.5f} d', fontsize=12, fontweight='bold')
ax1.set_xlim(-0.15, 0.15)
ax1.set_xlabel('Phase [days]')
ax1.set_ylabel('Normalized Flux')
ax1.legend(loc='lower left')
ax1.grid(True, alpha=0.3)

# PLOT 2: I check for Secondary Eclipse (Phase 0.5) to rule out binaries
# I fold the data exactly at half the period
lc_folded_sec = lc_combined.fold(period=best_period, epoch_time=best_t0 + (best_period/2))
lc_folded_sec.scatter(ax=ax2, color='blue', alpha=0.1, s=1, label='Phase 0.5 Data')
lc_folded_sec.bin(time_bin_size=0.005).plot(ax=ax2, color='orange', lw=2, label='Mean Flux')

ax2.set_title(f'FALSE POSITIVE CHECK (Phase 0.5)', fontsize=12, fontweight='bold')
ax2.set_xlim(-0.15, 0.15)
ax2.set_xlabel('Phase [days]')
# I add a green reference line at 1.0
ax2.axhline(1.0, color='green', linestyle='--', lw=2, label='Flux 1.0 (Ideal)')
ax2.legend(loc='lower left')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- 6. FINAL REPORT ---
print("\n" + "="*50)
print(f"📊 MY FINAL SCIENTIFIC REPORT: {TOI_ID}")
print("="*50)

# SOLUCIÓ: Posem float() per convertir la dada complexa en un número normal
print(f"1. True Depth Measured: {float(depth_ppm.value):.2f} ppm")
print(f"2. Background Noise:    {float(noise_ppm.value):.2f} ppm")
print("-" * 30)
print(f"3. SNR (Signal/Noise):  {float(snr_final.value):.2f}")
print("-" * 30)

print("MY INTERPRETATION:")
# Aquí també hem d'assegurar-nos que comparem números normals
if snr_final.value > 7.1:
    print("✅ SUCCESS: SNR > 7.1. I confirm a robust detection.")
    if abs(depth_ppm.value) < 500:
        print("   NOTE: I observe a small depth (<500 ppm), compatible with an Earth/Super-Earth planet.")
else:
    print("⚠️ WARNING: Low SNR. I cannot confirm the signal clearly.")

print("Phase 0.5 Check (Right Graph):")
print("   - Do I see a FLAT orange line? -> CONFIRMED PLANET (Solid candidate).")
print("   - Do I see a DIP? -> ECLIPSING BINARY (False Positive).")
print("="*50)
