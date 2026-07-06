# BRIEF: ADMIN SWEEP (Registry Office)

**Mission:** ministry hygiene — secrets containment, repo tidiness, and
keeping the founding documents current.
**Read first:** `hq/briefs/00-common.md`.

## Procedure
1. **Secrets audit.**
   - `shhhh/` and `chrome_data/` present in `.gitignore`; nothing from either
     tracked by git (`git ls-files shhhh chrome_data` must return empty).
   - Scan tracked files for credential *shapes* (key/token/password
     assignments, `service_account` JSON fields, auth-state files like
     `*_auth.json`) — report paths only, never the values.
   - Confirm `hq`, `CLAUDE.md`, `.claude`, `shhhh`, and the Charter are in
     `_config.yml` excludes, and none of them appear in a fresh `_site/`.
2. **Debris patrol.** List repo-root clutter fitting known debris patterns:
   `debug_*`, `*.log`, one-off scripts, `.DS_Store` in git. Recommend
   keep/kill per item, `[MINISTER]` unless it's gitignore-able noise
   (`[STAFF]`: add to `.gitignore`).
3. **Charter maintenance.** Cross-check the Charter's ACTIVE OPERATIONS
   against `hq/PIPELINE.md`. Draft (in the memo, as a diff) the edits that
   would bring the Charter current — e.g. operations to move to
   ARCHIVED/DORMANT. Note the Charter has two sections numbered "3";
   the drafted fix should renumber.
4. **"Jot that down" backlog.** If `hq/DECISIONS.md` contains decisions not
   yet reflected in the Charter's protocols, include them in the drafted
   Charter edits.

## Output
Memo per the common contract. Charter edits ship as a proposed diff in the
memo — the Charter is a founding document; only apply edits when the task
order or the Minister says so.

## Do not
- Delete anything. Recommend only.
- Touch `shhhh/` contents, `_config.yml`, or `.github/`.
