# MARS FOR ALL — The Analog Atlas
## Final Deployment & Implementation Plan
**Document:** `FINAL_DEPLOYMENT_PLAN.md`  
**Project:** NASA Space Apps Challenge 2026 — *MARS FOR ALL: The Analog Atlas*  
**Tagline:** *Earth is our testing ground. Space is our frontier.*  
**Date:** November 15, 2026  
**Status:** Architectural Plan (Awaiting Approval Before Execution)

---

## 1. Executive Summary & Objective

This implementation plan outlines the exact, step-by-step procedure to prepare **MARS FOR ALL — The Analog Atlas** for reliable demonstration, local access, and GitHub publication.

The plan addresses five key pillars:
1. **Unicode & Mojibake Repair:** Eliminating all corrupted character sequences (mathematical symbols, Greek letters, quotation marks, dashes, degree signs) across HTML, Python, and configuration files, with full pre-modification backups.
2. **Scientific Equation Preservation & Verification:** Formally documenting the exact mathematical equations implemented in `harmonized_terrain_analysis.py` and `planetary_similarity_harmonized.py` using GitHub-compatible Markdown LaTeX.
3. **Dual Access Architecture (Option C):** Providing both a zero-dependency standalone entry point (`index.html`) that works out of the box (via `file://` or GitHub Pages) with real pre-rendered data, and a complete Flask-powered backend application launched via an upgraded `START_ATLAS.bat`.
4. **GitHub & GitHub Pages Readiness:** Establishing a clean repository structure, creating a comprehensive `.gitignore`, configuring `.gitattributes` for Git LFS to handle large elevation models (>50 MB / >100 MB), fixing case-sensitivity (`src/backend`), converting `requirements.txt` from UTF-16 to UTF-8, and adding missing dependencies (`scipy`).
5. **Rigorous Verification & Professional Documentation:** Updating `README.md` with full project context, methodology, equations, and limitations, and generating `FINAL_DEPLOYMENT_REPORT.md`.

---

## 2. Project Architecture & Dependency Audit

### 2.1 File & Directory Inventory

```text
MARS_FOR_ALL/
├── data/
│   ├── processed/
│   │   ├── cholistan_elevation_90m.tif        (22.9 MB - Earth Cholistan elevation)
│   │   ├── cholistan_mosaic.tif               (43.3 MB)
│   │   ├── cholistan_terrain_metrics.csv      (837 B)
│   │   ├── earth_comparison_metrics.csv       (773 B)
│   │   ├── harmonized_similarity_results.csv  (2.6 KB - 18 rows: 3 Earth × 2 Ref × 3 Scenarios)
│   │   ├── harmonized_terrain_metrics.csv     (1.6 KB - 5 rows: Shackleton, Jezero, Kharan, Thar, Cholistan)
│   │   ├── jezero_elevation.tif               (83.9 KB - 256×256 Mars Jezero elevation)
│   │   ├── jezero_observation_count.tif       (25.3 KB)
│   │   ├── jezero_terrain_metrics.csv         (215 B)
│   │   ├── kharan_elevation.tif               (67.3 MB - Earth Kharan SRTM elevation)
│   │   ├── kharan_terrain_metrics.csv         (489 B)
│   │   ├── moon_baseline.csv                  (788 B)
│   │   ├── planetary_similarity_results.csv   (440 B)
│   │   ├── thar_elevation.tif                 (95.6 MB - Earth Thar SRTM elevation)
│   │   ├── thar_terrain_metrics.csv           (509 B)
│   │   ├── uncertainty_summary.csv            (914 B)
│   │   └── harmonized/
│   │       ├── cholistan_elevation_463m.tif   (878 KB)
│   │       ├── jezero_elevation_463m.tif      (83.9 KB)
│   │       ├── jezero_observation_count_463m.tif (25.3 KB)
│   │       ├── kharan_elevation_463m.tif      (696 KB)
│   │       ├── moon_elevation_463m.tif        (5.1 KB - 35×35 Moon Shackleton elevation)
│   │       ├── moon_elevation_uncertainty_463m.tif (5.0 KB)
│   │       ├── moon_observation_count_463m.tif (4.9 KB)
│   │       └── thar_elevation_463m.tif        (1.68 MB)
│   └── raw/                                   (Source SRTM, LOLA, MOLA datasets)
│       ├── earth/                             (SRTMGL1 tiles and zips)
│       ├── mars/                              (MEGDR files, including megt44n000hb.img = 123.8 MB)
│       └── moon/                              (Site04 LOLA polar tiles ~39 MB each)
├── docs/
│   └── mathematical_uncertainty_report.md
├── src/
│   ├── analysis/
│   │   ├── calculate_missing_p90.py
│   │   ├── cholistan_terrain_metrics.py
│   │   ├── combine_earth_metrics.py
│   │   ├── harmonized_terrain_analysis.py     (Core terrain metrics & gradient/roughness extraction)
│   │   ├── harmonize_earth.py
│   │   ├── harmonize_moon.py
│   │   ├── kharan_terrain_metrics.py
│   │   ├── moon_baseline.py
│   │   ├── moon_slope_percentiles.py
│   │   ├── planetary_comparison.py
│   │   ├── planetary_similarity.py
│   │   ├── planetary_similarity_harmonized.py (Core similarity calculation across 3 scenarios)
│   │   └── thar_terrain_metrics.py
│   └── backend/
│       └── app.py                             (Flask API & web server)
├── static/
│   ├── app.js                                 (Plotly 3D visualizer & API fetch logic)
│   └── style.css                              (Theme, typography, layout, responsive styling)
├── templates/
│   └── index.html                             (Jinja template & HTML structure)
├── tests/
├── README.md
├── requirements.txt                           (Currently UTF-16-LE, missing scipy)
└── START_ATLAS.bat                            (Launcher script)
```

