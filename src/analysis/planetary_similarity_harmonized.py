from pathlib import Path
import pandas as pd

INPUT = Path("data/processed/harmonized_terrain_metrics.csv")
OUTPUT = Path("data/processed/harmonized_similarity_results.csv")

df = pd.read_csv(INPUT)
df = df.set_index("region")

earth_regions = ["Kharan", "Thar", "Cholistan"]
reference_regions = ["Shackleton", "Jezero"]

slope_features = [
    "slope_mean_deg",
    "slope_median_deg",
    "slope_p90_deg",
]

roughness_features = [
    "roughness_mean_m",
    "roughness_median_m",
    "roughness_p90_m",
]

required_regions = reference_regions + earth_regions
required_features = slope_features + roughness_features

for region in required_regions:
    if region not in df.index:
        raise ValueError(f"Missing region: {region}")

for feature in required_features:
    if feature not in df.columns:
        raise ValueError(f"Missing metric column: {feature}")

for region in required_regions:
    for feature in required_features:
        value = float(df.loc[region, feature])

        if not pd.notna(value) or value < 0:
            raise ValueError(
                f"Invalid value for {region}, {feature}: {value}"
            )


def feature_similarity(reference, candidate):
    largest = max(abs(reference), abs(candidate))

    if largest == 0:
        return 100.0

    return 100.0 * min(
        abs(reference), abs(candidate)
    ) / largest


scenarios = [
    ("Balanced", 0.50, 0.50),
    ("Slope emphasis", 0.70, 0.30),
    ("Roughness emphasis", 0.30, 0.70),
]

results = []

for reference in reference_regions:
    for earth in earth_regions:

        slope_scores = [
            feature_similarity(
                float(df.loc[reference, feature]),
                float(df.loc[earth, feature])
            )
            for feature in slope_features
        ]

        roughness_scores = [
            feature_similarity(
                float(df.loc[reference, feature]),
                float(df.loc[earth, feature])
            )
            for feature in roughness_features
        ]

        slope_similarity = sum(slope_scores) / len(slope_scores)
        roughness_similarity = (
            sum(roughness_scores) / len(roughness_scores)
        )

        for scenario, slope_weight, roughness_weight in scenarios:

            overall = (
                slope_similarity * slope_weight
                + roughness_similarity * roughness_weight
            )

            results.append({
                "reference": reference,
                "earth_region": earth,
                "scenario": scenario,
                "slope_weight": slope_weight,
                "roughness_weight": roughness_weight,
                "slope_similarity": slope_similarity,
                "roughness_similarity": roughness_similarity,
                "overall_similarity": overall,
                "earth_data_coverage_percent":
                    float(df.loc[earth, "valid_coverage_percent"]),
                "reference_data_coverage_percent":
                    float(df.loc[reference, "valid_coverage_percent"]),
                "reference_observation_coverage_percent":
                    df.loc[reference, "observation_coverage_percent"],
            })

output = pd.DataFrame(results)

output["rank"] = (
    output.groupby(["reference", "scenario"])["overall_similarity"]
    .rank(method="min", ascending=False)
    .astype(int)
)

output = output.sort_values(
    ["reference", "scenario", "rank"]
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
output.to_csv(OUTPUT, index=False)

print("\nHARMONISED SIMILARITY ANALYSIS COMPLETE")
print("Saved:", OUTPUT)

for reference in reference_regions:
    print(f"\n{reference} — BALANCED MODEL")

    subset = output[
        (output["reference"] == reference)
        & (output["scenario"] == "Balanced")
    ]

    for _, row in subset.iterrows():
        print(
            f"{row['rank']}. {row['earth_region']}: "
            f"{row['overall_similarity']:.2f}%"
        )

print("\nWeight sensitivity results also saved.")
