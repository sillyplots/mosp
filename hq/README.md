# MINISTRY HQ — Office of the Chief of Staff

**Classification:** Internal. This folder is excluded from the Jekyll build
(`_config.yml` → `exclude: hq`). Verify that stays true before ever renaming
this folder. Nothing in here should appear on sillyplots.com.

## What this is

The operating layer of the Ministry of Silly Plots. The mandate lives in
[../ASSISTANT_TO_THE_MINISTER_OF_SILLY_PLOTS.md](../ASSISTANT_TO_THE_MINISTER_OF_SILLY_PLOTS.md)
(the Charter). HQ is where work is planned, tracked, critiqued, and reported.

The design principle: **judgment happens in writing, execution happens from
briefs.** Every standing duty is a module with a written brief in `briefs/`
that is explicit enough for a smaller, cheaper model to execute without
creativity. If a staffer model needs to make a judgment call, the brief is
underspecified — fix the brief, don't blame the staffer.

## Structure

| File / dir | Purpose |
|---|---|
| `IDEAS.md` | The idea ledger. Every silly plot concept, with its lifecycle stage. |
| `PIPELINE.md` | The editorial board. Posts from approved idea → published. |
| `DECISIONS.md` | The Minister's decision log. Append-only. |
| `briefs/` | One brief per standing duty. The contract each staffer runs against. |
| `reports/` | Dated output memos from staffer runs (`YYYY-MM-DD-<module>.md`). |

Staffer agents (cheaper Claude models) are defined in `../.claude/agents/`,
one per brief. Invoke them from any Claude Code session, e.g. *"have the
red-team agent review the top idea in IDEAS.md."*

## Standing orders (apply to every module)

1. **Commit, never publish.** Staffers may write files and commit to branches
   other than `main`. Pushing, merging to `main`, or anything that reaches
   the live site or an external service requires the Minister's signature.
2. **Secrets stay in `shhhh/`.** It is gitignored. Never copy credential
   material anywhere else, including into reports.
3. **Reports are files, not chat.** Every module run ends with a memo in
   `reports/` and, where applicable, an update to the relevant ledger
   (IDEAS/PIPELINE). If it isn't written down, it didn't happen.
4. **Ledgers are the source of truth.** Read them before acting; update them
   after acting. Do not maintain parallel state.
5. **Tone:** dry, bureaucratic, per the Charter. Filing a memo titled
   "RE: RE: FWD: Urgent — Goose Census Irregularities" is encouraged.
   Being unclear is not.

## The idea lifecycle

```
PROPOSED → RED-TEAMED → APPROVED → IN RESEARCH → DRAFTING → PUBLISHED
                ↓
             NIXED (with cause of death recorded)
```

`IDEAS.md` covers PROPOSED through APPROVED. Once approved, an idea gets a
row in `PIPELINE.md` and (when work starts) a folder under `posts/`.

## Scheduling (later)

Nothing runs on a timer yet. When a duty proves itself manually (likely
`ops-check` first), schedule it via Claude Code scheduled tasks. Do not
automate a module until its brief has survived at least three manual runs.
