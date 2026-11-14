import pandas as pd
import numpy as np
from pathlib import Path

earth_path = Path("data/processed/earth_comparison_metrics.csv")
output_path = Path("data/processed/planetary_similarity_results.csv")

earth = pd.read_csv(earth_path)

targets = {
    "Shackleton (Moon)": {
        "slope_mean_deg": 20.664146,
        "slope_median_deg": 20.550518,
        "slope_p90_deg": 33.162537
    },
    "Jezero (Mars)": {
        "slope_mean_deg": 14.535282,
        "slope_median_deg": 9.772264,
        "slope_p90_deg": 36.304607
    }
}

features = [
    "slope_mean_deg",
    "slope_median_deg",
    "slope_p90_deg"
]

results = []

for target_name, target in targets.items():
    for _, region in earth.iterrows():
        differences = []

        for feature in features:
            target_value = target[feature]
            earth_value = region[feature]

            # Relative difference, scaled to target magnitude.
            difference = abs(earth_value - target_value) / max(abs(target_value), 1)
            differences.append(difference)

        mean_difference = np.mean(differences)
        similarity = max(0, 100 * (1 - mean_difference))

        results.append({
            "target": target_name,
            "earth_region": region["region"],
            "similarity_score_percent": round(similarity, 2),
            "mean_slope_difference_deg": round(
                abs(region["slope_mean_deg"] - target["slope_mean_deg"]), 3
            ),
            "median_slope_difference_deg": round(
                abs(region["slope_median_deg"] - target["slope_median_deg"]), 3
            ),
            "p90_slope_difference_deg": round(
                abs(region["slope_p90_deg"] - target["slope_p90_deg"]), 3
            )
        })

results_df = pd.DataFrame(results)
results_df["rank"] = results_df.groupby("target")[
    "similarity_score_percent"
].rank(method="min", ascending=False).astype(int)

results_df = results_df.sort_values(["target", "rank"])
results_df.to_csv(output_path, index=False)

print("\nPLANETARY TERRAIN ANALOGUE RANKINGS")
print(results_df.to_string(index=False))
print(f"\nSaved: {output_path}")
