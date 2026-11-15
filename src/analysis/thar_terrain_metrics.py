from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.ndimage import uniform_filter

source = Path("data/processed/thar_elevation.tif")
output = Path("data/processed/thar_terrain_metrics.csv")

west, south, east, north = 69.0, 24.0, 71.5, 26.5
resolution = 90
target_crs = "EPSG:32642"

with rasterio.open(source) as src:
    window = from_bounds(west, south, east, north, src.transform)
    window = window.round_offsets().round_lengths()

    raw = src.read(1, window=window)
    src_transform = src.window_transform(window)
    bounds = rasterio.windows.bounds(window, src.transform)

    transform, width, height = calculate_default_transform(
        src.crs, target_crs,
        raw.shape[1], raw.shape[0],
        *bounds, resolution=resolution
    )

    elevation = np.full((height, width), -9999, dtype=np.float32)

    reproject(
        source=raw,
        destination=elevation,
        src_transform=src_transform,
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

valid_fraction = uniform_filter(
    valid.astype(np.float32), size=3, mode="constant", cval=0
)
neighbourhood_valid = valid_fraction >= (1 - 1e-6)

dy, dx = np.gradient(safe, resolution, resolution)
slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
slope_values = slope[neighbourhood_valid]

local_mean = uniform_filter(safe, size=3, mode="constant", cval=0)
local_mean_sq = uniform_filter(safe**2, size=3, mode="constant", cval=0)
roughness = np.sqrt(np.maximum(local_mean_sq - local_mean**2, 0))
roughness_values = roughness[neighbourhood_valid]

metrics = {
    "region": "Thar",
    "elevation_min_m": float(values.min()),
    "elevation_max_m": float(values.max()),
    "elevation_mean_m": float(values.mean()),
    "elevation_median_m": float(np.median(values)),
    "elevation_std_m": float(values.std()),
    "valid_pixels": int(values.size),
    "total_pixels": int(elevation.size),
    "valid_coverage_percent": float(100 * values.size / elevation.size),
    "analysis_resolution_m": resolution,
    "slope_mean_deg": float(slope_values.mean()),
    "slope_median_deg": float(np.median(slope_values)),
    "slope_p90_deg": float(np.percentile(slope_values, 90)),
    "roughness_mean_m": float(roughness_values.mean()),
    "roughness_median_m": float(np.median(roughness_values))
}

output.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame([metrics]).to_csv(output, index=False)

print("THAR TERRAIN METRICS")
for key, value in metrics.items():
    print(f"{key}: {value}")

print("Saved:", output)
