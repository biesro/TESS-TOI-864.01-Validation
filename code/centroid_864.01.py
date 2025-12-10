import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION ---
TIC_ID = "TIC 231728511"
KNOWN_PERIOD = 0.520667  # The period I identified in the BLS analysis
KNOWN_T0 = 1411.1454     # The epoch I identified (BTJD)

print(f"🕵️‍♀️ I AM STARTING THE CENTROID TEST FOR {TIC_ID}")

try:
    print("📡 I am downloading Sector 27 images...")
    # I specifically search for the TPF of sector 27 to avoid warnings and ensure I get the right data
    tpf = lk.search_targetpixelfile(TIC_ID, author="SPOC", sector=27).download()
    
    if tpf is None:
        print("❌ I could not download the TPF. Exiting.")
        exit()

    print("⚙️  I am calculating the center of light (Centroid) frame by frame...")
    
    # 1. I create the light curve (flux) from the pixel file
    lc = tpf.to_lightcurve(aperture_mask=tpf.pipeline_mask).remove_nans().flatten()
    
    # 2. I calculate the X (Column) and Y (Row) positions of the center of light for every frame
    centroids = tpf.estimate_centroids()
    centroid_col = centroids[0].value # X Coordinate
    centroid_row = centroids[1].value # Y Coordinate
    
    # --- KEY STEP: I create Temporal LightCurves for position and then fold them ---

    # 3. I create a LightCurve object using the X position as flux
    lc_centroid_col = lk.LightCurve(time=lc.time, flux=centroid_col)
    # 4. I fold this position curve using my known period
    folded_col = lc_centroid_col.fold(period=KNOWN_PERIOD, epoch_time=KNOWN_T0)
    
    # 5. I create a LightCurve object using the Y position as flux
    lc_centroid_row = lk.LightCurve(time=lc.time, flux=centroid_row)
    # 6. I fold this position curve as well
    folded_row = lc_centroid_row.fold(period=KNOWN_PERIOD, epoch_time=KNOWN_T0)
    
    # --- VISUALIZATION ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # GRAPH 1: I plot the movement in X
    folded_col.scatter(ax=ax1, s=1, alpha=0.3, c='gray')
    folded_col.bin(time_bin_size=0.01).plot(ax=ax1, c='red', lw=3, label='Mean Movement')
    ax1.set_title("Centroid Movement (X Axis - Columns)", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Pixels")
    ax1.set_xlim(-0.1, 0.1) 
    
    # GRAPH 2: I plot the movement in Y
    folded_row.scatter(ax=ax2, s=1, alpha=0.3, c='gray')
    folded_row.bin(time_bin_size=0.01).plot(ax=ax2, c='blue', lw=3, label='Mean Movement')
    ax2.set_title("Centroid Movement (Y Axis - Rows)", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Pixels")
    ax2.set_xlim(-0.1, 0.1)

    plt.suptitle(f"CENTROID VALIDATION - {TIC_ID}", fontsize=16)
    plt.tight_layout()
    plt.show()

    print("\n" + "="*50)
    print("📊 MY RESULT INTERPRETATION")
    print("="*50)
    print("✅ Do I see flat lines? -> The transit is real, in-situ.")
    print("❌ Do I see 'U' or 'V' shapes? -> False Positive from background star.")
    print("="*50)

except Exception as e:
    print(f"❌ Error during my analysis: {e}")