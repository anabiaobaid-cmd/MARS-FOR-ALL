# MARS FOR ALL — The Analog Atlas

> **Tagline:** Earth is our testing ground. Space is our frontier.  
> **Challenge:** NASA Space Apps Challenge 2026  
> **Research Track:** Planetary Terrain Science, Comparative Geomorphology & Analog Exploration  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Research Question & Objectives](#2-research-question--objectives)
3. [Study Locations (Earth, Moon & Mars)](#3-study-locations-earth-moon--mars)
4. [Data Sources & Planetary Archives](#4-data-sources--planetary-archives)
5. [Data Processing & Resolution Harmonization](#5-data-processing--resolution-harmonization)
6. [Mathematical Framework & Scientific Equations](#6-mathematical-framework--scientific-equations)
7. [Verified Quantitative Results](#7-verified-quantitative-results)
8. [Interactive Features & Platform Architecture](#8-interactive-features--platform-architecture)
9. [Scientific Limitations & Uncertainty Disclosures](#9-scientific-limitations--uncertainty-disclosures)
10. [Dual-Mode Access & Running the Application](#10-dual-mode-access--running-the-application)
11. [GitHub Pages Deployment](#11-github-pages-deployment)
12. [Repository Structure & Large File Management (Git LFS)](#12-repository-structure--large-file-management-git-lfs)
13. [Dependencies & Installation](#13-dependencies--installation)
14. [Unicode Compatibility & Scientific Notation Note](#14-unicode-compatibility--scientific-notation-note)
15. [AI Transparency & Attribution](#15-ai-transparency--attribution)

---

## 1. Project Overview

Planetary exploration increasingly depends on understanding the physical characteristics of extraterrestrial landscapes. While crewed and robotic missions cannot test landing and mobility systems on other worlds beforehand, Earth-based analog research offers an empirical opportunity to investigate measurable similarities between terrestrial and extraterrestrial environments.

**MARS FOR ALL — The Analog Atlas** approaches this challenge through quantitative terrain comparison rather than qualitative visual resemblance alone. The platform brings together three terrestrial landscapes in Pakistan (Kharan, Thar, and Cholistan), a Martian reference environment (Jezero Crater), and a lunar south-polar site (Shackleton Crater Rim) into a unified, harmonized comparative framework.

By combining open planetary elevation datasets, rigorous terrain processing, multi-scenario similarity screening, and three-dimensional interactive visualizations, the Atlas provides researchers, students, and mission designers with a traceable baseline for analog terrain screening.

---

## 2. Research Question & Objectives

### Central Research Question
> **To what extent do selected Pakistani landscapes exhibit measurable topographic similarities to selected lunar and Martian terrain environments under harmonized spatial scales?**

### Key Scientific Objectives
1. **Harmonize Heterogeneous Datasets:** Resample diverse terrestrial and planetary digital elevation models to a common spatial grid cell resolution (~463 metres/pixel).
2. **Extract Robust Morphometric Features:** Derive slope and surface roughness metrics across all study regions using central-difference gradients and moving-window statistics.
3. **Screen Feature-Level Resemblance:** Apply ratio-based similarity scoring across slope and roughness distributions to assess topographic proximity.
4. **Evaluate Model Robustness:** Test stability across alternative weighting scenarios (Balanced 50/50, Slope Emphasis 70/30, Roughness Emphasis 30/70) to establish sensitivity ranges.
5. **Maintain Research Integrity:** Quantify source observation coverage, grid validity, and elevation uncertainty, distinguishing numerical terrain screening from geological equivalence.

---

## 3. Study Locations (Earth, Moon & Mars)

| Region | Body | Type | Coordinates / Context | Topographic Character |
|---|---|---|---|---|
| **Kharan** | Earth (Pakistan) | Terrestrial Candidate | Western Balochistan | Basin floor with transverse/barchan dunes, alluvial fans, and bedrock ridges |
| **Thar** | Earth (Pakistan) | Terrestrial Candidate | Southeastern Sindh | Vast stabilized and active longitudinal/transverse sand seas with low relief |
| **Cholistan** | Earth (Pakistan) | Terrestrial Candidate | Southern Punjab | Hyper-arid desert plain with low-gradient longitudinal sand dunes |
| **Jezero Crater** | Mars | Planetary Reference | $18.38^\circ\text{N}, 77.58^\circ\text{E}$ | Ancient lake basin, delta deposits, impact crater rim, and volcanic plain |
| **Shackleton Rim** | Moon | Planetary Reference | $89.9^\circ\text{S}, 0.0^\circ\text{E}$ (South Pole) | Deep impact crater rim with extreme slopes, permanent shadow, and rough cratered topography |

---

## 4. Data Sources & Planetary Archives

The project uses authentic open-access elevation datasets published by NASA and international planetary science archives:

1. **Earth Datasets:**
   - **Source:** NASA Shuttle Radar Topography Mission (SRTM) Global 1 Arc-Second (~30 m resolution), Version 3 (`SRTMGL1.003`).
   - **Coverage:** Tiles spanning Kharan (`N27E064`–`N28E065`), Thar (`N24E070`–`N26E071`), and Cholistan (`N27E070`–`N29E071`).
2. **Mars Datasets:**
   - **Source:** Mars Global Surveyor (MGS) Mars Orbiter Laser Altimeter (MOLA) Mission Experiment Gridded Data Record (MEGDR).
   - **Products:** `megc44n000hb` (counts) and `megt44n000hb` (topography) at 128 pixels/degree (~463 m/pixel at equator).
   - **Archive:** NASA Planetary Data System (PDS) Geosciences Node.
3. **Moon Datasets:**
   - **Source:** Lunar Reconnaissance Orbiter (LRO) Lunar Orbiter Laser Altimeter (LOLA).
   - **Products:** LOLA South Pole 5 mpp Site04 products (`Site04_final_adj_5mpp_ldec.tif`, `slp.tif`, `surf.tif`, `slperr.tif`, `toterr.tif`), downscaled to 463 m.
   - **Archive:** NASA Planetary Geodynamics Data Archive (PGDA Product 78).
4. **Key Scientific References:**
   - Mazarico, E., et al. (2011). *Illumination conditions of the lunar polar regions using LOLA topography*. Icarus, 211(2), 1066–1081.
   - Barker, M. K., et al. (2021). *LOLA elevation maps for lunar south-pole sites*. Planetary and Space Science, 203, 105119.

---

## 5. Data Processing & Resolution Harmonization

Directly comparing a 30 m terrestrial DEM with a 5 m lunar DEM or a 463 m Mars DEM creates severe resolution-dependent artifacts. The project harmonizes all candidate and reference rasters onto a common analysis resolution:

- **Target Analysis Resolution:** $463.0577\text{ m/pixel}$ (the native equatorial resolution of MOLA 128 ppd).
- **Coordinate Reference Systems:**
  - Earth: Geographic WGS 84 (`EPSG:4326`) and UTM projected coordinates.
  - Mars: Equirectangular sphere ($R_{\text{Mars}} = 3,396,000\text{ m}$).
  - Moon: Lunar South Pole Stereographic projection.
- **Valid Observation Filtering:** Masked rasters retain only cells with valid physical elevation readings. Missing observation counts and laser altimetry uncertainties are mapped independently.

---

## 6. Mathematical Framework & Scientific Equations

Every mathematical expression implemented in the codebase is documented below and verified against `src/analysis/harmonized_terrain_analysis.py` and `src/analysis/planetary_similarity_harmonized.py`.

### 6.1 Terrain Slope ($S$)
Slope is derived from central-difference horizontal elevation gradients in physical metres:

$$S = \tan^{-1}\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180}{\pi}$$

Where:
- $S$ = Terrain slope in degrees ($^\circ$).
- $z$ = Surface elevation in metres ($m$).
- $\frac{\partial z}{\partial x}, \frac{\partial z}{\partial y}$ = First spatial partial derivatives of elevation computed via 2D numpy gradient.
- $dx, dy$ = Pixel grid spacing in metres ($463.0577\text{ m}$).
- *Mars Equirectangular Latitude Correction:*
  $$dx = dx_{\text{deg}} \times \left(\frac{\pi}{180}\right) R_{\text{Mars}} \cos(\phi_{\text{center}})$$
  where $R_{\text{Mars}} = 3,396,000\text{ m}$ and $\phi_{\text{center}}$ is the scene central latitude.

### 6.2 Terrain Roughness ($R$)
Local surface roughness is defined as the moving standard deviation of elevation within a complete $3 \times 3$ neighbourhood ($n = 9$ valid observations):

$$R = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (z_i - \bar{z})^2} = \sqrt{\overline{z^2} - (\bar{z})^2}$$

Where:
- $R$ = Local elevation roughness in metres ($m$).
- $z_i$ = Individual elevation values within the $3 \times 3$ moving window.
- $\bar{z}$ = Mean elevation within the $3 \times 3$ window, computed via uniform filtering.
- Neighbourhood validation: Only pixels surrounded by 9 valid neighbours (`uniform_filter(valid) >= 1.0 - 1e-9`) are retained.

### 6.3 Regional Morphometric Summary Features
For each region, slope and roughness distributions across all valid terrain cells are summarized into three key statistics:
- **Mean:** $\mu = \frac{1}{N}\sum_{j=1}^{N} x_j$
- **Median:** $P_{50}$ (50th percentile)
- **High-End Tail (P90):** $P_{90}$ (90th percentile)

Yielding 6 comparative features:
$$\mathbf{f}_{\text{slope}} = [S_{\text{mean}}, S_{\text{median}}, S_{P90}], \quad \mathbf{f}_{\text{rough}} = [R_{\text{mean}}, R_{\text{median}}, R_{P90}]$$

### 6.4 Feature-Level Similarity ($S_i$)
Each Earth candidate feature is compared against the corresponding reference feature using a bounded ratio metric:

$$S(f_{\text{ref}}, f_{\text{cand}}) = 100 \times \frac{\min(|f_{\text{ref}}|, |f_{\text{cand}}|)}{\max(|f_{\text{ref}}|, |f_{\text{cand}}|)}$$

If $\max(|f_{\text{ref}}|, |f_{\text{cand}}|) = 0$, $S(f_{\text{ref}}, f_{\text{cand}}) = 100\%$. The score ranges strictly between $0\%$ and $100\%$.

### 6.5 Group Similarities ($S_{\text{slope}}$, $S_{\text{roughness}}$)
The three slope-feature scores and three roughness-feature scores are averaged within their respective groups:

$$S_{\text{slope}} = \frac{1}{3} \sum_{k=1}^{3} S(f_{\text{slope, ref}, k}, f_{\text{slope, earth}, k})$$

$$S_{\text{roughness}} = \frac{1}{3} \sum_{k=1}^{3} S(f_{\text{rough, ref}, k}, f_{\text{rough, earth}, k})$$

### 6.6 Weighted Overall Similarity ($S_{\text{overall}}$)
Overall terrain similarity combines the slope and roughness group scores via weighting coefficients:

$$S_{\text{overall}} = w_{\text{slope}} S_{\text{slope}} + w_{\text{roughness}} S_{\text{roughness}}$$

Where $w_{\text{slope}} + w_{\text{roughness}} = 1.0$.

Three sensitivity scenarios are formally evaluated:
1. **Balanced Scenario:** $w_{\text{slope}} = 0.50, \quad w_{\text{roughness}} = 0.50$
2. **Slope Emphasis:** $w_{\text{slope}} = 0.70, \quad w_{\text{roughness}} = 0.30$
3. **Roughness Emphasis:** $w_{\text{slope}} = 0.30, \quad w_{\text{roughness}} = 0.70$

---

## 7. Verified Quantitative Results

All values reported below are computed directly from the harmonized data pipeline (`harmonized_terrain_metrics.csv` and `harmonized_similarity_results.csv`):

### 7.1 Harmonized Terrain Metrics Summary (at 463 m Resolution)

| Region | Mean Elev ($m$) | Mean Slope ($^\circ$) | Median Slope ($^\circ$) | P90 Slope ($^\circ$) | Mean Rough ($m$) | Median Rough ($m$) | P90 Rough ($m$) | Valid Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Jezero (Mars)** | -2325.27 | 3.73 | 2.67 | 7.92 | 26.46 | 19.61 | 52.79 | 32.45% |
| **Shackleton (Moon)** | +228.51 | 20.14 | 19.79 | 32.00 | 144.26 | 134.51 | 236.52 | 100.00% |
| **Kharan (Earth)** | +1050.24 | 2.57 | 1.18 | 6.63 | 18.29 | 8.89 | 46.16 | 97.10% |
| **Thar (Earth)** | +92.63 | 0.54 | 0.37 | 1.26 | 3.91 | 3.14 | 8.33 | 97.78% |
| **Cholistan (Earth)** | +119.21 | 0.31 | 0.17 | 0.76 | 2.28 | 1.40 | 5.47 | 96.84% |

### 7.2 Multi-Scenario Similarity Results

#### Mars Reference — Jezero Crater
| Earth Candidate | Balanced ($w_s=0.5, w_r=0.5$) | Slope Emphasis ($w_s=0.7, w_r=0.3$) | Roughness Emphasis ($w_s=0.3, w_r=0.7$) | Sensitivity Range | Rank |
|---|---:|---:|---:|---:|:---:|
| **Kharan** | **66.41%** | 66.06% | 66.76% | 0.70% | **#1** |
| **Thar** | **15.10%** | 14.93% | 15.27% | 0.34% | **#2** |
| **Cholistan** | **8.41%** | 8.29% | 8.53% | 0.24% | **#3** |

#### Lunar Reference — Shackleton Crater Rim
| Earth Candidate | Balanced ($w_s=0.5, w_r=0.5$) | Slope Emphasis ($w_s=0.7, w_r=0.3$) | Roughness Emphasis ($w_s=0.3, w_r=0.7$) | Sensitivity Range | Rank |
|---|---:|---:|---:|---:|:---:|
| **Kharan** | **13.04%** | 13.08% | 12.99% | 0.08% | **#1** |
| **Thar** | **2.84%** | 2.83% | 2.85% | 0.02% | **#2** |
| **Cholistan** | **1.62%** | 1.61% | 1.63% | 0.02% | **#3** |

### 7.3 Key Findings
1. **Consistent Hierarchy:** Kharan ranks #1 among the three Pakistani regions for both Jezero Crater and Shackleton Crater across all three weighting scenarios.
2. **Terrain Scale Contrast:** Jezero exhibits moderate slopes and roughness that align closely with Kharan's basin-and-range topography. In contrast, Shackleton's extreme lunar polar slopes ($20.14^\circ$ mean) significantly exceed all terrestrial dune landscapes studied.
3. **Model Stability:** The sensitivity range across weighting scenarios is narrow ($\le 0.70\%$), demonstrating that regional rankings are robust against variations in feature weighting.

---

## 8. Interactive Features & Platform Architecture

The platform provides a responsive, high-performance visual experience:
- **Jezero Crater 3D Viewer:** Interactive WebGL 3D surface mesh rendered via Plotly.js with elevation-encoded colormap.
- **Shackleton Crater 3D Viewer:** Interactive 3D lunar polar topography viewer.
- **Three Terrestrial 3D Viewers:** Independent 3D terrain viewers for Kharan, Thar, and Cholistan.
- **Dynamic Reference Selector:** Switch seamlessly between Mars (Jezero) and Moon (Shackleton) comparisons to inspect live similarity rankings and coverage data.
- **Deep Science Sections:** Mathematical framework, uncertainty analysis, methodology, and data traceability documentation.

---

## 9. Scientific Limitations & Uncertainty Disclosures

Responsible planetary science demands clear disclosure of limitations:

1. **Screening vs Qualification:** This project implements an initial *terrain-similarity screening model*. High similarity scores indicate numerical resemblance in slope and roughness distributions at 463 m/pixel; they **do not** constitute planetary analog qualification.
2. **Geological & Environmental Non-Equivalence:** Topographic similarity does not imply identical mineralogy, geological age, regolith mechanics, vacuum conditions, radiation environments, or atmospheric dynamics.
3. **Scale Sensitivity:** Terrain properties are fractal and scale-dependent. Surface roughness at 463 m resolution does not predict boulder distribution or centimetre-scale rover trafficability.
4. **Observation Disparities:** The lunar south pole LOLA dataset contains 9.15% direct laser observation coverage within the harmonized target grid (interrupted by permanently shadowed regions and orbital geometry).

---

## 10. Dual-Mode Access & Running the Application

The Analog Atlas implements **Option C Architecture**, providing two complementary modes of operation:

### Mode 1: Instant Standalone Access (No Python Required)
You can open and demonstrate the entire platform directly in any modern browser without installing Python or running a server:

1. Double-click `index.html` (or run `START_STANDALONE.bat` on Windows).
2. The application loads the pre-packaged, verified research dataset (`static/atlas_data.js`).
3. All interactive Plotly 3D visualizers, similarity switching, and research sections work completely offline or over `file:///`.

### Mode 2: Complete Local Flask Application
To run the full dynamic Python backend with live raster processing and API endpoints:

1. Open PowerShell or Command Prompt in the repository root.
2. Run the one-click Windows launcher:
   ```cmd
   START_ATLAS.bat
   ```
   *The launcher automatically detects virtual environments (`.venv` or `venv`), falls back to available Python launchers, launches `src/backend/app.py`, and opens `http://127.0.0.1:5000` in your default browser.*

3. Alternatively, launch manually via CLI:
   ```bash
   py -3.13 src/backend/app.py
   ```

#### Verified API Endpoints:
- `http://127.0.0.1:5000/` — Main Application Interface
- `http://127.0.0.1:5000/api/terrain` — Harmonized Terrain Metrics (JSON)
- `http://127.0.0.1:5000/api/similarity` — Multi-Scenario Similarity Results (JSON)
- `http://127.0.0.1:5000/api/jezero-elevation` — Jezero Crater 3D Elevation Grid
- `http://127.0.0.1:5000/api/shackleton-elevation` — Shackleton Crater 3D Elevation Grid
- `http://127.0.0.1:5000/api/earth-elevation/kharan` — Kharan 3D Elevation Grid
- `http://127.0.0.1:5000/api/earth-elevation/thar` — Thar 3D Elevation Grid
- `http://127.0.0.1:5000/api/earth-elevation/cholistan` — Cholistan 3D Elevation Grid

---

## 11. GitHub Pages Deployment

The repository is pre-configured for instant zero-configuration static publishing via GitHub Pages:

1. Push the repository to GitHub.
2. In your repository settings, navigate to **Pages** (under Code and automation).
3. Under **Build and deployment > Source**, select **Deploy from a branch**.
4. Choose `main` (or `master`) branch and set folder to `/ (root)`.
5. Click **Save**. Within 1–2 minutes, your Atlas will be live at:
   `https://<your-username>.github.io/<repository-name>/`

All relative asset paths (`static/style.css`, `static/atlas_data.js`, `static/app.js`) are compatible with GitHub repository subdirectories.

---

## 12. Repository Structure & Large File Management (Git LFS)

### 12.1 Directory Structure

```text
MARS_FOR_ALL/
├── .gitattributes          # Git LFS configuration for rasters and archives
├── .gitignore              # Clean ignore rules for virtualenvs, caches, and backups
├── FINAL_DEPLOYMENT_PLAN.md# Architectural deployment and audit plan
├── FINAL_DEPLOYMENT_REPORT.md # Verification and completion report
├── README.md               # Master documentation and scientific framework
├── requirements.txt        # Verified Python dependencies (UTF-8, no BOM)
├── START_ATLAS.bat         # One-click launcher for dynamic Flask backend
├── START_STANDALONE.bat    # One-click launcher for static standalone demo
├── index.html              # Standalone & GitHub Pages entry point
│
├── data/
│   ├── processed/          # Processed elevation grids & CSV similarity tables
│   │   ├── harmonized/     # 463 m harmonized rasters (Jezero, Moon, Earth)
│   │   └── *.tif, *.csv
│   └── raw/                # Source SRTM, MOLA, and LOLA datasets
│
├── docs/
│   └── mathematical_uncertainty_report.md
│
├── src/
│   ├── analysis/           # Python scientific processing scripts
│   │   ├── harmonized_terrain_analysis.py
│   │   ├── planetary_similarity_harmonized.py
│   │   └── ...
│   └── backend/            # Flask server application
│       └── app.py
│
├── static/
│   ├── app.js              # Dual-mode Plotly 3D visualizer logic
│   ├── atlas_data.js       # Pre-rendered research data payload (763 KB)
│   └── style.css           # Responsive scientific visual stylesheet
│
└── templates/
    └── index.html          # Jinja template for Flask server
```

### 12.2 Large File Management (Git LFS)
The repository contains large planetary and terrestrial rasters. GitHub enforces a 100 MB maximum file limit and issues warnings above 50 MB:
- `data/raw/mars/megt44n000hb.img`: **123.75 MB** (>100 MB GitHub limit)
- `data/processed/thar_elevation.tif`: **95.60 MB** (>50 MB warning)
- `data/processed/kharan_elevation.tif`: **67.25 MB** (>50 MB warning)
- `data/raw/mars/megc44n000hb.img`: **61.88 MB** (>50 MB warning)

These file types are formally tracked via `.gitattributes` using **Git Large File Storage (Git LFS)**:
```gitattributes
*.tif filter=lfs diff=lfs merge=lfs -text
*.img filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
```

To clone with full raster datasets:
```bash
git lfs install
git clone https://github.com/YOUR-USERNAME/MARS-FOR-ALL.git
```

---

## 13. Dependencies & Installation

### Environment Requirements
- Python 3.10, 3.11, 3.12, or 3.13
- Git and Git LFS

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/MARS-FOR-ALL.git
cd MARS-FOR-ALL

# Create a virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install verified dependencies
pip install -r requirements.txt
```

---

## 14. Unicode Compatibility & Scientific Notation Note

During development and multi-platform testing, character encoding audits identified mojibake corruption where UTF-8 characters were improperly decoded as Windows-1252. Corrupted artifacts (such as `Â·`, `â€”`, `âˆ‚`, `âˆš`, `Ã—`, `Ï€`, `záµ¢`, and `Sáµ¢`) affected scientific headings, mathematical formulas, and coordinate degree symbols.

A comprehensive repair stage was performed:
- All source files were normalized to **clean UTF-8 without byte-order marks (BOM)**.
- HTML documents explicitly declare `<meta charset="UTF-8">`.
- Mathematical formulas, Greek variables ($\partial, \sigma, \Sigma, \Delta, \pi$), subscripts ($z_i, \bar{z}, S_i, w_s, w_r$), and operators ($\sqrt{\cdot}, \times, -, \rightarrow$) have been fully restored and verified.
- Complete GitHub-compatible Markdown LaTeX equations are documented in this README to guarantee clear, unambiguous scientific presentation across all devices.

---

## 15. AI Transparency & Attribution

AI coding tools were utilized to assist in code auditing, encoding repair, documentation organization, and dual-mode standalone packaging. All scientific methodology, elevation rasters, mathematical formulas, and quantitative comparisons were derived directly from NASA source data and verified against Python analysis scripts.

---

**MARS FOR ALL — The Analog Atlas**  
*Earth is our testing ground. Space is our frontier.*  
NASA Space Apps Challenge 2026
