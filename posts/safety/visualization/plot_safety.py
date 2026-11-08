"""Charts for Operation Two Points. Run from repo root after the analysis script."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import pandas as pd

A = "posts/safety/analysis"
OUT = "posts/safety/assets"
INK, INK2, RULE, BG = "#16202a", "#4b5560", "#d9ddd8", "#fcfcfb"
NET, FACE, POS, NEG, MID = "#2a78d6", "#b9bfc4", "#2a78d6", "#e34948", "#f0efec"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": RULE, "figure.facecolor": BG,
                     "axes.facecolor": BG})
res = json.load(open(f"{A}/results.json"))
e = res["value_of_a_score"]["by_era"]["2024-25"]
td_face = res["value_of_a_score"]["td_face"]

# 1. What each score is worth
pr = res["proposal"]
rows = [("Touchdown", td_face, e["td_net"]), ("Field goal", 3, e["fg_net"]),
        ("Safety (current)", 2, pr["net_now_pooled"]), ("Safety (proposed)", td_face, pr["net_act"])]
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
for i, (n, f, net) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.barh(y + 0.19, f, 0.34, color=FACE, edgecolor=BG, linewidth=2)
    ax.barh(y - 0.19, net, 0.34, color=NET, edgecolor=BG, linewidth=2)
    ax.text(f + 0.08, y + 0.19, f"{f:.2f}".rstrip("0").rstrip("."), va="center", fontsize=9, color=INK2)
    ax.text(net + 0.08, y - 0.19, f"{net:.2f}", va="center", fontsize=9, color=INK, fontweight="bold")
ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
ax.set_xlim(0, 8)
ax.set_xlabel("Points (kickoffs: 2024–25; safety free kicks: 2012–25, too few to split by era)")
ax.grid(axis="x", color=RULE, linewidth=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=FACE), plt.Rectangle((0, 0), 1, 1, color=NET)],
          labels=["On the scoreboard", "Net, after the restart"], frameon=False, ncol=2,
          loc="lower left", bbox_to_anchor=(0, 1.0), borderaxespad=0.2)
ax.set_title("What a score is worth once the next possession is priced in", loc="left", fontsize=12, pad=30)
fig.tight_layout()
fig.savefig(f"{OUT}/safety_value.png")

# 2. Decision map, current vs proposed
g = pd.read_csv(f"{A}/decision_grid_rules.csv")
g = g[g.lead >= -6]
secs = sorted(g.secs.unique(), reverse=True)
leads = sorted(g.lead.unique())
fmt = lambda t: f"{t // 60}:{t % 60:02d}"
cmap = LinearSegmentedColormap.from_list("div", [NEG, MID, POS])
norm = TwoSlopeNorm(vmin=-6, vcenter=0, vmax=6)
fig, axes = plt.subplots(1, 2, figsize=(12, 7.6), dpi=200, sharey=True)
for ax, col, title in zip(axes, ["delta_now", "delta_td_rule"],
                          ["Current rule: 2 points + free kick", "Proposed: defensive TD + kickoff"]):
    m = g.pivot(index="lead", columns="secs", values=col)[secs] * 100
    ax.imshow(m.clip(-6, 6).values, cmap=cmap, norm=norm, aspect="auto", origin="lower")
    ax.set_xticks(range(len(secs)), [fmt(t) for t in secs], rotation=60, fontsize=8)
    ax.set_yticks(range(len(leads)), [f"{l:+d}" if l else "0" for l in leads], fontsize=8)
    ax.set_xticks([x - 0.5 for x in range(len(secs) + 1)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(len(leads) + 1)], minor=True)
    ax.grid(which="minor", color=BG, linewidth=1.5)
    ax.tick_params(which="minor", length=0)
    ax.set_title(title, loc="left", fontsize=12)
    ax.set_xlabel("Time left in game")
    for s in ax.spines.values():
        s.set_visible(False)
axes[0].set_ylabel("Lead of the team pinned deep (points)")
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cb = fig.colorbar(sm, ax=axes, orientation="horizontal", fraction=0.04, pad=0.14, aspect=50)
cb.set_label("Change in win probability from conceding instead of punting, percentage points (color capped at ±6). Assumes 2 timeouts each, 5 s burned by the punter.")
cb.outline.set_visible(False)
fig.suptitle("4th down at your own 1–5 in the 4th quarter: concede a safety or punt? Blue = conceding wins.",
             x=0.06, ha="left", fontsize=12, color=INK)
fig.savefig(f"{OUT}/safety_decision_map.png", bbox_inches="tight")
print("ok")