### 2.2 Frontend-Backend Dependencies

1. **Jinja Templating:**
   - Currently, `templates/index.html` uses only two Jinja expressions:
     - `{{ url_for('static', filename='style.css') }}`
     - `{{ url_for('static', filename='app.js') }}`
   - The rest of the 1,410-line HTML file is pure semantic HTML and inline CSS.
2. **Flask API Endpoints in `src/backend/app.py`:**
   - `/` -> Serves `index.html`.
   - `/api/terrain` -> Serves `harmonized_terrain_metrics.csv` (JSON).
   - `/api/similarity` -> Serves `harmonized_similarity_results.csv` (JSON).
   - `/api/jezero-elevation` -> Reads `data/processed/jezero_elevation.tif` (256×256) and returns `{region, units, x, y, z, width, height}`.
   - `/api/shackleton-elevation` -> Reads `data/processed/harmonized/moon_elevation_463m.tif` (35×35) and returns `{region, units, x, y, z, width, height}`.
   - `/api/earth-elevation/<region>` (`kharan`, `thar`, `cholistan`) -> Reads corresponding raw/processed GeoTIFF, dynamically downsamples with `Resampling.average` to a maximum dimension of 120 pixels, computes projected coordinates $(x, y)$, and returns elevation grid $z$.
3. **Frontend Consumer (`static/app.js`):**
   - Calls `/api/similarity` -> renders ranking cards for Jezero vs Earth or Shackleton vs Earth under the "Balanced" scenario.
   - Calls `/api/jezero-elevation` -> renders Plotly 3D surface in `#jezero-3d`.
   - Calls `/api/shackleton-elevation` -> renders Plotly 3D surface in `#shackleton-3d-viewer`.
   - Calls `/api/earth-elevation/kharan` -> renders Plotly 3D surface in `#earth-kharan-3d`.
   - Calls `/api/earth-elevation/thar` -> renders Plotly 3D surface in `#earth-thar-3d`.
   - Calls `/api/earth-elevation/cholistan` -> renders Plotly 3D surface in `#earth-cholistan-3d`.
4. **Current Launch Mechanism:**
   - `START_ATLAS.bat` executes `py -3.13 ".\src\Backend\app.py"`.
   - Flaws identified:
     - Hardcoded `Backend` casing (on disk it is lowercase `backend`), which breaks on case-sensitive OS.
     - Hardcoded `py -3.13` launcher, which fails if Python is invoked via `python`, `.venv`, or a different version.
     - Does not activate `.venv` if available.

---

## 3. Encoding & Mojibake Audit Findings

### 3.1 Mojibake Catalog in `templates/index.html`

Our diagnostic scan revealed widespread Windows-1252 / UTF-8 double-decoding artifacts:

