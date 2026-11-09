"""Charts for Operation Two Points. Run from repo root after the analysis script."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import pandas as pd

A = "posts/safety/analysis"
OUT = "posts/safety/assets"
INK, INK2, RULE, BG = "#1a2c4e", "#4b5560", "#d9ddd8", "#ffffff"
NET, FACE, POS, NEG, MID = "#2a78d6", "#b9bfc4", "#2a78d6", "#e34948", "#f0efec"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "text.color": INK, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": RULE, "figure.facecolor": BG,
                     "axes.facecolor": BG})
res = json.load(open(f"{A}/results.json"))
e = res["value_of_a_score"]["by_era"]["2024-25"]
td_face = res["value_of_a_score"]["td_face"]

# 1. What each score is worth
pr = res["proposal"]
rows = [("Touchdown", td_face, e["td_net"]), ("Field goal", 3, e["fg_net"]),
        ("Safety (current)", 2, pr["net_now_pooled"]), ("Safety (under the Act)", td_face, pr["net_act"])]
fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
for i, (n, f, net) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.barh(y + 0.19, f, 0.34, color=FACE, edgecolor=BG, linewidth=2)
    ax.barh(y - 0.19, net, 0.34, color=NET, edgecolor=BG, linewidth=2)
    ax.text(f + 0.08, y + 0.19, f"{f:.2f}".rstrip("0").rstrip("."), va="center", fontsize=11, color=INK2)
    ax.text(net + 0.08, y - 0.19, f"{net:.2f}", va="center", fontsize=11, color=INK, fontweight="bold")
ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
ax.set_xlim(0, 8)
ax.set_xlabel("Points")
ax.grid(axis="x", color=RULE, linewidth=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=FACE), plt.Rectangle((0, 0), 1, 1, color=NET)],
          labels=["On the scoreboard", "Net, after the restart"], frameon=False, ncol=2,
          loc="lower left", bbox_to_anchor=(0, 1.0), borderaxespad=0.2)
ax.set_title("What a score is really worth", loc="left", fontsize=16, pad=34, fontweight="bold")
fig.tight_layout()
fig.savefig(f"{OUT}/safety_value.png")

# 2. Decision map, current vs proposed (stacked so it reads at phone width)
g = pd.read_csv(f"{A}/decision_grid_rules.csv")
g = g[g.lead.between(-4, 16)]
secs = sorted(g.secs.unique(), reverse=True)
leads = sorted(g.lead.unique())
fmt = lambda t: f"{t // 60}:{t % 60:02d}"
cmap = LinearSegmentedColormap.from_list("div", [NEG, MID, POS])
norm = TwoSlopeNorm(vmin=-6, vcenter=0, vmax=6)
fig, axes = plt.subplots(2, 1, figsize=(8, 13), dpi=200, sharex=True, layout="constrained")
for ax, col, title in zip(axes, ["delta_now", "delta_td_rule"],
                          ["Current rule: 2 points + free kick", "Defensive Touchdown Act"]):
    m = g.pivot(index="lead", columns="secs", values=col)[secs] * 100
    ax.imshow(m.clip(-6, 6).values, cmap=cmap, norm=norm, aspect="auto", origin="lower")
    ax.set_yticks(range(len(leads)), [f"{l:+d}" if l else "0" for l in leads], fontsize=11)
    ax.set_xticks(range(len(secs)), [fmt(t) for t in secs], rotation=60, fontsize=11)
    ax.set_xticks([x - 0.5 for x in range(len(secs) + 1)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(len(leads) + 1)], minor=True)
    ax.grid(which="minor", color=BG, linewidth=1.5)
    ax.tick_params(which="minor", length=0)
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", color=INK)
    ax.set_ylabel("Your lead (points)")
    for sp in ax.spines.values():
        sp.set_visible(False)
axes[1].set_xlabel("Time left in game")
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cb = fig.colorbar(sm, ax=axes, location="bottom", fraction=0.03, pad=0.02, aspect=40, shrink=0.9)
cb.set_ticks([-6, -3, 0, 3, 6], labels=["Punt\nmuch better", "", "Same", "", "Safety\nmuch better"])
cb.outline.set_visible(False)
fig.suptitle("Pinned at your own 1–5: take the safety or punt?", x=0.02, ha="left", fontsize=17, fontweight="bold", color=INK)
fig.savefig(f"{OUT}/safety_decision_map.png", bbox_inches="tight")
print("ok")
