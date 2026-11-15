import math
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.merge import merge
from rasterio.windows import from_bounds
from rasterio.warp import reproject, transform_bounds, Resampling
from rasterio.transform import from_origin
from scipy.ndimage import uniform_filter

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "earth" / "cholistan"
PROCESSED = ROOT / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)

# Cholistan exploratory study window
WEST, SOUTH, EAST, NORTH = 70.0, 27.0, 72.0, 29.5

# Expected SRTM tiles
tile_names = [
    "N27E070.hgt", "N27E071.hgt",
    "N28E070.hgt", "N28E071.hgt",
    "N29E070.hgt", "N29E071.hgt"
]

tile_paths = [RAW / name for name in tile_names]

missing = [str(p) for p in tile_paths if not p.exists()]
if missing:
    raise FileNotFoundError("Missing HGT files:\n" + "\n".join(missing))

print("Opening six SRTM tiles...")
sources = [rasterio.open(path) for path in tile_paths]

try:
    mosaic, mosaic_transform = merge(
        sources,
        nodata=-32768,
        dtype="int16"
    )

    mosaic_profile = sources[0].profile.copy()
    mosaic_profile.update(
        driver="GTiff",
        height=mosaic.shape[1],
        width=mosaic.shape[2],
        transform=mosaic_transform,
        count=1,
        dtype="int16",
        nodata=-32768,
        compress="deflate"
    )

    mosaic_path = PROCESSED / "cholistan_mosaic.tif"

    with rasterio.open(mosaic_path, "w", **mosaic_profile) as dst:
        dst.write(mosaic[0], 1)

finally:
    for src in sources:
        src.close()

print("Mosaic saved:", mosaic_path)
print("Mosaic dimensions:", mosaic.shape[2], "x", mosaic.shape[1])

# Crop the mosaic to the selected geographic rectangle
with rasterio.open(mosaic_path) as src:
    window = from_bounds(
        WEST, SOUTH, EAST, NORTH,
        transform=src.transform
    )

    cropped = src.read(1, window=window)
    cropped_transform = src.window_transform(window)

    source_crs = src.crs
    source_nodata = src.nodata

# Reproject to UTM Zone 42N at 90-metre resolution
target_crs = "EPSG:32642"

left, bottom, right, top = transform_bounds(
    source_crs,
    target_crs,
    WEST, SOUTH, EAST, NORTH
)

resolution = 90
width = math.ceil((right - left) / resolution)
height = math.ceil((top - bottom) / resolution)

target_transform = from_origin(
    left, top, resolution, resolution
)

destination = np.full(
    (height, width),
    -9999,
    dtype=np.float32
)

reproject(
    source=cropped.astype(np.float32),
    destination=destination,
    src_transform=cropped_transform,
    src_crs=source_crs,
    src_nodata=source_nodata,
    dst_transform=target_transform,
    dst_crs=target_crs,
    dst_nodata=-9999,
    resampling=Resampling.bilinear
)

valid = np.isfinite(destination) & (destination != -9999)

if valid.sum() == 0:
    raise ValueError("No valid elevation pixels after reprojection.")

elevation_path = PROCESSED / "cholistan_elevation_90m.tif"

profile = {
    "driver": "GTiff",
    "height": height,
    "width": width,
    "count": 1,
    "dtype": "float32",
    "crs": target_crs,
    "transform": target_transform,
    "nodata": -9999,
    "compress": "deflate"
}

with rasterio.open(elevation_path, "w", **profile) as dst:
    dst.write(destination, 1)

print("90-metre elevation raster saved:", elevation_path)

# Terrain calculations
safe = np.where(valid, destination, 0.0)

# Slope in degrees
gradient_y, gradient_x = np.gradient(
    safe,
    resolution,
    resolution
)

slope = np.degrees(
    np.arctan(np.sqrt(gradient_x**2 + gradient_y**2))
)

# Roughness: standard deviation in a 3x3 neighbourhood
local_mean = uniform_filter(
    safe, size=3, mode="constant", cval=0
)

local_mean_sq = uniform_filter(
    safe**2, size=3, mode="constant", cval=0
)

roughness_variance = np.maximum(
    local_mean_sq - local_mean**2,
    0
)

roughness = np.sqrt(roughness_variance)

# Only retain pixels whose entire 3x3 neighbourhood is valid
valid_fraction = uniform_filter(
    valid.astype(np.float32),
    size=3,
    mode="constant",
    cval=0
)

neighbourhood_valid = valid_fraction >= (1 - 1e-6)

slope_valid = valid & neighbourhood_valid
roughness_valid = valid & neighbourhood_valid

def statistics(values):
    values = values[np.isfinite(values)]

    return {
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "std": float(np.std(values)),
        "p90": float(np.percentile(values, 90))
    }

elevation_stats = statistics(destination[valid])
slope_stats = statistics(slope[slope_valid])
roughness_stats = statistics(roughness[roughness_valid])

metrics = {
    "region": "Cholistan",
    "source": "NASA SRTM Global 1 arc second V003",
    "analysis_resolution_m": resolution,
    "crs": target_crs,
    "west": WEST,
    "east": EAST,
    "south": SOUTH,
    "north": NORTH,
    "valid_pixels": int(valid.sum()),
    "total_pixels": int(valid.size),
    "coverage_percent": float(valid.mean() * 100),
}

for key, value in elevation_stats.items():
    metrics[f"elevation_{key}_m"] = value

for key, value in slope_stats.items():
    metrics[f"slope_{key}_degrees"] = value

for key, value in roughness_stats.items():
    metrics[f"roughness_{key}_m"] = value

metrics_path = PROCESSED / "cholistan_terrain_metrics.csv"

pd.DataFrame([metrics]).to_csv(metrics_path, index=False)

print("\nCHOLISTAN TERRAIN METRICS")
print("-------------------------")

for key, value in metrics.items():
    print(f"{key}: {value}")

print("\nSaved metrics:", metrics_path)
