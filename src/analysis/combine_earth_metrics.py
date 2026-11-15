from pathlib import Path
import pandas as pd
import re

root = Path(__file__).resolve().parents[2]
folder = root / "data" / "processed"

files = {
    "Kharan": "kharan_terrain_metrics.csv",
    "Thar": "thar_terrain_metrics.csv",
    "Cholistan": "cholistan_terrain_metrics.csv"
}

def clean(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())

def read_region(region, filename):
    df = pd.read_csv(folder / filename)
    df.columns = [clean(c) for c in df.columns]
    row = df.iloc[0]

    def value(*names):
        for name in names:
            key = clean(name)
            if key in row.index and pd.notna(row[key]):
                return row[key]
        return None

    return {
        "region": region,
        "elevation_mean_m": value("elevation_mean_m"),
        "elevation_median_m": value("elevation_median_m"),
        "elevation_std_m": value("elevation_std_m"),
        "elevation_p90_m": value("elevation_p90_m"),
        "slope_mean_deg": value("slope_mean_deg", "slope_mean_degrees"),
        "slope_median_deg": value("slope_median_deg", "slope_median_degrees"),
        "slope_p90_deg": value("slope_p90_deg", "slope_p90_degrees"),
        "roughness_mean_m": value("roughness_mean_m"),
        "roughness_median_m": value("roughness_median_m"),
        "valid_coverage_percent": value("valid_coverage_percent", "coverage_percent"),
        "analysis_resolution_m": value("analysis_resolution_m")
    }

records = [
    read_region(region, filename)
    for region, filename in files.items()
]

combined = pd.DataFrame(records)

output = folder / "earth_comparison_metrics.csv"
combined.to_csv(output, index=False)

print(combined.to_string(index=False))
print("\nMissing values per column:")
print(combined.isna().sum())
print("\nSaved:", output)
