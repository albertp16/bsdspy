# bsdspy 🚧

**BSDSPY** is a Python library for computing seismic site factors and response spectra based on **NSCP 2015** (National Structural Code of the Philippines), **ACI 318-19**, and DPWH standards.  
Designed for internal use at APEC, it helps ensure quick and consistent seismic calculations—particularly for building designs within the Philippines.

---

## Features
- **SeismicSiteFactor** class that calculates site-specific factors based on ground type (I, II, or III).
- Methods to interpolate site factors for varying PGA (Peak Ground Acceleration) values.
- Extensible framework for additional seismic or structural design utilities.

---

## Installation

1. **Install from PyPI** (if/when publicly available):
   ```bash
   pip install bsdspy

from bsdspy.bsds import SeismicSiteFactor

# Create a SeismicSiteFactor instance with ground type "II"
site_factor_calc = SeismicSiteFactor(ground_type="II")

# Interpolate site factor at a given PGA, say 0.15g
pga_value = 0.15
sf = site_factor_calc.interpolate_site_factor(pga_value)

print(f"For ground type II and PGA={pga_value}, the site factor is {sf}.")