| Corrupted String in Code | Byte Sequence / Entities | Intended Character & Meaning | Exact Location / Context |
|---|---|---|---|
| `Â·` | `C2 A0` / `C2 B7` | `·` (Middle dot separator) | Lines 190, 252, 287, 303, 374, 383, 392, 454, 543, 551, 559, 683, 725-730, 745, 824, 955, 1050, 1141, 1220, 1332 |
| `â€”` | `E2 80 94` | `—` (Em dash) | Lines 593, 594, 601, 602, 603, 668, 669, 670, 671, 966, 981, 997, 1060, 1073, 1231, 1263 |
| `â€“` | `E2 80 93` | `–` (En dash) | Lines 941 (`0–100`), 1017 (`1066–1081`) |
| `â†’` | `E2 86 92` | `→` (Right arrow) | Line 203 (`EXPLORE THE SCIENCE →`) |
| `\x9d` | `0x9D` control byte | Removed / clean spacing | Lines 261, 262 (`Mars — Jezero Crater`, `Moon — Shackleton Rim`) |
| `âˆš` | `E2 88 9A` | `√` (Square root) | Lines 616, 620, 840, 857 |
| `âˆ‚` | `E2 88 82` | `∂` (Partial differential) | Lines 616, 840, 843 (`∂z/∂x`, `∂z/∂y`) |
| `Â²` | `C2 B2` | `²` (Superscript 2) | Lines 616, 620, 840, 857 |
| `Ã—` | `C3 97` | `×` (Multiplication sign) | Lines 840, 853, 857, 891, 929, 930 |
| `Ï€` | `CF 80` | `π` (Pi) | Line 840 (`180 / π`) |
| `Ïƒ` | `CF 83` | `σ` (Sigma / roughness) | Line 620 (`σ = ...`) |
| `Î£` | `CE A3` | `Σ` (Summation) | Lines 620, 857 (`Σ(...)`) |
| `Î”` | `CE 94` | `Δ` (Delta / difference) | Lines 624, 625 (`Δ = |A - B|`) |
| `âˆ’` | `E2 88 92` | `−` (Mathematical minus) | Lines 620, 624, 857 |
| `záµ¢` | `z + E1 B5 A2` | `zᵢ` (Elevation sample $i$) | Lines 620, 857, 860 |
| `zÌ„` | `z + CC 84` | `z̄` (Mean elevation) | Lines 620, 857, 860 |
| `Sáµ¢` | `S + E1 B5 A2` | `Sᵢ` (Feature similarity $i$) | Line 891 |
| `Aáµ¢`, `Báµ¢` | `A/B + E1 B5 A2` | `Aᵢ`, `Bᵢ` (Feature values) | Lines 891, 894 |
| `Sâ‚ `, `Sâ‚‚`, `Sâ‚ƒ` | `S + E2 82 81..83` | `S₁`, `S₂`, `S₃` (Slope features) | Line 912 |
| `Sâ‚„`, `Sâ‚…`, `Sâ‚†` | `S + E2 82 84..86` | `S₄`, `S₅`, `S₆` (Roughness features) | Line 918 |
| `wâ‚›` | `w + E2 82 9B` | `wₛ` (Slope weight) | Line 929 |
| `wáµ£` | `w + E1 B5 A3` | `wᵣ` (Roughness weight) | Line 930 |

### 3.2 HTML Document Structure Anomalies

In `templates/index.html`:
- At line 251, a `<footer>` tag opens, and sections `#comparison`, `#terrain-3d`, `#shackleton-3d`, `#our-story`, `#science-behind-atlas`, `#weighting-methodology`, `#earth-3d`, and `#science` are nested inside `<footer>`.
- The `<footer>` closes at line 676, followed by `</div>` and `<script>` tags at lines 680–681.
- Additional sections (`#weighting-analysis`, `#scientific-reliability`, `#mathematical-model`, `#data-references`, `#planetary-comparison`, `#lunar-finding`, `#research-results`, `#research-integrity`) were subsequently appended *after* the script tags up to line 1402, before `</body></html>`.
- **Repair Action:** Normalize the HTML5 hierarchy so all `<section>` elements sit in logical reading order within `<main class="main-content">`, followed by the official `<footer>`, followed by `<script>` tags at the base of `<body>`.

