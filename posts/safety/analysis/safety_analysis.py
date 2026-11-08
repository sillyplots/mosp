"""
Operation Two Points — what is a safety actually worth?

Data: nflverse play-by-play, 2012-2025 (regular + postseason).
Run from repo root:  python3 posts/safety/analysis/safety_analysis.py
Expects data/pbp/pbp_<season>.parquet (download URL in PBP_URL).
Writes posts/safety/analysis/results.json and decision_grid.csv.
"""
import glob, json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.parquet"
OUT = "posts/safety/analysis"
SCRIMMAGE = ["run", "pass", "punt", "field_goal", "qb_kneel", "qb_spike"]
COLS = ["game_id", "play_id", "season", "season_type", "home_team", "away_team", "result",
        "spread_line", "posteam", "defteam", "play_type", "desc", "qtr", "down", "ydstogo",
        "yardline_100", "game_seconds_remaining", "half_seconds_remaining", "game_half",
        "posteam_timeouts_remaining", "defteam_timeouts_remaining", "score_differential",
        "total_home_score", "total_away_score", "ep", "epa", "wp", "wpa", "safety",
        "touchdown", "field_goal_result", "kickoff_attempt", "punt_attempt", "punt_blocked",
        "home_opening_kickoff"]


def load():
    df = pd.concat(pd.read_parquet(f, columns=COLS) for f in sorted(glob.glob("data/pbp/pbp_*.parquet")))
    df = df.drop_duplicates(["game_id", "play_id"]).sort_values(["game_id", "play_id"]).reset_index(drop=True)
    df["era"] = pd.cut(df.season, [2011, 2015, 2023, 2030], labels=["2012-15", "2016-23", "2024-25"])
    return df


def next_scrimmage(df):
    """For every row, the index of the next scrimmage snap in the same game and half (or -1)."""
    is_scr = df.play_type.isin(SCRIMMAGE) & df.down.notna()
    idx = pd.Series(np.where(is_scr, df.index, np.nan), index=df.index)
    key = df.game_id + "_" + df.game_half.astype(str)
    # first scrimmage snap strictly after this row, within the same game-half
    nxt = idx.groupby(key).transform(lambda s: s.shift(-1).bfill())
    return nxt.fillna(-1).astype(int)


def sequence(df, nxt, i, team):
    """Outcome of the sequence starting at play i, from `team`'s view, ending at the next scrimmage snap."""
    j = nxt[i]
    if j < 0:
        return None
    a, b = df.loc[i], df.loc[j]
    # score_differential is pre-snap and from the possessing team's view
    m0 = a.score_differential if a.posteam == team else -a.score_differential
    m1 = b.score_differential if b.posteam == team else -b.score_differential
    return dict(has_ball=b.posteam == team, yardline_100=b.yardline_100, down=b.down, ydstogo=b.ydstogo,
                d_margin=m1 - m0, dt=a.game_seconds_remaining - b.game_seconds_remaining,
                ep_next=b.ep if b.posteam == team else -b.ep, game_id=a.game_id, season=a.season)


# ---------------------------------------------------------------- restart values (EP)
def restart_values(df, nxt):
    """EP of the possession that follows each kind of score, from the scoring team's view."""
    rows = []
    ko = df.index[(df.kickoff_attempt == 1)]
    for k in ko:
        prev = df.loc[:k - 1].tail(4)
        prev = prev[prev.game_id == df.at[k, "game_id"]]
        if prev.empty:
            continue
        if (prev.safety == 1).any():
            kind = "safety"
        elif (prev.touchdown == 1).any() or prev.desc.str.contains("EXTRA POINT|TWO-POINT", na=False).any():
            kind = "touchdown"
        elif (prev.field_goal_result == "made").any():
            kind = "field_goal"
        else:
            continue
        j = nxt[k]
        if j < 0:
            continue
        a, b = df.loc[k], df.loc[j]
        if a.half_seconds_remaining < 120:  # end-of-half restarts are clock plays, not possessions
            continue
        kicking = a.defteam if pd.notna(a.defteam) else None  # nflverse: posteam on a kickoff = receiving team
        receiving = a.posteam
        if b.posteam != receiving:
            continue  # onside recoveries, muffs: rare, excluded from the "normal restart" price
        rows.append(dict(kind=kind, era=a.era, season=a.season, recv_yardline_100=b.yardline_100,
                         ep_receiver=b.ep))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- win-probability model
FEATS = ["score_differential", "game_seconds_remaining", "half_seconds_remaining", "yardline_100", "down",
         "ydstogo", "posteam_timeouts_remaining", "defteam_timeouts_remaining", "is_home", "pos_spread",
         "diff_per_min", "receive_2h_ko"]


MONO = [1, 0, 0, -1, -1, -1, 1, -1, 0, 1, 1, 0]  # +1: more is better for the team with the ball


