import rasterio
import numpy as np
from pathlib import Path
from rasterio.warp import calculate_default_transform, reproject, Resampling

BASE = Path("data/processed")
OUTPUT = BASE / "harmonized"
OUTPUT.mkdir(parents=True, exist_ok=True)

RESOLUTION = 463.0577

datasets = {
    "Kharan": {
        "input": BASE / "kharan_elevation.tif",
        "crs": "EPSG:32641"
    },
    "Thar": {
        "input": BASE / "thar_elevation.tif",
        "crs": "EPSG:32642"
    },
    "Cholistan": {
        "input": BASE / "cholistan_elevation_90m.tif",
        "crs": "EPSG:32642"
    }
}

for name, info in datasets.items():
    source_path = info["input"]
    target_crs = info["crs"]

    print(f"\nProcessing {name}...")

    with rasterio.open(source_path) as src:
        nodata = src.nodata
        if nodata is None:
            nodata = -32768

        transform, width, height = calculate_default_transform(
            src.crs,
            target_crs,
            src.width,
            src.height,
            *src.bounds,
            resolution=RESOLUTION
        )

        profile = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": 1,
            "dtype": "float32",
            "crs": target_crs,
            "transform": transform,
            "nodata": -9999,
            "compress": "deflate"
        }

        destination = np.full(
            (height, width), -9999, dtype=np.float32
        )

        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=nodata,
            dst_transform=transform,
            dst_crs=target_crs,
            dst_nodata=-9999,
            resampling=Resampling.average
        )

    output_path = OUTPUT / f"{name.lower()}_elevation_463m.tif"

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(destination, 1)

    valid = destination != -9999

    print("Saved:", output_path)
    print("Shape:", destination.shape)
    print("Valid pixels:", int(valid.sum()))
    print("Mean elevation:", float(destination[valid].mean()))

print("\nEarth harmonisation complete.")
