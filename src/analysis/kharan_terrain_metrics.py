from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.ndimage import uniform_filter

source = Path("data/processed/kharan_elevation.tif")
output = Path("data/processed/kharan_terrain_metrics.csv")

resolution = 90
target_crs = "EPSG:32641"

with rasterio.open(source) as src:
    transform, width, height = calculate_default_transform(
        src.crs, target_crs, src.width, src.height,
        *src.bounds, resolution=resolution
    )

    elevation = np.full((height, width), -9999, dtype=np.float32)

    reproject(
        source=rasterio.band(src, 1),
        destination=elevation,
        src_transform=src.transform,
        src_crs=src.crs,
        src_nodata=src.nodata,
        dst_transform=transform,
        dst_crs=target_crs,
        dst_nodata=-9999,
        resampling=Resampling.bilinear
    )

valid = np.isfinite(elevation) & (elevation != -9999)
values = elevation[valid]

if values.size == 0:
    raise ValueError("No valid elevation pixels.")

safe = np.where(valid, elevation, 0.0)

# Require all nine cells in each 3x3 neighbourhood to be valid.
valid_fraction = uniform_filter(
    valid.astype(np.float32), size=3, mode="constant", cval=0
)
neighbourhood_valid = valid_fraction >= (1 - 1e-6)

# Slope
dy, dx = np.gradient(safe, resolution, resolution)
slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
slope_values = slope[neighbourhood_valid]

# Local 3x3 elevation standard deviation
local_mean = uniform_filter(safe, size=3, mode="constant", cval=0)
local_mean_sq = uniform_filter(safe**2, size=3, mode="constant", cval=0)
roughness = np.sqrt(np.maximum(local_mean_sq - local_mean**2, 0))
roughness_values = roughness[neighbourhood_valid]

metrics = {
    "region": "Kharan",
    "elevation_min_m": float(np.min(values)),
    "elevation_max_m": float(np.max(values)),
    "elevation_mean_m": float(np.mean(values)),
    "elevation_median_m": float(np.median(values)),
    "elevation_std_m": float(np.std(values)),
    "valid_pixels": int(values.size),
    "total_pixels": int(elevation.size),
    "valid_coverage_percent": float(100 * values.size / elevation.size),
    "analysis_resolution_m": resolution,
    "slope_mean_deg": float(np.mean(slope_values)),
    "slope_median_deg": float(np.median(slope_values)),
    "slope_p90_deg": float(np.percentile(slope_values, 90)),
    "roughness_mean_m": float(np.mean(roughness_values)),
    "roughness_median_m": float(np.median(roughness_values)),
}

pd.DataFrame([metrics]).to_csv(output, index=False)

print("KHARAN TERRAIN METRICS")
for key, value in metrics.items():
    print(f"{key}: {value}")

print("Saved:", output)
