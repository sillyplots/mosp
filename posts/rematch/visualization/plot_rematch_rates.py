"""Money chart: how often the prior-meeting winner wins the rematch, by situation.

Reads analysis/results.json and writes assets/rematch_win_rates.png.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e6e5e1"
SERIES = "#2a78d6"
HIGHLIGHT = "#e8f0fb"   # light tint of SERIES for the key-row band

KEY_ROW = "All prior winners"   # the headline result


def main():
    with open(os.path.join(ROOT, "analysis", "results.json")) as f:
        r = json.load(f)

    rows = [
        ("Fluke Game 1 winners", r["strata"]["fluke"]),
        ("Prior winner on the road", r["venue_alternation"]["prior_winner_record_away_game2"]),
        ("All prior winners", r["naive"]["all"]),
        ("Three-game sweep attempts", r["naive"]["sweep"]),
        ("Prior winner at home", r["venue_alternation"]["prior_winner_record_home_game2"]),
        ("Blowout Game 1 winners", r["strata"]["blowout"]),
    ]
    rows.sort(key=lambda x: x[1]["pct"])

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(8, 5.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    for y, (label, rec) in enumerate(rows):
        lo, hi = rec["ci"]
        key = label == KEY_ROW
        if key:
            # Shaded band across the whole row, from the label through the value columns
            ax.add_patch(Rectangle((-0.62, y - 0.42), 1.95, 0.84, transform=ax.get_yaxis_transform(),
                                   facecolor=HIGHLIGHT, edgecolor="none", clip_on=False, zorder=0))
        ax.plot([lo, hi], [y, y], color=SERIES, lw=3 if key else 2, solid_capstyle="round",
                alpha=0.8 if key else 0.3, zorder=2)
        ax.scatter([rec["pct"]], [y], s=140 if key else 80, color=SERIES, alpha=1 if key else 0.55,
                   edgecolor=SURFACE, linewidth=2, zorder=3)
        ax.text(1.10, y, f"{rec['pct']:.1f}%", transform=ax.get_yaxis_transform(), va="center", ha="right",
                fontsize=12.5 if key else 11, color=INK if key else INK_2, fontweight="bold" if key else "normal")
        ax.text(1.30, y, f"{rec['n']:,}", transform=ax.get_yaxis_transform(), va="center", ha="right",
                fontsize=11.5 if key else 10, color=INK if key else INK_2, fontweight="bold" if key else "normal")

    top = len(rows) - 0.35
    ax.text(1.10, top, "Win rate", transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=9.5,
            color=INK_2)
    ax.text(1.30, top, "Games", transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=9.5,
            color=INK_2)

    ax.axvline(50, color=MUTED, lw=1.2, ls=(0, (4, 3)), zorder=1)
    ax.text(50, len(rows) - 0.35, "coin flip", ha="center", va="bottom", fontsize=9.5, color=INK_2,
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5))

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([lab for lab, _ in rows], color=INK_2, fontsize=11)
    for tick in ax.get_yticklabels():
        if tick.get_text() == KEY_ROW:
            tick.set_fontweight("bold")
            tick.set_fontsize(12.5)
            tick.set_color(INK)
    ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_xlim(25, 85)
    ax.set_xticks(range(30, 81, 10))
    ax.set_xticklabels([f"{t}%" for t in range(30, 81, 10)], color=INK_2, fontsize=10)
    ax.tick_params(axis="both", length=0, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
    for side in ax.spines.values():
        side.set_visible(False)

    fig.text(0.02, 0.965, "Turns out it's not tough to beat a team twice", fontsize=16, fontweight="bold", color=INK,
             ha="left", va="top")
    fig.text(0.02, 0.905, "Rematch win rate of the team that won the prior meeting, with 95% intervals",
             fontsize=10.5, color=INK_2, ha="left", va="top")
    fig.text(0.02, 0.025, "Same-season NFL rematches 2002-2025; three-game sweep attempts 1970-2025. Fluke: won Game 1 while losing the EPA battle, "
             "turnover\nmargin +2 or better. Blowout: won Game 1 by 17+ points. Source: nflverse, FiveThirtyEight. "
             "The Ministry of Silly Plots.", fontsize=8, color=MUTED, ha="left", va="bottom", linespacing=1.4)

    fig.subplots_adjust(left=0.33, right=0.75, top=0.82, bottom=0.17)
    out = os.path.join(ROOT, "assets", "rematch_win_rates.png")
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
