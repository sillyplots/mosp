"""Download raw game and play-by-play data and build the cached inputs for the analysis.

Outputs (written to posts/rematch/etl/):
  games_nflverse.csv     nflverse schedule/results, 1999 onward
  games_538.csv          FiveThirtyEight game results, 1970-1998 (for three-game sweep attempts)
  team_game_stats.csv    one row per team per game, 1999 onward: offensive EPA, plays, turnovers

Play-by-play files are large (~20 MB per season), so each season is downloaded,
aggregated and discarded. Only the small aggregate file is kept.
"""
import os
import sys
import tempfile
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIRST_PBP_SEASON = 1999
LAST_COMPLETE_SEASON = 2025

NFLVERSE_GAMES_URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"
PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.parquet"
FTE_GAMES_URL = "https://raw.githubusercontent.com/fivethirtyeight/nfl-elo-game/master/data/nfl_games.csv"

PBP_COLUMNS = ["game_id", "season", "season_type", "posteam", "defteam",
               "pass", "rush", "epa", "interception", "fumble_lost"]


def load_games():
    games = pd.read_csv(NFLVERSE_GAMES_URL)
    games.to_csv(os.path.join(HERE, "games_nflverse.csv"), index=False)
    print(f"nflverse games: {len(games)} rows, seasons {games.season.min()}-{games.season.max()}")

    fte = pd.read_csv(FTE_GAMES_URL)
    fte = fte[(fte.season >= 1970) & (fte.season < FIRST_PBP_SEASON)]
    fte.to_csv(os.path.join(HERE, "games_538.csv"), index=False)
    print(f"FiveThirtyEight games: {len(fte)} rows, seasons {fte.season.min()}-{fte.season.max()}")


def aggregate_season(season):
    with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
        urllib.request.urlretrieve(PBP_URL.format(season=season), tmp.name)
        pbp = pd.read_parquet(tmp.name, columns=PBP_COLUMNS)

    # Offensive scrimmage plays only (passes and runs, including sacks and scrambles)
    plays = pbp[pbp.posteam.notna() & pbp.epa.notna() & ((pbp["pass"] == 1) | (pbp["rush"] == 1))].copy()
    plays["giveaway"] = plays.interception.fillna(0) + plays.fumble_lost.fillna(0)

    out = (plays.groupby(["game_id", "season", "season_type", "posteam", "defteam"])
           .agg(off_epa_sum=("epa", "sum"), off_plays=("epa", "size"), giveaways=("giveaway", "sum"))
           .reset_index()
           .rename(columns={"posteam": "team", "defteam": "opponent"}))
    return out


def load_team_game_stats(last_season=LAST_COMPLETE_SEASON):
    frames = []
    for season in range(FIRST_PBP_SEASON, last_season + 1):
        print(f"  play-by-play {season}...", flush=True)
        frames.append(aggregate_season(season))
    stats = pd.concat(frames, ignore_index=True)
    stats.to_csv(os.path.join(HERE, "team_game_stats.csv"), index=False)
    print(f"team-game stats: {len(stats)} rows")


if __name__ == "__main__":
    load_games()
    if "--games-only" not in sys.argv:
        load_team_game_stats()
