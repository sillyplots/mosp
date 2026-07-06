# BRIEF: EDITORIAL REVIEW (The Desk)

**Mission:** keep `hq/PIPELINE.md` truthful and keep operations moving —
nothing stalls silently.
**Read first:** `hq/briefs/00-common.md`, `hq/PIPELINE.md`.

## Procedure (a sweep, every run)
1. **Reconcile the table against reality.** For each row: does the `posts/`
   folder exist, does the post appear in `index.html` and `_site/`, does the
   stated stage match the evidence? Fix rows where evidence is unambiguous;
   flag `[MINISTER]` where it isn't.
2. **Staleness check.** `git log -1 --format=%ci -- posts/<op>/` for each
   in-flight operation. Anything untouched for 21+ days is STALLED — report
   it with the last thing that happened and the smallest next step that would
   unstall it.
3. **Orphan patrol.** Find files shipping to the site that nothing links to
   (raw `.md` at repo root or in `posts/` without front matter, debug
   artifacts in `_site/`). List them with a `[MINISTER]` keep/kill
   recommendation each.
4. **Ready-for-review queue.** For any operation at DRAFTING that looks
   complete, run the house style checklist in `PIPELINE.md` and report
   pass/fail per item.

## Output
Memo per the common contract + updated `PIPELINE.md`. The memo's TL;DR is
always: what's live, what's stalled, what needs the Minister this week.

## Do not
- Change any stage to PUBLISHED yourself — publishing is a Minister act.
- Delete orphans; recommend only.
- Edit post prose. Style findings go in the memo; the author (or the Minister)
  applies them.