### 3.3 File Encodings Audit

- `requirements.txt`: Currently encoded as `UTF-16-LE` with byte-order mark (`\xFF\xFE`). Standard `pip` and Unix tools fail to parse it. **Repair Action:** Transcode to clean UTF-8 (no BOM).
- `uncertainty_summary.csv`, `docs/mathematical_uncertainty_report.md`, and several `src/analysis/*.py` files: Encoded as `UTF-8-SIG` (UTF-8 with BOM). **Repair Action:** Normalize to clean UTF-8 without BOM.

---

## 4. Preservation & Verification of Scientific Equations

Every equation in the documentation and frontend will be matched directly against the Python implementation:

### 4.1 Terrain Slope ($S$)
- **Source File:** [`src/analysis/harmonized_terrain_analysis.py`](file:///c:/Users/sheik/OneDrive/Desktop/MARS_FOR_ALL/src/analysis/harmonized_terrain_analysis.py#L111-L115)
- **Code:**
  ```python
  gradient_y, gradient_x = np.gradient(filled, dy, dx)
  slope = np.degrees(np.arctan(np.sqrt(gradient_x**2 + gradient_y**2)))
  ```
- **Equation:**
  $$S = \tan^{-1}\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180}{\pi}$$
- **Variables & Units:**
  - $S$: Slope in degrees ($^\circ$).
  - $z$: Terrain surface elevation in metres ($m$).
  - $\frac{\partial z}{\partial x}, \frac{\partial z}{\partial y}$: Central-difference horizontal elevation gradients ($\text{m/m}$).
  - $dx, dy$: Pixel spacing in ground physical metres ($463.0577\text{ m}$).
  - *Mars correction:* For Jezero Crater (equirectangular projection), $dx = dx_{\text{deg}} \times \frac{\pi}{180} R_{\text{Mars}} \cos(\phi)$, where $R_{\text{Mars}} = 3,396,000\text{ m}$ and $\phi$ is crater latitude.

### 4.2 Local Terrain Roughness ($R$)
- **Source File:** [`src/analysis/harmonized_terrain_analysis.py`](file:///c:/Users/sheik/OneDrive/Desktop/MARS_FOR_ALL/src/analysis/harmonized_terrain_analysis.py#L118-L128)
- **Code:**
  ```python
  local_mean = uniform_filter(filled, size=3, mode="constant", cval=0.0)
  local_mean_squared = uniform_filter(filled**2, size=3, mode="constant", cval=0.0)
  roughness = np.sqrt(np.maximum(local_mean_squared - local_mean**2, 0))
  ```
- **Equation:**
  $$R = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (z_i - \bar{z})^2} = \sqrt{\overline{z^2} - (\bar{z})^2}$$
- **Variables & Units:**
  - $R$: Local elevation roughness in metres ($m$), defined as the standard deviation of elevation within a local $3 \times 3$ moving window ($n = 9$ valid grid cells).
  - $z_i$: Elevation of cell $i$ within the window ($m$).
  - $\bar{z}$: Moving window arithmetic mean elevation ($m$).
  - Masking: Only windows where all $3 \times 3$ neighbours are valid observations (`uniform_filter(valid) >= 1.0 - 1e-9`) are retained.

### 4.3 Regional Statistical Summaries
For each region, slope and roughness are aggregated over all valid terrain cells into three statistical metrics:
- Mean: $\mu = \frac{1}{N}\sum x_i$
- Median: $P_{50}$ (50th percentile)
- High-end threshold: $P_{90}$ (90th percentile)

Yielding 6 comparative features:
$$\mathbf{f}_{\text{slope}} = [S_{\text{mean}}, S_{\text{median}}, S_{P90}], \quad \mathbf{f}_{\text{rough}} = [R_{\text{mean}}, R_{\text{median}}, R_{P90}]$$

