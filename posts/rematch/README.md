# It's Tough to Beat a Team Twice: Rematch Analysis

**An Econometric Autopsy of Broadcast Booth Folklore**

This project tests the broadcast claim that it is hard to beat the same NFL team twice (or three times) in one season, using 1,165 same-season rematch games and a quality-controlled model of rematch outcomes.

Published at [sillyplots.com/post/rematch](https://sillyplots.com/post/rematch).

## Quick Start

```bash
# Build the working paper (requires a TeX distribution with pdflatex)
cd docs
pdflatex rematch_myth_mosp.tex
pdflatex rematch_myth_mosp.tex   # second pass resolves table references
```

## Project Structure

```
posts/rematch/
├── README.md                 # This file
├── index.md                  # Post page (served at /post/rematch)
│
├── assets/                   # Generated outputs (charts, graphics)
└── docs/                     # LaTeX report
    ├── rematch_myth_mosp.tex # Working paper source
    └── rematch_myth_mosp.pdf # Compiled working paper
```

## Methodology

### Sample

Three families of same-season rematches:
- **Regular-season divisional series** (2002 onward): Game 2 of each divisional pair (n = 1,019)
- **Non-divisional playoff rematches** (2002 onward): a playoff game against a regular-season opponent (n = 121)
- **Three-game sweep attempts** (1970 onward): a team that swept a divisional rival 2-0 meets it again in the playoffs (n = 25)

### Leave-One-Opponent-Out EPA

Team quality is net EPA per play, computed excluding all games against the rematch opponent:

```
LOOO-EPA(i, j) = EPA_off(i, -j) - EPA_def(i, -j)
```

### Rematch Model

```
logit P(W_g = 1) = α + β·ΔEPA_g + δ·Home_g + γ·Rematch_g
```

Where:
- `ΔEPA_g` = LOOO-EPA gap between the two teams
- `Home_g` = home-field indicator
- `Rematch_g` = team won the prior meeting

Under the booth hypothesis, `γ < 0`. A companion OLS model with point margin as the outcome tests whether rematches are closer.

### Key Finding

- **Prior-game winners win 58.5%** of 1,165 rematch games (682-483)
- **Three-game sweep attempts are 16-9** (64.0%, 95% CI 44.5-79.8%)
- **Rematch penalty γ = -0.04, p = 0.68** (95% CI -5.6 to +3.6 points of win probability)
- **Fluke Game 1 winners** win 46.2% of rematches; **blowout winners** win 67.5%

Verdict: **Grade-A Broadcast Mythology.**

## Data Sources

- **Play-by-Play Data**: [nflverse](https://nflverse.nflverse.com/) via BigQuery
- **Seasons**: 2002 onward (divisional and playoff rematches); 1970 onward (three-game sweep attempts)

## Outputs

| File | Description |
|------|-------------|
| `docs/rematch_myth_mosp.pdf` | Full scientific report |

## License

MIT