def add_feats(d):
    d = d.copy()
    d["diff_per_min"] = d.score_differential / (d.game_seconds_remaining / 60 + 1)
    return d


def wp_model(df):
    d = df[df.play_type.isin(SCRIMMAGE) & df.down.notna() & (df.qtr <= 4) & (df.result != 0)].copy()
    d["is_home"] = (d.posteam == d.home_team).astype(int)
    d["pos_spread"] = np.where(d.is_home == 1, d.spread_line, -d.spread_line)
    d["receive_2h_ko"] = ((d.game_half == "Half1") &
                          (((d.home_opening_kickoff == 1) & (d.is_home == 1)) |
                           ((d.home_opening_kickoff == 0) & (d.is_home == 0)))).astype(int)
    d["won"] = ((d.result > 0) == (d.is_home == 1)).astype(int)
    d = add_feats(d).dropna(subset=FEATS)
    train, test = d[d.season < 2025], d[d.season == 2025]
    m = HistGradientBoostingClassifier(max_iter=600, learning_rate=0.05, max_leaf_nodes=63,
                                       min_samples_leaf=200, l2_regularization=1.0, random_state=7,
                                       # more points / better field position can never lower WP
                                       monotonic_cst=MONO)
    m.fit(train[FEATS], train.won)
    p = m.predict_proba(test[FEATS])[:, 1]
    t2 = test.assign(p=p).dropna(subset=["wp"])
    brier = dict(ours=float(((t2.p - t2.won) ** 2).mean()), nflverse=float(((t2.wp - t2.won) ** 2).mean()),
                 corr_with_nflverse=float(np.corrcoef(t2.p, t2.wp)[0, 1]), n_test=int(len(t2)))
    m.fit(d[FEATS], d.won)  # refit on everything for the counterfactuals
    return m, brier


def wp_after(model, outcomes, lead, secs, my_to, opp_to, spread=0.0):
    """Mean WP for team T over sampled outcome sequences, starting from 4th-quarter state (lead, secs)."""
    o = outcomes
    rem = secs - o.dt.values
    margin = lead + o.d_margin.values
    X = pd.DataFrame(dict(
        score_differential=np.where(o.has_ball, margin, -margin),
        game_seconds_remaining=np.clip(rem, 1, None), half_seconds_remaining=np.clip(rem, 1, None),
        yardline_100=o.yardline_100.values, down=o.down.values, ydstogo=o.ydstogo.values,
        posteam_timeouts_remaining=np.where(o.has_ball, my_to, opp_to),
        defteam_timeouts_remaining=np.where(o.has_ball, opp_to, my_to),
        is_home=0, pos_spread=np.where(o.has_ball, spread, -spread), receive_2h_ko=0))
    X = add_feats(X)
    p = model.predict_proba(X[FEATS])[:, 1]
    wp = np.where(o.has_ball, p, 1 - p)
    final = np.where(margin > 0, 1.0, np.where(margin == 0, 0.5, 0.0))
    return float(np.where(rem <= 0, final, wp).mean())


