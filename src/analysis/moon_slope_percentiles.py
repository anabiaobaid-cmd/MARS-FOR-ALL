import numpy as np
import rasterio

path = "data/raw/moon/Site04_final_adj_5mpp_slp.tif"

with rasterio.open(path) as src:
    slope = src.read(1)
    if src.nodata is not None:
        slope = slope[slope != src.nodata]
    slope = slope[np.isfinite(slope)]

print("Moon slope mean:", np.mean(slope))
print("Moon slope median:", np.median(slope))
print("Moon slope P90:", np.percentile(slope, 90))
