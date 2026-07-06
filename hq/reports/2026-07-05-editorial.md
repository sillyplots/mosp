# EDITORIAL SWEEP — 2026-07-05
**The Desk** | Ministry of Silly Plots

---

## TL;DR
One operation live (Super Bowl, unchanged, correctly the only homepage link). Three operations
STALLED, all confirmed rather than merely suspected: **Stuperlatives** (156 days, raw orphan `.md`
shipping to the live site, zero chart assets), **IHOP Initiative** (198 days, raw orphan `.md` plus
literal debug artifacts — screenshots, a `debug/` folder — shipping to the live site), and
**Bridgelocks** (mosp copy untouched 49 days; it did graduate to `~/Documents/bridgelocks` as a
standalone repo, but that repo is itself stalled at 36 days with no remote, and the orphaned
original copy is still sitting in `posts/bridgelocks/` shipping to the site). Nothing here needs
the Minister to *unblock* a mystery — the mysteries are solved — but three decisions need the
Minister's sign-off this week: kill-or-keep on the pff debug artifacts, kill-or-keep on the stale
`posts/bridgelocks/` copy now that a canonical home exists, and whether Stuperlatives/IHOP get
revived or archived.

---

## 0. Housekeeping note

This sweep runs on branch `admin-sweep-2026-07-05`, which already had a prior commit (`eeb100f`,
"Registry Office: Admin sweep 2026-07-05") from an archivist run earlier this session. That commit
rewrote `hq/PIPELINE.md`, `hq/DECISIONS.md`, and added the brief files this sweep reads. This memo
builds on top of that state rather than re-doing it. It also found `posts/bridgelocks/` **fully
present** in the working tree — the deletions visible in an earlier git-status snapshot were never
committed on any branch (confirmed via `git log --all --oneline -- posts/bridgelocks/`, which shows
only the original add). Treat any prior report of "bridgelocks deleted from the repo" as describing
an uncommitted, and now moot, working-tree state.

---

## 1. Table reconciliation (all rows, against reality)

| Operation | Old stage | Evidence checked | True stage |
|---|---|---|---|
| Super Bowl | PUBLISHED | `posts/super_bowl/index.md` has proper front matter (`layout`, `title`, `permalink: /post/superbowl/`), builds cleanly to `_site/posts/super_bowl/`, `index.html` links it as "Read Our Latest Findings" and under Recent Publications. Only post linked anywhere on the homepage. | **PUBLISHED** — confirmed, no change. |
| Stuperlatives | UNCLEAR | `posts/stuperlatives/` exists (10 `.md` files: `README.md`, `report.md`, `walkthrough.md`, `optimizer/README.md`, `optimizer/kenneth_walker.md`, `optimizer/kenneth_walker_2025_report.md`, `optimizer/sam_darnold_2025_report.md`, `docs/WEATHER_ANALYSIS_APPROACH.md`, 2× `optimizer/examples/*/walkthrough.md`). None carry Jekyll front matter (no `---` blocks). All except top-level `README.md` (globally excluded by filename in `_config.yml`) confirmed present in the built `_site/posts/stuperlatives/` tree as raw markdown. **Zero image/chart assets anywhere in the folder** — no money chart exists, so this isn't even review-ready as a draft. Nothing in `index.html` references it. Last git touch: 2026-01-30 (156 days). | **DRAFTING, STALLED, orphaned.** |
| IHOP Initiative | UNCLEAR | `posts/pff_analysis/` exists. `README.md` (excluded by filename), `etl/PFF_SCRAPING_WALKTHROUGH.md`, `reporting/stadium_distance_rankings.md` all lack front matter and (excepting README) ship raw into `_site/posts/pff_analysis/`. It does have real chart assets (`reporting/plots/*.png` — regression plots, IHOP-effect scatter, grade distributions), so the underlying analysis is substantially done. But it also ships **debug artifacts**: `etl/test_screenshot.png`, `etl/debug_auth_state.png`, `etl/test_page.html`, and a literal `reporting/debug/` directory containing `team_row_debug.html` + `team_page_debug.png` — all confirmed present in `_site/`. No `index.md`, nothing in `index.html`. Charter (§4, Operation PFF Run Blocking) documents the key finding (p < 0.002, "closer is better") but that's a Charter entry, not a published post. Last git touch: 2025-12-19 (198 days). | **DRAFTING, STALLED, orphaned, plus a debug-artifact leak.** |
| Bridgelocks | RELOCATED? | `posts/bridgelocks/` is present and untracked-clean in the mosp working tree (see §0) — 16 files, `.gitignore`, README variants, `analysis/`, `data/`, `engine/`, `etl/`. Separately, `~/Documents/bridgelocks` is a genuine standalone git repo (own `.git`, `.claude/`, `CLAUDE.md` — same shape as the confirmed loud_quiet_loud graduation). `diff -rq` between the two shows substantial divergence: the standalone repo has ~15 additional plot scripts and PNGs (`plot_dumbbell.py`, `plot_heatmap.py`, `plot_seasonality.py`, `ballard_pr_curve.png`, etc.) not present in the mosp copy, and existing shared files (`process_data.py`, the notebook, several PNGs) differ. So the graduation is real and the standalone repo is the more current copy. However the standalone repo's own `git log` shows only 2 commits, the most recent dated **2026-05-30**, and `git remote -v` is empty (no backup, local-only). Mosp's tracked history for `posts/bridgelocks/` stops at 2026-05-17 (49 days). | **Graduated (confirmed), but stalled in its new home too (36 days), and the stale original in mosp is still shipping to the live site as an orphan.** |