### 4.4 Feature-Level Similarity ($S_i$)
- **Source File:** [`src/analysis/planetary_similarity_harmonized.py`](file:///c:/Users/sheik/OneDrive/Desktop/MARS_FOR_ALL/src/analysis/planetary_similarity_harmonized.py#L46-L54)
- **Code:**
  ```python
  def feature_similarity(reference, candidate):
      largest = max(abs(reference), abs(candidate))
      if largest == 0:
          return 100.0
      return 100.0 * min(abs(reference), abs(candidate)) / largest
  ```
- **Equation:**
  $$S(f_{\text{ref}}, f_{\text{cand}}) = 100 \times \frac{\min(|f_{\text{ref}}|, |f_{\text{cand}}|)}{\max(|f_{\text{ref}}|, |f_{\text{cand}}|)}$$
  If $\max(|f_{\text{ref}}|, |f_{\text{cand}}|) = 0$, $S = 100\%$.

### 4.5 Group Similarities ($S_{\text{slope}}$, $S_{\text{roughness}}$)
- **Source File:** [`src/analysis/planetary_similarity_harmonized.py`](file:///c:/Users/sheik/OneDrive/Desktop/MARS_FOR_ALL/src/analysis/planetary_similarity_harmonized.py#L84-L87)
- **Equations:**
  $$S_{\text{slope}} = \frac{1}{3} \sum_{k=1}^{3} S(f_{\text{slope, ref}, k}, f_{\text{slope, earth}, k})$$
  $$S_{\text{roughness}} = \frac{1}{3} \sum_{k=1}^{3} S(f_{\text{rough, ref}, k}, f_{\text{rough, earth}, k})$$

### 4.6 Overall Weighted Similarity & Sensitivity Analysis ($S_{\text{overall}}$)
- **Source File:** [`src/analysis/planetary_similarity_harmonized.py`](file:///c:/Users/sheik/OneDrive/Desktop/MARS_FOR_ALL/src/analysis/planetary_similarity_harmonized.py#L89-L94)
- **Equation:**
  $$S_{\text{overall}} = w_{\text{slope}} S_{\text{slope}} + w_{\text{roughness}} S_{\text{roughness}}$$
- **Evaluated Scenarios:**
  1. **Balanced:** $w_{\text{slope}} = 0.50, \quad w_{\text{roughness}} = 0.50$
  2. **Slope Emphasis:** $w_{\text{slope}} = 0.70, \quad w_{\text{roughness}} = 0.30$
  3. **Roughness Emphasis:** $w_{\text{slope}} = 0.30, \quad w_{\text{roughness}} = 0.70$
- **Verified Results:**
  - **Jezero Crater (Mars Reference):**
    1. Kharan: Balanced = $66.41\%$, Range = $0.70\%$ (Slope: $66.06\%$, Roughness: $66.76\%$) -> **Rank 1**
    2. Thar: Balanced = $15.10\%$, Range = $0.34\%$ (Slope: $14.93\%$, Roughness: $15.27\%$) -> **Rank 2**
    3. Cholistan: Balanced = $8.41\%$, Range = $0.24\%$ (Slope: $8.29\%$, Roughness: $8.53\%$) -> **Rank 3**
  - **Shackleton Crater (Moon Reference):**
    1. Kharan: Balanced = $13.04\%$, Range = $0.08\%$ (Slope: $13.08\%$, Roughness: $12.99\%$) -> **Rank 1**
    2. Thar: Balanced = $2.84\%$, Range = $0.02\%$ (Slope: $2.83\%$, Roughness: $2.85\%$) -> **Rank 2**
    3. Cholistan: Balanced = $1.62\%$, Range = $0.02\%$ (Slope: $1.61\%$, Roughness: $1.63\%$) -> **Rank 3**
- **Scientific Interpretation & Scope:**
  - This is a *terrain screening metric*, not an environmental qualification or habitability assessment.
  - Kharan exhibits the highest statistical terrain similarity among the three Pakistani study regions, primarily driven by moderate relief and dune-plain morphology.

---

## 5. Architectural Strategy: Option C (Dual Standalone & Flask)

To fulfill the constraint that double-clicking an HTML file or hosting on GitHub Pages cannot run Python/Flask, while preserving the full dynamic Flask backend:

### 5.1 Architecture Details

```
                          ┌─────────────────────────┐
                          │   MARS FOR ALL ATLAS    │
                          └────────────┬────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
     [Mode 1: Standalone Demo]                     [Mode 2: Dynamic Flask]
  - Double-click index.html                     - Launch START_ATLAS.bat
  - Or GitHub Pages (https://...)               - Starts http://127.0.0.1:5000
  - Zero Python backend needed                  - Full Flask API & endpoints
  - Loads static/atlas_data.js                  - Real-time GeoTIFF processing
  - Plotly 3D renders all 5 surfaces            - Dynamic /api/terrain & /api/similarity
  - Similarity selector fully interactive       - Renders templates/index.html
```

### 5.2 Implementation of Standalone Data Layer
1. Export the 100% exact real outputs of the Flask API endpoints into `static/atlas_data.js`:
   - `ATLAS_DATA.similarity`: All 18 rows of `harmonized_similarity_results.csv`.
   - `ATLAS_DATA.jezero`: Exact grid from `jezero_elevation.tif` (256×256).
   - `ATLAS_DATA.shackleton`: Exact grid from `moon_elevation_463m.tif` (35×35).
   - `ATLAS_DATA.kharan`: Exact grid downsampled by Flask (120×120).
   - `ATLAS_DATA.thar`: Exact grid downsampled by Flask (120×120).
   - `ATLAS_DATA.cholistan`: Exact grid downsampled by Flask (86×120).
2. Update `static/app.js` with smart data sourcing:
   - When running on `http://127.0.0.1:5000` (Flask): fetches from `/api/...`.
   - If fetch fails or if running via `file:///` protocol (double-clicked) or on static GitHub Pages: seamlessly falls back to `window.ATLAS_DATA`.
   - **Result:** Identical 3D interactive Plotly visualizer and similarity rankings in both modes without dummy data and without breaking.
3. Root `index.html`:
   - Create a clean root `index.html` referencing `static/style.css`, `static/atlas_data.js`, and `static/app.js`.
   - In `templates/index.html`, retain the Jinja version for Flask, ensuring both have identical content and layout.

### 5.3 Upgraded Launcher (`START_ATLAS.bat`)
Create a robust launcher that:
1. Detects `.venv\Scripts\python.exe` first; falls back to `py -3.13`, `python3`, or `python`.
2. Tests for required dependencies (`Flask`, `rasterio`, `scipy`).
3. Starts the server and opens `http://127.0.0.1:5000` in the user's default browser.
4. Uses correct case `src/backend/app.py`.

---

## 6. GitHub & GitHub Pages Deployment Strategy

### 6.1 Large Files & Git LFS Strategy

Our scan identified the following large files:
- `data/raw/mars/megt44n000hb.img`: **123.75 MB** (exceeds GitHub's 100 MB hard limit; push will be rejected without LFS).
- `data/processed/thar_elevation.tif`: **95.60 MB** (exceeds GitHub's 50 MB warning threshold).
- `data/processed/kharan_elevation.tif`: **67.25 MB** (exceeds GitHub's 50 MB warning threshold).
- `data/raw/mars/megc44n000hb.img`: **61.88 MB** (exceeds GitHub's 50 MB warning threshold).

**Action Plan:**
1. Configure `.gitattributes` to track `*.img` and `*.tif` with Git LFS:
   ```gitattributes
   *.tif filter=lfs diff=lfs merge=lfs -text
   *.img filter=lfs diff=lfs merge=lfs -text
   *.zip filter=lfs diff=lfs merge=lfs -text
   ```
2. Create a comprehensive `.gitignore` ignoring:
   - `.venv/`, `venv/`, `env/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`
   - OS artifacts (`Thumbs.db`, `.DS_Store`)
   - Backup files (`*.bak`, `*.backup`, `encoding_backups/`)
3. Document data provenance and access in `README.md` so users cloning without LFS can download raw files or use the provided harmonized rasters.

### 6.2 GitHub Pages Configuration
- GitHub Pages can serve directly from the repository root (`/`) using root `index.html`.
- Asset paths are purely relative (`static/style.css`, `static/atlas_data.js`, `static/app.js`), ensuring complete compatibility whether deployed at `https://<username>.github.io/<repo>/` or locally.

---

## 7. Phased Implementation Steps

### Phase 1: Pre-Modification Backup
- Create an immutable backup directory: `encoding_backups/pre_repair_20261115/`.
- Back up `templates/index.html`, `static/app.js`, `static/style.css`, `src/backend/app.py`, `requirements.txt`, `README.md`, and `START_ATLAS.bat`.

### Phase 2: Unicode & Mojibake Repair
- Perform targeted replacements in `templates/index.html`:
  - Replace all `Â·` with `·`.
  - Replace all `â€”` with `—`, `â€“` with `–`, `â†’` with `→`.
  - Replace mathematical symbols: `âˆš` -> `√`, `âˆ‚` -> `∂`, `Â²` -> `²`, `Ã—` -> `×`, `Ï€` -> `π`, `Ïƒ` -> `σ`, `Î£` -> `Σ`, `Î”` -> `Δ`, `âˆ’` -> `−`.
  - Replace variable indices: `záµ¢` -> `zᵢ`, `zÌ„` -> `z̄`, `Sáµ¢` -> `Sᵢ`, `Aáµ¢` -> `Aᵢ`, `Báµ¢` -> `Bᵢ`, `Sâ‚ ` -> `S₁`, etc., `wâ‚›` -> `wₛ`, `wáµ£` -> `wᵣ`.
  - Fix dropdown options: remove `\x9d` artifacts.
- Transcode `requirements.txt` to UTF-8 without BOM, and append `scipy==1.18.1`.
- Normalize UTF-8 BOM in Python scripts and markdown files to standard UTF-8.
- Run automated post-repair regex validation to ensure 0 mojibake signatures remain.

### Phase 3: HTML Structure Normalization
- Fix the DOM layout in `templates/index.html`:
  - Close `<footer>` only at the true bottom of the page.
  - Place all `<section>` elements in proper semantic sequence within `<main>`.
  - Position scripts immediately before `</body>`.
- Ensure `<meta charset="UTF-8">` is explicitly declared.

### Phase 4: Standalone Export & Dual-Mode Integration
- Run an export script to generate `static/atlas_data.js` containing real, verified data from all 6 endpoints.
- Update `static/app.js` with fallback logic to support both Flask API fetch and static/offline loading.
- Create root `index.html` for direct double-click access and GitHub Pages compatibility.

### Phase 5: Repository & Launcher Optimization
- Create `.gitignore`.
- Create `.gitattributes` for Git LFS.
- Normalize path cases: verify `src/backend/app.py` references.
- Upgrade `START_ATLAS.bat` with environment detection and clear console messaging.

### Phase 6: Documentation Overhaul (`README.md`)
- Update `README.md` with:
  1. Title and official tagline: *"Earth is our testing ground. Space is our frontier."*
  2. NASA Space Apps Challenge 2026 context and project goals.
  3. Study locations (Kharan, Thar, Cholistan, Jezero Crater, Shackleton Crater).
  4. Exact mathematical equations in GitHub-flavored LaTeX.
  5. Verified findings (Kharan #1 for Mars at 66.41%, Moon at 13.04%).
  6. Distinction between terrain screening and planetary qualification.
  7. Dual launch instructions (Flask app vs standalone HTML).
  8. Git LFS, repository structure, and data sources.
  9. Disclosure on Unicode repair and AI transparency.

### Phase 7: Verification & Final Deployment Report
- Execute comprehensive testing:
  - Python test client for all 8 Flask endpoints.
  - Headless/browser validation of standalone `index.html` loading.
  - Verification of Plotly 3D visualizers for Jezero, Shackleton, Kharan, Thar, and Cholistan.
  - Post-repair encoding audit across all files.
- Produce `FINAL_DEPLOYMENT_REPORT.md`.

---

## 8. Verification Matrix & Acceptance Criteria

| Component | Target State | Verification Method |
|---|---|---|
| **Encoding** | 0 mojibake characters, clean UTF-8 across all files | Automated regex scan across all repo text files |
| **Requirements** | UTF-8, no BOM, includes `scipy==1.18.1` | `pip install -r requirements.txt` dry-run |
| **Flask Endpoints** | All 8 endpoints return HTTP 200 with valid JSON/HTML | Python `test_client()` test suite |
| **3D Visualizers** | Plotly renders 5 terrains (Jezero, Shackleton, 3 Earth) | DOM element verification & Plotly data binding |
| **Similarity Model** | Matches verified values (Kharan: 66.41% Mars, 13.04% Moon) | Equality check against `harmonized_similarity_results.csv` |
| **Standalone Entry** | Double-clicking `index.html` works without server | File protocol load check |
| **GitHub Readiness** | Git LFS tracking configured, clean `.gitignore`, correct paths | `git status` and path case verification |
