/**
 * MARS FOR ALL — The Analog Atlas
 * Terrain Visualizer and Similarity Explorer
 * 
 * Architecture:
 * - Operates in dual mode:
 *   1. Dynamic Server Mode: Queries /api/* Flask endpoints when hosted on Flask.
 *   2. Standalone / Offline Mode: Seamlessly falls back to window.ATLAS_DATA
 *      when running without Flask, via file:/// protocol, or on GitHub Pages.
 */

// Helper to retrieve data from API or static bundle
async function fetchAtlasData(apiPath, staticKeyExtractor) {
    // If not running over http/https (e.g. file:///), use preloaded bundle directly
    if (window.location.protocol === "file:") {
        if (window.ATLAS_DATA) {
            return staticKeyExtractor(window.ATLAS_DATA);
        }
    }

    try {
        const response = await fetch(apiPath);
        if (response.ok) {
            return await response.json();
        }
    } catch (err) {
        // Fall back to preloaded static bundle if available
    }

    if (window.ATLAS_DATA) {
        return staticKeyExtractor(window.ATLAS_DATA);
    }

    throw new Error(`Data source unavailable for ${apiPath}`);
}

async function loadSimilarity(reference = "Jezero") {
    const container = document.getElementById("similarity-results");
    const status = document.getElementById("data-status");
    const title = document.getElementById("comparison-title");

    if (!container || !title) return;

    try {
        if (status) status.textContent = "Loading research data...";

        const results = await fetchAtlasData(
            "/api/similarity",
            data => data.similarity
        );

        const selectedResults = results
            .filter(item =>
                item.reference === reference &&
                item.scenario === "Balanced"
            )
            .sort((a, b) => a.rank - b.rank);

        if (selectedResults.length === 0) {
            throw new Error("No results available for " + reference);
        }

        title.textContent = reference === "Jezero"
            ? "Jezero vs Earth"
            : "Shackleton vs Earth";

        container.innerHTML = selectedResults.map(item => `
            <div class="card result-card">
                <div class="eyebrow">RANK #${item.rank}</div>
                <h3>${item.earth_region}</h3>
                <div class="score">
                    ${Number(item.overall_similarity).toFixed(2)}%
                </div>
                <p>Heuristic terrain-feature similarity</p>
                <p>
                    Earth data coverage:
                    ${Number(item.earth_data_coverage_percent).toFixed(1)}%
                </p>
                <p>
                    Reference observation coverage:
                    ${Number(item.reference_observation_coverage_percent).toFixed(2)}%
                </p>
            </div>
        `).join("");

        if (status) {
            status.textContent = "Live results loaded from our processed research dataset.";
        }

    } catch (error) {
        if (status) status.textContent = error.message;
        container.innerHTML =
            '<div class="card">Comparison data is currently unavailable.</div>';
    }
}


async function loadJezero3D() {
    const viewer = document.getElementById("jezero-3d");
    if (!viewer) return;

    try {
        viewer.textContent = "Loading NASA elevation data...";

        if (typeof Plotly === "undefined") {
            throw new Error("Plotly could not be loaded.");
        }

        const terrain = await fetchAtlasData(
            "/api/jezero-elevation",
            data => data.jezero
        );

        const surface = {
            type: "surface",
            x: terrain.x,
            y: terrain.y,
            z: terrain.z,
            connectgaps: false,
            colorscale: [
                [0, "#8EDCFF"],
                [0.25, "#B5E8FF"],
                [0.5, "#D5F3FF"],
                [0.75, "#FF8C00"],
                [1, "#FF4500"]
            ],
            colorbar: {
                title: {
                    text: "ELEVATION (m)",
                    font: { size: 15, color: "#e2e8f0" }
                },
                tickfont: { color: "#cbd5e1" }
            },
            hovertemplate:
                "Easting: %{x:.0f} m<br>" +
                "Northing: %{y:.0f} m<br>" +
                "Elevation: %{z:.1f} m" +
                "<extra></extra>"
        };

        const layout = {
            autosize: true,
            paper_bgcolor: "#111a2b",
            font: {
                color: "#f2f5fc",
                family: "DM Sans, sans-serif"
            },
            margin: { l: 10, r: 10, t: 35, b: 10 },
            scene: {
                bgcolor: "#111a2b",
                aspectmode: "manual",
                aspectratio: { x: 1, y: 1, z: 0.18 },
                xaxis: {
                    title: "Easting (m)",
                    gridcolor: "#334155"
                },
                yaxis: {
                    title: "Northing (m)",
                    gridcolor: "#334155"
                },
                zaxis: {
                    title: "Elevation (m)",
                    gridcolor: "#334155"
                },
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 0.8 }
                }
            }
        };

        await Plotly.newPlot(viewer, [surface], layout, {
            responsive: true,
            displaylogo: false,
            scrollZoom: true
        });

    } catch (error) {
        viewer.textContent =
            "Jezero terrain could not be loaded: " + error.message;
    }
}