---

## 2. Staleness check (21+ day threshold)

| Operation | Last touch (mosp) | Days stale | Status | Smallest next step |
|---|---|---|---|---|
| Super Bowl | 2026-02-03 | 152 | Not "stalled" — it's PUBLISHED and finished, staleness doesn't apply the same way to a shipped, unchanging post. | N/A |
| Stuperlatives | 2026-01-30 | 156 | STALLED | Decide archive vs. revive; if revive, next step is producing the missing money chart — there currently isn't one. |
| IHOP Initiative | 2025-12-19 | 198 | STALLED | Decide archive vs. revive; if revive, next step is writing `index.md` with front matter around the existing `reporting/plots/` assets and stripping debug artifacts first. |
| Bridgelocks (mosp copy) | 2026-05-17 | 49 | STALLED (superseded) | Confirm with Minister whether to delete `posts/bridgelocks/` from mosp now that the canonical copy lives in `~/Documents/bridgelocks`. |
| Bridgelocks (standalone) | 2026-05-30 | 36 | STALLED | Push a remote (currently none) and decide if/when it graduates to a mosp post the way the Super Bowl piece did. |

---

## 3. Orphan patrol

Files shipping to the built site that nothing links to:

| Path (shipped to `_site/`) | Type | Recommendation |
|---|---|---|
| `posts/stuperlatives/*.md` (9 files, all but README) | Raw unlinked markdown, no front matter | **[MINISTER]** Keep if Stuperlatives is revived soon; otherwise pull into drafting-only storage or add front matter and link it, don't leave it raw on the live site indefinitely. |
| `posts/pff_analysis/etl/PFF_SCRAPING_WALKTHROUGH.md`, `posts/pff_analysis/reporting/stadium_distance_rankings.md` | Raw unlinked markdown, no front matter | **[MINISTER]** Same call as Stuperlatives — this one has real charts, closer to review-ready with an `index.md` wrapper. |
| `posts/pff_analysis/etl/test_screenshot.png`, `posts/pff_analysis/etl/debug_auth_state.png`, `posts/pff_analysis/etl/test_page.html` | Scraper debug artifacts | **[MINISTER]** Kill recommended — these are test/debugging byproducts, not analysis output, and `debug_auth_state.png` in particular is the kind of thing that sounds adjacent to the `shhhh/pff_auth.json` credential the Charter mentions. Worth a second look to make sure it's just a screenshot and not a credential-bearing image before deleting. |
| `posts/pff_analysis/reporting/debug/team_row_debug.html`, `posts/pff_analysis/reporting/debug/team_page_debug.png` | Literal debug folder | **[MINISTER]** Kill recommended — named "debug," clearly not intended for publication. |
| `posts/bridgelocks/*` (16 files) | Superseded draft, stale relative to the standalone repo | **[MINISTER]** Kill-or-keep call described in §1/§2 above. |

No stray `.md` files found at repo root beyond `CLAUDE.md` and the Charter — both already excluded from the build in `_config.yml` per the 2026-07-05 DECISIONS.md entry, and confirmed absent from `_site/` by the prior admin-sweep. No debug artifacts found in `_site/` outside the `pff_analysis` ones listed above.

**Separate hygiene note, outside this brief's remit but worth flagging:** `posts/pff_analysis` folder was git-tracked as of `git ls-files` and `gooseorgeese` is a git-tracked top-level entry that is itself a nested repository (has its own `.git` and `.github/`, no `.gitmodules` entry in mosp, currently showing as modified in `git status`). That's a repo-hygiene matter for the archivist module, not something this sweep should touch.

---

## 4. Ready-for-review queue

Per the brief, this step applies to anything at DRAFTING that looks *complete*. Neither Stuperlatives
nor IHOP Initiative clears that bar:

- **Stuperlatives**: fails at the first checklist item — no money chart exists at all. Not ready for
  review; still early DRAFTING.
