from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from flask import Flask, jsonify, render_template

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "templates"),
    static_folder=str(PROJECT_ROOT / "static")
)


def read_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {filename}")

    df = pd.read_csv(path)
    return df.astype(object).where(pd.notna(df), None)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/terrain")
def terrain_data():
    try:
        df = read_csv("harmonized_terrain_metrics.csv")
        return jsonify(df.to_dict(orient="records"))
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/similarity")
def similarity_data():
    try:
        df = read_csv("harmonized_similarity_results.csv")
        return jsonify(df.to_dict(orient="records"))
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/jezero-elevation")
def jezero_elevation():
    try:
        raster_path = DATA_DIR / "jezero_elevation.tif"

        with rasterio.open(raster_path) as src:
            elevation = src.read(1, masked=True)
            values = elevation.filled(np.nan)

            z = [
                [
                    None if not np.isfinite(value) else round(float(value), 2)
                    for value in row
                ]
                for row in values
            ]

            x = [float(src.xy(0, col)[0]) for col in range(src.width)]
            y = [float(src.xy(row, 0)[1]) for row in range(src.height)]

            return jsonify({
                "region": "Jezero Crater",
                "units": "metres",
                "x": x,
                "y": y,
                "z": z,
                "width": src.width,
                "height": src.height
            })

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/shackleton-elevation")
def shackleton_elevation():
    try:
        raster_path = (
            PROJECT_ROOT / "data" / "processed" /
            "harmonized" / "moon_elevation_463m.tif"
        )

        with rasterio.open(raster_path) as src:
            elevation = src.read(1, masked=True)
            values = elevation.filled(np.nan)

            z = [
                [
                    None if not np.isfinite(value) else round(float(value), 2)
                    for value in row
                ]
                for row in values
            ]

            x = [float(src.xy(0, col)[0]) for col in range(src.width)]
            y = [float(src.xy(row, 0)[1]) for row in range(src.height)]

            return jsonify({
                "region": "Shackleton Crater Rim",
                "units": "metres",
                "x": x,
                "y": y,
                "z": z,
                "width": src.width,
                "height": src.height
            })

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/api/earth-elevation/<region>")
def earth_elevation(region):
    try:
        from rasterio.enums import Resampling
        from rasterio.transform import xy

        files = {
            "kharan": "kharan_elevation.tif",
            "thar": "thar_elevation.tif",
            "cholistan": "cholistan_elevation_90m.tif"
        }

        if region not in files:
            return jsonify({"error": "Unknown Earth region"}), 404

        raster_path = DATA_DIR / files[region]

        if not raster_path.exists():
            return jsonify({
                "error": f"Missing raster: {files[region]}"
            }), 404

        with rasterio.open(raster_path) as src:

            scale = min(
                1.0,
                120 / max(src.width, src.height)
            )

            width = max(1, round(src.width * scale))
            height = max(1, round(src.height * scale))

            elevation = src.read(
                1,
                masked=True,
                out_shape=(height, width),
                out_dtype="float32",
                resampling=Resampling.average
            )

            values = elevation.filled(np.nan)

            z = [
                [
                    None if not np.isfinite(value)
                    else round(float(value), 2)
                    for value in row
                ]
                for row in values
            ]

            transform = (
                src.transform *
                rasterio.Affine.scale(
                    src.width / width,
                    src.height / height
                )
            )

            x = [
                float(xy(transform, 0, col)[0])
                for col in range(width)
            ]

            y = [
                float(xy(transform, row, 0)[1])
                for row in range(height)
            ]

            horizontal_units = (
                "degrees" if src.crs and src.crs.is_geographic
                else "metres" if src.crs and src.crs.is_projected
                else "source CRS units"
            )

            return jsonify({
                "region": region.title(),
                "units": "metres",
                "horizontal_units": horizontal_units,
                "crs": str(src.crs),
                "source_resolution": list(src.res),
                "display_width": width,
                "display_height": height,
                "x": x,
                "y": y,
                "z": z
            })

    except Exception as error:
        return jsonify({"error": str(error)}), 500

if __name__ == "__main__":
    app.run(debug=True)



