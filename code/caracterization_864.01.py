import numpy as np
from astroquery.mast import Catalogs

# --- 1. INPUT OF DATA OBTAINED FROM MY ANALYSIS ---
TIC_ID = "231728511"
PERIOD_DAYS = 0.520667   # The period I identified in the BLS analysis
DEPTH_PPM = 158.0        # The transit depth measured in my analysis
DEPTH_DECIMAL = DEPTH_PPM / 1e6

print(f"🌟 SYSTEM CHARACTERIZATION FOR TIC {TIC_ID}")
print("---------------------------------------------")

# --- 2. RETRIEVING STELLAR DATA (TIC CATALOG) ---
print("📡 Connecting to TESS stellar catalog (TIC v8)...")

# I query the database to get the specific parameters of the host star
catalog_data = Catalogs.query_object(f"TIC {TIC_ID}", catalog="TIC")
star_radius = catalog_data[0]['rad']   # Radius in Solar Radii
star_mass = catalog_data[0]['mass']    # Mass in Solar Masses
star_temp = catalog_data[0]['Teff']    # Effective Temperature in Kelvin

# If data is missing (NaN), I assume Solar values as a first approximation
if np.isnan(star_radius): star_radius = 1.0
if np.isnan(star_mass): star_mass = 1.0
if np.isnan(star_temp): star_temp = 5770

print(f"   Star: Radius = {star_radius:.3f} R_sol | Mass = {star_mass:.3f} M_sol | Temp = {star_temp:.0f} K")

# --- 3. PHYSICAL CALCULATIONS OF THE PLANET ---

# A) PLANETARY RADIUS
# Formula used: Rp = R_star * sqrt(Depth)
# Conversion factor: 1 Solar Radius = 109.076 Earth Radii
planet_radius_earth = (star_radius * 109.076) * np.sqrt(DEPTH_DECIMAL)

# B) DISTANCE TO THE STAR (Semi-major axis 'a')
# I apply Kepler's 3rd Law (approximation)
# a (in AU) = cube_root( (P_years^2) * Star_Mass )
period_years = PERIOD_DAYS / 365.25
a_au = ( (period_years**2) * star_mass )**(1/3)

# C) EQUILIBRIUM TEMPERATURE (Planet Surface)
# I assume Bond Albedo = 0 (the planet absorbs all heat, like dark rock)
# Teq = T_star * sqrt(R_star / 2a)
# I convert 'a' from AU to Solar Radii for the formula (1 AU = 215.032 Solar Radii)
a_rs = a_au * 215.032
planet_temp_kelvin = star_temp * np.sqrt(star_radius / (2 * a_rs))
planet_temp_celsius = planet_temp_kelvin - 273.15

# --- 4. FINAL REPORT GENERATION ---
print("\n" + "="*50)
print(f"🪐 PLANETARY TECHNICAL SHEET (TOI 864.01)")
print("="*50)
print(f"📏 PLANETARY RADIUS:     {planet_radius_earth:.2f} x Earth")
print(f"🔥 ESTIMATED TEMPERATURE: {planet_temp_celsius:.0f} °C ({planet_temp_kelvin:.0f} K)")
print(f"🏃 DISTANCE (AU):       {a_au:.4f} AU (Extremely close!)")
print("-" * 50)

print("INTERPRETATION:")
if planet_radius_earth < 1.2:
    print("🪨 Type: EARTH (Compact Rocky)")
elif planet_radius_earth < 2.0:
    print("🌍 Type: SUPER-EARTH (Likely rocky)")
elif planet_radius_earth < 4.0:
    print("🎈 Type: SUB-NEPTUNE (Rocky core with gas atmosphere)")
else:
    print("💨 Type: GAS GIANT")

if planet_temp_celsius > 1000:
    print("🌋 Environment: LAVA WORLD (Surface rock is likely molten)")
elif planet_temp_celsius > 100:
    print("🧖 Environment: OVEN (Too hot for life)")
else:
    print("💧 Environment: TEMPERATE (Liquid water possible?)")
print("="*50)