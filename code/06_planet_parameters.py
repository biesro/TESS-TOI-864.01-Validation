"""
06_planet_parameters.py
-----------------------
Calculates the final physical parameters of the planet based on the validated transit signal.
Derives Radius, Semi-major axis, and Equilibrium Temperature.

Author: Biel Escolà Rodrigo
Target: TOI 864.01
"""

import numpy as np
from astroquery.mast import Catalogs

# --- 1. INPUT DATA (From Analysis) ---
TIC_ID = "231728511"
PERIOD_DAYS = 0.520667   
DEPTH_PPM = 158.0        
DEPTH_DECIMAL = DEPTH_PPM / 1e6

print(f"🌟 SYSTEM PARAMETERS FOR TIC {TIC_ID}")
print("---------------------------------------------")

# --- 2. RETRIEVING STELLAR DATA ---
print("📡 Retrieving stellar parameters (TIC v8)...")

catalog_data = Catalogs.query_object(f"TIC {TIC_ID}", catalog="TIC")
star_radius = catalog_data[0]['rad']   # Solar Radii
star_mass = catalog_data[0]['mass']    # Solar Masses
star_temp = catalog_data[0]['Teff']    # Kelvin

if np.isnan(star_radius): star_radius = 1.0
if np.isnan(star_mass): star_mass = 1.0
if np.isnan(star_temp): star_temp = 5770

print(f"   Star: R = {star_radius:.3f} R_sol | M = {star_mass:.3f} M_sol | Teff = {star_temp:.0f} K")

# --- 3. PHYSICAL CALCULATIONS ---

# A) PLANETARY RADIUS
# 1 R_sun = 109.076 R_earth
planet_radius_earth = (star_radius * 109.076) * np.sqrt(DEPTH_DECIMAL)

# B) SEMI-MAJOR AXIS (a)
# Kepler's 3rd Law approx
period_years = PERIOD_DAYS / 365.25
a_au = ( (period_years**2) * star_mass )**(1/3)

# C) EQUILIBRIUM TEMPERATURE
# Bond Albedo = 0 assumed
# 1 AU = 215.032 Solar Radii
a_rs = a_au * 215.032
planet_temp_kelvin = star_temp * np.sqrt(star_radius / (2 * a_rs))
planet_temp_celsius = planet_temp_kelvin - 273.15

# --- 4. FINAL REPORT ---
print("\n" + "="*50)
print(f"🪐 PLANETARY PARAMETERS SHEET (TOI 864.01)")
print("="*50)
print(f"📏 RADIUS:        {planet_radius_earth:.2f} R_earth")
print(f"🔥 TEMPERATURE:   {planet_temp_celsius:.0f} °C ({planet_temp_kelvin:.0f} K)")
print(f"🏃 DISTANCE (a):  {a_au:.4f} AU")
print("-" * 50)

print("CLASSIFICATION:")
if planet_radius_earth < 1.2:
    print("🪨 Type: EARTH (Compact Rocky)")
elif planet_radius_earth < 2.0:
    print("🌍 Type: SUPER-EARTH (Likely rocky)")
elif planet_radius_earth < 4.0:
    print("🎈 Type: SUB-NEPTUNE")
else:
    print("💨 Type: GAS GIANT")
print("="*50)
