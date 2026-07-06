# BRIEF: OPS CHECK (Inspectorate of Machinery)

**Mission:** verify the Ministry's running machinery is actually running.
**Read first:** `hq/briefs/00-common.md`, then the **Machinery Register**
below — which you also maintain.

## Machinery Register
*(One entry per live system. Update when systems are added/retired — that
change is `[STAFF]`; adding a system you merely suspect exists is not.)*

| System | What it is | How to check | Healthy looks like |
|---|---|---|---|
| sillyplots.com | GitHub Pages site, built from `main` by `.github/workflows/deploy.yml` | `curl -s -o /dev/null -w '%{http_code}' https://sillyplots.com` and `gh run list --workflow=deploy.yml --limit 3` | HTTP 200; latest run `success` |
| Homepage links | Post links resolve | `curl` each `href` in `index.html` | All 200 |
| *(bridgelocks scraper — GCP)* | Playwright scraper, deployed per old `posts/bridgelocks/etl/DEPLOY.md` (project since moved out of repo) | UNKNOWN — Minister to confirm whether still deployed and where it now lives | — |

## Procedure
1. Run every check in the register. Record actual output, not vibes.
2. For failures: one `[MINISTER]` or `[STAFF]` recommended action each, with
   the exact command or file. Do **not** attempt repairs — restarts, deploys,
   and config changes are outside this brief even when "obvious."
3. Local hygiene sweep: confirm `shhhh/` and `chrome_data/` are still in
   `.gitignore` and that `git status` shows no secret-looking files staged.
4. Memo per the common contract. TL;DR format: "N systems checked, N healthy,
   N failing, N unknown."

## Do not
- Fix anything remote. You are an inspector, not a mechanic.
- Mark an unknown as healthy. Unknown is a finding.
