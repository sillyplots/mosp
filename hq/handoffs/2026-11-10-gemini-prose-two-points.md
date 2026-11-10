# Handoff: prose edit, "The Defensive Touchdown Act"

**Repo:** `github.com/sillyplots/mosp` · **Base branch:** `claude/kind-feynman-cbfjfj`
**Work on:** a new branch `gemini/two-points-prose` off the base branch. Commit there. Do not merge or push to `main` (main is the live site).

## Task
Edit the prose of `posts/safety/index.md`: tighten it, cut points made twice, sharpen the deadpan, and make terms like "net value", "swing" and "WP pts" clear on first use. Prose only. The analysis is done and verified.

## Read first
- `CLAUDE.md`: house tone (dry bureaucratic deadpan; clarity beats bits).
- `posts/safety/analysis/results.json`: source of every number in the post.
- `hq/reports/2026-11-08-red-team-two-points.md`: why the caveats exist.

## Rules
1. Don't change any number, sample size, team or game. If one looks wrong, flag it; don't fix it.
2. Don't add facts, examples, citations or rule-book references.
3. Keep the "What the data does and does not say" paragraph and all caveats (upper bound, offenses would adapt, model noise, small 2024–25 sample). Reword them, don't soften them.
4. Keep the markup working: front matter, the `<style>` block, the `<div class="dta" markdown="1">` wrapper, HTML tags and classes, tables (same columns), `{: .costs}`, and image paths.
5. Keep the section order. Headings may be retitled. Amendment Sections 1–4: clarity edits only, no change of meaning.
6. No em-dash asides, no "not X, but Y" constructions, no stock filler.

## Done when
- Edits are committed to `gemini/two-points-prose`.
- The commit message lists what changed and anything flagged but left alone.
- Optional check: `JEKYLL_NO_BUNDLER_REQUIRE=true jekyll build` succeeds.
