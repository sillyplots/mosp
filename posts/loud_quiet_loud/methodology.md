# Structural Analysis Methodology

This document details the signal processing pipeline used to analyze the structure of tracks in the "Loud-Quiet-Loud" case study.

## Overview
We aim to identify structural boundaries (Verse, Chorus, Bridge) and beats from raw audio. The analysis is performed using the `librosa` Python library.

## Pipeline Steps

### 1. Preprocessing and Beat Tracking
- **Input**: Raw MP3 audio (converted to mono).
- **Beat Tracking**: We use `librosa.beat.beat_track` to estimate the global BPM and identify beat locations.
    - *Note*: This provides the temporal grid for the player visualization.

### 2. Feature Extraction (Chromagram)
To identify structural changes (which correspond to changes in harmony/chords), we compute a **Chromagram**:
- **Constant-Q Transform (CQT)**: We transform the audio into a CQT to map frequencies to the 12 musical pitch classes (C, C#, D, etc.).
- **Stacking**: To capture harmonic *texture* rather than instantaneous notes, we stack valid CQT frames over a ~1-2 second window using `librosa.feature.stack_memory` (n_steps=10, delay=3).

### 3. Structural Segmentation (Hybrid Recurrence)
We combine harmonic and dynamic features to identify structural boundaries, enforcing consistency across repeated sections.

1.  **Feature Stack**: We stack **Beat-Synchronized Chroma** (Harmony) and **Loudness** (Dynamics/Intensity) features. Loudness is weighted (5x) to prioritize the "Loud-Quiet-Loud" dynamic shifts.
2.  **Novelty Curve**: We compute a rolling Euclidean distance (novelty curve) to detect local changes in texture.
3.  **Recurrence Smoothing (Consistency Enforcement)**:
    -   We calculate a **Self-Similarity (Recurrence) Matrix** to identify repeated sections (e.g., Verse 1 is similar to Verse 2).
    -   We smooth the Novelty Curve using this recurrence matrix. If a structural boundary exists in one instance of a section, the recurrence link "polls" that boundary to other instances, ensuring consistent segmentation across the song.
    -   *Logic*: $N_{consistent} = (N + \alpha \cdot R \cdot N) / (1 + \alpha \cdot \sum R)$
4.  **Peak Picking**: We identify peaks in the smoothed novelty curve to place segment boundaries (prominence=0.04, min_distance=12 beats).

### 4. Loudness Analysis
- **RMS Energy**: We calculate the Root Mean Square (RMS) amplitude of the audio frames.
- **Decibel Scale**: Converted to dB using `librosa.amplitude_to_db` (ref=max) to visualize dynamic range (-80dB to 0dB).

## Reproducibility
The analysis is implemented in `posts/loud_quiet_loud/build_player_assets.py`.
- **Dependencies**: `librosa`, `numpy`, `matplotlib`, `scikit-learn` (via librosa).
- **Output**: JSON metadata (`data.json`) and visualization assets (`chromagram.png`, `loudness.png`).
