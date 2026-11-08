# It's Tough to Beat a Team Twice: Rematch Analysis

**An Econometric Autopsy of Broadcast Booth Folklore**

This project tests the broadcast claim that it is hard to beat the same NFL team twice (or three times) in one season, using 1,299 same-season rematch games and a quality-controlled model of rematch outcomes.

Published at [sillyplots.com/post/rematch](https://sillyplots.com/post/rematch).

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download data (optional - uses cached data in etl/ by default)
python etl/load_data.py

# 3. Run the analysis (writes analysis/results.json and analysis/rematch_games.csv)
python analysis/rematch_analysis.py

# 4. Generate the chart (writes assets/rematch_win_rates.png)
python visualization/plot_rematch_rates.py

# 5. Build the working paper (requires a TeX distribution with pdflatex)
cd docs
pdflatex rematch_myth_mosp.tex
pdflatex rematch_myth_mosp.tex   # second pass resolves table references
```

## Project Structure

```
posts/rematch/
├── README.md                 # This file
├── index.md                  # Post page (served at /post/rematch)
├── requirements.txt          # Python dependencies
│
├── etl/                      # Data extraction
│   ├── load_data.py          # Downloads schedules + play-by-play, builds cached inputs
│   ├── games_nflverse.csv    # nflverse schedules/results, 1999 onward
│   ├── games_538.csv         # FiveThirtyEight results, 1970-1998 (sweep attempts)
│   └── team_game_stats.csv   # Per team per game: offensive EPA, plays, giveaways
│
├── analysis/                 # Core analysis
│   ├── rematch_analysis.py   # Samples, LOOO-EPA, models, strata
│   ├── rematch_games.csv     # One row per rematch game (prior winner's perspective)
│   └── results.json          # Every number reported in the paper
│
├── visualization/            # Output generation
│   └── plot_rematch_rates.py # Rematch win-rate chart
│
├── assets/                   # Generated outputs
│   └── rematch_win_rates.png # Rematch win rate by situation
└── docs/                     # LaTeX report
    ├── rematch_myth_mosp.tex # Working paper source
    └── rematch_myth_mosp.pdf # Compiled working paper
```

## Methodology

### Sample

Three families of same-season rematches:
- **Regular-season divisional series** (2002-2025): Game 2 of each divisional pair (n = 1,145; series with a tied game excluded)
- **Non-divisional playoff rematches** (2002-2025): a playoff game against a regular-season opponent (n = 129)
- **Three-game sweep attempts** (1970-2025): a team that swept a divisional rival 2-0 meets it again in the playoffs (n = 25)

### Leave-One-Opponent-Out EPA

Team quality is net EPA per play, computed excluding all games against the rematch opponent:

```
LOOO-EPA(i, j) = EPA_off(i, -j) - EPA_def(i, -j)
```

### Rematch Model

```
logit P(prior winner wins) = γ + β·ΔEPA_g + δ·Home_g
```

Where:
- `ΔEPA_g` = LOOO-EPA gap (prior winner minus prior loser)
- `Home_g` = +1 if the prior winner is at home, -1 if away, 0 at a neutral site
- `γ` = the rematch effect: the prior winner's edge beyond quality and venue

One row per rematch game, from the prior winner's perspective. This is equivalent to a two-row-per-game model with a `Rematch` indicator, where the intercept is pinned at zero by symmetry. Under the booth hypothesis, `γ < 0`. A companion OLS model with point margin as the outcome tests whether rematches are closer.

### Key Finding

- **Prior-game winners win 57.9%** of 1,299 rematch games (752-547)
- **Three-game sweep attempts are 16-9** (64.0%, 95% CI 44.5-79.8%)
- **Rematch effect γ = +0.12, p = 0.07** (95% CI -0.2 to +5.8 points of win probability): no penalty
- **Rematch margins are 0.6 points wider** than first meetings (p = 0.10): no familiarity effect
- **Fluke Game 1 winners** win 45.2% of rematches (n = 31); **blowout winners** (17+ points) win 64.9% (n = 319)

Verdict: **Grade-A Broadcast Mythology.**

## Data Sources

- **Play-by-Play Data**: [nflverse](https://nflverse.nflverse.com/) (`nflverse-data` releases)
- **Pre-1999 Results**: [FiveThirtyEight NFL Elo game data](https://github.com/fivethirtyeight/nfl-elo-game)
- **Seasons**: 2002-2025 (divisional and playoff rematches); 1970-2025 (three-game sweep attempts)

## Outputs

| File | Description |
|------|-------------|
| `assets/rematch_win_rates.png` | Rematch win rate by situation (money chart) |
| `analysis/results.json` | All model estimates, records and intervals |
| `analysis/rematch_games.csv` | Rematch game-level dataset |
| `docs/rematch_myth_mosp.pdf` | Full scientific report |

## License

MIT
