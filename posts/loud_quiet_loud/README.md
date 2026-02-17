# Loud-Quiet-Loud: Dynamics Analysis

This project analyzes the "Loud-Quiet-Loud" dynamic structure in the music of **The Pixies**, comparing their transition patterns against a control group (Sonic Youth, Hüsker Dü, The Smiths).

## Methodology: Hybrid Segmentation

We developed a custom **Hybrid Segmentation** algorithm to accurately identify structural boundaries based on two factors:

1.  **Harmonic Structure**: Uses `librosa` (Recurrence Matrix, Spectral Clustering) to find musical sections (Verse, Chorus) based on chord progressions.
2.  **Dynamic Structure**: Uses `ruptures` (Change Point Detection, Pelt algorithm) to find significant shifts in loudness (dB).

The algorithm fuses these boundaries to create a robust segmentation that captures the macro-level structure of the songs.

### Key Parameters (Refined)
To capture the specific "step-function" dynamics of the Pixies and avoid over-segmentation (e.g., getting 26 transitions when there should be ~9), we use the following tuned parameters:

*   **Minimum Segment Size**: `5.0` seconds (ignores transient noise).
*   **Penalty (`pen`)**: `25.0` (Standardized Signal). Higher penalty reduces sensitivity to minor fluctuations.
*   **Boundary Fusion**: Transitions occurring within `2.0` seconds of each other are merged.

## Repository Structure

*   **`analyze_dynamics.py`**: The main script. Iterates through the `data/` directory, runs the segmentation pipeline on every track, calculates transition metrics (Count, Average Magnitude), and generates plots.
*   **`segmentation_pipeline.py`**: Contains the `HybridSegmenter` class. This is the core logic for the analysis.
*   **`data/`**: Directory containing the audio files (organized by Artist/Album).
*   **`output/`**: Generated plots and analysis artifacts.
    *   `segmentation_*.png`: overlay of boundaries on loudness trace for each track.
    *   `transition_analysis_full.png`: Final scatter plot comparing Pixies vs. Control.

## Installation & Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
# Requires: librosa, ruptures, numpy, pandas, matplotlib, scikit-learn
```

### 2. Run the Analysis
To process the full dataset (Pixies + Control) and generate all plots:

```bash
python3 analyze_dynamics.py
```

This will:
1.  Scan `data/` for MP3 files.
2.  Analyze each track (this takes time, ~10-20 seconds per track).
3.  Save individual segmentation plots to `output/`.
4.  Generate a final `transition_analysis_full.png` scatter plot.

## Results
The analysis successfully identifies songs like **"Where Is My Mind?"** and **"Tame"** as outliers with high-magnitude, frequent transitions, quantitatively defining the "Loud-Quiet-Loud" aesthetic.
