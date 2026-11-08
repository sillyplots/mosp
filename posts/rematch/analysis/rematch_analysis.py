"""Rematch analysis: is it tough to beat a team twice?

Reads the cached inputs built by etl/load_data.py and writes analysis/results.json.

Samples (all from the perspective of the team that won the prior meeting):
  divisional  Regular-season divisional Game 2s, 2002+ (Game 1 and Game 2 ties dropped)
  playoff     Postseason games between non-divisional teams that met once in the regular season, 2002+
  sweep       Postseason games where one team won both regular-season meetings, 1970+

Model: one row per rematch game, from the prior winner's perspective.
    logit P(prior winner wins) = gamma + beta * dEPA + delta * Home
Home is +1 if the prior winner is at home, -1 if away, 0 at a neutral site.
In the equivalent two-perspective model, where every game appears once per team with
Rematch = 1 for the prior winner and 0 for the prior loser, gamma is the coefficient on
Rematch and the intercept is pinned at zero by symmetry. gamma < 0 means prior winners
do worse than their quality and venue predict.
"""
import json
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
ETL = os.path.join(HERE, "..", "etl")

FIRST_SEASON = 2002          # post-realignment divisions
LAST_SEASON = 2025           # last complete season
SWEEP_FIRST_SEASON = 1970    # AFL-NFL merger
BLOWOUT_MARGIN = 17          # won Game 1 by three scores or more
FLUKE_TURNOVER_MARGIN = 2


def wilson(k, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * (c - h), 1), round(100 * (c + h), 1))


# ---------------------------------------------------------------- games

def load_games():
    nv = pd.read_csv(os.path.join(ETL, "games_nflverse.csv"))
    nv = nv[(nv.season <= LAST_SEASON) & nv.result.notna()].copy()
    # Schedules use historical codes; play-by-play uses current franchise codes
    relocated = {"STL": "LA", "SD": "LAC", "OAK": "LV"}
    nv["home_team"] = nv.home_team.replace(relocated)
    nv["away_team"] = nv.away_team.replace(relocated)
    nv = pd.DataFrame({
        "game_id": nv.game_id,
        "season": nv.season,
        "date": pd.to_datetime(nv.gameday),
        "post": nv.game_type != "REG",
        "home": nv.home_team,
        "away": nv.away_team,
        "home_score": nv.home_score,
        "away_score": nv.away_score,
        "neutral": nv.location == "Neutral",
        "div_game": nv.div_game == 1,
    })

    fte = pd.read_csv(os.path.join(ETL, "games_538.csv"))
    fte = pd.DataFrame({
        "game_id": None,
        "season": fte.season,
        "date": pd.to_datetime(fte.date),
        "post": fte.playoff == 1,
        "home": fte.team1,
        "away": fte.team2,
        "home_score": fte.score1,
        "away_score": fte.score2,
        "neutral": fte.neutral == 1,
        "div_game": np.nan,  # not recorded; sweeps are defined by two regular-season meetings
    })

    games = pd.concat([fte, nv], ignore_index=True)
    games["pair"] = [tuple(sorted(t)) for t in zip(games.home, games.away)]
    games["winner"] = np.where(games.home_score > games.away_score, games.home,
                               np.where(games.away_score > games.home_score, games.away, None))
    return games.sort_values("date").reset_index(drop=True)


def perspective(game, team):
    """Outcome of a game from one team's point of view."""
    home = 0 if game.neutral else (1 if game.home == team else -1)
    own = game.home_score if game.home == team else game.away_score
    opp = game.away_score if game.home == team else game.home_score
    return {"home": home, "win": int(own > opp), "margin": own - opp, "tie": own == opp}


def build_rematches(games):
    rows = []
    reg = games[~games.post]
    post = games[games.post]

    # Divisional Game 2s
    div = reg[(reg.season >= FIRST_SEASON) & (reg.div_game == True)]
    for (season, pair), g in div.groupby(["season", "pair"]):
        if len(g) != 2:
            continue
        g1, g2 = g.iloc[0], g.iloc[1]
        if pd.isna(g1.winner):
            continue  # Game 1 tie: no prior winner
        team = g1.winner
        opp = pair[0] if pair[1] == team else pair[1]
        r = perspective(g2, team)
        if r["tie"]:
            continue
        rows.append(dict(type="divisional", season=season, team=team, opp=opp,
                         prior_game_id=g1.game_id, game_id=g2.game_id,
                         prior_home=perspective(g1, team)["home"], **r))

    # Postseason rematches
    for _, pg in post[post.season >= SWEEP_FIRST_SEASON].iterrows():
        prior = reg[(reg.season == pg.season) & (reg.pair == pg.pair)]
        if len(prior) == 2:
            if prior.winner.isna().any() or prior.winner.nunique() != 1:
                continue  # split series: not a sweep attempt
            kind = "sweep"
        elif len(prior) == 1 and pg.season >= FIRST_SEASON and not prior.iloc[0].div_game:
            if pd.isna(prior.iloc[0].winner):
                continue
            kind = "playoff"
        else:
            continue
        last = prior.iloc[-1]
        team = last.winner
        opp = pg.pair[0] if pg.pair[1] == team else pg.pair[1]
        r = perspective(pg, team)
        if r["tie"]:
            continue
        rows.append(dict(type=kind, season=pg.season, team=team, opp=opp,
                         prior_game_id=last.game_id, game_id=pg.game_id,
                         prior_home=perspective(last, team)["home"], **r))

    return pd.DataFrame(rows)


