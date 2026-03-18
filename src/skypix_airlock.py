import sqlite3
import math
from datetime import date

def calculate_marginal_shading(ra_deg, lng):
    """
    Calculates 12 months of observability.
    Logic: 
    1. Full month in dark window = 0.60 (60%)
    2. Partial month = Days * 0.02 (2% per day)
    """
    ra_hours = ra_deg / 15.0
    monthly_weights = []

    for month in range(1, 13):
        # Determine LST at Midnight on the 15th
        # Rough anchor: LST at midnight shifts ~2h per month
        lst_at_midnight = (6.6 + (month - 9.5) * 2.0 - (lng / 15.0)) % 24
        
        # Distance from object transit to Midnight
        transit_diff = abs(ra_hours - lst_at_midnight)
        if transit_diff > 12: transit_diff = 24 - transit_diff

        # EXPERT LOGIC:
        # If transit is within 3 hours of midnight, it's a 'Full Month'
        if transit_diff < 3:
            weight = 0.60
        # If it's drifting out (3 to 5 hours), calculate marginal days
        elif 3 <= transit_diff <= 5:
            # Simple linear ramp: 5h diff = 0 days, 3h diff = 30 days
            days = int((5 - transit_diff) / 2 * 30)
            weight = round(days * 0.02, 2)
        else:
            weight = 0.0
            
        monthly_weights.append(weight)
    return monthly_weights

def run_airlock(scd_id, name, ra, dec):
    conn_cfg = sqlite3.connect("skypix_config.db")
    lng = conn_cfg.execute("SELECT default_long FROM setup_parameters WHERE id=1").fetchone()[0]
    conn_cfg.close()

    weights = calculate_marginal_shading(ra, lng)

    conn_sud = sqlite3.connect("skypix_sud.db")
    conn_sud.execute("""
        INSERT OR REPLACE INTO object_database (
            scd_primary_id, name, ra, dec,
            transit_jan, transit_feb, transit_mar, transit_apr,
            transit_may, transit_jun, transit_jul, transit_aug,
            transit_sep, transit_oct, transit_nov, transit_dec
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (scd_id, name, ra, dec, *weights))
    conn_sud.commit()
    conn_sud.close()
    print(f"✓ {name} Airlocked with Marginal Shading math applied.")

if __name__ == "__main__":
    # Test with M42
    run_airlock("M42-SCD", "Orion Nebula", 83.82, -5.39)