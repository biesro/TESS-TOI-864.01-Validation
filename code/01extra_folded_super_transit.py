import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u

# --- 1. PARÀMETRES DEL SISTEMA (TOI 864.01) ---
TIC_ID = "TIC 231728511"
PERIOD = 0.52067       # Dies
T0 = 1411.1454         # Època (BTJD)
BIN_SIZE_MINS = 10     # Minuts per bin (Ajusta-ho per tenir més o menys punts)

print(f"📥 Descarregant dades per {TIC_ID}...")

# --- 2. DESCÀRREGA I PROCESSAMENT ---
# Descarreguem tots els sectors disponibles (SPOC) i els unim (stitch)
search = lk.search_lightcurve(TIC_ID, mission="TESS", author="SPOC")
lc = search.download_all().stitch()

# Neteja bàsica: treure NaNs i aplanar (flatten) per treure variabilitat estel·lar
# window_length gran per no "aixafar" el trànsit, però suficient per aplanar
lc_clean = lc.remove_nans().flatten(window_length=1001).remove_outliers(sigma=5)

print("🔄 Plegant la corba de llum...")
# Pleguem la corba de llum amb el període i T0
folded_lc = lc_clean.fold(period=PERIOD, epoch_time=T0)

print("📊 Agrupant dades (Binning)...")
# Fem el "binning" per aconseguir els punts amb barres d'error (com a la imatge)
# Això redueix el soroll i mostra la tendència clara
binned_lc = folded_lc.bin(time_bin_size=BIN_SIZE_MINS * u.min)

# --- 3. GENERACIÓ DEL GRÀFIC (Estil RNAAS) ---
plt.figure(figsize=(10, 6))

# Dibuixem els punts amb barres d'error
plt.errorbar(
    binned_lc.time.value,      # Eix X: Fase
    binned_lc.flux.value,      # Eix Y: Flux
    yerr=binned_lc.flux_err.value, # Barres d'error
    fmt='o',                   # Format: punts rodons
    color='steelblue',         # Color blau acer (similar a la teva imatge)
    alpha=0.7,                 # Una mica transparent
    markersize=5,              # Mida del punt
    elinewidth=1.5,            # Gruix de la línia d'error
    capsize=0,                 # Sense remats a les barres d'error
    label='Binned Data'        # Llegenda
)

# --- 4. ESTIL I ETIQUETES ---
plt.title(f"Folded Super-Transit - {TIC_ID}", fontsize=14, fontweight='bold')
plt.xlabel("Phase (days)", fontsize=12)
plt.ylabel("Normalized Flux", fontsize=12)

# Límits exactes de la teva imatge (-0.15 a +0.15 dies)
plt.xlim(-0.15, 0.15)

# Forçar que matplotlib mostri el "+1" a dalt a l'esquerra (offset)
# (Això ho fa automàticament si els valors són propers a 1, però podem ajustar el format)
plt.ticklabel_format(useOffset=True, axis='y')

plt.legend(loc='upper right', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3) # Reixa suau de fons

# Guardar i mostrar
output_filename = "recreated_panel_A.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"✅ Imatge guardada com: {output_filename}")
plt.show()