- **IHOP Initiative**: has real analysis and charts (`reporting/plots/`), closer to review-ready, but
  missing the basic packaging (no `index.md`/front matter, no homepage entry) and carrying debug
  artifacts that would need to be stripped first. Style-checklist pass/fail if it were reviewed today:
  - Serious methods, absurd premise: **pass** (IHOP-proximity-vs-run-blocking-grade is exactly the
    Ministry's register).
  - Analytical Doctrine followed: **pass on paper** — Charter cites controlled regression with
    Home/Away and Experience controls, p < 0.002. Not independently re-verified against source code
    in this sweep (out of scope — style review, not a stats audit).
  - Money chart exists and is beautiful: **partial** — `ihop_effect_top_100.png` and
    `overall_regression_driving_time.png` exist; whether either is "the" money chart or needs
    polishing is an editorial call for whoever revives this.
  - Homepage/index links updated: **fail** — nothing links here.
  - No credentials/auth-state referenced: **needs check** — see `debug_auth_state.png` flag above.
- Neither operation should move to REVIEW yet; both need Minister direction on revive-vs-archive
  before further editorial polish is worth spending on them.

---

## 5. PIPELINE.md update

Updated the table (unambiguous facts only — stage labels reflect confirmed evidence above, not
speculation) and left the reconciliation questions (revive/archive Stuperlatives and IHOP; keep/kill
the stale Bridgelocks copy) as `[MINISTER]` items rather than guessing. Diff summary: replaced
"UNCLEAR"/"RELOCATED?" stage labels with evidence-backed stages and rewrote the notes columns to
state what was actually found instead of what needed to be found.

---

## Recommended actions

**[STAFF]**
- None outstanding from this sweep — all fact-finding closed out; no unambiguous cleanup this memo
  is authorized to perform (deleting orphans and editing post prose are both out of remit per the
  brief).

**[MINISTER]**
- Decide revive vs. archive for **Stuperlatives** (156 days stalled, no chart assets yet).
- Decide revive vs. archive for **IHOP Initiative** (198 days stalled, has charts, needs packaging).
- Decide keep vs. kill for the stale `posts/bridgelocks/` copy in mosp now that
  `~/Documents/bridgelocks` is the confirmed canonical, more-current home (same disposition question
  as loud_quiet_loud — should PIPELINE.md track it as "moved out, tracked elsewhere" the way that
  operation presumably is, or should the stale copy simply be deleted from mosp).
- Confirm the `debug_auth_state.png` / `test_page.html` / `reporting/debug/` artifacts under
  `posts/pff_analysis/` are safe to delete (recommended) — they look like scraper test output, not
  credentials, but this sweep did not open the auth-state file itself per the "never read `shhhh/`
  contents" spirit of the hard limits, and it isn't in `shhhh/` to begin with, which is itself worth
  the Minister's attention (a `debug_auth_state.png` sitting in a public-shipping folder rather than
  the secure zone).
- Push a remote for `~/Documents/bridgelocks` (currently local-only, one missed step away from being
  unrecoverable) — noting this is outside the mosp repo and outside this brief's remit, flagged for
  awareness only.

---

## 6. Addendum (Chief of Staff, post-sweep spot check)

Two items outside The Desk's ordinary sweep but surfaced while cross-checking its work, both urgent enough to flag now rather than hold for the next cycle:

**Tracked secret in `posts/bridgelocks/`.** `posts/bridgelocks/shhhhh/x_token` (note: `shhhhh`, five h's — not the gitignored `shhhh/`) is a **tracked file** (`git ls-files posts/bridgelocks/shhhhh/x_token` returns it), committed as part of f81864f along with the rest of the Bridgelocks draft. The `.gitignore` pattern on line 29 only matches `shhhh/` and does not catch the five-h typo directory, so this token is sitting in git history and the working tree unprotected. It does not currently appear in the built `_site/` (last build predates or doesn't include it), but it is one Jekyll rebuild away from shipping, and it is already permanently in git history regardless of build state. Per the hard limit against reading `shhhh/`-equivalent contents, I did not open the file — confirmed only its existence, tracked status, and size (115 bytes). **[MINISTER]**: rotate/revoke whatever token this is immediately, then decide whether to purge it from git history or simply delete-and-gitignore-going-forward (history purge is a separate, more invasive operation and its own decision).

**`_config.yml` exclude list does not match the prior admin-sweep's claims.** The current `exclude:` block in `_config.yml` lists only `antigravity_phone_chat_security_check, node_modules, package.json, package-lock.json, src, vite.config.js, README.md, Gemfile, Gemfile.lock, requirements.txt, migrate_content.py, vendor`. It does **not** list `hq`, `.claude`, `CLAUDE.md`, `ASSISTANT_TO_THE_MINISTER_OF_SILLY_PLOTS.md`, `shhhh`, or `chrome_data`, contrary to today's admin-sweep memo (`hq/reports/2026-07-05-admin-sweep.md`), which asserted all six were verified present in the exclude list. The current `_site/` (built 2026-07-05 20:55) does not contain any of these — Jekyll's default dotfile handling covers `.claude` and `.gitignore`-style entries automatically, which may explain part of the gap — but `hq`, `CLAUDE.md`, and the Charter are not dotfiles and have no visible exclusion mechanism in the file as it stands. Per hard limits I have not edited `_config.yml`. **[MINISTER]**: reconcile — either the admin-sweep memo describes a version of `_config.yml` that no longer matches what's on disk, or Jekyll's implicit behavior is doing more work than assumed and should be verified with a clean rebuild before trusting it further.

---

*Prepared by: The Desk, Ministry of Silly Plots*
*Date: 2026-07-05*
