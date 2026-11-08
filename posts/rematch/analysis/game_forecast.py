"""Forecast a single upcoming rematch with the fitted rematch model.

Usage: python analysis/game_forecast.py SEASON PRIOR_WINNER OPPONENT HOME
  HOME is +1 if the prior winner hosts the rematch, -1 if away, 0 if neutral.
Example (Week 9, 2026): python analysis/game_forecast.py 2026 SEA ARI 1

Downloads that season's nflverse play-by-play, computes each team's
Leave-One-Opponent-Out EPA from regular-season games played so far, and applies
the logit coefficients in analysis/results.json.
"""
import json
import os
import sys
import tempfile
import urllib.request

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.parquet"


def team_games(season):
    with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
        urllib.request.urlretrieve(PBP_URL.format(season=season), tmp.name)
        pbp = pd.read_parquet(tmp.name, columns=["game_id", "season_type", "posteam", "defteam",
                                                 "pass", "rush", "epa"])
    plays = pbp[(pbp.season_type == "REG") & pbp.posteam.notna() & pbp.epa.notna()
                & ((pbp["pass"] == 1) | (pbp["rush"] == 1))]
    return plays.groupby(["game_id", "posteam", "defteam"]).epa.agg(["sum", "size"]).reset_index()


def looo(tg, team, opp):
    off = tg[(tg.posteam == team) & (tg.defteam != opp)]
    dfn = tg[(tg.defteam == team) & (tg.posteam != opp)]
    return off["sum"].sum() / off["size"].sum() - dfn["sum"].sum() / dfn["size"].sum()


def main(season, team, opp, home):
    tg = team_games(season)
    d_epa = looo(tg, team, opp) - looo(tg, opp, team)
    with open(os.path.join(HERE, "results.json")) as f:
        m = json.load(f)["logit"]
    base = m["beta"]["coef"] * d_epa + m["delta"]["coef"] * home
    p = 1 / (1 + np.exp(-(base + m["gamma"]["coef"])))
    p_no_rematch = 1 / (1 + np.exp(-base))
    print(f"{team} vs {opp}, {season}: dEPA = {d_epa:+.3f}, home = {home:+d}")
    print(f"P({team} wins) = {p:.1%}  (without rematch term: {p_no_rematch:.1%})")


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]))
