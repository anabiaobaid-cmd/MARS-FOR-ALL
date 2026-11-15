# Mathematical Uncertainty and Sensitivity Analysis

## 1. Purpose

This analysis evaluates the sensitivity of terrain similarity rankings to the tested mathematical weighting scenarios.

## 2. Method

- Mean similarity across scenarios.
- Minimum and maximum similarity.
- Sensitivity range.
- Mean, best and worst rank.
- Frequency of ranking first.

The sensitivity range is not a statistical confidence interval.

## 3. Results: Jezero

| Earth region | Mean score | Minimum | Maximum | Range | Mean rank | First-place frequency |
|---|---:|---:|---:|---:|---:|---:|
| Kharan | 66.411 | 66.060642764304 | 66.7612928945026 | 0.7007 | 1 | 3/3 |
| Thar | 15.1007 | 14.9294206101103 | 15.2720047454677 | 0.3426 | 2 | 0/3 |
| Cholistan | 8.4114 | 8.29286765130606 | 8.52984579370971 | 0.237 | 3 | 0/3 |

Candidates ranked first in every tested scenario: Kharan

## 3. Results: Shackleton

| Earth region | Mean score | Minimum | Maximum | Range | Mean rank | First-place frequency |
|---|---:|---:|---:|---:|---:|---:|
| Kharan | 13.0353 | 12.9945069494372 | 13.0761864937131 | 0.0817 | 1 | 3/3 |
| Thar | 2.8375 | 2.8297036455386 | 2.84521237859716 | 0.0155 | 2 | 0/3 |
| Cholistan | 1.6194 | 1.60914313598437 | 1.62964793849093 | 0.0205 | 3 | 0/3 |

Candidates ranked first in every tested scenario: Kharan

## 4. Observation coverage

| Region | Direct observation coverage |
|---|---:|
| Cholistan | 96.844915% |
| Jezero | 32.4524% |
| Kharan | 97.10366% |
| Shackleton | 9.1541% |
| Thar | 97.777986% |

Coverage represents the proportion of valid source cells with direct observations. It is not a measurement error estimate.

## 5. Limitations

The three weighting scenarios are sensitivity tests, not independent statistical observations.

This analysis does not calculate measurement confidence intervals, spatial bootstrap intervals, or instrument error propagation.

Spatial autocorrelation must be considered before treating terrain pixels as independent observations.

## 6. Reproducibility

Input: data/processed/harmonized_similarity_results.csv

Output: data/processed/uncertainty_summary.csv

