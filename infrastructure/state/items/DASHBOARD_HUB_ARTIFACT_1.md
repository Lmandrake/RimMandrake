# DASHBOARD_HUB_ARTIFACT_1 — one place the human goes; the system checks it's fresh

Owner, verbatim (2026-09-11): "put all these artifacts together into a single
multi tab artifact so there's one place the human can go and the system can
check is fresh." Design: `design/RimMandrake/art_regen_registry_design.md` §4.

## spec
- One published artifact, stable URL, pinned for the owner. Thin tab shell
  `index.html` (rarely changes) + one data file per tab via the multi-file
  artifact mechanism (`art_status.json`, `health.json`, worldmap audit, …).
- A seat updating its dashboard republishes ONLY its own data file against the
  same URL (unpassed files are kept) — many writers, no collisions.
- Every data file carries `generatedAt` + a fingerprint of its source
  artifact; the shell shows a per-tab freshness lamp (green/amber/red by age)
  and a checker script reads the same fields. Tabs #hash-addressable.
- Dashboards IN: art regen, codebase health, maturity/health, worldmap audit.
  Working review sheets are LINKED, never embedded (they keep their own URLs).
- Repo HTML source kept alongside with a native path.
- Owner's default theme: the warm 70s dark-brown palette.
- Migration: existing codebase_health artifact + Maturity/Health dashboards
  fold in as tabs; their standalone publishers repoint to hub data files.

## verify
- [ ] Two different seats each republish their own tab's data file against the
      live URL without clobbering the other's (prove by fingerprint).
- [ ] A stale tab (source changed, data file not re-rendered) shows amber/red;
      the checker reports the same from the JSON fields.
- [ ] Sheets appear as links only; no workspace embedded.

## criteria
The owner opens one pinned URL and sees every status page with an honest
freshness lamp per tab; no dashboard ships standalone after migration.

## Built and published 2026-09-11 (BENCH)

**URL (stable, pinned): https://claude.ai/code/artifact/d066e619-b84d-479c-842f-a81b0182511c**
Shell + checker + generator: `infrastructure/dashboards/hub/` (index.html,
make_tab_data.py, hub_check.py, data/). Tabs: art (fed directly by
`infrastructure/artpipe/art_status.json`), health, maturity, worldmap, sheets
(links only). Republish rule: pass the URL as `url`, send ONLY your tab's data
file — unpassed files are kept.

Verify state: stale-lamp half PROVEN (checker flags art STALE against
registry.jsonl fingerprint, worldmap RED by age; shell lamps age-computed the
same). Still open: the two-seat no-clobber republish proof, and migration —
standalone publishers (codebase_health, maturity dashboard, artpipe) repoint
to hub data files.