# ---------------------------------------------------------------- EPA

def add_looo_epa(rm):
    tg = pd.read_csv(os.path.join(ETL, "team_game_stats.csv"))
    reg = tg[tg.season_type == "REG"]

    def looo(season, team, opp):
        s = reg[reg.season == season]
        off = s[(s.team == team) & (s.opponent != opp)]
        dfn = s[(s.opponent == team) & (s.team != opp)]
        return off.off_epa_sum.sum() / off.off_plays.sum() - dfn.off_epa_sum.sum() / dfn.off_plays.sum()

    has_pbp = rm.season >= 1999
    rm.loc[has_pbp, "looo_team"] = [looo(s, t, o) for s, t, o in rm.loc[has_pbp, ["season", "team", "opp"]].values]
    rm.loc[has_pbp, "looo_opp"] = [looo(s, o, t) for s, t, o in rm.loc[has_pbp, ["season", "team", "opp"]].values]
    rm["d_epa"] = rm.looo_team - rm.looo_opp

    # Prior-meeting box score: net EPA and turnover margin for the prior winner
    by_game = tg.set_index(["game_id", "team"])
    nets, tos = [], []
    for gid, t, o in rm[["prior_game_id", "team", "opp"]].values:
        try:
            mine, theirs = by_game.loc[(gid, t)], by_game.loc[(gid, o)]
            nets.append(mine.off_epa_sum - theirs.off_epa_sum)
            tos.append(theirs.giveaways - mine.giveaways)
        except (KeyError, TypeError):
            nets.append(np.nan)
            tos.append(np.nan)
    rm["prior_net_epa"] = nets
    rm["prior_to_margin"] = tos
    return rm


# ---------------------------------------------------------------- analysis

def record(df):
    k, n = int(df.win.sum()), len(df)
    lo, hi = wilson(k, n)
    return {"w": k, "l": n - k, "n": n, "pct": round(100 * k / n, 1), "ci": [lo, hi]}


def familiarity(games):
    """Are divisional Game 2 margins narrower than Game 1 margins, holding the quality gap fixed?"""
    tg = pd.read_csv(os.path.join(ETL, "team_game_stats.csv"))
    reg_tg = tg[tg.season_type == "REG"]
    season_net = {}
    for season, s in reg_tg.groupby("season"):
        off = s.groupby("team")[["off_epa_sum", "off_plays"]].sum()
        dfn = s.groupby("opponent")[["off_epa_sum", "off_plays"]].sum()
        season_net[season] = off.off_epa_sum / off.off_plays - dfn.off_epa_sum / dfn.off_plays

    div = games[~games.post & (games.season >= FIRST_SEASON) & (games.div_game == True)]
    rows = []
    for (season, pair), g in div.groupby(["season", "pair"]):
        if len(g) != 2:
            continue
        gap = abs(season_net[season][pair[0]] - season_net[season][pair[1]])
        for i, (_, gm) in enumerate(g.iterrows()):
            rows.append({"pair_id": f"{season}{pair}", "game2": i, "abs_margin": abs(gm.home_score - gm.away_score),
                         "abs_gap": gap})
    df = pd.DataFrame(rows)
    fit = smf.ols("abs_margin ~ game2 + abs_gap", df).fit(cov_type="cluster", cov_kwds={"groups": df.pair_id})
    lo, hi = fit.conf_int().loc["game2"]
    return {"coef": round(fit.params["game2"], 2), "se": round(fit.bse["game2"], 2),
            "p": round(fit.pvalues["game2"], 3), "ci": [round(lo, 2), round(hi, 2)], "n_games": len(df),
            "mean_game1_abs_margin": round(df[df.game2 == 0].abs_margin.mean(), 2)}


