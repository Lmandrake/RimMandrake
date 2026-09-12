# HUB_TAB_PUBLISHER_MIGRATION_1 — standalone dashboard publishers repoint to the hub

The hub is live and pinned: https://claude.ai/code/artifact/d066e619-b84d-479c-842f-a81b0182511c
(`DASHBOARD_HUB_ARTIFACT_1`; source `infrastructure/dashboards/hub/`). Each tab
reads ONE data file; a seat republishes ONLY its own file against that URL
(pass it as `url`; unpassed files are kept).

## spec
- artpipe: after `artreg.py render`, republish `data/art.json` (from
  `infrastructure/artpipe/art_status.json`) against the hub URL — fold into the
  render step or the daemon's post-wave hook.
- codebase-health hook: after writing `Transient/codebase_health.json`, run
  `python3 infrastructure/dashboards/hub/make_tab_data.py health` and republish
  `data/health.json`.
- maturity dashboard generator: same pattern, `maturity`.
- Retire the standalone dashboard artifacts (Repo Health Treemap etc.) only on
  the owner's word — the hub links replace them.
- 🔴 Doing ANY one of these from FOUNDRY's session completes the hub's two-seat
  no-clobber verify: after your republish, this seat's tabs must still render
  (fingerprints prove nothing else changed). Record the proof on
  DASHBOARD_HUB_ARTIFACT_1.

## verify
Each publisher republishes only its own tab file; `hub_check.py` shows all
lamps tracking their sources; two different seats have republished without
clobbering (fingerprint evidence on the hub item).
