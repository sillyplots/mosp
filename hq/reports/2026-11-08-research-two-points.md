# RE: The Two-Point Question — Preliminary Findings
**From:** Office of the Chief of Staff · **Date:** 2026-11-08 · **Re:** Minister's hypothesis that a safety should be worth more than 2 points

Commissioned directly by the Minister; run by the Chief of Staff (no staffer brief covers ad-hoc research yet).
Briefing page (private artifact): https://claude.ai/artifact/Fp5Nb7bZLWLPFWZ2HwXZkv

## Data & method
- nflverse play-by-play 2012–2025, 675,997 plays / 3,829 games, deduplicated on (game_id, play_id).
- Restart value = nflverse EP at the first snap of the next drive (end-of-half restarts excluded).
  Note: nflverse EPA scores a safety as a flat −2 and ignores the free kick; we price it separately.
- Own WP model (HistGradientBoosting, monotonic constraints), trained 2012–24; 2025 holdout Brier 0.159 vs nflverse 0.171.
- Decision grid: resample real outcomes of punts from own 1–5 (n=449) vs post-safety free kicks (n=207), +5s for the punter's run.
- Reproduce: `python3 posts/safety/analysis/safety_analysis.py` → `results.json`, `decision_grid.csv`.

## Findings
1. Free kick after a safety is worth **+1.8 EP** to the scorer (receive at ~own 39). Safety net value **≈3.9**, vs FG net 1.6 and TD net 5.6 (2024–25).
2. Kickoff-equivalent value (if scorer kicked off like any other score): **4.5 → 5.0 → 5.3** points across the 2012–15 / 2016–23 / 2024–25 kickoff eras.
3. Punting from own 1–2 beats conceding by **0.83 EP** (1.17 from 3–5, 1.42 from 6–10).
4. In WP terms the safety wins only when leading by **3–7 with ≲10s** (≲30s at +6/+7), by 1–5 WP points. Elsewhere it costs up to ~25 WP points (leads 0–2 worst).
5. 231 safeties total (16.5/season). 11 intentional end-game safeties, all leading by 5–30 with ≤63s; 9 of 11 with ≤30s.

## Verdict
Hypothesis is right in substance, wrong in remedy: the safety *is* worth more than 2 — about 3.9 — because of the free kick. Under-printed, correctly priced.

## Recommended actions
- [MINISTER] Approve for red team → post. Red team should poke at: EP-as-currency for "net value", the small 2024–25 free-kick sample, WP-model noise (±3 pts) mid-quarter.
- Raw pbp lives in `data/pbp/` — gitignored (`/data/`) and in the `_config.yml` exclude.

## Addendum — Minister's amendment: safety = defensive TD, then normal kickoff
- Defense's net value rises **3.93 → 5.54** (identical to any TD; +1.6 per safety, ~26 pts league-wide per season).
- Punt advantage from own 1–2 rises **0.83 → 2.54 EP** (own 6–10: 1.42 → 3.13).
- WP grid (`decision_grid_rules.csv`, leads −8..21): **no state** where conceding beats punting (max +0.1 WP pts). The current 3–7-lead / final-seconds window becomes a 43–92 pt loss.
- Late kickoffs sampled from real ones with the kicker trailing 1–8 in the last 5 min (714 plays, ~48% onside, 5.5% kicker recovery).
- Also fixed: TD try value now from structured `extra_point_result`/`two_point_conv_result` (desc wording changed); TD face 6.955, nets moved by ≤0.01.
- **Recommendation:** keep the 2-point rule. The amendment solves a problem the data doesn't show and removes a legitimate clock-management option.

## Addendum 2 — Red-team revisions applied (2026-11-08)
Red team verdict REVISE (`2026-11-08-red-team-two-points.md`). All 13 fixes applied to `posts/safety/index.md`:
- Every number in the post is now in `results.json` (new `earned_safeties`, `proposal`, `late_window_by_rule` blocks) or the grid CSVs.
- Headline safety value is now the pooled free kick (3.83, SE 0.06); 2024–25 (3.93 ± 0.43) shown as a check. FK−KO gap 2024–25: +0.51 [0.11, 0.95].
- Normative step stated: the data prices the Act; "safety = TD" is the Minister's principle. Swing: now 2.9, Act 4.6, pick-six 6.7.
- Rings removed from the decision map (only 2 of 11 intentional safeties snapped inside own 5).
- Retreat sensitivity run: 0s → window leads 5–7 (max 1.7 WP pts); 5s → 3–7 (4.9); 10s → 3–7 (11.6). Window is clock-driven.
- Late-game calibration: last-60s Brier 0.082 ours vs 0.082 nflverse (n=936).
- Minister's Section 4 (clock reset in final two minutes) modeled: lead 9+ final-10s cells go from 0 to −2.9 (Act) to −0.01 to −3.7 (Act + reset). Max gain anywhere 0.2 (noise).
- Retroactive: 20–30 flips by try assumption (22 flips + 8 OT with XP). Goal-line stakes: 1.0–3.3 now, 2.8–5.0 under Act.
- Behavioral response listed as out of scope. Prior art: no novelty claimed; nothing cited.
