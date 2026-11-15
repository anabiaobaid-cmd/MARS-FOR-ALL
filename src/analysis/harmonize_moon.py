import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from pathlib import Path
import math

base = Path("data/raw/moon")
output = Path("data/processed/harmonized")
output.mkdir(parents=True, exist_ok=True)

resolution = 463.0577

datasets = {
    "elevation": "Site04_final_adj_5mpp_surf.tif",
    "observation_count": "Site04_final_adj_5mpp_ldec.tif",
    "elevation_uncertainty": "Site04_final_adj_5mpp_toterr.tif"
}

for name, filename in datasets.items():
    source_path = base / filename

    with rasterio.open(source_path) as src:
        bounds = src.bounds
        width = math.ceil((bounds.right - bounds.left) / resolution)
        height = math.ceil((bounds.top - bounds.bottom) / resolution)

        transform = from_origin(
            bounds.left, bounds.top, resolution, resolution
        )

        destination = np.full(
            (height, width), -9999, dtype=np.float32
        )

        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=transform,
            dst_crs=src.crs,
            dst_nodata=-9999,
            resampling=Resampling.average
        )

        profile = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": 1,
            "dtype": "float32",
            "crs": src.crs,
            "transform": transform,
            "nodata": -9999,
            "compress": "deflate"
        }

    destination_path = output / f"moon_{name}_463m.tif"

    with rasterio.open(destination_path, "w", **profile) as dst:
        dst.write(destination, 1)

    valid = destination != -9999

    print(f"\n{name}")
    print("Saved:", destination_path)
    print("Dimensions:", destination.shape)
    print("Valid cells:", int(valid.sum()))

print("\nShackleton harmonisation complete.")
