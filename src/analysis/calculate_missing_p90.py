from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling

folder = Path("data/processed")

def calculate_p90(region):
    source = folder / f"{region}_elevation.tif"
    csv_path = folder / f"{region}_terrain_metrics.csv"

    with rasterio.open(source) as src:

        if region == "thar":
            west, south, east, north = 69.0, 24.0, 71.5, 26.5
            window = from_bounds(west, south, east, north, src.transform)
            window = window.round_offsets().round_lengths()
            raw = src.read(1, window=window)
            bounds = rasterio.windows.bounds(window, src.transform)
            src_transform = src.window_transform(window)
            src_width, src_height = raw.shape[1], raw.shape[0]
            source_data = raw
        else:
            src_width, src_height = src.width, src.height
            source_data = rasterio.band(src, 1)
            bounds = src.bounds
            src_transform = src.transform

        crs = src.crs
        nodata = src.nodata

        target_crs = "EPSG:32641" if region == "kharan" else "EPSG:32642"

        transform, width, height = calculate_default_transform(
            crs, target_crs,
            src_width, src_height,
            *bounds, resolution=90
        )

        elevation = np.full((height, width), -9999, dtype=np.float32)

        reproject(
            source=source_data,
            destination=elevation,
            src_transform=src_transform,
            src_crs=crs,
            src_nodata=nodata,
            dst_transform=transform,
            dst_crs=target_crs,
            dst_nodata=-9999,
            resampling=Resampling.bilinear
        )

    valid = np.isfinite(elevation) & (elevation != -9999)
    values = elevation[valid]

    if values.size == 0:
        raise ValueError(f"No valid elevation values for {region}")

    p90 = float(np.percentile(values, 90))

    df = pd.read_csv(csv_path)
    df["elevation_p90_m"] = p90
    df.to_csv(csv_path, index=False)

    print(f"{region.title()} elevation P90: {p90:.4f} m")
    print(f"Saved to: {csv_path}")

calculate_p90("kharan")
calculate_p90("thar")
