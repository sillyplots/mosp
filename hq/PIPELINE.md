# EDITORIAL PIPELINE — Ministry of Silly Plots

One row per operation that has cleared the idea stage. Stages:
`IN RESEARCH → DRAFTING → REVIEW → PUBLISHED → ARCHIVED`.

| Operation | Premise | Stage | Home | Notes |
|---|---|---|---|---|
| Super Bowl | Super Bowl stuperlatives analysis | PUBLISHED | `posts/super_bowl/` | Live at sillyplots.com/post/superbowl — only post linked from the homepage. Confirmed 2026-07-05. |
| Stuperlatives | Player stuperlatives (Walker, Darnold, et al.) | DRAFTING (STALLED, 156 days) | `posts/stuperlatives/` | Confirmed 2026-07-05: 10 raw `.md` files with no front matter ship into `_site/posts/stuperlatives/`, unlinked from `index.html`. Zero chart assets in the folder — not review-ready. Last git touch 2026-01-30. [MINISTER] revive or archive. |
| IHOP Initiative | O-line run blocking vs. IHOP proximity | DRAFTING (STALLED, 198 days) | `posts/pff_analysis/` | Confirmed 2026-07-05: raw `.md` + real chart assets in `reporting/plots/`, but also ships scraper debug artifacts (`etl/test_page.html`, `etl/debug_auth_state.png`, `reporting/debug/`) and has no `index.md`/homepage link. Charter's p < 0.002 finding is real analysis, just never packaged as a post. Last git touch 2025-12-19. [MINISTER] revive (strip debug artifacts, add front matter) or archive. |
| Bridgelocks | Seattle bridge opening commute analysis | SUPERSEDED (mosp copy STALLED, 49 days) | `posts/bridgelocks/` (stale) / `~/Documents/bridgelocks` (canonical) | Confirmed 2026-07-05: `posts/bridgelocks/` is present (not deleted, contra an earlier working-tree snapshot — those deletions were never committed). Graduation to `~/Documents/bridgelocks` is real and confirmed (own git repo, diverged and more current), same pattern as loud_quiet_loud, but that repo is itself stalled since 2026-05-30 with no remote configured. [MINISTER] keep-or-kill the stale mosp copy now that a canonical home exists. |

Table last reconciled against reality 2026-07-05 (see
`hq/reports/2026-07-05-editorial.md` for full evidence trail). Three
[MINISTER] decisions are open — see that memo's Recommended Actions.

## House style checklist (apply at REVIEW)

- Serious methods, absurd premise — the humor is in the deadpan, not the prose.
- Analytical Doctrine followed (relative metrics, controlled regression,
  standard controls, deduplication) — see the Charter, §Analytical Doctrine.
- The money chart exists and is beautiful. Visual excellence is non-negotiable.
- Homepage / index links updated. No orphaned raw `.md` files shipping to the site.
- No credentials, auth-state files, or `shhhh/` contents referenced in the post
  or its assets.
