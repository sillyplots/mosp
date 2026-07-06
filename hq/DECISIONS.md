# DECISION LOG — Office of the Minister

Append-only. Newest first. Staffers: read this before proposing anything the
Minister has already ruled on.

---

## 2026-07-05 — Founding of HQ
- **Chief of Staff established.** HQ lives in `hq/`, excluded from the Jekyll
  build. Portfolio: idea generation, red-teaming, editorial pipeline, ops
  babysitting, research staffing, ministry admin.
- **Staffing model:** Claude models run the modules (not Gemini, reversing an
  earlier inclination). Cheaper tiers (Haiku/Sonnet) execute briefs; frontier
  models are for designing briefs and judgment work.
- **Autonomy:** commit-never-publish. Staffers may write and commit to
  non-main branches; `main`, the live site, and external services require
  the Minister's signature.
- **Charter publication leak closed:** `ASSISTANT_TO_THE_MINISTER_OF_SILLY_PLOTS.md`
  and other internal paths added to `_config.yml` excludes — they had been
  shipping to sillyplots.com as raw files.