def main():
    df = load()
    nxt = next_scrimmage(df).values
    res = dict(seasons="2012-2025", plays=int(len(df)), games=int(df.game_id.nunique()))

    # 1. Safety census
    s = df[df.safety == 1]
    res["safeties"] = dict(total=int(len(s)), per_season=round(len(s) / 14, 1),
                           by_play_type=s.play_type.value_counts().to_dict(),
                           per_game_pct=round(100 * len(s) / df.game_id.nunique(), 1))

    # 2. Restart values
    rv = restart_values(df, nxt)
    tab = rv.groupby(["kind", "era"], observed=True).agg(n=("ep_receiver", "size"),
                                                          ep=("ep_receiver", "mean"),
                                                          yl=("recv_yardline_100", "mean")).reset_index()
    res["restart_ep"] = tab.round(3).to_dict("records")
    ko_ep = rv[rv.kind != "safety"].groupby("era", observed=True).ep_receiver.mean()
    fk_ep = rv[rv.kind == "safety"].groupby("era", observed=True).ep_receiver.mean()
    fk_ep_all = rv[rv.kind == "safety"].ep_receiver.mean()
    fk_n = int((rv.kind == "safety").sum())

    # TD face value: 6 + realised try value
    tries = df[df.desc.str.contains("EXTRA POINT|TWO-POINT CONVERSION ATTEMPT", na=False)]
    xp = tries.desc.str.contains("EXTRA POINT is GOOD", na=False).sum()
    two = tries.desc.str.contains("ATTEMPT SUCCEEDS", na=False).sum()
    td_pts = 6 + (xp + 2 * two) / len(tries)

    eras = {}
    for era, ko in ko_ep.items():
        eras[str(era)] = dict(kickoff_ep_to_receiver=round(ko, 3),
                              td_net=round(td_pts - ko, 3), fg_net=round(3 - ko, 3),
                              free_kick_ep_to_scorer=round(fk_ep[era], 3),
                              safety_net=round(2 + fk_ep[era], 3),
                              # what a safety would have to be worth if the scorer then kicked off like after any other score
                              safety_kickoff_equivalent_points=round(2 + fk_ep[era] + ko, 3))
    res["value_of_a_score"] = dict(td_face=round(td_pts, 3), safety_free_kick_ep_to_scorer=round(fk_ep_all, 3),
                                   n_safety_free_kicks=fk_n, by_era=eras)

    # 3. The decision in EP: 4th-down punt from own 10 or deeper vs. conceding a safety
    p = df[(df.punt_attempt == 1) & (df.down == 4) & (df.yardline_100 >= 90)].copy()
    p["ep_after"] = p.ep + p.epa
    p["own_yl"] = 100 - p.yardline_100
    p["bin"] = pd.cut(p.own_yl, [0, 2, 5, 10], labels=["own 1-2", "own 3-5", "own 6-10"])
    pt = p.groupby("bin", observed=True).agg(n=("ep_after", "size"), ep_after=("ep_after", "mean"),
                                             blocked_pct=("punt_blocked", "mean")).reset_index()
    safety_ep = -2 - fk_ep_all
    pt["safety_ep"] = safety_ep
    pt["punt_advantage"] = pt.ep_after - safety_ep
    res["punt_vs_safety_ep"] = pt.round(3).astype({"bin": str}).to_dict("records")

    # 4. The decision in WP
    model, brier = wp_model(df)
    res["wp_model_holdout_2025"] = brier
    punt_seq = [sequence(df, nxt, i, df.at[i, "posteam"]) for i in p.index[p.yardline_100 >= 95]]
    punt_seq = pd.DataFrame([x for x in punt_seq if x])
    saf_seq = [sequence(df, nxt, i, df.at[i, "posteam"]) for i in s.index if pd.notna(df.at[i, "posteam"])]
    saf_seq = pd.DataFrame([x for x in saf_seq if x])
    # keep only normal free-kick restarts (conceding team kicks, nothing weird mid-sequence)
    saf_seq = saf_seq[(saf_seq.d_margin == -2) & (~saf_seq.has_ball)]
    res["outcome_samples"] = dict(
        punts_from_own_5_or_deeper=int(len(punt_seq)),
        punt_mean_opp_start_own=round(float(100 - punt_seq[~punt_seq.has_ball].yardline_100.mean()), 1),
        punt_opp_scored_pct=round(100 * float((punt_seq.d_margin < 0).mean()), 2),
        punt_median_clock=float(punt_seq.dt.median()),
        safety_free_kicks=int(len(saf_seq)),
        fk_mean_opp_start_own=round(float(100 - saf_seq.yardline_100.mean()), 1),
        fk_median_clock=float(saf_seq.dt.median()))
    punt_seq = punt_seq[punt_seq.dt < 60]
    saf_seq = saf_seq[saf_seq.dt < 60]

    leads = list(range(-8, 15))
    secs_grid = [600, 420, 300, 240, 180, 150, 120, 90, 60, 45, 30, 20, 10, 5]
    grid = []
    for to in (0, 2):
        for L in leads:
            for t in secs_grid:
                wp_p = wp_after(model, punt_seq, L, t, to, to)
                # intentional safeties are run long on purpose: +5s of snap-to-whistle over the free-kick sample
                wp_s = wp_after(model, saf_seq.assign(dt=saf_seq.dt + 5), L, t, to, to)
                grid.append(dict(timeouts_each=to, lead=L, secs=t, wp_punt=wp_p, wp_safety=wp_s,
                                 delta=wp_s - wp_p))
    g = pd.DataFrame(grid)
    g.to_csv(f"{OUT}/decision_grid.csv", index=False)
    take = g[(g.delta > 0.005)]
    res["safety_preferred_states"] = take.sort_values(["timeouts_each", "lead", "secs"]).round(4).to_dict("records")
    early = g[g.secs >= 300]
    res["early_4q_mean_wp_cost_of_safety"] = round(float(-early.delta.mean()), 4)

    # 5. Real intentional safeties
    # end-game, protecting a lead: punter takes the snap and runs out of the back of the end zone
    ints = s[(s.play_type == "run") & s.desc.str.contains("Punt formation", na=False)
             & (s.game_seconds_remaining <= 120) & (s.score_differential > 0)]
    res["intentional_safeties"] = [
        dict(season=int(r.season), game=r.game_id, team=r.posteam, lead=int(r.score_differential),
             secs_left=int(r.game_seconds_remaining), desc=r.desc[:140]) for r in ints.itertuples()]

    with open(f"{OUT}/results.json", "w") as f:
        json.dump(res, f, indent=2, default=lambda x: x.item() if hasattr(x, "item") else str(x))
    print(json.dumps({k: v for k, v in res.items() if k not in ("safety_preferred_states",)}, indent=1, default=str))
    print(take.to_string())


if __name__ == "__main__":
    main()