async function loadShackleton3D() {
    const viewer = document.getElementById("shackleton-3d-viewer");
    if (!viewer) return;

    try {
        viewer.textContent = "Loading lunar elevation data...";

        if (typeof Plotly === "undefined") {
            throw new Error("Plotly could not be loaded.");
        }

        const terrain = await fetchAtlasData(
            "/api/shackleton-elevation",
            data => data.shackleton
        );

        const surface = {
            type: "surface",
            x: terrain.x,
            y: terrain.y,
            z: terrain.z,
            connectgaps: false,
            colorscale: [
                [0, "#10243D"],
                [0.25, "#256B91"],
                [0.5, "#70C5D8"],
                [0.75, "#C5E9ED"],
                [1, "#FFFFFF"]
            ],
            colorbar: {
                title: {
                    text: "Elevation (m)",
                    font: { color: "#e2e8f0" }
                },
                tickfont: { color: "#e2e8f0" }
            },
            hovertemplate:
                "Easting: %{x:.0f} m<br>" +
                "Northing: %{y:.0f} m<br>" +
                "Elevation: %{z:.1f} m" +
                "<extra></extra>"
        };

        const layout = {
            autosize: true,
            paper_bgcolor: "#111a2b",
            font: {
                color: "#f2f5fc",
                family: "DM Sans, sans-serif"
            },
            margin: { l: 10, r: 10, t: 35, b: 10 },
            scene: {
                bgcolor: "#111a2b",
                aspectmode: "manual",
                aspectratio: { x: 1, y: 1, z: 0.18 },
                xaxis: {
                    title: "Easting (m)",
                    gridcolor: "#334155"
                },
                yaxis: {
                    title: "Northing (m)",
                    gridcolor: "#334155"
                },
                zaxis: {
                    title: "Elevation (m)",
                    gridcolor: "#334155"
                },
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 0.8 }
                }
            }
        };

        await Plotly.newPlot(viewer, [surface], layout, {
            responsive: true,
            displaylogo: false,
            scrollZoom: true
        });

    } catch (error) {
        viewer.textContent =
            "Shackleton terrain could not be loaded: " + error.message;
    }
}


async function loadEarth3D(region) {
    const viewer = document.getElementById("earth-" + region + "-3d");
    if (!viewer) return;

    const palettes = {
        kharan: [
            [0, "#064E3B"],
            [0.25, "#059669"],
            [0.5, "#34D399"],
            [0.75, "#A3E6B5"],
            [1, "#E5F5C9"]
        ],
        thar: [
            [0, "#075985"],
            [0.25, "#0891B2"],
            [0.5, "#5EEAD4"],
            [0.75, "#D6C08A"],
            [1, "#FDE68A"]
        ],
        cholistan: [
            [0, "#134E4A"],
            [0.25, "#0F766E"],
            [0.5, "#2DD4BF"],
            [0.75, "#D6A84B"],
            [1, "#FDE68A"]
        ]
    };

    try {
        viewer.textContent = "Loading " + region + " terrain...";

        if (typeof Plotly === "undefined") {
            throw new Error("Plotly could not be loaded.");
        }

        const terrain = await fetchAtlasData(
            "/api/earth-elevation/" + region,
            data => data.earth && data.earth[region]
        );

        if (!terrain || !terrain.x || !terrain.y || !terrain.z) {
            throw new Error("Elevation data is incomplete.");
        }

        const elevationGrid = terrain.z.map(row =>
            row.map(value =>
                value === null ? NaN : Number(value)
            )
        );

        const horizontalUnits = terrain.horizontal_units || "metres";

        const surface = {
            type: "surface",
            x: terrain.x,
            y: terrain.y,
            z: elevationGrid,
            connectgaps: false,
            colorscale: palettes[region],
            colorbar: {
                title: {
                    text: "Elevation (m)",
                    font: { color: "#e2e8f0" }
                },
                tickfont: { color: "#e2e8f0" }
            },
            hovertemplate:
                "X: %{x}<br>" +
                "Y: %{y}<br>" +
                "Elevation: %{z:.1f} m" +
                "<extra></extra>"
        };

        const layout = {
            autosize: true,
            paper_bgcolor: "#111a2b",
            font: {
                color: "#f2f5fc",
                family: "DM Sans, sans-serif"
            },
            margin: { l: 10, r: 10, t: 35, b: 10 },
            scene: {
                bgcolor: "#111a2b",
                aspectmode: "manual",
                aspectratio: { x: 1, y: 1, z: 0.18 },
                xaxis: {
                    title: "X (" + horizontalUnits + ")",
                    gridcolor: "#334155"
                },
                yaxis: {
                    title: "Y (" + horizontalUnits + ")",
                    gridcolor: "#334155"
                },
                zaxis: {
                    title: "Elevation (m)",
                    gridcolor: "#334155"
                },
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 0.8 }
                }
            }
        };

        await Plotly.newPlot(viewer, [surface], layout, {
            responsive: true,
            displaylogo: false,
            scrollZoom: true
        });

    } catch (error) {
        console.error(region + " terrain error:", error);
        viewer.textContent =
            region + " terrain could not be loaded: " + error.message;
    }
}

const targetSelector = document.getElementById("target-select");

if (targetSelector) {
    targetSelector.addEventListener("change", function () {
        loadSimilarity(this.value);
    });
}

// Initialise viewers
loadSimilarity();
loadJezero3D();
loadShackleton3D();
loadEarth3D("kharan");
loadEarth3D("thar");
loadEarth3D("cholistan");
