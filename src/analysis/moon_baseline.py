from pathlib import Path
import csv
import numpy as np
import rasterio

folder = Path("data/raw/moon")
output = Path("data/processed/moon_baseline.csv")

rows = []

for path in sorted(folder.glob("*.tif")):
    with rasterio.open(path) as src:
        values = src.read(1, masked=True).compressed()

        if len(values) == 0:
            continue

        rows.append({
            "file": path.name,
            "valid_pixels": len(values),
            "coverage_percent": round(len(values) / (src.width * src.height) * 100, 3),
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "p25": float(np.percentile(values, 25)),
            "p75": float(np.percentile(values, 75))
        })

output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} layer summaries to {output}")
