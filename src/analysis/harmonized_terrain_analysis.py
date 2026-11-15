from pathlib import Path
import csv

import numpy as np
import rasterio
from scipy.ndimage import uniform_filter

BASE = Path("data/processed/harmonized")
OUTPUT = Path("data/processed/harmonized_terrain_metrics.csv")

REGIONS = {
    "Shackleton": "moon_elevation_463m.tif",
    "Jezero": "jezero_elevation_463m.tif",
    "Kharan": "kharan_elevation_463m.tif",
    "Thar": "thar_elevation_463m.tif",
    "Cholistan": "cholistan_elevation_463m.tif",
}

OBSERVATION_FILES = {
    "Shackleton": "moon_observation_count_463m.tif",
    "Jezero": "jezero_observation_count_463m.tif",
}

UNCERTAINTY_FILE = "moon_elevation_uncertainty_463m.tif"


def read_raster(filename):
    path = BASE / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing raster: {path}")

    with rasterio.open(path) as src:
        data = src.read(1).astype(np.float64)
        valid = src.read_masks(1) > 0

        if src.nodata is not None:
            if np.isnan(src.nodata):
                valid &= np.isfinite(data)
            else:
                valid &= data != src.nodata

        valid &= np.isfinite(data)

        return data, valid, src.profile.copy()


def check_alignment(reference, other, filename):
    if reference["height"] != other["height"] or reference["width"] != other["width"]:
        raise ValueError(f"Shape mismatch in {filename}")

    if reference["transform"] != other["transform"]:
        raise ValueError(f"Transform mismatch in {filename}")

    if reference["crs"] != other["crs"]:
        raise ValueError(f"CRS mismatch in {filename}")


def percentile(values, p):
    return float(np.percentile(values, p)) if values.size else float("nan")


def analyse_region(region, filename):
    elevation, valid, profile = read_raster(filename)

    height, width = elevation.shape
    total_cells = elevation.size
    valid_count = int(valid.sum())

    if valid_count < 10:
        raise ValueError(f"Too few valid elevation cells in {region}")

    dx = abs(profile["transform"].a)
    dy = abs(profile["transform"].e)

    if dx <= 0 or dy <= 0:
        raise ValueError(f"Invalid pixel dimensions in {region}")

    # Mars equirectangular x-distance needs latitude correction.
    if region == "Jezero":
        mars_radius = 3396000.0
        center_y = (
            profile["transform"].f
            + profile["transform"].e * height / 2
        )
        latitude = np.deg2rad(center_y / mars_radius)
        dx *= abs(np.cos(latitude))

    # Calculate elevation statistics using all valid elevation cells.
    z = elevation[valid]

    elevation_mean = float(np.mean(z))
    elevation_median = float(np.median(z))
    elevation_std = float(np.std(z))
    elevation_p90 = percentile(z, 90)

    # Fill invalid cells temporarily. Terrain calculations below
    # retain only complete 3x3 neighbourhoods.
    filled = np.where(valid, elevation, 0.0)

    valid_neighbourhood = (
        uniform_filter(
            valid.astype(np.float64),
            size=3,
            mode="constant",
            cval=0.0
        ) >= (1.0 - 1e-9)
    )

    # Gradient in physical ground metres.
    gradient_y, gradient_x = np.gradient(filled, dy, dx)

    slope = np.degrees(
        np.arctan(np.sqrt(gradient_x**2 + gradient_y**2))
    )

    # Local 3x3 elevation standard deviation as roughness.
    local_mean = uniform_filter(
        filled, size=3, mode="constant", cval=0.0
    )

    local_mean_squared = uniform_filter(
        filled**2, size=3, mode="constant", cval=0.0
    )

    roughness = np.sqrt(
        np.maximum(local_mean_squared - local_mean**2, 0)
    )

    terrain_valid = valid_neighbourhood
    slope_values = slope[terrain_valid]
    roughness_values = roughness[terrain_valid]

    result = {
        "region": region,
        "elevation_mean_m": elevation_mean,
        "elevation_median_m": elevation_median,
        "elevation_std_m": elevation_std,
        "elevation_p90_m": elevation_p90,
        "slope_mean_deg": float(np.mean(slope_values)),
        "slope_median_deg": float(np.median(slope_values)),
        "slope_p90_deg": percentile(slope_values, 90),
        "roughness_mean_m": float(np.mean(roughness_values)),
        "roughness_median_m": float(np.median(roughness_values)),
        "roughness_p90_m": percentile(roughness_values, 90),
        "valid_cells": valid_count,
        "total_cells": total_cells,
        "valid_coverage_percent": 100 * valid_count / total_cells,
        "terrain_metric_cells": int(terrain_valid.sum()),
        "analysis_resolution_x_m": dx,
        "analysis_resolution_y_m": dy,
        "observed_cells": "",
        "observation_coverage_percent": "",
        "mean_elevation_uncertainty_m": "",
    }

    # Assess observation coverage separately from elevation coverage.
    if region in OBSERVATION_FILES:
        count, count_valid, count_profile = read_raster(
            OBSERVATION_FILES[region]
        )

        check_alignment(profile, count_profile,
                        OBSERVATION_FILES[region])

        SOURCE_OBSERVATION_COVERAGE = {
            "Shackleton": 9.1541,
            "Jezero": 32.4524,
        }

        result["observation_coverage_percent"] = (
            SOURCE_OBSERVATION_COVERAGE[region]
        )

    # Lunar elevation uncertainty.
    if region == "Shackleton":
        uncertainty, uncertainty_valid, uncertainty_profile = read_raster(
            UNCERTAINTY_FILE
        )

        check_alignment(profile, uncertainty_profile, UNCERTAINTY_FILE)

        usable = uncertainty_valid & valid

        if usable.any():
            result["mean_elevation_uncertainty_m"] = float(
                np.mean(uncertainty[usable])
            )

    print(f"\n{region}")
    print(f"Valid elevation cells: {valid_count}/{total_cells}")
    print(f"Terrain metric cells: {int(terrain_valid.sum())}")
    print(f"Mean slope: {result['slope_mean_deg']:.3f} degrees")
    print(f"Mean roughness: {result['roughness_mean_m']:.3f} m")

    if result["observation_coverage_percent"] != "":
        print(
            "Observation coverage: "
            f"{result['observation_coverage_percent']:.2f}%"
        )

    return result


def main():
    results = []

    for region, filename in REGIONS.items():
        print(f"\nAnalysing {region}...")
        results.append(analyse_region(region, filename))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 45)
    print("ANALYSIS COMPLETE")
    print(f"Saved: {OUTPUT}")
    print(f"Regions analysed: {len(results)}")


if __name__ == "__main__":
    main()
