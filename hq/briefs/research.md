# BRIEF: RESEARCH STAFFING (Analytical Corps)

**Mission:** execute a scoped research task for an APPROVED operation. Unlike
the standing duties, this brief is a **template** — each assignment must come
with a task order before work starts.
**Read first:** `hq/briefs/00-common.md`, the operation's entry in
`hq/PIPELINE.md`, the Charter's Analytical Doctrine section, and your task
order.

## Task order format (Minister or Chief of Staff issues; file at
`hq/reports/YYYY-MM-DD-task-order-<codename>.md` before work starts)
- **Question:** the specific falsifiable thing to determine
- **Data:** source(s), where obtained/stored, known caveats
- **Method:** which doctrine tools apply (controlled regression? relative
  metrics? 80th-percentile ceiling?), and the standard controls to include
- **Done means:** the artifact(s) that end the task — e.g. "a CSV at X, a
  findings memo, and the money chart as PNG"

No task order → no work. Request one instead of guessing.

## Standing doctrine (from the Charter — applies to every task)
- Controlled regression with at minimum `IsHome` and `YearsInLeague`-style
  controls where applicable; report coefficients and p-values, not adjectives.
- Prefer relative metrics over absolutes.
- Deduplicate before processing; state row counts before/after.
- Deep dives on interesting anomalies go in a dedicated
  `deep_dives/analyze_<entity>.py`, never inline in the main pipeline.
- Keep local CSVs for reproducibility; scripts live under the operation's
  folder in `posts/<op>/` using its `etl/` / `analysis/` / `deep_dives/`
  structure.

## Output
Findings memo per the common contract: TL;DR states the answer to the task
order's question with effect size and confidence, then methods, then caveats
(honest ones — a null result filed plainly is a success; a dressed-up null
is a firing offense). Update the operation's row in `PIPELINE.md` notes.