def main():
    games = load_games()
    rm = add_looo_epa(build_rematches(games))
    rm.to_csv(os.path.join(HERE, "rematch_games.csv"), index=False)

    res = {"sample": {}, "naive": {}}
    for kind in ["divisional", "playoff", "sweep"]:
        sub = rm[rm.type == kind]
        res["naive"][kind] = record(sub)
        res["sample"][kind] = {"seasons": [int(sub.season.min()), int(sub.season.max())], "n": len(sub)}
    res["naive"]["all"] = record(rm)

    # Venue alternation: share of divisional Game 1 winners who played Game 2 on the road
    d = rm[rm.type == "divisional"]
    res["venue_alternation"] = {
        "pct_game1_winners_away_in_game2": round(100 * (d.home == -1).mean(), 1),
        "prior_winner_record_home_game2": record(d[d.home == 1]),
        "prior_winner_record_away_game2": record(d[d.home == -1]),
    }

    # Models: rematch games with play-by-play (1999+)
    m = rm[rm.d_epa.notna()].copy()
    X = sm.add_constant(m[["d_epa", "home"]])
    logit = sm.Logit(m.win, X).fit(disp=0)
    ols = sm.OLS(m.margin, X).fit()

    g, se = logit.params["const"], logit.bse["const"]
    g_lo, g_hi = g - 1.959964 * se, g + 1.959964 * se
    base = logit.params["d_epa"] * m.d_epa.mean() + logit.params["home"] * m.home.mean()
    p0 = 1 / (1 + np.exp(-base))
    to_pp = lambda x: round(100 * (1 / (1 + np.exp(-(base + x))) - p0), 1)

    def coefs(fit, name):
        return {"coef": round(fit.params[name], 3), "se": round(fit.bse[name], 3), "p": round(fit.pvalues[name], 3)}

    res["logit"] = {"beta": coefs(logit, "d_epa"), "delta": coefs(logit, "home"), "gamma": coefs(logit, "const"),
                    "gamma_ci_logodds": [round(g_lo, 2), round(g_hi, 2)],
                    "gamma_ci_pp": [to_pp(g_lo), to_pp(g_hi)], "gamma_pp": to_pp(g),
                    "n": int(logit.nobs), "pseudo_r2": round(logit.prsquared, 3),
                    "by_type": m.type.value_counts().to_dict()}
    res["ols"] = {"beta": coefs(ols, "d_epa"), "delta": coefs(ols, "home"), "gamma": coefs(ols, "const"),
                  "n": int(ols.nobs), "r2": round(ols.rsquared, 3)}

    res["familiarity"] = familiarity(games)

    # Game 1 profiles (prior meetings with play-by-play)
    s = rm[rm.prior_net_epa.notna()]
    fluke = s[(s.prior_net_epa < 0) & (s.prior_to_margin >= FLUKE_TURNOVER_MARGIN)]
    blow = s[(s.margin.notna()) & (s.prior_game_id.isin(
        games[(abs(games.home_score - games.away_score) >= BLOWOUT_MARGIN)].game_id))]
    res["strata"] = {"fluke": record(fluke), "blowout": record(blow), "base": record(s),
                     "blowout_definition": f"Won Game 1 by {BLOWOUT_MARGIN}+ points"}

    # Is the fluke/blowout gap real, and is it explained by team quality?
    from statsmodels.stats.proportion import proportions_ztest
    z, pz = proportions_ztest([fluke.win.sum(), blow.win.sum()], [len(fluke), len(blow)])
    s = s.assign(fluke=s.index.isin(fluke.index).astype(int), blowout=s.index.isin(blow.index).astype(int))
    q = s[s.d_epa.notna()]
    fit = sm.Logit(q.win, sm.add_constant(q[["d_epa", "home", "fluke", "blowout"]])).fit(disp=0)
    res["strata"]["fluke_vs_blowout_p"] = round(pz, 3)
    res["strata"]["mean_d_epa"] = {"fluke": round(fluke.d_epa.mean(), 3), "blowout": round(blow.d_epa.mean(), 3),
                                   "all": round(s.d_epa.mean(), 3)}
    res["strata"]["controlled_logit"] = {k: coefs(fit, k) for k in ["fluke", "blowout"]}

    # How much does venue imbalance move the naive divisional rate?
    home_rate = d[d.home == 1].win.mean()
    away_rate = d[d.home == -1].win.mean()
    res["venue_alternation"]["balanced_venue_rate"] = round(100 * (home_rate + away_rate) / 2, 1)
    res["venue_alternation"]["naive_rate_shift_pp"] = round(100 * ((home_rate + away_rate) / 2 - d.win.mean()), 2)

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(res, f, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps(res, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


if __name__ == "__main__":
    main()
